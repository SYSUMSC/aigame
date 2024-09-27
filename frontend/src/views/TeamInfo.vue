<template>
  <div>
    <div>
      <div class="rightComponent">
        <div>
          <!-- 用户已加入队伍，显示队伍信息 -->
          <h2 class="text-xl font-bold mb-4">当前队伍信息</h2>
          <p><strong>队伍名称:</strong> {{ teamInfo?.name }}</p>
          <p><strong id="inviteCode" data-clipboard-text="{{ teamInfo.invite_code }}">邀请码:</strong> {{
            teamInfo?.invite_code }}
            <button @click="oldCopyToClipboard(teamInfo?.invite_code)"
              class="border-2 border-white bg-yellow-50 rounded-md btn ml-2">复制</button>
          </p>
          <p><strong>队员:</strong></p>
          <ul>
            <li v-for="member in teamInfo?.members" :key="member.id">{{ member.username }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import { useUserStore } from '../stores/user';
import { useRouter } from 'vue-router';
import axios from 'axios';
import ClipboardJS from 'clipboard'

const teamInfo = ref<any>(null)
const isCaptain = ref<boolean>(false)
const userStore = useUserStore()
const router = useRouter()

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
        userStore.user.team_id = null
      } else {
        alert(res.data.msg);
        // 暂时试试返回用户界面看是否还有其它问题产生
        router.push("/user")
      }
    }
  } catch (error) {
    console.error(error);
    alert("获取队伍信息失败，请稍后再试。");
  }
};

const oldCopyToClipboard = async(text: string) => {
  try {
      if (!text) { 
        alert('邀请码为空，无法复制。')
      } else {
        await new ClipboardJS('.btn', {
        text: () => text
      });
      alert('邀请码已复制到剪贴板！')
    }
  } catch (err) {
    console.error('复制失败:', err)
    alert('复制邀请码失败，请手动复制。')
  }
}


onMounted( async () => {
  await fetchTeamInfo()
  console.log(isCaptain.value)
})

</script>