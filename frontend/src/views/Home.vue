<template>
  <div
    class="flex flex-col items-center justify-center min-h-screen bg-gray-100"
  >
    <!-- 平台介绍 -->
    <div class="text-center">
      <h1 class="text-4xl font-bold text-gray-800 mb-4">AI 竞赛平台</h1>
      <p class="text-lg text-gray-600 mb-6">
        欢迎来到 AI 竞赛平台，在这里你可以参与各种 AI
        挑战，与全球开发者一较高下，展示你的 AI 技能，并赢取丰厚奖励。
      </p>
      <p class="text-lg text-gray-600 mb-6">
        无论你是初学者还是经验丰富的开发者，我们的平台都能为你提供适合的竞赛和学习资源，助力你的
        AI 旅程。
      </p>
    </div>

    <!-- 按钮 -->
    <div class="flex space-x-4">
      <router-link
        to="/user/login"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        登录
      </router-link>
      <router-link
        to="/user/register"
        class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
      >
        注册
      </router-link>
    </div>
  </div>
</template>

<script setup lang="ts"></script>

<style scoped></style>
