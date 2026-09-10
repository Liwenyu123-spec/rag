import { useEffect } from 'react'
import { getOllamaBase, isBrowserOllamaMode } from '../lib/api'

/** 网页打开时给本地桥接续命；关闭后约 60 秒无心跳则桥接自动退出 */
export function useBridgeHeartbeat(enabled: boolean) {
  useEffect(() => {
    if (!enabled || !isBrowserOllamaMode()) return

    const base = getOllamaBase()
    const ping = () => {
      void fetch(`${base}/__ping`, { method: 'POST', mode: 'cors' }).catch(() => undefined)
    }

    ping()
    const id = window.setInterval(ping, 15000)

    const onHide = () => {
      try {
        navigator.sendBeacon(`${base}/__shutdown`)
      } catch {
        void fetch(`${base}/__shutdown`, {
          method: 'POST',
          mode: 'cors',
          keepalive: true,
        }).catch(() => undefined)
      }
    }

    window.addEventListener('pagehide', onHide)
    window.addEventListener('beforeunload', onHide)

    return () => {
      window.clearInterval(id)
      window.removeEventListener('pagehide', onHide)
      window.removeEventListener('beforeunload', onHide)
    }
  }, [enabled])
}
