<script setup lang="ts">
import { RouterView } from "vue-router";
import { useUserStore } from "./stores/user";
import NavBar from "./components/NavBar.vue";
</script>

<template>
  <NavBar />
  <div class="container mt-20 md:mt-18">
    <RouterView />
  </div>
</template>

<style scoped>
/* 可以在此处添加全局样式 */
</style>
