<template>
  <div class="pt-5">
    <div class="row justify-content-center">
      <div class="col-md-6">
        <div class="card">
          <div class="card-header">
            <h3 class="text-center">登录</h3>
          </div>
          <div class="card-body">
            <form @submit.prevent="login">
              <div class="form-group mb-3">
                <label for="username">用户名</label>
                <input
                  type="text"
                  id="username"
                  v-model="username"
                  class="form-control"
                  required
                />
              </div>
              <div class="form-group mb-3">
                <label for="password">密码</label>
                <input
                  type="password"
                  id="password"
                  v-model="password"
                  class="form-control"
                  required
                />
              </div>
              <button
                type="submit"
                class="btn btn-primary w-100"
              >
                登录
              </button>
            </form>
          </div>
        </div>
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
        router.push("/info");
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