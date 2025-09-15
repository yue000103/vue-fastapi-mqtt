import paho.mqtt.client as mqtt
import time
import json
from datetime import datetime

# MQTT 配置
BROKER_HOST = "broker.emqx.io"
BROKER_PORT = 1883
TOPIC = "test_0912"
CLIENT_ID = "python_subscriber_test"

def on_connect(client, userdata, flags, rc):
    """连接回调函数"""
    if rc == 0:
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 连接成功！")
        print(f"订阅主题: {TOPIC}")
        client.subscribe(TOPIC)
    else:
        print(f"连接失败，错误码: {rc}")

def on_message(client, userdata, msg):
    """消息接收回调函数"""
    try:
        topic = msg.topic
        payload = msg.payload.decode('utf-8')
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n[{timestamp}] 收到消息:")
        print(f"  主题: {topic}")
        print(f"  内容: {payload}")
        print(f"  QoS: {msg.qos}")
        print("-" * 50)
        
        # 尝试解析JSON格式的消息
        try:
            json_data = json.loads(payload)
            print(f"  JSON解析: {json.dumps(json_data, indent=2, ensure_ascii=False)}")
        except json.JSONDecodeError:
            print(f"  原始文本: {payload}")
            
    except Exception as e:
        print(f"处理消息时出错: {e}")

def on_disconnect(client, userdata, rc):
    """断开连接回调函数"""
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 连接断开")

def main():
    """主函数"""
    print("MQTT订阅者测试程序")
    print(f"服务器: {BROKER_HOST}:{BROKER_PORT}")
    print(f"主题: {TOPIC}")
    print(f"客户端ID: {CLIENT_ID}")
    print("=" * 50)
    
    # 创建MQTT客户端
    client = mqtt.Client(client_id=CLIENT_ID)
    
    # 设置回调函数
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect
    
    try:
        # 连接到broker
        print("正在连接到MQTT服务器...")
        client.connect(BROKER_HOST, BROKER_PORT, 60)
        
        # 开始循环监听
        print("开始监听消息... (按Ctrl+C退出)")
        client.loop_forever()
        
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        print(f"发生错误: {e}")
    finally:
        client.disconnect()
        print("程序结束")

if __name__ == "__main__":
    main()