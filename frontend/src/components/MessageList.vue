<script setup lang="ts">
import ChatMessage from './ChatMessage.vue'
import type { ChatMessageModel } from '../types/chat'

defineProps<{
  messages: ChatMessageModel[]
}>()
</script>

<template>
  <section class="message-list" aria-label="对话内容">
    <ChatMessage v-for="message in messages" :key="message.id" :message="message" />
  </section>
</template>
