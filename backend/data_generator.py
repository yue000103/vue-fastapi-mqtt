import asyncio
import threading
import time
import random
from datetime import datetime

class DataGenerator:
    """随机数据生成器类，每秒生成一个随机数并通过MQTT发布"""
    
    def __init__(self, mqtt_publisher):
        self.mqtt_publisher = mqtt_publisher
        self.is_running = False
        self.generated_count = 0
        self._thread = None
        self._stop_event = threading.Event()
        
    def start(self):
        """启动数据生成器"""
        if self.is_running:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ 数据生成器已在运行")
            return
        
        self.is_running = True
        self.generated_count = 0
        self._stop_event.clear()
        
        # 在新线程中运行数据生成
        self._thread = threading.Thread(target=self._generate_data_loop, daemon=True)
        self._thread.start()
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🚀 数据生成器启动成功")
    
    def stop(self):
        """停止数据生成器"""
        if not self.is_running:
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⚠️ 数据生成器未在运行")
            return
        
        self.is_running = False
        self._stop_event.set()
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=2)
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ⏹️ 数据生成器已停止")
    
    def _generate_data_loop(self):
        """数据生成循环 - 在单独线程中运行"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🔄 开始生成随机数据...")
        
        while not self._stop_event.is_set():
            try:
                # 生成随机数据 (0-100)，符合开发文档要求
                value = round(random.uniform(0, 100), 2)
                timestamp = datetime.now().isoformat()
                
                # 创建数据对象
                data = {
                    "timestamp": timestamp,
                    "value": value
                }
                
                # 异步发布数据
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                
                try:
                    success = loop.run_until_complete(self.mqtt_publisher.publish_data(data))
                    if success:
                        self.generated_count += 1
                        # 每10条数据打印一次状态，避免日志过多
                        if self.generated_count % 10 == 0:
                            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 📊 已生成 {self.generated_count} 条数据")
                except Exception as e:
                    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 发布数据失败: {e}")
                finally:
                    loop.close()
                
                # 等待1秒，如果收到停止信号则提前退出
                if self._stop_event.wait(1):
                    break
                    
            except Exception as e:
                print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ❌ 生成数据时出错: {e}")
                time.sleep(1)  # 出错时等待1秒后继续
        
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] 🏁 数据生成循环结束，总共生成 {self.generated_count} 条数据")
    
    def get_stats(self):
        """获取统计信息"""
        return {
            "is_running": self.is_running,
            "generated_count": self.generated_count,
            "start_time": getattr(self, 'start_time', None)
        }