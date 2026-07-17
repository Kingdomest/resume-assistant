<script setup lang="ts">
import { nextTick, ref } from 'vue'
import { ChevronDown } from 'lucide-vue-next'
import {
  optimizeResume,
  type OptimizeResumeResponse,
  type OptimizeResumeStreamEvent,
} from '../api/resumeOptimizer'
import type { ChatMessageModel } from '../types/chat'
import Composer from './Composer.vue'
import InterviewQuestionsPanel from './InterviewQuestionsPanel.vue'
import MessageList from './MessageList.vue'
import OptimizedResumePanel from './OptimizedResumePanel.vue'

const messages = ref<ChatMessageModel[]>([])
const result = ref<OptimizeResumeResponse | null>(null)
const isSubmitting = ref(false)
const errorMessage = ref<string | null>(null)
const pageEnd = ref<HTMLElement | null>(null)
const activeAbortController = ref<AbortController | null>(null)
const activePendingMessage = ref<ChatMessageModel | null>(null)

type StreamState = {
  diagnosis: string
  answer: string
  status: string
}

function makeMessage(
  role: ChatMessageModel['role'],
  kind: ChatMessageModel['kind'],
  content: string,
): ChatMessageModel {
  return {
    id: globalThis.crypto?.randomUUID?.() ?? `${Date.now()}-${Math.random()}`,
    role,
    kind,
    content,
    createdAt: new Date().toISOString(),
  }
}

async function scrollToLatest() {
  await nextTick()
  if (typeof pageEnd.value?.scrollIntoView === 'function') {
    pageEnd.value.scrollIntoView({ block: 'end', behavior: 'smooth' })
  }
}

function appendMessage(
  role: ChatMessageModel['role'],
  kind: ChatMessageModel['kind'],
  content: string,
) {
  const message = makeMessage(role, kind, content)
  messages.value.push(message)
  void scrollToLatest()
  return message
}

function parseTarget(text: string) {
  const companyMatch =
    text.match(/投(?:递)?(.+?)的/) ??
    text.match(/投(?:递)?(.+?)(?:后端开发|前端开发|算法|测试|产品|运营|岗位|岗|，|,|\s)/)
  const roleMatch = text.match(/(后端开发|前端开发|算法|测试|产品|运营)/)
  return {
    targetCompany: companyMatch?.[1] || '目标公司',
    targetRole: roleMatch?.[1] || '目标岗位',
    jdText: text,
  }
}

function handleStreamEvent(
  event: OptimizeResumeStreamEvent,
  pendingMessage: ChatMessageModel,
  state: StreamState,
  signal: AbortSignal,
) {
  if (signal.aborted) {
    return
  }

  if (event.type === 'status') {
    state.status = event.message
    if (!state.answer) {
      pendingMessage.kind = 'pending'
      pendingMessage.content = state.diagnosis
        ? `${event.message}\n\n${state.diagnosis}`
        : event.message
    }
  }

  if (event.type === 'diagnosis_delta') {
    state.diagnosis += event.content
    if (!state.answer) {
      pendingMessage.kind = 'pending'
      pendingMessage.content = `正在诊断匹配差距...\n\n${state.diagnosis}`
    }
  }

  if (event.type === 'answer_delta') {
    state.answer += event.content
    pendingMessage.kind = 'answer'
    pendingMessage.content = state.answer
  }

  if (event.type === 'result') {
    result.value = event.data
  }

  void scrollToLatest()
}

async function submit(payload: { text: string; file: File | null; resumeText: string }) {
  activeAbortController.value?.abort()
  const controller = new AbortController()
  activeAbortController.value = controller
  isSubmitting.value = true
  errorMessage.value = null
  result.value = null
  const resumeSource = payload.file ? `已上传简历：${payload.file.name}` : '已粘贴简历内容'
  appendMessage(
    'user',
    'request',
    `${payload.text}\n\n${resumeSource}`,
  )
  const pendingMessage = appendMessage(
    'assistant',
    'pending',
    '正在解析简历并匹配 JD，稍等一下...',
  )
  activePendingMessage.value = pendingMessage
  const streamState: StreamState = {
    diagnosis: '',
    answer: '',
    status: '',
  }
  try {
    const target = parseTarget(payload.text)
    const response = await optimizeResume({
      ...target,
      resumeFile: payload.file,
      resumeText: payload.resumeText,
      signal: controller.signal,
      onEvent: (event) => handleStreamEvent(event, pendingMessage, streamState, controller.signal),
    })
    if (controller.signal.aborted) {
      return
    }
    result.value = response
    pendingMessage.kind = 'answer'
    if (!streamState.answer.trim()) {
      pendingMessage.content = '已生成优化结果，下面已整理为简历正文和面试预测问题。'
    }
  } catch (error) {
    if (controller.signal.aborted) {
      pendingMessage.kind = 'answer'
      pendingMessage.content = '已停止生成。'
      return
    }
    const message = error instanceof Error ? error.message : '请求失败'
    errorMessage.value = message
    pendingMessage.kind = 'error'
    pendingMessage.content = message
    void scrollToLatest()
  } finally {
    isSubmitting.value = false
    if (activeAbortController.value === controller) {
      activeAbortController.value = null
      activePendingMessage.value = null
    }
  }
}

function stopGeneration() {
  if (!isSubmitting.value) {
    return
  }
  activeAbortController.value?.abort()
  if (activePendingMessage.value) {
    activePendingMessage.value.kind = 'answer'
    activePendingMessage.value.content = '已停止生成。'
  }
  errorMessage.value = null
  isSubmitting.value = false
  void scrollToLatest()
}
</script>

<template>
  <main class="chat-page">
    <header class="chat-header">
      <div>
        <p class="eyebrow">Resume ReAct Agent</p>
        <h1>简历优化助手</h1>
      </div>
      <span class="status-pill">DeepSeek 已接入</span>
    </header>

    <MessageList :messages="messages" />

    <section v-if="result" class="result-stack">
      <section v-if="result.warnings.length" class="warning-panel" aria-label="真实性校验">
        <h2>真实性校验</h2>
        <ul>
          <li v-for="warning in result.warnings" :key="warning">{{ warning }}</li>
        </ul>
      </section>
      <OptimizedResumePanel :content="result.optimized_resume" />
      <InterviewQuestionsPanel :questions="result.interview_questions" />
    </section>

    <p v-if="errorMessage" class="error-text">{{ errorMessage }}</p>

    <button
      v-if="messages.length || result"
      class="scroll-more-button"
      data-test="scroll-more"
      type="button"
      title="下拉查看更多生成内容"
      @click="scrollToLatest"
    >
      <ChevronDown :size="20" />
    </button>

    <div ref="pageEnd" aria-hidden="true" />
    <Composer :submitting="isSubmitting" @submit="submit" @stop="stopGeneration" />
  </main>
</template>
