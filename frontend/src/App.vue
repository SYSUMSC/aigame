<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import { useUserStore } from "./stores/user";
import { useRouter } from "vue-router";
// @ts-ignore
import { Collapse } from "bootstrap";

const userStore = useUserStore();
const router = useRouter();

const logout = () => {
  userStore.setUser(null);
  router.push("/");
};

// 封装导航跳转函数，跳转后自动关闭导航栏
const navigateAndCloseNav = (routePath: string) => {
  router.push(routePath);

  const navbarCollapse = document.getElementById("navbarNav");
  if (navbarCollapse && navbarCollapse.classList.contains("show")) {
    const bsCollapse = new Collapse(navbarCollapse, {
      toggle: false,
    });
    bsCollapse.hide();
  }
};
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <RouterLink class="navbar-brand" to="/">AI 竞赛平台</RouterLink>
      <button
        class="navbar-toggler"
        type="button"
        data-bs-toggle="collapse"
        data-bs-target="#navbarNav"
        aria-controls="navbarNav"
        aria-expanded="false"
        aria-label="Toggle navigation"
      >
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <a
              class="nav-link"
              @click.prevent="navigateAndCloseNav('/')"
              href="#"
              >首页</a
            >
          </li>
          <template v-if="userStore.isLoggedIn()">
            <li class="nav-item">
              <a
                class="nav-link"
                @click.prevent="navigateAndCloseNav('/user/')"
                href="#"
                >用户中心</a
              >
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                @click.prevent="navigateAndCloseNav('/user/team')"
                href="#"
                >队伍管理</a
              >
            </li>
            <li class="nav-item">
              <button @click="logout" class="btn nav-link">退出</button>
            </li>
          </template>
          <template v-else>
            <li class="nav-item">
              <a
                class="nav-link"
                @click.prevent="navigateAndCloseNav('/user/login')"
                href="#"
                >登录</a
              >
            </li>
            <li class="nav-item">
              <a
                class="nav-link"
                @click.prevent="navigateAndCloseNav('/user/reg')"
                href="#"
                >注册</a
              >
            </li>
          </template>
        </ul>
      </div>
    </div>
  </nav>
  <!-- 灰色背景 -->
  <RouterView class="container"/>
</template>

<style scoped>
.collapse {
  visibility: visible;
}
</style>
