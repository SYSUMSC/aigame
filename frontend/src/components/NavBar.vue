<script setup lang="ts">
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import { ref, watch } from "vue";
import { AntdWindowsWidth } from "../constants/antd-windows-width";
import { LogoutOutlined } from "@ant-design/icons-vue";
import { h } from "vue";
import { windowWidth } from "../global/window";

const userStore = useUserStore();
const router = useRouter();



// 当前选中的菜单项
const selectedKeys = ref<string[]>([router.currentRoute.value.path]);

// 监听 selectedKeys 的变化并跳转路由
watch(selectedKeys, (newKeys) => {
    router.push(newKeys[0]);
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
    <a-menu v-model:selectedKeys="selectedKeys" theme="light"
        v-bind:mode="windowWidth < AntdWindowsWidth.lg ? 'inline' : 'horizontal'" style="width: 100%; height: 100%;" :class="[windowWidth > AntdWindowsWidth.lg? '':'flex flex-col justify-start']">
        <a-menu-item v-if="windowWidth > AntdWindowsWidth.lg" key="/" class="amenu-select-hidden">
            <img src="/logo_aigame.svg" alt="AIGame" class="size-[50px] ">
        </a-menu-item>
        <a-menu-item key="/" style="" :class="windowWidth > AntdWindowsWidth.lg&& 'amenu-select'">
            首页
        </a-menu-item>
        <a-menu-item key="/info" :class="windowWidth > AntdWindowsWidth.lg&& 'amenu-select'" :disabled="!userStore.isLoggedIn()">
            用户中心
        </a-menu-item>
        <a-menu-item key="/competitioncenter" :class="windowWidth > AntdWindowsWidth.lg&& 'amenu-select'" :disabled="!userStore.isLoggedIn()">
            比赛中心
        </a-menu-item>
        <a-menu-item key="/announcements" :class="windowWidth > AntdWindowsWidth.lg&& 'amenu-select'" :disabled="!userStore.isLoggedIn()">
            公告
        </a-menu-item>
        <template v-if="userStore.isLoggedIn()">
            <a-menu-item v-if="windowWidth > AntdWindowsWidth.lg" key="/info" class="amenu-select-hidden !ml-auto lg:text-xl py-3 lg:!px-0">
                {{ userStore.user!.username }}
            </a-menu-item>
            <a-menu-item key="/logout" :class="[windowWidth > AntdWindowsWidth.lg? 'amenu-select':'', 'amenu-compact-l' ,'py-1','justify-self-end', 'mr-10' ,'lg:!px-0']">
                <a-button v-if="windowWidth > AntdWindowsWidth.lg" size="large" shape="circle" :icon="h(LogoutOutlined)" danger style="padding: 0; border: none;" class="!p-0 abtn-icon-lg"/>
                <span class="text-red-500" v-else>退出登录</span>
            </a-menu-item>
        </template>
        <template v-else>
            <a-menu-item key="/user/login" class="amenu-select-hidden !ml-auto lg:!px-0">
                <a-button v-if="windowWidth > AntdWindowsWidth.lg">
                    登录
                </a-button>
                <span v-else>登录</span>
            </a-menu-item>
            <a-menu-item key="/user/reg" class="amenu-select-hidden">
                <a-button type="primary" v-if="windowWidth > AntdWindowsWidth.lg">
                    注册
                </a-button>
                <span v-else>注册</span>
            </a-menu-item>
        </template>
    </a-menu>
</template>

<style scoped>
</style>