import { ArrowDown } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useChat } from './hooks/useChat'
import { useTheme } from './hooks/useTheme'
import { Composer } from './components/Composer'
import {
  ProductCopyModal,
  SocialPlanModal,
} from './components/DemoFormModal'
import { EmptyState, ModeSelect } from './components/EmptyState'
import { MessageBubble } from './components/MessageBubble'
import { MobileMenuButton, Sidebar } from './components/Sidebar'
import type { ChatMessage } from './types'

const BOTTOM_THRESHOLD = 80

export default function App() {
  const { dark, toggle } = useTheme()
  const chat = useChat()
  const [input, setInput] = useState('')
  const [mobileOpen, setMobileOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [stickToBottom, setStickToBottom] = useState(true)
  const [showJump, setShowJump] = useState(false)
  const [productOpen, setProductOpen] = useState(false)
  const [socialOpen, setSocialOpen] = useState(false)
  const listRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = useCallback((smooth = false) => {
    const el = listRef.current
    if (!el) return
    el.scrollTo({
      top: el.scrollHeight,
      behavior: smooth ? 'smooth' : 'auto',
    })
  }, [])

  const onListScroll = () => {
    const el = listRef.current
    if (!el) return
    const distance = el.scrollHeight - el.scrollTop - el.clientHeight
    const nearBottom = distance < BOTTOM_THRESHOLD
    setStickToBottom(nearBottom)
    setShowJump(!nearBottom && (chat.active?.messages.length ?? 0) > 0)
  }

  useEffect(() => {
    if (!stickToBottom) return
    requestAnimationFrame(() => scrollToBottom(false))
  }, [chat.active?.messages, chat.loading, stickToBottom, scrollToBottom])

  // 切换会话时回到底部跟踪
  useEffect(() => {
    setStickToBottom(true)
    setShowJump(false)
    requestAnimationFrame(() => scrollToBottom(false))
  }, [chat.activeId, scrollToBottom])

  const messages: ChatMessage[] = chat.active?.messages ?? []

  return (
    <div className="app-shell flex h-full text-body">
      <div className="ambient-orbs" aria-hidden="true">
        <div className="orb orb-blue" />
        <div className="orb orb-purple" />
      </div>
      <div className="noise-layer" aria-hidden="true" />

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

      <main className="relative flex min-h-0 min-w-0 flex-1 flex-col">
        <header className="glass-header flex h-14 shrink-0 items-center justify-between border-b px-4">
          <div className="flex items-center gap-2">
            <MobileMenuButton onClick={() => setMobileOpen(true)} />
            <div>
              <div className="text-sm text-title">DeepSeek 助手</div>
              <div className="text-[11px] text-aux">提示词策略 · 安全防护</div>
            </div>
          </div>
          <ModeSelect value={chat.active?.mode ?? 'zero_shot'} onChange={chat.setMode} />
        </header>

        <div
          ref={listRef}
          onScroll={onListScroll}
          className="chat-canvas min-h-0 flex-1 overflow-y-auto"
        >
          {messages.length === 0 ? (
            <EmptyState
              onPick={(text: string) => {
                setStickToBottom(true)
                void chat.send(text, true)
              }}
              onSelfConsistency={() => {
                setStickToBottom(true)
                void chat.runSelfConsistency('为旅行背包品牌生成一句口号')
              }}
              onProductCopy={() => setProductOpen(true)}
              onSocialPlan={() => setSocialOpen(true)}
            />
          ) : (
            <div className="mx-auto flex w-full max-w-[768px] flex-col gap-6 px-4 py-6">
              {messages.map((m) => (
                <MessageBubble
                  key={m.id}
                  message={m}
                  loading={chat.loading}
                  onRegenerate={chat.regenerate}
                  onLike={chat.toggleLike}
                />
              ))}
            </div>
          )}
        </div>

        {showJump && (
          <button
            type="button"
            onClick={() => {
              setStickToBottom(true)
              setShowJump(false)
              scrollToBottom(true)
            }}
            className="btn-motion btn-ghost absolute bottom-28 right-6 z-20 inline-flex h-10 items-center gap-1.5 rounded-full border px-3 text-[13px] text-body"
          >
            <ArrowDown size={16} />
            回到底部
          </button>
        )}

        <Composer
          value={input}
          onChange={setInput}
          loading={chat.loading}
          onStop={chat.stop}
          onSend={() => {
            const text = input
            setInput('')
            setStickToBottom(true)
            void chat.send(text, true)
          }}
        />
      </main>

      <ProductCopyModal
        open={productOpen}
        onClose={() => setProductOpen(false)}
        onSubmit={(product) => {
          setProductOpen(false)
          setStickToBottom(true)
          void chat.runProductCopy(product)
        }}
      />
      <SocialPlanModal
        open={socialOpen}
        onClose={() => setSocialOpen(false)}
        onSubmit={(topic) => {
          setSocialOpen(false)
          setStickToBottom(true)
          void chat.runSocialPlan(topic)
        }}
      />
    </div>
  )
}
