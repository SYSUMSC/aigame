<template>
	<div class="card btn-shadow w-full p-3 relative group transition-all duration-300 hover:scale-[1.02] hover:bg-gray-50">
		<p class="w-full whitespace-pre-wrap">{{ content }}</p>
		<p class="px-2 py-1 rounded-md ring-1 ring-gray-300 bg-white text-sm text-gray-500 absolute -bottom-3 right-2 transition-all duration-300 group-hover:bg-gray-50 group-hover:shadow-lg">{{ date.toLocaleString() }}</p>
	</div>
</template>
<script setup lang="ts">
export type Announcement = {
	content:String,
	date:Date,
}
defineProps<Announcement>();
</script>