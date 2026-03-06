<template>
  <div class="min-h-screen bg-gray-50 layout-wrapper">
    <!-- 自研导航栏 -->
    <div class="bg-white shadow w-full sticky top-0 z-40">
      <div class="flex items-center h-16 px-4 max-w-none">
        <!-- Logo/品牌名 -->
        <NuxtLink
          to="/"
          class="text-xl font-bold text-gray-900 hover:text-blue-600 transition-colors duration-150 shrink-0 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 rounded-md px-2 py-1"
        >
          {{ settings.title || "AI竞赛平台" }}
        </NuxtLink>

        <!-- 桌面端导航 - 居中显示 -->
        <div class="hidden md:flex md:flex-1 md:justify-center">
          <nav class="flex items-center space-x-1">
            <template v-for="item in desktopNavItems" :key="item.text">
              <!-- 有子菜单的导航项 -->
              <div v-if="item.children && item.children.length" class="relative group">
                <button
                  class="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                  :class="
                    isAdminSectionActive(item)
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
                  "
                >
                  <i v-if="item.icon" :class="['nav-icon', item.icon, 'mr-2']" aria-hidden="true"></i>
                  {{ item.text }}
                  <svg
                    class="ml-1 h-4 w-4"
                    fill="none"
                    stroke="currentColor"
                    viewBox="0 0 24 24"
                  >
                    <path
                      stroke-linecap="round"
                      stroke-linejoin="round"
                      stroke-width="2"
                      d="M19 9l-7 7-7-7"
                    />
                  </svg>
                </button>
                <!-- 下拉菜单 -->
                <div
                  class="absolute left-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200"
                >
                  <div class="py-1">
                    <NuxtLink
                      v-for="child in item.children"
                      :key="child.to || child.text"
                      :to="child.to"
                      class="block px-4 py-2 text-sm transition-colors duration-150"
                      :class="
                        isActiveRoute(child.to)
                          ? 'text-blue-600 bg-blue-50'
                          : 'text-gray-700 hover:bg-gray-100'
                      "
                    >
                      <i v-if="child.icon" :class="['nav-icon', child.icon, 'mr-2']" aria-hidden="true"></i>
                      {{ child.text }}
                    </NuxtLink>
                  </div>
                </div>
              </div>
              <!-- 普通导航项 -->
              <NuxtLink
                v-else
                :to="item.to"
                class="inline-flex items-center px-3 py-2 text-sm font-medium rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
                :class="
                  isActiveRoute(item.to)
                    ? 'text-blue-600 bg-blue-50'
                    : 'text-gray-700 hover:text-gray-900 hover:bg-gray-100'
                "
              >
                <i v-if="item.icon" :class="['nav-icon', item.icon, 'mr-2']" aria-hidden="true"></i>
                {{ item.text }}
              </NuxtLink>
            </template>
          </nav>
        </div>

        <!-- 桌面端右侧区域 -->
        <div class="hidden md:flex md:items-center md:space-x-4 shrink-0">
          <template v-if="isLoggedIn">
            <!-- 用户下拉菜单 -->
            <div class="relative group">
              <button
                data-testid="nav-user-menu"
                class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              >
                <i class="nav-icon fa-solid fa-user mr-2" aria-hidden="true"></i>
                欢迎, {{ user?.username }}
                <svg
                  class="ml-1 h-4 w-4"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    stroke-linecap="round"
                    stroke-linejoin="round"
                    stroke-width="2"
                    d="M19 9l-7 7-7-7"
                  />
                </svg>
              </button>
              <!-- 用户下拉菜单 -->
              <div
                class="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-50 opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all duration-200"
              >
                <div class="py-1">
                  <NuxtLink
                    to="/profile"
                    class="block px-4 py-2 text-sm transition-colors duration-150"
                    :class="
                      isActiveRoute('/profile')
                        ? 'text-blue-600 bg-blue-50'
                        : 'text-gray-700 hover:bg-gray-100'
                    "
                  >
                    <i class="nav-icon fa-solid fa-id-card mr-2" aria-hidden="true"></i>
                    个人资料
                  </NuxtLink>
                  <NuxtLink
                    to="/profile/password"
                    class="block px-4 py-2 text-sm transition-colors duration-150"
                    :class="
                      isActiveRoute('/profile/password')
                        ? 'text-blue-600 bg-blue-50'
                        : 'text-gray-700 hover:bg-gray-100'
                    "
                  >
                    <i class="nav-icon fa-solid fa-key mr-2" aria-hidden="true"></i>
                    修改密码
                  </NuxtLink>
                  <button
                    @click="handleLogout"
                    data-testid="nav-logout"
                    class="block w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 transition-colors duration-150"
                  >
                    <i class="nav-icon fa-solid fa-right-from-bracket mr-2" aria-hidden="true"></i>
                    退出
                  </button>
                </div>
              </div>
            </div>
          </template>
          <template v-else>
            <NuxtLink
              to="/login"
              data-testid="nav-login"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-gray-700 hover:text-gray-900 hover:bg-gray-100 rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <i class="nav-icon fa-solid fa-right-to-bracket mr-2" aria-hidden="true"></i>
              登录
            </NuxtLink>
            <NuxtLink
              to="/register"
              data-testid="nav-register"
              class="inline-flex items-center px-3 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors duration-150 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              <i class="nav-icon fa-solid fa-user-plus mr-2" aria-hidden="true"></i>
              注册
            </NuxtLink>
          </template>
        </div>

        <!-- 移动端导航 -->
        <div class="md:hidden flex items-center ml-auto">
          <MobileNav :nav-items="mobileNavItems" @child-action="handleChildAction" />
        </div>
      </div>
    </div>

    <main class="main-content">
      <slot />
    </main>

    <!-- Footer -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <footer class="bg-white border-t border-gray-200 mt-auto">
        <div class="py-6">
          <div class="text-center text-sm text-gray-500">
            <div v-html="settings.copyright || '© 2024 AI竞赛平台 版权所有'" />
          </div>
        </div>
      </footer>
    </div>
  </div>
</template>

<style scoped>
.layout-wrapper {
  display: flex;
  flex-direction: column;
  min-height: 100vh;
}

.main-content {
  flex-grow: 1;
}
</style>

<script setup>
// 导入组件
import MobileNav from "~/components/layout/MobileNav.vue";

// 使用认证状态管理
const { user, isLoggedIn, logout, fetchUser } = useCustomAuth();

// 使用 useSettings 获取全局设置数据
const { settings } = useSettings();

// 路由状态
const route = useRoute();

// 更新浏览器标签页标题
useHead({
  title: settings.value?.title || "AI竞赛平台",
});

// 在组件挂载时获取用户信息
onMounted(async () => {
  if (!user.value) {
    await fetchUser();
  }
});

const handleLogout = async () => {
  await logout();
};

// 处理子项动作（如退出登录）
const handleChildAction = (child) => {
  if (child.action === "logout") {
    handleLogout();
  }
};

// 路由激活状态判断
const isActiveRoute = (path) => {
  if (!path) return false;
  // 完全匹配 /profile 路径
  if (path === '/profile') {
    return route.path === '/profile';
  }
  if (path === "/") {
    return route.path === "/";
  }
  return route.path.startsWith(path);
};

// 判断管理后台区域是否激活
const isAdminSectionActive = (item) => {
  if (!item.children) return false;
  // 检查当前路由是否匹配任何管理后台子项
  return item.children.some((child) => child.to && route.path.startsWith(child.to));
};

// 管理员导航项
const adminNavItems = computed(() => [
  { text: "管理仪表板", to: "/admin/dashboard", icon: "fa-solid fa-gauge" },
  { text: "比赛管理", to: "/admin/competitions", icon: "fa-solid fa-flag-checkered" },
  { text: "评测队列", to: "/admin/queue", icon: "fa-solid fa-tasks" },
  { text: "评测节点", to: "/admin/evaluate-nodes", icon: "fa-solid fa-server" },
  { text: "题目管理", to: "/admin/problems", icon: "fa-solid fa-book" },
  { text: "用户管理", to: "/admin/users", icon: "fa-solid fa-users" },
  { text: "队伍管理", to: "/admin/teams", icon: "fa-solid fa-people-group" },
  { text: "提交管理", to: "/admin/submissions", icon: "fa-solid fa-file-arrow-up" },
  { text: "题解管理", to: "/admin/solutions", icon: "fa-solid fa-lightbulb" },
  { text: "公告管理", to: "/admin/announcements", icon: "fa-solid fa-bullhorn" },
  { text: "系统设置", to: "/admin/settings", icon: "fa-solid fa-gear" },
]);

// 桌面端导航项
const desktopNavItems = computed(() => {
  console.log(
    "Computing desktopNavItems, isLoggedIn:",
    isLoggedIn.value,
    "user:",
    user.value
  );

  const items = [{ text: "比赛", to: "/competitions", icon: "fa-solid fa-trophy" }];

  // 登录用户的导航项
  if (isLoggedIn.value) {
    items.push(
      { text: "我的队伍", to: "/teams", icon: "fa-solid fa-users" },
      { text: "我的提交", to: "/submissions", icon: "fa-solid fa-file-arrow-up" },
      { text: "公告", to: "/announcements", icon: "fa-solid fa-bullhorn" }
    );

    // 管理员导航项
    if (user.value?.role === "admin") {
      items.push({
        text: "管理后台",
        icon: "fa-solid fa-gear",
        children: adminNavItems.value,
      });
    }
  }

  console.log("Desktop nav items:", items);
  return items;
});

// 移动端导航项（包含所有项目）
const mobileNavItems = computed(() => {
  const items = [{ text: "比赛", to: "/competitions", icon: "fa-solid fa-trophy" }];

  if (isLoggedIn.value) {
    // 登录用户的导航项
    items.push(
      { text: "我的队伍", to: "/teams", icon: "fa-solid fa-users" },
      { text: "我的提交", to: "/submissions", icon: "fa-solid fa-file-arrow-up" },
      { text: "公告", to: "/announcements", icon: "fa-solid fa-bullhorn" }
    );

    // 管理员导航项（在移动端展开显示）
    if (user.value?.role === "admin") {
      items.push({
        text: "管理后台",
        icon: "fa-solid fa-gear",
        children: adminNavItems.value,
      });
    }

    // 用户相关项 - 放到一个可展开的用户菜单中
    items.push({
      text: `用户: ${user.value?.username || "用户"}`,
      icon: "fa-solid fa-user",
      children: [
        { text: "个人资料", to: "/profile", icon: "fa-solid fa-id-card" },
        { text: "修改密码", to: "/profile/password", icon: "fa-solid fa-key" },
        { text: "退出", action: "logout", icon: "fa-solid fa-right-from-bracket" },
      ],
    });
  } else {
    // 未登录用户的导航项
    items.push(
      { text: "登录", to: "/login", icon: "fa-solid fa-right-to-bracket" },
      { text: "注册", to: "/register", icon: "fa-solid fa-user-plus" }
    );
  }

  return items;
});
</script>
