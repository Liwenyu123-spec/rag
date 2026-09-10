import clsx from 'clsx'
import { Copy, Download, MessageSquareQuote, RefreshCw, ThumbsUp } from 'lucide-react'
import { useState } from 'react'
import type { ChatMessage } from '../types'
import {
  downloadText,
  messageExportName,
  productCopyToTableMarkdown,
} from '../lib/export'
import { MarkdownContent } from './MarkdownContent'
import { ThinkingBlock } from './ThinkingBlock'

function AssistantAvatar() {
  return (
    <div className="avatar-assistant mt-0.5" aria-hidden>
      ✦
    </div>
  )
}

function UserAvatar({ content }: { content: string }) {
  const letter = (content.trim()[0] || '我').toUpperCase()
  return (
    <div className="avatar-user mt-0.5" aria-hidden>
      {letter}
    </div>
  )
}

function ActionBar({
  liked,
  onCopy,
  onDownload,
  onRegenerate,
  onLike,
  onContinue,
}: {
  liked?: boolean
  onCopy: () => void
  onDownload?: () => void
  onRegenerate?: () => void
  onLike?: () => void
  onContinue?: () => void
}) {
  return (
    <div className="msg-actions absolute -top-2 right-0 z-10 flex items-center gap-1 rounded-[12px] border px-1.5 py-1 opacity-0 shadow-[0_12px_32px_rgba(15,23,42,0.12)] backdrop-blur-md transition-opacity duration-150 group-hover:opacity-100">
      <button
        type="button"
        title="复制"
        onClick={onCopy}
        className="btn-motion rounded-[10px] p-1.5 text-[var(--text-aux)] hover:bg-black/5 hover:text-[var(--text-main)] dark:hover:bg-white/10"
      >
        <Copy size={14} />
      </button>
      {onDownload && (
        <button
          type="button"
          title="导出 Markdown"
          onClick={onDownload}
          className="btn-motion rounded-[10px] p-1.5 text-[var(--text-aux)] hover:bg-black/5 hover:text-[var(--text-main)] dark:hover:bg-white/10"
        >
          <Download size={14} />
        </button>
      )}
      {onContinue && (
        <button
          type="button"
          title="基于这段继续聊"
          onClick={onContinue}
          className="btn-motion rounded-[10px] p-1.5 text-[var(--text-aux)] hover:bg-black/5 hover:text-[var(--text-main)] dark:hover:bg-white/10"
        >
          <MessageSquareQuote size={14} />
        </button>
      )}
      {onRegenerate && (
        <button
          type="button"
          title="重新生成"
          onClick={onRegenerate}
          className="btn-motion rounded-[10px] p-1.5 text-[var(--text-aux)] hover:bg-black/5 hover:text-[var(--text-main)] dark:hover:bg-white/10"
        >
          <RefreshCw size={14} />
        </button>
      )}
      {onLike && (
        <button
          type="button"
          title="点赞"
          onClick={onLike}
          className={clsx(
            'btn-motion rounded-[10px] p-1.5 hover:bg-black/5 dark:hover:bg-white/10',
            liked ? 'text-[#4d6bfe]' : 'text-[var(--text-aux)] hover:text-[var(--text-main)]',
          )}
        >
          <ThumbsUp size={14} fill={liked ? 'currentColor' : 'none'} />
        </button>
      )}
    </div>
  )
}

export function MessageBubble({
  message,
  loading,
  onRegenerate,
  onLike,
  onContinue,
}: {
  message: ChatMessage
  loading?: boolean
  onRegenerate?: (id: string) => void
  onLike?: (id: string) => void
  onContinue?: (content: string) => void
}) {
  const [copied, setCopied] = useState(false)
  const isUser = message.role === 'user'

  const copyText = async () => {
    const text = message.content || ''
    if (!text) return
    await navigator.clipboard.writeText(text)
    setCopied(true)
    setTimeout(() => setCopied(false), 1200)
  }

  const downloadMsg = () => {
    const text =
      message.kind === 'product_copy'
        ? productCopyToTableMarkdown(message.content, message.meta?.product?.name)
        : message.content
    downloadText(messageExportName(message), text)
  }

  if (isUser) {
    return (
      <div className="group relative animate-fade-up flex items-start justify-end gap-3">
        <div className="relative max-w-[70%]">
          {!message.typing && message.content && (
            <ActionBar onCopy={copyText} />
          )}
          <div className="bubble-user px-4 py-3 text-body whitespace-pre-wrap">
            {message.content}
          </div>
          {copied && (
            <span className="absolute -bottom-5 right-0 text-[11px] text-aux">已复制</span>
          )}
        </div>
        <UserAvatar content={message.content} />
      </div>
    )
  }

  const canContinue =
    Boolean(onContinue) &&
    !message.typing &&
    Boolean(message.content) &&
    (message.kind === 'social_plan' ||
      message.kind === 'product_copy' ||
      message.kind === 'compare' ||
      message.kind === 'tool_chat')

  return (
    <div className="group relative animate-fade-up flex items-start gap-3">
      <AssistantAvatar />
      <div className="relative min-w-0 max-w-[85%]">
        {!message.typing && message.content && (
          <ActionBar
            liked={message.liked}
            onCopy={copyText}
            onDownload={downloadMsg}
            onContinue={
              canContinue ? () => onContinue?.(message.content) : undefined
            }
            onRegenerate={
              onRegenerate && !loading ? () => onRegenerate(message.id) : undefined
            }
            onLike={onLike ? () => onLike(message.id) : undefined}
          />
        )}
        <div className="bubble-assistant px-4 py-3 text-body">
          {(message.thinking || (message.typing && !message.content)) && (
            <ThinkingBlock thinking={message.thinking || ''} streaming={message.typing} />
          )}
          <div className={clsx(message.typing && 'typing-caret')}>
            {message.content ? (
              <MarkdownContent content={message.content} />
            ) : message.typing ? (
              <span className="text-aux">正在生成…</span>
            ) : null}
          </div>
          {message.error && !message.typing && (
            <div className="mt-3 flex items-center gap-2 border-t border-white/10 pt-3">
              <span className="text-[13px] text-aux">生成失败</span>
              {onRegenerate && (
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => onRegenerate(message.id)}
                  className="btn-motion btn-ghost rounded-[12px] border px-3 py-1 text-[13px] text-[#e8eefc]"
                >
                  重试
                </button>
              )}
            </div>
          )}
        </div>
        {copied && (
          <span className="absolute -bottom-5 left-0 text-[11px] text-aux">已复制</span>
        )}
      </div>
    </div>
  )
}
