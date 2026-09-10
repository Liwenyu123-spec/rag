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
import { apiFetch } from '../lib/api'
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
    title: 'æ°å¯¹è¯?,
    updatedAt: Date.now(),
    messages: [],
    mode,
  }
}

function formatCompare(results: Record<string, string>, modes: PromptMode[]) {
  return modes
    .map((m) => `### ${MODE_LABELS[m] || m}\n\n${results[m] || 'ï¼æ ç»æï¼?}`)
    .join('\n\n---\n\n')
}

function formatToolSteps(
  steps: Array<{ type: string; name?: string; arg?: string; result?: string; content?: string }>,
  answer: string,
) {
  const parts: string[] = []
  for (const s of steps) {
    if (s.type === 'tool') {
      parts.push(`**è°ç¨å·¥å·** \`${s.name}\`\n- åæ°ï¼?{s.arg}\n- ç»æï¼?{s.result}`)
    }
  }
  parts.push(`### æç»åç­\n\n${answer}`)
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
    void apiFetch('/system_prompt', {
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
      await apiFetch('/reset', { method: 'POST' })
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
    const res = await apiFetch('/system_prompt', {
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
          const res = await apiFetch(
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

        const resp = await apiFetch(
          `/stream_chat?question=${encodeURIComponent(question)}&mode=${encodeURIComponent(mode)}`,
          { signal: controller.signal },
        )
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const reader = resp.body?.getReader()
        if (!reader) throw new Error('æ æ³è¯»åæµå¼ååº')

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
            content: `è¯·æ±å¤±è´¥ï¼?{(err as Error).message}`,
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
      const question = text.trim() || 'ä¸ºæè¡èååççæä¸å¥å£å?
      if (loading) return

      const botId = pushPair(`[èªæä¸è´æ§] ${question}`, {
        kind: 'self_consistency',
        sourceQuestion: question,
        meta: { question },
        content: 'èªæä¸è´æ§éå¤æ¬¡è°ç¨æ¨¡åï¼è¯·ç¨åâ?,
      }, question)

      setLoading(true)
      try {
        const res = await apiFetch(
          `/self_consistency?question=${encodeURIComponent(question)}&num=2`,
        )
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        const data = await res.json()
        const failed = Boolean(data.error)
        const content = data.error
          ? String(data.error)
          : `åéæ¹æ¡ï¼\n${(data.candidates || [])
              .map((c: string, i: number) => `${i + 1}. ${c}`)
              .join('\n')}\n\næç»è¯éï¼\n${data.final || ''}`
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
          content: `è¯·æ±å¤±è´¥ï¼?{(err as Error).message}`,
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
        name: 'å¨èªå¨è±æµæº',
        features: '1åééç­, 20Baré«åèå, ææºAppæ§å¶',
        audience: 'è¿½æ±çæ´»åè´¨çç¬å±ç½é¢?,
      }

      const botId = pushPair(
        `[çµåææ¡] ${payload.name}ï½åç¹ï¼${payload.features}ï½äººç¾¤ï¼${payload.audience}`,
        {
          kind: 'product_copy',
          sourceQuestion: payload.name,
          meta: { product: payload },
          content: 'æ­£å¨æ?Few-Shot + CoT çæäº§åææ¡â?,
        },
        `çµåææ¡Â·${payload.name}`,
      )

      setLoading(true)
      try {
        const res = await apiFetch('/product_copy', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload),
        })
        const data = await res.json()
        patchBotMessage(botId, {
          content: data.error ? String(data.error) : data.result || 'æªçæåå®?,
          typing: false,
          error: Boolean(data.error),
          kind: 'product_copy',
          sourceQuestion: payload.name,
          meta: { product: payload },
        })
      } catch (err) {
        patchBotMessage(botId, {
          content: `è¯·æ±å¤±è´¥ï¼?{(err as Error).message}`,
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
      const subject = (topic || 'ç¬å±å¥³ççä½ææ¬ç²¾è´çæ´»').trim()

      const botId = pushPair(
        `[ç¤¾äº¤ç­å] ${subject}`,
        {
          kind: 'social_plan',
          sourceQuestion: subject,
          meta: { topic: subject },
          content: 'é¶æ®µ 1/4ï¼æ­£å¨åæ£ç­ååæ¯â?,
        },
        `ç¤¾äº¤ç­åÂ·${subject.slice(0, 16)}`,
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
        const resp = await apiFetch(
          `/social_plan_stream?topic=${encodeURIComponent(subject)}`,
        )
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`)
        const reader = resp.body?.getReader()
        if (!reader) throw new Error('æ æ³è¯»åæµå¼ååº')

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
              patch(sections.join('\n\n---\n\n') || 'ç­åå®æ', false, false)
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
                patch(json.content || 'ç­åå¤±è´¥', false, true)
                continue
              }
              if (json.content && json.title) {
                if (json.content.length < 40 && !json.done) {
                  patch(
                    `${sections.length ? sections.join('\n\n---\n\n') + '\n\n---\n\n' : ''}é¶æ®µ ${json.stage}/4ï¼?{json.content}`,
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
        patch(`è¯·æ±å¤±è´¥ï¼?{(err as Error).message}`, false, true)
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
        `[æ¨¡å¼å¯¹æ¯] ${q}`,
        {
          kind: 'compare',
          sourceQuestion: q,
          meta: { question: q, modes },
          content: `æ­£å¨å¯¹æ¯ ${modes.map((m) => MODE_LABELS[m]).join(' / ')}ï¼è¯·ç¨åâ¦`,
        },
        `å¯¹æ¯Â·${q.slice(0, 16)}`,
      )

      setLoading(true)
      try {
        const res = await apiFetch('/compare', {
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
          content: `è¯·æ±å¤±è´¥ï¼?{(err as Error).message}`,
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
        `[å·¥å·è°ç¨] ${q}`,
        {
          kind: 'tool_chat',
          sourceQuestion: q,
          meta: { question: q },
          content: 'æ­£å¨æ?ReAct å³å®æ¯å¦è°ç¨å·¥å·â?,
        },
        `å·¥å·Â·${q.slice(0, 16)}`,
      )

      setLoading(true)
      try {
        const res = await apiFetch('/tool_chat', {
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
          content: `è¯·æ±å¤±è´¥ï¼?{(err as Error).message}`,
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
