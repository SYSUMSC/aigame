import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import axios from "axios";
import Home from "../views/Home.vue";
import Login from "../views/Login.vue";
import Reg from "../views/Reg.vue";
import Forget from "../views/Forget.vue";
import UserCenter from "../views/UserCenter.vue";
import Team from "../views/Team.vue";
import CompetitionCenter from "../views/CompetitionCenter.vue";
import CompetitionDetail from "../views/CompetitionDetail.vue";
import { useUserStore } from "../stores/user";
import Column from "../views/Column.vue";
import ProblemDetail from "../views/ProblemDetail.vue";
import Leaderboard from "../views/Leaderboard.vue";
import Announcements from "../views/Announcements.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "首页",
    component: Home,
    alias: '/home'
  },
  {
    path: "/user/login",
    name: "登录",
    component: Login,
  },
  {
    path: "/user/reg",
    name: "注册",
    component: Reg,
  },
  {
    path: "/user/forget",
    name: "忘记密码",
    component: Forget,
  },
  {
    path: "/user/team",
    name: "队伍管理",
    component: Team,
    meta: { requiresAuth: true },
  },
  {
    path: "/user",
    name: "用户中心",
    component: UserCenter,
    meta: { requiresAuth: true },
  },
  {
    path: "/info",
    name: "Info",
    component: Column,
    meta: { requiresAuth: true },
  },
  {
    path: "/competitioncenter",
    name: "比赛中心",
    component: CompetitionCenter,
    meta: { requiresAuth: true },
  },
  {
    path: '/competition/:id',
    name: 'CompetitionDetail',
    component: CompetitionDetail,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/problem/:id',
    name: 'ProblemDetail',
    component: ProblemDetail,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/competition/:id/leaderboard',
    name: 'CompetitionLeaderboard',
    component: Leaderboard,
    meta: { requiresAuth: true },
    props: true
  },
  {
    path: '/announcements',
    name: '公告',
    component: Announcements,
    meta: { requiresAuth: true },
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach(async (to, from, next) => {
  const userStore = useUserStore();

  // 如果有 Token 且用户未登录，需要获取用户信息
  if (userStore.isLoggedIn()) {
    try {
      // 获取用户信息
      const userInfoRes = await axios.get("/api/user/info");
      if (userInfoRes.status === 200 && userInfoRes.data.code === 0) {
        const userData = userInfoRes.data.data;
        userStore.setUser(userData); // 将用户信息存储到 Pinia
      } else {
        localStorage.removeItem("token");
        userStore.setUser(null);
        next({ name: "登录" }); // 信息获取失败，重定向到登录页
      }
    } catch (error) {
      console.error("获取用户信息失败:", error);
      localStorage.removeItem("token");
      userStore.setUser(null);
      next({ name: "登录" }); // 失败，重定向到登录页
    }
  }

  // 如果目标路由需要认证
  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!userStore.isLoggedIn()) {
      next({ name: "登录", query: { redirect: to.fullPath } }); // 未登录，重定向到登录页面，并附带重定向路径
    } else {
      next(); // 用户已登录，继续导航
    }
  } else {
    next(); // 不需要认证的路由，直接继续导航
  }

  // 更新网页标题
  const defaultTitle = "AI 竞赛平台"; // 默认的网页标题
  if (to.name) {
    document.title = `${defaultTitle} -- ${String(to.name)}`;
  } else {
    document.title = defaultTitle;
  }
});

export default router;