<template>
  <div class="chart-container">
    <h3 class="chart-title">📊 实时数据监控 (最近5分钟)</h3>
    <div class="chart-stats">
      <span class="stat-item">数据点: {{ displayData.length }}</span>
      <span class="stat-item" v-if="displayData.length > 0">
        最新值: {{ displayData[displayData.length - 1]?.value.toFixed(2) }}
      </span>
      <span class="stat-item" v-if="displayData.length > 0">
        最新时间: {{ formatTime(displayData[displayData.length - 1]?.timestamp) }}
      </span>
    </div>
    <div class="chart-wrapper">
      <svg ref="chartSvg" class="chart-svg"></svg>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import * as d3 from 'd3'

// Props
const props = defineProps({
  data: {
    type: Array,
    default: () => []
  },
  isActive: {
    type: Boolean,
    default: true
  }
})

// Refs
const chartSvg = ref(null)

// Data
const maxDataPoints = 300
const margin = { top: 20, right: 30, bottom: 40, left: 60 }
const width = 1100 - margin.left - margin.right
const height = 300 - margin.bottom - margin.top

// Computed
const displayData = computed(() => {
  return props.data.slice(-maxDataPoints)
})

// D3 相关变量
let svg, g, xScale, yScale, line, xAxis, yAxis, path, tooltip

// Methods
const formatTime = (timestamp) => {
  if (!timestamp) return ''
  const date = new Date(timestamp)
  return date.toLocaleTimeString('zh-CN', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit', 
    second: '2-digit'
  })
}

const initChart = () => {
  if (!chartSvg.value) return

  // 清除之前的内容
  d3.select(chartSvg.value).selectAll("*").remove()

  // 创建SVG
  svg = d3.select(chartSvg.value)
    .attr('width', width + margin.left + margin.right)
    .attr('height', height + margin.top + margin.bottom)

  // 创建主绘图区域
  g = svg.append('g')
    .attr('transform', `translate(${margin.left},${margin.top})`)

  // 创建比例尺
  xScale = d3.scaleTime()
    .range([0, width])

  yScale = d3.scaleLinear()
    .domain([0, 100])
    .range([height, 0])

  // 创建线条生成器
  line = d3.line()
    .x(d => xScale(new Date(d.timestamp)))
    .y(d => yScale(d.value))
    .curve(d3.curveMonotoneX)

  // 创建坐标轴
  xAxis = d3.axisBottom(xScale)
    .tickFormat(d3.timeFormat('%H:%M:%S'))
    .ticks(6)

  yAxis = d3.axisLeft(yScale)
    .ticks(5)

  // 添加坐标轴
  g.append('g')
    .attr('class', 'x-axis')
    .attr('transform', `translate(0,${height})`)

  g.append('g')
    .attr('class', 'y-axis')

  // 创建线条路径
  path = g.append('path')
    .attr('class', 'data-line')
    .attr('fill', 'none')
    .attr('stroke', '#2196F3')
    .attr('stroke-width', 2)

  // 创建渐变区域
  const gradient = svg.append('defs')
    .append('linearGradient')
    .attr('id', 'area-gradient')
    .attr('gradientUnits', 'userSpaceOnUse')
    .attr('x1', 0).attr('y1', height + margin.top)
    .attr('x2', 0).attr('y2', margin.top)

  gradient.append('stop')
    .attr('offset', '0%')
    .attr('stop-color', '#2196F3')
    .attr('stop-opacity', 0)

  gradient.append('stop')
    .attr('offset', '100%')
    .attr('stop-color', '#2196F3')
    .attr('stop-opacity', 0.3)

  // 创建面积生成器
  const area = d3.area()
    .x(d => xScale(new Date(d.timestamp)))
    .y0(height)
    .y1(d => yScale(d.value))
    .curve(d3.curveMonotoneX)

  // 添加面积路径
  g.append('path')
    .attr('class', 'data-area')
    .attr('fill', 'url(#area-gradient)')

  // 创建提示框
  tooltip = d3.select('body').append('div')
    .attr('class', 'd3-tooltip')
    .style('opacity', 0)
    .style('position', 'absolute')
    .style('background', 'rgba(0, 0, 0, 0.8)')
    .style('color', 'white')
    .style('padding', '8px')
    .style('border-radius', '4px')
    .style('font-size', '12px')
    .style('pointer-events', 'none')
    .style('z-index', '1000')

  console.log('✅ D3 图表初始化完成')
}

const updateChart = () => {
  if (!g || displayData.value.length === 0) return

  try {
    const data = displayData.value

    // 更新x轴域
    const timeExtent = d3.extent(data, d => new Date(d.timestamp))
    xScale.domain(timeExtent)

    // 更新坐标轴
    g.select('.x-axis')
      .transition()
      .duration(300)
      .call(xAxis)

    g.select('.y-axis')
      .transition()
      .duration(300)
      .call(yAxis)

    // 更新线条路径
    path
      .datum(data)
      .transition()
      .duration(300)
      .attr('d', line)

    // 更新面积路径
    const area = d3.area()
      .x(d => xScale(new Date(d.timestamp)))
      .y0(height)
      .y1(d => yScale(d.value))
      .curve(d3.curveMonotoneX)

    g.select('.data-area')
      .datum(data)
      .transition()
      .duration(300)
      .attr('d', area)

    // 更新数据点
    const circles = g.selectAll('.data-point')
      .data(data.slice(-50)) // 只显示最后50个点避免性能问题

    circles.exit().remove()

    circles.enter()
      .append('circle')
      .attr('class', 'data-point')
      .attr('r', 0)
      .attr('fill', '#2196F3')
      .attr('stroke', 'white')
      .attr('stroke-width', 2)
      .merge(circles)
      .transition()
      .duration(300)
      .attr('cx', d => xScale(new Date(d.timestamp)))
      .attr('cy', d => yScale(d.value))
      .attr('r', 3)

    // 添加鼠标交互
    g.selectAll('.data-point')
      .on('mouseover', function(event, d) {
        d3.select(this).attr('r', 5)
        tooltip.transition().duration(200).style('opacity', .9)
        tooltip.html(`时间: ${formatTime(d.timestamp)}<br/>数值: ${d.value.toFixed(2)}`)
          .style('left', (event.pageX + 10) + 'px')
          .style('top', (event.pageY - 28) + 'px')
      })
      .on('mouseout', function() {
        d3.select(this).attr('r', 3)
        tooltip.transition().duration(500).style('opacity', 0)
      })

  } catch (error) {
    console.warn('D3 图表更新失败:', error.message)
  }
}

const clearChart = () => {
  console.log('清除图表数据')
  if (g) {
    g.select('.data-line').attr('d', null)
    g.select('.data-area').attr('d', null)
    g.selectAll('.data-point').remove()
  }
}

const destroyChart = () => {
  if (tooltip) {
    tooltip.remove()
    tooltip = null
  }
  if (chartSvg.value) {
    d3.select(chartSvg.value).selectAll("*").remove()
  }
  svg = g = xScale = yScale = line = xAxis = yAxis = path = null
}

// Lifecycle hooks
onMounted(() => {
  nextTick(() => {
    initChart()
    if (displayData.value.length > 0) {
      updateChart()
    }
  })
})

onBeforeUnmount(() => {
  destroyChart()
})

// Watchers
watch(() => props.data, () => {
  if (props.isActive) {
    updateChart()
  }
}, { deep: true })

watch(() => props.isActive, (newValue) => {
  if (newValue) {
    nextTick(() => {
      updateChart()
    })
  }
})

// 暴露方法给父组件
defineExpose({
  clearChart,
  updateChart
})
</script>

<style scoped>
.chart-container {
  width: 100%;
  background: white;
  border-radius: 10px;
  padding: 20px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

.chart-title {
  margin: 0 0 15px 0;
  color: #333;
  font-size: 18px;
  font-weight: bold;
  text-align: center;
}

.chart-stats {
  display: flex;
  justify-content: space-around;
  margin-bottom: 20px;
  padding: 10px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 14px;
}

.stat-item {
  color: #666;
  font-weight: 500;
}

.stat-item:first-child {
  color: #2196F3;
  font-weight: bold;
}

.chart-wrapper {
  width: 100%;
  overflow: hidden;
}

.chart-svg {
  width: 100%;
  height: 340px;
  display: block;
}

/* D3 样式 */
:deep(.x-axis text),
:deep(.y-axis text) {
  font-size: 12px;
  fill: #666;
}

:deep(.x-axis path),
:deep(.y-axis path),
:deep(.x-axis line),
:deep(.y-axis line) {
  stroke: #ddd;
  stroke-width: 1;
}

:deep(.data-point) {
  cursor: pointer;
}

@media (max-width: 768px) {
  .chart-stats {
    flex-direction: column;
    gap: 5px;
    text-align: center;
  }
  
  .chart-svg {
    height: 280px;
  }
}
</style>