<script setup lang="ts">
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import { ref, watch } from "vue";
import { AntdWindowsWidth } from "../constants/antd-windows-width";

const {windowWidth} = defineProps<{windowWidth: number}>();

const userStore = useUserStore();
const router = useRouter();



// 当前选中的菜单项
const selectedKeys = ref<string[]>([router.currentRoute.value.path]);

// 监听 selectedKeys 的变化并跳转路由
watch(selectedKeys, (newKeys) => {
  // const newKey = newKeys[0];
  // if (newKey === '/logout') {
  //   logout();
  // } else {
    router.push(newKeys[0]);
  // }
});

// 新的tab切换逻辑
watch(router.currentRoute, (to) => {
    if (to.path === '/logout') {
    logout();
  } else {
    // TODO 如果比赛和赛题用的是子路由的形式就可以继续在"比赛中心"的tab处高亮
    router.push(to.path);
    selectedKeys.value = [to.path];
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
    <a-menu v-model:selectedKeys="selectedKeys" theme="dark" v-bind:mode=" windowWidth < AntdWindowsWidth.lg  ? 'inline' : 'horizontal' " >
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