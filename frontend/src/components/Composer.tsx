import { SendHorizontal, Square } from 'lucide-react'
import { useEffect, useRef } from 'react'

/** 15px * 1.7 * 6 行 ≈ 153px */
const MAX_LINES = 6
const LINE_HEIGHT = 15 * 1.7
const MAX_HEIGHT = Math.round(LINE_HEIGHT * MAX_LINES)

export function Composer({
  value,
  onChange,
  onSend,
  onStop,
  loading,
}: {
  value: string
  onChange: (v: string) => void
  onSend: () => void
  onStop: () => void
  loading: boolean
}) {
  const ref = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    el.style.height = 'auto'
    const next = Math.min(el.scrollHeight, MAX_HEIGHT)
    el.style.height = `${next}px`
    el.style.overflowY = el.scrollHeight > MAX_HEIGHT ? 'auto' : 'hidden'
  }, [value])

  return (
    <div className="glass-composer-wrap border-t px-4 py-4 pb-[max(1rem,env(safe-area-inset-bottom))]">
      <div className="composer-shell mx-auto flex max-w-[768px] items-end gap-2 px-3 py-2">
        <textarea
          ref={ref}
          rows={1}
          value={value}
          disabled={loading}
          placeholder="给 DeepSeek 发送消息…"
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              onSend()
            }
          }}
          style={{ maxHeight: MAX_HEIGHT }}
          className="min-h-[44px] flex-1 resize-none bg-transparent py-2.5 text-[15px] font-normal leading-[1.7] text-[#e8eefc] outline-none placeholder:text-[#8a8f99] disabled:opacity-60"
        />
        {loading ? (
          <button
            type="button"
            onClick={onStop}
            className="btn-motion btn-danger mb-0.5 inline-flex h-10 items-center gap-1.5 rounded-[12px] bg-[#ef4444] px-3 text-sm font-normal text-white hover:bg-[#dc2626]"
          >
            <Square size={14} fill="currentColor" />
            停止生成
          </button>
        ) : (
          <button
            type="button"
            disabled={!value.trim()}
            onClick={onSend}
            className="btn-motion btn-primary mb-0.5 inline-flex h-10 w-10 items-center justify-center rounded-[12px] bg-ds-blue text-white hover:bg-ds-blue-hover disabled:cursor-not-allowed disabled:bg-[#475569] disabled:shadow-none"
          >
            <SendHorizontal size={18} />
          </button>
        )}
      </div>
      <p className="mx-auto mt-2 max-w-[768px] text-center text-[11px] text-aux">
        Enter 发送 · Shift+Enter 换行 · AI 内容请自行核实
      </p>
    </div>
  )
}
