<script setup lang="ts">
import type { AgentTrace } from '../api/resumeOptimizer'

defineProps<{
  traces: AgentTrace[]
}>()
</script>

<template>
  <ol class="thought-timeline">
    <li v-for="trace in traces" :key="`${trace.round}-${trace.agent}-${trace.action}`">
      <strong>{{ trace.agent }}</strong>
      <span>{{ trace.thought }}</span>
      <code>{{ trace.action }}</code>
      <p>{{ trace.observation }}</p>
    </li>
  </ol>
</template>
