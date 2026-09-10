import { useEffect, useRef, useState, type ReactNode } from 'react'
import { MODE_LABELS, type ProductPayload, type PromptMode } from '../types'
import { PROMPT_TEMPLATES } from '../lib/templates'

export const fieldClass =
  'w-full rounded-[12px] border border-[var(--border-soft)] bg-white/70 px-3 py-2.5 text-[14px] text-[var(--text-main)] outline-none backdrop-blur-md placeholder:text-[var(--text-aux)] focus:border-[#4d6bfe]/60 dark:bg-white/5'

export function ProductCopyModal({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean
  onClose: () => void
  onSubmit: (product: ProductPayload) => void
}) {
  const [form, setForm] = useState<ProductPayload>({
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

export function SloganModal({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean
  onClose: () => void
  onSubmit: (question: string) => void
}) {
  const [question, setQuestion] = useState('为旅行背包品牌生成一句口号')
  const inputRef = useRef<HTMLInputElement>(null)

  useEffect(() => {
    if (open) {
      inputRef.current?.focus()
      inputRef.current?.select()
    }
  }, [open])

  if (!open) return null

  return (
    <ModalShell title="demo02 · 自我一致性" onClose={onClose}>
      <p className="mb-4 text-[13px] text-aux">
        多角度生成候选口号，再评选最优。可改成任意品牌 / 产品。
      </p>
      <label className="mb-5 block">
        <span className="mb-1.5 block text-[12px] text-aux">任务描述</span>
        <input
          ref={inputRef}
          className={fieldClass}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' && question.trim()) {
              e.preventDefault()
              onSubmit(question.trim())
            }
          }}
          placeholder="例如：为咖啡店生成一句口号"
        />
      </label>
      <ModalActions
        onClose={onClose}
        disabled={!question.trim()}
        onSubmit={() => onSubmit(question.trim())}
        submitLabel="开始评选"
      />
    </ModalShell>
  )
}

export function CompareModal({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean
  onClose: () => void
  onSubmit: (question: string, modes: PromptMode[]) => void
}) {
  const [question, setQuestion] = useState('为新中式茶饮写一条小红书种草文案')
  const [modes, setModes] = useState<PromptMode[]>(['zero_shot', 'cot', 'tot'])
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  if (!open) return null

  const toggle = (m: PromptMode) => {
    setModes((prev) =>
      prev.includes(m) ? prev.filter((x) => x !== m) : [...prev, m],
    )
  }

  return (
    <ModalShell title="多模式对比" onClose={onClose} wide>
      <p className="mb-4 text-[13px] text-aux">
        同一问题用多种提示词策略并排生成，方便看差异（不写入多轮记忆）。
      </p>
      <label className="mb-3 block">
        <span className="mb-1.5 block text-[12px] text-aux">对比问题</span>
        <textarea
          ref={inputRef}
          rows={3}
          className={`${fieldClass} resize-none leading-[1.6]`}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
      </label>
      <div className="mb-5 flex flex-wrap gap-2">
        {(Object.keys(MODE_LABELS) as PromptMode[]).map((m) => (
          <button
            key={m}
            type="button"
            onClick={() => toggle(m)}
            className={`rounded-full border px-3 py-1 text-[12px] ${
              modes.includes(m)
                ? 'border-[#4d6bfe] bg-[#4d6bfe]/15 text-[#4d6bfe]'
                : 'border-[var(--border-soft)] text-aux'
            }`}
          >
            {MODE_LABELS[m]}
          </button>
        ))}
      </div>
      <ModalActions
        onClose={onClose}
        disabled={!question.trim() || modes.length < 2}
        onSubmit={() => onSubmit(question.trim(), modes)}
        submitLabel="开始对比"
      />
    </ModalShell>
  )
}

export function ToolChatModal({
  open,
  onClose,
  onSubmit,
}: {
  open: boolean
  onClose: () => void
  onSubmit: (question: string) => void
}) {
  const [question, setQuestion] = useState('北京今天天气怎么样？另外算一下 128*36+9')
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (open) inputRef.current?.focus()
  }, [open])

  if (!open) return null

  return (
    <ModalShell title="工具调用演示" onClose={onClose} wide>
      <p className="mb-4 text-[13px] text-aux">
        纯文本 ReAct：模型决定调用 calculator / weather / now / note_search，适合文本模型。
      </p>
      <label className="mb-5 block">
        <span className="mb-1.5 block text-[12px] text-aux">问题</span>
        <textarea
          ref={inputRef}
          rows={3}
          className={`${fieldClass} resize-none leading-[1.6]`}
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
        />
      </label>
      <ModalActions
        onClose={onClose}
        disabled={!question.trim()}
        onSubmit={() => onSubmit(question.trim())}
        submitLabel="开始调用"
      />
    </ModalShell>
  )
}

export function SystemPromptModal({
  open,
  value,
  onClose,
  onSubmit,
}: {
  open: boolean
  value: string
  onClose: () => void
  onSubmit: (content: string) => void
}) {
  const [content, setContent] = useState(value)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (open) {
      setContent(value)
      inputRef.current?.focus()
    }
  }, [open, value])

  if (!open) return null

  return (
    <ModalShell title="系统提示词" onClose={onClose} wide>
      <p className="mb-4 text-[13px] text-aux">
        可编辑角色与约束；保存后会重建服务端记忆。留空表示不注入 system。
      </p>
      <textarea
        ref={inputRef}
        rows={8}
        className={`${fieldClass} mb-5 resize-y leading-[1.6]`}
        value={content}
        onChange={(e) => setContent(e.target.value)}
        placeholder="例如：你是严谨的技术助教，回答简洁，不确定时明确说明。"
      />
      <ModalActions
        onClose={onClose}
        disabled={false}
        onSubmit={() => onSubmit(content.trim())}
        submitLabel="保存并生效"
      />
    </ModalShell>
  )
}

export function TemplatePickerModal({
  open,
  onClose,
  onPick,
}: {
  open: boolean
  onClose: () => void
  onPick: (prompt: string) => void
}) {
  if (!open) return null

  return (
    <ModalShell title="提示词模板库" onClose={onClose} wide>
      <p className="mb-4 text-[13px] text-aux">点选模板填入输入框，可再编辑后发送。</p>
      <div className="mb-2 max-h-[50vh] space-y-2 overflow-y-auto">
        {PROMPT_TEMPLATES.map((t) => (
          <button
            key={t.id}
            type="button"
            onClick={() => onPick(t.prompt)}
            className="suggestion-card w-full rounded-[14px] px-3.5 py-3 text-left"
          >
            <div className="text-[13px] font-semibold text-title">{t.title}</div>
            <div className="mt-0.5 text-[12px] text-aux">{t.description}</div>
          </button>
        ))}
      </div>
      <div className="mt-3 flex justify-end">
        <button
          type="button"
          onClick={onClose}
          className="btn-motion btn-ghost rounded-[12px] border border-[var(--border-soft)] px-3.5 py-2 text-[13px] text-body"
        >
          关闭
        </button>
      </div>
    </ModalShell>
  )
}

export function ModalShell({
  title,
  onClose,
  children,
  wide,
}: {
  title: string
  onClose: () => void
  children: ReactNode
  wide?: boolean
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
        className={`w-full rounded-[20px] border border-[var(--border-soft)] bg-[var(--bg-sidebar)] p-5 shadow-[0_24px_80px_rgba(15,23,42,0.28)] backdrop-blur-xl ${
          wide ? 'max-w-lg' : 'max-w-md'
        }`}
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
