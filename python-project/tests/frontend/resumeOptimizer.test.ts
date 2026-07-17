import { describe, expect, it, vi } from 'vitest'
import { optimizeResume, type OptimizeResumeStreamEvent } from '../../frontend/src/api/resumeOptimizer'

describe('optimizeResume', () => {
  it('posts multipart form data to the backend', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        diagnosis: '技能描述偏泛',
        react_trace: [],
        optimized_resume: '## 定制简历',
        interview_questions: ['Redis 缓存一致性怎么保证？'],
        warnings: [],
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    const result = await optimizeResume({
      targetCompany: '字节跳动',
      targetRole: '后端开发',
      jdText: '要求 Java 和 Redis',
      resumeFile: new File(['resume'], 'resume.pdf', { type: 'application/pdf' }),
    })

    expect(fetchMock).toHaveBeenCalledWith('/api/optimize-resume', {
      method: 'POST',
      body: expect.any(FormData),
    })
    expect(result.diagnosis).toBe('技能描述偏泛')
  })

  it('posts pasted resume text without a resume file', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        diagnosis: '技能描述偏泛',
        react_trace: [],
        optimized_resume: '## 定制简历',
        interview_questions: ['Redis 缓存一致性怎么保证？'],
        warnings: [],
      }),
    })
    vi.stubGlobal('fetch', fetchMock)

    await optimizeResume({
      targetCompany: '字节跳动',
      targetRole: '后端开发',
      jdText: '要求 Java 和 Redis',
      resumeFile: null,
      resumeText: '张三，熟悉 Java、Redis 和 MySQL。',
    })

    const body = fetchMock.mock.calls[0][1].body as FormData
    expect(body.get('resume_file')).toBeNull()
    expect(body.get('resume_text')).toBe('张三，熟悉 Java、Redis 和 MySQL。')
  })

  it('passes abort signal to the backend request', async () => {
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      json: async () => ({
        diagnosis: '技能描述偏泛',
        react_trace: [],
        optimized_resume: '## 定制简历',
        interview_questions: ['Redis 缓存一致性怎么保证？'],
        warnings: [],
      }),
    })
    vi.stubGlobal('fetch', fetchMock)
    const controller = new AbortController()

    await optimizeResume({
      targetCompany: '字节跳动',
      targetRole: '后端开发',
      jdText: '要求 Java 和 Redis',
      resumeFile: null,
      resumeText: '张三，熟悉 Java、Redis 和 MySQL。',
      signal: controller.signal,
    })

    expect(fetchMock).toHaveBeenCalledWith('/api/optimize-resume', {
      method: 'POST',
      body: expect.any(FormData),
      signal: controller.signal,
    })
  })

  it('consumes streamed optimization events', async () => {
    const responsePayload = {
      diagnosis: '技能描述偏泛',
      react_trace: [],
      optimized_resume: '## 定制简历',
      interview_questions: ['Redis 缓存一致性怎么保证？'],
      warnings: [],
    }
    const stream = new ReadableStream({
      start(controller) {
        const encoder = new TextEncoder()
        controller.enqueue(
          encoder.encode(
            [
              'event: status',
              'data: {"type":"status","message":"正在诊断"}',
              '',
              'event: answer_delta',
              'data: {"type":"answer_delta","content":"## 定制简历"}',
              '',
              'event: result',
              `data: ${JSON.stringify({ type: 'result', data: responsePayload })}`,
              '',
              'event: done',
              'data: {"type":"done"}',
              '',
              '',
            ].join('\n'),
          ),
        )
        controller.close()
      },
    })
    const fetchMock = vi.fn().mockResolvedValue({
      ok: true,
      body: stream,
    })
    vi.stubGlobal('fetch', fetchMock)
    const events: OptimizeResumeStreamEvent[] = []

    const result = await optimizeResume({
      targetCompany: '字节跳动',
      targetRole: '后端开发',
      jdText: '要求 Java 和 Redis',
      resumeFile: null,
      resumeText: '张三，熟悉 Java、Redis 和 MySQL。',
      onEvent: (event) => events.push(event),
    })

    expect(fetchMock).toHaveBeenCalledWith('/api/optimize-resume/stream', {
      method: 'POST',
      body: expect.any(FormData),
    })
    expect(events.map((event) => event.type)).toEqual([
      'status',
      'answer_delta',
      'result',
      'done',
    ])
    expect(result.optimized_resume).toBe('## 定制简历')
  })
})
