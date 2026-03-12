import { reactive, readonly } from 'vue'

const state = reactive({
  // 文件上传状态
  isUploaded: false,
  totalChapters: 0,
  chapterTitles: [],
  currentChapterIndex: 0,

  // 图谱数据
  graphData: null,
  mainCharacters: [],

  // 选中的人物
  selectedCharacter: null,
  characterQuotes: []
})

const actions = {
  // 设置上传状态
  setUploaded(status, totalChapters, chapterTitles) {
    state.isUploaded = status
    state.totalChapters = totalChapters
    state.chapterTitles = chapterTitles
  },

  // 设置当前章节
  setCurrentChapter(index) {
    state.currentChapterIndex = index
  },

  // 设置图谱数据
  setGraphData(data) {
    state.graphData = data
  },

  // 设置主角列表
  setMainCharacters(chars) {
    state.mainCharacters = chars
  },

  // 选中人物
  selectCharacter(name, quotes) {
    state.selectedCharacter = name
    state.characterQuotes = quotes
  },

  // 清除选中
  clearSelectedCharacter() {
    state.selectedCharacter = null
    state.characterQuotes = []
  },

  // 重置状态
  reset() {
    state.isUploaded = false
    state.totalChapters = 0
    state.chapterTitles = []
    state.currentChapterIndex = 0
    state.graphData = null
    state.mainCharacters = []
    state.selectedCharacter = null
    state.characterQuotes = []
  }
}

export default {
  state: readonly(state),
  actions
}
