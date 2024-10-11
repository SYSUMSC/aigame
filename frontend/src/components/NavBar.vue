<script setup lang="ts">
import { RouterLink, useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import { ref } from 'vue';

const userStore = useUserStore();
const router = useRouter();
const logout = () => {
  userStore.setUser(null);
  router.push("/");
};

const navigateAndCloseNav = (routePath: string) => {
  router.push(routePath);
};
const isOpen = ref(false);
</script>

<template>
  <nav class="bg-white shadow-md fixed w-full z-10 top-0 left-0">
    <div class="container mx-auto px-4 py-4 flex justify-between items-center">
      <!-- Logo -->
      <RouterLink class="text-xl font-bold text-gray-800" to="/">AI 竞赛平台</RouterLink>

      <!-- Hamburger Menu for Mobile -->
      <button
        @click="isOpen = !isOpen"
        class="block lg:hidden text-gray-800 focus:outline-none">
        <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor" class="w-6 h-6">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
        </svg>
      </button>

      <!-- Menu Links -->
      <div class="hidden lg:flex space-x-6">
        <RouterLink class="text-gray-800 hover:text-blue-600" to="/" @click="navigateAndCloseNav('/')">首页</RouterLink>

        <template v-if="userStore.isLoggedIn()">
          <RouterLink class="text-gray-800 hover:text-blue-600" to="/info" @click="navigateAndCloseNav('/info')">用户中心</RouterLink>
          <RouterLink class="text-gray-800 hover:text-blue-600" to="/competitioncenter" @click="navigateAndCloseNav('/competitioncenter')">比赛中心</RouterLink>
          <button @click="logout" class="text-gray-800 hover:text-blue-600">退出</button>
        </template>
        <template v-else>
          <RouterLink class="text-gray-800 hover:text-blue-600" to="/user/login" @click="navigateAndCloseNav('/user/login')">登录</RouterLink>
          <RouterLink class="text-gray-800 hover:text-blue-600" to="/user/reg" @click="navigateAndCloseNav('/user/reg')">注册</RouterLink>
        </template>
      </div>
    </div>

    <!-- Mobile Menu -->
    <div v-if="isOpen" class="lg:hidden bg-white shadow-md">
      <ul class="space-y-4 py-4">
        <li>
          <RouterLink class="block text-gray-800 hover:text-blue-600 px-4" to="/" @click="navigateAndCloseNav('/')">首页</RouterLink>
        </li>
        <template v-if="userStore.isLoggedIn()">
          <li>
            <RouterLink class="block text-gray-800 hover:text-blue-600 px-4" to="/info" @click="navigateAndCloseNav('/info')">用户中心</RouterLink>
          </li>
          <li>
            <RouterLink class="block text-gray-800 hover:text-blue-600 px-4" to="/competitioncenter" @click="navigateAndCloseNav('/competitioncenter')">比赛中心</RouterLink>
          </li>
          <li>
            <button @click="logout" class="block text-gray-800 hover:text-blue-600 px-4">退出</button>
          </li>
        </template>
        <template v-else>
          <li>
            <RouterLink class="block text-gray-800 hover:text-blue-600 px-4" to="/user/login" @click="navigateAndCloseNav('/user/login')">登录</RouterLink>
          </li>
          <li>
            <RouterLink class="block text-gray-800 hover:text-blue-600 px-4" to="/user/reg" @click="navigateAndCloseNav('/user/reg')">注册</RouterLink>
          </li>
        </template>
      </ul>
    </div>
  </nav>
</template>



<style scoped>
/* 可以在此处添加自定义样式 */
</style>
