import axios from 'axios'

const API_BASE_URL = 'http://localhost:5000/api'

// 创建 axios 实例
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 300000, // 5 分钟超时 (300 秒)
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 上传小说文件
 */
export async function uploadNovel(file) {
  const formData = new FormData()
  formData.append('file', file)

  const response = await api.post('/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    },
    timeout: 300000 // 5 分钟超时
  })

  if (response.data.success) {
    // 标记已上传文件
    localStorage.setItem('novelUploaded', 'true')
    localStorage.setItem('totalChapters', response.data.total_chapters)
    localStorage.setItem('chapterTitles', JSON.stringify(response.data.chapter_titles))
  }

  return response.data
}

/**
 * 获取指定章节的人物关系图谱
 */
export async function getChapterGraph(chapterIndex) {
  const response = await api.get(`/chapter/${chapterIndex}`, {
    timeout: 300000 // 5 分钟超时
  })
  return response.data
}

/**
 * 获取人物的相关语句
 */
export async function getCharacterQuotes(characterName) {
  const response = await api.get(`/character/${characterName}`, {
    timeout: 60000 // 1 分钟超时（这个操作比较快）
  })
  return response.data
}

/**
 * 获取主角列表
 */
export async function getMainCharacters() {
  const response = await api.get('/main-characters')
  return response.data
}

/**
 * 清除上传状态
 */
export function clearUploadStatus() {
  localStorage.removeItem('novelUploaded')
  localStorage.removeItem('totalChapters')
  localStorage.removeItem('chapterTitles')
  localStorage.removeItem('currentChapter')
}

export default api
