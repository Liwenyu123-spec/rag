import { SendHorizontal, Square } from 'lucide-react'
import { useEffect, useRef } from 'react'

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
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`
  }, [value])

  return (
    <div className="border-t border-ds-border bg-ds-bg/90 px-4 pb-[max(1rem,env(safe-area-inset-bottom))] pt-3 backdrop-blur">
      <div className="mx-auto flex max-w-[768px] items-end gap-2 rounded-2xl border border-ds-border bg-ds-subtle px-3 py-2 shadow-sm transition focus-within:border-ds-blue/50 focus-within:shadow-[0_0_0_3px_rgba(77,107,254,0.12)]">
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
          className="max-h-40 min-h-[44px] flex-1 resize-none bg-transparent py-2.5 text-[15px] leading-[1.7] text-ds-text outline-none placeholder:text-ds-muted disabled:opacity-60"
        />
        {loading ? (
          <button
            type="button"
            onClick={onStop}
            className="mb-0.5 inline-flex h-10 items-center gap-1.5 rounded-xl bg-[#ef4444] px-3 text-sm font-medium text-white transition hover:bg-[#dc2626]"
          >
            <Square size={14} fill="currentColor" />
            停止生成
          </button>
        ) : (
          <button
            type="button"
            disabled={!value.trim()}
            onClick={onSend}
            className="mb-0.5 inline-flex h-10 w-10 items-center justify-center rounded-xl bg-ds-blue text-white transition hover:bg-ds-blue-hover disabled:cursor-not-allowed disabled:bg-[#c9cdd4]"
          >
            <SendHorizontal size={18} />
          </button>
        )}
      </div>
      <p className="mx-auto mt-2 max-w-[768px] text-center text-[11px] text-ds-muted">
        Enter 发送 · Shift+Enter 换行 · AI 内容请自行核实
      </p>
    </div>
  )
}
