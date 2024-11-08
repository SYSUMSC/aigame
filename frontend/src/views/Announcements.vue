<template>
	<!-- <div class="size-full bg-gray-50"> -->
		<div class="card max-w-[1000px] mx-auto p-5 bg-gray-5 rounded-2xl shadow-md">
			<h1 class="w-fit text-3xl font-bold mb-4 relative transition-all duration-300 hover:scale-105">公告</h1>
			<div class="w-full flex flex-col gap-3">
				<AnnouncementItems v-for="announcement in announcements" :content="announcement.content" :date="announcement.date" :key="announcement.date.toString()"/>
			</div>
		</div>
	<!-- </div> -->
</template>
<script setup lang="ts">
import { ref } from 'vue'
import AnnouncementItems, { Announcement } from './AnnouncementItems.vue';
// TODO to implement
const testAnnouncement:Announcement[] = [{content:`选手 Ne***, Am***、zi*** 等 7 人存在作弊或疑似作弊等违规行为，相关用户已经封禁，如有异议请通过平台底部邮件联系组委会申诉。提醒各位选手认真阅读诚信比赛承诺书、数据收集政策和参赛提示：https://hack.lug.ustc.edu.cn/terms/ 。`,date:new Date("2024-11-08")}, {content:`(USTC 校内) 参加 Hackergame 2024 的同学可以在「青春科大」平台报名获取学时。


只要完成签到题目（50 分） 即可获取 2.0 二课学时；其他分数（100，200，400，600，800，1000）的学时需要额外提交解答文档（writeup） 到 sec-class@ustclug.org ，详见二课平台各子项目通知。

（子项目可重复报名，例如 1000 分+ 的选手可以报名所有子项目，并获取全部 24 个二课学时）

题解提交截止时间：11.09 12:00 二课报名截止时间：11.16 12:00`,date:new Date("2024-11-09")}, {content:`选手 千高***, Je***、4k**** 等 11 人存在作弊或疑似作弊等违规行为，相关用户已经封禁，如有异议请通过平台底部邮件联系组委会申诉。提醒各位选手认真阅读诚信比赛承诺书、数据收集政策和参赛提示：https://hack.lug.ustc.edu.cn/terms/ 。`,date:new Date("2024-11-10")}, {content:`选手 yu******, 我爱***、wd**** 等 7 人存在作弊或疑似作弊等违规行为，相关用户已经封禁，如有异议请通过平台底部邮件联系组委会申诉。提醒各位选手认真阅读诚信比赛承诺书、数据收集政策和参赛提示：https://hack.lug.ustc.edu.cn/terms/ 。`,date:new Date("2024-11-11")}]
const announcements = ref < Announcement[] > (testAnnouncement)
</script>
<style scoped>
h1:before{
	content: '';
	position: absolute;
	width: 0;
	left: 0;
	bottom: 0;
	height: 2px;
	background-color: gray;
	transition: all 0.3s;
	/* &:hover{
		width: 100%;
	} */
}
h1:hover:before{
	width: 100%;
}
</style>