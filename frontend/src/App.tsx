import { ArrowDown } from 'lucide-react'
import { useCallback, useEffect, useRef, useState } from 'react'
import { useBackendStatus } from './hooks/useBackendStatus'
import { useBridgeHeartbeat } from './hooks/useBridgeHeartbeat'
import { useChat } from './hooks/useChat'
import { useTheme } from './hooks/useTheme'
import { useWallpaper } from './hooks/useWallpaper'
import { getOllamaThink, setOllamaThink } from './lib/api'
import { Composer } from './components/Composer'
import {
  CompareModal,
  ProductCopyModal,
  SloganModal,
  SocialPlanModal,
  SystemPromptModal,
  TemplatePickerModal,
  ToolChatModal,
} from './components/DemoFormModal'
import { EmptyState, ModeSelect, OllamaModelSelect, ThinkToggle } from './components/EmptyState'
import { MessageBubble } from './components/MessageBubble'
import { OllamaSetupBanner } from './components/OllamaSetupBanner'
import { MobileMenuButton, Sidebar } from './components/Sidebar'
import { WallpaperModal } from './components/WallpaperModal'
import { downloadText, sessionToMarkdown } from './lib/export'
import type { ChatMessage } from './types'

const BOTTOM_THRESHOLD = 80

export default function App() {
  const { dark, toggle } = useTheme()
  const chat = useChat()
  const {
    status: backend,
    models: ollamaModels,
    model: ollamaModel,
    selectModel,
    refresh: refreshBackend,
    isBrowserOllama,
  } = useBackendStatus()
  useBridgeHeartbeat(Boolean(isBrowserOllama && backend?.ok))
  const { wallpaper, setFromFile, clear: clearWallpaper, setDim } = useWallpaper()
  const [input, setInput] = useState('')
  const [mobileOpen, setMobileOpen] = useState(false)
  const [collapsed, setCollapsed] = useState(false)
  const [stickToBottom, setStickToBottom] = useState(true)
  const [showJump, setShowJump] = useState(false)
  const [productOpen, setProductOpen] = useState(false)
  const [socialOpen, setSocialOpen] = useState(false)
  const [sloganOpen, setSloganOpen] = useState(false)
  const [compareOpen, setCompareOpen] = useState(false)
  const [toolOpen, setToolOpen] = useState(false)
  const [systemOpen, setSystemOpen] = useState(false)
  const [templateOpen, setTemplateOpen] = useState(false)
  const [wallpaperOpen, setWallpaperOpen] = useState(false)
  const [thinkOn, setThinkOn] = useState(() => getOllamaThink())
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

  useEffect(() => {
    setStickToBottom(true)
    setShowJump(false)
    requestAnimationFrame(() => scrollToBottom(false))
  }, [chat.activeId, scrollToBottom])

  const messages: ChatMessage[] = chat.active?.messages ?? []

  const continueFrom = (content: string) => {
    setInput(
      `请基于以下内容继续帮我优化/展开，保留可执行细节：\n\n${content.slice(0, 3500)}`,
    )
    setStickToBottom(true)
  }

  return (
    <div
      className={`app-shell flex h-full text-body${wallpaper.src ? ' has-wallpaper' : ''}`}
    >
      {wallpaper.src && (
        <div
          className="wallpaper-layer"
          style={
            wallpaper.kind === 'image'
              ? { backgroundImage: `url(${wallpaper.src})` }
              : undefined
          }
          aria-hidden="true"
        >
          {wallpaper.kind === 'video' && (
            <video
              className="wallpaper-video"
              src={wallpaper.src}
              autoPlay
              muted
              loop
              playsInline
            />
          )}
          <div className="wallpaper-dim" style={{ opacity: wallpaper.dim }} />
        </div>
      )}
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
        onWallpaper={() => setWallpaperOpen(true)}
        onEditSystem={() => setSystemOpen(true)}
        onExportSession={() => {
          if (!chat.active) return
          const md = sessionToMarkdown(chat.active)
          const stamp = new Date().toISOString().slice(0, 10)
          downloadText(`${chat.active.title || 'chat'}-${stamp}.md`, md)
        }}
      />

      <main className="relative flex min-h-0 min-w-0 flex-1 flex-col">
        <OllamaSetupBanner
          ok={isBrowserOllama ? backend?.ok : true}
          hint={backend?.hint}
          onRetry={() => void refreshBackend()}
        />
        <header className="glass-header flex h-14 shrink-0 items-center justify-between border-b px-4">
          <div className="flex items-center gap-2">
            <MobileMenuButton onClick={() => setMobileOpen(true)} />
            <div>
              <div className="text-sm text-title">DeepSeek 助手</div>
              <div className="text-[11px] text-aux">
                {backend?.backend === 'ollama'
                  ? `本地 Ollama · ${backend.model || '模型'}${
                      backend.ok && backend.model_ready === false
                        ? ' · 模型未就绪'
                        : backend.ok
                          ? ' · 已连接'
                          : ' · 未连接'
                    }`
                  : backend?.backend === 'deepseek'
                    ? `云端 DeepSeek · ${backend.model || ''}`
                    : backend?.ok === false
                      ? '后端未连接'
                      : '提示词策略 · 工具演示'}
              </div>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {isBrowserOllama && (
              <>
                <ThinkToggle
                  on={thinkOn}
                  onChange={(v) => {
                    setOllamaThink(v)
                    setThinkOn(v)
                  }}
                />
                <OllamaModelSelect
                  value={ollamaModel}
                  models={ollamaModels}
                  onChange={selectModel}
                />
              </>
            )}
            <ModeSelect value={chat.active?.mode ?? 'zero_shot'} onChange={chat.setMode} />
          </div>
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
              onSelfConsistency={() => setSloganOpen(true)}
              onProductCopy={() => setProductOpen(true)}
              onSocialPlan={() => setSocialOpen(true)}
              onCompare={() => setCompareOpen(true)}
              onToolChat={() => setToolOpen(true)}
              onTemplates={() => setTemplateOpen(true)}
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
                  onContinue={continueFrom}
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
      <SloganModal
        open={sloganOpen}
        onClose={() => setSloganOpen(false)}
        onSubmit={(q) => {
          setSloganOpen(false)
          setStickToBottom(true)
          void chat.runSelfConsistency(q)
        }}
      />
      <CompareModal
        open={compareOpen}
        onClose={() => setCompareOpen(false)}
        onSubmit={(q, modes) => {
          setCompareOpen(false)
          setStickToBottom(true)
          void chat.runCompare(q, modes)
        }}
      />
      <ToolChatModal
        open={toolOpen}
        onClose={() => setToolOpen(false)}
        onSubmit={(q) => {
          setToolOpen(false)
          setStickToBottom(true)
          void chat.runToolChat(q)
        }}
      />
      <SystemPromptModal
        open={systemOpen}
        value={chat.systemPrompt}
        onClose={() => setSystemOpen(false)}
        onSubmit={(content) => {
          void chat.saveSystemPrompt(content).then(() => setSystemOpen(false))
        }}
      />
      <TemplatePickerModal
        open={templateOpen}
        onClose={() => setTemplateOpen(false)}
        onPick={(prompt) => {
          setTemplateOpen(false)
          setInput(prompt)
        }}
      />
      <WallpaperModal
        open={wallpaperOpen}
        hasWallpaper={Boolean(wallpaper.src)}
        kind={wallpaper.kind}
        dim={wallpaper.dim}
        onClose={() => setWallpaperOpen(false)}
        onPickFile={setFromFile}
        onClear={clearWallpaper}
        onDim={setDim}
      />
    </div>
  )
}
