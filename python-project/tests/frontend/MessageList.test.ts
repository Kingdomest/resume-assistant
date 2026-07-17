import { mount } from '@vue/test-utils'
import { describe, expect, it } from 'vitest'
import MessageList from '../../frontend/src/components/MessageList.vue'

describe('MessageList', () => {
  it('renders user and assistant messages', () => {
    const wrapper = mount(MessageList, {
      props: {
        messages: [
          {
            id: '1',
            role: 'user',
            kind: 'request',
            content: '我想投字节后端岗',
            createdAt: '2026-07-07T00:00:00.000Z',
          },
          {
            id: '2',
            role: 'assistant',
            kind: 'answer',
            content: '## 定制简历',
            createdAt: '2026-07-07T00:00:01.000Z',
          },
        ],
      },
    })

    expect(wrapper.text()).toContain('我想投字节后端岗')
    expect(wrapper.text()).toContain('定制简历')
  })
})
