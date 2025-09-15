import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime
import threading
import random

# MQTT 配置
BROKER_HOST = "broker.emqx.io"
BROKER_PORT = 1883
CLIENT_ID = "python_publisher_test"

class MQTTPublisher:
    def __init__(self):
        self.client = mqtt.Client(client_id=CLIENT_ID)
        self.is_connected = False
        self.setup_callbacks()
    
    def setup_callbacks(self):
        """设置回调函数"""
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
    
    def on_connect(self, client, userdata, flags, rc):
        """连接回调函数"""
        if rc == 0:
            self.is_connected = True
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ✅ 连接成功！")
        else:
            print(f"❌ 连接失败，错误码: {rc}")
    
    def on_disconnect(self, client, userdata, rc):
        """断开连接回调函数"""
        self.is_connected = False
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔌 连接断开")
    
    def on_publish(self, client, userdata, mid):
        """消息发布回调函数"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📤 消息发布成功 (ID: {mid})")
    
    def connect(self):
        """连接到MQTT服务器"""
        try:
            print(f"正在连接到 {BROKER_HOST}:{BROKER_PORT}...")
            self.client.connect(BROKER_HOST, BROKER_PORT, 60)
            self.client.loop_start()
            
            # 等待连接建立
            timeout = 10
            while not self.is_connected and timeout > 0:
                time.sleep(0.1)
                timeout -= 0.1
            
            if not self.is_connected:
                print("❌ 连接超时")
                return False
            
            return True
        except Exception as e:
            print(f"❌ 连接错误: {e}")
            return False
    
    def disconnect(self):
        """断开连接"""
        self.client.loop_stop()
        self.client.disconnect()
    
    def publish_message(self, topic, message, qos=0):
        """发布消息"""
        if not self.is_connected:
            print("❌ 未连接到服务器")
            return False
        
        try:
            # 如果消息是字典，转换为JSON字符串
            if isinstance(message, dict):
                message = json.dumps(message, ensure_ascii=False)
            
            result = self.client.publish(topic, message, qos)
            
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📤 发送消息:")
                print(f"  主题: {topic}")
                print(f"  内容: {message}")
                print(f"  QoS: {qos}")
                print("-" * 50)
                return True
            else:
                print(f"❌ 发布失败，错误码: {result.rc}")
                return False
        except Exception as e:
            print(f"❌ 发布消息时出错: {e}")
            return False
    
    def publish_json_message(self, topic, data, qos=0):
        """发布JSON格式消息"""
        json_message = {
            "timestamp": datetime.now().isoformat(),
            "data": data
        }
        return self.publish_message(topic, json_message, qos)
    
    def start_auto_publish(self, topic, interval=5):
        """开始自动发布测试消息"""
        def auto_publish():
            counter = 1
            while self.is_connected:
                # 模拟传感器数据
                sensor_data = {
                    "id": counter,
                    "temperature": round(random.uniform(20.0, 30.0), 2),
                    "humidity": round(random.uniform(40.0, 80.0), 2),
                    "status": random.choice(["正常", "警告", "异常"]),
                    "location": "传感器_001"
                }
                
                self.publish_json_message(topic, sensor_data)
                counter += 1
                time.sleep(interval)
        
        thread = threading.Thread(target=auto_publish, daemon=True)
        thread.start()
        print(f"🔄 开始自动发布到主题 '{topic}'，间隔 {interval} 秒")

def interactive_mode():
    """交互模式"""
    publisher = MQTTPublisher()
    
    print("=" * 60)
    print("🚀 MQTT 发布者测试程序")
    print(f"服务器: {BROKER_HOST}:{BROKER_PORT}")
    print("=" * 60)
    
    if not publisher.connect():
        return
    
    try:
        while True:
            print("\n📋 选择操作:")
            print("1. 发布单条消息")
            print("2. 发布JSON消息")
            print("3. 开始自动发布")
            print("4. 退出程序")
            
            choice = input("请输入选择 (1-4): ").strip()
            
            if choice == "1":
                topic = input("请输入主题: ").strip() or "test_0912"
                message = input("请输入消息内容: ").strip() or "Hello from Python!"
                publisher.publish_message(topic, message)
            
            elif choice == "2":
                topic = input("请输入主题: ").strip() or "test_0912"
                print("请输入JSON数据 (直接回车使用默认数据):")
                json_input = input().strip()
                
                if json_input:
                    try:
                        data = json.loads(json_input)
                    except json.JSONDecodeError:
                        print("❌ JSON格式错误")
                        continue
                else:
                    data = {
                        "message": "Hello from Python!",
                        "type": "test",
                        "value": random.randint(1, 100)
                    }
                
                publisher.publish_json_message(topic, data)
            
            elif choice == "3":
                topic = input("请输入主题: ").strip() or "test_0912"
                interval = input("请输入发布间隔(秒，默认5): ").strip()
                interval = int(interval) if interval.isdigit() else 5
                
                publisher.start_auto_publish(topic, interval)
                print("按任意键停止自动发布...")
                input()
                print("⏹️ 停止自动发布")
            
            elif choice == "4":
                break
            
            else:
                print("❌ 无效选择，请重新输入")
    
    except KeyboardInterrupt:
        print("\n\n⏹️ 程序被用户中断")
    
    finally:
        publisher.disconnect()
        print("👋 程序结束")

def quick_test():
    """快速测试函数"""
    publisher = MQTTPublisher()
    
    if publisher.connect():
        # 发送几条测试消息
        test_messages = [
            ("test_0912", "Hello from Python Publisher!"),
            ("test_0912", {"message": "JSON测试", "number": 42, "status": "success"}),
            ("test_0912", f"当前时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        ]
        
        for topic, message in test_messages:
            publisher.publish_message(topic, message)
            time.sleep(1)
        
        publisher.disconnect()

if __name__ == "__main__":
    # 可以选择运行模式
    print("请选择运行模式:")
    print("1. 交互模式 (推荐)")
    print("2. 快速测试")
    
    mode = input("请输入选择 (1-2): ").strip()
    
    if mode == "2":
        quick_test()
    else:
        interactive_mode()