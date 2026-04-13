<template>
  <div class="external-link">
    <p>正在跳转到外部链接...</p>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'
import { useRoute } from 'vue-router'

const route = useRoute()

onMounted(() => {
  // 在新窗口打开外部链接
  window.open(route.path, '_blank')
  // 或者直接跳转到外部链接
  // window.location.href = route.path
})
</script>