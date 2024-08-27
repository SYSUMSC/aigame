<template>
    <div class="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12">
      <div class="relative py-3 sm:max-w-xl sm:mx-auto">
        <div class="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20">
          <h1 class="text-2xl font-bold mb-6">用户中心</h1>
          <div v-if="userStore.user">
            <div class="mb-4">
              <label class="block text-gray-700">用户名</label>
              <p class="text-gray-900">{{ userStore.user.username }}</p>
            </div>
            <div class="mb-4">
              <label class="block text-gray-700">电子邮件</label>
              <p class="text-gray-900">{{ userStore.user.email }}</p>
            </div>
            <div class="mb-4">
              <label class="block text-gray-700">姓名</label>
              <p class="text-gray-900">{{ userStore.user.name }}</p>
            </div>
            <div class="mb-4">
              <label class="block text-gray-700">学号</label>
              <p class="text-gray-900">{{ userStore.user.student_id }}</p>
            </div>
          </div>
          <div v-else>
            <p>请登录以查看用户信息。</p>
          </div>
        </div>
      </div>
    </div>
  </template>

  <script setup lang="ts">
  import { useUserStore } from '../stores/user';

  const userStore = useUserStore();
  </script>

  <style scoped>
  </style>