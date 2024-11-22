<template>
    <a-config-provider :theme="{
    token:{
        colorPrimary: '#757FDE',
        // colorPrimaryActive: '#000',
        colorPrimaryHover: '#6C75CA',
        // colorPrimaryBg: '#757FDE',
        // colorPrimaryText: '#757FDE',
        // colorPrimaryTextHover: '#6C75CA',
        // colorLink: '#757FDE',
        colorLinkHover: '#757FDE',

        colorPrimaryBgHover: '#000',
        // colorBgBase: '#FFF',
        // colorBgContainer: '#fff',
        colorBgLayout: '#FAFAFA',
        // colorPrimaryBg: '#757FDE',
        // colorBgElevated:'#757FDE'
        colorError:'#FF5C5C',
        colorErrorHover: '#B44343',
        colorErrorActive:''
    }}">
        <a-layout class="h-screen">
            <a-layout-sider style="position: fixed;" theme="light" class="h-screen z-50" v-if="windowWidth < AntdWindowsWidth.lg"
                breakpoint="lg" collapsed-width="0" @collapse="onCollapse" @breakpoint="onBreakpoint">
                <NavBar :window-width="windowWidth" />
            </a-layout-sider>
            <a-layout>
                <a-layout-header v-if="windowWidth >= AntdWindowsWidth.lg"
                    style="height: 50px;max-height: 50px; line-height: 50px; background-color: '#000无效'; padding: 0 ">
                    <NavBar :window-width="windowWidth" />
                </a-layout-header>
                <a-layout-content class="overflow-x-hidden overflow-y-aut" style="padding: 30px ;">
                    <!-- <div :style="{ padding: '24px', background: '#fff', height: '100%' }"> -->
                    <RouterView />
                    <!-- </div> -->
                </a-layout-content>
                <a-layout-footer style="text-align: center">
                    Ant Design ©2018 Created by Ant UED
                </a-layout-footer>
            </a-layout>
        </a-layout>
    </a-config-provider>
</template>
<script lang="ts" setup>
import { onBeforeUnmount, onMounted, ref } from 'vue';
import { UserOutlined, VideoCameraOutlined, UploadOutlined } from '@ant-design/icons-vue';
import { RouterView } from "vue-router";
import NavBar from './components/NavBar.vue';
import { AntdWindowsWidth } from './constants/antd-windows-width';
const onCollapse = (collapsed: boolean, type: string) => {
    console.log(collapsed, type);
};

const onBreakpoint = (broken: boolean) => {
    console.log(broken);
};
const windowWidth = ref(0);
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
