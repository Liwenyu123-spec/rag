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
      /* 后端未启动时仍允许本地新建 */
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
        createdAt: Date.now(),
      }

      updateActive((s) => ({
        ...s,
        title: s.messages.length === 0 ? question.slice(0, 24) : s.title,
        messages: [...s.messages, userMsg, botMsg],
      }))

      setLoading(true)
      const mode = active?.mode ?? 'zero_shot'
      const controller = new AbortController()
      abortRef.current = controller

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
          const data = await res.text()
          const { thinking, content } = splitThinking(data)
          patchBot({ content, thinking, typing: false })
          return
        }

        const resp = await fetch(
          `/stream_chat?question=${encodeURIComponent(question)}&mode=${encodeURIComponent(mode)}`,
          { signal: controller.signal },
        )
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
              patchBot({ typing: false })
              continue
            }
            try {
              const json = JSON.parse(data) as { content?: string }
              raw += json.content || ''
              const { thinking, content } = splitThinking(raw)
              patchBot({ content, thinking, typing: true })
            } catch {
              /* ignore parse errors */
            }
          }
        }
        patchBot({ typing: false })
      } catch (err) {
        if ((err as Error).name === 'AbortError') {
          patchBot({ typing: false })
        } else {
          patchBot({
            content: `请求失败：${(err as Error).message}`,
            typing: false,
          })
        }
      } finally {
        setLoading(false)
        abortRef.current = null
      }
    },
    [active?.mode, activeId, loading, updateActive],
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
            createdAt: Date.now(),
          },
        ],
      }))
      setLoading(true)

      try {
        const res = await fetch(
          `/self_consistency?question=${encodeURIComponent(question)}&num=2`,
        )
        const data = await res.json()
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
                    m.id === botId ? { ...m, content, typing: false } : m,
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
                      ? { ...m, content: `请求失败：${(err as Error).message}`, typing: false }
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
  }
}
