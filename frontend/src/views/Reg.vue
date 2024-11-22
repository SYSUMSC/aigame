<template>
	<a-config-provider :theme="{
    token:{
        colorPrimary: '#E58A57',
        colorPrimaryHover: '#CF7D4F',
        colorLinkHover: '#E58A57',
    }}">
		<div class="size-full relative">
			<div class="size-full lg:w-[400px] lg:h-[700px] max-h-full bg-white rounded-2xl shadow-md absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2" >
				<!-- style="width: 400px; height: 600px; max-height: 100%;" class="p-3 bg-white rounded-2xl shadow-md fle flex-col justify-center absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 overflow-y-auto" -->
				<a-form layout="vertical" :rules="{username: [{ required: true, message: '请输入用户名' }], password: [{ required: true, message: '请输入密码', trigger: 'blur' }]}" @submit.prevent="reg" class="w-full max-h-full p-5 lg:p-3 absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 overflow-y-auto" >
					<!-- dTODO flex导致出现滚动条的高度下能正常滚动底部到但顶部无法滚动完全 -->
					<a-form-item class="mb-3 flex justify-center">
						<img v-if="windowWidth <= AntdWindowsWidth.lg" src="/logo_aigame.svg" alt="" class="size-[200px]">
						<h3 class="w-full text-4xl text-center font-bold text-secondary">注册</h3>
					</a-form-item>
					<a-form-item label="用户名" class="mb-3">
						<a-input v-model:value="username" placeholder="请输入用户名" />
					</a-form-item>
					<a-form-item label="电子邮箱" class="mb-3">
						<a-input v-model:value="email" placeholder="请输入电子邮箱" />
					</a-form-item>
					<a-form-item label="验证码" class="mb-3">
					<a-input-group class="!flex" compact>
						<a-input class="flex-1" v-model:value="verify_code" placeholder="请输入验证码" />
						<a-button type="default" @click="sendVerifyCode">发送验证码</a-button>
					</a-input-group>
					</a-form-item>
					<a-form-item label="姓名" class="mb-3">
						<a-input v-model:value="name" placeholder="请输入姓名" />
					</a-form-item>
					<a-form-item label="学号" class="mb-3">
						<a-input v-model:value="student_id" placeholder="请输入学号" />
					</a-form-item>
					<a-form-item label="密码">
						<a-input-password v-model:value="password" placeholder="请输入密码" />
						<!-- <span class="w-full block text-sm text-end text-gray-400 hover:text-primary hover:underline"><a @click="forget">忘记密码?</a></span> -->
					</a-form-item>
					<a-form-item>
						<a-button type="primary" html-type="submit" class="w-full text-l">
							注册
						</a-button>
						<span class="w-full mt-1 block text-sm text-center text-gray-400 ">已有账号？<a class="hover:text-secondary hover:underline" @click="toLogin">去登录</a></span>
					</a-form-item>
				</a-form>
			</div>
		</div>
	</a-config-provider>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';
import { windowWidth } from '../global/window';
import { AntdWindowsWidth } from '../constants/antd-windows-width';

const username = ref('');
const email = ref('');
const name = ref('');
const student_id = ref('');
const password = ref('');
const verify_code = ref('');
const router = useRouter();

function toLogin() {
	router.push('/user/login');
}
const sendVerifyCode = async () => {
	// 去除空格
	email.value = email.value.trim();
	if (email.value) {
		try {
			const res = await axios.post('/api/user/register', {
				username: username.value,
				email: email.value,
				name: name.value,
				student_id: student_id.value,
				password: password.value,
			},{withCredentials:true});
			alert(res.data.msg);
		} catch (error) {
			console.error(error);
			alert('注册失败，请稍后再试。');
		}
	} else {
		alert('请输入电子邮件。');
	}
};

const reg = async () => {
	// 去除空格
	verify_code.value = verify_code.value.trim();
	if (verify_code.value) {
		const res = await axios.post('/api/user/register', {
			username: username.value,
			email: email.value,
			name: name.value,
			student_id: student_id.value,
			password: password.value,
		},{
      headers:{
        'Content-Type':'application/json',
        'X-Verify-Code':verify_code.value
      },
      withCredentials:true
    });
    if (res.status === 200 && res.data.code === 0) {
				alert('注册成功，跳转到登录页面');

				// 注册成功后跳转到登录页面
				router.push('/user/login');
			} else {
				alert(res.data.msg);
			}
	}
};
</script>
