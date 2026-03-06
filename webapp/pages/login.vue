<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
      <div class="space-y-8">
        <div>
          <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">
            登录到您的账户
          </h2>
        </div>
        <form class="mt-8 space-y-6" data-testid="login-form" @submit.prevent="handleLogin">
          <div class="space-y-4">
            <div>
              <label for="identifier" class="sr-only">邮箱地址或用户名</label>
              <input
                id="identifier"
                v-model="form.identifier"
                data-testid="login-identifier"
                name="identifier"
                type="text"
                autocomplete="username"
                required
                class="relative block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="邮箱地址或用户名"
              />
            </div>
            <div>
              <label for="password" class="sr-only">密码</label>
              <input
                id="password"
                v-model="form.password"
                data-testid="login-password"
                name="password"
                type="password"
                autocomplete="current-password"
                required
                class="relative block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="密码"
              />
            </div>
          </div>

        <div v-if="error" class="text-red-600 text-sm text-center" data-testid="login-error">
          {{ error }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            data-testid="login-submit"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {{ isLoading ? "登录中..." : "登录" }}
          </button>
        </div>

        <div class="text-center">
          <NuxtLink to="/register" data-testid="login-to-register" class="text-blue-600 hover:text-blue-500">
            还没有账户？注册
          </NuxtLink>
        </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
// 使用认证状态管理
const { login, isLoading, isLoggedIn } = useCustomAuth();
const route = useRoute();
const router = useRouter();

const form = reactive({
  identifier: "",
  password: "",
});

const error = ref("");

const redirectTo = computed(() => {
  if (route.query.redirect && typeof route.query.redirect === "string") {
    // Basic validation to prevent open redirects
    if (route.query.redirect.startsWith("/")) {
      return route.query.redirect;
    }
  }
  return "/";
});

// 如果用户已经登录，则重定向
watch(
  isLoggedIn,
  (loggedIn) => {
    if (loggedIn) {
      router.push(redirectTo.value);
    }
  },
  { immediate: true }
);

const handleLogin = async () => {
  if (isLoading.value) return;

  error.value = "";

  try {
    await login(form.identifier, form.password);
    // 登录成功后，isLoggedIn 会变为 true，watch 会触发重定向
  } catch (err) {
    error.value = err.statusMessage || err.message || "登录失败";
  }
};
</script>
