# Go实时聊天应用实战项目

## 项目概述
本项目将构建一个高性能的实时聊天应用，包含用户认证、私聊、群聊、消息持久化、在线状态等功能。通过这个项目，您将学习如何使用Go语言构建实时Web应用，掌握WebSocket、长轮询、消息队列等关键技术。

## 技术栈
- **Go 1.21+**: 主要开发语言
- **Gin框架**: HTTP服务器和REST API
- **Gorilla WebSocket**: WebSocket连接管理
- **Redis**: 缓存、发布订阅和会话管理
- **PostgreSQL**: 消息持久化存储
- **JWT**: 用户认证
- **Socket.IO**: 客户端实时通信（可选）
- **Docker**: 容器化部署
- **Nginx**: 反向代理和负载均衡

## 系统架构

```
┌─────────────────────────────────────────────────────────────┐
│                    Load Balancer (Nginx)                     │
└─────────────────────────────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐   ┌────────▼────────┐   ┌───────▼──────┐
│ Chat Server 1 │   │ Chat Server 2  │   │ Chat Server 3  │
│   (Go/Gin)    │   │   (Go/Gin)    │   │   (Go/Gin)    │
└───────┬──────┘   └────────┬────────┘   └───────┬──────┘
        │                    │                    │
        └────────────────────┼────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
┌───────▼──────┐   ┌────────▼────────┐   ┌───────▼──────┐
│   Redis      │   │  PostgreSQL    │   │  Auth Service │
│ (Pub/Sub)    │   │ (Messages)    │   │  (JWT Auth)   │
└──────────────┘   └─────────────────┘   └──────────────┘
```

## 核心功能

### 1. 用户管理
- 用户注册和登录
- JWT认证和授权
- 用户状态管理（在线/离线）
- 用户资料管理

### 2. 消息功能
- 实时消息发送和接收
- 私聊和群聊支持
- 消息持久化存储
- 消息历史查询
- 消息状态（已发送、已读）
- 消息撤回和删除

### 3. 群组功能
- 创建和管理群组
- 群成员管理
- 群权限控制
- 群公告和群主设置

### 4. 实时通知
- 在线状态通知
- 消息提醒
- 系统通知
- 推送通知（可选）

## 数据模型设计

### 用户模型
```go
// models/user.go
package models

import (
	"time"
	"gorm.io/gorm"
)

type User struct {
	ID          string    `json:"id" gorm:"primary_key"`
	Username    string    `json:"username" gorm:"unique;not null"`
	Email       string    `json:"email" gorm:"unique;not null"`
	Password    string    `json:"-" gorm:"not null"`
	FirstName   string    `json:"first_name"`
	LastName    string    `json:"last_name"`
	Avatar      string    `json:"avatar"`
	Status      string    `json:"status" gorm:"default:'offline'"`
	LastSeen    time.Time `json:"last_seen"`
	IsActive    bool      `json:"is_active" gorm:"default:true"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	DeletedAt   gorm.DeletedAt `json:"-" gorm:"index"`
}

type UserSession struct {
	ID        string    `json:"id" gorm:"primary_key"`
	UserID    string    `json:"user_id" gorm:"not null"`
	Token     string    `json:"token" gorm:"unique;not null"`
	ExpiresAt time.Time `json:"expires_at"`
	CreatedAt time.Time `json:"created_at"`
}

// 用户状态枚举
const (
	UserStatusOffline  = "offline"
	UserStatusOnline   = "online"
	UserStatusBusy     = "busy"
	UserStatusAway     = "away"
)
```

### 消息模型
```go
// models/message.go
package models

import (
	"time"
	"gorm.io/gorm"
)

type Message struct {
	ID         string    `json:"id" gorm:"primary_key"`
	SenderID   string    `json:"sender_id" gorm:"not null"`
	ReceiverID string    `json:"receiver_id" gorm:"index"`
	GroupID    string    `json:"group_id" gorm:"index"`
	Content    string    `json:"content" gorm:"not null"`
	MessageType string   `json:"message_type" gorm:"default:'text'"`
	Status     string    `json:"status" gorm:"default:'sent'"`
	IsRead     bool      `json:"is_read" gorm:"default:false"`
	IsDeleted  bool      `json:"is_deleted" gorm:"default:false"`
	ReadAt     time.Time `json:"read_at"`
	CreatedAt  time.Time `json:"created_at"`
	UpdatedAt  time.Time `json:"updated_at"`
	DeletedAt  gorm.DeletedAt `json:"-" gorm:"index"`

	// 关联
	Sender   User   `json:"sender" gorm:"foreignKey:SenderID"`
	Receiver User   `json:"receiver" gorm:"foreignKey:ReceiverID"`
	Group    Group  `json:"group" gorm:"foreignKey:GroupID"`
}

// 消息状态枚举
const (
	MessageStatusSent    = "sent"
	MessageStatusDelivered = "delivered"
	MessageStatusRead    = "read"
)

// 消息类型枚举
const (
	MessageTypeText  = "text"
	MessageTypeImage = "image"
	MessageTypeFile  = "file"
	MessageTypeSystem = "system"
)
```

### 群组模型
```go
// models/group.go
package models

import (
	"time"
	"gorm.io/gorm"
)

type Group struct {
	ID          string    `json:"id" gorm:"primary_key"`
	Name        string    `json:"name" gorm:"not null"`
	Description string    `json:"description"`
	Avatar      string    `json:"avatar"`
	OwnerID     string    `json:"owner_id" gorm:"not null"`
	MaxMembers  int       `json:"max_members" gorm:"default:100"`
	IsPrivate   bool      `json:"is_private" gorm:"default:false"`
	CreatedAt   time.Time `json:"created_at"`
	UpdatedAt   time.Time `json:"updated_at"`
	DeletedAt   gorm.DeletedAt `json:"-" gorm:"index"`

	// 关联
	Owner    User           `json:"owner" gorm:"foreignKey:OwnerID"`
	Members  []GroupMember  `json:"members" gorm:"foreignKey:GroupID"`
	Messages []Message      `json:"messages" gorm:"foreignKey:GroupID"`
}

type GroupMember struct {
	ID        string    `json:"id" gorm:"primary_key"`
	GroupID   string    `json:"group_id" gorm:"not null"`
	UserID    string    `json:"user_id" gorm:"not null"`
	Role      string    `json:"role" gorm:"default:'member'"`
	JoinedAt  time.Time `json:"joined_at"`
	IsAdmin   bool      `json:"is_admin" gorm:"default:false"`
	IsActive  bool      `json:"is_active" gorm:"default:true"`
	CreatedAt time.Time `json:"created_at"`
	UpdatedAt time.Time `json:"updated_at"`

	// 关联
	Group Group `json:"group" gorm:"foreignKey:GroupID"`
	User  User  `json:"user" gorm:"foreignKey:UserID"`
}

// 群组成员角色枚举
const (
	GroupRoleOwner  = "owner"
	GroupRoleAdmin  = "admin"
	GroupRoleMember = "member"
)
```

## WebSocket连接管理

### Hub设计
```go
// websocket/hub.go
package websocket

import (
	"sync"
	"time"
)

type Hub struct {
	// 注册的客户端
	clients map[*Client]bool

	// 用户ID到客户端的映射
	userClients map[string][]*Client

	// 群组ID到客户端的映射
	groupClients map[string][]*Client

	// 广播消息
	broadcast chan []byte

	// 注册/注销客户端
	register   chan *Client
	unregister chan *Client

	// 用户状态更新
	userStatus chan UserStatusUpdate

	// 消息发送队列
	messageQueue chan Message

	// 互斥锁
	mu sync.RWMutex

	// 依赖服务
	userService    UserService
	messageService MessageService
	groupService   GroupService
}

type UserStatusUpdate struct {
	UserID string `json:"user_id"`
	Status string `json:"status"`
}

type Message struct {
	Type    string      `json:"type"`
	Content interface{} `json:"content"`
	From    string      `json:"from"`
	To      string      `json:"to"`
	GroupID string      `json:"group_id,omitempty"`
}

func NewHub(userService UserService, messageService MessageService, groupService GroupService) *Hub {
	return &Hub{
		clients:       make(map[*Client]bool),
		userClients:   make(map[string][]*Client),
		groupClients:  make(map[string][]*Client),
		broadcast:     make(chan []byte, 256),
		register:      make(chan *Client, 256),
		unregister:    make(chan *Client, 256),
		userStatus:    make(chan UserStatusUpdate, 256),
		messageQueue:  make(chan Message, 256),
		userService:   userService,
		messageService: messageService,
		groupService:  groupService,
	}
}

func (h *Hub) Run() {
	ticker := time.NewTicker(30 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case client := <-h.register:
			h.handleClientRegister(client)

		case client := <-h.unregister:
			h.handleClientUnregister(client)

		case message := <-h.broadcast:
			h.handleBroadcast(message)

		case status := <-h.userStatus:
			h.handleUserStatusUpdate(status)

		case msg := <-h.messageQueue:
			h.handleMessage(msg)

		case <-ticker.C:
			h.cleanupInactiveClients()
		}
	}
}

func (h *Hub) handleClientRegister(client *Client) {
	h.mu.Lock()
	defer h.mu.Unlock()

	// 注册客户端
	h.clients[client] = true

	// 添加到用户客户端映射
	if userID := client.userID; userID != "" {
		h.userClients[userID] = append(h.userClients[userID], client)
	}

	// 发送欢迎消息
	welcome := Message{
		Type:    "system",
		Content: "Welcome to chat server",
		From:    "server",
		To:      client.userID,
	}
	client.send <- welcome.encode()

	// 广播用户上线通知
	h.broadcastUserStatus(client.userID, "online")
}

func (h *Hub) handleClientUnregister(client *Client) {
	h.mu.Lock()
	defer h.mu.Unlock()

	if _, ok := h.clients[client]; !ok {
		return
	}

	// 从客户端映射中删除
	delete(h.clients, client)

	// 从用户客户端映射中删除
	if userID := client.userID; userID != "" {
		clients := h.userClients[userID]
		for i, c := range clients {
			if c == client {
				h.userClients[userID] = append(clients[:i], clients[i+1:]...)
				break
			}
		}

		// 如果用户没有其他连接，标记为离线
		if len(h.userClients[userID]) == 0 {
			h.broadcastUserStatus(userID, "offline")
		}
	}

	// 从群组客户端映射中删除
	for groupID, clients := range h.groupClients {
		for i, c := range clients {
			if c == client {
				h.groupClients[groupID] = append(clients[:i], clients[i+1:]...)
				break
			}
		}
	}

	// 关闭发送通道
	close(client.send)
}

func (h *Hub) handleBroadcast(message []byte) {
	h.mu.RLock()
	defer h.mu.RUnlock()

	for client := range h.clients {
		select {
		case client.send <- message:
		default:
			close(client.send)
			delete(h.clients, client)
		}
	}
}

func (h *Hub) handleUserStatusUpdate(status UserStatusUpdate) {
	h.broadcastUserStatus(status.UserID, status.Status)
}

func (h *Hub) handleMessage(msg Message) {
	switch msg.Type {
	case "private":
		h.handlePrivateMessage(msg)
	case "group":
		h.handleGroupMessage(msg)
	case "typing":
		h.handleTypingIndicator(msg)
	case "read":
		h.handleReadReceipt(msg)
	}
}

func (h *Hub) handlePrivateMessage(msg Message) {
	h.mu.RLock()
	defer h.mu.RUnlock()

	// 发送给接收者
	if clients, ok := h.userClients[msg.To]; ok {
		for _, client := range clients {
			select {
			case client.send <- msg.encode():
			default:
				close(client.send)
				delete(h.clients, client)
			}
		}
	}

	// 保存消息到数据库
	h.messageService.SavePrivateMessage(msg.From, msg.To, msg.Content.(string))
}

func (h *Hub) handleGroupMessage(msg Message) {
	h.mu.RLock()
	defer h.mu.RUnlock()

	// 发送给群组成员
	if clients, ok := h.groupClients[msg.GroupID]; ok {
		for _, client := range clients {
			// 不发送给消息发送者
			if client.userID != msg.From {
				select {
				case client.send <- msg.encode():
				default:
					close(client.send)
					delete(h.clients, client)
				}
			}
		}
	}

	// 保存消息到数据库
	h.messageService.SaveGroupMessage(msg.From, msg.GroupID, msg.Content.(string))
}

func (h *Hub) handleTypingIndicator(msg Message) {
	h.mu.RLock()
	defer h.mu.RUnlock()

	// 发送给特定的用户或群组
	if msg.GroupID != "" {
		// 群组打字状态
		if clients, ok := h.groupClients[msg.GroupID]; ok {
			for _, client := range clients {
				if client.userID != msg.From {
					select {
					case client.send <- msg.encode():
					default:
						close(client.send)
						delete(h.clients, client)
					}
				}
			}
		}
	} else {
		// 私聊打字状态
		if clients, ok := h.userClients[msg.To]; ok {
			for _, client := range clients {
				select {
				case client.send <- msg.encode():
				default:
						close(client.send)
						delete(h.clients, client)
					}
				}
			}
		}
	}
}

func (h *Hub) handleReadReceipt(msg Message) {
	// 更新消息状态
	h.messageService.MarkMessageAsRead(msg.Content.(string))

	// 通知消息发送者
	if clients, ok := h.userClients[msg.From]; ok {
		for _, client := range clients {
			select {
			case client.send <- msg.encode():
			default:
				close(client.send)
				delete(h.clients, client)
			}
		}
	}
}

func (h *Hub) broadcastUserStatus(userID, status string) {
	// 更新用户状态
	h.userService.UpdateUserStatus(userID, status)

	// 广播状态更新
	statusMsg := Message{
		Type:    "user_status",
		Content: UserStatusUpdate{UserID: userID, Status: status},
		From:    "system",
	}

	h.mu.RLock()
	// 广播给所有用户（或者只广播给好友/群组成员）
	for client := range h.clients {
		select {
		case client.send <- statusMsg.encode():
		default:
			close(client.send)
			delete(h.clients, client)
		}
	}
	h.mu.RUnlock()
}

func (h *Hub) cleanupInactiveClients() {
	h.mu.Lock()
	defer h.mu.Unlock()

	for client := range h.clients {
		if time.Since(client.lastActivity) > 5*time.Minute {
			h.unregister <- client
		}
	}
}
```

### 客户端连接管理
```go
// websocket/client.go
package websocket

import (
	"encoding/json"
	"log"
	"net/http"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

var (
	upgrader = websocket.Upgrader{
		ReadBufferSize:  1024,
		WriteBufferSize: 1024,
		CheckOrigin: func(r *http.Request) bool {
			return true // 生产环境中应该验证origin
		},
	}
)

type Client struct {
	hub         *Hub
	conn        *websocket.Conn
	send        chan []byte
	userID      string
	lastActivity time.Time
	mu          sync.Mutex
}

func NewClient(hub *Hub, conn *websocket.Conn, userID string) *Client {
	return &Client{
		hub:          hub,
		conn:         conn,
		send:         make(chan []byte, 256),
		userID:       userID,
		lastActivity: time.Now(),
	}
}

func (c *Client) readPump() {
	defer func() {
		c.hub.unregister <- c
		c.conn.Close()
	}()

	for {
		_, message, err := c.conn.ReadMessage()
		if err != nil {
			if websocket.IsUnexpectedCloseError(err, websocket.CloseGoingAway, websocket.CloseAbnormalClosure) {
				log.Printf("error: %v", err)
			}
			break
		}

		c.mu.Lock()
		c.lastActivity = time.Now()
		c.mu.Unlock()

		var msg Message
		if err := json.Unmarshal(message, &msg); err != nil {
			log.Printf("error unmarshaling message: %v", err)
			continue
		}

		// 设置发送者
		msg.From = c.userID

		// 处理消息
		c.hub.messageQueue <- msg
	}
}

func (c *Client) writePump() {
	ticker := time.NewTicker(50 * time.Second)
	defer func() {
		ticker.Stop()
		c.conn.Close()
	}()

	for {
		select {
		case message, ok := <-c.send:
			if !ok {
				c.conn.WriteMessage(websocket.CloseMessage, []byte{})
				return
			}

			if err := c.conn.WriteMessage(websocket.TextMessage, message); err != nil {
				log.Printf("error writing message: %v", err)
				return
			}

		case <-ticker.C:
			if err := c.conn.WriteMessage(websocket.PingMessage, nil); err != nil {
				return
			}
		}
	}
}

func (m *Message) encode() []byte {
	data, _ := json.Marshal(m)
	return data
}
```

## HTTP API设计

### 认证相关API
```go
// handlers/auth.go
package handlers

import (
	"net/http"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
	"golang.org/x/crypto/bcrypt"
)

type AuthHandler struct {
	userService UserService
	jwtSecret   string
}

func NewAuthHandler(userService UserService, jwtSecret string) *AuthHandler {
	return &AuthHandler{
		userService: userService,
		jwtSecret:   jwtSecret,
	}
}

func (h *AuthHandler) Register(c *gin.Context) {
	var req struct {
		Username string `json:"username" binding:"required"`
		Email    string `json:"email" binding:"required,email"`
		Password string `json:"password" binding:"required,min=6"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 检查用户是否已存在
	if exists, _ := h.userService.UserExists(req.Username, req.Email); exists {
		c.JSON(http.StatusConflict, gin.H{"error": "User already exists"})
		return
	}

	// 加密密码
	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(req.Password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}

	// 创建用户
	user := &models.User{
		Username:  req.Username,
		Email:     req.Email,
		Password:  string(hashedPassword),
		Status:    models.UserStatusOffline,
		IsActive:  true,
		CreatedAt: time.Now(),
	}

	if err := h.userService.CreateUser(user); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
		return
	}

	// 生成JWT令牌
	token, err := h.generateJWTToken(user.ID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{
		"user":  user,
		"token": token,
	})
}

func (h *AuthHandler) Login(c *gin.Context) {
	var req struct {
		Email    string `json:"email" binding:"required,email"`
		Password string `json:"password" binding:"required"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 查找用户
	user, err := h.userService.GetUserByEmail(req.Email)
	if err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	// 验证密码
	if err := bcrypt.CompareHashAndPassword([]byte(user.Password), []byte(req.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid credentials"})
		return
	}

	// 生成JWT令牌
	token, err := h.generateJWTToken(user.ID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}

	// 更新用户状态
	h.userService.UpdateUserStatus(user.ID, models.UserStatusOnline)

	c.JSON(http.StatusOK, gin.H{
		"user":  user,
		"token": token,
	})
}

func (h *AuthHandler) generateJWTToken(userID string) (string, error) {
	claims := jwt.MapClaims{
		"user_id": userID,
		"exp":     time.Now().Add(24 * time.Hour).Unix(),
		"iat":     time.Now().Unix(),
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	return token.SignedString([]byte(h.jwtSecret))
}

func (h *AuthHandler) Logout(c *gin.Context) {
	userID := c.MustGet("user_id").(string)

	// 更新用户状态
	h.userService.UpdateUserStatus(userID, models.UserStatusOffline)

	c.JSON(http.StatusOK, gin.H{"message": "Logged out successfully"})
}
```

### 用户相关API
```go
// handlers/user.go
package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type UserHandler struct {
	userService UserService
}

func NewUserHandler(userService UserService) *UserHandler {
	return &UserHandler{
		userService: userService,
	}
}

func (h *UserHandler) GetUserProfile(c *gin.Context) {
	userID := c.MustGet("user_id").(string)

	user, err := h.userService.GetUserByID(userID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"user": user})
}

func (h *UserHandler) UpdateUserProfile(c *gin.Context) {
	userID := c.MustGet("user_id").(string)

	var req struct {
		FirstName string `json:"first_name"`
		LastName  string `json:"last_name"`
		Avatar    string `json:"avatar"`
		Status    string `json:"status"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 更新用户信息
	updates := map[string]interface{}{
		"first_name": req.FirstName,
		"last_name":  req.LastName,
		"avatar":     req.Avatar,
	}

	if req.Status != "" {
		updates["status"] = req.Status
	}

	if err := h.userService.UpdateUser(userID, updates); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update user"})
		return
	}

	user, _ := h.userService.GetUserByID(userID)
	c.JSON(http.StatusOK, gin.H{"user": user})
}

func (h *UserHandler) SearchUsers(c *gin.Context) {
	query := c.Query("q")
	if query == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Search query is required"})
		return
	}

	users, err := h.userService.SearchUsers(query)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to search users"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"users": users})
}

func (h *UserHandler) GetUserContacts(c *gin.Context) {
	userID := c.MustGet("user_id").(string)

	contacts, err := h.userService.GetUserContacts(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get contacts"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"contacts": contacts})
}
```

### 消息相关API
```go
// handlers/message.go
package handlers

import (
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
)

type MessageHandler struct {
	messageService MessageService
	hub           *Hub
}

func NewMessageHandler(messageService MessageService, hub *Hub) *MessageHandler {
	return &MessageHandler{
		messageService: messageService,
		hub:           hub,
	}
}

func (h *MessageHandler) GetMessages(c *gin.Context) {
	userID := c.MustGet("user_id").(string)
	receiverID := c.Param("receiver_id")

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))

	messages, err := h.messageService.GetPrivateMessages(userID, receiverID, page, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get messages"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"messages": messages})
}

func (h *MessageHandler) GetGroupMessages(c *gin.Context) {
	userID := c.MustGet("user_id").(string)
	groupID := c.Param("group_id")

	// 检查用户是否在群组中
	isMember, err := h.messageService.IsGroupMember(userID, groupID)
	if err != nil || !isMember {
		c.JSON(http.StatusForbidden, gin.H{"error": "Not a member of this group"})
		return
	}

	page, _ := strconv.Atoi(c.DefaultQuery("page", "1"))
	limit, _ := strconv.Atoi(c.DefaultQuery("limit", "50"))

	messages, err := h.messageService.GetGroupMessages(groupID, page, limit)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get messages"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"messages": messages})
}

func (h *MessageHandler) MarkMessageAsRead(c *gin.Context) {
	userID := c.MustGet("user_id").(string)
	messageID := c.Param("message_id")

	if err := h.messageService.MarkMessageAsRead(messageID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to mark message as read"})
		return
	}

	// 通知消息发送者
	message, err := h.messageService.GetMessageByID(messageID)
	if err == nil && message.SenderID != userID {
		h.hub.messageQueue <- Message{
			Type:    "read",
			Content: messageID,
			From:    userID,
			To:      message.SenderID,
		}
	}

	c.JSON(http.StatusOK, gin.H{"message": "Message marked as read"})
}

func (h *MessageHandler) DeleteMessage(c *gin.Context) {
	userID := c.MustGet("user_id").(string)
	messageID := c.Param("message_id")

	// 检查消息是否属于用户
	message, err := h.messageService.GetMessageByID(messageID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Message not found"})
		return
	}

	if message.SenderID != userID {
		c.JSON(http.StatusForbidden, gin.H{"error": "Not authorized to delete this message"})
		return
	}

	if err := h.messageService.DeleteMessage(messageID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete message"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Message deleted successfully"})
}
```

### 群组相关API
```go
// handlers/group.go
package handlers

import (
	"net/http"

	"github.com/gin-gonic/gin"
)

type GroupHandler struct {
	groupService  GroupService
	messageService MessageService
	hub          *Hub
}

func NewGroupHandler(groupService GroupService, messageService MessageService, hub *Hub) *GroupHandler {
	return &GroupHandler{
		groupService:  groupService,
		messageService: messageService,
		hub:          hub,
	}
}

func (h *GroupHandler) CreateGroup(c *gin.Context) {
	userID := c.MustGet("user_id").(string)

	var req struct {
		Name        string `json:"name" binding:"required"`
		Description string `json:"description"`
		IsPrivate   bool   `json:"is_private"`
		MaxMembers  int    `json:"max_members"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	group := &models.Group{
		Name:        req.Name,
		Description: req.Description,
		OwnerID:     userID,
		IsPrivate:   req.IsPrivate,
		MaxMembers:  req.MaxMembers,
		CreatedAt:   time.Now(),
	}

	if err := h.groupService.CreateGroup(group); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create group"})
		return
	}

	// 添加创建者为群主
	member := &models.GroupMember{
		GroupID:  group.ID,
		UserID:   userID,
		Role:     models.GroupRoleOwner,
		IsAdmin:  true,
		JoinedAt: time.Now(),
	}

	if err := h.groupService.AddGroupMember(member); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add group member"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"group": group})
}

func (h *GroupHandler) GetGroups(c *gin.Context) {
	userID := c.MustGet("user_id").(string)

	groups, err := h.groupService.GetUserGroups(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get groups"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"groups": groups})
}

func (h *GroupHandler) GetGroupInfo(c *gin.Context) {
	userID := c.MustGet("user_id").(string)
	groupID := c.Param("group_id")

	// 检查用户是否在群组中
	isMember, err := h.groupService.IsGroupMember(userID, groupID)
	if err != nil || !isMember {
		c.JSON(http.StatusForbidden, gin.H{"error": "Not a member of this group"})
		return
	}

	group, err := h.groupService.GetGroupByID(groupID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"group": group})
}

func (h *GroupHandler) AddGroupMember(c *gin.Context) {
	userID := c.MustGet("user_id").(string)
	groupID := c.Param("group_id")

	var req struct {
		UserID string `json:"user_id" binding:"required"`
		Role   string `json:"role"`
	}

	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// 检查用户是否有权限添加成员
	isAdmin, err := h.groupService.IsGroupAdmin(userID, groupID)
	if err != nil || !isAdmin {
		c.JSON(http.StatusForbidden, gin.H{"error": "Not authorized to add members"})
		return
	}

	member := &models.GroupMember{
		GroupID:  groupID,
		UserID:   req.UserID,
		Role:     req.Role,
		JoinedAt: time.Now(),
	}

	if err := h.groupService.AddGroupMember(member); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to add group member"})
		return
	}

	// 通知群组成员
	h.hub.messageQueue <- Message{
		Type:    "group_member_added",
		Content: map[string]interface{}{
			"group_id": groupID,
			"user_id":  req.UserID,
			"role":     req.Role,
		},
		From:    userID,
		GroupID: groupID,
	}

	c.JSON(http.StatusOK, gin.H{"message": "Member added successfully"})
}

func (h *GroupHandler) RemoveGroupMember(c *gin.Context) {
	userID := c.MustGet("user_id").(string)
	groupID := c.Param("group_id")
	targetUserID := c.Param("user_id")

	// 检查权限
	isAdmin, err := h.groupService.IsGroupAdmin(userID, groupID)
	if err != nil || (!isAdmin && userID != targetUserID) {
		c.JSON(http.StatusForbidden, gin.H{"error": "Not authorized to remove this member"})
		return
	}

	if err := h.groupService.RemoveGroupMember(groupID, targetUserID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to remove group member"})
		return
	}

	// 通知群组成员
	h.hub.messageQueue <- Message{
		Type:    "group_member_removed",
		Content: map[string]interface{}{
			"group_id": groupID,
			"user_id":  targetUserID,
		},
		From:    userID,
		GroupID: groupID,
	}

	c.JSON(http.StatusOK, gin.H{"message": "Member removed successfully"})
}

func (h *GroupHandler) LeaveGroup(c *gin.Context) {
	userID := c.MustGet("user_id").(string)
	groupID := c.Param("group_id")

	// 检查用户是否在群组中
	isMember, err := h.groupService.IsGroupMember(userID, groupID)
	if err != nil || !isMember {
		c.JSON(http.StatusForbidden, gin.H{"error": "Not a member of this group"})
		return
	}

	// 群主不能直接离开群组
	group, err := h.groupService.GetGroupByID(groupID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Group not found"})
		return
	}

	if group.OwnerID == userID {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Group owner cannot leave group directly"})
		return
	}

	if err := h.groupService.RemoveGroupMember(groupID, userID); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to leave group"})
		return
	}

	// 通知群组成员
	h.hub.messageQueue <- Message{
		Type:    "group_member_left",
		Content: map[string]interface{}{
			"group_id": groupID,
			"user_id":  userID,
		},
		From:    userID,
		GroupID: groupID,
	}

	c.JSON(http.StatusOK, gin.H{"message": "Left group successfully"})
}
```

## WebSocket路由设置
```go
// routes/websocket.go
package routes

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/your-username/chat-app/websocket"
)

func SetupWebSocketRoutes(r *gin.Engine, hub *websocket.Hub, authService AuthService) {
	// WebSocket连接端点
	r.GET("/ws", func(c *gin.Context) {
		// 从查询参数中获取token
		token := c.Query("token")
		if token == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Token is required"})
			return
		}

		// 验证token
		userID, err := authService.ValidateToken(token)
		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
			return
		}

		// 升级HTTP连接为WebSocket连接
		conn, err := websocket.Upgrade(c.Writer, c.Request, nil)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to upgrade connection"})
			return
		}

		// 创建客户端
		client := websocket.NewClient(hub, conn, userID)

		// 注册客户端
		hub.Register <- client

		// 启动读写goroutine
		go client.WritePump()
		go client.ReadPump()
	})

	// 获取在线用户列表
	r.GET("/ws/online-users", func(c *gin.Context) {
		userID := c.MustGet("user_id").(string)

		onlineUsers := hub.GetOnlineUsers(userID)
		c.JSON(http.StatusOK, gin.H{"online_users": onlineUsers})
	})
}
```

## 中间件设置
```go
// middleware/auth.go
package middleware

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/golang-jwt/jwt/v5"
)

func AuthMiddleware(jwtSecret string) gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header is required"})
			c.Abort()
			return
		}

		// 解析Bearer token
		tokenString := strings.TrimPrefix(authHeader, "Bearer ")
		if tokenString == authHeader {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Bearer token is required"})
			c.Abort()
			return
		}

		// 验证token
		token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
			return []byte(jwtSecret), nil
		})

		if err != nil {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
			c.Abort()
			return
		}

		if !token.Valid {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
			c.Abort()
			return
		}

		// 获取claims
		claims, ok := token.Claims.(jwt.MapClaims)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token claims"})
			c.Abort()
			return
		}

		// 设置用户ID到上下文
		userID, ok := claims["user_id"].(string)
		if !ok {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid user ID in token"})
			c.Abort()
			return
		}

		c.Set("user_id", userID)
		c.Next()
	}
}

func CORSMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		c.Header("Access-Control-Allow-Origin", "*")
		c.Header("Access-Control-Allow-Credentials", "true")
		c.Header("Access-Control-Allow-Headers", "Content-Type, Content-Length, Accept-Encoding, X-CSRF-Token, Authorization, accept, origin, Cache-Control, X-Requested-With")
		c.Header("Access-Control-Allow-Methods", "POST, OPTIONS, GET, PUT, DELETE")

		if c.Request.Method == "OPTIONS" {
			c.AbortWithStatus(204)
			return
		}

		c.Next()
	}
}
```

## Redis发布订阅集成

### Redis消息发布
```go
// redis/publisher.go
package redis

import (
	"context"
	"encoding/json"
	"log"

	"github.com/go-redis/redis/v8"
)

type RedisPublisher struct {
	client *redis.Client
}

func NewRedisPublisher(addr string) *RedisPublisher {
	return &RedisPublisher{
		client: redis.NewClient(&redis.Options{
			Addr: addr,
		}),
	}
}

func (p *RedisPublisher) PublishMessage(ctx context.Context, channel string, message interface{}) error {
	data, err := json.Marshal(message)
	if err != nil {
		return err
	}

	return p.client.Publish(ctx, channel, data).Err()
}

func (p *RedisPublisher) PublishUserStatus(ctx context.Context, userID, status string) error {
	message := map[string]interface{}{
		"type":    "user_status",
		"user_id": userID,
		"status":  status,
	}

	return p.PublishMessage(ctx, "user_status", message)
}

func (p *RedisPublisher) PublishMessageEvent(ctx context.Context, eventType string, message interface{}) error {
	payload := map[string]interface{}{
		"type":    eventType,
		"message": message,
	}

	return p.PublishMessage(ctx, "messages", payload)
}
```

### Redis消息订阅
```go
// redis/subscriber.go
package redis

import (
	"context"
	"encoding/json"
	"log"

	"github.com/go-redis/redis/v8"
	"github.com/your-username/chat-app/websocket"
)

type RedisSubscriber struct {
	client *redis.Client
	hub    *websocket.Hub
}

func NewRedisSubscriber(addr string, hub *websocket.Hub) *RedisSubscriber {
	return &RedisSubscriber{
		client: redis.NewClient(&redis.Options{
			Addr: addr,
		}),
		hub: hub,
	}
}

func (s *RedisSubscriber) Start(ctx context.Context) {
	pubsub := s.client.Subscribe(ctx, "user_status", "messages")
	defer pubsub.Close()

	ch := pubsub.Channel()
	for {
		select {
		case <-ctx.Done():
			return
		case msg := <-ch:
			s.handleMessage(ctx, msg)
		}
	}
}

func (s *RedisSubscriber) handleMessage(ctx context.Context, msg *redis.Message) {
	var payload map[string]interface{}
	if err := json.Unmarshal([]byte(msg.Payload), &payload); err != nil {
		log.Printf("Failed to unmarshal Redis message: %v", err)
		return
	}

	switch msg.Channel {
	case "user_status":
		s.handleUserStatus(payload)
	case "messages":
		s.handleMessageEvent(payload)
	}
}

func (s *RedisSubscriber) handleUserStatus(payload map[string]interface{}) {
	userID, ok := payload["user_id"].(string)
	if !ok {
		return
	}

	status, ok := payload["status"].(string)
	if !ok {
		return
	}

	// 更新Hub中的用户状态
	s.hub.UserStatus <- websocket.UserStatusUpdate{
		UserID: userID,
		Status: status,
	}
}

func (s *RedisSubscriber) handleMessageEvent(payload map[string]interface{}) {
	eventType, ok := payload["type"].(string)
	if !ok {
		return
	}

	message, ok := payload["message"].(map[string]interface{})
	if !ok {
		return
	}

	// 转换为WebSocket消息格式
	wsMessage := websocket.Message{
		Type:    eventType,
		Content: message,
	}

	// 发送到Hub
	s.hub.Broadcast <- wsMessage.encode()
}
```

## 服务层实现

### 用户服务
```go
// services/user_service.go
package services

import (
	"context"
	"time"

	"gorm.io/gorm"
)

type UserService struct {
	db *gorm.DB
}

func NewUserService(db *gorm.DB) *UserService {
	return &UserService{db: db}
}

func (s *UserService) CreateUser(user *models.User) error {
	return s.db.Create(user).Error
}

func (s *UserService) GetUserByID(id string) (*models.User, error) {
	var user models.User
	err := s.db.First(&user, "id = ?", id).Error
	return &user, err
}

func (s *UserService) GetUserByEmail(email string) (*models.User, error) {
	var user models.User
	err := s.db.First(&user, "email = ?", email).Error
	return &user, err
}

func (s *UserService) UpdateUser(id string, updates map[string]interface{}) error {
	return s.db.Model(&models.User{}).Where("id = ?", id).Updates(updates).Error
}

func (s *UserService) UpdateUserStatus(id string, status string) error {
	return s.db.Model(&models.User{}).Where("id = ?", id).Updates(map[string]interface{}{
		"status":     status,
		"last_seen":  time.Now(),
	}).Error
}

func (s *UserService) UserExists(username, email string) (bool, error) {
	var count int64
	err := s.db.Model(&models.User{}).Where("username = ? OR email = ?", username, email).Count(&count).Error
	return count > 0, err
}

func (s *UserService) SearchUsers(query string) ([]*models.User, error) {
	var users []*models.User
	err := s.db.Where("username LIKE ? OR email LIKE ? OR first_name LIKE ? OR last_name LIKE ?",
		"%"+query+"%", "%"+query+"%", "%"+query+"%", "%"+query+"%").Find(&users).Error
	return users, err
}

func (s *UserService) GetUserContacts(userID string) ([]*models.User, error) {
	var contacts []*models.User
	// 这里应该查询用户的好友列表，简化实现
	err := s.db.Where("id != ?", userID).Limit(50).Find(&contacts).Error
	return contacts, err
}
```

### 消息服务
```go
// services/message_service.go
package services

import (
	"context"
	"time"

	"gorm.io/gorm"
)

type MessageService struct {
	db *gorm.DB
}

func NewMessageService(db *gorm.DB) *MessageService {
	return &MessageService{db: db}
}

func (s *MessageService) SavePrivateMessage(senderID, receiverID, content string) error {
	message := &models.Message{
		SenderID:   senderID,
		ReceiverID: receiverID,
		Content:    content,
		MessageType: models.MessageTypeText,
		Status:     models.MessageStatusSent,
		CreatedAt:  time.Now(),
	}

	return s.db.Create(message).Error
}

func (s *MessageService) SaveGroupMessage(senderID, groupID, content string) error {
	message := &models.Message{
		SenderID:   senderID,
		GroupID:    groupID,
		Content:    content,
		MessageType: models.MessageTypeText,
		Status:     models.MessageStatusSent,
		CreatedAt:  time.Now(),
	}

	return s.db.Create(message).Error
}

func (s *MessageService) GetPrivateMessages(userID, receiverID string, page, limit int) ([]*models.Message, error) {
	var messages []*models.Message
	offset := (page - 1) * limit

	err := s.db.Where("((sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)) AND is_deleted = false",
		userID, receiverID, receiverID, userID).
		Order("created_at DESC").
		Limit(limit).
		Offset(offset).
		Find(&messages).Error

	return messages, err
}

func (s *MessageService) GetGroupMessages(groupID string, page, limit int) ([]*models.Message, error) {
	var messages []*models.Message
	offset := (page - 1) * limit

	err := s.db.Where("group_id = ? AND is_deleted = false", groupID).
		Order("created_at DESC").
		Limit(limit).
		Offset(offset).
		Find(&messages).Error

	return messages, err
}

func (s *MessageService) MarkMessageAsRead(messageID string) error {
	return s.db.Model(&models.Message{}).Where("id = ?", messageID).Updates(map[string]interface{}{
		"status":  models.MessageStatusRead,
		"is_read": true,
		"read_at": time.Now(),
	}).Error
}

func (s *MessageService) DeleteMessage(messageID string) error {
	return s.db.Model(&models.Message{}).Where("id = ?", messageID).Update("is_deleted", true).Error
}

func (s *MessageService) GetMessageByID(messageID string) (*models.Message, error) {
	var message models.Message
	err := s.db.First(&message, "id = ? AND is_deleted = false", messageID).Error
	return &message, err
}

func (s *MessageService) IsGroupMember(userID, groupID string) (bool, error) {
	var count int64
	err := s.db.Model(&models.GroupMember{}).Where("user_id = ? AND group_id = ? AND is_active = true", userID, groupID).Count(&count).Error
	return count > 0, err
}
```

### 群组服务
```go
// services/group_service.go
package services

import (
	"context"
	"time"

	"gorm.io/gorm"
)

type GroupService struct {
	db *gorm.DB
}

func NewGroupService(db *gorm.DB) *GroupService {
	return &GroupService{db: db}
}

func (s *GroupService) CreateGroup(group *models.Group) error {
	return s.db.Create(group).Error
}

func (s *GroupService) GetGroupByID(id string) (*models.Group, error) {
	var group models.Group
	err := s.db.Preload("Owner").Preload("Members.User").First(&group, "id = ?", id).Error
	return &group, err
}

func (s *GroupService) GetUserGroups(userID string) ([]*models.Group, error) {
	var groups []*models.Group
	err := s.db.Joins("JOIN group_members ON groups.id = group_members.group_id").
		Where("group_members.user_id = ? AND group_members.is_active = true", userID).
		Preload("Owner").
		Find(&groups).Error
	return groups, err
}

func (s *GroupService) AddGroupMember(member *models.GroupMember) error {
	return s.db.Create(member).Error
}

func (s *GroupService) RemoveGroupMember(groupID, userID string) error {
	return s.db.Model(&models.GroupMember{}).
		Where("group_id = ? AND user_id = ?", groupID, userID).
		Update("is_active", false).Error
}

func (s *GroupService) IsGroupMember(userID, groupID string) (bool, error) {
	var count int64
	err := s.db.Model(&models.GroupMember{}).Where("user_id = ? AND group_id = ? AND is_active = true", userID, groupID).Count(&count).Error
	return count > 0, err
}

func (s *GroupService) IsGroupAdmin(userID, groupID string) (bool, error) {
	var member models.GroupMember
	err := s.db.Where("user_id = ? AND group_id = ? AND is_active = true", userID, groupID).First(&member).Error
	if err != nil {
		return false, err
	}

	return member.IsAdmin || member.Role == models.GroupRoleOwner, nil
}
```

## Docker部署

### Dockerfile
```dockerfile
# Dockerfile
FROM golang:1.21-alpine AS builder

WORKDIR /app

# 安装依赖
RUN apk add --no-cache git

# 复制go mod文件
COPY go.mod go.sum ./
RUN go mod download

# 复制源代码
COPY . .

# 构建应用
RUN CGO_ENABLED=0 GOOS=linux go build -o main .

# 最终镜像
FROM alpine:latest

# 安装ca-certificates
RUN apk --no-cache add ca-certificates tzdata

WORKDIR /root/

# 复制二进制文件
COPY --from=builder /app/main .
COPY --from=builder /app/config ./config

# 暴露端口
EXPOSE 8080

# 运行应用
CMD ["./main"]
```

### Docker Compose
```yaml
# docker-compose.yml
version: '3.8'

services:
  # Chat应用
  chat-app:
    build: .
    ports:
      - "8080:8080"
    environment:
      - DB_HOST=postgres
      - DB_PORT=5432
      - DB_USER=postgres
      - DB_PASSWORD=postgres
      - DB_NAME=chat_app
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - JWT_SECRET=your-secret-key
    depends_on:
      - postgres
      - redis
    networks:
      - chat-network

  # PostgreSQL数据库
  postgres:
    image: postgres:15-alpine
    environment:
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=postgres
      - POSTGRES_DB=chat_app
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
    networks:
      - chat-network

  # Redis缓存
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    networks:
      - chat-network

  # Nginx反向代理
  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - chat-app
    networks:
      - chat-network

volumes:
  postgres_data:
  redis_data:

networks:
  chat-network:
    driver: bridge
```

### Nginx配置
```nginx
# nginx.conf
events {
    worker_connections 1024;
}

http {
    upstream chat_app {
        server chat-app:8080;
    }

    server {
        listen 80;
        server_name localhost;

        # HTTP -> HTTPS重定向（生产环境）
        # return 301 https://$server_name$request_uri;

        # 静态文件
        location /static/ {
            alias /app/static/;
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # WebSocket代理
        location /ws {
            proxy_pass http://chat_app;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # API代理
        location /api/ {
            proxy_pass http://chat_app;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # 前端应用
        location / {
            root /app/frontend;
            try_files $uri $uri/ /index.html;
            expires 1h;
            add_header Cache-Control "public";
        }
    }

    # HTTPS配置（生产环境）
    # server {
    #     listen 443 ssl http2;
    #     server_name localhost;
    #
    #     ssl_certificate /etc/nginx/ssl/cert.pem;
    #     ssl_certificate_key /etc/nginx/ssl/key.pem;
    #
    #     # 其他配置同上
    # }
}
```

## 测试

### 单元测试
```go
// services/user_service_test.go
package services

import (
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/suite"
	"gorm.io/driver/postgres"
	"gorm.io/gorm"
)

type UserServiceSuite struct {
	suite.Suite
	db         *gorm.DB
	service    *UserService
	cleanupDB  func()
}

func (suite *UserServiceSuite) SetupSuite() {
	// 创建测试数据库
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
	suite.NoError(err)
	suite.db = db

	// 自动迁移
	suite.NoError(db.AutoMigrate(&models.User{}))

	suite.service = NewUserService(db)

	suite.cleanupDB = func() {
		db.Exec("DELETE FROM users")
	}
}

func (suite *UserServiceSuite) TearDownSuite() {
	suite.cleanupDB()
}

func (suite *UserServiceSuite) TestCreateUser() {
	user := &models.User{
		Username:  "testuser",
		Email:     "test@example.com",
		Password:  "hashedpassword",
		Status:    models.UserStatusOffline,
		IsActive:  true,
		CreatedAt: time.Now(),
	}

	err := suite.service.CreateUser(user)
	suite.NoError(err)
	suite.NotEmpty(user.ID)

	// 验证用户是否创建成功
	retrieved, err := suite.service.GetUserByID(user.ID)
	suite.NoError(err)
	suite.Equal(user.Username, retrieved.Username)
	suite.Equal(user.Email, retrieved.Email)
}

func (suite *UserServiceSuite) TestGetUserByEmail() {
	user := &models.User{
		Username:  "testuser2",
		Email:     "test2@example.com",
		Password:  "hashedpassword",
		Status:    models.UserStatusOffline,
		IsActive:  true,
		CreatedAt: time.Now(),
	}

	suite.NoError(suite.service.CreateUser(user))

	retrieved, err := suite.service.GetUserByEmail(user.Email)
	suite.NoError(err)
	suite.Equal(user.ID, retrieved.ID)
	suite.Equal(user.Username, retrieved.Username)
}

func (suite *UserServiceSuite) TestUpdateUserStatus() {
	user := &models.User{
		Username:  "testuser3",
		Email:     "test3@example.com",
		Password:  "hashedpassword",
		Status:    models.UserStatusOffline,
		IsActive:  true,
		CreatedAt: time.Now(),
	}

	suite.NoError(suite.service.CreateUser(user))

	err := suite.service.UpdateUserStatus(user.ID, models.UserStatusOnline)
	suite.NoError(err)

	retrieved, err := suite.service.GetUserByID(user.ID)
	suite.NoError(err)
	suite.Equal(models.UserStatusOnline, retrieved.Status)
}

func TestUserService(t *testing.T) {
	suite.Run(t, new(UserServiceSuite))
}
```

### 集成测试
```go
// integration/chat_integration_test.go
package integration

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/gorilla/websocket"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/suite"
)

type ChatIntegrationSuite struct {
	suite.Suite
	server       *httptest.Server
	router       *gin.Engine
	user1Token   string
	user2Token   string
	user1ID      string
	user2ID      string
	wsConn1      *websocket.Conn
	wsConn2      *websocket.Conn
}

func (suite *ChatIntegrationSuite) SetupSuite() {
	// 初始化路由
	suite.router = setupRouter()
	suite.server = httptest.NewServer(suite.router)

	// 注册两个用户
	suite.user1Token = suite.registerUser("user1", "user1@example.com")
	suite.user2Token = suite.registerUser("user2", "user2@example.com")

	// 获取用户ID
	suite.user1ID = suite.getUserID(suite.user1Token)
	suite.user2ID = suite.getUserID(suite.user2Token)

	// 建立WebSocket连接
	suite.wsConn1 = suite.createWebSocketConnection(suite.user1Token)
	suite.wsConn2 = suite.createWebSocketConnection(suite.user2Token)
}

func (suite *ChatIntegrationSuite) TearDownSuite() {
	if suite.wsConn1 != nil {
		suite.wsConn1.Close()
	}
	if suite.wsConn2 != nil {
		suite.wsConn2.Close()
	}
	suite.server.Close()
}

func (suite *ChatIntegrationSuite) registerUser(username, email string) string {
	user := map[string]interface{}{
		"username": username,
		"email":    email,
		"password": "password123",
	}

	jsonData, _ := json.Marshal(user)
	resp, err := http.Post(suite.server.URL+"/api/v1/auth/register", "application/json", bytes.NewBuffer(jsonData))
	suite.NoError(err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	suite.NoError(err)

	return response["token"].(string)
}

func (suite *ChatIntegrationSuite) getUserID(token string) string {
	req, _ := http.NewRequest("GET", suite.server.URL+"/api/v1/users/profile", nil)
	req.Header.Set("Authorization", "Bearer "+token)

	resp, err := http.DefaultClient.Do(req)
	suite.NoError(err)
	defer resp.Body.Close()

	var response map[string]interface{}
	err = json.NewDecoder(resp.Body).Decode(&response)
	suite.NoError(err)

	user := response["user"].(map[string]interface{})
	return user["id"].(string)
}

func (suite *ChatIntegrationSuite) createWebSocketConnection(token string) *websocket.Conn {
	url := "ws" + suite.server.URL[4:] + "/ws?token=" + token
	conn, _, err := websocket.DefaultDialer.Dial(url, nil)
	suite.NoError(err)
	return conn
}

func (suite *ChatIntegrationSuite) TestWebSocketConnection() {
	suite.NotNil(suite.wsConn1)
	suite.NotNil(suite.wsConn2)
}

func (suite *ChatIntegrationSuite) TestPrivateMessage() {
	// 发送消息
	message := map[string]interface{}{
		"type":    "private",
		"content": "Hello from user1",
		"to":      suite.user2ID,
	}

	suite.wsConn1.WriteJSON(message)

	// 接收消息
	var received map[string]interface{}
	err := suite.wsConn2.ReadJSON(&received)
	suite.NoError(err)

	suite.Equal("private", received["type"])
	suite.Equal("Hello from user1", received["content"])
	suite.Equal(suite.user1ID, received["from"])
	suite.Equal(suite.user2ID, received["to"])
}

func (suite *ChatIntegrationSuite) TestUserStatusUpdate() {
	// 发送状态更新
	statusUpdate := map[string]interface{}{
		"type":    "user_status",
		"content": map[string]interface{}{
			"user_id": suite.user1ID,
			"status":  "busy",
		},
	}

	suite.wsConn1.WriteJSON(statusUpdate)

	// 验证状态更新
	var received map[string]interface{}
	err := suite.wsConn2.ReadJSON(&received)
	suite.NoError(err)

	suite.Equal("user_status", received["type"])
	content := received["content"].(map[string]interface{})
	suite.Equal(suite.user1ID, content["user_id"])
	suite.Equal("busy", content["status"])
}

func TestChatIntegration(t *testing.T) {
	suite.Run(t, new(ChatIntegrationSuite))
}
```

## 性能优化

### 连接池优化
```go
// database/pool.go
package database

import (
	"context"
	"time"

	"gorm.io/driver/postgres"
	"gorm.io/gorm"
	"gorm.io/gorm/logger"
)

func NewConnectionPool(dsn string) (*gorm.DB, error) {
	db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{
		Logger: logger.Default.LogMode(logger.Silent),
	})
	if err != nil {
		return nil, err
	}

	sqlDB, err := db.DB()
	if err != nil {
		return nil, err
	}

	// 配置连接池
	sqlDB.SetMaxIdleConns(10)           // 最大空闲连接数
	sqlDB.SetMaxOpenConns(100)           // 最大打开连接数
	sqlDB.SetConnMaxLifetime(time.Hour)   // 连接最大生命周期
	sqlDB.SetConnMaxIdleTime(30 * time.Minute) // 连接最大空闲时间

	return db, nil
}
```

### 缓存优化
```go
// cache/layered_cache.go
package cache

import (
	"context"
	"encoding/json"
	"time"

	"github.com/go-redis/redis/v8"
)

type LayeredCache struct {
	localCache  map[string]CacheItem
	redisClient *redis.Client
	mu          sync.RWMutex
}

type CacheItem struct {
	Value      interface{}
	Expiration time.Time
}

func NewLayeredCache(redisAddr string) *LayeredCache {
	return &LayeredCache{
		localCache:  make(map[string]CacheItem),
		redisClient: redis.NewClient(&redis.Options{Addr: redisAddr}),
	}
}

func (c *LayeredCache) Get(ctx context.Context, key string, dest interface{}) error {
	// 首先检查本地缓存
	if item, ok := c.getLocal(key); ok {
		return json.Unmarshal(item.Value.([]byte), dest)
	}

	// 检查Redis缓存
	data, err := c.redisClient.Get(ctx, key).Bytes()
	if err == nil {
		// 缓存到本地
		c.setLocal(key, data, 5*time.Minute)
		return json.Unmarshal(data, dest)
	}

	return err
}

func (c *LayeredCache) Set(ctx context.Context, key string, value interface{}, expiration time.Duration) error {
	data, err := json.Marshal(value)
	if err != nil {
		return err
	}

	// 设置Redis缓存
	err = c.redisClient.Set(ctx, key, data, expiration).Err()
	if err != nil {
		return err
	}

	// 缓存到本地
	c.setLocal(key, data, 5*time.Minute)

	return nil
}

func (c *LayeredCache) getLocal(key string) (CacheItem, bool) {
	c.mu.RLock()
	defer c.mu.RUnlock()

	item, ok := c.localCache[key]
	if !ok {
		return CacheItem{}, false
	}

	if time.Now().After(item.Expiration) {
		return CacheItem{}, false
	}

	return item, true
}

func (c *LayeredCache) setLocal(key string, value []byte, expiration time.Duration) {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.localCache[key] = CacheItem{
		Value:      value,
		Expiration: time.Now().Add(expiration),
	}
}
```

## 监控和日志

### Prometheus监控
```go
// monitoring/metrics.go
package monitoring

import (
	"strconv"
	"time"

	"github.com/prometheus/client_golang/prometheus"
	"github.com/prometheus/client_golang/prometheus/promauto"
)

var (
	// HTTP请求指标
	httpRequestsTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "chat_http_requests_total",
			Help: "Total number of HTTP requests",
		},
		[]string{"method", "endpoint", "status"},
	)

	httpRequestDuration = promauto.NewHistogramVec(
		prometheus.HistogramOpts{
			Name:    "chat_http_request_duration_seconds",
			Help:    "Duration of HTTP requests",
			Buckets: prometheus.DefBuckets,
		},
		[]string{"method", "endpoint"},
	)

	// WebSocket连接指标
	websocketConnections = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "chat_websocket_connections_total",
			Help: "Total number of active WebSocket connections",
		},
	)

	websocketMessagesTotal = promauto.NewCounterVec(
		prometheus.CounterOpts{
			Name: "chat_websocket_messages_total",
			Help: "Total number of WebSocket messages",
		},
		[]string{"type"},
	)

	// 业务指标
	usersTotal = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "chat_users_total",
			Help: "Total number of users",
		},
	)

	messagesTotal = promauto.NewCounter(
		prometheus.CounterOpts{
			Name: "chat_messages_total",
			Help: "Total number of messages sent",
		},
	)

	groupsTotal = promauto.NewGauge(
		prometheus.GaugeOpts{
			Name: "chat_groups_total",
			Help: "Total number of groups",
		},
	)
)

func RecordHTTPRequest(method, endpoint string, status int, duration time.Duration) {
	httpRequestsTotal.WithLabelValues(method, endpoint, strconv.Itoa(status)).Inc()
	httpRequestDuration.WithLabelValues(method, endpoint).Observe(duration.Seconds())
}

func RecordWebSocketConnection(connect bool) {
	if connect {
		websocketConnections.Inc()
	} else {
		websocketConnections.Dec()
	}
}

func RecordWebSocketMessage(messageType string) {
	websocketMessagesTotal.WithLabelValues(messageType).Inc()
}

func UpdateUsersCount(count int) {
	usersTotal.Set(float64(count))
}

func RecordMessage() {
	messagesTotal.Inc()
}

func UpdateGroupsCount(count int) {
	groupsTotal.Set(float64(count))
}
```

### 结构化日志
```go
// logging/logger.go
package logging

import (
	"log/slog"
	"os"
	"time"

	"github.com/lmittmann/tint"
)

type Logger struct {
	*slog.Logger
}

type LogFields map[string]interface{}

func NewLogger(serviceName string) *Logger {
	handler := tint.NewHandler(os.Stdout, &tint.Options{
		Level:      slog.LevelDebug,
		TimeFormat: time.RFC3339,
		AddSource:  true,
	})

	logger := slog.New(handler)
	logger = logger.With("service", serviceName)

	return &Logger{Logger: logger}
}

func (l *Logger) WithFields(fields LogFields) *Logger {
	var args []interface{}
	for key, value := range fields {
		args = append(args, key, value)
	}
	return &Logger{Logger: l.Logger.With(args...)}
}

func (l *Logger) Info(msg string, fields LogFields) {
	if len(fields) > 0 {
		l.Logger.Info(msg, l.slogFields(fields)...)
	} else {
		l.Logger.Info(msg)
	}
}

func (l *Logger) Error(msg string, fields LogFields) {
	if len(fields) > 0 {
		l.Logger.Error(msg, l.slogFields(fields)...)
	} else {
		l.Logger.Error(msg)
	}
}

func (l *Logger) Debug(msg string, fields LogFields) {
	if len(fields) > 0 {
		l.Logger.Debug(msg, l.slogFields(fields)...)
	} else {
		l.Logger.Debug(msg)
	}
}

func (l *Logger) slogFields(fields LogFields) []interface{} {
	var args []interface{}
	for key, value := range fields {
		args = append(args, key, value)
	}
	return args
}
```

## 前端集成

### HTML客户端
```html
<!-- public/index.html -->
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Go Chat App</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: Arial, sans-serif;
            background-color: #f0f0f0;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }

        .chat-container {
            display: flex;
            height: 600px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .sidebar {
            width: 300px;
            border-right: 1px solid #ddd;
            padding: 20px;
            overflow-y: auto;
        }

        .chat-area {
            flex: 1;
            display: flex;
            flex-direction: column;
        }

        .chat-header {
            padding: 20px;
            border-bottom: 1px solid #ddd;
            background-color: #f8f9fa;
        }

        .chat-messages {
            flex: 1;
            padding: 20px;
            overflow-y: auto;
            background-color: #fff;
        }

        .chat-input {
            padding: 20px;
            border-top: 1px solid #ddd;
            background-color: #f8f9fa;
        }

        .user-list {
            list-style: none;
        }

        .user-item {
            padding: 10px;
            border-radius: 4px;
            cursor: pointer;
            margin-bottom: 5px;
        }

        .user-item:hover {
            background-color: #f0f0f0;
        }

        .user-item.active {
            background-color: #007bff;
            color: white;
        }

        .message {
            margin-bottom: 15px;
            padding: 10px;
            border-radius: 8px;
            max-width: 70%;
        }

        .message.sent {
            background-color: #007bff;
            color: white;
            margin-left: auto;
        }

        .message.received {
            background-color: #e9ecef;
            color: #333;
        }

        .input-group {
            display: flex;
            gap: 10px;
        }

        .input-group input {
            flex: 1;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .input-group button {
            padding: 10px 20px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .input-group button:hover {
            background-color: #0056b3;
        }

        .status-indicator {
            width: 8px;
            height: 8px;
            border-radius: 50%;
            display: inline-block;
            margin-right: 5px;
        }

        .status-online {
            background-color: #28a745;
        }

        .status-offline {
            background-color: #dc3545;
        }

        .status-busy {
            background-color: #ffc107;
        }

        .auth-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 20px;
            background-color: white;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }

        .auth-container h2 {
            text-align: center;
            margin-bottom: 20px;
        }

        .form-group {
            margin-bottom: 15px;
        }

        .form-group label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }

        .form-group input {
            width: 100%;
            padding: 10px;
            border: 1px solid #ddd;
            border-radius: 4px;
        }

        .form-group button {
            width: 100%;
            padding: 10px;
            background-color: #007bff;
            color: white;
            border: none;
            border-radius: 4px;
            cursor: pointer;
        }

        .form-group button:hover {
            background-color: #0056b3;
        }

        .hidden {
            display: none;
        }

        .typing-indicator {
            font-style: italic;
            color: #666;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="container">
        <!-- 认证界面 -->
        <div id="auth-container" class="auth-container">
            <h2>Login / Register</h2>
            <div class="form-group">
                <label for="email">Email:</label>
                <input type="email" id="email" placeholder="Enter your email">
            </div>
            <div class="form-group">
                <label for="password">Password:</label>
                <input type="password" id="password" placeholder="Enter your password">
            </div>
            <div class="form-group">
                <button onclick="login()">Login</button>
            </div>
            <div class="form-group">
                <button onclick="register()">Register</button>
            </div>
        </div>

        <!-- 聊天界面 -->
        <div id="chat-container" class="chat-container hidden">
            <div class="sidebar">
                <h3>Users</h3>
                <ul id="user-list" class="user-list">
                    <!-- 用户列表将通过JavaScript动态生成 -->
                </ul>
            </div>
            <div class="chat-area">
                <div class="chat-header">
                    <h3 id="chat-header">Select a user to chat</h3>
                </div>
                <div class="chat-messages" id="chat-messages">
                    <!-- 消息将通过JavaScript动态添加 -->
                </div>
                <div class="chat-input">
                    <div class="input-group">
                        <input type="text" id="message-input" placeholder="Type your message..." onkeypress="handleKeyPress(event)">
                        <button onclick="sendMessage()">Send</button>
                    </div>
                    <div id="typing-indicator" class="typing-indicator hidden"></div>
                </div>
            </div>
        </div>
    </div>

    <script>
        let ws = null;
        let token = null;
        let currentUser = null;
        let selectedUser = null;
        let users = [];

        // 登录功能
        async function login() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;

            try {
                const response = await fetch('/api/v1/auth/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ email, password }),
                });

                const data = await response.json();
                if (response.ok) {
                    token = data.token;
                    currentUser = data.user;
                    initChat();
                } else {
                    alert(data.error);
                }
            } catch (error) {
                console.error('Login error:', error);
                alert('Login failed');
            }
        }

        // 注册功能
        async function register() {
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const username = email.split('@')[0];

            try {
                const response = await fetch('/api/v1/auth/register', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ username, email, password }),
                });

                const data = await response.json();
                if (response.ok) {
                    token = data.token;
                    currentUser = data.user;
                    initChat();
                } else {
                    alert(data.error);
                }
            } catch (error) {
                console.error('Register error:', error);
                alert('Registration failed');
            }
        }

        // 初始化聊天界面
        function initChat() {
            document.getElementById('auth-container').classList.add('hidden');
            document.getElementById('chat-container').classList.remove('hidden');

            // 建立WebSocket连接
            connectWebSocket();

            // 加载用户列表
            loadUsers();
        }

        // 建立WebSocket连接
        function connectWebSocket() {
            const wsUrl = `ws://${window.location.host}/ws?token=${token}`;
            ws = new WebSocket(wsUrl);

            ws.onopen = function() {
                console.log('WebSocket connected');
            };

            ws.onmessage = function(event) {
                const message = JSON.parse(event.data);
                handleWebSocketMessage(message);
            };

            ws.onclose = function() {
                console.log('WebSocket disconnected');
                // 尝试重新连接
                setTimeout(connectWebSocket, 5000);
            };

            ws.onerror = function(error) {
                console.error('WebSocket error:', error);
            };
        }

        // 处理WebSocket消息
        function handleWebSocketMessage(message) {
            switch (message.type) {
                case 'private':
                    if (message.from === selectedUser?.id) {
                        addMessage(message.content, 'received');
                    }
                    break;
                case 'user_status':
                    updateUserStatus(message.content.user_id, message.content.status);
                    break;
                case 'typing':
                    if (message.from === selectedUser?.id) {
                        showTypingIndicator(message.content);
                    }
                    break;
                case 'read':
                    // 处理已读回执
                    break;
            }
        }

        // 加载用户列表
        async function loadUsers() {
            try {
                const response = await fetch('/api/v1/users/contacts', {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                const data = await response.json();
                users = data.contacts;
                updateUserList();
            } catch (error) {
                console.error('Load users error:', error);
            }
        }

        // 更新用户列表
        function updateUserList() {
            const userList = document.getElementById('user-list');
            userList.innerHTML = '';

            users.forEach(user => {
                const li = document.createElement('li');
                li.className = 'user-item';
                li.innerHTML = `
                    <span class="status-indicator status-${user.status}"></span>
                    ${user.username} (${user.email})
                `;
                li.onclick = () => selectUser(user);
                userList.appendChild(li);
            });
        }

        // 选择用户
        function selectUser(user) {
            selectedUser = user;
            document.getElementById('chat-header').textContent = `Chat with ${user.username}`;

            // 高亮选中的用户
            document.querySelectorAll('.user-item').forEach(item => {
                item.classList.remove('active');
            });
            event.target.classList.add('active');

            // 加载聊天历史
            loadChatHistory(user.id);
        }

        // 加载聊天历史
        async function loadChatHistory(userId) {
            try {
                const response = await fetch(`/api/v1/messages/private/${userId}`, {
                    headers: {
                        'Authorization': `Bearer ${token}`,
                    },
                });

                const data = await response.json();
                const messages = data.messages;

                // 清空现有消息
                document.getElementById('chat-messages').innerHTML = '';

                // 显示历史消息
                messages.forEach(message => {
                    const direction = message.sender_id === currentUser.id ? 'sent' : 'received';
                    addMessage(message.content, direction);
                });
            } catch (error) {
                console.error('Load chat history error:', error);
            }
        }

        // 发送消息
        function sendMessage() {
            const input = document.getElementById('message-input');
            const content = input.value.trim();

            if (!content || !selectedUser) return;

            // 发送WebSocket消息
            const message = {
                type: 'private',
                content: content,
                to: selectedUser.id,
            };

            ws.send(JSON.stringify(message));

            // 添加到消息列表
            addMessage(content, 'sent');

            // 清空输入框
            input.value = '';
        }

        // 添加消息到聊天界面
        function addMessage(content, direction) {
            const messagesDiv = document.getElementById('chat-messages');
            const messageDiv = document.createElement('div');
            messageDiv.className = `message ${direction}`;
            messageDiv.textContent = content;
            messagesDiv.appendChild(messageDiv);

            // 滚动到底部
            messagesDiv.scrollTop = messagesDiv.scrollHeight;
        }

        // 更新用户状态
        function updateUserStatus(userId, status) {
            const user = users.find(u => u.id === userId);
            if (user) {
                user.status = status;
                updateUserList();
            }
        }

        // 显示输入指示器
        function showTypingIndicator(content) {
            const indicator = document.getElementById('typing-indicator');
            indicator.textContent = `${content.username} is typing...`;
            indicator.classList.remove('hidden');

            // 3秒后隐藏
            setTimeout(() => {
                indicator.classList.add('hidden');
            }, 3000);
        }

        // 处理回车键
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }

        // 页面加载时检查是否已登录
        window.onload = function() {
            const savedToken = localStorage.getItem('chat_token');
            if (savedToken) {
                token = savedToken;
                // 验证token是否有效
                // 这里应该调用API验证token
                // 为了简化，我们假设token是有效的
                initChat();
            }
        };

        // 保存token到localStorage
        if (token) {
            localStorage.setItem('chat_token', token);
        }
    </script>
</body>
</html>
```

## 项目启动指南

### 1. 环境准备
```bash
# 克隆项目
git clone https://github.com/your-username/go-chat-app.git
cd go-chat-app

# 安装依赖
go mod download

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，设置数据库连接等配置
```

### 2. 启动服务
```bash
# 使用Docker Compose启动所有服务
docker-compose up -d

# 或者手动启动各个服务
# 启动数据库和Redis
docker run -d --name postgres -e POSTGRES_PASSWORD=postgres -p 5432:5432 postgres:15
docker run -d --name redis -p 6379:6379 redis:7

# 启动聊天应用
go run main.go
```

### 3. 测试应用
1. 打开浏览器访问 `http://localhost:8080`
2. 注册两个用户账户
3. 在两个不同的浏览器标签页中登录这两个账户
4. 选择用户进行聊天
5. 测试实时消息传递、状态更新等功能

## 扩展功能

### 1. 文件上传
```go
// handlers/upload.go
package handlers

import (
	"fmt"
	"io"
	"net/http"
	"os"
	"path/filepath"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
)

func (h *MessageHandler) UploadFile(c *gin.Context) {
	userID := c.MustGet("user_id").(string)
	receiverID := c.Param("receiver_id")

	file, header, err := c.Request.FormFile("file")
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to get file"})
		return
	}
	defer file.Close()

	// 生成文件名
	ext := filepath.Ext(header.Filename)
	filename := fmt.Sprintf("%d_%s%s", time.Now().Unix(), userID, ext)

	// 创建上传目录
	uploadDir := "uploads"
	if err := os.MkdirAll(uploadDir, 0755); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create upload directory"})
		return
	}

	// 保存文件
	filePath := filepath.Join(uploadDir, filename)
	out, err := os.Create(filePath)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create file"})
		return
	}
	defer out.Close()

	if _, err := io.Copy(out, file); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
		return
	}

	// 生成文件URL
	fileURL := fmt.Sprintf("/uploads/%s", filename)

	// 发送文件消息
	message := websocket.Message{
		Type:    "private",
		Content: map[string]interface{}{
			"type":     "file",
			"filename": header.Filename,
			"size":     header.Size,
			"url":      fileURL,
		},
		From: userID,
		To:   receiverID,
	}

	h.hub.messageQueue <- message

	c.JSON(http.StatusOK, gin.H{
		"message":   "File uploaded successfully",
		"file_url":  fileURL,
		"file_name": header.Filename,
	})
}
```

### 2. 消息加密
```go
// crypto/encryption.go
package crypto

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"encoding/base64"
	"io"
)

type Encryption struct {
	key []byte
}

func NewEncryption(key string) *Encryption {
	return &Encryption{
		key: []byte(key),
	}
}

func (e *Encryption) Encrypt(plaintext string) (string, error) {
	block, err := aes.NewCipher(e.key)
	if err != nil {
		return "", err
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err = io.ReadFull(rand.Reader, nonce); err != nil {
		return "", err
	}

	ciphertext := gcm.Seal(nonce, nonce, []byte(plaintext), nil)
	return base64.URLEncoding.EncodeToString(ciphertext), nil
}

func (e *Encryption) Decrypt(ciphertext string) (string, error) {
	data, err := base64.URLEncoding.DecodeString(ciphertext)
	if err != nil {
		return "", err
	}

	block, err := aes.NewCipher(e.key)
	if err != nil {
		return "", err
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return "", err
	}

	nonceSize := gcm.NonceSize()
	if len(data) < nonceSize {
		return "", fmt.Errorf("ciphertext too short")
	}

	nonce, ciphertext := data[:nonceSize], data[nonceSize:]
	plaintext, err := gcm.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		return "", err
	}

	return string(plaintext), nil
}
```

### 3. 推送通知
```go
// notifications/push.go
package notifications

import (
	"context"
	"fmt"

	"github.com/appleboy/go-fcm"
)

type PushNotificationService struct {
	fcmClient *fcm.Client
}

func NewPushNotificationService(serverKey string) *PushNotificationService {
	client, err := fcm.NewClient(serverKey)
	if err != nil {
		panic(err)
	}

	return &PushNotificationService{
		fcmClient: client,
	}
}

func (s *PushNotificationService) SendPushNotification(ctx context.Context, token, title, body string, data map[string]string) error {
	message := &fcm.Message{
		Token: token,
		Notification: &fcm.Notification{
			Title: title,
			Body:  body,
		},
		Data: data,
	}

	// 发送消息
	response, err := s.fcmClient.Send(ctx, message)
	if err != nil {
		return err
	}

	if response.Failure > 0 {
		return fmt.Errorf("failed to send push notification to %d devices", response.Failure)
	}

	return nil
}
```

## 总结

通过这个实时聊天应用项目，您将学习到：

1. **WebSocket编程**: 使用Gorilla WebSocket构建实时通信
2. **并发处理**: Go语言的goroutine和channel的强大应用
3. **消息队列**: Redis发布订阅模式的实现
4. **用户认证**: JWT认证和会话管理
5. **数据持久化**: 关系型数据库的设计和操作
6. **实时功能**: 在线状态、打字指示器、消息回执等
7. **性能优化**: 连接池、缓存、消息队列等技术
8. **部署运维**: Docker容器化部署和Nginx配置
9. **监控和日志**: 完整的监控和日志系统
10. **前端集成**: WebSocket客户端的实现

这个项目展示了Go语言在实时Web应用开发中的强大能力，通过合理的设计模式和最佳实践，可以构建出高性能、可扩展的实时通信系统。

*最后更新: 2025年9月*