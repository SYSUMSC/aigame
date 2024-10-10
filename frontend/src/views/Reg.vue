<template>
	<div class="pt-5">
		<div class="row justify-content-center">
			<div class="col-md-6">
				<div class="card">
					<div class="card-header">
						<h3 class="text-center">注册</h3>
					</div>
					<div class="card-body">
						<form @submit.prevent="reg">
							<div class="form-group mb-3">
								<label for="username">用户名</label>
								<input
									type="text"
									id="username"
									v-model="username"
									class="form-control"
									required
								/>
							</div>
							<div class="form-group mb-3">
								<label for="email">电子邮件</label>
								<input
									type="email"
									id="email"
									v-model="email"
									class="form-control"
									required
								/>
							</div>
							<div class="form-group mb-3">
								<label for="verify_code">验证码</label>
								<input
									type="text"
									id="verify_code"
									v-model="verify_code"
									class="form-control"
								/>
							</div>
							<div class="form-group mb-3">
								<label for="name">姓名</label>
								<input
									type="text"
									id="name"
									v-model="name"
									class="form-control"
									required
								/>
							</div>
							<div class="form-group mb-3">
								<label for="student_id">学号</label>
								<input
									type="text"
									id="student_id"
									v-model="student_id"
									class="form-control"
									required
								/>
							</div>
							<div class="form-group mb-3">
								<label for="password">密码</label>
								<input
									type="password"
									id="password"
									v-model="password"
									class="form-control"
									required
								/>
							</div>
							<button
								@click="sendVerifyCode"
								class="btn btn-primary w-100 mb-3"
							>
								发送验证码
							</button>
							<button
								type="submit"
								class="btn btn-primary w-100"
							>
								注册
							</button>
						</form>
					</div>
				</div>
			</div>
		</div>
	</div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import axios from 'axios';
import { useRouter } from 'vue-router';

const username = ref('');
const email = ref('');
const name = ref('');
const student_id = ref('');
const password = ref('');
const verify_code = ref('');
const router = useRouter();

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
