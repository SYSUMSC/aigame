<template>
  <div class="min-h-screen bg-gray-100 py-6 flex flex-col sm:py-12">
    <div class="container mx-auto">
      <div class="card shadow-lg">
        <div class="card-body p-6">
          <h1 class="text-2xl font-bold mb-6 text-center">用户中心</h1>
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
            <p class="text-center text-gray-600">请登录以查看用户信息。</p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from '../stores/user';

const userStore = useUserStore();
</script>

<style scoped></style>
