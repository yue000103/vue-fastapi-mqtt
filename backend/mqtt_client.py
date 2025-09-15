import paho.mqtt.client as mqtt
import json
import asyncio
from datetime import datetime
import threading
import time

class MQTTPublisher:
    """MQTT发布器类，负责连接MQTT服务器并发布数据"""
    
    def __init__(self):
        # MQTT配置 - 使用与现有代码相同的配置
        self.broker_host = "broker.emqx.io"
        self.broker_port = 1883
        self.client_id = "fastapi_publisher_" + str(int(time.time()))
        self.topic = "data/random"  # 根据开发文档要求
        
        self.client = None
        self.is_connected = False
        self._loop = None
        self._thread = None
        
    async def connect(self):
        """连接到MQTT服务器"""
        try:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔌 连接MQTT服务器: {self.broker_host}:{self.broker_port}")
            
            # 在新线程中运行MQTT客户端
            self._thread = threading.Thread(target=self._run_mqtt_client, daemon=True)
            self._thread.start()
            
            # 等待连接建立
            timeout = 10
            while not self.is_connected and timeout > 0:
                await asyncio.sleep(0.1)
                timeout -= 0.1
            
            if self.is_connected:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ MQTT连接成功")
                return True
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ MQTT连接超时")
                return False
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ MQTT连接错误: {e}")
            return False
    
    def _run_mqtt_client(self):
        """在单独线程中运行MQTT客户端"""
        self.client = mqtt.Client(client_id=self.client_id)
        
        # 设置回调函数
        self.client.on_connect = self._on_connect
        self.client.on_disconnect = self._on_disconnect
        self.client.on_publish = self._on_publish
        
        try:
            # 连接到broker
            self.client.connect(self.broker_host, self.broker_port, 60)
            
            # 开始循环
            self.client.loop_forever()
            
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ MQTT客户端错误: {e}")
    
    def _on_connect(self, client, userdata, flags, rc):
        """连接回调函数"""
        if rc == 0:
            self.is_connected = True
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ MQTT连接建立成功")
        else:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ MQTT连接失败，错误码: {rc}")
    
    def _on_disconnect(self, client, userdata, rc):
        """断开连接回调函数"""
        self.is_connected = False
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔌 MQTT连接断开")
    
    def _on_publish(self, client, userdata, mid):
        """消息发布回调函数"""
        pass  # 不打印每次发布的日志，避免太多输出
    
    async def publish_data(self, data):
        """发布数据到MQTT"""
        if not self.is_connected or not self.client:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ MQTT未连接，无法发布数据")
            return False
        
        try:
            # 确保数据格式符合开发文档要求
            message = {
                "timestamp": data.get("timestamp", datetime.now().isoformat()),
                "value": data.get("value", 0)
            }
            
            # 转换为JSON字符串
            json_message = json.dumps(message, ensure_ascii=False)
            
            # 发布消息
            result = self.client.publish(self.topic, json_message, qos=0)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                return True
            else:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 发布失败，错误码: {result.rc}")
                return False
                
        except Exception as e:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 发布数据时出错: {e}")
            return False
    
    async def disconnect(self):
        """断开MQTT连接"""
        if self.client:
            self.is_connected = False
            self.client.loop_stop()
            self.client.disconnect()
            
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
            
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔌 MQTT连接已断开")