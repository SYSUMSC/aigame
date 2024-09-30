<template>
  <div class="container">
    <div class="row">
      <div class="col-md-6">
        <LeftComponent />
      </div>
      <div class="col-md-6">
        <RightComponent />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import LeftComponent from './UserCenter.vue';
import RightComponent from './Team.vue';

</script>