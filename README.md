# 实时数据采集系统

基于Vue + FastAPI + MQTT的实时数据采集和可视化系统，实现后端持续生成随机数据，前端实时接收并绘制时间序列图表。

## 🚀 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- 网络连接（用于连接公共MQTT服务器）

### 启动方式

#### Windows用户
1. 双击 `start_backend.bat` 启动后端服务
2. 双击 `start_frontend.bat` 启动前端服务
3. 打开浏览器访问 http://localhost:3000

#### 手动启动

**启动后端:**
```bash
cd backend
pip install -r requirements.txt
python main.py
```

**启动前端:**
```bash
cd frontend  
npm install
npm run dev
```

## 📋 功能特性

### 后端功能 (FastAPI)
- ✅ **数据生成器**: 每秒生成一个随机数 (0-100)
- ✅ **MQTT发布器**: 连接到 broker.emqx.io 并发布数据到 `data/random` 主题
- ✅ **RESTful API**: 提供系统状态和健康检查接口
- ✅ **自动重连**: MQTT连接断开时自动重连
- ✅ **持续运行**: 独立于前端状态持续生成数据

### 前端功能 (Vue 3)
- ✅ **实时图表**: 使用Chart.js绘制实时时间序列图
- ✅ **控制面板**: 开始/暂停/继续/重新开始按钮
- ✅ **MQTT客户端**: WebSocket连接到MQTT服务器
- ✅ **数据管理**: 保持最近5分钟数据 (300个数据点)
- ✅ **状态监控**: 显示连接状态、数据统计等信息
- ✅ **响应式设计**: 支持桌面和移动设备

### 控制逻辑
- **开始**: 连接MQTT并开始接收和显示数据
- **暂停**: 暂停图表更新 (后端继续生成，前端暂停接收)
- **继续**: 恢复图表更新和数据接收  
- **重新开始**: 清空图表数据，重新开始接收

## 🏗️ 系统架构

```
[Vue前端:3000] <--MQTT--> [broker.emqx.io:8084] <--MQTT--> [FastAPI后端:8000]
    |                                                           |
[实时图表显示]                                            [随机数生成器]
[控制按钮]                                                [MQTT发布器]
```

## 📊 数据流程

1. **FastAPI后端** 每秒生成随机数据 (0-100)
2. 数据通过**MQTT**发布到公共服务器 `broker.emqx.io`
3. **Vue前端** 通过WebSocket连接MQTT服务器订阅数据  
4. 前端根据控制面板状态决定是否更新图表
5. 图表保持最近5分钟的历史数据

## 🌐 API接口

- `GET /` - 系统根路径和状态
- `GET /status` - 详细系统状态 
- `GET /health` - 健康检查

## 📁 项目结构

```
vue-fastapi-mqtt/
├── backend/                 # FastAPI后端
│   ├── main.py             # FastAPI应用入口  
│   ├── mqtt_client.py      # MQTT发布器
│   ├── data_generator.py   # 随机数生成器
│   └── requirements.txt    # Python依赖
├── frontend/               # Vue前端
│   ├── src/
│   │   ├── components/     # Vue组件
│   │   ├── services/       # MQTT服务
│   │   └── App.vue        # 主应用
│   ├── package.json       # Node.js依赖
│   └── vite.config.js     # Vite配置
├── start_backend.bat      # Windows后端启动脚本
├── start_frontend.bat     # Windows前端启动脚本
├── 开发文档.md            # 详细开发文档
└── README.md             # 项目说明
```

## 🔧 技术栈

- **后端**: FastAPI + Python + paho-mqtt
- **前端**: Vue 3 + Chart.js + MQTT.js + Vite
- **消息队列**: MQTT (broker.emqx.io)
- **数据传输**: WebSocket + MQTT协议

## 💡 使用说明

1. **首次使用**: 先启动后端，再启动前端
2. **数据接收**: 点击"开始"按钮连接MQTT并开始接收数据
3. **暂停接收**: 点击"暂停"暂停图表更新，后端继续生成数据
4. **继续接收**: 点击"继续"恢复数据接收和图表更新
5. **重新开始**: 点击"重新开始"清空数据并重新连接

## ❗ 注意事项

- 需要稳定的网络连接访问公共MQTT服务器
- 后端会持续生成数据，与前端状态无关
- 前端仅在"接收"状态时更新图表
- 图表最多显示最近5分钟的数据
- 系统支持自动重连功能

## 🐛 故障排除

**常见问题:**
1. **MQTT连接失败**: 检查网络连接，确保能访问 broker.emqx.io
2. **端口占用**: 确保8000和3000端口未被占用
3. **依赖安装失败**: 检查Python/Node.js版本是否符合要求

**调试方法:**
- 查看浏览器控制台日志
- 查看后端控制台输出
- 检查MQTT服务器连接状态

---

📧 **技术支持**: 如遇问题请检查控制台日志或联系开发者
🎯 **项目目标**: 演示实时数据采集和可视化的完整解决方案