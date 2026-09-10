/** 从模型回复中拆出思考过程（支持 &lt;think&gt; 标签） */
export function splitThinking(raw: string): { thinking: string; content: string } {
  const thinkRe = /<think>([\s\S]*?)<\/think>/i
  const match = raw.match(thinkRe)
  if (match) {
    return {
      thinking: match[1].trim(),
      content: raw.replace(thinkRe, '').trim(),
    }
  }

  // 流式过程中尚未闭合
  const open = raw.match(/<think>([\s\S]*)$/i)
  if (open && !raw.includes('</think>')) {
    return {
      thinking: open[1],
      content: '',
    }
  }

  return { thinking: '', content: raw }
}

export function uid() {
  return `${Date.now()}-${Math.random().toString(36).slice(2, 8)}`
}
