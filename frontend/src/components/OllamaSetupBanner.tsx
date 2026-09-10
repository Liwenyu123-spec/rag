import { isBrowserOllamaMode } from '../lib/api'

const SITE = 'https://liwenyu123-spec.github.io/rag/'

/** PowerShell 专用（同学按 Win 搜 powershell 时用这个） */
const PS_CMD = `curl.exe -sL "https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py" -o "$env:TEMP\\pna_proxy.py"; Start-Process pythonw -ArgumentList "$env:TEMP\\pna_proxy.py" -WindowStyle Hidden; Start-Sleep 1; try { (Invoke-RestMethod http://127.0.0.1:18789/__ping).ok } catch { "启动失败：请确认已安装 Python，并已打开 Ollama" }`

/** CMD 专用 */
const CMD_CMD =
  'curl.exe -sL "https://raw.githubusercontent.com/Liwenyu123-spec/rag/master/pna_proxy.py" -o "%TEMP%\\pna_proxy.py" && start "" /B pythonw "%TEMP%\\pna_proxy.py" && timeout /t 1 >nul && curl.exe -s http://127.0.0.1:18789/__ping'

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
          用 <b>PowerShell</b> 时请复制下面「PowerShell」那一段（不要用旧的 CMD
          命令，否则会没反应）。
          {hint ? ` 详情：${hint}` : ''}
        </p>

        <div className="mb-3 space-y-3 rounded-[12px] border border-[var(--border-soft)] bg-white/40 p-3 dark:bg-black/20">
          <div>
            <div className="mb-1 font-medium text-title">PowerShell（推荐）</div>
            <pre className="overflow-x-auto rounded-[10px] bg-black/80 p-2 text-[11px] leading-5 text-white whitespace-pre-wrap">
              {PS_CMD}
            </pre>
            <p className="mt-1 text-[12px] text-aux">
              成功时会显示 <code className="text-[11px]">True</code>；若提示找不到
              pythonw，把命令里的 pythonw 改成 python 再试。
            </p>
          </div>
          <div>
            <div className="mb-1 font-medium text-title">命令提示符 CMD</div>
            <pre className="overflow-x-auto rounded-[10px] bg-black/80 p-2 text-[11px] leading-5 text-white whitespace-pre-wrap">
              {CMD_CMD}
            </pre>
          </div>
          <ol className="list-decimal space-y-1 pl-5 text-aux">
            <li>确认本机 Ollama 已打开</li>
            <li>运行上面命令，看到 True / ok 后再开网页</li>
            <li>
              打开{' '}
              <a className="text-[#4d6bfe] underline" href={SITE}>
                {SITE}
              </a>
              ，黑窗口可关
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
