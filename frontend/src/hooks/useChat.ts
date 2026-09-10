import { useCallback, useEffect, useRef, useState } from 'react'
import type {
  ChatMessage,
  MessageKind,
  MessageMeta,
  ProductPayload,
  PromptMode,
  Session,
} from '../types'
import { MODE_LABELS } from '../types'
import { splitThinking, uid } from '../lib/utils'

const STORAGE_KEY = 'ds-chat-sessions'
const SYSTEM_KEY = 'ds-system-prompt'

function loadSessions(): Session[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as Session[]) : []
  } catch {
    return []
  }
}

function saveSessions(sessions: Session[]) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions))
}

function loadSystemPrompt() {
  try {
    return localStorage.getItem(SYSTEM_KEY) ?? ''
  } catch {
    return ''
  }
}

function createSession(mode: PromptMode = 'zero_shot'): Session {
  return {
    id: uid(),
    title: '新对话',
    updatedAt: Date.now(),
    messages: [],
    mode,
  }
}

function formatCompare(results: Record<string, string>, modes: PromptMode[]) {
  return modes
    .map((m) => `### ${MODE_LABELS[m] || m}\n\n${results[m] || '（无结果）'}`)
    .join('\n\n---\n\n')
}

function formatToolSteps(
  steps: Array<{ type: string; name?: string; arg?: string; result?: string; content?: string }>,
  answer: string,
) {
  const parts: string[] = []
  for (const s of steps) {
    if (s.type === 'tool') {
      parts.push(`**调用工具** \`${s.name}\`\n- 参数：${s.arg}\n- 结果：${s.result}`)
    }
  }
  parts.push(`### 最终回答\n\n${answer}`)
  return parts.join('\n\n')
}

export function useChat() {
  const [sessions, setSessions] = useState<Session[]>(() => {
    const list = loadSessions()
    return list.length ? list : [createSession()]
  })
  const [activeId, setActiveId] = useState(() => sessions[0]?.id)
  const [loading, setLoading] = useState(false)
  const [systemPrompt, setSystemPromptState] = useState(loadSystemPrompt)
  const abortRef = useRef<AbortController | null>(null)
  const syncedSystem = useRef(false)

  const active = sessions.find((s) => s.id === activeId) ?? sessions[0]

  useEffect(() => {
    saveSessions(sessions)
  }, [sessions])

  useEffect(() => {
    if (syncedSystem.current) return
    syncedSystem.current = true
    const content = loadSystemPrompt()
    void fetch('/system_prompt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    }).catch(() => undefined)
  }, [])

  const updateActive = useCallback(
    (updater: (s: Session) => Session) => {
      setSessions((prev) =>
        prev.map((s) => (s.id === activeId ? updater({ ...s, updatedAt: Date.now() }) : s)),
      )
    },
    [activeId],
  )

  const patchBotMessage = useCallback(
    (botId: string, partial: Partial<ChatMessage>) => {
      setSessions((prev) =>
        prev.map((s) =>
          s.id === activeId
            ? {
                ...s,
                updatedAt: Date.now(),
                messages: s.messages.map((m) => (m.id === botId ? { ...m, ...partial } : m)),
              }
            : s,
        ),
      )
    },
    [activeId],
  )

  const pushPair = useCallback(
    (
      userContent: string,
      botPartial: Partial<ChatMessage>,
      titleHint?: string,
    ): string => {
      const botId = uid()
      updateActive((s) => ({
        ...s,
        title:
          s.messages.length === 0
            ? (titleHint || userContent).slice(0, 24)
            : s.title,
        messages: [
          ...s.messages,
          {
            id: uid(),
            role: 'user',
            content: userContent,
            createdAt: Date.now(),
          },
          {
            id: botId,
            role: 'assistant',
            content: '',
            typing: true,
            createdAt: Date.now(),
            ...botPartial,
          },
        ],
      }))
      return botId
    },
    [updateActive],
  )

  const newChat = useCallback(async () => {
    abortRef.current?.abort()
    setLoading(false)
    try {
      await fetch('/reset', { method: 'POST' })
    } catch {
      /* ignore */
    }
    const s = createSession(active?.mode ?? 'zero_shot')
    setSessions((prev) => [s, ...prev])
    setActiveId(s.id)
  }, [active?.mode])

  const deleteSession = useCallback(
    (id: string) => {
      setSessions((prev) => {
        const next = prev.filter((s) => s.id !== id)
        if (!next.length) {
          const s = createSession()
          setActiveId(s.id)
          return [s]
        }
        if (id === activeId) setActiveId(next[0].id)
        return next
      })
    },
    [activeId],
  )

  const setMode = useCallback(
    (mode: PromptMode) => {
      updateActive((s) => ({ ...s, mode }))
    },
    [updateActive],
  )

  const saveSystemPrompt = useCallback(async (content: string) => {
    setSystemPromptState(content)
    localStorage.setItem(SYSTEM_KEY, content)
    const res = await fetch('/system_prompt', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ content }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.error || `HTTP ${res.status}`)
    }
  }, [])

  const stop = useCallback(() => {
    abortRef.current?.abort()
    setLoading(false)
    updateActive((s) => ({
      ...s,
      messages: s.messages.map((m) => (m.typing ? { ...m, typing: false } : m)),
    }))
  }, [updateActive])

  const requestAssistant = useCallback(
    async (question: string, botId: string, stream = true) => {
      const mode = active?.mode ?? 'zero_shot'
      const controller = new AbortController()
      abortRef.current = controller
      setLoading(true)

      try {
        if (!stream) {
          const res = await fetch(
            `/chat?question=${encodeURIComponent(question)}&mode=${encodeURIComponent(mode)}`,
            { signal: controller.signal },
          )
          if (!res.ok) throw new Error(`HTTP ${res.status}`)
          const data = await res.text()
          const { thinking, content } = splitThinking(data)
          patchBotMessage(botId, {
            content,
            thinking,
            typing: false,
            error: false,
            kind: 'chat',
            sourceQuestion: question,
          })
          return
        }

        const resp = await fetch(
          `/stream_chat?question=${encodeURIComponent(question)}&mode=${encodeURIComponent(mode)}`,
          { signal: controller.signal },
        )
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const reader = resp.body?.getReader()
        if (!reader) throw new Error('无法读取流式响应')

        const decoder = new TextDecoder()
        let buffer = ''
        let raw = ''

        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          const parts = buffer.split('\n\n')
          buffer = parts.pop() ?? ''

          for (const part of parts) {
            const line = part.trim()
            if (!line.startsWith('data: ')) continue
            const data = line.slice(6)
            if (data === '[DONE]') {
              patchBotMessage(botId, {
                typing: false,
                error: false,
                kind: 'chat',
                sourceQuestion: question,
              })
              continue
            }
            try {
              const json = JSON.parse(data) as { content?: string }
              raw += json.content || ''
              const { thinking, content } = splitThinking(raw)
              patchBotMessage(botId, {
                content,
                thinking,
                typing: true,
                error: false,
                kind: 'chat',
                sourceQuestion: question,
              })
            } catch {
              /* ignore */
            }
          }
        }
        patchBotMessage(botId, {
          typing: false,
          error: false,
          kind: 'chat',
          sourceQuestion: question,
        })
      } catch (err) {
        if ((err as Error).name === 'AbortError') {
          patchBotMessage(botId, { typing: false })
        } else {
          patchBotMessage(botId, {
            content: `请求失败：${(err as Error).message}`,
            typing: false,
            error: true,
            kind: 'chat',
            sourceQuestion: question,
          })
        }
      } finally {
        setLoading(false)
        abortRef.current = null
      }
    },
    [active?.mode, patchBotMessage],
  )

  const send = useCallback(
    async (text: string, stream = true) => {
      const question = text.trim()
      if (!question || loading) return

      const botId = pushPair(question, {
        kind: 'chat',
        sourceQuestion: question,
        content: '',
        thinking: '',
      })
      await requestAssistant(question, botId, stream)
    },
    [loading, pushPair, requestAssistant],
  )

  const runSelfConsistency = useCallback(
    async (text: string) => {
      const question = text.trim() || '为旅行背包品牌生成一句口号'
      if (loading) return

      const botId = pushPair(`[自我一致性] ${question}`, {
        kind: 'self_consistency',
        sourceQuestion: question,
        meta: { question },
        content: '自我一致性需多次调用模型，请稍候…',
      }, question)

      setLoading(true)
      try {
        const res = await fetch(
          `/self_consistency?question=${encodeURIComponent(question)}&num=2`,
        )
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        const failed = Boolean(data.error)
        const content = data.error
          ? String(data.error)
          : `候选方案：\n${(data.candidates || [])
              .map((c: string, i: number) => `${i + 1}. ${c}`)
              .join('\n')}\n\n最终评选：\n${data.final || ''}`
        patchBotMessage(botId, {
          content,
          typing: false,
          error: failed,
          kind: 'self_consistency',
          sourceQuestion: question,
          meta: { question },
        })
      } catch (err) {
        patchBotMessage(botId, {
          content: `请求失败：${(err as Error).message}`,
          typing: false,
          error: true,
          kind: 'self_consistency',
          sourceQuestion: question,
          meta: { question },
        })
      } finally {
        setLoading(false)
      }
    },
    [loading, patchBotMessage, pushPair],
  )

  const runProductCopy = useCallback(
    async (product?: ProductPayload) => {
      if (loading) return
      const payload = product || {
        name: '全自动豆浆机',
        features: '1分钟速热, 20Bar高压萃取, 手机App控制',
        audience: '追求生活品质的独居白领',
      }

      const botId = pushPair(
        `[电商文案] ${payload.name}｜卖点：${payload.features}｜人群：${payload.audience}`,
        {
          kind: 'product_copy',
          sourceQuestion: payload.name,
          meta: { product: payload },
          content: '正在按 Few-Shot + CoT 生成产品文案…',
        },
        `电商文案·${payload.name}`,
      )

      setLoading(true)
      try {
        const res = await fetch('/product_copy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        const data = await res.json()
        patchBotMessage(botId, {
          content: data.error ? String(data.error) : data.result || '未生成内容',
          typing: false,
          error: Boolean(data.error),
          kind: 'product_copy',
          sourceQuestion: payload.name,
          meta: { product: payload },
        })
      } catch (err) {
        patchBotMessage(botId, {
          content: `请求失败：${(err as Error).message}`,
          typing: false,
          error: true,
          kind: 'product_copy',
          meta: { product: payload },
        })
      } finally {
        setLoading(false)
      }
    },
    [loading, patchBotMessage, pushPair],
  )

  const runSocialPlan = useCallback(
    async (topic?: string) => {
      if (loading) return
      const subject = (topic || '独居女生的低成本精致生活').trim()

      const botId = pushPair(
        `[社交策划] ${subject}`,
        {
          kind: 'social_plan',
          sourceQuestion: subject,
          meta: { topic: subject },
          content: '阶段 1/4：正在发散策划分支…',
        },
        `社交策划·${subject.slice(0, 16)}`,
      )

      setLoading(true)
      const patch = (content: string, typing = true, error = false) => {
        patchBotMessage(botId, {
          content,
          typing,
          error,
          kind: 'social_plan',
          sourceQuestion: subject,
          meta: { topic: subject },
        })
      }

      try {
        const resp = await fetch(
          `/social_plan_stream?topic=${encodeURIComponent(subject)}`,
        )
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const reader = resp.body?.getReader()
        if (!reader) throw new Error('无法读取流式响应')

        const decoder = new TextDecoder()
        let buffer = ''
        const sections: string[] = []

        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buffer += decoder.decode(value, { stream: true })
          const parts = buffer.split('\n\n')
          buffer = parts.pop() ?? ''

          for (const part of parts) {
            const line = part.trim()
            if (!line.startsWith('data: ')) continue
            const data = line.slice(6)
            if (data === '[DONE]') {
              patch(sections.join('\n\n---\n\n') || '策划完成', false, false)
              continue
            }
            try {
              const json = JSON.parse(data) as {
                stage?: number | string
                title?: string
                content?: string
                done?: boolean
              }
              if (json.stage === 'error') {
                patch(json.content || '策划失败', false, true)
                continue
              }
              if (json.content && json.title) {
                if (json.content.length < 40 && !json.done) {
                  patch(
                    `${sections.length ? sections.join('\n\n---\n\n') + '\n\n---\n\n' : ''}阶段 ${json.stage}/4：${json.content}`,
                    true,
                  )
                } else {
                  sections.push(`### ${json.title}\n\n${json.content}`)
                  patch(sections.join('\n\n---\n\n'), !json.done)
                }
              }
            } catch {
              /* ignore */
            }
          }
        }
        if (sections.length) patch(sections.join('\n\n---\n\n'), false)
      } catch (err) {
        patch(`请求失败：${(err as Error).message}`, false, true)
      } finally {
        setLoading(false)
      }
    },
    [loading, patchBotMessage, pushPair],
  )

  const runCompare = useCallback(
    async (question: string, modes: PromptMode[]) => {
      if (loading) return
      const q = question.trim()
      if (!q || modes.length < 2) return

      const botId = pushPair(
        `[模式对比] ${q}`,
        {
          kind: 'compare',
          sourceQuestion: q,
          meta: { question: q, modes },
          content: `正在对比 ${modes.map((m) => MODE_LABELS[m]).join(' / ')}，请稍候…`,
        },
        `对比·${q.slice(0, 16)}`,
      )

      setLoading(true)
      try {
        const res = await fetch('/compare', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q, modes }),
        })
        const data = await res.json()
        if (data.error) {
          patchBotMessage(botId, {
            content: String(data.error),
            typing: false,
            error: true,
            kind: 'compare',
            meta: { question: q, modes },
          })
        } else {
          patchBotMessage(botId, {
            content: formatCompare(data.results || {}, modes),
            typing: false,
            error: false,
            kind: 'compare',
            sourceQuestion: q,
            meta: { question: q, modes },
          })
        }
      } catch (err) {
        patchBotMessage(botId, {
          content: `请求失败：${(err as Error).message}`,
          typing: false,
          error: true,
          kind: 'compare',
          meta: { question: q, modes },
        })
      } finally {
        setLoading(false)
      }
    },
    [loading, patchBotMessage, pushPair],
  )

  const runToolChat = useCallback(
    async (question: string) => {
      if (loading) return
      const q = question.trim()
      if (!q) return

      const botId = pushPair(
        `[工具调用] ${q}`,
        {
          kind: 'tool_chat',
          sourceQuestion: q,
          meta: { question: q },
          content: '正在按 ReAct 决定是否调用工具…',
        },
        `工具·${q.slice(0, 16)}`,
      )

      setLoading(true)
      try {
        const res = await fetch('/tool_chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ question: q }),
        })
        const data = await res.json()
        if (data.error) {
          patchBotMessage(botId, {
            content: String(data.error),
            typing: false,
            error: true,
            kind: 'tool_chat',
            meta: { question: q },
          })
        } else {
          patchBotMessage(botId, {
            content: formatToolSteps(data.steps || [], data.answer || ''),
            typing: false,
            error: false,
            kind: 'tool_chat',
            sourceQuestion: q,
            meta: { question: q },
          })
        }
      } catch (err) {
        patchBotMessage(botId, {
          content: `请求失败：${(err as Error).message}`,
          typing: false,
          error: true,
          kind: 'tool_chat',
          meta: { question: q },
        })
      } finally {
        setLoading(false)
      }
    },
    [loading, patchBotMessage, pushPair],
  )

  const regenerate = useCallback(
    async (assistantId: string) => {
      if (loading) return
      const session = sessions.find((s) => s.id === activeId)
      if (!session) return

      const idx = session.messages.findIndex((m) => m.id === assistantId)
      if (idx < 0) return
      const target = session.messages[idx]
      const prevUser = [...session.messages.slice(0, idx)].reverse().find((m) => m.role === 'user')
      const kind: MessageKind = target.kind || 'chat'
      const meta: MessageMeta | undefined = target.meta

      updateActive((s) => ({
        ...s,
        messages: s.messages.filter((m) => m.id !== assistantId && m.id !== prevUser?.id),
      }))

      if (kind === 'self_consistency') {
        await runSelfConsistency(meta?.question || target.sourceQuestion || '')
        return
      }
      if (kind === 'product_copy' && meta?.product) {
        await runProductCopy(meta.product)
        return
      }
      if (kind === 'social_plan') {
        await runSocialPlan(meta?.topic || target.sourceQuestion)
        return
      }
      if (kind === 'compare' && meta?.question && meta.modes?.length) {
        await runCompare(meta.question, meta.modes)
        return
      }
      if (kind === 'tool_chat') {
        await runToolChat(meta?.question || target.sourceQuestion || '')
        return
      }

      const question = (target.sourceQuestion || prevUser?.content || '').trim()
      if (!question) return
      const botId = pushPair(question, {
        kind: 'chat',
        sourceQuestion: question,
        content: '',
        thinking: '',
      })
      // pushPair already added user+bot; remove duplicate user from regenerate path
      // Actually we filtered both and then pushPair adds user again - good.
      await requestAssistant(question, botId, true)
    },
    [
      activeId,
      loading,
      pushPair,
      requestAssistant,
      runCompare,
      runProductCopy,
      runSelfConsistency,
      runSocialPlan,
      runToolChat,
      sessions,
      updateActive,
    ],
  )

  const toggleLike = useCallback(
    (messageId: string) => {
      updateActive((s) => ({
        ...s,
        messages: s.messages.map((m) =>
          m.id === messageId ? { ...m, liked: !m.liked } : m,
        ),
      }))
    },
    [updateActive],
  )

  return {
    sessions,
    active,
    activeId,
    setActiveId,
    loading,
    systemPrompt,
    saveSystemPrompt,
    newChat,
    deleteSession,
    setMode,
    send,
    stop,
    runSelfConsistency,
    runProductCopy,
    runSocialPlan,
    runCompare,
    runToolChat,
    regenerate,
    toggleLike,
  }
}
