<template>
	<div class="size-full relative">
		<div class="w-[400px] h-[600px] max-h-full bg-white rounded-2xl shadow-md absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" >
			<!-- style="width: 400px; height: 600px; max-height: 100%;" class="p-3 bg-white rounded-2xl shadow-md fle flex-col justify-center absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 overflow-y-auto" -->
			<a-form layout="vertical" rules="" @submit.prevent="resetPassword" class="w-full max-h-full p-3 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 overflow-y-auto" >
				<a-form-item class="mb-3">
					<h3 class="w-full text-4xl text-center font-bold text-primary">找回密码</h3>
				</a-form-item>
				<a-form-item label="邮箱" class="mb-3">
					<a-input v-model="email" placeholder="请输入邮箱" />
				</a-form-item>
				<a-form-item label="验证码" class="mb-3">
					<a-input-group class="!flex" compact>
						<a-input class="flex-1" v-model="code" placeholder="验证码" />
						<a-button type="default" @click="forgetPassword">发送验证码</a-button>
					</a-input-group>
				</a-form-item>
				<a-form-item label="密码">
					<a-input-password v-model="code" placeholder="请输入新密码" />
				</a-form-item>
				<a-form-item>
					<a-button type="primary" html-type="submit" class="w-full">
						重置密码
					</a-button>
					<span class="w-full mt-1 block text-xs text-center text-gray-400 "><a class="hover:text-primary hover:underline" @click="toLogin">返回登录界面</a></span>
				</a-form-item>
			</a-form>
		</div>
	</div>
</template>
<script setup>
import { ref } from 'vue';
import axios from 'axios';
import router from '../router';

const email = ref('');
const code = ref('');
const password = ref('');

function toLogin() {
	router.push('/user/login');
}
const forgetPassword = async () => {
	//去除邮箱所有空格
	email.value = email.value.replace(/\s+/g, '');
	if (!email.value) {
		alert('请输入邮箱');
		return;
	}
	try {
		const res = await axios.post(
			`/api/user/forgot-password?email=${email.value}`,
			{},
			{
				withCredentials: true,
			}
		);
		if (res.data.code === 200) {
			alert('发送成功');
		}
	} catch (e) {
		alert(e);
	}
};

const resetPassword = async () => {
	//去除邮箱所有空格
	email.value = email.value.replace(/\s+/g, '');
	if (!email.value) {
		alert('请输入邮箱');
		return;
	}
    //去除验证码所有空格
    code.value = code.value.replace(/\s+/g, '');
    if (!code.value) {
        alert('请输入验证码');
        return;
    }
    if (!password.value) {
        alert('请输入密码');
        return;
    }
	try {
		const res = await axios.post(
			`/api/user/reset-password`,
			{
				email: email.value,
				new_password: password.value,
			},
			{
				headers: {
					'X-Reset-Code': code.value,
				},
				withCredentials: true,
			}
		);
		if (res.data.code === 200) {
			alert('重置成功');
		}
	} catch (e) {
		alert(e);
	}
};
</script>
