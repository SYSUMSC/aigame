<script setup lang="ts">
import { RouterLink, RouterView } from 'vue-router'
import { useUserStore } from './stores/user';

const userStore = useUserStore();
</script>

<template>
  <div>
    <header class="bg-gray-800 text-white">
      <nav class="container mx-auto flex items-center justify-between py-4">
        <div>
          <RouterLink to="/" class="text-xl font-bold">AI 竞赛平台</RouterLink>
        </div>
        <div class="flex items-center space-x-4">
          <RouterLink to="/" class="hover:text-gray-300">首页</RouterLink>
          <template v-if="userStore.isLoggedIn()">
            <RouterLink to="/user" class="hover:text-gray-300">用户中心</RouterLink>
            <button @click="userStore.setUser(null)" class="hover:text-gray-300">退出</button>
          </template>
          <template v-else>
            <RouterLink to="/user/login" class="hover:text-gray-300">登录</RouterLink>
            <RouterLink to="/user/register" class="hover:text-gray-300">注册</RouterLink>
          </template>
        </div>
      </nav>
    </header>
    <RouterView />
  </div>
</template>

<style scoped>
header {
  background-color: #f8f8f8;
  padding: 1rem;
  border-bottom: 1px solid #e7e7e7;
}

nav {
  display: flex;
  gap: 1rem;
}

nav a {
  text-decoration: none;
  color: #333;
  font-weight: bold;
}

nav a:hover {
  color: #42b983;
}
</style>