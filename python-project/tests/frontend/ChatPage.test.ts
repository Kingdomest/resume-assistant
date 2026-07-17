import { mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import ChatPage from '../../frontend/src/components/ChatPage.vue'
import Composer from '../../frontend/src/components/Composer.vue'
import { optimizeResume } from '../../frontend/src/api/resumeOptimizer'

vi.mock('../../frontend/src/api/resumeOptimizer', () => ({
  optimizeResume: vi.fn(() => new Promise(() => {})),
}))

describe('ChatPage', () => {
  beforeEach(() => {
    vi.mocked(optimizeResume).mockClear()
    vi.mocked(optimizeResume).mockImplementation(() => new Promise(() => {}))
  })

  it('renders the chat workspace shell', () => {
    const wrapper = mount(ChatPage)

    expect(wrapper.text()).toContain('简历优化助手')
    expect(wrapper.text()).toContain('DeepSeek 已接入')
    expect(wrapper.find('textarea').exists()).toBe(true)
  })

  it('places generated content above the input workspace', () => {
    const wrapper = mount(ChatPage)
    const composer = wrapper.find('[data-test="composer"]')
    const messageList = wrapper.find('.message-list')

    expect(composer.exists()).toBe(true)
    expect(messageList.exists()).toBe(true)
    expect(
      messageList.element.compareDocumentPosition(composer.element) &
        Node.DOCUMENT_POSITION_FOLLOWING,
    ).toBeTruthy()
  })

  it('renders final generated content without expanded agent thoughts', async () => {
    vi.mocked(optimizeResume).mockResolvedValue({
      diagnosis: '技能描述偏泛',
      react_trace: [
        {
          round: 1,
          agent: 'DecisionAgent',
          thought: '分析简历与 JD 的差距',
          action: 'analyze_resume_gap',
          observation: '缺少量化指标',
        },
      ],
      optimized_resume: '## 定制简历\n面向字节后端开发岗位',
      interview_questions: ['Redis 缓存一致性怎么保证？'],
      warnings: [],
    })
    const wrapper = mount(ChatPage)

    wrapper.findComponent(Composer).vm.$emit('submit', {
      text: '我想投字节跳动后端开发岗，JD 要求 Java 和 Redis',
      file: null,
      resumeText: '张三，熟悉 Java、Redis 和 MySQL。',
    })
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('面向字节后端开发岗位')
    expect(wrapper.text()).toContain('Redis 缓存一致性怎么保证？')
    expect(wrapper.text()).not.toContain('DecisionAgent')
    expect(wrapper.text()).not.toContain('分析简历与 JD 的差距')
    expect(wrapper.find('[data-test="scroll-more"]').exists()).toBe(true)
  })

  it('renders safety warnings returned by the backend', async () => {
    vi.mocked(optimizeResume).mockResolvedValue({
      diagnosis: 'JD 要求 Rust，但原简历只体现 Java。',
      react_trace: [],
      optimized_resume: '（真实性校验）原简历未体现 Rust，请补充真实经历后再写入。',
      interview_questions: ['Rust 所有权机制是什么？'],
      warnings: ['优化结果中出现原简历未体现的技术栈：Rust。相关表述已替换。'],
    })
    const wrapper = mount(ChatPage)

    wrapper.findComponent(Composer).vm.$emit('submit', {
      text: '我想投后端开发岗，JD 要求 Rust',
      file: null,
      resumeText: '张三，熟悉 Java。',
    })
    await wrapper.vm.$nextTick()
    await wrapper.vm.$nextTick()

    expect(wrapper.text()).toContain('真实性校验')
    expect(wrapper.text()).toContain('原简历未体现的技术栈：Rust')
  })

  it('shows an immediate processing message after submit', async () => {
    const wrapper = mount(ChatPage)

    wrapper.findComponent(Composer).vm.$emit('submit', {
      text: '我想投字节跳动后端开发岗，JD 要求 Java 和 Redis',
      file: new File(['resume'], 'resume.pdf', { type: 'application/pdf' }),
      resumeText: '',
    })
    await wrapper.vm.$nextTick()

    expect(optimizeResume).toHaveBeenCalled()
    expect(wrapper.text()).toContain('正在解析简历并匹配 JD')
  })

  it('submits pasted resume text when no file is provided', async () => {
    const wrapper = mount(ChatPage)

    wrapper.findComponent(Composer).vm.$emit('submit', {
      text: '我想投字节跳动后端开发岗，JD 要求 Java 和 Redis',
      file: null,
      resumeText: '张三，熟悉 Java、Redis 和 MySQL。',
    })
    await wrapper.vm.$nextTick()

    expect(optimizeResume).toHaveBeenCalledWith(expect.objectContaining({
      targetCompany: '字节跳动',
      targetRole: '后端开发',
      jdText: '我想投字节跳动后端开发岗，JD 要求 Java 和 Redis',
      resumeFile: null,
      resumeText: '张三，熟悉 Java、Redis 和 MySQL。',
    }))
    expect(wrapper.text()).toContain('已粘贴简历内容')
  })

  it('aborts the current request when stop is clicked', async () => {
    let signal: AbortSignal | undefined
    vi.mocked(optimizeResume).mockImplementation((input) => {
      signal = input.signal
      return new Promise(() => {})
    })
    const wrapper = mount(ChatPage)

    wrapper.findComponent(Composer).vm.$emit('submit', {
      text: '我想投字节跳动后端开发岗，JD 要求 Java 和 Redis',
      file: null,
      resumeText: '张三，熟悉 Java、Redis 和 MySQL。',
    })
    await wrapper.vm.$nextTick()

    wrapper.findComponent(Composer).vm.$emit('stop')
    await wrapper.vm.$nextTick()

    expect(signal?.aborted).toBe(true)
    expect(wrapper.text()).toContain('已停止生成')
  })
})
