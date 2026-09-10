import { useCallback, useEffect, useRef, useState } from 'react'
import type { ChatMessage, PromptMode, Session } from '../types'
import { splitThinking, uid } from '../lib/utils'

const STORAGE_KEY = 'ds-chat-sessions'

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

function createSession(mode: PromptMode = 'zero_shot'): Session {
  return {
    id: uid(),
    title: '新对话',
    updatedAt: Date.now(),
    messages: [],
    mode,
  }
}

export function useChat() {
  const [sessions, setSessions] = useState<Session[]>(() => {
    const list = loadSessions()
    return list.length ? list : [createSession()]
  })
  const [activeId, setActiveId] = useState(() => sessions[0]?.id)
  const [loading, setLoading] = useState(false)
  const abortRef = useRef<AbortController | null>(null)

  const active = sessions.find((s) => s.id === activeId) ?? sessions[0]

  useEffect(() => {
    saveSessions(sessions)
  }, [sessions])

  const updateActive = useCallback(
    (updater: (s: Session) => Session) => {
      setSessions((prev) =>
        prev.map((s) => (s.id === activeId ? updater({ ...s, updatedAt: Date.now() }) : s)),
      )
    },
    [activeId],
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

      const patchBot = (partial: Partial<ChatMessage>) => {
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
      }

      try {
        if (!stream) {
          const res = await fetch(
            `/chat?question=${encodeURIComponent(question)}&mode=${encodeURIComponent(mode)}`,
            { signal: controller.signal },
          )
          if (!res.ok) throw new Error(`HTTP ${res.status}`)
          const data = await res.text()
          const { thinking, content } = splitThinking(data)
          patchBot({ content, thinking, typing: false, error: false, sourceQuestion: question })
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
              patchBot({ typing: false, error: false, sourceQuestion: question })
              continue
            }
            try {
              const json = JSON.parse(data) as { content?: string }
              raw += json.content || ''
              const { thinking, content } = splitThinking(raw)
              patchBot({ content, thinking, typing: true, error: false, sourceQuestion: question })
            } catch {
              /* ignore */
            }
          }
        }
        patchBot({ typing: false, error: false, sourceQuestion: question })
      } catch (err) {
        if ((err as Error).name === 'AbortError') {
          patchBot({ typing: false })
        } else {
          patchBot({
            content: `请求失败：${(err as Error).message}`,
            typing: false,
            error: true,
            sourceQuestion: question,
          })
        }
      } finally {
        setLoading(false)
        abortRef.current = null
      }
    },
    [active?.mode, activeId],
  )

  const send = useCallback(
    async (text: string, stream = true) => {
      const question = text.trim()
      if (!question || loading) return

      const userMsg: ChatMessage = {
        id: uid(),
        role: 'user',
        content: question,
        createdAt: Date.now(),
      }
      const botId = uid()
      const botMsg: ChatMessage = {
        id: botId,
        role: 'assistant',
        content: '',
        thinking: '',
        typing: true,
        sourceQuestion: question,
        createdAt: Date.now(),
      }

      updateActive((s) => ({
        ...s,
        title: s.messages.length === 0 ? question.slice(0, 24) : s.title,
        messages: [...s.messages, userMsg, botMsg],
      }))

      await requestAssistant(question, botId, stream)
    },
    [loading, requestAssistant, updateActive],
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
      const question = (target.sourceQuestion || prevUser?.content || '').trim()
      if (!question) return

      // 自我一致性消息走专用重试
      if (prevUser?.content.startsWith('[自我一致性]')) {
        const plain = question.replace(/^\[自我一致性\]\s*/, '')
        updateActive((s) => ({
          ...s,
          messages: s.messages.filter((m) => m.id !== assistantId && m.id !== prevUser.id),
        }))
        // 延迟到 runSelfConsistency，由外部调用链处理
        return { type: 'self_consistency' as const, question: plain }
      }

      const botId = uid()
      updateActive((s) => ({
        ...s,
        messages: [
          ...s.messages.slice(0, idx),
          {
            id: botId,
            role: 'assistant',
            content: '',
            thinking: '',
            typing: true,
            sourceQuestion: question.replace(/^\[自我一致性\]\s*/, ''),
            createdAt: Date.now(),
          },
        ],
      }))
      await requestAssistant(question.replace(/^\[自我一致性\]\s*/, ''), botId, true)
      return { type: 'chat' as const }
    },
    [activeId, loading, requestAssistant, sessions, updateActive],
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

  const runSelfConsistency = useCallback(
    async (text: string) => {
      const question = text.trim() || '为旅行背包品牌生成一句口号'
      if (loading) return

      const userMsg: ChatMessage = {
        id: uid(),
        role: 'user',
        content: `[自我一致性] ${question}`,
        createdAt: Date.now(),
      }
      const botId = uid()
      updateActive((s) => ({
        ...s,
        title: s.messages.length === 0 ? question.slice(0, 24) : s.title,
        messages: [
          ...s.messages,
          userMsg,
          {
            id: botId,
            role: 'assistant',
            content: '自我一致性需多次调用模型，请稍候…',
            typing: true,
            sourceQuestion: question,
            createdAt: Date.now(),
          },
        ],
      }))
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
        setSessions((prev) =>
          prev.map((s) =>
            s.id === activeId
              ? {
                  ...s,
                  messages: s.messages.map((m) =>
                    m.id === botId
                      ? {
                          ...m,
                          content,
                          typing: false,
                          error: failed,
                          sourceQuestion: question,
                        }
                      : m,
                  ),
                }
              : s,
          ),
        )
      } catch (err) {
        setSessions((prev) =>
          prev.map((s) =>
            s.id === activeId
              ? {
                  ...s,
                  messages: s.messages.map((m) =>
                    m.id === botId
                      ? {
                          ...m,
                          content: `请求失败：${(err as Error).message}`,
                          typing: false,
                          error: true,
                          sourceQuestion: question,
                        }
                      : m,
                  ),
                }
              : s,
          ),
        )
      } finally {
        setLoading(false)
      }
    },
    [activeId, loading, updateActive],
  )

  const retryOrRegenerate = useCallback(
    async (assistantId: string) => {
      const result = await regenerate(assistantId)
      if (result?.type === 'self_consistency') {
        await runSelfConsistency(result.question)
      }
    },
    [regenerate, runSelfConsistency],
  )

  const runProductCopy = useCallback(
    async (product?: { name: string; features: string; audience: string }) => {
      if (loading) return
      const payload = product || {
        name: '全自动豆浆机',
        features: '1分钟速热, 20Bar高压萃取, 手机App控制',
        audience: '追求生活品质的独居白领',
      }

      const userMsg: ChatMessage = {
        id: uid(),
        role: 'user',
        content: `[电商文案] ${payload.name}｜卖点：${payload.features}｜人群：${payload.audience}`,
        createdAt: Date.now(),
      }
      const botId = uid()
      updateActive((s) => ({
        ...s,
        title: s.messages.length === 0 ? `电商文案·${payload.name}` : s.title,
        messages: [
          ...s.messages,
          userMsg,
          {
            id: botId,
            role: 'assistant',
            content: '正在按 Few-Shot + CoT 生成产品文案…',
            typing: true,
            sourceQuestion: payload.name,
            createdAt: Date.now(),
          },
        ],
      }))
      setLoading(true)

      try {
        const res = await fetch('/product_copy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        const data = await res.json()
        const content = data.error
          ? String(data.error)
          : data.result || '未生成内容'
        setSessions((prev) =>
          prev.map((s) =>
            s.id === activeId
              ? {
                  ...s,
                  messages: s.messages.map((m) =>
                    m.id === botId
                      ? {
                          ...m,
                          content,
                          typing: false,
                          error: Boolean(data.error),
                          sourceQuestion: payload.name,
                        }
                      : m,
                  ),
                }
              : s,
          ),
        )
      } catch (err) {
        setSessions((prev) =>
          prev.map((s) =>
            s.id === activeId
              ? {
                  ...s,
                  messages: s.messages.map((m) =>
                    m.id === botId
                      ? {
                          ...m,
                          content: `请求失败：${(err as Error).message}`,
                          typing: false,
                          error: true,
                          sourceQuestion: payload.name,
                        }
                      : m,
                  ),
                }
              : s,
          ),
        )
      } finally {
        setLoading(false)
      }
    },
    [activeId, loading, updateActive],
  )

  const runSocialPlan = useCallback(
    async (topic?: string) => {
      if (loading) return
      const subject = (topic || '独居女生的低成本精致生活').trim()

      const userMsg: ChatMessage = {
        id: uid(),
        role: 'user',
        content: `[社交策划] ${subject}`,
        createdAt: Date.now(),
      }
      const botId = uid()
      updateActive((s) => ({
        ...s,
        title: s.messages.length === 0 ? `社交策划·${subject.slice(0, 16)}` : s.title,
        messages: [
          ...s.messages,
          userMsg,
          {
            id: botId,
            role: 'assistant',
            content: '阶段 1/4：正在发散策划分支…',
            typing: true,
            sourceQuestion: subject,
            createdAt: Date.now(),
          },
        ],
      }))
      setLoading(true)

      const patch = (content: string, typing = true, error = false) => {
        setSessions((prev) =>
          prev.map((s) =>
            s.id === activeId
              ? {
                  ...s,
                  messages: s.messages.map((m) =>
                    m.id === botId
                      ? { ...m, content, typing, error, sourceQuestion: subject }
                      : m,
                  ),
                }
              : s,
          ),
        )
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
                // 进度提示 vs 正式结果：短提示只更新状态，长内容写入章节
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
        if (sections.length) {
          patch(sections.join('\n\n---\n\n'), false)
        }
      } catch (err) {
        patch(`请求失败：${(err as Error).message}`, false, true)
      } finally {
        setLoading(false)
      }
    },
    [activeId, loading, updateActive],
  )

  return {
    sessions,
    active,
    activeId,
    setActiveId,
    loading,
    newChat,
    deleteSession,
    setMode,
    send,
    stop,
    runSelfConsistency,
    runProductCopy,
    runSocialPlan,
    regenerate: retryOrRegenerate,
    toggleLike,
  }
}
