export type Role = 'user' | 'assistant'

export interface ChatMessage {
  id: string
  role: Role
  content: string
  thinking?: string
  typing?: boolean
  createdAt: number
}

export interface Session {
  id: string
  title: string
  updatedAt: number
  messages: ChatMessage[]
  mode: PromptMode
}

export type PromptMode = 'zero_shot' | 'few_shot' | 'cot' | 'tot'

export const MODE_LABELS: Record<PromptMode, string> = {
  zero_shot: '零样本',
  few_shot: '少样本',
  cot: '思维链',
  tot: '思维树',
}
