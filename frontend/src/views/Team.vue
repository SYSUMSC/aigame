<template>
  <div class="min-h-screen py-6 flex flex-col sm:py-12">
    <div class="container mx-auto">
      <div class="card shadow-lg">
        <div class="card-body p-6">
          <h1 class="text-2xl font-bold mb-6 text-center">队伍管理</h1>

          <div v-if="!userStore.user.team_id">
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
          </div>

          <div v-else>
            <!-- 用户已加入队伍，显示队伍信息 -->
            <h2 class="text-xl font-bold mb-4">当前队伍信息</h2>
            <p><strong>队伍名称:</strong> {{ teamInfo.name }}</p>
            <p><strong>邀请码:</strong> {{ teamInfo.invite_code }}</p>
            <p><strong>队员:</strong></p>
            <ul>
              <li v-for="member in teamInfo.members" :key="member.id">
                {{ member.name }} ({{ member.username }})
                <button
                  v-if="isCaptain && member.id !== userStore.user.id"
                  @click="removeMember(member.id)"
                  class="ml-2 btn btn-danger btn-sm"
                >
                  移除
                </button>
              </li>
            </ul>
            <button
              v-if="isCaptain"
              @click="disbandTeam"
              class="btn btn-danger mt-4"
            >
              解散队伍
            </button>
            <button v-else @click="leaveTeam" class="btn btn-warning mt-4">
              退出队伍
            </button>
          </div>
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
    <div v-if="showCreateTeamModal" class="modal-backdrop fade show"></div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
import { useUserStore } from "../stores/user";
import { useRouter } from "vue-router";

const userStore = useUserStore();
const router = useRouter();
const inviteCode = ref("");
const newTeamName = ref("");
const teamInfo = ref<any>(null);
const isCaptain = ref(false);
const showCreateTeamModal = ref(false);

const fetchTeamInfo = async () => {
  try {
    const res = await axios.get("/api/user/team_info");
    if (res.status === 200 && res.data.code === 0) {
      teamInfo.value = res.data.data;
      isCaptain.value = teamInfo.value.captain_id === userStore.user?.id;
    } else {
      alert(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    alert("获取队伍信息失败，请稍后再试。");
  }
};

const joinTeam = async () => {
  try {
    const res = await axios.post("/api/user/join_team", {
      invite_code: inviteCode.value,
    });
    if (res.status === 200 && res.data.code === 0) {
      alert("成功加入队伍");
      await fetchTeamInfo();
    } else {
      alert(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    alert("加入队伍失败，请稍后再试。");
  }
};

const leaveTeam = async () => {
  try {
    const res = await axios.post("/api/user/leave_team");
    if (res.status === 200 && res.data.code === 0) {
      alert("成功退出队伍");
      userStore.user!.team_id = null;
      router.push("/");
    } else {
      alert(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    alert("退出队伍失败，请稍后再试。");
  }
};

const disbandTeam = async () => {
  try {
    const res = await axios.post("/api/user/disband_team");
    if (res.status === 200 && res.data.code === 0) {
      alert("成功解散队伍");
      userStore.user!.team_id = null;
      router.push("/");
    } else {
      alert(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    alert("解散队伍失败，请稍后再试。");
  }
};

const removeMember = async (memberId: number) => {
  try {
    const res = await axios.post("/api/user/remove_member", {
      member_id: memberId,
    });
    if (res.status === 200 && res.data.code === 0) {
      alert("成功移除队员");
      await fetchTeamInfo();
    } else {
      alert(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    alert("移除队员失败，请稍后再试。");
  }
};

const createTeam = async () => {
  try {
    const res = await axios.post("/api/user/create_team", {
      name: newTeamName.value,
    });
    if (res.status === 200 && res.data.code === 0) {
      alert("成功创建队伍");
      showCreateTeamModal.value = false;
      await fetchTeamInfo();
    } else {
      alert(res.data.msg);
    }
  } catch (error) {
    console.error(error);
    alert("创建队伍失败，请稍后再试。");
  }
};

fetchTeamInfo();

</script>

<style scoped></style>
