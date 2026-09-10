/** 从模型回复中拆出思考过程（DeepSeek R1 的 think 标签） */
export function splitThinking(raw: string): { thinking: string; content: string } {
  const open = `<${'think'}>`
  const close = `</${'think'}>`
  const start = raw.indexOf(open)
  if (start === -1) {
    return { thinking: '', content: raw }
  }

  const innerStart = start + open.length
  const end = raw.indexOf(close, innerStart)
  if (end === -1) {
    // 流式过程中尚未闭合
    return {
      thinking: raw.slice(innerStart),
      content: raw.slice(0, start),
    }
  }

  return {
    thinking: raw.slice(innerStart, end).trim(),
    content: (raw.slice(0, start) + raw.slice(end + close.length)).trim(),
  }
}

export function uid() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}
