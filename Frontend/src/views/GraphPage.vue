<template>
  <div class="graph-page">
    <!-- 左侧人物语录面板 -->
    <div class="sidebar" v-if="selectedCharacter">
      <div class="sidebar-header">
        <h3>{{ selectedCharacter }}</h3>
        <button @click="closeSidebar" class="close-btn">×</button>
      </div>
      <div class="quotes-list">
        <div v-for="(quote, index) in characterQuotes" :key="index" class="quote-item">
          <div class="quote-number">{{ index + 1 }}</div>
          <p class="quote-text">{{ quote.text }}</p>
        </div>
        <div v-if="characterQuotes.length === 0" class="no-quotes">
          暂无相关语句
        </div>
      </div>
    </div>

    <!-- 中间图谱区域 -->
    <div class="main-content">
      <div class="header">
        <button @click="goBack" class="back-btn">← 返回上传</button>
        <h2 class="chapter-title">
          {{ currentChapterTitle || `第${currentChapterIndex + 1}章` }}
        </h2>
        <div class="stats">
          <span>人物：{{ characterCount }}</span>
          <span>关系：{{ relationCount }}</span>
        </div>
      </div>

      <div class="graph-container" ref="graphContainer">
        <CharacterGraph
            ref="graphComponent"
            :graph-data="graphData"
            @node-click="handleNodeClick"
        />
      </div>

      <!-- 底部分页条 -->
      <div class="pagination-bar">
        <Pagination
            :total="totalChapters"
            :current="currentChapterIndex"
            @page-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script>
import {onMounted, ref, computed, watch} from 'vue'
import {useRouter} from 'vue-router'
import {getChapterGraph, getCharacterQuotes, clearUploadStatus} from '../api'
import store from '../store'
import CharacterGraph from '../components/CharacterGraph.vue'
import Pagination from '../components/Pagination.vue'

export default {
  name: 'GraphPage',
  components: {
    CharacterGraph,
    Pagination
  },

  setup() {
    const router = useRouter()
    const graphComponent = ref(null)
    const graphContainer = ref(null)

    const selectedCharacter = computed(() => store.state.selectedCharacter)
    const characterQuotes = computed(() => store.state.characterQuotes)
    const graphData = computed(() => store.state.graphData)
    const currentChapterIndex = computed(() => store.state.currentChapterIndex)
    const totalChapters = computed(() => store.state.totalChapters)
    const chapterTitles = computed(() => store.state.chapterTitles)

    const characterCount = computed(() => graphData.value?.character_count || 0)
    const relationCount = computed(() => graphData.value?.relation_count || 0)

    const currentChapterTitle = computed(() => {
      if (chapterTitles.value && chapterTitles.value[currentChapterIndex.value]) {
        return chapterTitles.value[currentChapterIndex.value]
      }
      return null
    })

    // 加载初始章节（第一章）
    onMounted(async () => {
      if (!store.state.isUploaded) {
        router.push('/')
        return
      }

      // 如果没有当前章节索引，默认为第一章
      if (currentChapterIndex.value === 0 && !graphData.value) {
        await loadChapter(0)
      }
    })

    // 加载指定章节
    async function loadChapter(chapterIndex) {
      try {
        const result = await getChapterGraph(chapterIndex)
        store.actions.setCurrentChapter(chapterIndex)
        store.actions.setGraphData(result.graph_data)
      } catch (err) {
        console.error('加载章节失败:', err)
      }
    }

    // 处理章节切换
    async function handlePageChange(newIndex) {
      if (newIndex !== currentChapterIndex.value) {
        await loadChapter(newIndex)
      }
    }

    // 处理节点点击
    async function handleNodeClick(characterName) {
      try {
        const result = await getCharacterQuotes(characterName)
        store.actions.selectCharacter(characterName, result.quotes)
      } catch (err) {
        console.error('获取语录失败:', err)
      }
    }

    // 关闭侧边栏
    function closeSidebar() {
      store.actions.clearSelectedCharacter()
    }

    // 返回上传页面
    function goBack() {
      clearUploadStatus()
      store.actions.reset()
      router.push('/')
    }

    return {
      graphComponent,
      graphContainer,
      selectedCharacter,
      characterQuotes,
      graphData,
      currentChapterIndex,
      totalChapters,
      currentChapterTitle,
      characterCount,
      relationCount,
      handlePageChange,
      handleNodeClick,
      closeSidebar,
      goBack
    }
  }
}
</script>

<style scoped>
.graph-page {
  display: flex;
  height: 100vh;
  background: #f5f7fa;
}

.sidebar {
  width: 400px;
  background: #fff;
  border-right: 1px solid #e4e7ed;
  display: flex;
  flex-direction: column;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.1);
}

.sidebar-header {
  padding: 20px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: #fafafa;
}

.sidebar-header h3 {
  margin: 0;
  font-size: 18px;
  color: #333;
}

.close-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: transparent;
  font-size: 24px;
  color: #999;
  cursor: pointer;
  border-radius: 4px;
  transition: background 0.3s;
}

.close-btn:hover {
  background: #f0f0f0;
  color: #333;
}

.quotes-list {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

.quote-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
}

.quote-number {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  background: #409EFF;
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.quote-text {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  flex: 1;
}

.no-quotes {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-size: 14px;
}

.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.header {
  padding: 20px;
  background: #fff;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 20px;
}

.back-btn {
  padding: 8px 16px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: all 0.3s;
}

.back-btn:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
}

.chapter-title {
  flex: 1;
  margin: 0;
  font-size: 20px;
  color: #333;
}

.stats {
  display: flex;
  gap: 20px;
  font-size: 14px;
  color: #606266;
}

.stats span {
  padding: 6px 12px;
  background: #f0f9eb;
  border-radius: 4px;
}

.graph-container {
  flex: 1;
  overflow: hidden;
  position: relative;
}

.pagination-bar {
  padding: 20px;
  background: #fff;
  border-top: 1px solid #e4e7ed;
  display: flex;
  justify-content: center;
}
</style>
