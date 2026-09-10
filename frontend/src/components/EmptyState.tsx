import { MODE_LABELS, type PromptMode } from '../types'

const SUGGESTIONS = [
  { icon: '💡', text: '用简单的语言解释一下什么是大语言模型' },
  { icon: '📚', text: '帮我制定一份今天的学习计划' },
  { icon: '⌨️', text: '帮我优化一段 Python 代码' },
]

export function EmptyState({
  onPick,
  onSelfConsistency,
  onProductCopy,
  onSocialPlan,
  onCompare,
  onToolChat,
  onTemplates,
}: {
  onPick: (text: string) => void
  onSelfConsistency: () => void
  onProductCopy?: () => void
  onSocialPlan?: () => void
  onCompare?: () => void
  onToolChat?: () => void
  onTemplates?: () => void
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
            onClick={() => onPick(item.text)}
            className="suggestion-card rounded-[16px] px-4 py-3.5 text-left text-[14px] text-body"
          >
            <span className="mr-2">{item.icon}</span>
            {item.text}
          </button>
        ))}
        <button
          type="button"
          onClick={onSelfConsistency}
          className="suggestion-card rounded-[16px] px-4 py-3.5 text-left text-[14px] text-body"
        >
          <span className="mr-2">✨</span>
          自我一致性 · 自定义口号任务
        </button>
      </div>

      <div className="mt-5 grid w-full max-w-xl grid-cols-1 gap-3 sm:grid-cols-2">
        <DemoCard
          title="demo05 · 电商文案"
          desc="自定义产品信息，Few-Shot + CoT"
          onClick={onProductCopy}
        />
        <DemoCard
          title="demo06 · 社交策划"
          desc="自定义主题，ToT 四阶段"
          onClick={onSocialPlan}
        />
        <DemoCard
          title="多模式对比"
          desc="零样本 / 思维链 / 思维树并排"
          onClick={onCompare}
        />
        <DemoCard
          title="工具调用"
          desc="纯文本 ReAct：计算 / 天气 / 笔记"
          onClick={onToolChat}
        />
        <DemoCard
          title="提示词模板"
          desc="面试 · 周报 · 代码评审 · 润色"
          onClick={onTemplates}
        />
      </div>

      <p className="mt-6 text-xs text-aux">
        支持模式：{Object.values(MODE_LABELS).join(' · ')}
      </p>
    </div>
  )
}

function DemoCard({
  title,
  desc,
  onClick,
}: {
  title: string
  desc: string
  onClick?: () => void
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="suggestion-card rounded-[16px] px-4 py-3.5 text-left text-[14px] text-body"
    >
      <div className="mb-1 text-[13px] font-semibold text-[#4d6bfe]">{title}</div>
      <div className="text-aux text-[13px]">{desc}</div>
    </button>
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

/** 选择本机 Ollama 已安装的模型 */
export function OllamaModelSelect({
  value,
  models,
  onChange,
}: {
  value: string
  models: string[]
  onChange: (m: string) => void
}) {
  if (!models.length) {
    return (
      <span className="max-w-[140px] truncate text-[11px] text-aux" title="本机暂无模型">
        无本地模型
      </span>
    )
  }
  return (
    <select
      value={models.includes(value) ? value : models[0]}
      onChange={(e) => onChange(e.target.value)}
      title="使用本机 Ollama 模型"
      className="max-w-[180px] rounded-[12px] border border-[var(--border-soft)] bg-white/60 px-3 py-1.5 text-xs font-normal text-[var(--text-main)] outline-none backdrop-blur-md transition-[border-color] duration-150 hover:border-[#4d6bfe]/50 dark:bg-white/5"
    >
      {models.map((m) => (
        <option key={m} value={m} className="bg-white text-[#1f2329] dark:bg-[#0f172a] dark:text-[#e8eefc]">
          {m}
        </option>
      ))}
    </select>
  )
}

