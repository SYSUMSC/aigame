<template>
	<div class="pt-5">
		<div class="row justify-content-center">
			<div class="col-md-6">
				<div class="card">
					<div class="card-header">
						<h3 class="text-center">登录</h3>
					</div>
					<div class="card-body">
						<div>
							<div class="form-group mb-3">
								<label for="email">邮箱</label>
								<input
									type="text"
									id="email"
									v-model="email"
									class="form-control"
									required
								/>
							</div>
							<div class="form-group mb-3">
								<label for="code">验证码</label>
								<input
									type="text"
									id="code"
									v-model="code"
									class="form-control"
								/>
							</div>
							<div class="form-group mb-3">
								<label for="password">密码</label>
								<input
									type="password"
									id="password"
									v-model="password"
									class="form-control"
								/>
							</div>
							<button
								@click="forgetPassword"
								class="btn btn-primary w-100"
							>
								发送验证码
							</button>
							<button
								@click="resetPassword"
								class="btn btn-primary w-100 mt-3"
							>
								重置密码
							</button>
						</div>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>
<script setup>
import { ref } from 'vue';
import axios from 'axios';

const email = ref('');
const code = ref('');
const password = ref('');

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
