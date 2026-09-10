import { Bot } from 'lucide-react'
import type { ChatMessage } from '../types'
import { MarkdownContent } from './MarkdownContent'
import { ThinkingBlock } from './ThinkingBlock'
import clsx from 'clsx'

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="animate-fade-up flex justify-end">
        <div className="bubble-user max-w-[70%] px-4 py-2.5 whitespace-pre-wrap">
          {message.content}
        </div>
      </div>
    )
  }

  return (
    <div className="animate-fade-up flex items-start gap-3">
      <div className="mt-0.5 flex h-8 w-8 shrink-0 items-center justify-center rounded-full bg-ds-blue text-white shadow-sm">
        <Bot size={16} />
      </div>
      <div className="bubble-assistant min-w-0 max-w-[70%] px-4 py-2.5 text-ds-text">
        {(message.thinking || (message.typing && !message.content)) && (
          <ThinkingBlock thinking={message.thinking || ''} streaming={message.typing} />
        )}
        <div className={clsx(message.typing && 'typing-caret')}>
          {message.content ? (
            <MarkdownContent content={message.content} />
          ) : message.typing ? (
            <span className="text-ds-muted">正在生成…</span>
          ) : null}
        </div>
      </div>
    </div>
  )
}
