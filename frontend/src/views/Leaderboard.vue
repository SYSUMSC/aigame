<!-- <!-- <template>
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
      </div>
    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import axios from 'axios';
import { useRoute } from 'vue-router';

const leaderboard = ref([]);
const route = useRoute();

onMounted(async () => {
  try {
    const competitionId = route.params.id;  // 获取当前比赛的ID
    const res = await axios.get(`/api/competition/leaderboard`, {
      params: { competition_id: competitionId }
    });
    if (res.data.code === 0) {
      leaderboard.value = res.data.data;  // 设置排行榜数据
    } else {
      console.error('获取排行榜时出错:', res.data.msg);
    }
  } catch (error) {
    console.error('获取排行榜时发生错误:', error);
  }
});
</script> -->

<!-- <template>
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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'

const leaderboard = ref([])

// 在页面挂载时发起POST请求
onMounted(async () => {
  try {
    const res = await axios.post('/api/competition/leaderboard', { competition_id: 1 }) // 假设比赛ID为1
    if (res.data.code === 0) {
      leaderboard.value = res.data.data
    } else {
      console.error('获取排行榜失败:', res.data.msg)
    }
  } catch (error) {
    console.error('Error fetching leaderboard:', error)
  }
})
</script> --> -->


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
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import axios from 'axios'
import { useRoute } from 'vue-router'  // 获取路由参数

const leaderboard = ref([])
const route = useRoute()

// 在页面挂载时发起POST请求
onMounted(async () => {
  try {
    const competitionId = route.params.id;  // 从路由中获取比赛ID
    const res = await axios.post('/api/competition/leaderboard', { competition_id: competitionId }) // POST请求
    if (res.data.code === 0) {
      leaderboard.value = res.data.data
    } else {
      console.error('获取排行榜失败:', res.data.msg)
    }
  } catch (error) {
    console.error('Error fetching leaderboard:', error)
  }
})
</script>
