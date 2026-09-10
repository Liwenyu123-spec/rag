export type PromptTemplate = {
  id: string
  title: string
  description: string
  prompt: string
}

export const PROMPT_TEMPLATES: PromptTemplate[] = [
  {
    id: 'interview',
    title: '模拟面试',
    description: '按岗位出题并点评回答',
    prompt:
      '请扮演资深面试官。我要面试「前端工程师」岗位。先问我一道中等难度算法/工程题，等我回答后再点评并给出参考答案。一次只问一题。',
  },
  {
    id: 'weekly',
    title: '周报助手',
    description: '把零散事项整理成周报',
    prompt:
      '请帮我把下面工作事项整理成一份简洁周报，包含：本周完成、进行中、风险与阻塞、下周计划。用 Markdown 列表输出。事项如下：\n1. \n2. \n3. ',
  },
  {
    id: 'code_review',
    title: '代码评审',
    description: '找 bug、风格与可维护性',
    prompt:
      '请对下面这段代码做评审：指出潜在 bug、边界条件、可读性与性能问题，并给出修改建议（保留原逻辑）。代码：\n```python\n\n```',
  },
  {
    id: 'rewrite',
    title: '文案润色',
    description: '更清晰、更口语',
    prompt:
      '请把下面文字润色成更清晰、自然的中文，保留原意，输出「润色版」和「改动说明」两点。原文：\n',
  },
]
