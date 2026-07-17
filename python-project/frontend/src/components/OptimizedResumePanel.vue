<script setup lang="ts">
import { computed } from 'vue'
import { parseContentBlocks } from '../utils/formatText'

const props = defineProps<{
  content: string
}>()

const blocks = computed(() => parseContentBlocks(props.content))
</script>

<template>
  <section class="result-panel">
    <header class="result-panel-header">
      <span>Optimized Resume</span>
      <h2>定制版简历</h2>
    </header>
    <div class="resume-document formatted-content">
      <template v-for="(block, index) in blocks" :key="`${block.type}-${index}`">
        <h3 v-if="block.type === 'heading'">{{ block.text }}</h3>
        <p v-else-if="block.type === 'paragraph'">{{ block.text }}</p>
        <ul v-else>
          <li v-for="item in block.items" :key="item">{{ item }}</li>
        </ul>
      </template>
    </div>
  </section>
</template>
