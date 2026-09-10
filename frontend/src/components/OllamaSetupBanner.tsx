import { isBrowserOllamaMode } from '../lib/api'

const SITE = 'https://liwenyu123-spec.github.io/rag/'
const START_CMD =
  'curl -sL https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py -o %TEMP%\\pna_proxy.py && start "" /B pythonw %TEMP%\\pna_proxy.py'

export function OllamaSetupBanner({
  ok,
  hint,
  onRetry,
}: {
  ok: boolean | undefined
  hint?: string | null
  onRetry: () => void
}) {
  if (!isBrowserOllamaMode()) return null
  if (ok === true) return null
  if (ok === undefined) {
    return (
      <div className="border-b border-[var(--border-soft)] bg-[#4d6bfe]/10 px-4 py-2 text-center text-[13px] text-body">
        正在检测本机桥接…
      </div>
    )
  }

  return (
    <div className="z-30 border-b border-amber-500/30 bg-amber-500/15 px-4 py-4 text-[13px] text-body">
      <div className="mx-auto max-w-[768px]">
        <div className="mb-1 text-[14px] font-semibold text-title">
          先启动一次本地桥接（可关黑窗口）
        </div>
        <p className="mb-3 text-aux">
          不用下载整个项目。启动后可关掉命令行；关掉网页大约 1
          分钟后桥接会自动退出。{hint ? ` 详情：${hint}` : ''}
        </p>
        <div className="mb-3 rounded-[12px] border border-[var(--border-soft)] bg-white/40 p-3 dark:bg-black/20">
          <ol className="list-decimal space-y-2 pl-5 text-aux">
            <li>确认本机 Ollama 已打开</li>
            <li>
              Win + R 输入 <code className="text-[12px]">powershell</code>，粘贴运行：
              <pre className="mt-1 overflow-x-auto rounded-[10px] bg-black/80 p-2 text-[11px] text-white whitespace-pre-wrap">
                {START_CMD}
              </pre>
            </li>
            <li>看到启动成功后，黑窗口可以关掉</li>
            <li>
              打开 / 刷新{' '}
              <a className="text-[#4d6bfe] underline" href={SITE}>
                {SITE}
              </a>
            </li>
          </ol>
        </div>
        <button
          type="button"
          onClick={onRetry}
          className="btn-motion rounded-[12px] bg-[#4d6bfe] px-3.5 py-2 text-[13px] text-white"
        >
          我已启动，重新检测
        </button>
      </div>
    </div>
  )
}
