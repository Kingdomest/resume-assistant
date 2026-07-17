<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowUp, Square } from 'lucide-vue-next'
import FileUploadButton from './FileUploadButton.vue'

const props = defineProps<{
  disabled?: boolean
  submitting?: boolean
}>()

const emit = defineEmits<{
  submit: [payload: { text: string; file: File | null; resumeText: string }]
  stop: []
}>()

const text = ref('')
const resumeText = ref('')
const file = ref<File | null>(null)
const hasResumeSource = computed(() => Boolean(file.value || resumeText.value.trim()))
const canSubmit = computed(() => Boolean(text.value.trim() && hasResumeSource.value))

function submit() {
  if (!canSubmit.value) {
    return
  }
  emit('submit', {
    text: text.value.trim(),
    file: file.value,
    resumeText: resumeText.value.trim(),
  })
}
</script>

<template>
  <section class="composer" data-test="composer" aria-label="简历优化输入区">
    <div class="composer-grid">
      <article class="composer-panel" data-test="jd-panel">
        <div class="panel-heading">
          <span>Step 01</span>
          <h2>目标岗位 / JD</h2>
        </div>
        <textarea
          data-test="jd-textarea"
          v-model="text"
          class="scroll-textarea"
          rows="8"
          placeholder="粘贴目标岗位 JD，或描述你想投递的岗位"
          :disabled="props.disabled || props.submitting"
          @keydown.ctrl.enter.prevent="submit"
        />
      </article>

      <article class="composer-panel" data-test="resume-panel">
        <div class="panel-heading">
          <span>Step 02</span>
          <h2>简历内容</h2>
        </div>
        <FileUploadButton
          :file="file"
          :disabled="props.disabled || props.submitting"
          @file-selected="file = $event"
          @file-cleared="file = null"
        />
        <textarea
          data-test="resume-textarea"
          v-model="resumeText"
          class="resume-textarea scroll-textarea"
          rows="8"
          placeholder="未上传文件时，在这里粘贴简历内容"
          :disabled="props.disabled || props.submitting"
          @keydown.ctrl.enter.prevent="submit"
        />
      </article>
    </div>

    <footer class="composer-actions">
      <p>填写 JD，并上传或粘贴简历后即可开始优化</p>
      <button
        class="send-button"
        :class="{ 'is-stop': props.submitting }"
        data-test="send-button"
        type="button"
        :title="props.submitting ? '停止生成' : '发送'"
        :disabled="props.submitting ? false : props.disabled || !canSubmit"
        @click="props.submitting ? emit('stop') : submit()"
      >
        <Square v-if="props.submitting" :size="15" />
        <ArrowUp v-else :size="18" />
        <span>{{ props.submitting ? '停止生成' : '开始优化' }}</span>
      </button>
    </footer>
  </section>
</template>
