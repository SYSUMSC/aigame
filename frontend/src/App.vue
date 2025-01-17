<template>
    <a-config-provider :theme="{
    token:{
        colorPrimary: '#757FDE',
        colorPrimaryHover: '#6C75CA',
        colorLinkHover: '#757FDE',

        colorPrimaryBgHover: '#000',
        colorBgLayout: '#FAFAFA',
        colorError:'#FF5C5C',
        colorErrorHover: '#B44343',
        colorErrorActive: ''
    }}">
        <a-layout class="h-screen">
            <a-layout-sider style="position: fixed;" theme="light" class="h-screen z-50" v-if="windowWidth < AntdWindowsWidth.lg"
                breakpoint="lg" collapsed-width="0" @collapse="onCollapse" @breakpoint="onBreakpoint">
                <NavBar/>
            </a-layout-sider>
            <a-layout>
                <a-layout-header v-if="windowWidth >= AntdWindowsWidth.lg"
                    style="height: 50px;max-height: 50px; line-height: 50px; background-color: '#000无效'; padding: 0 ">
                    <NavBar/>
                </a-layout-header>
                <a-layout-content class="overflow-x-hidden overflow-y-aut" style="padding: 30px ;">
                    <RouterView />
                </a-layout-content>
                <a-layout-footer style="text-align: center">
                    Ant Design ©2018 Created by Ant UED
                </a-layout-footer>
            </a-layout>
        </a-layout>
    </a-config-provider>
</template>
<script lang="ts" setup>
import { onBeforeUnmount, onMounted } from 'vue';
import { RouterView } from "vue-router";

import NavBar from './components/NavBar.vue';

import { AntdWindowsWidth } from './constants/antd-windows-width';
import { windowWidth } from './global/window.js'
const onCollapse = (collapsed: boolean, type: string) => {
    console.log(collapsed, type);
};

const onBreakpoint = (broken: boolean) => {
    console.log(broken);
};
onMounted(() => {
    windowWidth.value = window.innerWidth;
    window.addEventListener('resize', () => {
        windowWidth.value = window.innerWidth;
    });
})
onBeforeUnmount(() => {
    window.removeEventListener('resize', () => {
        windowWidth.value = window.innerWidth;
    });
})



</script>
<style scoped>
#components-layout-demo-responsive .logo {
    height: 32px;
    background: rgba(255, 255, 255, 0.2);
    margin: 16px;
}

.site-layout-sub-header-background {
    background: #fff;
}

.site-layout-background {
    background: #fff;
}

[data-theme='dark'] .site-layout-sub-header-background {
    background: #141414;
}
</style>
