// 使用全局的mqtt对象（从CDN加载）
export class MQTTClient {
    constructor() {
        // 检查MQTT是否已加载
        if (!window.mqtt) {
            throw new Error('MQTT库未加载，请确保CDN脚本已正确加载')
        }
        this.client = null
        this.isConnected = false
        this.isConnecting = false
        this.brokerUrl = 'wss://broker.emqx.io:8084/mqtt'
        this.clientId = 'vue_client_' + Math.random().toString(16).substr(2, 8)
        this.topic = 'data/random' // 与后端发布的主题一致
        this.callbacks = {
            onConnect: null,
            onDisconnect: null,
            onMessage: null,
            onError: null
        }
    }

    // 设置回调函数
    setCallbacks(callbacks) {
        this.callbacks = { ...this.callbacks, ...callbacks }
    }

    // 连接到MQTT服务器
    connect() {
        if (this.isConnected || this.isConnecting) {
            console.warn('MQTT客户端已连接或正在连接中')
            return Promise.resolve()
        }

        return new Promise((resolve, reject) => {
            this.isConnecting = true
            console.log('连接到MQTT服务器:', this.brokerUrl)

            try {
                // 检查全局mqtt是否正确加载
                console.log('全局MQTT库状态:', window.mqtt)
                if (!window.mqtt || typeof window.mqtt.connect !== 'function') {
                    throw new Error('MQTT库未正确加载，请确保CDN已加载')
                }
                
                this.client = window.mqtt.connect(this.brokerUrl, {
                    clientId: this.clientId,
                    clean: true,
                    connectTimeout: 4000,
                    reconnectPeriod: 1000,
                })

                this.client.on('connect', () => {
                    console.log('✅ MQTT连接成功')
                    this.isConnected = true
                    this.isConnecting = false
                    
                    if (this.callbacks.onConnect) {
                        this.callbacks.onConnect()
                    }
                    resolve()
                })

                this.client.on('error', (error) => {
                    console.error('❌ MQTT连接错误:', error)
                    this.isConnecting = false
                    
                    if (this.callbacks.onError) {
                        this.callbacks.onError(error)
                    }
                    reject(error)
                })

                this.client.on('message', (topic, payload) => {
                    try {
                        const message = payload.toString()
                        console.log('📨 收到MQTT消息:', { topic, message })
                        
                        // 解析JSON数据
                        const data = JSON.parse(message)
                        
                        if (this.callbacks.onMessage) {
                            this.callbacks.onMessage(topic, data)
                        }
                    } catch (error) {
                        console.error('❌ 解析消息失败:', error)
                    }
                })

                this.client.on('disconnect', () => {
                    console.log('🔌 MQTT连接断开')
                    this.isConnected = false
                    this.isConnecting = false
                    
                    if (this.callbacks.onDisconnect) {
                        this.callbacks.onDisconnect()
                    }
                })

            } catch (error) {
                console.error('❌ 创建MQTT客户端失败:', error)
                this.isConnecting = false
                reject(error)
            }
        })
    }

    // 订阅主题
    subscribe() {
        if (!this.isConnected || !this.client) {
            console.error('❌ MQTT未连接，无法订阅')
            return Promise.reject(new Error('MQTT未连接'))
        }

        return new Promise((resolve, reject) => {
            this.client.subscribe(this.topic, (error) => {
                if (error) {
                    console.error('❌ 订阅失败:', error)
                    reject(error)
                } else {
                    console.log('✅ 订阅成功:', this.topic)
                    resolve()
                }
            })
        })
    }

    // 取消订阅
    unsubscribe() {
        if (!this.isConnected || !this.client) {
            return Promise.resolve()
        }

        return new Promise((resolve) => {
            this.client.unsubscribe(this.topic, (error) => {
                if (error) {
                    console.error('❌ 取消订阅失败:', error)
                } else {
                    console.log('✅ 取消订阅成功:', this.topic)
                }
                resolve()
            })
        })
    }

    // 断开连接
    disconnect() {
        if (this.client) {
            this.client.end()
            this.client = null
        }
        this.isConnected = false
        this.isConnecting = false
        console.log('🔌 MQTT客户端已断开')
    }

    // 获取连接状态
    getStatus() {
        return {
            isConnected: this.isConnected,
            isConnecting: this.isConnecting,
            clientId: this.clientId,
            topic: this.topic
        }
    }
}