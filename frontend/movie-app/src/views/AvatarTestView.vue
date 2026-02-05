<template>
  <div class="avatar-test-page">
    <h2>头像组件测试页面</h2>
    
    <div class="test-section">
      <h3>基础用法</h3>
      <AvatarUpload 
        v-model="avatar1"
        :size="100"
        placeholder="点击上传头像"
      />
    </div>
    
    <div class="test-section">
      <h3>只读模式</h3>
      <AvatarUpload 
        v-model="avatar2"
        :size="80"
        :editable="false"
        placeholder="只读头像"
      />
    </div>
    
    <div class="test-section">
      <h3>大尺寸头像</h3>
      <AvatarUpload 
        v-model="avatar3"
        :size="150"
        placeholder="大尺寸头像"
      />
    </div>
    
    <div class="debug-info">
      <h3>调试信息</h3>
      <div class="debug-item">
        <label>Avatar 1:</label>
        <input v-model="avatar1" placeholder="头像URL" />
      </div>
      <div class="debug-item">
        <label>Avatar 2:</label>
        <input v-model="avatar2" placeholder="头像URL" />
      </div>
      <div class="debug-item">
        <label>Avatar 3:</label>
        <input v-model="avatar3" placeholder="头像URL" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import AvatarUpload from '@/components/AvatarUpload.vue'

const avatar1 = ref('')
const avatar2 = ref('/media/avatars/default.jpg')
const avatar3 = ref('')
</script>

<style scoped>
.avatar-test-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.test-section {
  margin: 40px 0;
  padding: 20px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background: #fafafa;
}

.test-section h3 {
  margin-top: 0;
  margin-bottom: 20px;
  color: #409eff;
}

.debug-info {
  margin-top: 40px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 8px;
}

.debug-item {
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 10px 0;
}

.debug-item label {
  min-width: 80px;
  font-weight: 500;
}

.debug-item input {
  flex: 1;
  padding: 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-family: monospace;
}

h2 {
  color: #2c3e50;
  text-align: center;
  margin-bottom: 40px;
}
</style>