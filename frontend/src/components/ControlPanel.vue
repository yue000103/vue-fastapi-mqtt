<template>
  <div class="control-panel">
    <div class="status-section">
      <h3>📊 系统状态</h3>
      <div class="status-grid">
        <div class="status-item">
          <span class="status-label">MQTT连接:</span>
          <span :class="['status-value', mqttStatus.isConnected ? 'connected' : 'disconnected']">
            {{ mqttStatus.isConnected ? '✅ 已连接' : '❌ 未连接' }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">数据接收:</span>
          <span :class="['status-value', isReceiving ? 'receiving' : 'stopped']">
            {{ isReceiving ? '📊 接收中' : '⏹️ 已停止' }}
          </span>
        </div>
        <div class="status-item">
          <span class="status-label">接收数据:</span>
          <span class="status-value">{{ totalMessages }} 条</span>
        </div>
        <div class="status-item">
          <span class="status-label">运行时间:</span>
          <span class="status-value">{{ runningTime }}</span>
        </div>
      </div>
    </div>

    <div class="control-section">
      <h3>🎛️ 控制面板</h3>
      <div class="button-grid">
        <button 
          class="control-btn start-btn" 
          @click="handleStart"
          :disabled="mqttStatus.isConnecting || (mqttStatus.isConnected && isReceiving)"
        >
          <span class="btn-icon">▶️</span>
          {{ mqttStatus.isConnecting ? '连接中...' : '开始' }}
        </button>

        <button 
          class="control-btn pause-btn" 
          @click="handlePause"
          :disabled="!mqttStatus.isConnected || !isReceiving"
        >
          <span class="btn-icon">⏸️</span>
          暂停
        </button>

        <button 
          class="control-btn resume-btn" 
          @click="handleResume"
          :disabled="!mqttStatus.isConnected || isReceiving"
        >
          <span class="btn-icon">⏯️</span>
          继续
        </button>

        <button 
          class="control-btn restart-btn" 
          @click="handleRestart"
          :disabled="mqttStatus.isConnecting"
        >
          <span class="btn-icon">🔄</span>
          重新开始
        </button>
      </div>
    </div>

    <div class="info-section">
      <h3>ℹ️ 系统信息</h3>
      <div class="info-grid">
        <div class="info-item">
          <strong>MQTT服务器:</strong> broker.emqx.io:8084
        </div>
        <div class="info-item">
          <strong>订阅主题:</strong> data/random
        </div>
        <div class="info-item">
          <strong>客户端ID:</strong> {{ mqttStatus.clientId || '未连接' }}
        </div>
        <div class="info-item">
          <strong>数据频率:</strong> 每秒1次
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'ControlPanel',
  props: {
    mqttStatus: {
      type: Object,
      default: () => ({
        isConnected: false,
        isConnecting: false,
        clientId: null
      })
    },
    isReceiving: {
      type: Boolean,
      default: false
    },
    totalMessages: {
      type: Number,
      default: 0
    }
  },
  data() {
    return {
      startTime: null,
      runningTime: '00:00:00',
      timer: null
    }
  },
  methods: {
    handleStart() {
      this.$emit('start')
      this.startTimer()
    },

    handlePause() {
      this.$emit('pause')
    },

    handleResume() {
      this.$emit('resume')
    },

    handleRestart() {
      this.$emit('restart')
      this.resetTimer()
      this.startTimer()
    },

    startTimer() {
      if (this.timer) {
        clearInterval(this.timer)
      }
      
      this.startTime = new Date()
      this.timer = setInterval(() => {
        this.updateRunningTime()
      }, 1000)
    },

    resetTimer() {
      if (this.timer) {
        clearInterval(this.timer)
        this.timer = null
      }
      this.startTime = null
      this.runningTime = '00:00:00'
    },

    updateRunningTime() {
      if (!this.startTime) return
      
      const now = new Date()
      const diff = Math.floor((now - this.startTime) / 1000)
      
      const hours = Math.floor(diff / 3600)
      const minutes = Math.floor((diff % 3600) / 60)
      const seconds = diff % 60
      
      this.runningTime = `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
    }
  },

  beforeUnmount() {
    if (this.timer) {
      clearInterval(this.timer)
    }
  }
}
</script>

<style scoped>
.control-panel {
  background: white;
  border-radius: 12px;
  padding: 25px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
}

h3 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 18px;
  font-weight: bold;
  border-bottom: 2px solid #f0f0f0;
  padding-bottom: 8px;
}

.status-section,
.control-section,
.info-section {
  margin-bottom: 30px;
}

.status-section:last-child,
.control-section:last-child,
.info-section:last-child {
  margin-bottom: 0;
}

.status-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 15px;
}

.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px;
  background: #f8f9fa;
  border-radius: 8px;
  border-left: 4px solid #e9ecef;
}

.status-label {
  font-weight: 500;
  color: #666;
}

.status-value {
  font-weight: bold;
  font-size: 14px;
}

.status-value.connected {
  color: #28a745;
}

.status-value.disconnected {
  color: #dc3545;
}

.status-value.receiving {
  color: #007bff;
}

.status-value.stopped {
  color: #6c757d;
}

.button-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 15px;
}

.control-btn {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 14px 20px;
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: bold;
  cursor: pointer;
  transition: all 0.3s ease;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.control-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
}

.control-btn:active:not(:disabled) {
  transform: translateY(0);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
}

.start-btn {
  background: linear-gradient(45deg, #28a745, #20c997);
  color: white;
}

.pause-btn {
  background: linear-gradient(45deg, #ffc107, #fd7e14);
  color: white;
}

.resume-btn {
  background: linear-gradient(45deg, #007bff, #6610f2);
  color: white;
}

.restart-btn {
  background: linear-gradient(45deg, #dc3545, #e83e8c);
  color: white;
}

.btn-icon {
  font-size: 18px;
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 12px;
}

.info-item {
  padding: 10px 12px;
  background: #f8f9fa;
  border-radius: 6px;
  font-size: 14px;
  color: #555;
}

.info-item strong {
  color: #333;
}

@media (max-width: 768px) {
  .control-panel {
    padding: 20px;
  }
  
  .button-grid {
    grid-template-columns: 1fr 1fr;
  }
  
  .status-grid,
  .info-grid {
    grid-template-columns: 1fr;
  }
}
</style>