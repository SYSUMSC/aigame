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
  
  const leaderboard = ref([])
  
  onMounted(async () => {
    try {
      const res = await axios.get('/api/competition/leaderboard')
      leaderboard.value = res.data
    } catch (error) {
      console.error('Error fetching leaderboard:', error)
    }
  })
  </script>  