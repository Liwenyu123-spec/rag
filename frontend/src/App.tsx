import { useEffect, useRef, useState } from 'react'
import { useChat } from '../hooks/useChat'
import { useTheme } from '../hooks/useTheme'
import { Composer } from './Composer'
import { EmptyState, ModeSelect } from './EmptyState'
import { MessageBubble } from './MessageBubble'
import { MobileMenuButton, Sidebar } from './Sidebar'

export default function App() {
  const { dark, toggle } = useTheme()
  const chat = useChat()
  const [input, setInput] = useState('')
  const [mobileOpen, setMobileOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const listRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = listRef.current
    if (!el) return
    requestAnimationFrame(() => {
      el.scrollTop = el.scrollHeight
    })
  }, [chat.active?.messages, chat.loading])

  const messages = chat.active?.messages ?? []

  return (
    <div className="flex h-full bg-ds-bg text-ds-text">
      <Sidebar
        open={mobileOpen}
        collapsed={collapsed}
        sessions={chat.sessions}
        activeId={chat.activeId}
        dark={dark}
        onToggleDark={toggle}
        onSelect={chat.setActiveId}
        onNew={chat.newChat}
        onDelete={chat.deleteSession}
        onCloseMobile={() => setMobileOpen(false)}
        onToggleCollapse={() => setCollapsed((v) => !v)}
      />

      <main className="flex min-h-0 min-w-0 flex-1 flex-col">
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-ds-border px-4">
          <div className="flex items-center gap-2">
            <MobileMenuButton onClick={() => setMobileOpen(true)} />
            <div>
              <div className="text-sm font-semibold">DeepSeek 助手</div>
              <div className="text-[11px] text-ds-muted">提示词策略 · 安全防护</div>
            </div>
          </div>
          <ModeSelect value={chat.active?.mode ?? 'zero_shot'} onChange={chat.setMode} />
        </header>

        <div ref={listRef} className="min-h-0 flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <EmptyState
              onPick={(text) => {
                void chat.send(text, true)
              }}
              onSelfConsistency={() => chat.runSelfConsistency('为旅行背包品牌生成一句口号')}
            />
          ) : (
            <div className="mx-auto flex w-full max-w-[768px] flex-col gap-5 px-4 py-6">
              {messages.map((m) => (
                <MessageBubble key={m.id} message={m} />
              ))}
            </div>
          )}
        </div>

        <Composer
          value={input}
          onChange={setInput}
          loading={chat.loading}
          onStop={chat.stop}
          onSend={() => {
            const text = input
            setInput('')
            void chat.send(text, true)
          }}
        />
      </main>
    </div>
  )
}
