<template>
  <div class="app">
    <header class="app-header">
      <div class="container">
        <h1>📊 实时数据采集系统</h1>
        <p>基于Vue + FastAPI + MQTT的实时数据可视化平台</p>
      </div>
    </header>

    <main class="app-main">
      <div class="container">
        <!-- 控制面板 -->
        <ControlPanel
          :mqtt-status="mqttStatus"
          :is-receiving="isReceiving"
          :total-messages="chartData.length"
          @start="handleStart"
          @pause="handlePause"
          @resume="handleResume"
          @restart="handleRestart"
        />

        <!-- 实时图表 -->
        <DataChart
          :data="chartData"
          :is-active="isReceiving"
          ref="dataChart"
        />

        <!-- 消息日志（可选显示） -->
        <div v-if="showMessageLog" class="message-log">
          <div class="log-header">
            <h3>📨 消息日志</h3>
            <button @click="toggleMessageLog" class="toggle-btn">
              {{ showMessageLog ? '隐藏日志' : '显示日志' }}
            </button>
          </div>
          <div class="log-content">
            <div v-if="recentMessages.length === 0" class="no-messages">
              暂无消息记录
            </div>
            <div
              v-for="(message, index) in recentMessages"
              :key="index"
              class="log-message"
            >
              <span class="message-time">{{ formatLogTime(message.timestamp) }}</span>
              <span class="message-value">数值: {{ message.value }}</span>
            </div>
          </div>
        </div>
      </div>
    </main>

    <footer class="app-footer">
      <div class="container">
        <p>&copy; 2025 实时数据采集系统 | 技术栈: Vue 3 + FastAPI + MQTT + Chart.js</p>
      </div>
    </footer>

    <!-- 连接状态提示 -->
    <div v-if="connectionError" class="error-toast">
      <span class="error-icon">❌</span>
      <span class="error-message">{{ connectionError }}</span>
      <button @click="dismissError" class="dismiss-btn">×</button>
    </div>
  </div>
</template>

<script>
import DataChart from './components/DataChart.vue'
import ControlPanel from './components/ControlPanel.vue'
import { MQTTClient } from './services/mqtt.js'

export default {
  name: 'App',
  components: {
    DataChart,
    ControlPanel
  },
  data() {
    return {
      mqttClient: null,
      mqttStatus: {
        isConnected: false,
        isConnecting: false,
        clientId: null
      },
      isReceiving: false,
      chartData: [],
      recentMessages: [],
      connectionError: null,
      showMessageLog: false,
      maxDataPoints: 300, // 5分钟数据
      maxLogMessages: 50   // 最近50条日志
    }
  },
  mounted() {
    // 延迟初始化，确保CDN脚本已加载
    setTimeout(() => {
      this.initMQTTClient()
    }, 100)
  },
  beforeUnmount() {
    this.cleanup()
  },
  methods: {
    // 初始化MQTT客户端
    initMQTTClient() {
      try {
        this.mqttClient = new MQTTClient()
        console.log('✅ MQTT客户端创建成功')
        
        // 设置MQTT回调函数
        this.mqttClient.setCallbacks({
        onConnect: () => {
          this.mqttStatus.isConnected = true
          this.mqttStatus.isConnecting = false
          this.mqttStatus.clientId = this.mqttClient.clientId
          this.connectionError = null
          console.log('✅ MQTT连接建立成功')
        },
        onDisconnect: () => {
          this.mqttStatus.isConnected = false
          this.mqttStatus.isConnecting = false
          this.isReceiving = false
          console.log('🔌 MQTT连接已断开')
        },
        onMessage: (topic, data) => {
          if (this.isReceiving) {
            this.handleNewData(data)
          }
        },
        onError: (error) => {
          this.mqttStatus.isConnecting = false
          this.connectionError = `连接失败: ${error.message}`
          console.error('❌ MQTT连接错误:', error)
        }
      })
      } catch (error) {
        console.error('❌ MQTT客户端初始化失败:', error)
        this.connectionError = `初始化失败: ${error.message}`
      }
    },

    // 处理新数据
    handleNewData(data) {
      try {
        // 添加到图表数据
        this.chartData.push({
          timestamp: data.timestamp,
          value: data.value
        })

        // 限制数据点数量
        if (this.chartData.length > this.maxDataPoints) {
          this.chartData = this.chartData.slice(-this.maxDataPoints)
        }

        // 添加到消息日志
        this.recentMessages.unshift({
          timestamp: data.timestamp,
          value: data.value
        })

        // 限制日志消息数量
        if (this.recentMessages.length > this.maxLogMessages) {
          this.recentMessages = this.recentMessages.slice(0, this.maxLogMessages)
        }

      } catch (error) {
        console.error('❌ 处理数据时出错:', error)
      }
    },

    // 控制面板事件处理
    async handleStart() {
      try {
        this.mqttStatus.isConnecting = true
        this.connectionError = null

        // 检查MQTT客户端是否正确初始化
        if (!this.mqttClient) {
          console.log('🔄 重新初始化MQTT客户端...')
          this.initMQTTClient()
        }

        if (!this.mqttClient) {
          throw new Error('MQTT客户端初始化失败')
        }

        await this.mqttClient.connect()
        await this.mqttClient.subscribe()
        
        this.isReceiving = true
        console.log('🚀 开始接收数据')

      } catch (error) {
        this.connectionError = `启动失败: ${error.message}`
        console.error('❌ 启动失败:', error)
      }
    },

    handlePause() {
      this.isReceiving = false
      this.mqttClient.disconnect()
      console.log('⏸️ 暂停接收数据')
    },

    handleResume() {
      this.handleStart()
    },

    async handleRestart() {
      try {
        console.log('🔄 重新开始...')
        
        // 停止接收
        this.isReceiving = false
        
        // 清空数据
        this.chartData = []
        this.recentMessages = []
        
        // 清空图表
        if (this.$refs.dataChart) {
          this.$refs.dataChart.clearChart()
        }

        // 重新连接并开始
        if (this.mqttStatus.isConnected) {
          await this.mqttClient.unsubscribe()
          this.mqttClient.disconnect()
        }

        // 稍等片刻后重新连接
        setTimeout(async () => {
          await this.handleStart()
        }, 1000)

      } catch (error) {
        this.connectionError = `重启失败: ${error.message}`
        console.error('❌ 重启失败:', error)
      }
    },

    // 切换消息日志显示
    toggleMessageLog() {
      this.showMessageLog = !this.showMessageLog
    },

    // 格式化日志时间
    formatLogTime(timestamp) {
      const date = new Date(timestamp)
      return date.toLocaleTimeString('zh-CN', { hour12: false })
    },

    // 关闭错误提示
    dismissError() {
      this.connectionError = null
    },

    // 清理资源
    cleanup() {
      if (this.mqttClient) {
        this.mqttClient.disconnect()
      }
    }
  }
}
</script>

<style scoped>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

.app {
  min-height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  display: flex;
  flex-direction: column;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 20px;
  width: 100%;
}

/* 头部样式 */
.app-header {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
  padding: 20px 0;
  text-align: center;
  color: white;
}

.app-header h1 {
  font-size: 2.5rem;
  font-weight: bold;
  margin-bottom: 8px;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
}

.app-header p {
  font-size: 1.1rem;
  opacity: 0.9;
  text-shadow: 1px 1px 2px rgba(0, 0, 0, 0.3);
}

/* 主体样式 */
.app-main {
  flex: 1;
  padding: 30px 0;
}

/* 消息日志样式 */
.message-log {
  background: white;
  border-radius: 12px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow: hidden;
  margin-top: 20px;
}

.log-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 25px;
  border-bottom: 1px solid #f0f0f0;
  background: #f8f9fa;
}

.log-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.toggle-btn {
  background: #007bff;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.toggle-btn:hover {
  background: #0056b3;
}

.log-content {
  max-height: 300px;
  overflow-y: auto;
  padding: 20px 25px;
}

.no-messages {
  text-align: center;
  color: #666;
  font-style: italic;
  padding: 20px;
}

.log-message {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  margin-bottom: 8px;
  background: #f8f9fa;
  border-radius: 6px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
}

.message-time {
  color: #666;
  font-size: 12px;
}

.message-value {
  color: #007bff;
  font-weight: bold;
}

/* 底部样式 */
.app-footer {
  background: rgba(0, 0, 0, 0.2);
  color: white;
  text-align: center;
  padding: 20px 0;
  backdrop-filter: blur(10px);
}

.app-footer p {
  font-size: 14px;
  opacity: 0.8;
}

/* 错误提示样式 */
.error-toast {
  position: fixed;
  top: 20px;
  right: 20px;
  background: #dc3545;
  color: white;
  padding: 15px 20px;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(220, 53, 69, 0.3);
  display: flex;
  align-items: center;
  gap: 10px;
  max-width: 400px;
  z-index: 1000;
  animation: slideInRight 0.3s ease;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

.error-icon {
  font-size: 18px;
}

.error-message {
  flex: 1;
  font-size: 14px;
}

.dismiss-btn {
  background: none;
  border: none;
  color: white;
  font-size: 20px;
  cursor: pointer;
  padding: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  transition: background 0.3s;
}

.dismiss-btn:hover {
  background: rgba(255, 255, 255, 0.2);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .container {
    padding: 0 15px;
  }

  .app-header h1 {
    font-size: 2rem;
  }

  .app-header p {
    font-size: 1rem;
  }

  .app-main {
    padding: 20px 0;
  }

  .error-toast {
    right: 10px;
    left: 10px;
    max-width: none;
  }
}
</style>