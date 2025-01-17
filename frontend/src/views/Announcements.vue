<template>
	<div
		class="card max-w-[1000px] mx-auto p-5 bg-gray-5 rounded-2xl shadow-md"
	>
		<h1
			class="w-fit text-3xl font-bold mb-4 relative transition-all duration-300 hover:scale-105"
		>
			公告
		</h1>
		<div class="w-full flex flex-col gap-3">
			<AnnouncementItems
				v-for="announcement in announcements"
				:content="announcement.content"
				:date="announcement.date"
				:key="announcement.date.toString()"
			/>
		</div>
	</div>
</template>
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import axios from 'axios';

import AnnouncementItems, { Announcement } from './AnnouncementItems.vue';

// 定义公告数据
const announcements = ref<Announcement[]>([]);

// 获取公告信息
const fetchAnnouncements = async () => {
	try {
		const res = await axios.get('/api/user/announcements');
		if (res.status === 200 && res.data.code === 0) {
			announcements.value = res.data.data.map((item: any) => ({
				content: item.content,
				date: new Date(item.date),
			}));
		} else {
			console.error('获取公告失败:', res.data.msg);
		}
	} catch (error) {
		console.error('公告请求失败:', error);
	}
};

// 页面加载时获取公告数据
onMounted(fetchAnnouncements);
</script>

<style scoped>
h1:before {
	content: '';
	position: absolute;
	width: 0;
	left: 0;
	bottom: 0;
	height: 2px;
	background-color: gray;
	transition: all 0.3s;
}
h1:hover:before {
	width: 100%;
}
</style>
