import { ChevronDown, ChevronRight, Sparkles } from 'lucide-react'
import { useState } from 'react'

export function ThinkingBlock({ thinking, streaming }: { thinking: string; streaming?: boolean }) {
  const [open, setOpen] = useState(false)
  if (!thinking && !streaming) return null

  return (
    <div className="mb-2 overflow-hidden rounded-[16px] border border-white/10 bg-white/5 shadow-[0_12px_32px_rgba(0,0,0,0.22)] backdrop-blur-md">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="flex w-full items-center gap-2 px-3 py-2 text-left text-[13px] text-aux transition hover:text-[#e8eefc]"
      >
        {open ? <ChevronDown size={14} /> : <ChevronRight size={14} />}
        <Sparkles size={14} className="text-ds-blue" />
        <span>{streaming && !thinking.includes('\n') ? '正在深度思考…' : '已深度思考'}</span>
      </button>
      {open && (
        <div className="border-t border-white/10 px-3 py-2 text-[13px] leading-6 text-aux whitespace-pre-wrap">
          {thinking || '…'}
        </div>
      )}
    </div>
  )
}
