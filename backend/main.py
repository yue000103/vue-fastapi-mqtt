from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
from datetime import datetime
import uvicorn
from data_generator import DataGenerator
from mqtt_client import MQTTPublisher

app = FastAPI(title="实时数据采集系统", version="1.0.0")

# CORS 设置，允许前端访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 全局变量
data_generator = None
mqtt_publisher = None

@app.on_event("startup")
async def startup_event():
    """应用启动时初始化数据生成器和MQTT发布器"""
    global data_generator, mqtt_publisher
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 系统启动中...")
    
    # 创建MQTT发布器
    mqtt_publisher = MQTTPublisher()
    if await mqtt_publisher.connect():
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ MQTT连接成功")
        
        # 创建数据生成器并开始生成数据
        data_generator = DataGenerator(mqtt_publisher)
        data_generator.start()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 数据生成器已启动")
    else:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ MQTT连接失败")

@app.on_event("shutdown")
async def shutdown_event():
    """应用关闭时清理资源"""
    global data_generator, mqtt_publisher
    
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🛑 系统关闭中...")
    
    if data_generator:
        data_generator.stop()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏹️ 数据生成器已停止")
    
    if mqtt_publisher:
        await mqtt_publisher.disconnect()
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔌 MQTT连接已断开")

@app.get("/")
async def root():
    """根路径，返回系统状态"""
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    return {
        "message": "实时数据采集系统",
        "time": current_time,
        "status": "running" if data_generator and data_generator.is_running else "stopped",
        "mqtt_connected": mqtt_publisher.is_connected if mqtt_publisher else False
    }

@app.get("/status")
async def get_status():
    """获取系统状态"""
    return {
        "timestamp": datetime.now().isoformat(),
        "data_generator_running": data_generator.is_running if data_generator else False,
        "mqtt_connected": mqtt_publisher.is_connected if mqtt_publisher else False,
        "generated_count": data_generator.generated_count if data_generator else 0
    }

@app.get("/health")
async def health_check():
    """健康检查端点"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 实时数据采集系统 - FastAPI后端")
    print("📊 每秒生成随机数据并通过MQTT发布")
    print("🔌 MQTT服务器: broker.emqx.io:1883")
    print("📡 数据主题: data/random")
    print("=" * 60)
    
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8008,
        reload=True,
        log_level="info"
    )