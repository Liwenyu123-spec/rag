import { isBrowserOllamaMode } from '../lib/api'

const RELEASE_ZIP =
  'https://github.com/Liwenyu123-spec/rag/releases/download/ollama-share/rag-ollama-share.zip'
const REPO = 'https://github.com/Liwenyu123-spec/rag'

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
        正在检测本机 Ollama…
      </div>
    )
  }

  return (
    <div className="z-30 border-b border-amber-500/30 bg-amber-500/15 px-4 py-4 text-[13px] text-body">
      <div className="mx-auto max-w-[768px]">
        <div className="mb-1 text-[14px] font-semibold text-title">
          连不上本机 Ollama（所以会像卡住一样）
        </div>
        <p className="mb-3 text-aux">
          从 GitHub 网页访问 <code className="text-[12px]">127.0.0.1</code>{' '}
          时，Chrome 常会拦截（Private Network Access）。这不是模型坏了。
          {hint ? ` 详情：${hint}` : ''}
        </p>
        <div className="mb-3 rounded-[12px] border border-[var(--border-soft)] bg-white/40 p-3 dark:bg-black/20">
          <div className="mb-1 font-medium text-title">推荐同学这样用（最稳）</div>
          <ol className="list-decimal space-y-1 pl-5 text-aux">
            <li>
              安装并打开{' '}
              <a className="text-[#4d6bfe] underline" href="https://ollama.com/download" target="_blank" rel="noreferrer">
                Ollama
              </a>
              ，执行 <code className="text-[12px]">ollama pull deepseek-r1:1.5b</code>（或任意模型）
            </li>
            <li>
              下载压缩包：{' '}
              <a className="text-[#4d6bfe] underline" href={RELEASE_ZIP}>
                rag-ollama-share.zip
              </a>
            </li>
            <li>解压后双击 <code className="text-[12px]">start_ollama.bat</code></li>
            <li>
              浏览器打开{' '}
              <a className="text-[#4d6bfe] underline" href="http://127.0.0.1:8002">
                http://127.0.0.1:8002
              </a>{' '}
              （本地网页，不会被 Chrome 拦截）
            </li>
          </ol>
        </div>
        <div className="mb-3 text-aux">
          若仍想用本网页：先运行仓库里的{' '}
          <code className="text-[12px]">enable_ollama_cors.bat</code> 并完全重启 Ollama，再点重试；
          仍失败请改用上面的本地启动。仓库：{' '}
          <a className="text-[#4d6bfe] underline" href={REPO} target="_blank" rel="noreferrer">
            Liwenyu123-spec/rag
          </a>
        </div>
        <button
          type="button"
          onClick={onRetry}
          className="btn-motion rounded-[12px] bg-[#4d6bfe] px-3.5 py-2 text-[13px] text-white"
        >
          重新检测连接
        </button>
      </div>
    </div>
  )
}
