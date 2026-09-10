import { ChevronDown, ChevronRight, Sparkles } from 'lucide-react'
import { useState } from 'react'

export function ThinkingBlock({ thinking, streaming }: { thinking: string; streaming?: boolean }) {
  const [open, setOpen] = useState(false)
  if (!thinking && !streaming) return null

  return (
    <div className="mb-2 overflow-hidden rounded-xl border border-ds-border bg-ds-subtle/80">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-[13px] text-ds-muted transition hover:text-ds-text"
      >
        {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <Sparkles size={14} className="text-ds-blue" />
        <span>{streaming && !thinking.includes('\n') ? '正在深度思考…' : '已深度思考'}</span>
      </button>
      {open && (
        <div className="border-t border-ds-border px-3 py-2 text-[13px] leading-6 text-ds-muted whitespace-pre-wrap">
          {thinking || '…'}
        </div>
      )}
    </div>
  )
}
