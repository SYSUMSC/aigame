<!-- <template>
  <main class="min-h-screen py-6 flex flex-col justify-center items-center">
    <div class="container mx-auto">
      <div class="card">
        <div class="card-header">赛题详情</div>
        <div class="card-body">
          <h1 class="mb-3 fs-4">{{ problem?.name }}</h1>
          <p>难度: {{ difficultyLevels[problem?.difficulty as 1 | 2 | 3 | 4] || "未知难度" }}</p>
          <p>类型: {{ problemType?.name || "未知类型" }}</p>
          <p>描述: {{ problemType?.description || "无描述" }}</p>
          <p>分数: {{ problem?.score || "未评分" }}</p>

          <!-- 文件上传表单 -->
          <!-- <form @submit.prevent="submitFile">
            <input type="file" @change="handleFileChange" class="mb-3" required />
            <button type="submit" class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700">
              提交文件
            </button>
          </form>
        </div>
      </div>
    </div>
  </main>
</template> -->
<!-- 
<script setup lang="ts">
import { ref, onMounted } from "vue";
import axios from "axios";
import { useRoute } from "vue-router";

type Problem = {
  id: number;
  name: string;
  difficulty: number;
  problem_type_id: number;
  description: string;
  score: number;
};

type ProblemType = {
  id: number;
  name: string;
  description:string;
};

const route = useRoute();
const problem = ref<Problem | null>(null);
const problemType = ref<ProblemType | null>(null);
const selectedFile = ref<File | null>(null);

const difficultyLevels = {
  1: "旅行",
  2: "经典",
  3: "专家",
  4: "大师",
}; -->
<!-- 
// 获取赛题详情
const fetchProblemDetail = async (problemId: number) => {
  try {
    const res = await axios.post(`/api/user/problem/${problemId}`, {});
    if (res.status === 200 && res.data.code === 0) {
      problem.value = res.data.data.problem;
      problemType.value = res.data.data.problem_type;
    } else {
      console.error("获取赛题详情失败:", `状态码: ${res.status}, 错误消息: ${res.data.msg}`);
    }
  } catch (error) {
    console.error("发生错误:", error);
  }
};

onMounted(() => {
  const problemId = Number(route.params.id);
  fetchProblemDetail(problemId);
});
</script> --> -->



<template>
  <main class="min-h-screen py-6 flex flex-col justify-center items-center">
    <div class="container mx-auto">
      <div class="card">
        <div class="card-header">赛题详情</div>
        <div class="card-body">
          <h1 class="mb-3 fs-4">{{ problem?.name }}</h1>
          <p>难度: {{ difficultyLevels[problem?.difficulty as 1 | 2 | 3 | 4] || "未知难度" }}</p>
          <p>类型: {{ problemType?.name || "未知类型" }}</p>
          <p>描述: {{ problemType?.description || "无描述" }}</p>
          <p>分数: {{ problem?.score || "未评分" }}</p>

          <!-- 文件上传表单 -->
          <form @submit.prevent="submitFile">
            <input type="file" @change="handleFileChange" class="mb-3" required />
            <button type="submit" class="bg-blue-500 text-white font-bold py-2 px-4 rounded hover:bg-blue-700">
              提交文件
            </button>
          </form>
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
  description: string;
  score: number;
};

type ProblemType = {
  id: number;
  name: string;
  description:string;
};

const route = useRoute();
const problem = ref<Problem | null>(null);
const problemType = ref<ProblemType | null>(null);
const selectedFile = ref<File | null>(null);

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
      console.error("获取赛题详情失败:", `状态码: ${res.status}, 错误消息: ${res.data.msg}`);
    }
  } catch (error) {
    console.error("发生错误:", error);
  }
};

// 处理文件更改
const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0]; // 选中的文件存储在selectedFile中
  }
};

// 提交文件
const submitFile = async () => {
  if (!selectedFile.value) {
    alert("请选择文件");
    return;
  }

  const formData = new FormData();
  formData.append("file", selectedFile.value); // 将文件添加到FormData中

  try {
    // const res = await axios.post(`/api/problem/${problem.value?.id}/submit`, formData, {
    //   headers: {
    //     "Content-Type": "multipart/form-data",
    //   }
    // });
      const res = await axios.post(`/api/user/problem/${problem.value?.id}/submit`, formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        }
      });


    if (res.status === 200 && res.data.code === 0) {
      alert("文件提交成功");
    } else {
      console.error("文件提交失败:", res.data.msg);
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
