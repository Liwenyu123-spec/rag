import { useCallback, useEffect, useRef, useState } from 'react'

const META_KEY = 'ds-wallpaper-meta'
const DB_NAME = 'ds-wallpaper-db'
const STORE = 'media'
const MEDIA_ID = 'current'

const MAX_IMAGE = 2.5 * 1024 * 1024
const MAX_VIDEO = 40 * 1024 * 1024

export type WallpaperKind = 'image' | 'video'

export type WallpaperState = {
  kind: WallpaperKind | null
  /** 图片 dataURL 或视频 blob URL */
  src: string | null
  dim: number
  ready: boolean
}

type Meta = { kind: WallpaperKind; dim: number }

function openDb(): Promise<IDBDatabase> {
  return new Promise((resolve, reject) => {
    const req = indexedDB.open(DB_NAME, 1)
    req.onupgradeneeded = () => {
      const db = req.result
      if (!db.objectStoreNames.contains(STORE)) db.createObjectStore(STORE)
    }
    req.onsuccess = () => resolve(req.result)
    req.onerror = () => reject(req.error || new Error('IndexedDB 打开失败'))
  })
}

async function idbPut(blob: Blob) {
  const db = await openDb()
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite')
    tx.objectStore(STORE).put(blob, MEDIA_ID)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error || new Error('保存失败'))
  })
  db.close()
}

async function idbGet(): Promise<Blob | null> {
  const db = await openDb()
  const blob = await new Promise<Blob | null>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readonly')
    const req = tx.objectStore(STORE).get(MEDIA_ID)
    req.onsuccess = () => resolve((req.result as Blob) || null)
    req.onerror = () => reject(req.error || new Error('读取失败'))
  })
  db.close()
  return blob
}

async function idbClear() {
  const db = await openDb()
  await new Promise<void>((resolve, reject) => {
    const tx = db.transaction(STORE, 'readwrite')
    tx.objectStore(STORE).delete(MEDIA_ID)
    tx.oncomplete = () => resolve()
    tx.onerror = () => reject(tx.error || new Error('清除失败'))
  })
  db.close()
}

function loadMeta(): Meta | null {
  try {
    const raw = localStorage.getItem(META_KEY)
    if (!raw) {
      // 兼容旧版：仅有图片 dataURL
      const legacy = localStorage.getItem('ds-wallpaper')
      const dim = Number(localStorage.getItem('ds-wallpaper-dim') ?? '0.45') || 0.45
      if (legacy) return { kind: 'image', dim }
      return null
    }
    return JSON.parse(raw) as Meta
  } catch {
    return null
  }
}

function saveMeta(meta: Meta | null) {
  try {
    if (meta) localStorage.setItem(META_KEY, JSON.stringify(meta))
    else localStorage.removeItem(META_KEY)
    // 清理旧键，避免占空间
    localStorage.removeItem('ds-wallpaper')
  } catch {
    /* ignore */
  }
}

export function useWallpaper() {
  const [wallpaper, setWallpaper] = useState<WallpaperState>({
    kind: null,
    src: null,
    dim: 0.45,
    ready: false,
  })
  const objectUrlRef = useRef<string | null>(null)

  const revokeObjectUrl = () => {
    if (objectUrlRef.current) {
      URL.revokeObjectURL(objectUrlRef.current)
      objectUrlRef.current = null
    }
  }

  useEffect(() => {
    let cancelled = false

    ;(async () => {
      const meta = loadMeta()
      if (!meta) {
        if (!cancelled) {
          setWallpaper({ kind: null, src: null, dim: 0.45, ready: true })
        }
        return
      }

      // 旧版图片仍在 localStorage
      const legacy = localStorage.getItem('ds-wallpaper')
      if (meta.kind === 'image' && legacy) {
        if (!cancelled) {
          setWallpaper({
            kind: 'image',
            src: legacy,
            dim: meta.dim,
            ready: true,
          })
        }
        // 迁移到 IndexedDB
        try {
          const res = await fetch(legacy)
          const blob = await res.blob()
          await idbPut(blob)
          saveMeta({ kind: 'image', dim: meta.dim })
        } catch {
          /* keep legacy */
        }
        return
      }

      try {
        const blob = await idbGet()
        if (!blob || cancelled) {
          if (!cancelled) {
            setWallpaper({ kind: null, src: null, dim: meta.dim, ready: true })
          }
          return
        }
        revokeObjectUrl()
        const url = URL.createObjectURL(blob)
        objectUrlRef.current = url
        if (!cancelled) {
          setWallpaper({
            kind: meta.kind,
            src: url,
            dim: meta.dim,
            ready: true,
          })
        }
      } catch {
        if (!cancelled) {
          setWallpaper({ kind: null, src: null, dim: meta.dim, ready: true })
        }
      }
    })()

    return () => {
      cancelled = true
    }
  }, [])

  useEffect(() => {
    return () => revokeObjectUrl()
  }, [])

  const setFromFile = useCallback(async (file: File) => {
    const isImage = file.type.startsWith('image/')
    const isVideo = file.type.startsWith('video/')
    if (!isImage && !isVideo) {
      throw new Error('请选择图片或视频文件')
    }
    if (isImage && file.size > MAX_IMAGE) {
      throw new Error('图片请小于约 2.5MB')
    }
    if (isVideo && file.size > MAX_VIDEO) {
      throw new Error('视频请小于约 40MB（建议短循环、压缩后的 mp4）')
    }

    await idbPut(file)
    const kind: WallpaperKind = isVideo ? 'video' : 'image'
    const dim = wallpaper.dim || 0.45
    saveMeta({ kind, dim })

    revokeObjectUrl()
    const url = URL.createObjectURL(file)
    objectUrlRef.current = url
    setWallpaper({ kind, src: url, dim, ready: true })
  }, [wallpaper.dim])

  const clear = useCallback(async () => {
    revokeObjectUrl()
    saveMeta(null)
    try {
      await idbClear()
    } catch {
      /* ignore */
    }
    setWallpaper((s) => ({ ...s, kind: null, src: null }))
  }, [])

  const setDim = useCallback((dim: number) => {
    const next = Math.min(0.85, Math.max(0.1, dim))
    setWallpaper((s) => {
      if (s.kind) saveMeta({ kind: s.kind, dim: next })
      else {
        try {
          localStorage.setItem('ds-wallpaper-dim', String(next))
        } catch {
          /* ignore */
        }
      }
      return { ...s, dim: next }
    })
  }, [])

  return { wallpaper, setFromFile, clear, setDim }
}
