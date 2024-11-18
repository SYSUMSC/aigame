<template>
  <a-layout class="h-screen">
    <!-- <a-layout-sider
      breakpoint="lg"
      collapsed-width="0"
      @collapse="onCollapse"
      @breakpoint="onBreakpoint"
    >
  </a-layout-sider> -->
    <a-layout>
      <a-layout-header :style="{ background: '#fff', padding: 0 }" >
        <NavBar />
      </a-layout-header>
      <a-layout-content class="h-screen overflow-y-auto" :style="{ margin: '24px 16px 0' }">
        <div :style="{ padding: '24px', background: '#fff', height: '100%' }">  <RouterView /></div>
      </a-layout-content>
      <a-layout-footer style="text-align: center">
        Ant Design ©2018 Created by Ant UED
      </a-layout-footer>
    </a-layout>
  </a-layout>
</template>
<script lang="ts" setup>
import { ref } from 'vue';
import { UserOutlined, VideoCameraOutlined, UploadOutlined } from '@ant-design/icons-vue';
import { RouterView } from "vue-router";
import NavBar from './components/NavBar.vue';
const onCollapse = (collapsed: boolean, type: string) => {
  console.log(collapsed, type);
};

const onBreakpoint = (broken: boolean) => {
  console.log(broken);
};

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
