<script setup lang="ts">
import { RouterLink, RouterView } from "vue-router";
import { useUserStore } from "./stores/user";
import { useRouter } from "vue-router";
// @ts-ignore
import { Collapse } from "bootstrap";
import { onMounted, ref } from "vue";
import axios from "axios";


const userStore = useUserStore();
const router = useRouter();
const isCaptain = ref(false);
const teamInfo = ref<any>(null);
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

const fetchTeamInfo = async () => {
  try {
    const res = await axios.get("/api/user/team_info");
    if (res.status === 200 && res.data.code === 0) {
      teamInfo.value = res.data.data;
      if (userStore.user) {
        userStore.user.team_id = teamInfo.value.id;
      }
      isCaptain.value = teamInfo.value.captain_id === userStore.user?.id;
    } else {
      if (res.data.msg === "用户不在任何队伍中" && userStore.user) {
        // 只要让这里不再显示任何信息，由于此时没有报错，用户可以再次使用当前页面重新加入队伍
        userStore.user.team_id = null;
      } else {
        alert(res.data.msg);
        // 暂时试试返回用户界面看是否还有其它问题产生
        router.push("/user");
      }
    }
  } catch (error) {
    console.error(error);
    alert("获取队伍信息失败，请稍后再试。");
  }
}

onMounted( async () => {
  await fetchTeamInfo()
  console.log('isCaptaion value is ' + isCaptain.value)
})
</script>

<template>
  <nav class="navbar navbar-expand-lg navbar-light bg-light">
    <div class="container-fluid">
      <RouterLink class="navbar-brand" to="/">AI 竞赛平台</RouterLink>
      <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarNav"
        aria-controls="navbarNav" aria-expanded="false" aria-label="Toggle navigation">
        <span class="navbar-toggler-icon"></span>
      </button>
      <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav ms-auto">
          <li class="nav-item">
            <a class="nav-link" @click.prevent="navigateAndCloseNav('/')" href="#">首页</a>
          </li>
          <template v-if="userStore.isLoggedIn()">
            <!-- <li class="nav-item">
              <a class="nav-link" @click.prevent="navigateAndCloseNav('/user/')" href="#">用户中心</a>
            </li> -->
            <li class="nav-item">
              <a class="nav-link" v-if="isCaptain" @click.prevent="navigateAndCloseNav('/user/team')" href="#">队伍管理</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" @click.prevent="navigateAndCloseNav('/info')" href="#">用户信息</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" @click.prevent="navigateAndCloseNav('/competitioncenter')" href="#">比赛中心</a>
            </li>
            <li class="nav-item">
              <button @click="logout" class="btn nav-link">退出</button>
            </li>
          </template>
          <template v-else>
            <li class="nav-item">
              <a class="nav-link" @click.prevent="navigateAndCloseNav('/user/login')" href="#">登录</a>
            </li>
            <li class="nav-item">
              <a class="nav-link" @click.prevent="navigateAndCloseNav('/user/reg')" href="#">注册</a>
            </li>

          </template>
        </ul>
      </div>
    </div>
  </nav>
  <!-- 灰色背景 -->
  <RouterView class="container" />
</template>

<style scoped>
.collapse {
  visibility: visible;
}
</style>
