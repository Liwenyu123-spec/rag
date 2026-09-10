import { useCallback, useEffect, useState } from 'react'
import {
  getOllamaModel,
  isBrowserOllamaMode,
  listOllamaModels,
  setOllamaModel,
  apiFetch,
} from '../lib/api'

export type BackendStatus = {
  ok: boolean
  backend?: string
  model?: string
  model_ready?: boolean
  models?: string[]
  hint?: string | null
  ollama?: boolean
}

export function useBackendStatus() {
  const [status, setStatus] = useState<BackendStatus | null>(null)
  const [models, setModels] = useState<string[]>([])
  const [model, setModel] = useState(() => getOllamaModel())

  const refresh = useCallback(async () => {
    try {
      const res = await apiFetch('/health')
      const data = (await res.json()) as BackendStatus
      setStatus(data)
      if (data.models?.length) setModels(data.models)
      if (data.model) setModel(data.model)
    } catch {
      setStatus({
        ok: false,
        hint: '连不上本机 Ollama。请先打开 Ollama 应用。',
      })
    }

    if (isBrowserOllamaMode()) {
      try {
        const names = await listOllamaModels()
        setModels(names)
        const saved = getOllamaModel()
        if (saved && names.includes(saved)) setModel(saved)
        else if (names[0]) {
          setOllamaModel(names[0])
          setModel(names[0])
        }
      } catch {
        /* health 已处理 */
      }
    }
  }, [])

  useEffect(() => {
    void refresh()
    const id = window.setInterval(() => void refresh(), 15000)
    return () => window.clearInterval(id)
  }, [refresh])

  const selectModel = useCallback(
    (name: string) => {
      setOllamaModel(name)
      setModel(name)
      setStatus((s) =>
        s
          ? {
              ...s,
              model: name,
              model_ready: (s.models || models).includes(name),
              hint: null,
            }
          : s,
      )
    },
    [models],
  )

  return { status, models, model, selectModel, refresh, isBrowserOllama: isBrowserOllamaMode() }
}
