import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import Composer from '../../frontend/src/components/Composer.vue'
import FileUploadButton from '../../frontend/src/components/FileUploadButton.vue'

describe('Composer', () => {
  it('renders symmetric job and resume input panels', () => {
    const wrapper = mount(Composer)

    expect(wrapper.find('[data-test="jd-panel"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="resume-panel"]').exists()).toBe(true)
    expect(wrapper.find('[data-test="jd-panel"]').text()).toContain('目标岗位 / JD')
    expect(wrapper.find('[data-test="resume-panel"]').text()).toContain('简历内容')
  })

  it('uses fixed scrollable text areas for overflow content', () => {
    const wrapper = mount(Composer)

    expect(wrapper.find('[data-test="jd-textarea"]').classes()).toContain('scroll-textarea')
    expect(wrapper.find('[data-test="resume-textarea"]').classes()).toContain('scroll-textarea')
  })

  it('emits submit with text and selected file', async () => {
    const wrapper = mount(Composer)
    const file = new File(['resume'], 'resume.pdf', { type: 'application/pdf' })

    await wrapper.find('[data-test="jd-textarea"]').setValue('我想投字节跳动后端岗，JD 要求 Java 和 Redis')
    await wrapper.findComponent(FileUploadButton).vm.$emit('file-selected', file)
    await wrapper.find('[data-test="send-button"]').trigger('click')

    const emitted = wrapper.emitted('submit')
    expect(emitted).toBeTruthy()
    expect(emitted?.[0][0]).toEqual({
      text: '我想投字节跳动后端岗，JD 要求 Java 和 Redis',
      file,
      resumeText: '',
    })
  })

  it('emits submit with pasted resume text when no file is selected', async () => {
    const wrapper = mount(Composer)

    await wrapper.find('[data-test="jd-textarea"]').setValue('我想投字节跳动后端岗，JD 要求 Java 和 Redis')
    await wrapper.find('[data-test="resume-textarea"]').setValue('张三，熟悉 Java、Redis 和 MySQL。')
    await wrapper.find('[data-test="send-button"]').trigger('click')

    const emitted = wrapper.emitted('submit')
    expect(emitted).toBeTruthy()
    expect(emitted?.[0][0]).toEqual({
      text: '我想投字节跳动后端岗，JD 要求 Java 和 Redis',
      file: null,
      resumeText: '张三，熟悉 Java、Redis 和 MySQL。',
    })
  })

  it('shows a stop button while submitting and emits stop', async () => {
    const wrapper = mount(Composer, {
      props: {
        submitting: true,
      },
    })

    const button = wrapper.find('[data-test="send-button"]')
    expect(button.text()).toContain('停止生成')
    expect(button.classes()).toContain('is-stop')

    await button.trigger('click')

    expect(wrapper.emitted('stop')).toBeTruthy()
    expect(wrapper.emitted('submit')).toBeFalsy()
  })

  it('disables send when job description or resume source is missing', async () => {
    const wrapper = mount(Composer)

    expect(wrapper.find('[data-test="send-button"]').attributes('disabled')).toBeDefined()

    await wrapper.find('[data-test="jd-textarea"]').setValue('我想投字节跳动后端岗，JD 要求 Java 和 Redis')
    expect(wrapper.find('[data-test="send-button"]').attributes('disabled')).toBeDefined()
  })
})
