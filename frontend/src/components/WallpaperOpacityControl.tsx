import { useEffect, useId, useRef, useState } from 'react'
import { Contrast } from 'lucide-react'

/** 遮罩浓度 ↔ 壁纸可见度：dim 越高，壁纸越淡、文字越清晰 */
function dimToVisibility(dim: number) {
  return Math.round((1 - dim) * 100)
}

function visibilityToDim(visibilityPct: number) {
  return 1 - visibilityPct / 100
}

export function WallpaperOpacityControl({
  dim,
  onDim,
}: {
  dim: number
  onDim: (v: number) => void
}) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const labelId = useId()
  const visibility = dimToVisibility(dim)

  useEffect(() => {
    if (!open) return
    const onPointer = (e: MouseEvent) => {
      if (!rootRef.current?.contains(e.target as Node)) setOpen(false)
    }
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') setOpen(false)
    }
    document.addEventListener('mousedown', onPointer)
    document.addEventListener('keydown', onKey)
    return () => {
      document.removeEventListener('mousedown', onPointer)
      document.removeEventListener('keydown', onKey)
    }
  }, [open])

  return (
    <div ref={rootRef} className="relative">
      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className="btn-motion btn-ghost inline-flex items-center gap-1.5 rounded-[12px] border border-[#4d6bfe]/60 px-2.5 py-1.5 text-[13px] text-[#93a8ff]"
        title="调节壁纸透明度"
        aria-expanded={open}
        aria-controls={labelId}
      >
        <Contrast size={15} />
        <span className="hidden sm:inline">{visibility}%</span>
      </button>

      {open && (
        <div
          id={labelId}
          className="glass-panel absolute right-0 top-[calc(100%+8px)] z-50 w-[220px] rounded-[16px] border border-white/10 p-3 shadow-[0_16px_40px_rgba(0,0,0,0.35)]"
        >
          <div className="mb-2 flex items-center justify-between text-[12px] text-aux">
            <span>壁纸透明度</span>
            <span className="tabular-nums text-body">{visibility}%</span>
          </div>
          <input
            type="range"
            min={20}
            max={90}
            step={5}
            value={visibility}
            onChange={(e) => onDim(visibilityToDim(Number(e.target.value)))}
            className="w-full accent-[#4d6bfe]"
            aria-label="壁纸透明度"
          />
          <div className="mt-1.5 flex justify-between text-[11px] text-aux">
            <span>更淡</span>
            <span>更清晰</span>
          </div>
        </div>
      )}
    </div>
  )
}
