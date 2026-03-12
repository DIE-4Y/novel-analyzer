<template>
  <div class="pagination">
    <button
      @click="goToPage(0)"
      :disabled="current === 0"
      class="page-btn"
      title="第一章"
    >
      ⟪
    </button>

    <button
      @click="prevPage"
      :disabled="current === 0"
      class="page-btn"
    >
      上一章
    </button>

    <div class="page-numbers">
      <!-- 显示首页 -->
      <button
        v-if="visiblePages[0] > 1"
        @click="goToPage(0)"
        class="page-number"
      >
        1
      </button>

      <!-- 省略号 -->
      <span v-if="visiblePages[0] > 2" class="ellipsis">...</span>

      <!-- 当前页附近的页码 -->
      <button
        v-for="page in visiblePages"
        :key="page"
        @click="goToPage(page - 1)"
        :class="['page-number', { active: page - 1 === current }]"
      >
        {{ page }}
      </button>

      <!-- 省略号 -->
      <span v-if="visiblePages[visiblePages.length - 1] < total - 1" class="ellipsis">...</span>

      <!-- 显示末页 -->
      <button
        v-if="visiblePages[visiblePages.length - 1] < total"
        @click="goToPage(total - 1)"
        class="page-number"
      >
        {{ total }}
      </button>
    </div>

    <button
      @click="nextPage"
      :disabled="current === total - 1"
      class="page-btn"
    >
      下一章
    </button>

    <button
      @click="goToPage(total - 1)"
      :disabled="current === total - 1"
      class="page-btn"
      title="最后一章"
    >
      ⟫
    </button>

    <div class="page-info">
      <span>共 {{ total }} 章</span>
      <input
        type="number"
        v-model.number="jumpToPage"
        @keyup.enter="handleJump"
        :min="1"
        :max="total"
        class="jump-input"
        placeholder="跳转"
      />
      <button @click="handleJump" class="jump-btn">跳转</button>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Pagination',
  props: {
    total: {
      type: Number,
      required: true,
      default: 0
    },
    current: {
      type: Number,
      required: true,
      default: 0
    }
  },

  emits: ['page-change'],

  data() {
    return {
      jumpToPage: null
    }
  },

  computed: {
    visiblePages() {
      const delta = 2
      const range = []
      const start = Math.max(2, this.current + 1 - delta)
      const end = Math.min(this.total - 1, this.current + 1 + delta)

      for (let i = start; i <= end; i++) {
        range.push(i)
      }

      return range
    }
  },

  methods: {
    prevPage() {
      if (this.current > 0) {
        this.$emit('page-change', this.current - 1)
      }
    },

    nextPage() {
      if (this.current < this.total - 1) {
        this.$emit('page-change', this.current + 1)
      }
    },

    goToPage(index) {
      if (index >= 0 && index < this.total && index !== this.current) {
        this.$emit('page-change', index)
      }
    },

    handleJump() {
      if (this.jumpToPage !== null && this.jumpToPage >= 1 && this.jumpToPage <= this.total) {
        this.goToPage(this.jumpToPage - 1)
        this.jumpToPage = null
      }
    }
  }
}
</script>

<style scoped>
.pagination {
  display: flex;
  align-items: center;
  gap: 8px;
}

.page-btn {
  padding: 6px 12px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: all 0.3s;
  min-width: 36px;
}

.page-btn:hover:not(:disabled) {
  background: #f5f7fa;
  border-color: #c0c4cc;
}

.page-btn:disabled {
  color: #c0c4cc;
  cursor: not-allowed;
  background: #f5f7fa;
}

.page-numbers {
  display: flex;
  gap: 6px;
  align-items: center;
}

.page-number {
  min-width: 36px;
  height: 36px;
  padding: 0 12px;
  background: #fff;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  color: #606266;
  transition: all 0.3s;
}

.page-number:hover {
  background: #f5f7fa;
  border-color: #c0c4cc;
}

.page-number.active {
  background: #409EFF;
  color: #fff;
  border-color: #409EFF;
}

.ellipsis {
  color: #999;
  padding: 0 4px;
}

.page-info {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #999;
  margin-left: 12px;
}

.jump-input {
  width: 60px;
  padding: 6px 8px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  text-align: center;
}

.jump-input:focus {
  outline: none;
  border-color: #409EFF;
}

.jump-btn {
  padding: 6px 12px;
  background: #409EFF;
  color: #fff;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.jump-btn:hover {
  background: #66b1ff;
}
</style>
