import { useEffect, useState } from 'react'

export type BackendStatus = {
  ok: boolean
  backend?: string
  model?: string
  model_ready?: boolean
  hint?: string | null
  ollama?: boolean
}

export function useBackendStatus() {
  const [status, setStatus] = useState<BackendStatus | null>(null)

  useEffect(() => {
    let alive = true
    const load = async () => {
      try {
        const res = await fetch('/health')
        const data = (await res.json()) as BackendStatus
        if (alive) setStatus(data)
      } catch {
        if (alive) {
          setStatus({
            ok: false,
            hint: '后端未连接。请运行 python 910_ollama.py 或 910.py',
          })
        }
      }
    }
    void load()
    const id = window.setInterval(load, 15000)
    return () => {
      alive = false
      window.clearInterval(id)
    }
  }, [])

  return status
}
