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
      <div className="mb-5 flex h-14 w-14 items-center justify-center rounded-[16px] bg-ds-blue text-2xl text-white shadow-lg shadow-ds-blue/25">
        ✦
      </div>
      <h2 className="mb-8 text-2xl font-semibold tracking-tight text-ds-text">
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
            className="suggestion-card rounded-[16px] border border-ds-border bg-ds-bg px-4 py-3.5 text-left text-[14px] text-ds-text shadow-sm hover:border-ds-blue/40"
          >
            <span className="mr-2">{item.icon}</span>
            {item.text}
          </button>
        ))}
      </div>
      <p className="mt-6 text-xs text-ds-muted">
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
      className="rounded-[12px] border border-ds-border bg-ds-subtle px-3 py-1.5 text-xs text-ds-text outline-none transition-[border-color] duration-150 hover:border-ds-blue/40"
    >
      {(Object.keys(MODE_LABELS) as PromptMode[]).map((k) => (
        <option key={k} value={k}>
          {MODE_LABELS[k]}
        </option>
      ))}
    </select>
  )
}
