export type AgentTrace = {
  round: number
  agent: string
  thought: string
  action: string
  observation: string
}

export type OptimizeResumeResponse = {
  diagnosis: string
  react_trace: AgentTrace[]
  optimized_resume: string
  interview_questions: string[]
  warnings: string[]
}

export type OptimizeResumeStreamEvent =
  | { type: 'status'; message: string }
  | { type: 'diagnosis_delta'; content: string }
  | { type: 'answer_delta'; content: string }
  | { type: 'result'; data: OptimizeResumeResponse }
  | { type: 'error'; message: string }
  | { type: 'done' }

export type OptimizeResumeInput = {
  targetCompany: string
  targetRole: string
  jdText: string
  resumeFile: File | null
  resumeText?: string
  signal?: AbortSignal
  onEvent?: (event: OptimizeResumeStreamEvent) => void
}

function buildFormData(input: OptimizeResumeInput) {
  const formData = new FormData()
  formData.append('target_company', input.targetCompany)
  formData.append('target_role', input.targetRole)
  formData.append('jd_text', input.jdText)
  if (input.resumeFile) {
    formData.append('resume_file', input.resumeFile)
  }
  if (input.resumeText?.trim()) {
    formData.append('resume_text', input.resumeText.trim())
  }
  return formData
}

async function readError(response: Response) {
  const errorBody = await response.json().catch(() => ({ detail: '请求失败' }))
  throw new Error(errorBody.detail || '简历优化请求失败')
}

function parseSseEvent(block: string): OptimizeResumeStreamEvent | null {
  const dataLines = block
    .split(/\r?\n/)
    .filter((line) => line.startsWith('data:'))
    .map((line) => line.slice(5).trimStart())

  if (!dataLines.length) {
    return null
  }

  return JSON.parse(dataLines.join('\n')) as OptimizeResumeStreamEvent
}

async function optimizeResumeStream(input: OptimizeResumeInput): Promise<OptimizeResumeResponse> {
  const response = await fetch('/api/optimize-resume/stream', {
    method: 'POST',
    body: buildFormData(input),
    ...(input.signal ? { signal: input.signal } : {}),
  })

  if (!response.ok) {
    await readError(response)
  }
  if (!response.body) {
    throw new Error('当前浏览器不支持流式响应')
  }

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  let finalResult: OptimizeResumeResponse | null = null

  while (true) {
    const { value, done } = await reader.read()
    buffer += decoder.decode(value, { stream: !done })

    const normalized = buffer.replace(/\r\n/g, '\n')
    const blocks = normalized.split('\n\n')
    buffer = blocks.pop() ?? ''

    for (const block of blocks) {
      const event = parseSseEvent(block)
      if (!event) {
        continue
      }
      input.onEvent?.(event)
      if (event.type === 'result') {
        finalResult = event.data
      }
      if (event.type === 'error') {
        throw new Error(event.message)
      }
    }

    if (done) {
      break
    }
  }

  if (buffer.trim()) {
    const event = parseSseEvent(buffer)
    if (event) {
      input.onEvent?.(event)
      if (event.type === 'result') {
        finalResult = event.data
      }
      if (event.type === 'error') {
        throw new Error(event.message)
      }
    }
  }

  if (!finalResult) {
    throw new Error('流式响应未返回最终结果')
  }

  return finalResult
}

export async function optimizeResume(input: OptimizeResumeInput): Promise<OptimizeResumeResponse> {
  if (input.onEvent) {
    return optimizeResumeStream(input)
  }

  const response = await fetch('/api/optimize-resume', {
    method: 'POST',
    body: buildFormData(input),
    ...(input.signal ? { signal: input.signal } : {}),
  })

  if (!response.ok) {
    await readError(response)
  }

  return response.json()
}
