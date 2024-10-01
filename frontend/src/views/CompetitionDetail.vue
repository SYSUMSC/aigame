<template>
  <main class="min-h-screen py-6 flex flex-col justify-center items-center">
    <div class="container mx-auto">
      <div class="card">
        <div class="card-header">比赛详情</div>
        <div class="card-body">
          <h1 class="mb-3 fs-4">{{ competition?.name }}</h1>
          <p>开始时间: {{ competition?.start_time }}</p>
          <p>结束时间: {{ competition?.end_time }}</p>
          <p>描述: {{ competition?.description }}</p>
          <br /><br />
          <h3>赛题列表:</h3>

          <select v-model="filters.difficulty" class="mb-2">
            <option value="null">全部难度</option>
            <option value="1">旅行</option>
            <option value="2">经典</option>
            <option value="3">专家</option>
            <option value="4">大师</option>
          </select>
          <select v-model="filters.problem_type_id">
            <option value="null">全部类型</option>
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
              {{ problem.name }} -- 难度: {{ difficultyLevels[problem.difficulty as 1 | 2 | 3 | 4] || "未知难度" }} -- 类型：{{ problemTypes[problem.problem_type_id - 1]?.name || "未知类型" }}
              <button @click="viewProblemDetail(problem.id)" class="bg-green-500 text-white font-bold py-1 px-3 ml-4 rounded hover:bg-green-700">
                查看详情
              </button>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { onMounted, ref, watchEffect } from "vue";
import axios from "axios";
import { useRoute, useRouter } from "vue-router";

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
const filters = ref({ difficulty: "null", problem_type_id: "null" });
const problemTypes = ref<ProblemTypes>([]);

// 获取比赛详情
const fetchCompetitionDetail = async (competitionId: number) => {
  try {
    const config = {
      headers: { 
        'Content-Type': 'application/json' 
      }
    };
    const res = await axios.post(
      `/api/user/competition/${competitionId}`,
      {},
      config
    );
    if (res.status === 200 && res.data.code === 0) {
      competition.value = res.data.data;
    } else {
      console.error("Failed to fetch competition details:", res.data.msg);
    }
  } catch (error) {
    console.error("An error occurred:", error);
  }
};

// 获取赛题列表
const fetchProblems = async (competitionId: number) => {
  try {
    const config = {
      headers: { 
        'Content-Type': 'application/json' 
      }
    };
    
    // 构建请求体，仅包含非 "null" 值的字段
    const filtersToSend = {};
    if (filters.value.difficulty !== "null") {
      filtersToSend.difficulty = Number(filters.value.difficulty); // 确保转换为数字
    }
    if (filters.value.problem_type_id !== "null") {
      filtersToSend.problem_type_id = Number(filters.value.problem_type_id); // 确保转换为数字
    }

    const res = await axios.post(
      `/api/user/competition/${competitionId}/problems`,
      filtersToSend,
      config
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

// 获取问题类型列表
const fetchProblemTypes = async () => {
  try {
    const config = {
      headers: { 
        'Content-Type': 'application/json' 
      }
    };
    const res = await axios.post(
      "/api/user/problem_types",
      {},
      config
    );
    if (res.status === 200 && res.data.code === 0) {
      problemTypes.value = res.data.data;
    } else {
      console.error("Failed to fetch problem types:", res.data.msg);
    }
  } catch (error) {
    console.error("An error occurred:", error);
  }
};

// 创建路由实例
const router = useRouter();

// 定义跳转到赛题详情页面的函数
const viewProblemDetail = (problemId: number) => {
  router.push({ name: 'ProblemDetail', params: { id: problemId } });
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
