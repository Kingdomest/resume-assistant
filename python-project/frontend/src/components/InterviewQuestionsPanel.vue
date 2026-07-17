<script setup lang="ts">
defineProps<{
  questions: string[]
}>()
</script>

<template>
  <section class="result-panel">
    <header class="result-panel-header">
      <span>Interview Prep</span>
      <h2>面试预测问题</h2>
    </header>
    <ol class="question-list">
      <li v-for="question in questions" :key="question">{{ question }}</li>
    </ol>
  </section>
</template>
