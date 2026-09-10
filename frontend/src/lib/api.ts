/** 浏览器直连本机 Ollama，用于 GitHub Pages「打开网站即用」。 */

const OLLAMA_BASE = 'http://127.0.0.1:11434'
const MODEL_KEY = 'ds-ollama-model'
const SYS_KEY = 'ds-system-prompt'

const PROMPT_MODES: Record<string, string> = {
  zero_shot: `请直接完成用户任务。
要求：突出核心卖点，文案风格清晰，必要时附带话题标签。`,
  few_shot: `你是一位专业的文案策划师。请参考下面示例格式生成内容。

示例1：
输入：产品-智能手表，特点-健康监测、运动追踪、长续航
输出：你的私人健康管家来啦！24小时健康监测，精准运动追踪，超长续航不用频繁充电。#智能手表 #健康生活 #运动达人

示例2：
输入：产品-无线耳机，特点-降噪功能、高清音质、舒适佩戴
输出：沉浸式音乐体验，从此告别噪音干扰！高清音质还原每一个音符，人体工学设计久戴不累。#无线耳机 #降噪神器 #音乐爱好者

现在请按同样格式处理用户的任务。`,
  cot: `请按以下步骤思考后再给出最终答案：
1. 目标受众分析
2. 核心卖点提炼（3个）
3. 内容结构设计（开头/中间/结尾）
4. 语言风格确定
5. 互动引导设计
最后输出完整结果。`,
  tot: `请构建思维树，探索不同方向：
主干：用户任务的最优解决方案
分支1：内容创意方向（传统文化 / 现代生活 / 跨界合作）
分支2：平台策略方向（短视频 / 社交电商 / 私域）
分支3：用户互动方向（UGC / 体验活动 / KOL）
请为每个子分支给出具体方案并评估可行性，最后推荐最佳组合。`,
}

type ChatRole = 'system' | 'user' | 'assistant'
type Msg = { role: ChatRole; content: string }

let memory: Msg[] = []

export function isBrowserOllamaMode() {
  if (import.meta.env.VITE_BROWSER_OLLAMA === 'true') return true
  if (typeof window === 'undefined') return false
  return (
    window.location.hostname.endsWith('github.io') ||
    window.location.search.includes('browser_ollama=1')
  )
}

export function getOllamaModel() {
  return localStorage.getItem(MODEL_KEY) || ''
}

export function setOllamaModel(name: string) {
  const n = name.trim()
  if (!n) return
  localStorage.setItem(MODEL_KEY, n)
}

/** 列出本机 Ollama 已安装模型 */
export async function listOllamaModels(signal?: AbortSignal): Promise<string[]> {
  const res = await fetch(`${OLLAMA_BASE}/api/tags`, { signal })
  if (!res.ok) throw new Error(`Ollama HTTP ${res.status}`)
  const payload = (await res.json()) as { models?: { name: string }[] }
  return (payload.models || []).map((m) => m.name).filter(Boolean)
}

/** 当前选用模型：优先本地已保存且仍存在的；否则用本机列表第一个 */
export async function resolveOllamaModel(signal?: AbortSignal): Promise<string> {
  const names = await listOllamaModels(signal)
  const saved = getOllamaModel()
  if (saved && names.includes(saved)) return saved
  if (names.length) {
    setOllamaModel(names[0])
    return names[0]
  }
  return saved || 'deepseek-r1:1.5b'
}

function getModel() {
  return getOllamaModel() || 'deepseek-r1:1.5b'
}

function getSystem() {
  return localStorage.getItem(SYS_KEY) || ''
}

function buildUserContent(question: string, mode: string) {
  const strategy = PROMPT_MODES[mode] || PROMPT_MODES.zero_shot
  return `${strategy}\n\n用户任务：\n${question}`
}

function jsonResponse(data: unknown, status = 200) {
  return new Response(JSON.stringify(data), {
    status,
    headers: { 'Content-Type': 'application/json' },
  })
}

function textResponse(text: string, status = 200) {
  return new Response(text, { status, headers: { 'Content-Type': 'text/plain; charset=utf-8' } })
}

async function ollamaGenerate(prompt: string, signal?: AbortSignal) {
  const res = await fetch(`${OLLAMA_BASE}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: getModel(),
      prompt,
      stream: false,
    }),
    signal,
  })
  if (!res.ok) throw new Error(`Ollama HTTP ${res.status}`)
  const data = (await res.json()) as { response?: string }
  return (data.response || '').trim()
}

async function ollamaChat(messages: Msg[], signal?: AbortSignal) {
  const res = await fetch(`${OLLAMA_BASE}/api/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      model: getModel(),
      messages,
      stream: false,
      think: true,
    }),
    signal,
  })
  if (!res.ok) throw new Error(`Ollama HTTP ${res.status}`)
  const data = (await res.json()) as {
    message?: { content?: string; thinking?: string }
  }
  const thinking = (data.message?.thinking || '').trim()
  const content = (data.message?.content || '').trim()
  if (thinking && content) {
    return `<${'think'}>\n${thinking}\n</${'think'}>\n\n${content}`
  }
  return content || thinking
}

function sseFromOllamaChat(messages: Msg[], signal?: AbortSignal) {
  const stream = new ReadableStream({
    async start(controller) {
      const enc = new TextEncoder()
      const send = (obj: unknown) => {
        controller.enqueue(enc.encode(`data: ${JSON.stringify(obj)}\n\n`))
      }
      try {
        // 先给前端一个心跳，避免长时间只有 thinking 时看起来像卡死
        send({ status: 'started' })
        const res = await fetch(`${OLLAMA_BASE}/api/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            model: getModel(),
            messages,
            stream: true,
            think: true,
          }),
          signal,
        })
        if (!res.ok || !res.body) throw new Error(`Ollama HTTP ${res.status}`)
        const reader = res.body.getReader()
        const decoder = new TextDecoder()
        let buf = ''
        let answer = ''
        let thinking = ''
        while (true) {
          const { done, value } = await reader.read()
          if (done) break
          buf += decoder.decode(value, { stream: true })
          const lines = buf.split('\n')
          buf = lines.pop() ?? ''
          for (const line of lines) {
            if (!line.trim()) continue
            try {
              const json = JSON.parse(line) as {
                message?: { content?: string; thinking?: string }
                done?: boolean
              }
              const thinkDelta = json.message?.thinking || ''
              const delta = json.message?.content || ''
              if (thinkDelta) {
                thinking += thinkDelta
                send({ thinking: thinkDelta })
              }
              if (delta) {
                answer += delta
                send({ content: delta })
              }
            } catch {
              /* ignore */
            }
          }
        }
        memory.push({
          role: 'assistant',
          content: answer || thinking,
        })
        // 若只有思考没有正文，把思考作为可见回复，避免空白气泡
        if (!answer && thinking) {
          send({ content: thinking })
        }
        controller.enqueue(enc.encode('data: [DONE]\n\n'))
      } catch (err) {
        send({ content: `请求失败：${(err as Error).message}` })
        controller.enqueue(enc.encode('data: [DONE]\n\n'))
      } finally {
        controller.close()
      }
    },
  })
  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
    },
  })
}

function socialSse(topic: string) {
  const stream = new ReadableStream({
    async start(controller) {
      const enc = new TextEncoder()
      const send = (obj: unknown) => {
        controller.enqueue(enc.encode(`data: ${JSON.stringify(obj)}\n\n`))
      }
      try {
        send({ stage: 1, title: '发散方向', content: '正在构思 3 个策划分支…' })
        const ideas = await ollamaGenerate(
          `你是一位拥有百万粉丝的小红书/抖音运营总监。主题：**${topic}**。提出3个截然不同方向：干货科普 / 情感故事 / 争议挑战。简要描述。`,
        )
        send({ stage: 1, title: '发散方向', content: ideas })

        send({ stage: 2, title: '评估剪枝', content: '正在评估爆款率与执行难度…' })
        const evaluation = await ollamaGenerate(
          `基于以下三个方向：\n${ideas}\n\n请评估风险并选出最推荐的一个方向，说明理由。`,
        )
        send({ stage: 2, title: '评估剪枝', content: evaluation })

        send({ stage: 3, title: '内容日历', content: '正在生成下周 5 条内容日历…' })
        const draft = await ollamaGenerate(
          `策略：\n${evaluation}\n\n生成下周内容发布日历（5条），Markdown 表格：星期|选题标题|封面图建议|核心文案结构。`,
        )
        send({ stage: 3, title: '内容日历', content: draft })

        send({ stage: 4, title: '审核优化', content: '正在润色标题与网感…' })
        const plan = await ollamaGenerate(
          `初稿：\n${draft}\n\n作为审核编辑：指出最弱标题并修改；语气更有网感。输出最终版。`,
        )
        send({ stage: 4, title: '最终策划', content: plan, done: true })
      } catch (err) {
        send({ stage: 'error', content: `API error: ${(err as Error).message}` })
      }
      controller.enqueue(enc.encode('data: [DONE]\n\n'))
      controller.close()
    },
  })
  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream', 'Cache-Control': 'no-cache' },
  })
}

function runTool(name: string, arg: string) {
  const n = name.trim().toLowerCase()
  if (['calculator', 'calc', 'math'].includes(n)) {
    try {
      // 仅允许数字与基本运算符
      const expr = arg.trim()
      if (!/^[\d+\-*/().\s%]+$/.test(expr)) {
        return '仅支持简单四则运算'
      }
      const v = new Function(`"use strict"; return (${expr})`)()
      return String(v)
    } catch (e) {
      return `计算失败: ${(e as Error).message}`
    }
  }
  if (['weather', '天气'].includes(n)) {
    const city = arg.trim() || '北京'
    return `${city}：晴间多云，约 22℃（演示数据）`
  }
  if (['now', 'time', 'datetime', '时间'].includes(n)) {
    return new Date().toLocaleString()
  }
  if (['note_search', 'notes', '笔记'].includes(n)) {
    return '- 提示词策略：零样本 / 少样本 / 思维链 / 思维树\n- 自我一致性：多候选再评选'
  }
  return `未知工具：${name}`
}

async function toolChat(question: string) {
  const system = `你是带工具能力的助手。只能通过下列工具获取外部信息。

可用工具：
1) calculator — 参数：数学表达式
2) weather — 参数：城市名
3) now — 参数：可空
4) note_search — 参数：关键词

输出格式二选一：
TOOL: 工具名 | 参数
或
FINAL: 最终中文回答`

  const transcript: Msg[] = [
    { role: 'system', content: system },
    { role: 'user', content: question },
  ]
  const steps: Array<Record<string, string>> = []
  for (let i = 0; i < 4; i++) {
    const text = await ollamaChat(transcript)
    transcript.push({ role: 'assistant', content: text })
    const toolMatch = text.match(/TOOL\s*[:：]\s*([^|\n]+)\|\s*(.+)/is)
    const finalMatch = text.match(/FINAL\s*[:：]\s*(.+)/is)
    if (toolMatch) {
      const toolName = toolMatch[1].trim()
      const toolArg = toolMatch[2].trim()
      const result = runTool(toolName, toolArg)
      steps.push({ type: 'tool', name: toolName, arg: toolArg, result })
      transcript.push({
        role: 'user',
        content: `工具结果（${toolName}）：${result}\n请继续，需要则再 TOOL，否则 FINAL。`,
      })
      continue
    }
    const answer = finalMatch ? finalMatch[1].trim() : text
    steps.push({ type: 'final', content: answer })
    return { question, steps, answer }
  }
  return { question, steps, answer: '工具调用轮次用尽' }
}

export async function browserOllamaFetch(
  input: string,
  init?: RequestInit,
): Promise<Response> {
  const url = new URL(input, window.location.origin)
  const path = url.pathname
  const method = (init?.method || 'GET').toUpperCase()
  const signal = init?.signal || undefined

  try {
    if (path === '/health' || path.endsWith('/health')) {
      const names = await listOllamaModels(signal)
      let model = getOllamaModel()
      if (!model || !names.includes(model)) {
        model = names[0] || model || 'deepseek-r1:1.5b'
        if (names[0]) setOllamaModel(names[0])
      }
      const model_ready = names.includes(model)
      return jsonResponse({
        ok: true,
        backend: 'ollama',
        ollama: true,
        model,
        model_ready,
        models: names,
        hint: model_ready
          ? null
          : names.length
            ? `请在右上角选择本机已有模型`
            : `本机还没有模型，请执行: ollama pull deepseek-r1:1.5b 或你喜欢的其他模型`,
      })
    }

    if (path === '/modes' || path.endsWith('/modes')) {
      return jsonResponse({
        modes: [
          { id: 'zero_shot', name: '零样本' },
          { id: 'few_shot', name: '少样本' },
          { id: 'cot', name: '思维链' },
          { id: 'tot', name: '思维树' },
        ],
        backend: 'ollama',
        model: getModel(),
      })
    }

    if ((path === '/reset' || path.endsWith('/reset')) && method === 'POST') {
      memory = []
      const sys = getSystem()
      if (sys) memory.push({ role: 'system', content: sys })
      return jsonResponse({ ok: true, system_prompt: sys })
    }

    if (path === '/system_prompt' || path.endsWith('/system_prompt')) {
      if (method === 'GET') return jsonResponse({ content: getSystem() })
      const body = init?.body ? JSON.parse(String(init.body)) : { content: '' }
      const content = String(body.content || '').trim()
      localStorage.setItem(SYS_KEY, content)
      memory = []
      if (content) memory.push({ role: 'system', content })
      return jsonResponse({ ok: true, content })
    }

    if (path === '/chat' || path.endsWith('/chat')) {
      const question = url.searchParams.get('question') || ''
      const mode = url.searchParams.get('mode') || 'zero_shot'
      const userContent = buildUserContent(question, mode)
      memory.push({ role: 'user', content: userContent })
      const answer = await ollamaChat(memory, signal)
      memory.push({ role: 'assistant', content: answer })
      return textResponse(answer)
    }

    if (path === '/stream_chat' || path.endsWith('/stream_chat')) {
      const question = url.searchParams.get('question') || ''
      const mode = url.searchParams.get('mode') || 'zero_shot'
      const userContent = buildUserContent(question, mode)
      memory.push({ role: 'user', content: userContent })
      return sseFromOllamaChat([...memory], signal)
    }

    if (path === '/self_consistency' || path.endsWith('/self_consistency')) {
      const question = url.searchParams.get('question') || ''
      const num = Math.min(5, Math.max(2, Number(url.searchParams.get('num') || 2)))
      const angles = ['自由探索', '可靠品质', '冒险精神', '轻便舒适', '陪伴旅途']
      const candidates: string[] = []
      for (let i = 0; i < num; i++) {
        const text = await ollamaGenerate(
          `你是创意文案专家。任务：${question}\n要求：口号不超过15字。\n请从「${angles[i]}」角度只输出一句口号：`,
          signal,
        )
        candidates.push(text)
      }
      const final = await ollamaGenerate(
        `请从以下方案选最佳，只输出最终口号：\n${candidates.map((c, i) => `${i + 1}. ${c}`).join('\n')}`,
        signal,
      )
      return jsonResponse({ candidates, final })
    }

    if ((path === '/product_copy' || path.endsWith('/product_copy')) && method === 'POST') {
      const product = init?.body ? JSON.parse(String(init.body)) : {}
      const prompt = `你是电商金牌文案。按思维链：人群痛点→卖点转化→标题正文→标签。
产品：${JSON.stringify(product, null, 0)}
输出格式：
标题：...
正文：...
标签：...`
      const result = await ollamaGenerate(prompt, signal)
      return jsonResponse({ product, result })
    }

    if ((path === '/compare' || path.endsWith('/compare')) && method === 'POST') {
      const body = init?.body ? JSON.parse(String(init.body)) : {}
      const question = String(body.question || '')
      const modes: string[] = body.modes || ['zero_shot', 'cot', 'tot']
      const results: Record<string, string> = {}
      for (const mode of modes) {
        results[mode] = await ollamaChat(
          [{ role: 'user', content: buildUserContent(question, mode) }],
          signal,
        )
      }
      return jsonResponse({ question, modes, results })
    }

    if ((path === '/tool_chat' || path.endsWith('/tool_chat')) && method === 'POST') {
      const body = init?.body ? JSON.parse(String(init.body)) : {}
      const data = await toolChat(String(body.question || ''))
      return jsonResponse(data)
    }

    if (path === '/social_plan_stream' || path.endsWith('/social_plan_stream')) {
      const topic = url.searchParams.get('topic') || ''
      return socialSse(topic)
    }

    if ((path === '/social_plan' || path.endsWith('/social_plan')) && method === 'POST') {
      const body = init?.body ? JSON.parse(String(init.body)) : {}
      const topic = String(body.topic || '')
      // 简化：一次生成
      const plan = await ollamaGenerate(`为主题「${topic}」做小红书/抖音一周内容策划，含方向评估与5条日历。`)
      return jsonResponse({ topic, ideas: '', evaluation: '', plan })
    }

    return jsonResponse({ error: `浏览器 Ollama 模式未实现: ${path}` }, 404)
  } catch (err) {
    const msg = (err as Error).message || String(err)
    const hint =
      msg.includes('Failed to fetch') || msg.includes('NetworkError')
        ? '连不上本机 Ollama。请先打开 Ollama，并允许网页跨域（见仓库说明 enable_ollama_cors.bat）。'
        : msg
    if (path.includes('stream') || path.includes('chat')) {
      if (path.includes('stream')) {
        const enc = new TextEncoder()
        const stream = new ReadableStream({
          start(controller) {
            controller.enqueue(
              enc.encode(`data: ${JSON.stringify({ content: hint })}\n\n`),
            )
            controller.enqueue(enc.encode('data: [DONE]\n\n'))
            controller.close()
          },
        })
        return new Response(stream, { headers: { 'Content-Type': 'text/event-stream' } })
      }
      return textResponse(hint, 503)
    }
    return jsonResponse(
      {
        ok: false,
        backend: 'ollama',
        ollama: false,
        model: getModel(),
        model_ready: false,
        hint,
        error: hint,
      },
      503,
    )
  }
}

export async function apiFetch(input: string, init?: RequestInit) {
  if (isBrowserOllamaMode()) return browserOllamaFetch(input, init)
  return fetch(input, init)
}
