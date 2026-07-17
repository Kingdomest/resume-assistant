<script setup lang="ts">
import { computed } from 'vue'
import type { ChatMessageModel } from '../types/chat'
import { parseContentBlocks } from '../utils/formatText'

const props = defineProps<{
  message: ChatMessageModel
}>()

const blocks = computed(() => parseContentBlocks(props.message.content))
const roleLabel = computed(() => (props.message.role === 'user' ? '你' : 'AI 助手'))
</script>

<template>
  <article class="chat-message" :class="[`is-${message.role}`, `kind-${message.kind}`]">
    <header class="message-meta">
      <span>{{ roleLabel }}</span>
    </header>
    <div class="message-content formatted-content">
      <template v-for="(block, index) in blocks" :key="`${block.type}-${index}`">
        <h3 v-if="block.type === 'heading'">{{ block.text }}</h3>
        <p v-else-if="block.type === 'paragraph'">{{ block.text }}</p>
        <ul v-else>
          <li v-for="item in block.items" :key="item">{{ item }}</li>
        </ul>
      </template>
    </div>
  </article>
</template>
