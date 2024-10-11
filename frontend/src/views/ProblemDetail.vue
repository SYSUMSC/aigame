<template>
  <main class="min-h-screen py-6 flex flex-col justify-center items-center">
    <div class="container mx-auto">
      <div class="card">
        <div class="card-header">赛题详情</div>
        <div class="card-body">
          <h1 class="mb-3 fs-4">{{ problem?.name }}</h1>
          <div class="flex flex-col space-y-2">
            <div class="flex items-center">
              <span class="font-bold text-gray-700 mr-2">难度:</span>
              <span class="bg-blue-100 text-blue-800 px-2 py-1 rounded">{{
                difficultyLevels[problem?.difficulty as 1 | 2 | 3 | 4] ||
                "未知难度"
              }}</span>
            </div>

            <div class="flex items-center">
              <span class="font-bold text-gray-700 mr-2">类型:</span>
              <span class="bg-green-100 text-green-800 px-2 py-1 rounded">{{
                problemType?.name || "未知类型"
              }}</span>
            </div>

            <div class="flex items-center">
              <span class="font-bold text-gray-700 mr-2">类型描述:</span>
              <span class="text-gray-600">{{
                problemType?.description || "无描述"
              }}</span>
            </div>

            <div class="flex items-start">
              <span class="font-bold text-gray-700 mr-2">描述:</span>
              <p class="text-gray-600">{{ problem?.content || "无描述" }}</p>
            </div>

            <div class="flex items-center">
              <span class="font-bold text-gray-700 mr-2">分数:</span>
              <span class="bg-yellow-100 text-yellow-800 px-2 py-1 rounded">{{
                problem?.score || "未评分"
              }}</span>
            </div>

            <div class="flex items-center">
              <!-- 文件上传表单 -->
              <form @submit.prevent="submitFile">
                <input
                  type="file"
                  @change="handleFileChange"
                  class="mb-3 block w-full text-sm text-gray-900 border border-gray-300 rounded-lg cursor-pointer bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  required
                />
                <button
                  type="submit"
                  class="w-full bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700"
                >
                  提交文件
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  </main>
</template>

<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute } from "vue-router";

type Problem = {
  id: number;
  name: string;
  difficulty: number;
  problem_type_id: number;
  content: string;
  score: number;
};

type ProblemType = {
  id: number;
  name: string;
  description: string;
};

const route = useRoute();
const problem = ref<Problem | null>(null);
const problemType = ref<ProblemType | null>(null);
const selectedFile = ref<File | null>(null);
const userStore = { team_id: 1 }; // 假设从userStore获取team_id

const difficultyLevels = {
  1: "旅行",
  2: "经典",
  3: "专家",
  4: "大师",
};

// 获取赛题详情
const fetchProblemDetail = async (problemId: number) => {
  try {
    const res = await axios.post(`/api/user/problem/${problemId}`, {});
    if (res.status === 200 && res.data.code === 0) {
      problem.value = res.data.data.problem;
      problemType.value = res.data.data.problem_type;
    } else {
      console.error(
        "获取赛题详情失败:",
        `状态码: ${res.status}, 错误消息: ${res.data.msg}`
      );
    }
  } catch (error) {
    console.error("发生错误:", error);
  }
};

// 处理文件更改
const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
  }
};

// 提交文件
const submitFile = async () => {
  if (!selectedFile.value) {
    alert("请选择文件");
    return;
  }

  // 检查队伍是否已报名
  const checkParticipation = await axios.get("/api/user/participation", {
    params: {
      team_id: userStore.team_id,
    },
  });

  if (
    checkParticipation.data.code !== 0 ||
    checkParticipation.data.data.length === 0
  ) {
    alert("您的队伍尚未报名此比赛，无法提交文件");
    return; // 阻止文件提交
  }

  const formData = new FormData();
  formData.append("file", selectedFile.value);

  try {
    const res = await axios.post(
      `/api/user/problem/${problem.value?.id}/submit`,
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    if (res.status === 200 && res.data.code === 0) {
      alert("文件提交成功");
    } else {
      alert("文件提交失败: " + res.data.msg);
    }
  } catch (error) {
    console.error("文件上传出错:", error);
  }
};

onMounted(() => {
  const problemId = Number(route.params.id);
  fetchProblemDetail(problemId);
});
</script>
