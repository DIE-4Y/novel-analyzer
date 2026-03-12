<template>
  <div class="upload-container">
    <h1 class="title">小说人物关系图谱分析系统</h1>

    <div class="upload-box">
      <div class="upload-area" @dragover.prevent @drop="handleDrop">
        <input
          type="file"
          ref="fileInput"
          @change="handleFileChange"
          accept=".txt,.pdf"
          style="display: none"
        />

        <div v-if="!fileName" class="upload-placeholder" @click="$refs.fileInput.click()">
          <div class="icon">📁</div>
          <p>点击或拖拽上传小说文件</p>
          <p class="hint">支持格式：TXT, PDF</p>
        </div>

        <div v-else class="file-info">
          <div class="icon">📄</div>
          <p>{{ fileName }}</p>
          <button @click="removeFile" class="remove-btn">删除</button>
        </div>
      </div>

      <button
        v-if="fileName"
        @click="uploadFile"
        class="upload-btn"
        :disabled="uploading"
      >
        {{ uploading ? '处理中...' : '开始分析' }}
      </button>
    </div>

    <div v-if="error" class="error-message">
      {{ error }}
    </div>

    <div v-if="uploading" class="loading">
      <div class="spinner"></div>
      <p>正在分析小说内容，提取人物关系...</p>
    </div>
  </div>
</template>

<script>
import { uploadNovel } from '../api'
import store from '../store'

export default {
  name: 'UploadPage',
  data() {
    return {
      fileName: '',
      selectedFile: null,
      uploading: false,
      error: ''
    }
  },

  methods: {
    handleFileChange(event) {
      const file = event.target.files[0]
      if (file) {
        this.selectedFile = file
        this.fileName = file.name
        this.error = ''
      }
    },

    handleDrop(event) {
      const file = event.dataTransfer.files[0]
      if (file && (file.type === 'text/plain' || file.type === 'application/pdf')) {
        this.selectedFile = file
        this.fileName = file.name
        this.$refs.fileInput.files = event.dataTransfer.files
        this.error = ''
      } else {
        this.error = '仅支持 TXT 和 PDF 格式的文件'
      }
    },

    removeFile() {
      this.fileName = ''
      this.selectedFile = null
      this.error = ''
      if (this.$refs.fileInput) {
        this.$refs.fileInput.value = ''
      }
    },

    async uploadFile() {
      if (!this.selectedFile) {
        this.error = '请先选择文件'
        return
      }

      // 检查文件大小（最大 16MB）
      if (this.selectedFile.size > 16 * 1024 * 1024) {
        this.error = '文件大小不能超过 16MB'
        return
      }

      this.uploading = true
      this.error = ''

      try {
        const result = await uploadNovel(this.selectedFile)

        // 更新状态
        store.actions.setUploaded(
          true,
          result.total_chapters,
          result.chapter_titles
        )
        store.actions.setMainCharacters(result.main_characters)
        store.actions.setGraphData(result.graph_data)

        // 跳转到图谱页面
        this.$router.push('/graph')
      } catch (err) {
        console.error('上传失败:', err)
        this.error = err.response?.data?.error || '上传失败，请重试'
      } finally {
        this.uploading = false
      }
    }
  }
}
</script>

<style scoped>
.upload-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 40px 20px;
  text-align: center;
}

.title {
  font-size: 32px;
  color: #333;
  margin-bottom: 40px;
  font-weight: 600;
}

.upload-box {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 40px;
}

.upload-area {
  border: 2px dashed #ddd;
  border-radius: 8px;
  transition: all 0.3s;
  cursor: pointer;
}

.upload-area:hover {
  border-color: #409EFF;
  background: #f5f7fa;
}

.upload-placeholder {
  padding: 60px 20px;
  color: #999;
}

.upload-placeholder .icon {
  font-size: 64px;
  margin-bottom: 20px;
}

.upload-placeholder p {
  font-size: 16px;
  margin: 10px 0;
}

.hint {
  font-size: 14px;
  color: #bbb;
}

.file-info {
  padding: 40px 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
}

.file-info .icon {
  font-size: 48px;
}

.file-info p {
  font-size: 16px;
  color: #333;
  flex: 1;
}

.remove-btn {
  padding: 8px 16px;
  background: #f44;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background 0.3s;
}

.remove-btn:hover {
  background: #d33;
}

.upload-btn {
  margin-top: 20px;
  padding: 12px 40px;
  background: #409EFF;
  color: #fff;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  cursor: pointer;
  transition: background 0.3s;
}

.upload-btn:hover:not(:disabled) {
  background: #66b1ff;
}

.upload-btn:disabled {
  background: #a0cfff;
  cursor: not-allowed;
}

.error-message {
  margin-top: 20px;
  padding: 12px;
  background: #fef0f0;
  color: #f56c6c;
  border-radius: 4px;
  font-size: 14px;
}

.loading {
  margin-top: 30px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 4px solid #f3f3f3;
  border-top: 4px solid #409EFF;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.loading p {
  color: #666;
  font-size: 14px;
}
</style>
