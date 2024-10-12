<template>
  <div class="card">
    <div class="card-header">比赛详情</div>
    <div class="card-body">
      <h1 class="mb-3 text-2xl font-bold">{{ competition?.name }}</h1>
      <p class="text-gray-600">开始时间: {{ competition?.start_time }}</p>
      <p class="text-gray-600">结束时间: {{ competition?.end_time }}</p>
      <p class="text-gray-700">{{ competition?.description }}</p>
      <br /><br />
      <h3 class="text-xl font-semibold mb-4">赛题列表:</h3>

      <div class="flex space-x-4 mb-4">
        <select v-model="filters.difficulty" class="p-2 border rounded">
          <option value="null">全部难度</option>
          <option value="1">旅行</option>
          <option value="2">经典</option>
          <option value="3">专家</option>
          <option value="4">大师</option>
        </select>
        <select v-model="filters.problem_type_id" class="p-2 border rounded">
          <option value="null">全部类型</option>
          <option v-for="type in problemTypes" :key="type.id" :value="type.id">
            {{ type.name }}
          </option>
        </select>
      </div>

      <ul class="space-y-4">
        <li
          v-for="problem in problems"
          :key="problem.id"
          class="p-4 border border-gray-200 rounded-lg shadow-sm"
        >
          <div class="flex justify-between items-center">
            <div>
              <span class="text-lg font-semibold">{{ problem.name }}</span> --
              难度:
              <span class="text-gray-600">{{
                difficultyLevels[problem.difficulty as 1 | 2 | 3 | 4] ||
                "未知难度"
              }}</span>
              -- 类型：
              <span class="text-gray-600">{{
                problemTypes[problem.problem_type_id - 1]?.name || "未知类型"
              }}</span>
            </div>
            <button
              @click="viewProblemDetail(problem.id)"
              class="bg-green-500 text-white font-bold py-1 px-3 rounded hover:bg-green-700"
            >
              查看详情
            </button>
          </div>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from "vue";
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
        "Content-Type": "application/json",
      },
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
        "Content-Type": "application/json",
      },
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
        "Content-Type": "application/json",
      },
    };
    const res = await axios.post("/api/user/problem_types", {}, config);
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
  router.push({ name: "ProblemDetail", params: { id: problemId } });
};

onMounted(() => {
  const competitionId = Number(route.params.id);
  fetchCompetitionDetail(competitionId);
  fetchProblems(competitionId);
  fetchProblemTypes();
});

// 监听 filters 变化并自动筛选
watch(
  () => [filters.value.difficulty, filters.value.problem_type_id],
  ([newDifficulty, newProblemTypeId]) => {
    const competitionId = Number(route.params.id);
    fetchProblems(competitionId);
  }
);
</script>