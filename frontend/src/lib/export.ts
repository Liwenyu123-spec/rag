import type { ChatMessage, Session } from '../types'
import { MODE_LABELS } from '../types'

export function downloadText(filename: string, content: string) {
  const blob = new Blob([content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}

export function sessionToMarkdown(session: Session): string {
  const lines = [
    `# ${session.title || '对话导出'}`,
    '',
    `模式：${MODE_LABELS[session.mode] || session.mode}`,
    `导出时间：${new Date().toLocaleString()}`,
    '',
  ]
  for (const m of session.messages) {
    const who = m.role === 'user' ? '用户' : '助手'
    lines.push(`## ${who}`)
    lines.push('')
    lines.push(m.content || '')
    lines.push('')
  }
  return lines.join('\n')
}

/** 尝试从电商文案中拆出标题/正文/标签，便于表格导出 */
export function productCopyToTableMarkdown(content: string, productName?: string): string {
  const title =
    content.match(/标题\s*[:：]\s*(.+)/)?.[1]?.trim() ||
    content.match(/标题[：:]\s*\n?\s*(.+)/)?.[1]?.trim() ||
    ''
  const body =
    content.match(/正文\s*[:：]\s*([\s\S]*?)(?=标签\s*[:：]|$)/)?.[1]?.trim() || ''
  const tags =
    content.match(/标签\s*[:：]\s*(.+)/)?.[1]?.trim() || ''

  const rows = [
    `# 电商文案导出${productName ? ` · ${productName}` : ''}`,
    '',
    '| 字段 | 内容 |',
    '| :--- | :--- |',
    `| 标题 | ${escapeCell(title || '（未解析到）')} |`,
    `| 正文 | ${escapeCell(body || '（未解析到，见原文）')} |`,
    `| 标签 | ${escapeCell(tags || '（未解析到）')} |`,
    '',
    '## 原文',
    '',
    content,
    '',
  ]
  return rows.join('\n')
}

function escapeCell(s: string) {
  return s.replace(/\|/g, '\\|').replace(/\n/g, '<br>')
}

export function messageExportName(message: ChatMessage, fallback = 'message') {
  const stamp = new Date().toISOString().slice(0, 19).replace(/[:T]/g, '-')
  if (message.kind === 'product_copy') return `product-copy-${stamp}.md`
  if (message.kind === 'social_plan') return `social-plan-${stamp}.md`
  if (message.kind === 'compare') return `compare-${stamp}.md`
  return `${fallback}-${stamp}.md`
}
