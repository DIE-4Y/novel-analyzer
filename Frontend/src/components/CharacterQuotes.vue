<template>
  <div class="quotes-container">
    <h3 v-if="characterName" class="character-name">{{ characterName }}</h3>
    <div class="quotes-list">
      <div
        v-for="(quote, index) in quotes"
        :key="index"
        class="quote-item"
      >
        <div class="quote-index">{{ index + 1 }}</div>
        <p class="quote-content">{{ quote.text }}</p>
      </div>
      <div v-if="!quotes || quotes.length === 0" class="no-data">
        暂无相关语句
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'CharacterQuotes',
  props: {
    characterName: {
      type: String,
      default: ''
    },
    quotes: {
      type: Array,
      default: () => []
    }
  }
}
</script>

<style scoped>
.quotes-container {
  padding: 20px;
}

.character-name {
  font-size: 18px;
  color: #333;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 2px solid #409EFF;
}

.quotes-list {
  max-height: calc(100vh - 200px);
  overflow-y: auto;
}

.quote-item {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 6px;
  transition: background 0.3s;
}

.quote-item:hover {
  background: #ecf5ff;
}

.quote-index {
  flex-shrink: 0;
  width: 28px;
  height: 28px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: #fff;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: bold;
}

.quote-content {
  margin: 0;
  font-size: 14px;
  line-height: 1.6;
  color: #333;
  flex: 1;
}

.no-data {
  text-align: center;
  color: #999;
  padding: 40px 0;
  font-size: 14px;
}
</style>
