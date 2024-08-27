<template>
  <div
    class="min-h-screen bg-gray-100 py-6 flex flex-col justify-center sm:py-12"
  >
    <div class="relative py-3 sm:max-w-xl sm:mx-auto">
      <div
        class="relative px-4 py-10 bg-white shadow-lg sm:rounded-3xl sm:p-20"
      >
        <h1 class="text-2xl font-bold mb-6">登录</h1>
        <form @submit.prevent="login">
          <div class="mb-4">
            <label for="username" class="block text-gray-700">用户名</label>
            <input
              type="text"
              id="username"
              v-model="username"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50"
              required
            />
          </div>
          <div class="mb-4">
            <label for="password" class="block text-gray-700">密码</label>
            <input
              type="password"
              id="password"
              v-model="password"
              class="mt-1 block w-full border-gray-300 rounded-md shadow-sm focus:border-indigo-500 focus:ring focus:ring-indigo-500 focus:ring-opacity-50"
              required
            />
          </div>
          <button
            type="submit"
            class="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
          >
            登录
          </button>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';

const username = ref('');
const password = ref('');
const userStore = useUserStore();
const router = useRouter();

const login = async () => {
  try {
    const res = await axios.post("/api/user/login", {
      username: username.value,
      password: password.value,
    });

    // 检查是否登录成功
    if (res.status === 200 && res.data.code === 0) {
      const token = res.data.data.access_token;

      // 存储 token
      localStorage.setItem("token", token);
      // 设置 axios 默认头
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

      // 打印请求头以检查
      console.log("Authorization Header:", axios.defaults.headers.common['Authorization']);

      // 调用 me API 获取用户信息
      const userInfoRes = await axios.get("/api/user/info");
      console.log("User Info Response:", userInfoRes);

      if (userInfoRes.status === 200 && userInfoRes.data.code === 0) {
        const userData = userInfoRes.data.data;
        // 存储用户数据
        userStore.setUser(userData);

        // 跳转到用户主页
        router.push("/user");
      } else {
        alert("获取用户信息失败");
      }
    } else {
      alert(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    alert("登录失败，请稍后再试。");
  }
};
</script>