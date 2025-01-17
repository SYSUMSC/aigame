<template>
	<div class="size-full relative">
		<div class="size-full lg:w-[400px] lg:h-[500px] max-h-full bg-white rounded-2xl shadow-md absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" >
			<!-- style="width: 400px; height: 600px; max-height: 100%;" class="p-3 bg-white rounded-2xl shadow-md fle flex-col justify-center absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 overflow-y-auto" -->
			<a-form layout="vertical" @submit.prevent="login" class="w-full max-h-full p-5 lg:p-3 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 overflow-y-auto" >
				<!-- dTODO flex导致出现滚动条的高度下能正常滚动底部到但顶部无法滚动完全 -->
				<a-form-item class="mb-3 flex justify-center">
					<img v-if="windowWidth <= AntdWindowsWidth.lg" src="/logo_aigame.svg" alt="" class="size-[200px]">
					<h3 class="w-full text-4xl text-center font-bold text-primary">登录</h3>
				</a-form-item>
				<a-form-item label="用户名" class="mb-3" :rules="[{ required: true, message: '请输入用户名',trigger:'blur' }]">
					<a-input v-model:value="username" placeholder="请输入用户名" />
				</a-form-item>
				<a-form-item label="密码" :rules="[{ required: true, message: '请输入密码',trigger:'blur' }]">
					<a-input-password v-model:value="password" placeholder="请输入密码" />
					<span class="w-full block text-sm text-end text-gray-400 "><a class="hover:text-primary hover:underline" @click="forget">忘记密码?</a></span>
				</a-form-item>
				<a-form-item>
					<a-button type="primary" html-type="submit" class="w-full text-l">
						登录
					</a-button>
					<span class="w-full mt-1 block text-sm text-center text-gray-400 ">还没有账号？<a class="hover:text-primary hover:underline" @click="toReg">去注册</a></span>
				</a-form-item>
			</a-form>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import axios from 'axios';

import { useUserStore } from '../stores/user';
import { windowWidth } from '../global/window';
import { AntdWindowsWidth } from '../constants/antd-windows-width';

const username = ref('');
const password = ref('');
const userStore = useUserStore();
const router = useRouter();

const forget = () => {
	router.push('/user/forget');
};

function toReg() {
	router.push('/user/reg');
}
const login = async () => {
	try {
		const res = await axios.post('/api/user/login', {
			username: username.value,
			password: password.value,
		});

		// 检查是否登录成功
		if (res.status === 200 && res.data.code === 0) {
			const token = res.data.data.access_token;

			// 存储 token
			localStorage.setItem('token', token);
			// 设置 axios 默认头
			axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

			// 打印请求头以检查
			console.log(
				'Authorization Header:',
				axios.defaults.headers.common['Authorization']
			);

			// 调用 me API 获取用户信息
			const userInfoRes = await axios.get('/api/user/info');
			console.log('User Info Response:', userInfoRes);

			if (userInfoRes.status === 200 && userInfoRes.data.code === 0) {
				const userData = userInfoRes.data.data;
				// 存储用户数据
				userStore.setUser(userData);

				// 跳转到用户主页
				router.push('/info');
			} else {
				alert('获取用户信息失败');
			}
		} else {
			alert(res.data.msg);
		}
	} catch (error) {
		console.error(error);
		alert('登录失败，请稍后再试。');
	}
};
</script>
