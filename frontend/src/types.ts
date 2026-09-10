export type Role = 'user' | 'assistant'

export type MessageKind =
  | 'chat'
  | 'self_consistency'
  | 'product_copy'
  | 'social_plan'
  | 'compare'
  | 'tool_chat'

export type ProductPayload = {
  name: string
  features: string
  audience: string
}

export interface MessageMeta {
  product?: ProductPayload
  topic?: string
  question?: string
  modes?: PromptMode[]
}

export interface ChatMessage {
  id: string
  role: Role
  content: string
  thinking?: string
  typing?: boolean
  error?: boolean
  liked?: boolean
  kind?: MessageKind
  meta?: MessageMeta
  /** 助手消息对应的用户问题，用于重试/重新生成 */
  sourceQuestion?: string
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
