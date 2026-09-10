import { useEffect, useRef, useState, type ReactNode } from 'react'

const fieldClass =
  'w-full rounded-[12px] border border-[var(--border-soft)] bg-white/70 px-3 py-2.5 text-[14px] text-[var(--text-main)] outline-none backdrop-blur-md placeholder:text-[var(--text-aux)] focus:border-[#4d6bfe]/60 dark:bg-white/5'

type ProductForm = {
  name: string
  features: string
  audience: string
}

export function ProductCopyModal({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean
  onClose: () => void
  onSubmit: (product: ProductForm) => void
}) {
  const [form, setForm] = useState<ProductForm>({
    name: '全自动豆浆机',
    features: '1分钟速热, 20Bar高压萃取, 手机App控制',
    audience: '追求生活品质的独居白领',
  })
  const firstRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (open) firstRef.current?.focus()
  }, [open])

  if (!open) return null

  const canSubmit =
    form.name.trim() && form.features.trim() && form.audience.trim()

  return (
    <ModalShell title="demo05 · 电商文案" onClose={onClose}>
      <p className="mb-4 text-[13px] text-aux">
        填写产品信息后，用 Few-Shot + CoT 生成标题 / 正文 / 标签。
      </p>
      <label className="mb-3 block">
        <span className="mb-1.5 block text-[12px] text-aux">产品名称</span>
        <input
          ref={firstRef}
          className={fieldClass}
          value={form.name}
          onChange={(e) => setForm((f) => ({ ...f, name: e.target.value }))}
          placeholder="例如：全自动豆浆机"
        />
      </label>
      <label className="mb-3 block">
        <span className="mb-1.5 block text-[12px] text-aux">核心卖点</span>
        <textarea
          rows={3}
          className={`${fieldClass} resize-none leading-[1.6]`}
          value={form.features}
          onChange={(e) => setForm((f) => ({ ...f, features: e.target.value }))}
          placeholder="逗号分隔，例如：1分钟速热, 手机App控制"
        />
      </label>
      <label className="mb-5 block">
        <span className="mb-1.5 block text-[12px] text-aux">目标人群</span>
        <input
          className={fieldClass}
          value={form.audience}
          onChange={(e) => setForm((f) => ({ ...f, audience: e.target.value }))}
          placeholder="例如：追求生活品质的独居白领"
        />
      </label>
      <ModalActions
        onClose={onClose}
        disabled={!canSubmit}
        onSubmit={() =>
          onSubmit({
            name: form.name.trim(),
            features: form.features.trim(),
            audience: form.audience.trim(),
          })
        }
        submitLabel="生成文案"
      />
    </ModalShell>
  )
}

export function SocialPlanModal({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean
  onClose: () => void
  onSubmit: (topic: string) => void
}) {
  const [topic, setTopic] = useState('独居女生的低成本精致生活')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (open) {
      inputRef.current?.focus()
      inputRef.current?.select()
    }
  }, [open])

  if (!open) return null

  return (
    <ModalShell title="demo06 · 社交策划" onClose={onClose}>
      <p className="mb-4 text-[13px] text-aux">
        输入任意主题，将按 ToT 四阶段发散 → 评估 → 日历 → 优化。
      </p>
      <label className="mb-5 block">
        <span className="mb-1.5 block text-[12px] text-aux">策划主题</span>
        <input
          ref={inputRef}
          className={fieldClass}
          value={topic}
          onChange={(e) => setTopic(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && topic.trim()) {
              e.preventDefault()
              onSubmit(topic.trim())
            }
          }}
          placeholder="例如：周末露营装备清单"
        />
      </label>
      <ModalActions
        onClose={onClose}
        disabled={!topic.trim()}
        onSubmit={() => onSubmit(topic.trim())}
        submitLabel="开始策划"
      />
    </ModalShell>
  )
}

function ModalShell({
  title,
  onClose,
  children,
}: {
  title: string
  onClose: () => void
  children: ReactNode
}) {
  useEffect(() => {
    const onKey = (e: KeyboardEvent) => {
      if (e.key === 'Escape') onClose()
    }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [onClose])

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/35 px-4 backdrop-blur-[2px]"
      onClick={onClose}
      role="presentation"
    >
      <div
        role="dialog"
        aria-modal="true"
        aria-label={title}
        className="w-full max-w-md rounded-[20px] border border-[var(--border-soft)] bg-[var(--bg-sidebar)] p-5 shadow-[0_24px_80px_rgba(15,23,42,0.28)] backdrop-blur-xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-1 text-[15px] font-semibold text-title">{title}</div>
        {children}
      </div>
    </div>
  )
}

function ModalActions({
  onClose,
  onSubmit,
  disabled,
  submitLabel,
}: {
  onClose: () => void
  onSubmit: () => void
  disabled: boolean
  submitLabel: string
}) {
  return (
    <div className="flex justify-end gap-2">
      <button
        type="button"
        onClick={onClose}
        className="btn-motion btn-ghost rounded-[12px] border border-[var(--border-soft)] px-3.5 py-2 text-[13px] text-body"
      >
        取消
      </button>
      <button
        type="button"
        disabled={disabled}
        onClick={onSubmit}
        className="btn-motion btn-primary rounded-[12px] bg-[#4d6bfe] px-3.5 py-2 text-[13px] text-white disabled:opacity-50"
      >
        {submitLabel}
      </button>
    </div>
  )
}
