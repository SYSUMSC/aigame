<template>
  <div class="flex flex-col items-center justify-center h-screen">  
    <!-- 平台介绍 -->  
      <div class="text-center">  
        <h1 class="text-4xl font-bold text-gray-800 mb-4">AI 竞赛平台</h1>  
        <p v-html="TextIntro" class="text-lg text-gray-600 mb-6"></p>  
        <p v-html="TextWelc" class="text-lg text-gray-600 mb-6"></p>  
      </div>
    <div class="flex space-x-4 py-4" v-if="!userStore.user">
      <router-link
        to="/user/login"
        class="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded"
      >
        登录
      </router-link>
      <router-link
        to="/user/reg"
        class="bg-green-500 hover:bg-green-700 text-white font-bold py-2 px-4 rounded"
      >
        注册
      </router-link>
    </div>
  </div>  
</template>  
  
<script setup lang="ts">  
import { useUserStore } from '../stores/user'  
import { Ref, ref, onMounted } from 'vue'  
  
const userStore = useUserStore()  
  
// 原始文本  
const originalTextIntro = "欢迎来到 AI 竞赛平台，在这里你可以参与各种 AI 挑战，与全球开发者一较高下，展示你的 AI 技能，并赢取丰厚奖励。"  
const originalTextWelc = "无论你是初学者还是经验丰富的开发者，我们的平台都能为你提供适合的竞赛和学习资源，助力你的 AI 旅程。"  
  
// 格式化后的文本，用于逐字显示  
const TextIntro = ref('')  
const TextWelc = ref('')  
  
// 模拟打字效果  
const typeEffect = (text: string, target: Ref<string>, interval: number = 100) => {  
  let index = 0
  const type = setInterval(() => {  
    if (index < text.length) {
      target.value += text.charAt(index)  
      index++  
    } else {  
      clearInterval(type)  
    }  
  }, interval)  
}  
  
onMounted(() => {  
  typeEffect(originalTextIntro, TextIntro)  
  typeEffect(originalTextWelc, TextWelc, 130) // 稍微慢一点的间隔  
})  
</script>