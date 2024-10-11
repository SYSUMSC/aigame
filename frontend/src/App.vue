<script setup lang="ts">
import { RouterView } from "vue-router";
import { useUserStore } from "./stores/user";
import NavBar from './components/NavBar.vue';

</script>

<template>
  <NavBar />
  <!-- 灰色背景 -->
  <RouterView class="container mx-auto px-4 py-8" />
</template>

<style scoped>
/* 可以在此处添加全局样式 */
</style>
