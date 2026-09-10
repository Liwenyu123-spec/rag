import { ImagePlus, Trash2 } from 'lucide-react'
import { useRef, useState } from 'react'
import { fieldClass, ModalShell } from './DemoFormModal'

export function WallpaperModal({
  open,
  hasWallpaper,
  kind,
  dim,
  onClose,
  onPickFile,
  onClear,
  onDim,
}: {
  open: boolean
  hasWallpaper: boolean
  kind: 'image' | 'video' | null
  dim: number
  onClose: () => void
  onPickFile: (file: File) => Promise<void>
  onClear: () => void
  onDim: (v: number) => void
}) {
  const inputRef = useRef<HTMLInputElement>(null)
  const [error, setError] = useState('')
  const [busy, setBusy] = useState(false)

  if (!open) return null

  return (
    <ModalShell title="聊天壁纸" onClose={onClose}>
      <p className="mb-4 text-[13px] text-aux">
        支持本地图片或视频作背景（非 Windows 桌面）。视频会静音循环播放；文件存在浏览器
        IndexedDB，刷新后仍可用。图片建议 &lt; 2.5MB，视频建议短循环 mp4 / webm，&lt; 40MB。
      </p>

      <input
        ref={inputRef}
        type="file"
        accept="image/*,video/mp4,video/webm,video/ogg,.mp4,.webm,.ogg"
        className="hidden"
        onChange={async (e) => {
          const file = e.target.files?.[0]
          e.target.value = ''
          if (!file) return
          setBusy(true)
          setError('')
          try {
            await onPickFile(file)
          } catch (err) {
            setError((err as Error).message)
          } finally {
            setBusy(false)
          }
        }}
      />

      <button
        type="button"
        disabled={busy}
        onClick={() => inputRef.current?.click()}
        className="btn-motion btn-primary mb-3 flex w-full items-center justify-center gap-2 rounded-[12px] bg-[#4d6bfe] px-3 py-2.5 text-[13px] text-white disabled:opacity-50"
      >
        <ImagePlus size={16} />
        {busy
          ? '保存中…'
          : hasWallpaper
            ? `更换${kind === 'video' ? '视频' : '图片'}`
            : '选择图片 / 视频'}
      </button>

      {hasWallpaper && (
        <>
          <p className="mb-2 text-[12px] text-aux">
            当前：{kind === 'video' ? '视频壁纸' : '图片壁纸'}
          </p>
          <label className="mb-3 block">
            <span className="mb-1.5 flex items-center justify-between text-[12px] text-aux">
              <span>遮罩浓度（越高字越清晰）</span>
              <span>{Math.round(dim * 100)}%</span>
            </span>
            <input
              type="range"
              min={0.15}
              max={0.8}
              step={0.05}
              value={dim}
              onChange={(e) => onDim(Number(e.target.value))}
              className="w-full accent-[#4d6bfe]"
            />
          </label>
          <button
            type="button"
            onClick={() => void onClear()}
            className="btn-motion btn-ghost mb-3 flex w-full items-center justify-center gap-2 rounded-[12px] border border-[var(--border-soft)] px-3 py-2 text-[13px] text-body"
          >
            <Trash2 size={14} />
            清除壁纸
          </button>
        </>
      )}

      {error && <p className="mb-3 text-[12px] text-red-500">{error}</p>}

      <div className="flex justify-end">
        <button
          type="button"
          onClick={onClose}
          className={`${fieldClass} !w-auto cursor-pointer px-3.5 py-2 text-[13px]`}
        >
          完成
        </button>
      </div>
    </ModalShell>
  )
}
