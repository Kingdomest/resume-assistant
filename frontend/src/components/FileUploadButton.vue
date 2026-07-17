<script setup lang="ts">
import { Paperclip, X } from 'lucide-vue-next'

const props = defineProps<{
  file: File | null
  disabled?: boolean
}>()

const emit = defineEmits<{
  'file-selected': [file: File]
  'file-cleared': []
}>()

function onFileChange(event: Event) {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]
  if (file) {
    emit('file-selected', file)
  }
  input.value = ''
}
</script>

<template>
  <div class="file-upload">
    <label class="icon-button" title="上传简历">
      <Paperclip :size="19" />
      <input
        type="file"
        accept=".pdf,.docx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        :disabled="props.disabled"
        @change="onFileChange"
      />
    </label>
    <button
      v-if="props.file"
      class="file-chip"
      type="button"
      title="移除文件"
      @click="emit('file-cleared')"
    >
      <span>{{ props.file.name }}</span>
      <X :size="14" />
    </button>
  </div>
</template>
