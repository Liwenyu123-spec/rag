import { MODE_LABELS, type PromptMode } from '../types'

const SUGGESTIONS = [
  { icon: '💡', text: '用简单的语言解释一下什么是大语言模型' },
  { icon: '📚', text: '帮我制定一份今天的学习计划' },
  { icon: '⌨️', text: '帮我优化一段 Python 代码' },
  { icon: '✨', text: '为旅行背包品牌生成一句口号' },
]

export function EmptyState({
  onPick,
  onSelfConsistency,
}: {
  onPick: (text: string) => void
  onSelfConsistency: () => void
}) {
  return (
    <div className="flex h-full flex-col items-center justify-center px-4 pb-10">
      <div className="logo-float mb-5 flex h-14 w-14 items-center justify-center rounded-full border border-white/10 bg-gradient-to-br from-[#6b8aff] via-[#4d6bfe] to-[#3b57e8] text-2xl text-white shadow-[0_20px_50px_rgba(77,107,254,0.35)]">
        ✦
      </div>
      <h2 className="mb-8 text-2xl text-title tracking-tight">
        有什么可以帮你的吗
      </h2>
      <div className="grid w-full max-w-xl grid-cols-1 gap-3 sm:grid-cols-2">
        {SUGGESTIONS.map((item) => (
          <button
            key={item.text}
            type="button"
            onClick={() =>
              item.text.includes('口号') ? onSelfConsistency() : onPick(item.text)
            }
            className="suggestion-card rounded-[16px] px-4 py-3.5 text-left text-[14px] text-body"
          >
            <span className="mr-2">{item.icon}</span>
            {item.text}
          </button>
        ))}
      </div>
      <p className="mt-6 text-xs text-aux">
        支持模式：{Object.values(MODE_LABELS).join(' · ')}
      </p>
    </div>
  )
}

export function ModeSelect({
  value,
  onChange,
}: {
  value: PromptMode
  onChange: (m: PromptMode) => void
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value as PromptMode)}
      className="rounded-[12px] border border-[var(--border-soft)] bg-white/60 px-3 py-1.5 text-xs font-normal text-[var(--text-main)] outline-none backdrop-blur-md transition-[border-color] duration-150 hover:border-[#4d6bfe]/50 dark:bg-white/5"
    >
      {(Object.keys(MODE_LABELS) as PromptMode[]).map((k) => (
        <option key={k} value={k} className="bg-white text-[#1f2329] dark:bg-[#0f172a] dark:text-[#e8eefc]">
          {MODE_LABELS[k]}
        </option>
      ))}
    </select>
  )
}
