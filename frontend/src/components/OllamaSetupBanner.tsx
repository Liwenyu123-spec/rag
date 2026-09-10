import { isBrowserOllamaMode } from '../lib/api'

const PROXY_CMD =
  'curl -sL https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py | python'
const PROXY_CMD_WIN =
  'curl -sL https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py | python'
const SITE = 'https://liwenyu123-spec.github.io/rag/'

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
        正在检测本机 Ollama 桥接…
      </div>
    )
  }

  return (
    <div className="z-30 border-b border-amber-500/30 bg-amber-500/15 px-4 py-4 text-[13px] text-body">
      <div className="mx-auto max-w-[768px]">
        <div className="mb-1 text-[14px] font-semibold text-title">
          需要先开一个本地小桥接（不用下载整个项目）
        </div>
        <p className="mb-3 text-aux">
          你已有 Ollama 和模型也够用。但 Chrome 会拦截网页直接访问本机 11434，所以要在本机跑一行命令开桥接（端口
          18789）。{hint ? ` 详情：${hint}` : ''}
        </p>
        <div className="mb-3 rounded-[12px] border border-[var(--border-soft)] bg-white/40 p-3 dark:bg-black/20">
          <div className="mb-2 font-medium text-title">步骤（约 10 秒）</div>
          <ol className="list-decimal space-y-2 pl-5 text-aux">
            <li>确认本机 Ollama 已打开，且已有模型（你已经有就可以）</li>
            <li>
              打开 PowerShell / 命令提示符，粘贴运行（保持窗口不要关）：
              <pre className="mt-1 overflow-x-auto rounded-[10px] bg-black/80 p-2 text-[12px] text-white">
                {PROXY_CMD_WIN}
              </pre>
            </li>
            <li>
              再打开或刷新本页：{' '}
              <a className="text-[#4d6bfe] underline" href={SITE}>
                {SITE}
              </a>
            </li>
          </ol>
          <p className="mt-2 text-[12px] text-aux">
            若没有 curl，可先把{' '}
            <a
              className="text-[#4d6bfe] underline"
              href="https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py"
              target="_blank"
              rel="noreferrer"
            >
              pna_proxy.py
            </a>{' '}
            另存为文件后执行 <code className="text-[12px]">python pna_proxy.py</code>
            （只下这一个小文件）。
          </p>
          <p className="mt-1 hidden text-[12px] text-aux sm:block">
            macOS / Linux 同样：<code className="text-[12px]">{PROXY_CMD}</code>
          </p>
        </div>
        <button
          type="button"
          onClick={onRetry}
          className="btn-motion rounded-[12px] bg-[#4d6bfe] px-3.5 py-2 text-[13px] text-white"
        >
          我已启动桥接，重新检测
        </button>
      </div>
    </div>
  )
}
