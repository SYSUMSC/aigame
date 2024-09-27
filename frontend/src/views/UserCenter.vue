<template>
  <div class="min-h-screen py-6 flex flex-col sm:py-12">
    <div class="container mx-auto">
      <div class="card">
        <div class="card-header">用户中心</div>
        <div class="card-body">
          <template v-if="userStore.user">
            <div class="mb-4">
              <label class="block text-muted">用户名</label>
              <p class="text-dark font-weight-bold">
                {{ userStore.user.username }}
              </p>
            </div>
            <div class="mb-4">
              <label class="block text-muted">电子邮件</label>
              <p class="text-dark font-weight-bold">
                {{ userStore.user.email }}
              </p>
            </div>
            <div class="mb-4">
              <label class="block text-muted">姓名</label>
              <p class="text-dark font-weight-bold">
                {{ userStore.user.name }}
              </p>
            </div>
            <div class="mb-4">
              <label class="block text-muted">学号</label>
              <p class="text-dark font-weight-bold">
                {{ userStore.user.student_id }}
              </p>
            </div>
          </template>
          <template v-else>
            <div class="alert alert-warning text-center" role="alert">
              请登录以查看用户信息。
            </div>
          </template>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUserStore } from "../stores/user";

const userStore = useUserStore();
</script>

<style scoped></style>
