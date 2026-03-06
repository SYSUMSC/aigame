<template>
  <div class="max-w-2xl mx-auto py-12 px-4">
    <div v-if="pending" class="text-center py-8">
      <div
        class="inline-block animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"
      ></div>
      <p class="mt-2 text-gray-600">正在加载邀请信息...</p>
    </div>

    <div
      v-else-if="error"
      class="bg-red-50 border border-red-200 rounded-md p-6 text-center shadow-md"
    >
      <h1 class="text-2xl font-bold text-red-800">邀请无效</h1>
      <p class="mt-2 text-red-700">
        {{ error.data?.message || "此邀请链接可能已失效或不存在。" }}
      </p>
    </div>

    <div v-else-if="invitation" class="bg-white shadow-lg rounded-lg p-8 text-center">
      <h1 class="text-3xl font-bold text-gray-900 mb-4">您收到了一个邀请</h1>
      <p class="text-lg text-gray-700 mb-6">
        <template v-if="invitation.invitedBy">
          <span class="font-semibold">{{ invitation.invitedBy.username || invitation.invitedBy.realName || '队长' }}</span>
          邀请您加入队伍
          <span class="font-semibold text-blue-600">{{ invitation.team.name }}</span
          >。
        </template>
        <template v-else>
          您被邀请加入队伍
          <span class="font-semibold text-blue-600">{{ invitation.team.name }}</span
          >。
        </template>
      </p>

      <div v-if="invitation.status === 'PENDING'" class="mt-8">
        <div class="flex justify-center space-x-4">
          <button
            @click="acceptInvitation"
            :disabled="isProcessing"
            class="px-6 py-3 border border-transparent rounded-md shadow-sm text-base font-medium text-white bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500 disabled:opacity-50"
          >
            {{ isProcessing ? "处理中..." : "接受邀请" }}
          </button>
          <button
            @click="rejectInvitation"
            :disabled="isProcessing"
            class="px-6 py-3 border border-gray-300 rounded-md shadow-sm text-base font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
          >
            {{ isProcessing ? "处理中..." : "拒绝邀请" }}
          </button>
        </div>
        <p v-if="actionError" class="text-red-600 text-sm mt-4">{{ actionError }}</p>
      </div>

      <div v-else class="mt-8">
        <p
          class="text-xl font-medium"
          :class="{
            'text-green-600': invitation.status === 'ACCEPTED',
            'text-red-600': invitation.status === 'REJECTED',
          }"
        >
          邀请已{{ invitation.status === "ACCEPTED" ? "接受" : "拒绝" }}
        </p>
        <NuxtLink
          v-if="invitation.status === 'ACCEPTED'"
          :to="`/teams/${invitation.team.id}`"
          class="mt-4 inline-block text-blue-600 hover:text-blue-800"
        >
          前往队伍页面 &rarr;
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup>
definePageMeta({
  middleware: "auth",
});

const route = useRoute();
const router = useRouter();
const invitationId = route.params.id;

const isProcessing = ref(false);
const actionError = ref("");

const { data: invitation, pending, error } = await useFetch(
  `/api/invitations/${invitationId}`,
  {
    lazy: true,
    server: false, // 仅在客户端发起请求
  }
);

const acceptInvitation = async () => {
  isProcessing.value = true;
  actionError.value = "";
  try {
    const response = await $fetch(`/api/invitations/${invitationId}/accept`, {
      method: "POST",
    });
    push.success("已成功加入队伍！");
    await router.push(`/teams/${invitation.value.team.id}`);
  } catch (err) {
    actionError.value = err.data?.message || "接受邀请失败";
    isProcessing.value = false;
  }
};

const rejectInvitation = async () => {
  isProcessing.value = true;
  actionError.value = "";
  try {
    await $fetch(`/api/invitations/${invitationId}/reject`, {
      method: "POST",
    });
    push.success("已拒绝邀请。");
    // 刷新数据以展示最新邀请状态
    const { data: updatedInvitation } = await useFetch(
      `/api/invitations/${invitationId}`
    );
    invitation.value = updatedInvitation.value;
  } catch (err) {
    actionError.value = err.data?.message || "拒绝邀请失败";
  } finally {
    isProcessing.value = false;
  }
};
</script>
