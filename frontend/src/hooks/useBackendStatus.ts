import { useEffect, useState } from 'react'
import { apiFetch } from '../lib/api'

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
        const res = await apiFetch('/health')
        const data = (await res.json()) as BackendStatus
        if (alive) setStatus(data)
      } catch {
        if (alive) {
          setStatus({
            ok: false,
            hint: '连不上本机 Ollama。请先打开 Ollama 应用。',
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
