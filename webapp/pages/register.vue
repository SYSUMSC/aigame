<template>
  <div class="min-h-screen flex items-center justify-center">
    <div class="max-w-md w-full bg-white p-8 rounded-lg shadow-md">
      <div class="space-y-8">
        <div>
          <h2 class="mt-6 text-center text-3xl font-extrabold text-gray-900">创建新账户</h2>
        </div>
        <form class="mt-8 space-y-6" data-testid="register-form" @submit.prevent="handleRegister">
          <div class="space-y-4">
            <div>
              <label for="username" class="sr-only">用户名</label>
              <input
                id="username"
                v-model="form.username"
                data-testid="register-username"
                name="username"
                type="text"
                required
                class="relative block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="用户名"
              />
            </div>
            <div>
              <label for="email" class="sr-only">邮箱地址</label>
              <input
                id="email"
                v-model="form.email"
                data-testid="register-email"
                name="email"
                type="email"
                autocomplete="email"
                required
                class="relative block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="邮箱地址"
              />
            </div>
            <div>
              <label for="password" class="sr-only">密码</label>
              <input
                id="password"
                v-model="form.password"
                data-testid="register-password"
                name="password"
                type="password"
                autocomplete="new-password"
                required
                class="relative block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="密码 (至少6位)"
              />
            </div>
            <div>
              <label for="realName" class="sr-only">真实姓名</label>
              <input
                id="realName"
                v-model="form.realName"
                data-testid="register-real-name"
                name="realName"
                type="text"
                class="relative block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="真实姓名"
              />
            </div>
            <div>
              <label for="studentId" class="sr-only">学号</label>
              <input
                id="studentId"
                v-model="form.studentId"
                data-testid="register-student-id"
                name="studentId"
                type="text"
                class="relative block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="学号"
              />
            </div>
            <div>
              <label for="phoneNumber" class="sr-only">手机号</label>
              <input
                id="phoneNumber"
                v-model="form.phoneNumber"
                data-testid="register-phone-number"
                name="phoneNumber"
                type="tel"
                class="relative block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                placeholder="手机号"
              />
            </div>
            <div>
              <label for="education" class="sr-only">学历</label>
              <select
                id="education"
                v-model="form.education"
                data-testid="register-education"
                name="education"
                class="relative block w-full appearance-none rounded-md border border-gray-300 px-3 py-2 text-gray-900 placeholder-gray-500 focus:z-10 focus:border-blue-500 focus:outline-none focus:ring-blue-500 sm:text-sm"
                :class="{ 'text-gray-500': !form.education }"
              >
                <option disabled value="">请选择学历</option>
                <option value="BACHELOR">本科</option>
                <option value="MASTER">硕士</option>
                <option value="DOCTORATE">博士</option>
              </select>
            </div>
          </div>

        <div v-if="error" class="text-red-600 text-sm text-center" data-testid="register-error">
          {{ error }}
        </div>

        <div>
          <button
            type="submit"
            :disabled="isLoading"
            data-testid="register-submit"
            class="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {{ isLoading ? "注册中..." : "注册" }}
          </button>
        </div>

        <div class="text-center">
          <NuxtLink to="/login" data-testid="register-to-login" class="text-blue-600 hover:text-blue-500">
            已有账户？登录
          </NuxtLink>
        </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
// 使用认证状态管理
const { register, isLoading } = useCustomAuth();

const form = reactive({
  username: "",
  email: "",
  password: "",
  realName: "",
  studentId: "",
  phoneNumber: "",
  education: "",
});

const error = ref("");

const handleRegister = async () => {
  if (isLoading.value) return;

  error.value = "";

  if (form.password.length < 6) {
    error.value = "密码至少需要6位";
    return;
  }

  // 验证手机号格式（如果提供了手机号）
  if (form.phoneNumber && !/^1[3-9]\d{9}$/.test(form.phoneNumber)) {
    error.value = "请输入正确的手机号格式";
    return;
  }

  // 验证学号长度（如果提供了学号）
  if (form.studentId && (form.studentId.length < 6 || form.studentId.length > 20)) {
    error.value = "学号长度应在6-20个字符之间";
    return;
  }

  // 验证真实姓名长度（如果提供了真实姓名）
  if (form.realName && (form.realName.length < 2 || form.realName.length > 50)) {
    error.value = "真实姓名长度应在2-50个字符之间";
    return;
  }

  try {
    await register(
      form.username,
      form.email,
      form.password,
      form.phoneNumber,
      form.studentId,
      form.realName,
      form.education
    );
    // 注册成功会自动跳转到首页
  } catch (err) {
    error.value = err.statusMessage || err.message || "注册失败";
  }
};
</script>
