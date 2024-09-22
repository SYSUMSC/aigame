<template>
    <div class="min-h-screen py-6 flex flex-col sm:py-12">
        <div class="container mx-auto">
            <div class="card shadow-lg rounded-lg border-0">
                <div class="card-body p-6">
                    <h1 class="text-2xl font-bold mb-6 text-center text-primary">比赛中心</h1>

                    <div class="mt-5 p-2 border border-gray-300 rounded flex flex-row justify-between"
                        v-for="competition in competitions" :key="competition.id">
                        <div>
                            <h2 class="mb-3 fs-4">{{ competition.name }}</h2>
                            <span>开始时间: {{ competition.start_time }}</span>
                            <span class="ml-6">结束时间: {{ competition.end_time }}</span>
                            <p>描述: {{ competition.description }}</p>
                        </div>
                        <div v-if="isCaptain">
                            <button v-if="!isJoin(competition.id)" @click="join(competition.id)"
                                class="btn btn-primary ml-6">报名</button>
                            <button v-else @click="quit(competition.id)" class="btn btn-danger ml-6">退出</button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>
</template>
<script setup lang="ts">
import { onMounted, ref } from 'vue';
import axios from 'axios';
import { useUserStore } from '../stores/user';
type Competition = {
    id: number;
    name: string;
    start_time: string;
    end_time: string;
    status: number;
    description: string;
}
const isCaptain = ref<boolean>(false);
const hasJoinedCompetitions = ref<Competition[]>([]);
const userStore = useUserStore();
const competitions = ref<Competition[]>([]);
const teamInfo = ref<any>(null);
const isJoin = (id: number) => {
    hasJoinedCompetitions.value.forEach((competition) => {
        if (competition.id === id) {
            return true;
        }
    })
    return false;
};
// const fetchTeamInfo = async () => {
//     try {
//         const res = await axios.get("/api/user/team_info");
//         if (res.status === 200 && res.data.code === 0) {
//             teamInfo.value = res.data.data;
//             if (userStore.user) {
//                 userStore.user.team_id = teamInfo.value.id;
//             }
//             isCaptain.value = teamInfo.value.captain_id === userStore.user?.id;
//         } else {
//             if (res.data.msg === "用户不在任何队伍中" && userStore.user) {
//                 // 只要让这里不再显示任何信息，由于此时没有报错，用户可以再次使用当前页面重新加入队伍
//                 userStore.user.team_id = null
//             } else {
//                 alert(res.data.msg);
//                 // 暂时试试返回用户界面看是否还有其它问题产生
//                 router.push("/user")
//             }
//         }
//     } catch (error) {
//         console.error(error);
//         alert("获取队伍信息失败，请稍后再试。");
//     }
// };
const join = async (competition_id: number) => {
    const res = await axios.post('/user/participation', {
        user_id: userStore.user?.id,
        competition_id: competition_id,
        team_id: userStore.user?.team_id
    });
    if (res.status === 200 && res.data.code === 0) {
        alert("报名成功");
    } else {
        alert(res.data.msg);
    }
}

const getJoinInfo = async () => {
    const res = await axios.get('/user/participation', {
        params: {
            user_id: userStore.user?.id
        }
    });
    if (res.status === 200 && res.data.code === 0) {
        hasJoinedCompetitions.value = res.data.data;
    }
}

const quit = async (competition_id: number) => {
    const res = await axios.post('/user/participation/quit', {
        user_id: userStore.user?.id,
        competition_id: competition_id,
        team_id: userStore.user?.team_id
    });
    if (res.status === 200 && res.data.code === 0) {
        alert("退出成功");
    } else {
        alert(res.data.msg);
    }
}

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
    const res = await axios.get('/user/competition');
    await getJoinInfo();
    await fetchTeamInfo();
    console.log(res)
    // competitions.value = res.data;
    competitions.value = [
        {
            id: 1,
            name: '比赛1',
            start_time: '2021-10-01 00:00:00',
            end_time: '2021-10-31 23:59:59',
            status: 0,
            description: "比赛1描述"
        },
        {
            id: 2,
            name: '比赛2',
            start_time: '2021-11-01 00:00:00',
            end_time: '2021-11-30 23:59:59',
            status: 1,
            description: "比赛2描述"
        },
        {
            id: 3,
            name: '比赛3',
            start_time: '2021-12-01 00:00:00',
            end_time: '2021-12-31 23:59:59',
            status: 2,
            description: "比赛3描述"
        },
        {
            id: 4,
            name: '比赛4',
            start_time: '2022-01-01 00:00:00',
            end_time: '2022-01-31 23:59:59',
            status: 3,
            description: "比赛4描述"
        },
        {
            id: 5,
            name: '比赛5',
            start_time: '2022-02-01 00:00:00',
            end_time: '2022-02-28 23:59:59',
            status: 4,
            description: "比赛5描述"
        }
    ]
});
</script>
