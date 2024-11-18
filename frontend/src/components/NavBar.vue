<script setup lang="ts">
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import { ref, watch } from "vue";

const userStore = useUserStore();
const router = useRouter();

// 当前选中的菜单项
const selectedKeys = ref<string[]>(['/']);

// 监听 selectedKeys 的变化并跳转路由
watch(selectedKeys, (newKeys) => {
  const newKey = newKeys[0];
  if (newKey === '/logout') {
    logout();
  } else {
    router.push(newKey);
  }
});

// 用户登出
const logout = () => {
  userStore.setUser(null);
  selectedKeys.value = ['/'];
  router.push('/');
};
</script>

<template>
    <a-menu v-model:selectedKeys="selectedKeys" theme="dark" mode="inline">
      <a-menu-item key="/">
        首页
      </a-menu-item>
      <template v-if="userStore.isLoggedIn()">
        <a-menu-item key="/info">
          用户中心
        </a-menu-item>
        <a-menu-item key="/competitioncenter">
          比赛中心
        </a-menu-item>
        <a-menu-item key="/announcements">
          公告
        </a-menu-item>
        <a-menu-item key="/logout">
          退出
        </a-menu-item>
      </template>
      <template v-else>
        <a-menu-item key="/user/login">
          登录
        </a-menu-item>
        <a-menu-item key="/user/reg">
          注册
        </a-menu-item>
      </template>
    </a-menu>
</template>