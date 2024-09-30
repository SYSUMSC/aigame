<template>
  <div class="min-h-screen py-6 flex flex-col sm:py-12">
    <div class="container mx-auto">
      <div class="card">
        <div class="card-header">队伍管理</div>

        <div class="card-body">
          <template v-if="!userStore.user?.team_id">
            <!-- 用户未加入任何队伍，显示加入或创建队伍的选项 -->
            <button
              @click="showCreateTeamModal = true"
              class="btn btn-success w-100 mb-4"
            >
              创建队伍
            </button>
            <form @submit.prevent="joinTeam">
              <div class="form-group mb-3">
                <label for="invite_code">邀请码</label>
                <input
                  type="text"
                  id="invite_code"
                  v-model="inviteCode"
                  class="form-control"
                  required
                />
              </div>
              <button type="submit" class="btn btn-primary w-100">
                加入队伍
              </button>
            </form>
          </template>

          <template v-else-if="teamInfo">
            <!-- 用户已加入队伍，显示队伍信息 -->
            <h2 class="text-xl font-bold mb-4">当前队伍信息</h2>
            <p><strong>队伍名称:</strong> {{ teamInfo.name }}</p>
            <p>
              <strong
                id="inviteCode"
                data-clipboard-text="{{ teamInfo.invite_code }}"
                >邀请码:</strong
              >
              {{ teamInfo.invite_code }}
              <button
                @click="oldCopyToClipboard(teamInfo.invite_code)"
                class="border-2 border-white bg-yellow-50 rounded-md btn ml-2"
              >
                复制
              </button>
            </p>
            <p><strong>队员:</strong></p>
            <ul>
              <li v-for="member in teamInfo.members" :key="member.id">
                {{ member.name }} ({{ member.username }})
                <button
                  v-if="isCaptain && member.id !== userStore.user.id"
                  @click="removeMember(member.id)"
                  class="border-2 border-white rounded-md mt-1 btn btn-danger btn-sm"
                >
                  移除
                </button>
              </li>
            </ul>
            <button
              v-if="isCaptain"
              @click="generateInviteCode"
              class="border-2 border-white rounded-md btn btn-info mt-4"
            >
              生成邀请码
            </button>
            <button
              v-if="isCaptain"
              @click="showTransferModal = true"
              class="border-2 border-white rounded-md btn btn-danger mt-4"
            >
              转让队伍
            </button>
            <button
              v-if="isCaptain"
              @click="disbandTeam"
              class="border-2 border-white rounded-md btn btn-danger mt-4"
            >
              解散队伍
            </button>
            <button v-else @click="leaveTeam" class="btn btn-warning mt-4">
              退出队伍
            </button>
          </template>
        </div>
      </div>
    </div>

    <!-- 创建队伍模态框 -->
    <div
      v-if="showCreateTeamModal"
      class="modal fade show"
      style="display: block"
    >
      <div class="modal-dialog">
        <div class="modal-content">
          <div class="modal-header">
            <h5 class="modal-title">创建队伍</h5>
            <button
              type="button"
              class="btn-close"
              @click="showCreateTeamModal = false"
            ></button>
          </div>
          <div class="modal-body">
            <div class="form-group mb-3">
              <label for="team_name">队伍名称</label>
              <input
                type="text"
                id="team_name"
                v-model="newTeamName"
                class="form-control"
                required
              />
            </div>
          </div>
          <div class="modal-footer">
            <button
              type="button"
              class="btn btn-secondary"
              @click="showCreateTeamModal = false"
            >
              取消
            </button>
            <button type="button" class="btn btn-primary" @click="createTeam">
              创建
            </button>
          </div>
        </div>
      </div>
    </div>
    <!-- 队伍转让模态框 -->
    <div
      v-if="showTransferModal"
      @close="showTransferModal = false"
      class="fixed top-0 left-0 w-screen h-screen flex items-center justify-center bg-gray-500 bg-opacity-50 z-50"
    >
      <div class="bg-white rounded-lg shadow-xl p-6 w-full max-w-sm">
        <div class="flex justify-between items-center">
          <h3 class="text-xl font-bold">选择新队长</h3>
          <button class="text-gray-700 mt-2" @click="showTransferModal = false">
            &times;
          </button>
        </div>
        <div class="overflow-y-auto h-60">
          <ol>
            <li v-for="member in teamInfo.members" :key="member.userId">
              <input
                v-if="isCaptain && member.id !== userStore.user?.id"
                type="radio"
                :id="member.userId"
                v-model="selectedCaptainId"
                :value="member.id"
                class="mr-2"
              />
              <label
                :for="member.userId"
                v-if="isCaptain && member.id !== userStore.user?.id"
                class="font-medium text-gray-700"
                >{{ member.name }}</label
              >
            </li>
          </ol>
        </div>
        <div class="flex justify-end mt-4">
          <button
            :disabled="!selectedCaptainId"
            class="border-2 border-white rounded-md btn btn-primary ml-2"
            @click="transferCaptaincy"
          >
            确认转让
          </button>
          <button
            class="border-2 border-white rounded-md btn btn-secondary"
            @click="showTransferModal = false"
          >
            取消
          </button>
        </div>
      </div>
    </div>
    <div v-if="showCreateTeamModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
import { useUserStore } from "../stores/user";
import { useRouter } from "vue-router";
import ClipboardJS from "clipboard";
import { layer } from "vue3-layer";


const userStore = useUserStore();
const router = useRouter();
const inviteCode = ref("");
const newTeamName = ref("");
const teamInfo = ref<any>(null);
const isCaptain = ref(false);
const showCreateTeamModal = ref(false);
const showTransferModal = ref(false);
const selectedCaptainId = ref("");
// const copyInviteCode = ref(false)

// const sendData = () => {
//   emit('commit',
//   // userStore.user?.id === teamInfo.value.captain_id
//     isCaptain.value
//   )
//   console.log("send value is "+isCaptain.value)
// }

const copyToClipboard = async (text: string) => {
  // 使用原生api
  try {
    if (!text) {
      layer.msg("邀请码为空，无法复制。");
    } else {
      await navigator.clipboard.writeText(text);
      layer.msg("邀请码已复制到剪贴板！");
    }
  } catch (err) {
    console.error("复制失败:", err);
    layer.msg("复制邀请码失败，请手动复制。");
  }
};
/**@deprecated */
const oldCopyToClipboard = async (text: string) => {
  try {
    if (!text) {
      layer.msg("邀请码为空，无法复制。");
    } else {
      await new ClipboardJS(".btn", {
        text: () => text,
      });
      layer.msg("邀请码已复制到剪贴板！");
    }
  } catch (err) {
    console.error("复制失败:", err);
    layer.msg("复制邀请码失败，请手动复制。");
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
      console.log(isCaptain.value);
    } else {
      if (res.data.msg === "用户不在任何队伍中" && userStore.user) {
        // 只要让这里不再显示任何信息，由于此时没有报错，用户可以再次使用当前页面重新加入队伍
        userStore.user.team_id = null;
      } else {
        layer.msg(res.data.msg);
        // 暂时试试返回用户界面看是否还有其它问题产生
        router.push("/user");
      }
    }
  } catch (error) {
    console.error(error);
    layer.msg("获取队伍信息失败，请稍后再试。");
  }
};

const joinTeam = async () => {
  try {
    const res = await axios.post("/api/user/join_team", {
      invite_code: inviteCode.value,
    });
    if (res.status === 200 && res.data.code === 0) {
      layer.msg("成功加入队伍");
      await fetchTeamInfo();
    } else {
      layer.msg(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    layer.msg("加入队伍失败，请稍后重试。");
  }
};

const leaveTeam = async () => {
  try {
    const res = await axios.post("/api/user/leave_team");
    if (res.status === 200 && res.data.code === 0) {
      if (userStore.user) {
        userStore.user.team_id = null;
      }
      layer.msg("成功退出队伍");
    } else {
      layer.msg(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    layer.msg("退出队伍失败，请稍后再试。");
  }
};

const disbandTeam = async () => {
  try {
    const res = await axios.post("/api/user/disband_team");
    if (res.status === 200 && res.data.code === 0) {
      if (userStore.user) {
        userStore.user.team_id = null;
      }
      layer.msg("成功解散队伍");
    } else {
      layer.msg(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    layer.msg("解散队伍失败，请稍后再试。");
  }
};

const removeMember = async (memberId: number) => {
  try {
    const res = await axios.post("/api/user/remove_member", {
      member_id: memberId,
    });
    if (res.status === 200 && res.data.code === 0) {
      layer.msg("成功移除队员");
      await fetchTeamInfo();
    } else {
      layer.msg(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    layer.msg("移除队员失败，请稍后再试。");
  }
};

const createTeam = async () => {
  try {
    const res = await axios.post("/api/user/create_team", {
      name: newTeamName.value,
    });
    if (res.status === 200 && res.data.code === 0) {
      layer.msg("成功创建队伍");
      showCreateTeamModal.value = false;
      await fetchTeamInfo();
    } else {
      layer.msg(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    layer.msg("创建队伍失败，请稍后再试。");
  }
};

// 新增的生成邀请码功能
const generateInviteCode = async () => {
  try {
    const res = await axios.post("/api/user/create_invite_code");
    if (res.status === 200 && res.data.code === 0) {
      teamInfo.value.invite_code = res.data.data.invite_code; // 更新队伍信息中的邀请码
      layer.msg("邀请码生成成功: " + res.data.data.invite_code);
    } else {
      layer.msg(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    layer.msg("生成邀请码失败，请稍后再试。");
  }
};

// 新增队伍转让功能
const transferCaptaincy = async () => {
  try {
    const res = await axios.post("api/user/transfer_captain", {
      new_captain_id: selectedCaptainId.value,
    });
    if (res.status === 200 && res.data.code === 0) {
      layer.msg("转让队伍成功");
      await fetchTeamInfo();
      router.replace("/user/team");
    } else {
      layer.msg(res.data.msg);
      router.replace("/user/team");
    }
    showTransferModal.value = false;
  } catch (error) {
    console.error(error);
    layer.msg("转让队伍失败，请稍后重试。");
  }
};

onMounted(async () => {
  await fetchTeamInfo();
});
</script>

<style scoped></style>
