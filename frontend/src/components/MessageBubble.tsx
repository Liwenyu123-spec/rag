import clsx from 'clsx'
import type { ChatMessage } from '../types'
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

export function MessageBubble({ message }: { message: ChatMessage }) {
  const isUser = message.role === 'user'

  if (isUser) {
    return (
      <div className="animate-fade-up flex items-start justify-end gap-3">
        <div className="bubble-user max-w-[70%] px-4 py-3 text-body whitespace-pre-wrap">
          {message.content}
        </div>
        <UserAvatar content={message.content} />
      </div>
    )
  }

  return (
    <div className="animate-fade-up flex items-start gap-3">
      <AssistantAvatar />
      <div className="bubble-assistant min-w-0 max-w-[70%] px-4 py-3 text-body">
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
      </div>
    </div>
  )
}
