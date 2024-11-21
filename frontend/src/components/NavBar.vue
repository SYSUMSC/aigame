<script setup lang="ts">
import { useRouter } from "vue-router";
import { useUserStore } from "../stores/user";
import { ref, watch } from "vue";
import { AntdWindowsWidth } from "../constants/antd-windows-width";
import { LogoutOutlined } from "@ant-design/icons-vue";
import { h } from "vue";

const { windowWidth } = defineProps<{ windowWidth: number }>();

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
    <a-menu v-model:selectedKeys="selectedKeys" theme="light"
        v-bind:mode="windowWidth < AntdWindowsWidth.lg ? 'inline' : 'horizontal'" style="width: 100%;" class="w-ful">
        <a-menu-item key="/" class="amenu-select-hidden">
            <img src="/logo_aigame.svg" alt="AIGame" class="size-[50px] ">
        </a-menu-item>
        <a-menu-item key="/" style="" class="amenu-select">
            首页
        </a-menu-item>
        <a-menu-item key="/info" class="amenu-select" :disabled="!userStore.isLoggedIn()">
            用户中心
        </a-menu-item>
        <a-menu-item key="/competitioncenter" class="amenu-select" :disabled="!userStore.isLoggedIn()">
            比赛中心
        </a-menu-item>
        <a-menu-item key="/announcements" class="amenu-select" :disabled="!userStore.isLoggedIn()">
            公告
        </a-menu-item>
        <template v-if="userStore.isLoggedIn()">
            <a-menu-item key="/info" class="amenu-select-hidden force-ml-auto text-xl py-3 force-px-0">
                {{ userStore.user!.username }}
            </a-menu-item>
            <a-menu-item key="/logout" class="amenu-select amenu-compact-l py-1 mr-10 force-px-0">
                <a-button size="large" shape="circle" :icon="h(LogoutOutlined)" danger style="padding: 0; border: none;" class="force-p-0 abtn-icon-lg"/>
            </a-menu-item>
        </template>
        <template v-else>
            <!-- <div class="justify-self-end"> -->
            <a-menu-item key="/user/login" class="amenu-select-hidden force-ml-auto force-px-0">
                <a-button>
                    登录
                </a-button>
            </a-menu-item>
            <!-- flex- self-end force-justify-self-end fle justify-end  -->
            <a-menu-item key="/user/reg" class="amenu-select-hidden force-pl-">
                <a-button type="primary" class="force-p">
                    注册
                </a-button>
            </a-menu-item>
            <!-- </div> -->
            <!-- <div class="self-end"> -->
                <!-- <a-button class="justify-self-end">
                    登录
                </a-button>
                <a-button type="primary" class="justify-self-end">
                    注册
                </a-button> -->
            <!-- </div>  -->
        </template>
    </a-menu>
</template>

<style scoped>
/* .amenu-select-hidden::after{
    display: none;
    border: none;
    @apply border-none
} */
 /* !啊啊所以原来是在这里不生效艹？？？…… */
/* .ant-menu-item-selected::after{
    border-bottom-width: 0 !important;
} */
/* ::v-deep .ant-menu-light.ant-menu-horizontal >.ant-menu-item::after, :where(.css-dev-only-do-not-override-1p3hq3p).ant-menu-light.ant-menu-horizontal >.ant-menu-submenu::after{
    border: none !important;
} */
 /* :where(.css-dev-only-do-not-override-1p3hq3p).ant-menu-light.ant-menu-horizontal >.ant-menu-submenu-selected::after{
    border-bottom-width: 0 !important;
 } */

</style>