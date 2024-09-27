<template>
  <main class="min-h-screen py-6 flex flex-col justify-center items-center">
    <div class="container mx-auto">
      <div class="card">
        <header>
          <h1 class="text-2xl font-bold mb-6 text-center text-primary">
            比赛详情
          </h1>
        </header>
        <main>
          <h1 class="mb-3 fs-4">{{ competition?.name }}</h1>
          <p>开始时间: {{ competition?.start_time }}</p>
          <p>结束时间: {{ competition?.end_time }}</p>
          <p>描述: {{ competition?.description }}</p>
          <br /><br />
          <h3>赛题列表:</h3>

          <select v-model="filters.difficulty" class="mb-2">
            <option value="all">全部难度</option>
            <option value="1">旅行</option>
            <option value="2">经典</option>
            <option value="3">专家</option>
            <option value="4">大师</option>
          </select>
          <select v-model="filters.problem_type_id">
            <option value="all">全部类型</option>
            <option
              v-for="type in problemTypes"
              :key="type.id"
              :value="type.id"
            >
              {{ type.name }}
            </option>
          </select>
          <button
            @click="fetchProblems(Number(route.params.id))"
            class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700"
          >
            筛选
          </button>
          <ul>
            <li v-for="problem in problems" :key="problem.id">
              {{ problem.name }}--难度:
              {{
                difficultyLevels[problem.difficulty as 1 | 2 | 3 | 4] ||
                "未知难度"
              }}--类型：{{
                problemTypes[problem.problem_type_id - 1]?.name || "未知类型"
              }}
            </li>
          </ul>
        </main>
        <footer class="mb-4"></footer>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref, watchEffect } from "vue";
import axios from "axios";
import { useRoute } from "vue-router";

type Competition = {
  id: number;
  name: string;
  start_time: string;
  end_time: string;
  status: number;
  description: string;
  problems: Array<{
    id: number;
    name: string;
    difficulty: number;
    problem_type_id: number;
  }>;
};

type ProblemType = {
  id: number;
  name: string;
  description?: string;
};

type ProblemTypes = Array<ProblemType>;

const difficultyLevels = {
  1: "旅行",
  2: "经典",
  3: "专家",
  4: "大师",
};

const route = useRoute();
const competition = ref<Competition | null>(null);
const problems = ref<Competition["problems"]>([]);
const filters = ref({ difficulty: "all", problem_type_id: "all" });
const problemTypes = ref<ProblemTypes>([]);

const fetchCompetitionDetail = async (competitionId: number) => {
  try {
    const res = await axios.get(`/api/user/competition/${competitionId}`);
    if (res.status === 200 && res.data.code === 0) {
      competition.value = res.data.data;
    } else {
      console.error("Failed to fetch competition details:", res.data.msg);
    }
  } catch (error) {
    console.error("An error occurred:", error);
  }
};

const fetchProblems = async (competitionId: number) => {
  try {
    let params: { difficulty: string; problem_type_id: string } = {
      difficulty: "",
      problem_type_id: "",
    };
    if (filters.value.difficulty !== "all") {
      params.difficulty = filters.value.difficulty;
    }
    if (filters.value.problem_type_id !== "all") {
      params.problem_type_id = filters.value.problem_type_id;
    }
    const res = await axios.get(
      `/api/user/competition/${competitionId}/problems`,
      { params }
    );
    if (res.status === 200 && res.data.code === 0) {
      problems.value = res.data.data;
    } else {
      console.error("Failed to fetch problems:", res.data.msg);
    }
  } catch (error) {
    console.error("An error occurred:", error);
  }
};

const fetchProblemTypes = async () => {
  try {
    const res = await axios.get("/api/user/problem_types");
    if (res.status === 200 && res.data.code === 0) {
      problemTypes.value = res.data.data;
    } else {
      console.error("Failed to fetch problem types:", res.data.msg);
    }
  } catch (error) {
    console.error("An error occurred:", error);
  }
};

onMounted(() => {
  const competitionId = Number(route.params.id);
  fetchCompetitionDetail(competitionId);
  fetchProblems(competitionId);
  fetchProblemTypes();
});

watchEffect(() => {
  const competitionId = Number(route.params.id);
  fetchCompetitionDetail(competitionId);
  fetchProblems(competitionId);
});
</script>
