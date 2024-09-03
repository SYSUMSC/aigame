import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import Home from "../views/Home.vue";
import Login from "../views/Login.vue";
import Reg from "../views/Reg.vue";
import UserCenter from "../views/UserCenter.vue";
import Team from "../views/Team.vue";
import { useUserStore } from "../stores/user";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/",
    name: "首页",
    component: Home,
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
];

const router = createRouter({
  history: createWebHistory(),
  routes,
});

router.beforeEach((to, from, next) => {
  const userStore = useUserStore();

  if (to.matched.some((record) => record.meta.requiresAuth)) {
    if (!userStore.isLoggedIn()) {
      next({ name: "Login" });
    } else {
      next();
    }
  } else {
    next();
  }

  // 更新网页标题
  const defaultTitle = 'AI 竞赛平台'; // 默认的网页标题
  if (to.name) {
    document.title = `${defaultTitle} -- ${String(to.name)}`;
  } else {
    document.title = defaultTitle;
  }
});

export default router;
