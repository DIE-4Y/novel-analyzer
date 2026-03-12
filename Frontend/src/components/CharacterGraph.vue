<template>
  <div ref="chartContainer" class="chart-container"></div>
</template>

<script>
import { onMounted, onBeforeUnmount, watch, ref } from 'vue'
import * as echarts from 'echarts'

export default {
  name: 'CharacterGraph',
  props: {
    graphData: {
      type: Object,
      required: true,
      default: () => ({ nodes: [], links: [] })
    }
  },

  emits: ['node-click'],

  setup(props, { emit }) {
    const chartContainer = ref(null)
    const chart = ref(null)

    onMounted(() => {
      initChart()
    })

    onBeforeUnmount(() => {
      if (chart.value) {
        chart.value.dispose()
        window.removeEventListener('resize', handleResize)
      }
    })

    watch(() => props.graphData, (newData) => {
      if (chart.value && newData) {
        updateChart(newData)
      }
    }, { deep: true })

    function initChart() {
      if (!chartContainer.value) return

      chart.value = echarts.init(chartContainer.value)

      // 窗口大小变化时重绘
      window.addEventListener('resize', handleResize)

      // 点击事件
      chart.value.on('click', (params) => {
        if (params.dataType === 'node' && params.name) {
          emit('node-click', params.name)
        }
      })

      if (props.graphData) {
        updateChart(props.graphData)
      }
    }

    function handleResize() {
      if (chart.value) {
        chart.value.resize()
      }
    }

    function updateChart(data) {
      if (!chart.value || !data) return

      const option = {
        tooltip: {
          show: true,
          formatter: (params) => {
            if (params.dataType === 'node') {
              const appearCount = params.data.appearCount || 0
              const degree = params.data.value || 0
              return `<strong>${params.name}</strong><br/>
                      出现次数：${appearCount}<br/>
                      关联人物：${degree}`
            } else if (params.dataType === 'edge') {
              return `${params.data.source} ↔ ${params.data.target}<br/>互动次数：${params.data.value || 0}`
            }
            return ''
          }
        },
        legend: [{
          show: false
        }],
        series: [
          {
            type: 'graph',
            layout: 'force',
            data: data.nodes || [],
            links: data.links || [],
            roam: true,
            label: {
              show: true,
              position: 'right',
              formatter: '{b}',
              fontSize: 12,
              color: '#333'
            },
            force: {
              repulsion: 300,
              edgeLength: [50, 150],
              gravity: 0.1
            },
            draggable: true,
            emphasis: {
              focus: 'adjacency',
              lineStyle: {
                width: 4,
                opacity: 0.8
              }
            },
            lineStyle: {
              color: 'source',
              curveness: 0.3,
              width: 2,
              opacity: 0.7
            }
          }
        ]
      }

      chart.value.setOption(option, true)
    }

    return {
      chartContainer
    }
  }
}
</script>

<style scoped>
.chart-container {
  width: 100%;
  height: 100%;
}
</style>
