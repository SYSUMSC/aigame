<template>
  <div class="min-h-screen py-6 flex flex-col sm:py-12">
    <div class="container mx-auto">
      <div class="card">
        <div class="card-header">比赛中心</div>

				<div class="card-body">
					<div
						class="p-2 border border-gray-300 rounded flex flex-row justify-between"
						v-for="competition in competitions"
						:key="competition.id"
					>
						<div>
							<h2 class="mb-3 fs-4">{{ competition.name }}</h2>
							<span>开始时间: {{ competition.start_time }}</span>
							<span class="ml-6"
								>结束时间: {{ competition.end_time }}</span
							>
							<p>描述: {{ competition.description }}</p>
						</div>
						<div class="flex flex-row ml-6 space-x-2">
							<button
								v-if="isCaptain && !isJoin(competition.id)"
								@click="join(competition.id)"
								class="btn bg-blue-500 hover:bg-blue-600 text-white w-24 h-full mr-2"
							>
								报名
							</button>
							<button
								v-else-if="isCaptain && isJoin(competition.id)"
								@click="quit(competition.id)"
								class="btn bg-red-500 hover:bg-red-600 text-white w-24 h-full"
							>
								退出
							</button>
							<button
								@click="viewDetail(competition.id)"
								class="btn bg-gray-500 hover:bg-gray-600 text-white w-24 h-full"
							>
								查看详情
							</button>
							<button
								@click="viewLeaderboard(competition.id)"
								class="btn bg-gray-500 hover:bg-gray-600 text-white w-24 h-full"
							>
								排行榜
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { onMounted, ref } from "vue";
import axios from "axios";
import { useUserStore } from "../stores/user";
import router from "../router";
type Competition = {
  id: number;
  name: string;
  start_time: string;
  end_time: string;
  status: number;
  description: string;
};
type Participation = {
  competition_id: number;
  id: number;
  join_time: string;
  score: number | null;
  team_id: number;
  update_time: string;
  user_id: number;
};

const isCaptain = ref<boolean>(false);
const participations = ref<Participation[]>([]);
const userStore = useUserStore();
const competitions = ref<Competition[]>([]);
const teamInfo = ref<any>(null);

const isJoin = (competition_id: number) => {
  return participations.value.some((p) => p.competition_id === competition_id);
};

const join = async (competition_id: number) => {
  const res = await axios.post("/api/user/participation", {
    user_id: userStore.user?.id,
    competition_id: competition_id,
    team_id: userStore.user?.team_id,
  });
  if (res.status === 200 && res.data.code === 0) {
    alert("报名成功");
  } else {
    alert(res.data.msg);
  }
};

const getJoinInfo = async () => {
  const res = await axios.get("/api/user/participation", {
    params: {
      team_id: userStore.user?.team_id,
    },
  });
  if (res.status === 200 && res.data.code === 0) {
    participations.value = await res.data.data;
  }
};

const quit = async (competition_id: number) => {
  const res = await axios.delete("/api/user/participation", {
    params: {
      team_id: userStore.user?.team_id,
      competition_id: competition_id,
    },
  });
  if (res.status === 200 && res.data.code === 0) {
    alert("退出成功");
  } else {
    alert(res.data.msg);
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
    }
  } catch (error) {
    console.error(error);
    alert("获取队伍信息失败，请稍后再试。");
  }
};

onMounted(async () => {
  const res = await axios.get("/api/user/competition");
  competitions.value = res.data.data;
  await getJoinInfo();
  await fetchTeamInfo();
});

//查看详情按钮
const viewDetail = (competition_id: any) => {
  router.push({ name: "CompetitionDetail", params: { id: competition_id } });
};

//排行榜按钮
const viewLeaderboard = (competition_id: any) => {
	router.push({ name: 'CompetitionLeaderboard', params: { id: competition_id } });
};
</script>
