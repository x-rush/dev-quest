# 03 - 实时应用实战项目

## 目录

1. [项目概述](#项目概述)
2. [技术架构](#技术架构)
3. [项目结构](#项目结构)
4. [实时通信实现](#实时通信实现)
5. [状态同步策略](#状态同步策略)
6. [性能优化](#性能优化)
7. [错误处理](#错误处理)
8. [测试策略](#测试策略)
9. [部署配置](#部署配置)
10. [扩展功能](#扩展功能)
11. [总结](#总结)

## 项目概述

构建一个功能完整的实时协作应用，包含多人协作编辑、实时聊天、在线状态显示、文件共享等功能。

### 功能特性

- **多人协作编辑**: 实时文档协作，支持光标位置同步
- **实时聊天**: 群组聊天、私聊、文件分享
- **在线状态**: 用户在线状态、活跃度显示
- **实时通知**: 即时通知、推送消息
- **文件共享**: 实时文件上传、预览、同步
- **版本控制**: 文档版本历史、回滚功能
- **权限管理**: 细粒度权限控制
- **离线支持**: 离线编辑、冲突解决

### 与传统PHP实时应用的对比

**传统PHP实时应用：**
- 依赖轮询或长轮询
- 服务器资源消耗大
- 实时性较差
- 扩展性有限

**Next.js实时应用：**
- WebSocket全双工通信
- 事件驱动架构
- 高性能实时同步
- 水平扩展支持

## 技术架构

### 核心技术栈

```typescript
// package.json 核心依赖
{
  "dependencies": {
    "next": "15.0.0",
    "react": "19.0.0",
    "react-dom": "19.0.0",
    "typescript": "5.0.0",

    // 实时通信
    "socket.io-client": "^4.7.0",
    "socket.io": "^4.7.0",

    // 状态管理
    "zustand": "^4.4.0",
    "@tanstack/react-query": "^5.0.0",

    // 协作编辑
    "yjs": "^13.6.0",
    "y-websocket": "^1.5.0",
    "quill": "^1.3.7",
    "react-quill": "^2.0.0",

    // 文件处理
    "multer": "^1.4.5-lts.1",
    "sharp": "^0.32.0",

    // 推送通知
    "web-push": "^3.6.0",

    // 数据库
    "@prisma/client": "^5.0.0",
    "redis": "^4.6.0",

    // 认证
    "next-auth": "^4.24.0",
    "jsonwebtoken": "^9.0.0"
  }
}
```

### 架构设计

```typescript
// lib/socket/index.ts
import { Server } from "socket.io"
import { createAdapter } from "@socket.io/redis-adapter"
import { createClient } from "redis"
import jwt from "jsonwebtoken"

interface AuthenticatedSocket extends Socket {
  user?: {
    id: string
    email: string
    name: string
  }
}

export function setupSocketIO(server: any) {
  const io = new Server(server, {
    cors: {
      origin: process.env.NODE_ENV === "production" ? false : ["http://localhost:3000"],
      methods: ["GET", "POST"],
    },
    transports: ["websocket", "polling"],
  })

  // Redis adapter for horizontal scaling
  if (process.env.REDIS_URL) {
    const pubClient = createClient({ url: process.env.REDIS_URL })
    const subClient = pubClient.duplicate()

    io.adapter(createAdapter(pubClient, subClient))
  }

  // Authentication middleware
  io.use((socket: AuthenticatedSocket, next) => {
    const token = socket.handshake.auth.token

    if (!token) {
      return next(new Error("Authentication error"))
    }

    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET!)
      socket.user = decoded.user
      next()
    } catch (err) {
      next(new Error("Authentication error"))
    }
  })

  // Connection handler
  io.on("connection", (socket: AuthenticatedSocket) => {
    console.log(`User connected: ${socket.user?.id}`)

    // Join user to their personal room
    socket.join(`user:${socket.user?.id}`)

    // Handle room joining
    socket.on("join:room", (roomId: string) => {
      socket.join(`room:${roomId}`)
      socket.to(`room:${roomId}`).emit("user:joined", {
        userId: socket.user?.id,
        name: socket.user?.name,
      })
    })

    // Handle room leaving
    socket.on("leave:room", (roomId: string) => {
      socket.leave(`room:${roomId}`)
      socket.to(`room:${roomId}`).emit("user:left", {
        userId: socket.user?.id,
        name: socket.user?.name,
      })
    })

    // Handle document collaboration
    socket.on("doc:sync", (data: { docId: string; operations: any[] }) => {
      socket.to(`room:${data.docId}`).emit("doc:update", {
        operations: data.operations,
        userId: socket.user?.id,
        timestamp: Date.now(),
      })
    })

    // Handle chat messages
    socket.on("chat:message", (data: { roomId: string; message: string; type: 'text' | 'file' }) => {
      const messageData = {
        id: `msg_${Date.now()}`,
        userId: socket.user?.id,
        userName: socket.user?.name,
        message: data.message,
        type: data.type,
        timestamp: new Date().toISOString(),
        roomId: data.roomId,
      }

      io.to(`room:${data.roomId}`).emit("chat:new", messageData)

      // Save message to database
      saveMessageToDatabase(messageData)
    })

    // Handle typing indicators
    socket.on("typing:start", (data: { roomId: string }) => {
      socket.to(`room:${data.roomId}`).emit("user:typing", {
        userId: socket.user?.id,
        userName: socket.user?.name,
        isTyping: true,
      })
    })

    socket.on("typing:stop", (data: { roomId: string }) => {
      socket.to(`room:${data.roomId}`).emit("user:typing", {
        userId: socket.user?.id,
        userName: socket.user?.name,
        isTyping: false,
      })
    })

    // Handle file sharing
    socket.on("file:share", (data: { roomId: string; fileData: any }) => {
      const fileMessage = {
        id: `file_${Date.now()}`,
        userId: socket.user?.id,
        userName: socket.user?.name,
        type: 'file',
        fileData: data.fileData,
        timestamp: new Date().toISOString(),
        roomId: data.roomId,
      }

      io.to(`room:${data.roomId}`).emit("file:shared", fileMessage)
    })

    // Handle presence
    socket.on("presence:update", (data: { status: 'online' | 'away' | 'busy' }) => {
      io.emit("presence:changed", {
        userId: socket.user?.id,
        status: data.status,
        timestamp: Date.now(),
      })
    })

    // Handle disconnection
    socket.on("disconnect", () => {
      console.log(`User disconnected: ${socket.user?.id}`)
      io.emit("presence:changed", {
        userId: socket.user?.id,
        status: 'offline',
        timestamp: Date.now(),
      })
    })
  })

  return io
}

async function saveMessageToDatabase(messageData: any) {
  // Implementation for saving messages to database
}
```

## 项目结构

```
realtime-app/
├── app/
│   ├── (collab)/
│   │   ├── rooms/
│   │   ├── documents/
│   │   └── layout.tsx
│   ├── api/
│   │   ├── auth/
│   │   ├── socket/
│   │   ├── documents/
│   │   ├── files/
│   │   └── notifications/
│   ├── globals.css
│   └── layout.tsx
├── components/
│   ├── collaboration/
│   │   ├── editor/
│   │   ├── cursor-tracker.tsx
│   │   └── presence-indicator.tsx
│   ├── chat/
│   │   ├── chat-window.tsx
│   │   ├── message-list.tsx
│   │   └── message-input.tsx
│   ├── files/
│   │   ├── file-uploader.tsx
│   │   ├── file-preview.tsx
│   │   └── file-share.tsx
│   └── ui/
├── hooks/
│   ├── use-socket.ts
│   ├── use-collaboration.ts
│   ├── use-presence.ts
│   └── use-offline-support.ts
├── lib/
│   ├── socket/
│   ├── yjs/
│   ├── auth/
│   └── utils/
├── store/
│   ├── collaboration.ts
│   ├── chat.ts
│   └── presence.ts
├── types/
│   ├── collaboration.ts
│   ├── chat.ts
│   └── socket.ts
└── public/
```

## 实时通信实现

### 1. Socket.IO客户端集成

```typescript
// hooks/use-socket.ts
"use client"

import { useEffect, useRef, useCallback } from "react"
import { io, Socket } from "socket.io-client"
import { useSession } from "next-auth/react"

interface UseSocketOptions {
  autoConnect?: boolean
  reconnection?: boolean
  reconnectionAttempts?: number
  reconnectionDelay?: number
}

export function useSocket(options: UseSocketOptions = {}) {
  const { data: session } = useSession()
  const socketRef = useRef<Socket | null>(null)
  const reconnectAttempts = useRef(0)
  const maxReconnectAttempts = options.reconnectionAttempts || 5

  const connect = useCallback(() => {
    if (!session?.user) return

    if (socketRef.current?.connected) return

    const socket = io(process.env.NEXT_PUBLIC_SOCKET_URL!, {
      auth: {
        token: session.accessToken,
      },
      autoConnect: false,
      reconnection: options.reconnection ?? true,
      reconnectionAttempts: maxReconnectAttempts,
      reconnectionDelay: options.reconnectionDelay ?? 1000,
      transports: ["websocket", "polling"],
    })

    socketRef.current = socket

    // Connection event handlers
    socket.on("connect", () => {
      console.log("Socket connected")
      reconnectAttempts.current = 0
    })

    socket.on("disconnect", (reason) => {
      console.log("Socket disconnected:", reason)

      if (reason === "io server disconnect") {
        // Server initiated disconnect, don't reconnect
        socket.disconnect()
      }
    })

    socket.on("connect_error", (error) => {
      console.error("Socket connection error:", error)
      reconnectAttempts.current++

      if (reconnectAttempts.current >= maxReconnectAttempts) {
        console.error("Max reconnection attempts reached")
        socket.disconnect()
      }
    })

    // Connect the socket
    socket.connect()

    return socket
  }, [session, options, maxReconnectAttempts])

  const disconnect = useCallback(() => {
    if (socketRef.current) {
      socketRef.current.disconnect()
      socketRef.current = null
    }
  }, [])

  const joinRoom = useCallback((roomId: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit("join:room", roomId)
    }
  }, [])

  const leaveRoom = useCallback((roomId: string) => {
    if (socketRef.current?.connected) {
      socketRef.current.emit("leave:room", roomId)
    }
  }, [])

  useEffect(() => {
    if (options.autoConnect !== false && session?.user) {
      connect()
    }

    return () => {
      disconnect()
    }
  }, [connect, disconnect, options.autoConnect, session])

  return {
    socket: socketRef.current,
    connect,
    disconnect,
    joinRoom,
    leaveRoom,
    isConnected: socketRef.current?.connected || false,
  }
}
```

### 2. 协作编辑器实现

```typescript
// components/collaboration/editor/collaborative-editor.tsx
"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import dynamic from "next/dynamic"
import * as Y from "yjs"
import { WebsocketProvider } from "y-websocket"
import { QuillBinding } from "y-quill"
import { useSocket } from "@/hooks/use-socket"
import { useSession } from "next-auth/react"
import { CursorTracker } from "./cursor-tracker"
import { PresenceIndicator } from "./presence-indicator"

// 动态导入Quill编辑器
const ReactQuill = dynamic(() => import("react-quill"), { ssr: false })
import "react-quill/dist/quill.snow.css"

interface CollaborativeEditorProps {
  documentId: string
  initialContent?: string
  onContentChange?: (content: string) => void
}

export function CollaborativeEditor({
  documentId,
  initialContent,
  onContentChange,
}: CollaborativeEditorProps) {
  const { data: session } = useSession()
  const { socket, isConnected } = useSocket()
  const [editor, setEditor] = useState<any>(null)
  const [isConnectedToYjs, setIsConnectedToYjs] = useState(false)
  const ydocRef = useRef<Y.Doc | null>(null)
  const providerRef = useRef<WebsocketProvider | null>(null)
  const bindingRef = useRef<QuillBinding | null>(null)
  const quillRef = useRef<any>(null)

  // 初始化Y.js文档
  const initializeYjs = useCallback(() => {
    if (!session?.user || !documentId) return

    // 创建Y.js文档
    const ydoc = new Y.Doc()
    ydocRef.current = ydoc

    // 创建WebSocket provider
    const wsUrl = `${process.env.NEXT_PUBLIC_WS_URL}/document/${documentId}`
    const provider = new WebsocketProvider(wsUrl, documentId, ydoc, {
      WebSocketPolyfill: WebSocket,
    })

    providerRef.current = provider

    // 监听连接状态
    provider.on("status", (status: { connected: boolean }) => {
      setIsConnectedToYjs(status.connected)
    })

    // 监听用户加入/离开
    provider.awareness.on("change", (changes: any) => {
      const states = Array.from(provider.awareness.getStates().entries())
      // 处理用户状态变化
    })

    // 获取或创建文本类型
    const ytext = ydoc.getText("quill")

    // 等待Quill编辑器初始化
    if (quillRef.current) {
      const binding = new QuillBinding(ytext, quillRef.current.getEditor(), provider.awareness)
      bindingRef.current = binding
    }

    return () => {
      provider.destroy()
      ydoc.destroy()
    }
  }, [documentId, session])

  // 处理编辑器挂载
  const handleEditorMount = useCallback((quill: any) => {
    quillRef.current = quill

    // 配置Quill编辑器
    const toolbarOptions = [
      [{ header: [1, 2, 3, false] }],
      ["bold", "italic", "underline", "strike"],
      [{ color: [] }, { background: [] }],
      [{ list: "ordered" }, { list: "bullet" }],
      ["link", "image", "video"],
      ["clean"],
    ]

    quill.getModule("toolbar").addHandler("image", () => {
      // 处理图片插入
      insertImage()
    })

    // 设置初始内容
    if (initialContent) {
      quill.clipboard.dangerouslyPasteHTML(initialContent)
    }

    setEditor(quill)

    // 如果Y.js已经初始化，创建binding
    if (ydocRef.current && providerRef.current) {
      const ytext = ydocRef.current.getText("quill")
      const binding = new QuillBinding(ytext, quill, providerRef.current.awareness)
      bindingRef.current = binding
    }

    // 监听内容变化
    quill.on("text-change", () => {
      const content = quill.root.innerHTML
      onContentChange?.(content)
    })
  }, [initialContent, onContentChange])

  // 插入图片处理
  const insertImage = useCallback(() => {
    const input = document.createElement("input")
    input.setAttribute("type", "file")
    input.setAttribute("accept", "image/*")
    input.click()

    input.onchange = async () => {
      const file = input.files?.[0]
      if (!file) return

      try {
        // 上传图片
        const formData = new FormData()
        formData.append("file", file)
        formData.append("documentId", documentId)

        const response = await fetch("/api/files/upload", {
          method: "POST",
          body: formData,
        })

        const data = await response.json()

        if (data.url) {
          // 在编辑器中插入图片
          const range = editor?.getSelection()
          editor?.insertEmbed(range?.index || 0, "image", data.url, "user")
        }
      } catch (error) {
        console.error("Failed to upload image:", error)
      }
    }
  }, [documentId, editor])

  // 加入Socket.IO房间
  useEffect(() => {
    if (isConnected && socket) {
      socket.emit("join:room", documentId)

      return () => {
        socket.emit("leave:room", documentId)
      }
    }
  }, [isConnected, socket, documentId])

  // 初始化Y.js
  useEffect(() => {
    if (session?.user && documentId) {
      initializeYjs()
    }
  }, [initializeYjs])

  // 处理用户离开
  useEffect(() => {
    return () => {
      if (providerRef.current) {
        providerRef.current.destroy()
      }
      if (ydocRef.current) {
        ydocRef.current.destroy()
      }
    }
  }, [])

  const editorModules = {
    toolbar: [
      [{ header: [1, 2, 3, false] }],
      ["bold", "italic", "underline", "strike"],
      [{ color: [] }, { background: [] }],
      [{ list: "ordered" }, { list: "bullet" }],
      ["link", "image"],
      ["clean"],
    ],
    clipboard: {
      matchVisual: false,
    },
  }

  return (
    <div className="relative">
      {/* 连接状态指示器 */}
      <div className="absolute top-2 right-2 z-10">
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${
            isConnectedToYjs ? "bg-green-500" : "bg-red-500"
          }`} />
          <span className="text-xs text-gray-600">
            {isConnectedToYjs ? "Connected" : "Disconnected"}
          </span>
        </div>
      </div>

      {/* 在线用户指示器 */}
      <PresenceIndicator documentId={documentId} />

      {/* 协作编辑器 */}
      <div className="border rounded-lg">
        <ReactQuill
          ref={handleEditorMount}
          theme="snow"
          modules={editorModules}
          placeholder="Start collaborating..."
          className="min-h-[500px]"
        />
      </div>

      {/* 光标追踪器 */}
      {session?.user && (
        <CursorTracker
          documentId={documentId}
          userId={session.user.id}
          userName={session.user.name || session.user.email}
        />
      )}
    </div>
  )
}
```

### 3. 实时聊天组件

```typescript
// components/chat/chat-window.tsx
"use client"

import { useEffect, useRef, useState, useCallback } from "react"
import { useSocket } from "@/hooks/use-socket"
import { useSession } from "next-auth/react"
import { MessageList } from "./message-list"
import { MessageInput } from "./message-input"
import { TypingIndicator } from "./typing-indicator"
import { FileShare } from "../files/file-share"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { Users, Settings, Phone, Video } from "lucide-react"
import type { Message, User } from "@/types/chat"

interface ChatWindowProps {
  roomId: string
  roomName: string
  participants: User[]
}

export function ChatWindow({ roomId, roomName, participants }: ChatWindowProps) {
  const { data: session } = useSession()
  const { socket, isConnected } = useSocket()
  const [messages, setMessages] = useState<Message[]>([])
  const [isTyping, setIsTyping] = useState<Record<string, boolean>>({})
  const [onlineUsers, setOnlineUsers] = useState<string[]>([])
  const typingTimeoutRef = useRef<NodeJS.Timeout>()

  // 处理新消息
  const handleNewMessage = useCallback((message: Message) => {
    setMessages(prev => [...prev, message])
  }, [])

  // 处理用户输入状态
  const handleTypingStatus = useCallback((data: {
    userId: string
    userName: string
    isTyping: boolean
  }) => {
    setIsTyping(prev => ({
      ...prev,
      [data.userId]: data.isTyping,
    }))

    // 清除之前的超时
    if (typingTimeoutRef.current) {
      clearTimeout(typingTimeoutRef.current)
    }

    // 如果用户开始输入，设置超时来清除输入状态
    if (data.isTyping) {
      typingTimeoutRef.current = setTimeout(() => {
        setIsTyping(prev => ({
          ...prev,
          [data.userId]: false,
        }))
      }, 3000) // 3秒后自动清除输入状态
    }
  }, [])

  // 处理文件分享
  const handleFileShare = useCallback((fileData: any) => {
    const fileMessage: Message = {
      id: fileData.id,
      userId: fileData.userId,
      userName: fileData.userName,
      type: 'file',
      content: fileData.fileData.name,
      fileUrl: fileData.fileData.url,
      fileSize: fileData.fileData.size,
      fileType: fileData.fileData.type,
      timestamp: fileData.timestamp,
    }

    setMessages(prev => [...prev, fileMessage])
  }, [])

  // 发送消息
  const sendMessage = useCallback((content: string, type: 'text' | 'file' = 'text', fileData?: any) => {
    if (!socket?.connected || !session?.user) return

    if (type === 'file' && fileData) {
      socket.emit("file:share", {
        roomId,
        fileData,
      })
    } else {
      socket.emit("chat:message", {
        roomId,
        message: content,
        type,
      })
    }
  }, [socket, session, roomId])

  // 更新输入状态
  const updateTypingStatus = useCallback((isTyping: boolean) => {
    if (!socket?.connected || !session?.user) return

    if (isTyping) {
      socket.emit("typing:start", { roomId })
    } else {
      socket.emit("typing:stop", { roomId })
    }
  }, [socket, session, roomId])

  // 设置Socket事件监听器
  useEffect(() => {
    if (!socket || !isConnected) return

    socket.on("chat:new", handleNewMessage)
    socket.on("user:typing", handleTypingStatus)
    socket.on("file:shared", handleFileShare)

    // 加入房间
    socket.emit("join:room", roomId)

    // 加载历史消息
    const loadHistory = async () => {
      try {
        const response = await fetch(`/api/chat/history/${roomId}`)
        const history = await response.json()
        setMessages(history)
      } catch (error) {
        console.error("Failed to load chat history:", error)
      }
    }

    loadHistory()

    return () => {
      socket.off("chat:new", handleNewMessage)
      socket.off("user:typing", handleTypingStatus)
      socket.off("file:shared", handleFileShare)
      socket.emit("leave:room", roomId)
    }
  }, [socket, isConnected, roomId, handleNewMessage, handleTypingStatus, handleFileShare])

  // 获取当前输入用户
  const typingUsers = Object.entries(isTyping)
    .filter(([_, isTyping]) => isTyping)
    .map(([userId]) => participants.find(p => p.id === userId))
    .filter(Boolean)

  return (
    <div className="flex flex-col h-full">
      {/* 聊天头部 */}
      <Card className="flex-shrink-0">
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <CardTitle className="text-lg">{roomName}</CardTitle>
              <Badge variant="secondary">
                {participants.length} participants
              </Badge>
              {onlineUsers.length > 0 && (
                <Badge variant="outline" className="text-green-600">
                  {onlineUsers.length} online
                </Badge>
              )}
            </div>

            <div className="flex items-center space-x-2">
              <Button variant="ghost" size="sm">
                <Phone className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Video className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Users className="w-4 h-4" />
              </Button>
              <Button variant="ghost" size="sm">
                <Settings className="w-4 h-4" />
              </Button>
            </div>
          </div>
        </CardHeader>
      </Card>

      {/* 消息列表 */}
      <div className="flex-1 overflow-hidden">
        <MessageList
          messages={messages}
          currentUserId={session?.user?.id}
          participants={participants}
        />
      </div>

      {/* 输入状态指示器 */}
      {typingUsers.length > 0 && (
        <div className="px-4 py-2 bg-gray-50 border-t">
          <TypingIndicator users={typingUsers.map(u => u?.name).filter(Boolean)} />
        </div>
      )}

      {/* 消息输入 */}
      <div className="flex-shrink-0 p-4 border-t">
        <MessageInput
          onSendMessage={sendMessage}
          onTypingStatusUpdate={updateTypingStatus}
          roomId={roomId}
        />
      </div>
    </div>
  )
}
```

## 状态同步策略

### 1. Y.js文档同步

```typescript
// lib/yjs/document-manager.ts
import * as Y from "yjs"
import { WebsocketProvider } from "y-websocket"
import { IndexeddbPersistence } from "y-indexeddb"

interface DocumentManagerConfig {
  documentId: string
  userId: string
  userName: string
  wsUrl: string
}

export class DocumentManager {
  private doc: Y.Doc
  private provider: WebsocketProvider
  private persistence: IndexeddbPersistence
  private config: DocumentManagerConfig

  constructor(config: DocumentManagerConfig) {
    this.config = config
    this.doc = new Y.Doc()

    // 设置用户信息
    this.doc.gcFilter = () => false // 禁用垃圾回收以保持历史记录

    // 初始化WebSocket provider
    this.provider = new WebsocketProvider(
      `${config.wsUrl}/document/${config.documentId}`,
      config.documentId,
      this.doc,
      {
        WebSocketPolyfill: WebSocket,
      }
    )

    // 初始化IndexedDB持久化
    this.persistence = new IndexeddbPersistence(config.documentId, this.doc)

    // 设置用户信息
    this.setupUserAwareness()

    // 监听文档更新
    this.setupDocumentListeners()
  }

  private setupUserAwareness() {
    const awareness = this.provider.awareness

    // 设置当前用户信息
    awareness.setLocalStateField("user", {
      id: this.config.userId,
      name: this.config.userName,
      color: this.getUserColor(this.config.userId),
      cursor: null,
    })

    // 监听其他用户变化
    awareness.on("change", (changes: any) => {
      const states = awareness.getStates()
      this.handleAwarenessUpdate(states)
    })
  }

  private setupDocumentListeners() {
    this.doc.on("update", (update: Uint8Array, origin: any) => {
      if (origin !== this.provider) {
        // 处理来自其他客户端的更新
        this.handleRemoteUpdate(update)
      }
    })

    this.doc.on("afterTransaction", (transaction: Y.Transaction) => {
      // 处理本地事务完成
      this.handleTransactionComplete(transaction)
    })
  }

  private handleAwarenessUpdate(states: Map<number, any>) {
    // 处理用户状态变化（光标位置、选择等）
    const users = Array.from(states.entries()).map(([clientId, state]) => ({
      clientId,
      ...state.user,
    }))

    // 发送用户状态更新到UI
    this.emit("users:update", users)
  }

  private handleRemoteUpdate(update: Uint8Array) {
    // 处理远程文档更新
    this.emit("document:remote-update", update)
  }

  private handleTransactionComplete(transaction: Y.Transaction) {
    // 处理本地事务完成
    if (transaction.local) {
      this.emit("document:local-update", transaction)
    }
  }

  // 获取文档内容
  getContent(): string {
    const ytext = this.doc.getText("quill")
    return ytext.toString()
  }

  // 设置文档内容
  setContent(content: string) {
    const ytext = this.doc.getText("quill")
    ytext.delete(0, ytext.length)
    ytext.insert(0, content)
  }

  // 应用操作
  applyOperation(operation: any) {
    Y.applyUpdate(this.doc, operation)
  }

  // 获取文档历史
  getHistory(): any[] {
    // 实现文档历史记录
    return []
  }

  // 撤销操作
  undo() {
    Y.undoManager(this.doc).undo()
  }

  // 重做操作
  redo() {
    Y.undoManager(this.doc).redo()
  }

  // 生成用户颜色
  private getUserColor(userId: string): string {
    const colors = [
      "#ef4444", "#f97316", "#f59e0b", "#eab308", "#84cc16",
      "#22c55e", "#10b981", "#14b8a6", "#06b6d4", "#0ea5e9",
      "#3b82f6", "#6366f1", "#8b5cf6", "#a855f7", "#d946ef",
    ]

    let hash = 0
    for (let i = 0; i < userId.length; i++) {
      hash = userId.charCodeAt(i) + ((hash << 5) - hash)
    }

    return colors[Math.abs(hash) % colors.length]
  }

  // 事件发射器
  private listeners: Map<string, Function[]> = new Map()

  on(event: string, callback: Function) {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, [])
    }
    this.listeners.get(event)!.push(callback)
  }

  emit(event: string, data: any) {
    const callbacks = this.listeners.get(event) || []
    callbacks.forEach(callback => callback(data))
  }

  // 清理资源
  destroy() {
    this.provider.destroy()
    this.persistence.destroy()
    this.doc.destroy()
  }
}
```

### 2. 冲突解决策略

```typescript
// lib/yjs/conflict-resolution.ts
import * as Y from "yjs"

export interface ConflictResolutionStrategy {
  resolve(conflict: Y.Transaction): void
}

// 最后写入获胜策略
export class LastWriteWinsStrategy implements ConflictResolutionStrategy {
  resolve(conflict: Y.Transaction): void {
    // Y.js已经内置了基于时间戳的冲突解决
    // 这里可以添加自定义逻辑
  }
}

// 基于用户权限的策略
export class PermissionBasedStrategy implements ConflictResolutionStrategy {
  private userPermissions: Map<string, number> = new Map()

  setUserPermission(userId: string, level: number) {
    this.userPermissions.set(userId, level)
  }

  resolve(conflict: Y.Transaction): void {
    // 根据用户权限解决冲突
    const userId = this.extractUserId(conflict)
    const userLevel = this.userPermissions.get(userId) || 0

    // 如果用户权限不足，回滚操作
    if (userLevel < this.getRequiredLevel(conflict)) {
      conflict.meta?.set('reverted', true)
    }
  }

  private extractUserId(transaction: Y.Transaction): string {
    // 从事务中提取用户ID
    return transaction.origin?.userId || 'unknown'
  }

  private getRequiredLevel(transaction: Y.Transaction): number {
    // 根据操作类型确定所需权限级别
    return 1 // 默认权限级别
  }
}

// 操作转换策略
export class OperationalTransformationStrategy implements ConflictResolutionStrategy {
  resolve(conflict: Y.Transaction): void {
    // 实现操作转换算法
    this.transformOperations(conflict)
  }

  private transformOperations(transaction: Y.Transaction): void {
    // 对操作进行转换以解决冲突
    // 这是一个简化的示例，实际实现会更复杂
    const operations = this.extractOperations(transaction)
    const transformed = this.transform(operations)
    this.applyTransformedOperations(transformed)
  }

  private extractOperations(transaction: Y.Transaction): any[] {
    // 从事务中提取操作
    return []
  }

  private transform(operations: any[]): any[] {
    // 转换操作
    return operations
  }

  private applyTransformedOperations(operations: any[]): void {
    // 应用转换后的操作
  }
}

// 冲突检测器
export class ConflictDetector {
  private pendingTransactions: Map<string, Y.Transaction> = new Map()

  addTransaction(transaction: Y.Transaction): void {
    const transactionId = this.generateTransactionId(transaction)
    this.pendingTransactions.set(transactionId, transaction)
  }

  removeTransaction(transactionId: string): void {
    this.pendingTransactions.delete(transactionId)
  }

  detectConflicts(): ConflictInfo[] {
    const conflicts: ConflictInfo[] = []
    const transactions = Array.from(this.pendingTransactions.values())

    for (let i = 0; i < transactions.length; i++) {
      for (let j = i + 1; j < transactions.length; j++) {
        const conflict = this.checkConflict(transactions[i], transactions[j])
        if (conflict) {
          conflicts.push(conflict)
        }
      }
    }

    return conflicts
  }

  private checkConflict(tx1: Y.Transaction, tx2: Y.Transaction): ConflictInfo | null {
    // 检查两个事务是否存在冲突
    const overlappingItems = this.findOverlappingItems(tx1, tx2)

    if (overlappingItems.length > 0) {
      return {
        transactions: [tx1, tx2],
        overlappingItems,
        type: this.determineConflictType(tx1, tx2),
      }
    }

    return null
  }

  private findOverlappingItems(tx1: Y.Transaction, tx2: Y.Transaction): any[] {
    // 找到重叠的操作项
    return []
  }

  private determineConflictType(tx1: Y.Transaction, tx2: Y.Transaction): string {
    // 确定冲突类型
    return "concurrent_edit"
  }

  private generateTransactionId(transaction: Y.Transaction): string {
    // 生成唯一的事务ID
    return `${transaction.id}_${Date.now()}`
  }
}

interface ConflictInfo {
  transactions: Y.Transaction[]
  overlappingItems: any[]
  type: string
}
```

## 性能优化

### 1. 消息批处理

```typescript
// lib/socket/message-batcher.ts
interface MessageBatch {
  messages: any[]
  timeout: NodeJS.Timeout | null
  flush: () => void
}

export class MessageBatcher {
  private batchInterval: number
  private maxBatchSize: number
  private batches: Map<string, MessageBatch> = new Map()

  constructor(batchInterval = 100, maxBatchSize = 50) {
    this.batchInterval = batchInterval
    this.maxBatchSize = maxBatchSize
  }

  addMessage(event: string, roomId: string, data: any, socket: any): void {
    const batchKey = `${event}:${roomId}`

    if (!this.batches.has(batchKey)) {
      this.batches.set(batchKey, {
        messages: [],
        timeout: null,
        flush: () => this.flushBatch(batchKey),
      })
    }

    const batch = this.batches.get(batchKey)!
    batch.messages.push(data)

    // 如果达到最大批次大小，立即发送
    if (batch.messages.length >= this.maxBatchSize) {
      this.flushBatch(batchKey)
      return
    }

    // 设置定时器
    if (!batch.timeout) {
      batch.timeout = setTimeout(() => {
        this.flushBatch(batchKey)
      }, this.batchInterval)
    }
  }

  private flushBatch(batchKey: string): void {
    const batch = this.batches.get(batchKey)
    if (!batch || batch.messages.length === 0) return

    const [event, roomId] = batchKey.split(':')

    // 批量发送消息
    if (batch.messages.length === 1) {
      // 单条消息直接发送
      batch.messages.forEach(message => {
        this.sendMessage(event, roomId, message)
      })
    } else {
      // 批量消息打包发送
      this.sendMessage(event, roomId, {
        type: 'batch',
        messages: batch.messages,
        timestamp: Date.now(),
      })
    }

    // 清理定时器
    if (batch.timeout) {
      clearTimeout(batch.timeout)
    }

    // 移除批次
    this.batches.delete(batchKey)
  }

  private sendMessage(event: string, roomId: string, data: any): void {
    // 实际发送消息的逻辑
    // 这里需要传入socket实例
    console.log(`Sending ${event} to room ${roomId}:`, data)
  }

  flushAll(): void {
    // 刷新所有待处理的批次
    const batchKeys = Array.from(this.batches.keys())
    batchKeys.forEach(key => this.flushBatch(key))
  }
}
```

### 2. 数据压缩

```typescript
// lib/utils/compression.ts
import { deflate, inflate } from 'pako'

export class MessageCompressor {
  // 压缩消息
  static compress(message: any): string {
    try {
      const jsonString = JSON.stringify(message)
      const compressed = deflate(jsonString)
      return Buffer.from(compressed).toString('base64')
    } catch (error) {
      console.error('Compression failed:', error)
      return JSON.stringify(message)
    }
  }

  // 解压缩消息
  static decompress(compressedMessage: string): any {
    try {
      const buffer = Buffer.from(compressedMessage, 'base64')
      const decompressed = inflate(buffer)
      return JSON.parse(new TextDecoder().decode(decompressed))
    } catch (error) {
      console.error('Decompression failed:', error)
      // 如果解压失败，尝试直接解析JSON
      try {
        return JSON.parse(compressedMessage)
      } catch {
        return null
      }
    }
  }

  // 检查是否需要压缩
  static shouldCompress(message: any, threshold = 1024): boolean {
    const jsonString = JSON.stringify(message)
    return jsonString.length > threshold
  }
}

// 使用示例
const message = {
  type: 'document_update',
  operations: [/* ... */],
  timestamp: Date.now(),
}

if (MessageCompressor.shouldCompress(message)) {
  const compressed = MessageCompressor.compress(message)
  // 发送压缩后的消息
}
```

### 3. 连接池管理

```typescript
// lib/socket/connection-pool.ts
interface Connection {
  socket: any
  lastUsed: number
  isActive: boolean
}

export class ConnectionPool {
  private pool: Map<string, Connection> = new Map()
  private maxPoolSize: number
  private idleTimeout: number
  private cleanupInterval: NodeJS.Timeout | null = null

  constructor(maxPoolSize = 10, idleTimeout = 300000) { // 5分钟
    this.maxPoolSize = maxPoolSize
    this.idleTimeout = idleTimeout
    this.startCleanupTask()
  }

  getConnection(key: string): Connection | null {
    const connection = this.pool.get(key)

    if (connection && connection.isActive) {
      connection.lastUsed = Date.now()
      return connection
    }

    return null
  }

  createConnection(key: string, socket: any): boolean {
    if (this.pool.size >= this.maxPoolSize) {
      this.cleanupIdleConnections()
    }

    if (this.pool.size >= this.maxPoolSize) {
      return false // 池已满
    }

    const connection: Connection = {
      socket,
      lastUsed: Date.now(),
      isActive: true,
    }

    this.pool.set(key, connection)
    return true
  }

  releaseConnection(key: string): void {
    const connection = this.pool.get(key)
    if (connection) {
      connection.lastUsed = Date.now()
    }
  }

  removeConnection(key: string): void {
    const connection = this.pool.get(key)
    if (connection) {
      connection.socket.disconnect?.()
      this.pool.delete(key)
    }
  }

  private cleanupIdleConnections(): void {
    const now = Date.now()
    const keysToRemove: string[] = []

    for (const [key, connection] of this.pool) {
      if (now - connection.lastUsed > this.idleTimeout) {
        keysToRemove.push(key)
      }
    }

    keysToRemove.forEach(key => this.removeConnection(key))
  }

  private startCleanupTask(): void {
    this.cleanupInterval = setInterval(() => {
      this.cleanupIdleConnections()
    }, 60000) // 每分钟清理一次
  }

  getPoolStats() {
    return {
      totalConnections: this.pool.size,
      activeConnections: Array.from(this.pool.values()).filter(c => c.isActive).length,
      maxPoolSize: this.maxPoolSize,
    }
  }

  destroy(): void {
    if (this.cleanupInterval) {
      clearInterval(this.cleanupInterval)
    }

    // 关闭所有连接
    for (const [key, connection] of this.pool) {
      this.removeConnection(key)
    }

    this.pool.clear()
  }
}
```

## 错误处理

### 1. 连接错误处理

```typescript
// hooks/use-connection-handler.ts
"use client"

import { useEffect, useState, useCallback } from "react"
import { useSession } from "next-auth/react"
import { toast } from "react-hot-toast"

interface ConnectionErrorHandler {
  retryConnection: () => void
  connectionState: 'connected' | 'disconnected' | 'connecting' | 'error'
  errorMessage?: string
}

export function useConnectionHandler(): ConnectionErrorHandler {
  const { data: session } = useSession()
  const [connectionState, setConnectionState] = useState<'connected' | 'disconnected' | 'connecting' | 'error'>('disconnected')
  const [errorMessage, setErrorMessage] = useState<string>()
  const [retryCount, setRetryCount] = useState(0)
  const maxRetries = 5

  const retryConnection = useCallback(() => {
    if (retryCount >= maxRetries) {
      toast.error("Maximum reconnection attempts reached. Please refresh the page.")
      return
    }

    setConnectionState('connecting')
    setRetryCount(prev => prev + 1)

    // 模拟重连逻辑
    setTimeout(() => {
      // 这里应该是实际的重连逻辑
      const success = Math.random() > 0.3 // 70% 成功率

      if (success) {
        setConnectionState('connected')
        setRetryCount(0)
        toast.success("Reconnected successfully")
      } else {
        setConnectionState('error')
        setErrorMessage("Connection failed")
        toast.error("Reconnection failed. Retrying...")

        // 指数退避重试
        const delay = Math.min(1000 * Math.pow(2, retryCount), 30000)
        setTimeout(retryConnection, delay)
      }
    }, 1000)
  }, [retryCount, maxRetries])

  // 自动重连逻辑
  useEffect(() => {
    if (connectionState === 'disconnected' && session?.user) {
      const timer = setTimeout(() => {
        retryConnection()
      }, 5000)

      return () => clearTimeout(timer)
    }
  }, [connectionState, session, retryConnection])

  // 监听网络状态
  useEffect(() => {
    const handleOnline = () => {
      if (connectionState === 'disconnected') {
        retryConnection()
      }
    }

    const handleOffline = () => {
      setConnectionState('disconnected')
      toast.error("Network connection lost")
    }

    window.addEventListener('online', handleOnline)
    window.addEventListener('offline', handleOffline)

    return () => {
      window.removeEventListener('online', handleOnline)
      window.removeEventListener('offline', handleOffline)
    }
  }, [connectionState, retryConnection])

  return {
    retryConnection,
    connectionState,
    errorMessage,
  }
}
```

### 2. 数据同步错误处理

```typescript
// lib/sync/error-handler.ts
export interface SyncError {
  type: 'conflict' | 'network' | 'validation' | 'permission'
  message: string
  data?: any
  timestamp: number
  retryable: boolean
}

export class SyncErrorHandler {
  private errorHandlers: Map<string, (error: SyncError) => void> = new Map()
  private retryQueue: Map<string, SyncError[]> = new Map()

  constructor() {
    this.setupGlobalErrorHandlers()
  }

  // 处理同步错误
  handleError(error: SyncError): void {
    console.error('Sync error:', error)

    // 调用特定类型的错误处理器
    const handler = this.errorHandlers.get(error.type)
    if (handler) {
      handler(error)
    }

    // 如果错误可重试，加入重试队列
    if (error.retryable) {
      this.addToRetryQueue(error)
    }

    // 通知UI
    this.notifyUI(error)
  }

  // 注册错误处理器
  registerErrorHandler(type: string, handler: (error: SyncError) => void): void {
    this.errorHandlers.set(type, handler)
  }

  // 加入重试队列
  private addToRetryQueue(error: SyncError): void {
    const key = `${error.type}_${error.timestamp}`

    if (!this.retryQueue.has(key)) {
      this.retryQueue.set(key, [error])

      // 设置重试定时器
      setTimeout(() => {
        this.retryError(key)
      }, this.getRetryDelay(error))
    }
  }

  // 重试错误
  private retryError(key: string): void {
    const errors = this.retryQueue.get(key)
    if (!errors) return

    errors.forEach(error => {
      // 这里实现重试逻辑
      console.log('Retrying error:', error)
      // 实际的重试逻辑取决于错误类型
    })

    this.retryQueue.delete(key)
  }

  // 获取重试延迟
  private getRetryDelay(error: SyncError): number {
    switch (error.type) {
      case 'network':
        return Math.min(1000 * Math.pow(2, this.getRetryCount(error)), 30000)
      case 'conflict':
        return 5000 // 冲突错误等待更长时间
      default:
        return 2000
    }
  }

  // 获取重试次数
  private getRetryCount(error: SyncError): number {
    // 实现重试次数跟踪
    return 0
  }

  // 通知UI
  private notifyUI(error: SyncError): void {
    // 使用自定义事件或状态管理通知UI
    window.dispatchEvent(new CustomEvent('sync-error', { detail: error }))
  }

  // 设置全局错误处理器
  private setupGlobalErrorHandlers(): void {
    // 网络错误处理器
    this.registerErrorHandler('network', (error) => {
      console.log('Handling network error:', error)
      // 可以显示网络状态指示器
    })

    // 冲突错误处理器
    this.registerErrorHandler('conflict', (error) => {
      console.log('Handling conflict error:', error)
      // 可以显示冲突解决对话框
    })

    // 验证错误处理器
    this.registerErrorHandler('validation', (error) => {
      console.log('Handling validation error:', error)
      // 可以显示验证错误消息
    })

    // 权限错误处理器
    this.registerErrorHandler('permission', (error) => {
      console.log('Handling permission error:', error)
      // 可以显示权限错误消息
    })
  }

  // 创建不同类型的错误
  static createError(type: SyncError['type'], message: string, data?: any, retryable = true): SyncError {
    return {
      type,
      message,
      data,
      timestamp: Date.now(),
      retryable,
    }
  }
}

// 使用示例
const errorHandler = new SyncErrorHandler()

// 在组件中监听错误
useEffect(() => {
  const handleSyncError = (event: CustomEvent) => {
    const error = event.detail as SyncError
    // 显示错误消息或采取其他行动
  }

  window.addEventListener('sync-error', handleSyncError as EventListener)

  return () => {
    window.removeEventListener('sync-error', handleSyncError as EventListener)
  }
}, [])
```

## 测试策略

### 1. Socket.IO测试

```typescript
// __tests__/socket/socket.test.ts
import { Server } from "socket.io"
import { createServer } from "http"
import { io as ClientIO } from "socket.io-client"
import { setupSocketIO } from "@/lib/socket"

describe("Socket.IO Integration", () => {
  let io: Server
  let serverSocket: any
  let clientSocket: any
  let httpServer: any

  beforeAll((done) => {
    httpServer = createServer()
    io = setupSocketIO(httpServer)

    httpServer.listen(() => {
      const port = (httpServer.address() as any).port
      clientSocket = ClientIO(`http://localhost:${port}`)

      io.on("connection", (socket) => {
        serverSocket = socket
      })

      clientSocket.on("connect", done)
    })
  })

  afterAll(() => {
    io.close()
    clientSocket.close()
    httpServer.close()
  })

  test("should connect and disconnect", (done) => {
    clientSocket.on("connect", () => {
      expect(clientSocket.connected).toBe(true)
      clientSocket.disconnect()
    })

    clientSocket.on("disconnect", () => {
      expect(clientSocket.connected).toBe(false)
      done()
    })
  })

  test("should join and leave rooms", (done) => {
    const roomId = "test-room"

    clientSocket.emit("join:room", roomId)

    serverSocket.on("join:room", (receivedRoomId: string) => {
      expect(receivedRoomId).toBe(roomId)
      expect(serverSocket.rooms.has(`room:${roomId}`)).toBe(true)

      clientSocket.emit("leave:room", roomId)

      serverSocket.on("leave:room", (receivedRoomId: string) => {
        expect(receivedRoomId).toBe(roomId)
        expect(serverSocket.rooms.has(`room:${roomId}`)).toBe(false)
        done()
      })
    })
  })

  test("should handle chat messages", (done) => {
    const roomId = "test-room"
    const message = "Hello, World!"

    clientSocket.emit("join:room", roomId)

    setTimeout(() => {
      clientSocket.emit("chat:message", {
        roomId,
        message,
        type: "text",
      })

      clientSocket.on("chat:new", (data: any) => {
        expect(data.message).toBe(message)
        expect(data.roomId).toBe(roomId)
        done()
      })
    }, 100)
  })

  test("should handle typing indicators", (done) => {
    const roomId = "test-room"

    clientSocket.emit("join:room", roomId)

    setTimeout(() => {
      clientSocket.emit("typing:start", { roomId })

      serverSocket.on("typing:start", (data: any) => {
        expect(data.roomId).toBe(roomId)

        clientSocket.emit("typing:stop", { roomId })

        serverSocket.on("typing:stop", (stopData: any) => {
          expect(stopData.roomId).toBe(roomId)
          done()
        })
      })
    }, 100)
  })
})
```

### 2. 协作编辑测试

```typescript
// __tests__/collaboration/editor.test.ts
import { Doc } from "yjs"
import { WebsocketProvider } from "y-websocket"
import { QuillBinding } from "y-quill"

describe("Collaborative Editor", () => {
  let doc1: Doc
  let doc2: Doc
  let provider1: WebsocketProvider
  let provider2: WebsocketProvider

  beforeAll(() => {
    // 创建两个文档实例模拟两个用户
    doc1 = new Doc()
    doc2 = new Doc()

    // 模拟WebSocket provider
    provider1 = new WebsocketProvider("ws://localhost:3000", "test-doc", doc1)
    provider2 = new WebsocketProvider("ws://localhost:3000", "test-doc", doc2)
  })

  afterAll(() => {
    provider1.destroy()
    provider2.destroy()
    doc1.destroy()
    doc2.destroy()
  })

  test("should sync text changes between documents", (done) => {
    const ytext1 = doc1.getText("quill")
    const ytext2 = doc2.getText("quill")

    ytext1.insert(0, "Hello")

    // 等待同步
    setTimeout(() => {
      expect(ytext2.toString()).toBe("Hello")
      done()
    }, 100)
  })

  test("should handle concurrent edits", (done) => {
    const ytext1 = doc1.getText("quill")
    const ytext2 = doc2.getText("quill")

    // 用户1在开头插入
    ytext1.insert(0, "User1: ")

    // 用户2在结尾插入
    ytext2.insert(ytext2.length, " User2")

    // 等待同步
    setTimeout(() => {
      const result1 = ytext1.toString()
      const result2 = ytext2.toString()

      // 两个文档应该同步到相同状态
      expect(result1).toBe(result2)
      expect(result1).toContain("User1:")
      expect(result1).toContain("User2")
      done()
    }, 200)
  })

  test("should handle deletion conflicts", (done) => {
    const ytext1 = doc1.getText("quill")
    const ytext2 = doc2.getText("quill")

    // 设置初始文本
    ytext1.insert(0, "Hello World")

    setTimeout(() => {
      // 用户1删除前5个字符
      ytext1.delete(0, 5)

      // 用户2删除后5个字符
      ytext2.delete(6, 5)

      // 等待同步
      setTimeout(() => {
        const result1 = ytext1.toString()
        const result2 = ytext2.toString()

        expect(result1).toBe(result2)
        done()
      }, 100)
    }, 100)
  })
})
```

## 部署配置

### 1. 生产环境配置

```typescript
// lib/config/production.ts
export const productionConfig = {
  // Socket.IO配置
  socket: {
    cors: {
      origin: process.env.ALLOWED_ORIGINS?.split(',') || [],
      methods: ["GET", "POST"],
      credentials: true,
    },
    transports: ["websocket"],
    pingTimeout: 60000,
    pingInterval: 25000,
  },

  // Redis配置
  redis: {
    host: process.env.REDIS_HOST || "localhost",
    port: parseInt(process.env.REDIS_PORT || "6379"),
    password: process.env.REDIS_PASSWORD,
    db: parseInt(process.env.REDIS_DB || "0"),
    keyPrefix: "realtime:",
  },

  // 消息队列配置
  queue: {
    batchSize: 50,
    batchInterval: 100,
    maxRetries: 3,
    retryDelay: 1000,
  },

  // 性能配置
  performance: {
    maxConnections: 1000,
    connectionTimeout: 30000,
    messageSizeLimit: 1024 * 1024, // 1MB
    compressionThreshold: 1024,
  },

  // 监控配置
  monitoring: {
    metricsEnabled: true,
    healthCheckInterval: 30000,
    errorReportingEnabled: true,
  },

  // 安全配置
  security: {
    jwtSecret: process.env.JWT_SECRET,
    jwtExpiration: "24h",
    rateLimitWindow: 900000, // 15分钟
    rateLimitMax: 100,
  },
}
```

### 2. Docker Compose配置

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/realtime_app
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your-secret-key
      - NEXTAUTH_URL=http://localhost:3000
      - NEXTAUTH_SECRET=your-nextauth-secret
    depends_on:
      - db
      - redis
    restart: unless-stopped

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: realtime_app
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    restart: unless-stopped

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    restart: unless-stopped

  # 水平扩展时的额外实例
  app-worker:
    build: .
    environment:
      - NODE_ENV=production
      - DATABASE_URL=postgresql://user:password@db:5432/realtime_app
      - REDIS_URL=redis://redis:6379
      - JWT_SECRET=your-secret-key
      - NEXTAUTH_URL=http://localhost:3000
      - NEXTAUTH_SECRET=your-nextauth-secret
      - WORKER=true
    depends_on:
      - db
      - redis
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:
```

## 扩展功能

### 1. 视频会议集成

```typescript
// components/video-conference/video-conference.tsx
"use client"

import { useEffect, useRef, useState } from "react"
import { useSocket } from "@/hooks/use-socket"
import { useSession } from "next-auth/react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Video, VideoOff, Mic, MicOff, Phone, Users, ScreenShare } from "lucide-react"

interface VideoConferenceProps {
  roomId: string
}

export function VideoConference({ roomId }: VideoConferenceProps) {
  const { data: session } = useSession()
  const { socket } = useSocket()
  const [isVideoEnabled, setIsVideoEnabled] = useState(false)
  const [isAudioEnabled, setIsAudioEnabled] = useState(false)
  const [participants, setParticipants] = useState<any[]>([])
  const [localStream, setLocalStream] = useState<MediaStream | null>(null)
  const [isScreenSharing, setIsScreenSharing] = useState(false)

  const localVideoRef = useRef<HTMLVideoElement>(null)
  const peerConnections = useRef<Map<string, RTCPeerConnection>>(new Map())

  // 初始化媒体流
  const initializeMedia = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true,
      })

      setLocalStream(stream)

      if (localVideoRef.current) {
        localVideoRef.current.srcObject = stream
      }

      setIsVideoEnabled(true)
      setIsAudioEnabled(true)
    } catch (error) {
      console.error("Failed to initialize media:", error)
    }
  }

  // 创建WebRTC连接
  const createPeerConnection = (userId: string): RTCPeerConnection => {
    const configuration = {
      iceServers: [
        { urls: "stun:stun.l.google.com:19302" },
        { urls: "stun:stun1.l.google.com:19302" },
      ],
    }

    const peerConnection = new RTCPeerConnection(configuration)

    // 添加本地流
    if (localStream) {
      localStream.getTracks().forEach(track => {
        peerConnection.addTrack(track, localStream!)
      })
    }

    // 处理ICE候选
    peerConnection.onicecandidate = (event) => {
      if (event.candidate) {
        socket.emit("webrtc:ice-candidate", {
          userId,
          candidate: event.candidate,
        })
      }
    }

    // 处理远程流
    peerConnection.ontrack = (event) => {
      // 处理远程视频流
      handleRemoteStream(userId, event.streams[0])
    }

    peerConnections.current.set(userId, peerConnection)
    return peerConnection
  }

  // 处理WebRTC信号
  useEffect(() => {
    if (!socket || !session?.user) return

    // 处理视频会议邀请
    socket.on("video:invite", async (data: { fromUserId: string; fromUserName: string }) => {
      // 显示邀请对话框
      const accept = confirm(`${data.fromUserName} is inviting you to a video call. Accept?`)

      if (accept) {
        await initializeMedia()
        socket.emit("video:accept", { toUserId: data.fromUserId })
      }
    })

    // 处理WebRTC offer
    socket.on("webrtc:offer", async (data: { fromUserId: string; offer: RTCSessionDescriptionInit }) => {
      const peerConnection = createPeerConnection(data.fromUserId)

      await peerConnection.setRemoteDescription(new RTCSessionDescription(data.offer))

      const answer = await peerConnection.createAnswer()
      await peerConnection.setLocalDescription(answer)

      socket.emit("webrtc:answer", {
        toUserId: data.fromUserId,
        answer,
      })
    })

    // 处理WebRTC answer
    socket.on("webrtc:answer", async (data: { fromUserId: string; answer: RTCSessionDescriptionInit }) => {
      const peerConnection = peerConnections.current.get(data.fromUserId)

      if (peerConnection) {
        await peerConnection.setRemoteDescription(new RTCSessionDescription(data.answer))
      }
    })

    // 处理ICE候选
    socket.on("webrtc:ice-candidate", async (data: { fromUserId: string; candidate: RTCIceCandidateInit }) => {
      const peerConnection = peerConnections.current.get(data.fromUserId)

      if (peerConnection) {
        await peerConnection.addIceCandidate(new RTCIceCandidate(data.candidate))
      }
    })

    // 处理用户离开
    socket.on("video:user-left", (data: { userId: string }) => {
      const peerConnection = peerConnections.current.get(data.userId)

      if (peerConnection) {
        peerConnection.close()
        peerConnections.current.delete(data.userId)
      }

      setParticipants(prev => prev.filter(p => p.id !== data.userId))
    })

    return () => {
      // 清理所有连接
      peerConnections.current.forEach(connection => connection.close())
      peerConnections.current.clear()
    }
  }, [socket, session])

  // 发起视频通话
  const startVideoCall = async () => {
    if (!socket || !session?.user) return

    await initializeMedia()

    socket.emit("video:invite", {
      roomId,
      fromUserId: session.user.id,
      fromUserName: session.user.name,
    })
  }

  // 切换视频
  const toggleVideo = () => {
    if (localStream) {
      const videoTrack = localStream.getVideoTracks()[0]
      videoTrack.enabled = !videoTrack.enabled
      setIsVideoEnabled(videoTrack.enabled)
    }
  }

  // 切换音频
  const toggleAudio = () => {
    if (localStream) {
      const audioTrack = localStream.getAudioTracks()[0]
      audioTrack.enabled = !audioTrack.enabled
      setIsAudioEnabled(audioTrack.enabled)
    }
  }

  // 结束通话
  const endCall = () => {
    peerConnections.current.forEach(connection => connection.close())
    peerConnections.current.clear()

    if (localStream) {
      localStream.getTracks().forEach(track => track.stop())
      setLocalStream(null)
    }

    setIsVideoEnabled(false)
    setIsAudioEnabled(false)

    socket.emit("video:end", { roomId })
  }

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          Video Conference
          <div className="flex items-center space-x-2">
            <Users className="w-4 h-4" />
            <span className="text-sm">{participants.length + 1}</span>
          </div>
        </CardTitle>
      </CardHeader>
      <CardContent>
        {/* 本地视频 */}
        <div className="relative mb-4">
          <video
            ref={localVideoRef}
            autoPlay
            muted
            playsInline
            className="w-full h-64 bg-gray-900 rounded-lg"
          />
          {!isVideoEnabled && (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-900 rounded-lg">
              <div className="text-white text-center">
                <div className="w-16 h-16 bg-gray-700 rounded-full flex items-center justify-center mx-auto mb-2">
                  <span className="text-2xl">
                    {session?.user?.name?.[0]?.toUpperCase()}
                  </span>
                </div>
                <p>Camera Off</p>
              </div>
            </div>
          )}
        </div>

        {/* 远程视频 */}
        <div className="grid grid-cols-2 gap-4 mb-4">
          {participants.map((participant) => (
            <div key={participant.id} className="relative">
              <video
                autoPlay
                playsInline
                className="w-full h-32 bg-gray-900 rounded-lg"
                ref={(el) => {
                  if (el && participant.stream) {
                    el.srcObject = participant.stream
                  }
                }}
              />
              <div className="absolute bottom-2 left-2 text-white text-sm bg-black bg-opacity-50 px-2 py-1 rounded">
                {participant.name}
              </div>
            </div>
          ))}
        </div>

        {/* 控制按钮 */}
        <div className="flex justify-center space-x-4">
          <Button
            variant={isVideoEnabled ? "default" : "destructive"}
            size="sm"
            onClick={toggleVideo}
          >
            {isVideoEnabled ? <Video className="w-4 h-4" /> : <VideoOff className="w-4 h-4" />}
          </Button>

          <Button
            variant={isAudioEnabled ? "default" : "destructive"}
            size="sm"
            onClick={toggleAudio}
          >
            {isAudioEnabled ? <Mic className="w-4 h-4" /> : <MicOff className="w-4 h-4" />}
          </Button>

          <Button
            variant={isScreenSharing ? "default" : "outline"}
            size="sm"
            onClick={() => setIsScreenSharing(!isScreenSharing)}
          >
            <ScreenShare className="w-4 h-4" />
          </Button>

          <Button variant="destructive" size="sm" onClick={endCall}>
            <Phone className="w-4 h-4" />
          </Button>
        </div>
      </CardContent>
    </Card>
  )
}
```

### 2. AI助手集成

```typescript
// lib/ai/assistant.ts
export class AIAssistant {
  private apiKey: string
  private baseUrl: string

  constructor(apiKey: string, baseUrl = "https://api.openai.com/v1") {
    this.apiKey = apiKey
    this.baseUrl = baseUrl
  }

  // 生成文档摘要
  async generateSummary(content: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system",
            content: "You are a helpful assistant that summarizes documents. Provide a concise summary of the given text.",
          },
          {
            role: "user",
            content: `Please summarize this document:\n\n${content}`,
          },
        ],
        max_tokens: 200,
        temperature: 0.5,
      }),
    })

    const data = await response.json()
    return data.choices[0].message.content
  }

  // 智能文本补全
  async autoComplete(context: string, cursorPosition: number): Promise<string[]> {
    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system",
            content: "You are a coding assistant. Provide code completions based on the context.",
          },
          {
            role: "user",
            content: `Complete the following code:\n\n${context}`,
          },
        ],
        max_tokens: 100,
        temperature: 0.3,
        n: 3,
      }),
    })

    const data = await response.json()
    return data.choices.map(choice => choice.message.content)
  }

  // 代码审查
  async reviewCode(code: string): Promise<{
    issues: Array<{
      type: 'error' | 'warning' | 'suggestion'
      message: string
      line: number
      suggestion?: string
    }>
    score: number
  }> {
    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-4",
        messages: [
          {
            role: "system",
            content: `You are a code reviewer. Analyze the provided code and identify issues, potential improvements, and best practices violations. Respond in JSON format with issues array and overall score.`,
          },
          {
            role: "user",
            content: `Please review this code:\n\n${code}`,
          },
        ],
        response_format: { type: "json_object" },
        temperature: 0.1,
      }),
    })

    const data = await response.json()
    return JSON.parse(data.choices[0].message.content)
  }

  // 翻译功能
  async translateText(text: string, targetLanguage: string): Promise<string> {
    const response = await fetch(`${this.baseUrl}/chat/completions`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Authorization": `Bearer ${this.apiKey}`,
      },
      body: JSON.stringify({
        model: "gpt-3.5-turbo",
        messages: [
          {
            role: "system",
            content: `You are a translator. Translate the given text to ${targetLanguage}. Provide only the translation without any additional text.`,
          },
          {
            role: "user",
            content: text,
          },
        ],
        max_tokens: 500,
        temperature: 0.3,
      }),
    })

    const data = await response.json()
    return data.choices[0].message.content
  }
}

// 使用示例
const aiAssistant = new AIAssistant(process.env.OPENAI_API_KEY!)

// 在协作编辑器中集成AI功能
function useAIAssistant(documentId: string) {
  const [isGenerating, setIsGenerating] = useState(false)

  const generateSummary = async (content: string) => {
    setIsGenerating(true)
    try {
      const summary = await aiAssistant.generateSummary(content)
      return summary
    } finally {
      setIsGenerating(false)
    }
  }

  const getCodeCompletions = async (context: string, cursorPosition: number) => {
    return aiAssistant.autoComplete(context, cursorPosition)
  }

  const reviewDocument = async (content: string) => {
    return aiAssistant.reviewCode(content)
  }

  return {
    generateSummary,
    getCodeCompletions,
    reviewDocument,
    isGenerating,
  }
}
```

## 总结

### 项目特色

1. **实时协作功能**
   - 多人同时编辑文档
   - 实时光标位置同步
   - 冲突检测和解决
   - 版本控制和历史记录

2. **丰富的通信功能**
   - 实时聊天系统
   - 文件共享和预览
   - 视频会议集成
   - 推送通知支持

3. **高性能架构**
   - WebSocket实时通信
   - 消息批处理优化
   - 数据压缩和缓存
   - 水平扩展支持

4. **用户体验优化**
   - 离线编辑支持
   - 实时状态同步
   - 智能错误恢复
   - 响应式设计

### 技术亮点

1. **Y.js集成**
   - CRDT数据同步
   - 冲突自由解决
   - 高性能文档操作
   - 历史记录管理

2. **Socket.IO优化**
   - 连接池管理
   - 消息批处理
   - 自动重连机制
   - 错误处理策略

3. **WebRTC支持**
   - 点对点视频通话
   - 屏幕共享功能
   - 实时媒体流处理
   - 低延迟通信

4. **AI功能集成**
   - 智能文本补全
   - 代码审查建议
   - 自动文档摘要
   - 多语言翻译

### 实施建议

1. **分阶段开发**
   - 先实现基础协作功能
   - 逐步添加高级特性
   - 持续性能优化

2. **测试策略**
   - 单元测试核心功能
   - 集成测试实时通信
   - E2E测试用户流程
   - 性能测试和优化

3. **监控和维护**
   - 实时性能监控
   - 错误日志收集
   - 用户行为分析
   - 系统健康检查

### 扩展方向

1. **移动端支持**
   - React Native应用
   - PWA功能
   - 移动端优化

2. **企业级功能**
   - SSO集成
   - 权限管理
   - 审计日志
   - 数据加密

3. **AI增强功能**
   - 智能内容推荐
   - 自动分类整理
   - 智能搜索
   - 语音识别

---

通过这个实时协作应用项目，你已经掌握了构建现代化实时Web应用的完整技能。这个项目展示了Next.js 15在实时通信、协作编辑、视频会议等方面的强大能力，可以作为其他实时应用的基础模板。记住关注性能优化、用户体验和安全性，持续迭代改进产品功能。