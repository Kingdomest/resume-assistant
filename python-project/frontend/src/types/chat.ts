export type ChatMessageModel = {
  id: string
  role: 'user' | 'assistant' | 'system'
  kind: 'request' | 'pending' | 'thought' | 'answer' | 'error'
  content: string
  createdAt: string
}
