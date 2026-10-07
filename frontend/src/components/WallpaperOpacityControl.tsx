import { ImagePlus, Trash2, X } from 'lucide-react'
import { useEffect, useId, useRef, useState } from 'react'

/** 遮罩浓度 ↔ 壁纸可见度：dim 越高，壁纸越淡、文字越清晰 */
function dimToVisibility(dim: number) {
  return Math.round((1 - dim) * 100)
}

function visibilityToDim(visibilityPct: number) {
  return 1 - visibilityPct / 100
}

export function WallpaperFab({
  hasWallpaper,
  kind,
  dim,
  onOpenModal,
  onDim,
  onClear,
}: {
  hasWallpaper: boolean
  kind: 'image' | 'video' | null
  dim: number
  onOpenModal: () => void
  onDim: (v: number) => void
  onClear: () => void
}) {
  const [open, setOpen] = useState(false)
  const rootRef = useRef<HTMLDivElement>(null)
  const panelId = useId()
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
    <div ref={rootRef} className="wallpaper-fab-root pointer-events-auto fixed bottom-[7.5rem] right-5 z-40 md:bottom-28">
      {open && (
        <div
          id={panelId}
          className="glass-panel mb-3 w-[260px] rounded-[18px] border border-white/15 p-3.5 shadow-[0_20px_50px_rgba(0,0,0,0.4)]"
        >
          <div className="mb-3 flex items-center justify-between">
            <div className="text-[14px] font-medium text-title">聊天壁纸</div>
            <button
              type="button"
              onClick={() => setOpen(false)}
              className="btn-motion btn-ghost rounded-[10px] p-1 text-aux hover:text-body"
              aria-label="关闭"
            >
              <X size={16} />
            </button>
          </div>

          <p className="mb-3 text-[12px] leading-5 text-aux">
            {hasWallpaper
              ? `当前：${kind === 'video' ? '视频' : '图片'}壁纸 · 可调透明度`
              : '还没有壁纸，先从本地上传图片或视频'}
          </p>

          <button
            type="button"
            onClick={() => {
              setOpen(false)
              onOpenModal()
            }}
            className="btn-motion btn-primary mb-3 flex w-full items-center justify-center gap-2 rounded-[12px] bg-[#4d6bfe] px-3 py-2.5 text-[13px] text-white"
          >
            <ImagePlus size={16} />
            {hasWallpaper ? '更换图片 / 视频' : '上传图片 / 视频'}
          </button>

          <label className={`mb-2 block ${hasWallpaper ? '' : 'pointer-events-none opacity-40'}`}>
            <span className="mb-1.5 flex items-center justify-between text-[12px] text-aux">
              <span>壁纸透明度</span>
              <span className="tabular-nums text-body">{visibility}%</span>
            </span>
            <input
              type="range"
              min={20}
              max={90}
              step={5}
              value={visibility}
              disabled={!hasWallpaper}
              onChange={(e) => onDim(visibilityToDim(Number(e.target.value)))}
              className="w-full accent-[#4d6bfe]"
              aria-label="壁纸透明度"
            />
            <span className="mt-1 flex justify-between text-[11px] text-aux">
              <span>更淡</span>
              <span>更清晰</span>
            </span>
          </label>

          {hasWallpaper && (
            <button
              type="button"
              onClick={() => void onClear()}
              className="btn-motion btn-ghost mt-2 flex w-full items-center justify-center gap-2 rounded-[12px] border border-[var(--border-soft)] px-3 py-2 text-[13px] text-body"
            >
              <Trash2 size={14} />
              清除壁纸
            </button>
          )}
        </div>
      )}

      <button
        type="button"
        onClick={() => setOpen((v) => !v)}
        className={`btn-motion flex h-12 items-center gap-2 rounded-full border px-4 text-[13px] font-medium shadow-[0_12px_32px_rgba(0,0,0,0.35)] ${
          hasWallpaper
            ? 'border-[#4d6bfe]/70 bg-[#4d6bfe] text-white'
            : 'border-white/15 bg-black/55 text-white backdrop-blur-md dark:bg-white/10'
        }`}
        aria-expanded={open}
        aria-controls={panelId}
        title="聊天壁纸与透明度"
      >
        <ImagePlus size={18} />
        壁纸
        {hasWallpaper && (
          <span className="rounded-full bg-white/20 px-1.5 py-0.5 text-[11px] tabular-nums">
            {visibility}%
          </span>
        )}
      </button>
    </div>
  )
}

/** @deprecated 保留旧名导出，避免其它引用报错 */
export function WallpaperOpacityControl(props: {
  dim: number
  onDim: (v: number) => void
}) {
  const visibility = dimToVisibility(props.dim)
  return (
    <label className="inline-flex items-center gap-2 rounded-[12px] border border-[#4d6bfe]/60 px-2.5 py-1.5 text-[12px] text-[#93a8ff]">
      <span className="whitespace-nowrap">透明度</span>
      <input
        type="range"
        min={20}
        max={90}
        step={5}
        value={visibility}
        onChange={(e) => props.onDim(visibilityToDim(Number(e.target.value)))}
        className="w-[88px] accent-[#4d6bfe]"
        aria-label="壁纸透明度"
      />
      <span className="w-8 tabular-nums">{visibility}%</span>
    </label>
  )
}
