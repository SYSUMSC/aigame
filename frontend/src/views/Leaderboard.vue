<template>
  <div class="card">
    <div class="card-header">排行榜</div>
    <div class="card-body">
      <table class="table table-striped">
        <thead>
          <tr>
            <th scope="col">排名</th>
            <th scope="col">队伍名称</th>
            <th scope="col">总分</th>
          </tr>
        </thead>
        <tbody>
          <tr v-for="(team, index) in leaderboard" :key="team.team_id">
            <th scope="row">{{ index + 1 }}</th>
            <td>{{ team.name }}</td>
            <td>{{ team.total_score }}</td>
          </tr>
        </tbody>
      </table>
      <div v-if="loading">加载中...</div>
      <div v-if="noMoreData">没有更多数据了</div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue';
import { useRoute } from 'vue-router';
import axios from 'axios';

const leaderboard = ref([]);
const loading = ref(false);
const page = ref(1);
const pageSize = ref(10);
const noMoreData = ref(false);

const route = useRoute();

// const loadLeaderboard = async () => {
//   if (loading.value || noMoreData.value) return;
//   loading.value = true;

//   try {
//     const competitionId = route.params.id;

//     // const res = await axios.post('/api/competition/leaderboard', {
//     //   competition_id: competitionId,
//     //   page: page.value,
//     //   page_size: pageSize.value
//     // });
//     const res = await axios.post('/api/competition/leaderboard', 
//       {
//         competition_id: competitionId, 
//         page: page.value, 
//         page_size: pageSize.value 
//       }, 
//       {
//         headers: { 'Content-Type': 'application/json' }
//       });

//     if (res.data.code === 0) {
//       if (res.data.data.length < pageSize.value) {
//         noMoreData.value = true;
//       }
//       leaderboard.value.push(...res.data.data);
//       page.value += 1;
//     } else {
//       console.error('获取排行榜时出错:', res.data.msg);
//     }
//   } catch (error) {
//     console.error('获取排行榜时发生错误:', error);
//   } finally {
//     loading.value = false;
//   }
// };

const loadLeaderboard = async () => {
  if (loading.value || noMoreData.value) return;
  loading.value = true;

  try {
    const competitionId = route.params.id;

    const res = await axios.post('/api/user/competition/leaderboard', 
      {
        // competition_id: competitionId,
        competition_id: parseInt(competitionId, 10), // 将 competitionId 转换为整数 
        page: page.value, 
        page_size: pageSize.value 
      }, 
      {
        headers: { 'Content-Type': 'application/json' }
      });

    // 在这里添加 console.log 来打印返回的数据
    console.log('Response data:', res.data);

    if (res.data.code === 0) {
      if (res.data.data.length < pageSize.value) {
        noMoreData.value = true;
      }
      leaderboard.value.push(...res.data.data);
      page.value += 1;
    } else {
      console.error('获取排行榜时出错:', res.data.msg);
    }
  } catch (error) {
    console.error('获取排行榜时发生错误:', error);
  } finally {
    loading.value = false;
  }
};


const handleScroll = () => {
  const bottomOfWindow = window.innerHeight + window.scrollY >= document.documentElement.scrollHeight;
  if (bottomOfWindow) {
    loadLeaderboard();
  }
};

onMounted(() => {
  window.addEventListener('scroll', handleScroll);
  loadLeaderboard();
});

onBeforeUnmount(() => {
  window.removeEventListener('scroll', handleScroll);
});
</script>

<style scoped>
/* 添加样式，适配加载状态 */
.table {
  width: 100%;
  margin-bottom: 1rem;
  color: #212529;
}

.card {
  margin: 2rem 0;
}

.loading {
  text-align: center;
  padding: 1rem;
}

.no-more-data {
  text-align: center;
  padding: 1rem;
  color: gray;
}
</style>
