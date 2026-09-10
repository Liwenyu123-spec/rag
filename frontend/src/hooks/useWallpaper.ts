import { useCallback, useEffect, useState } from 'react'

const KEY = 'ds-wallpaper'
const DIM_KEY = 'ds-wallpaper-dim'
const MAX_BYTES = 2.5 * 1024 * 1024 // localStorage 容量有限

export type WallpaperState = {
  dataUrl: string | null
  dim: number // 0~0.85 遮罩，保证文字可读
}

function load(): WallpaperState {
  try {
    return {
      dataUrl: localStorage.getItem(KEY),
      dim: Number(localStorage.getItem(DIM_KEY) ?? '0.45') || 0.45,
    }
  } catch {
    return { dataUrl: null, dim: 0.45 }
  }
}

export function useWallpaper() {
  const [wallpaper, setWallpaper] = useState<WallpaperState>(load)

  useEffect(() => {
    try {
      if (wallpaper.dataUrl) localStorage.setItem(KEY, wallpaper.dataUrl)
      else localStorage.removeItem(KEY)
      localStorage.setItem(DIM_KEY, String(wallpaper.dim))
    } catch {
      /* quota */
    }
  }, [wallpaper])

  const setFromFile = useCallback(async (file: File) => {
    if (!file.type.startsWith('image/')) {
      throw new Error('请选择图片文件')
    }
    if (file.size > MAX_BYTES) {
      throw new Error('图片请小于约 2.5MB（本地存储容量有限）')
    }
    const dataUrl = await readAsDataURL(file)
    setWallpaper((s) => ({ ...s, dataUrl }))
  }, [])

  const clear = useCallback(() => {
    setWallpaper((s) => ({ ...s, dataUrl: null }))
  }, [])

  const setDim = useCallback((dim: number) => {
    setWallpaper((s) => ({ ...s, dim: Math.min(0.85, Math.max(0.1, dim)) }))
  }, [])

  return { wallpaper, setFromFile, clear, setDim }
}

function readAsDataURL(file: File) {
  return new Promise<string>((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = () => resolve(String(reader.result))
    reader.onerror = () => reject(new Error('读取图片失败'))
    reader.readAsDataURL(file)
  })
}
