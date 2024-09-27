<template>
  <div class="container">
    <div class="row">
      <div class="col-md-6">
        <LeftComponent />
      </div>
      <div class="col-md-6">
        <RightComponent />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref } from 'vue';
import LeftComponent from './UserCenter.vue';
import RightComponent from './Team.vue';
import axios from 'axios';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';

const isCaptain = ref(true);
const userStore = useUserStore();
const teamInfo = ref<any>(null);
const router = useRouter();

const handleData = (data: boolean) => {
  isCaptain.value = data;
  console.log('rec is ' + data);
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
};

onMounted(async () => {
  await fetchTeamInfo()
});
</script>