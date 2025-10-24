# Go集成测试详解

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `testing/quality-assurance` |
| **难度** | ⭐⭐⭐ |
| **标签** | `#testing` `#integration-testing` `#quality-assurance` `#testing-strategies` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 概述
集成测试是验证多个组件或系统协同工作是否正常的重要测试手段。与单元测试不同，集成测试关注的是组件之间的交互、数据流和整体功能。本指南将详细介绍Go语言集成测试的各个方面，包括测试策略、工具使用和最佳实践。

## 集成测试基础

### 什么是集成测试
集成测试是验证多个独立模块、服务或系统协同工作是否正常的测试方法。它介于单元测试和端到端测试之间，主要关注：

- 组件间的接口和交互
- 数据流的正确性
- 外部依赖的集成
- 业务逻辑的端到端验证

### 集成测试的重要性
- **发现接口问题**: 识别组件间接口不匹配
- **验证集成点**: 确保外部依赖正确集成
- **测试数据流**: 验证数据在不同组件间的传递
- **模拟真实环境**: 在接近生产环境中测试

## 集成测试策略

### 1. 测试金字塔

```
        /\
       /  \
      / E2E \
     /______\
    /        \
   / Integration \
  /______________\
 /                \
/   Unit Tests     \
/__________________\
```

- **单元测试 (70%)**: 快速、隔离的测试
- **集成测试 (20%)**: 组件间交互测试
- **端到端测试 (10%)**: 完整业务流程测试

### 2. 集成测试层次

```
┌─────────────────────────────────────────────────────────────┐
│                     端到端测试                              │
├─────────────────────────────────────────────────────────────┤
│                   服务集成测试                             │
├─────────────────────────────────────────────────────────────┤
│                   数据库集成测试                           │
├─────────────────────────────────────────────────────────────┤
│                   API集成测试                              │
├─────────────────────────────────────────────────────────────┤
│                   单元测试                                 │
└─────────────────────────────────────────────────────────────┘
```

## 数据库集成测试

### 使用Testcontainer

```go
package database

import (
	"context"
	"database/sql"
	"fmt"
	"testing"
	"time"

	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
)

type User struct {
	ID        int       `json:"id"`
	Username  string    `json:"username"`
	Email     string    `json:"email"`
	CreatedAt time.Time `json:"created_at"`
}

type UserRepository struct {
	db *sql.DB
}

func NewUserRepository(db *sql.DB) *UserRepository {
	return &UserRepository{db: db}
}

func (r *UserRepository) Create(ctx context.Context, user *User) error {
	query := `INSERT INTO users (username, email, created_at) VALUES ($1, $2, $3) RETURNING id`
	return r.db.QueryRowContext(ctx, query, user.Username, user.Email, user.CreatedAt).Scan(&user.ID)
}

func (r *UserRepository) GetByID(ctx context.Context, id int) (*User, error) {
	user := &User{}
	query := `SELECT id, username, email, created_at FROM users WHERE id = $1`
	err := r.db.QueryRowContext(ctx, query, id).Scan(&user.ID, &user.Username, &user.Email, &user.CreatedAt)
	return user, err
}

func (r *UserRepository) Update(ctx context.Context, user *User) error {
	query := `UPDATE users SET username = $1, email = $2 WHERE id = $3`
	_, err := r.db.ExecContext(ctx, query, user.Username, user.Email, user.ID)
	return err
}

func (r *UserRepository) Delete(ctx context.Context, id int) error {
	query := `DELETE FROM users WHERE id = $1`
	_, err := r.db.ExecContext(ctx, query, id)
	return err
}

func TestUserRepositoryIntegration(t *testing.T) {
	ctx := context.Background()

	// 创建PostgreSQL容器
	pgContainer, err := postgres.RunContainer(ctx,
		testcontainers.WithImage("postgres:15-alpine"),
		postgres.WithDatabase("testdb"),
		postgres.WithUsername("testuser"),
		postgres.WithPassword("testpass"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).
				WithStartupTimeout(5*time.Second),
		),
	)
	if err != nil {
		t.Fatalf("Failed to start PostgreSQL container: %v", err)
	}
	defer pgContainer.Terminate(ctx)

	// 获取数据库连接字符串
	connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
	if err != nil {
		t.Fatalf("Failed to get connection string: %v", err)
	}

	// 连接数据库
	db, err := sql.Open("postgres", connStr)
	if err != nil {
		t.Fatalf("Failed to connect to database: %v", err)
	}
	defer db.Close()

	// 创建表
	_, err = db.ExecContext(ctx, `
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			username VARCHAR(50) NOT NULL UNIQUE,
			email VARCHAR(100) NOT NULL UNIQUE,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		t.Fatalf("Failed to create table: %v", err)
	}

	// 创建用户仓库
	repo := NewUserRepository(db)

	// 测试创建用户
	t.Run("CreateUser", func(t *testing.T) {
		user := &User{
			Username:  "testuser",
			Email:     "test@example.com",
			CreatedAt: time.Now(),
		}

		err := repo.Create(ctx, user)
		if err != nil {
			t.Errorf("Failed to create user: %v", err)
		}

		if user.ID == 0 {
			t.Error("User ID should not be zero")
		}
	})

	// 测试获取用户
	t.Run("GetUser", func(t *testing.T) {
		user := &User{
			Username:  "getuser",
			Email:     "get@example.com",
			CreatedAt: time.Now(),
		}

		// 先创建用户
		err := repo.Create(ctx, user)
		if err != nil {
			t.Fatalf("Failed to create user: %v", err)
		}

		// 获取用户
		retrieved, err := repo.GetByID(ctx, user.ID)
		if err != nil {
			t.Errorf("Failed to get user: %v", err)
		}

		if retrieved.Username != user.Username {
			t.Errorf("Expected username %s, got %s", user.Username, retrieved.Username)
		}

		if retrieved.Email != user.Email {
			t.Errorf("Expected email %s, got %s", user.Email, retrieved.Email)
		}
	})

	// 测试更新用户
	t.Run("UpdateUser", func(t *testing.T) {
		user := &User{
			Username:  "updateuser",
			Email:     "update@example.com",
			CreatedAt: time.Now(),
		}

		// 先创建用户
		err := repo.Create(ctx, user)
		if err != nil {
			t.Fatalf("Failed to create user: %v", err)
		}

		// 更新用户
		user.Username = "updateduser"
		user.Email = "updated@example.com"

		err = repo.Update(ctx, user)
		if err != nil {
			t.Errorf("Failed to update user: %v", err)
		}

		// 验证更新
		retrieved, err := repo.GetByID(ctx, user.ID)
		if err != nil {
			t.Errorf("Failed to get updated user: %v", err)
		}

		if retrieved.Username != "updateduser" {
			t.Errorf("Expected updated username %s, got %s", "updateduser", retrieved.Username)
		}
	})

	// 测试删除用户
	t.Run("DeleteUser", func(t *testing.T) {
		user := &User{
			Username:  "deleteuser",
			Email:     "delete@example.com",
			CreatedAt: time.Now(),
		}

		// 先创建用户
		err := repo.Create(ctx, user)
		if err != nil {
			t.Fatalf("Failed to create user: %v", err)
		}

		// 删除用户
		err = repo.Delete(ctx, user.ID)
		if err != nil {
			t.Errorf("Failed to delete user: %v", err)
		}

		// 验证删除
		_, err = repo.GetByID(ctx, user.ID)
		if err == nil {
			t.Error("Expected error when getting deleted user")
		}
	})
}
```

### 使用内存数据库

```go
package database

import (
	"database/sql"
	"testing"
	"time"

	_ "github.com/mattn/go-sqlite3"
)

func TestUserRepositoryWithSQLite(t *testing.T) {
	// 使用内存SQLite数据库
	db, err := sql.Open("sqlite3", ":memory:")
	if err != nil {
		t.Fatalf("Failed to open database: %v", err)
	}
	defer db.Close()

	// 创建表
	_, err = db.Exec(`
		CREATE TABLE users (
			id INTEGER PRIMARY KEY AUTOINCREMENT,
			username TEXT NOT NULL UNIQUE,
			email TEXT NOT NULL UNIQUE,
			created_at DATETIME DEFAULT CURRENT_TIMESTAMP
		)
	`)
	if err != nil {
		t.Fatalf("Failed to create table: %v", err)
	}

	repo := NewUserRepository(db)

	// 测试用例
	testCases := []struct {
		name     string
		setup    func() (*User, error)
		test     func(*User) error
		validate func(*User, error)
	}{
		{
			name: "CreateUser",
			setup: func() (*User, error) {
				return &User{
					Username:  "testuser",
					Email:     "test@example.com",
					CreatedAt: time.Now(),
				}, nil
			},
			test: func(user *User) error {
				return repo.Create(context.Background(), user)
			},
			validate: func(user *User, err error) {
				if err != nil {
					t.Errorf("Create user failed: %v", err)
				}
				if user.ID == 0 {
					t.Error("User ID should not be zero")
				}
			},
		},
		{
			name: "GetNonExistentUser",
			setup: func() (*User, error) {
				return nil, nil
			},
			test: func(user *User) error {
				_, err := repo.GetByID(context.Background(), 999)
				return err
			},
			validate: func(user *User, err error) {
				if err == nil {
					t.Error("Expected error when getting non-existent user")
				}
			},
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// 每个测试前清理数据
			_, err := db.Exec("DELETE FROM users")
			if err != nil {
				t.Fatalf("Failed to clean table: %v", err)
			}

			// 设置测试数据
			user, err := tc.setup()
			if err != nil {
				t.Fatalf("Setup failed: %v", err)
			}

			// 执行测试
			err = tc.test(user)

			// 验证结果
			tc.validate(user, err)
		})
	}
}
```

## API集成测试

### HTTP客户端测试

```go
package api

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

type User struct {
	ID       string `json:"id"`
	Username string `json:"username"`
	Email    string `json:"email"`
}

type UserHandler struct {
	users map[string]*User
}

func NewUserHandler() *UserHandler {
	return &UserHandler{
		users: make(map[string]*User),
	}
}

func (h *UserHandler) CreateUser(c *gin.Context) {
	var user User
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user.ID = generateID()
	h.users[user.ID] = user

	c.JSON(http.StatusCreated, user)
}

func (h *UserHandler) GetUser(c *gin.Context) {
	id := c.Param("id")
	user, exists := h.users[id]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	c.JSON(http.StatusOK, user)
}

func (h *UserHandler) UpdateUser(c *gin.Context) {
	id := c.Param("id")
	user, exists := h.users[id]
	if !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	var updateUser User
	if err := c.ShouldBindJSON(&updateUser); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	user.Username = updateUser.Username
	user.Email = updateUser.Email

	c.JSON(http.StatusOK, user)
}

func (h *UserHandler) DeleteUser(c *gin.Context) {
	id := c.Param("id")
	if _, exists := h.users[id]; !exists {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	delete(h.users, id)
	c.Status(http.StatusNoContent)
}

func (h *UserHandler) ListUsers(c *gin.Context) {
	var users []*User
	for _, user := range h.users {
		users = append(users, user)
	}

	c.JSON(http.StatusOK, users)
}

func TestUserAPIIntegration(t *testing.T) {
	// 设置Gin为测试模式
	gin.SetMode(gin.TestMode)

	// 创建用户处理器
	handler := NewUserHandler()

	// 创建路由
	router := gin.Default()
	router.POST("/users", handler.CreateUser)
	router.GET("/users/:id", handler.GetUser)
	router.PUT("/users/:id", handler.UpdateUser)
	router.DELETE("/users/:id", handler.DeleteUser)
	router.GET("/users", handler.ListUsers)

	// 测试创建用户
	t.Run("CreateUser", func(t *testing.T) {
		user := User{
			Username: "testuser",
			Email:    "test@example.com",
		}

		jsonData, _ := json.Marshal(user)
		req, _ := http.NewRequest("POST", "/users", bytes.NewBuffer(jsonData))
		req.Header.Set("Content-Type", "application/json")

		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusCreated, w.Code)

		var response User
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.NotEmpty(t, response.ID)
		assert.Equal(t, user.Username, response.Username)
		assert.Equal(t, user.Email, response.Email)
	})

	// 测试获取用户
	t.Run("GetUser", func(t *testing.T) {
		// 先创建用户
		user := User{
			Username: "getuser",
			Email:    "get@example.com",
		}

		jsonData, _ := json.Marshal(user)
		req, _ := http.NewRequest("POST", "/users", bytes.NewBuffer(jsonData))
		req.Header.Set("Content-Type", "application/json")

		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		var createdUser User
		json.Unmarshal(w.Body.Bytes(), &createdUser)

		// 获取用户
		req, _ = http.NewRequest("GET", "/users/"+createdUser.ID, nil)
		w = httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response User
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, createdUser.ID, response.ID)
		assert.Equal(t, createdUser.Username, response.Username)
		assert.Equal(t, createdUser.Email, response.Email)
	})

	// 测试更新用户
	t.Run("UpdateUser", func(t *testing.T) {
		// 先创建用户
		user := User{
			Username: "updateuser",
			Email:    "update@example.com",
		}

		jsonData, _ := json.Marshal(user)
		req, _ := http.NewRequest("POST", "/users", bytes.NewBuffer(jsonData))
		req.Header.Set("Content-Type", "application/json")

		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		var createdUser User
		json.Unmarshal(w.Body.Bytes(), &createdUser)

		// 更新用户
		updatedUser := User{
			Username: "updateduser",
			Email:    "updated@example.com",
		}

		jsonData, _ = json.Marshal(updatedUser)
		req, _ = http.NewRequest("PUT", "/users/"+createdUser.ID, bytes.NewBuffer(jsonData))
		req.Header.Set("Content-Type", "application/json")

		w = httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response User
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Equal(t, "updateduser", response.Username)
		assert.Equal(t, "updated@example.com", response.Email)
	})

	// 测试删除用户
	t.Run("DeleteUser", func(t *testing.T) {
		// 先创建用户
		user := User{
			Username: "deleteuser",
			Email:    "delete@example.com",
		}

		jsonData, _ := json.Marshal(user)
		req, _ := http.NewRequest("POST", "/users", bytes.NewBuffer(jsonData))
		req.Header.Set("Content-Type", "application/json")

		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		var createdUser User
		json.Unmarshal(w.Body.Bytes(), &createdUser)

		// 删除用户
		req, _ = http.NewRequest("DELETE", "/users/"+createdUser.ID, nil)
		w = httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusNoContent, w.Code)

		// 验证用户已删除
		req, _ = http.NewRequest("GET", "/users/"+createdUser.ID, nil)
		w = httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusNotFound, w.Code)
	})

	// 测试用户列表
	t.Run("ListUsers", func(t *testing.T) {
		// 清空用户
		handler.users = make(map[string]*User)

		// 创建几个用户
		users := []User{
			{Username: "user1", Email: "user1@example.com"},
			{Username: "user2", Email: "user2@example.com"},
			{Username: "user3", Email: "user3@example.com"},
		}

		for _, user := range users {
			jsonData, _ := json.Marshal(user)
			req, _ := http.NewRequest("POST", "/users", bytes.NewBuffer(jsonData))
			req.Header.Set("Content-Type", "application/json")

			w := httptest.NewRecorder()
			router.ServeHTTP(w, req)
		}

		// 获取用户列表
		req, _ := http.NewRequest("GET", "/users", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response []User
		err := json.Unmarshal(w.Body.Bytes(), &response)
		assert.NoError(t, err)
		assert.Len(t, response, 3)
	})
}
```

### 外部API集成测试

```go
package external

import (
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type Post struct {
	ID     int    `json:"id"`
	Title  string `json:"title"`
	Body   string `json:"body"`
	UserID int   `json:"userId"`
}

type PostService struct {
	baseURL    string
	httpClient *http.Client
}

func NewPostService(baseURL string) *PostService {
	return &PostService{
		baseURL: baseURL,
		httpClient: &http.Client{
			Timeout: 10 * time.Second,
		},
	}
}

func (s *PostService) GetPosts() ([]Post, error) {
	resp, err := s.httpClient.Get(s.baseURL + "/posts")
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var posts []Post
	err = json.Unmarshal(body, &posts)
	if err != nil {
		return nil, err
	}

	return posts, nil
}

func (s *PostService) GetPost(id int) (*Post, error) {
	resp, err := s.httpClient.Get(fmt.Sprintf("%s/posts/%d", s.baseURL, id))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var post Post
	err = json.Unmarshal(body, &post)
	if err != nil {
		return nil, err
	}

	return &post, nil
}

func (s *PostService) CreatePost(post *Post) (*Post, error) {
	jsonData, err := json.Marshal(post)
	if err != nil {
		return nil, err
	}

	resp, err := s.httpClient.Post(s.baseURL+"/posts", "application/json", bytes.NewReader(jsonData))
	if err != nil {
		return nil, err
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusCreated {
		return nil, fmt.Errorf("unexpected status code: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return nil, err
	}

	var createdPost Post
	err = json.Unmarshal(body, &createdPost)
	if err != nil {
		return nil, err
	}

	return &createdPost, nil
}

func TestPostServiceIntegration(t *testing.T) {
	// 创建模拟的外部API服务器
	mockServer := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		switch r.URL.Path {
		case "/posts":
			if r.Method == http.MethodGet {
				// 返回帖子列表
				posts := []Post{
					{ID: 1, Title: "Post 1", Body: "Body 1", UserID: 1},
					{ID: 2, Title: "Post 2", Body: "Body 2", UserID: 2},
				}
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(posts)
			} else if r.Method == http.MethodPost {
				// 创建新帖子
				var post Post
				err := json.NewDecoder(r.Body).Decode(&post)
				if err != nil {
					http.Error(w, err.Error(), http.StatusBadRequest)
					return
				}

				post.ID = 3 // 模拟分配ID
				w.Header().Set("Content-Type", "application/json")
				w.WriteHeader(http.StatusCreated)
				json.NewEncoder(w).Encode(post)
			}
		case "/posts/1":
			if r.Method == http.MethodGet {
				// 返回单个帖子
				post := Post{ID: 1, Title: "Post 1", Body: "Body 1", UserID: 1}
				w.Header().Set("Content-Type", "application/json")
				json.NewEncoder(w).Encode(post)
			}
		case "/posts/999":
			// 返回404
			w.WriteHeader(http.StatusNotFound)
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer mockServer.Close()

	// 创建帖子服务
	service := NewPostService(mockServer.URL)

	t.Run("GetPosts", func(t *testing.T) {
		posts, err := service.GetPosts()
		require.NoError(t, err)
		assert.Len(t, posts, 2)
		assert.Equal(t, "Post 1", posts[0].Title)
		assert.Equal(t, "Post 2", posts[1].Title)
	})

	t.Run("GetPost", func(t *testing.T) {
		post, err := service.GetPost(1)
		require.NoError(t, err)
		assert.Equal(t, 1, post.ID)
		assert.Equal(t, "Post 1", post.Title)
		assert.Equal(t, "Body 1", post.Body)
	})

	t.Run("GetNonExistentPost", func(t *testing.T) {
		post, err := service.GetPost(999)
		assert.Error(t, err)
		assert.Nil(t, post)
	})

	t.Run("CreatePost", func(t *testing.T) {
		newPost := &Post{
			Title:  "New Post",
			Body:   "New Body",
			UserID: 1,
		}

		createdPost, err := service.CreatePost(newPost)
		require.NoError(t, err)
		assert.Equal(t, 3, createdPost.ID)
		assert.Equal(t, "New Post", createdPost.Title)
		assert.Equal(t, "New Body", createdPost.Body)
	})

	t.Run("NetworkError", func(t *testing.T) {
		// 测试网络错误情况
		service := NewPostService("http://invalid-url")
		_, err := service.GetPosts()
		assert.Error(t, err)
	})
}
```

## 消息队列集成测试

### Redis集成测试

```go
package queue

import (
	"context"
	"encoding/json"
	"testing"
	"time"

	"github.com/go-redis/redis/v8"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/redis"
)

type Message struct {
	ID      string      `json:"id"`
	Type    string      `json:"type"`
	Payload interface{} `json:"payload"`
}

type MessageQueue struct {
	client *redis.Client
}

func NewMessageQueue(client *redis.Client) *MessageQueue {
	return &MessageQueue{client: client}
}

func (q *MessageQueue) Publish(ctx context.Context, channel string, message *Message) error {
	data, err := json.Marshal(message)
	if err != nil {
		return err
	}

	return q.client.Publish(ctx, channel, data).Err()
}

func (q *MessageQueue) Subscribe(ctx context.Context, channel string) <-chan *Message {
	msgChan := make(chan *Message, 100)

	go func() {
		defer close(msgChan)

		pubsub := q.client.Subscribe(ctx, channel)
		defer pubsub.Close()

		for {
			select {
			case <-ctx.Done():
				return
			case msg := <-pubsub.Channel():
				var message Message
				if err := json.Unmarshal([]byte(msg.Payload), &message); err != nil {
					continue
				}
				msgChan <- &message
			}
		}
	}()

	return msgChan
}

func TestMessageQueueIntegration(t *testing.T) {
	ctx := context.Background()

	// 创建Redis容器
	redisContainer, err := redis.RunContainer(ctx,
		testcontainers.WithImage("redis:7-alpine"),
	)
	require.NoError(t, err)
	defer redisContainer.Terminate(ctx)

	// 获取Redis连接地址
	redisAddr, err := redisContainer.ConnectionString(ctx)
	require.NoError(t, err)

	// 创建Redis客户端
	client := redis.NewClient(&redis.Options{
		Addr: redisAddr,
	})

	// 测试连接
	_, err = client.Ping(ctx).Result()
	require.NoError(t, err)

	// 创建消息队列
	queue := NewMessageQueue(client)

	t.Run("PublishAndSubscribe", func(t *testing.T) {
		channel := "test-channel"
		message := &Message{
			ID:      "123",
			Type:    "test",
			Payload: "test payload",
		}

		// 订阅频道
		msgChan := queue.Subscribe(ctx, channel)

		// 发布消息
		err := queue.Publish(ctx, channel, message)
		require.NoError(t, err)

		// 接收消息
		select {
		case received := <-msgChan:
			assert.Equal(t, message.ID, received.ID)
			assert.Equal(t, message.Type, received.Type)
			assert.Equal(t, message.Payload, received.Payload)
		case <-time.After(5 * time.Second):
			t.Fatal("Timeout waiting for message")
		}
	})

	t.Run("MultipleSubscribers", func(t *testing.T) {
		channel := "multi-channel"
		message := &Message{
			ID:      "456",
			Type:    "broadcast",
			Payload: "broadcast message",
		}

		// 创建多个订阅者
		sub1 := queue.Subscribe(ctx, channel)
		sub2 := queue.Subscribe(ctx, channel)
		sub3 := queue.Subscribe(ctx, channel)

		// 发布消息
		err := queue.Publish(ctx, channel, message)
		require.NoError(t, err)

		// 所有订阅者都应该收到消息
		received := 0
		timeout := time.After(5 * time.Second)

		for received < 3 {
			select {
			case msg := <-sub1:
				assert.Equal(t, message.ID, msg.ID)
				received++
			case msg := <-sub2:
				assert.Equal(t, message.ID, msg.ID)
				received++
			case msg := <-sub3:
				assert.Equal(t, message.ID, msg.ID)
				received++
			case <-timeout:
				t.Fatal("Timeout waiting for messages")
			}
		}

		assert.Equal(t, 3, received)
	})

	t.Run("MultipleChannels", func(t *testing.T) {
		channels := []string{"channel1", "channel2", "channel3"}
		messages := []*Message{
			{ID: "1", Type: "type1", Payload: "payload1"},
			{ID: "2", Type: "type2", Payload: "payload2"},
			{ID: "3", Type: "type3", Payload: "payload3"},
		}

		// 订阅不同频道
		subs := make([]<-chan *Message, len(channels))
		for i, channel := range channels {
			subs[i] = queue.Subscribe(ctx, channel)
		}

		// 发布消息到不同频道
		for i, channel := range channels {
			err := queue.Publish(ctx, channel, messages[i])
			require.NoError(t, err)
		}

		// 验证每个频道的消息
		for i, sub := range subs {
			select {
			case msg := <-sub:
				assert.Equal(t, messages[i].ID, msg.ID)
				assert.Equal(t, messages[i].Type, msg.Type)
			case <-time.After(5 * time.Second):
				t.Fatalf("Timeout waiting for message on channel %s", channels[i])
			}
		}
	})
}
```

## 服务集成测试

### 微服务集成测试

```go
package service

import (
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// UserService 用户服务
type UserService struct {
	users map[string]*User
}

func NewUserService() *UserService {
	return &UserService{
		users: map[string]*User{
			"1": {ID: "1", Name: "User 1", Email: "user1@example.com"},
			"2": {ID: "2", Name: "User 2", Email: "user2@example.com"},
		},
	}
}

func (s *UserService) GetUser(id string) (*User, error) {
	user, exists := s.users[id]
	if !exists {
		return nil, fmt.Errorf("user not found")
	}
	return user, nil
}

func (s *UserService) GetUsers() ([]*User, error) {
	var users []*User
	for _, user := range s.users {
		users = append(users, user)
	}
	return users, nil
}

// OrderService 订单服务
type OrderService struct {
	orders map[string]*Order
}

func NewOrderService() *OrderService {
	return &OrderService{
		orders: map[string]*Order{
			"1": {ID: "1", UserID: "1", Product: "Product 1", Amount: 100.0},
			"2": {ID: "2", UserID: "2", Product: "Product 2", Amount: 200.0},
		},
	}
}

func (s *OrderService) GetOrder(id string) (*Order, error) {
	order, exists := s.orders[id]
	if !exists {
		return nil, fmt.Errorf("order not found")
	}
	return order, nil
}

func (s *OrderService) GetOrdersByUser(userID string) ([]*Order, error) {
	var orders []*Order
	for _, order := range s.orders {
		if order.UserID == userID {
			orders = append(orders, order)
		}
	}
	return orders, nil
}

// APIService API网关服务
type APIService struct {
	userService  *UserService
	orderService *OrderService
}

func NewAPIService(userService *UserService, orderService *OrderService) *APIService {
	return &APIService{
		userService:  userService,
		orderService: orderService,
	}
}

func (s *APIService) GetUserWithOrders(c *gin.Context) {
	userID := c.Param("userID")

	// 获取用户信息
	user, err := s.userService.GetUser(userID)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	// 获取用户订单
	orders, err := s.orderService.GetOrdersByUser(userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get orders"})
		return
	}

	// 组合响应
	response := gin.H{
		"user":   user,
		"orders": orders,
	}

	c.JSON(http.StatusOK, response)
}

func TestAPIServiceIntegration(t *testing.T) {
	// 设置Gin为测试模式
	gin.SetMode(gin.TestMode)

	// 创建服务
	userService := NewUserService()
	orderService := NewOrderService()
	apiService := NewAPIService(userService, orderService)

	// 创建路由
	router := gin.Default()
	router.GET("/users/:userID/orders", apiService.GetUserWithOrders)

	// 测试获取用户及其订单
	t.Run("GetUserWithOrders", func(t *testing.T) {
		// 测试存在的用户
		req, _ := http.NewRequest("GET", "/users/1/orders", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		// 验证用户信息
		user, ok := response["user"].(map[string]interface{})
		assert.True(t, ok)
		assert.Equal(t, "1", user["id"])
		assert.Equal(t, "User 1", user["name"])

		// 验证订单信息
		orders, ok := response["orders"].([]interface{})
		assert.True(t, ok)
		assert.Len(t, orders, 1)

		order := orders[0].(map[string]interface{})
		assert.Equal(t, "1", order["id"])
		assert.Equal(t, "Product 1", order["product"])
	})

	t.Run("GetUserWithNoOrders", func(t *testing.T) {
		// 测试没有订单的用户
		req, _ := http.NewRequest("GET", "/users/2/orders", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusOK, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		// 验证用户信息
		user, ok := response["user"].(map[string]interface{})
		assert.True(t, ok)
		assert.Equal(t, "2", user["id"])
		assert.Equal(t, "User 2", user["name"])

		// 验证订单信息（应该为空）
		orders, ok := response["orders"].([]interface{})
		assert.True(t, ok)
		assert.Len(t, orders, 0)
	})

	t.Run("GetNonExistentUser", func(t *testing.T) {
		// 测试不存在的用户
		req, _ := http.NewRequest("GET", "/users/999/orders", nil)
		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		assert.Equal(t, http.StatusNotFound, w.Code)

		var response map[string]interface{}
		err := json.Unmarshal(w.Body.Bytes(), &response)
		require.NoError(t, err)

		assert.Contains(t, response, "error")
	})
}
```

## 测试工具和辅助函数

### 测试辅助函数

```go
package testutils

import (
	"bytes"
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

// HTTPTestHelper HTTP测试辅助结构
type HTTPTestHelper struct {
	router *gin.Engine
	t      *testing.T
}

func NewHTTPTestHelper(router *gin.Engine, t *testing.T) *HTTPTestHelper {
	return &HTTPTestHelper{
		router: router,
		t:      t,
	}
}

// Request 发送HTTP请求并返回响应
func (h *HTTPTestHelper) Request(method, url string, body interface{}, headers map[string]string) *httptest.ResponseRecorder {
	var bodyBytes []byte
	if body != nil {
		var err error
		bodyBytes, err = json.Marshal(body)
		require.NoError(h.t, err)
	}

	req, err := http.NewRequest(method, url, bytes.NewBuffer(bodyBytes))
	require.NoError(h.t, err)

	// 设置请求头
	req.Header.Set("Content-Type", "application/json")
	for key, value := range headers {
		req.Header.Set(key, value)
	}

	w := httptest.NewRecorder()
	h.router.ServeHTTP(w, req)

	return w
}

// AssertStatus 断言HTTP状态码
func (h *HTTPTestHelper) AssertStatus(w *httptest.ResponseRecorder, expectedStatus int) {
	assert.Equal(h.t, expectedStatus, w.Code)
}

// AssertJSONResponse 断言JSON响应
func (h *HTTPTestHelper) AssertJSONResponse(w *httptest.ResponseRecorder, target interface{}) {
	require.NoError(h.t, json.Unmarshal(w.Body.Bytes(), target))
}

// AssertErrorMessage 断言错误消息
func (h *HTTPTestHelper) AssertErrorMessage(w *httptest.ResponseRecorder, expectedMessage string) {
	var response map[string]interface{}
	require.NoError(h.t, json.Unmarshal(w.Body.Bytes(), &response))
	assert.Contains(h.t, response, "error")
	assert.Equal(h.t, expectedMessage, response["error"])
}

// 使用示例
func TestUserAPIWithHelper(t *testing.T) {
	router := setupRouter()
	helper := NewHTTPTestHelper(router, t)

	t.Run("CreateUser", func(t *testing.T) {
		user := map[string]interface{}{
			"username": "testuser",
			"email":    "test@example.com",
		}

		w := helper.Request("POST", "/users", user, nil)
		helper.AssertStatus(w, http.StatusCreated)

		var response map[string]interface{}
		helper.AssertJSONResponse(w, &response)
		assert.NotEmpty(t, response["id"])
		assert.Equal(t, user["username"], response["username"])
	})
}
```

### 数据库测试辅助函数

```go
package testutils

import (
	"context"
	"database/sql"
	"fmt"
	"testing"
	"time"

	"github.com/testcontainers/testcontainers-go"
	"github.com/testcontainers/testcontainers-go/modules/postgres"
	"github.com/testcontainers/testcontainers-go/wait"
)

// DatabaseTestHelper 数据库测试辅助结构
type DatabaseTestHelper struct {
	db      *sql.DB
	cleanup func()
}

// NewTestDatabase 创建测试数据库
func NewTestDatabase(t *testing.T) *DatabaseTestHelper {
	ctx := context.Background()

	// 创建PostgreSQL容器
	pgContainer, err := postgres.RunContainer(ctx,
		testcontainers.WithImage("postgres:15-alpine"),
		postgres.WithDatabase("testdb"),
		postgres.WithUsername("testuser"),
		postgres.WithPassword("testpass"),
		testcontainers.WithWaitStrategy(
			wait.ForLog("database system is ready to accept connections").
				WithOccurrence(2).
				WithStartupTimeout(5*time.Second),
		),
	)
	require.NoError(t, err)

	// 获取连接字符串
	connStr, err := pgContainer.ConnectionString(ctx, "sslmode=disable")
	require.NoError(t, err)

	// 连接数据库
	db, err := sql.Open("postgres", connStr)
	require.NoError(t, err)

	return &DatabaseTestHelper{
		db: db,
		cleanup: func() {
			db.Close()
			pgContainer.Terminate(ctx)
		},
	}
}

// DB 获取数据库连接
func (h *DatabaseTestHelper) DB() *sql.DB {
	return h.db
}

// Cleanup 清理资源
func (h *DatabaseTestHelper) Cleanup() {
	h.cleanup()
}

// CreateUsersTable 创建用户表
func (h *DatabaseTestHelper) CreateUsersTable() error {
	_, err := h.db.Exec(`
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			username VARCHAR(50) NOT NULL UNIQUE,
			email VARCHAR(100) NOT NULL UNIQUE,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)
	`)
	return err
}

// TruncateTable 清空表数据
func (h *DatabaseTestHelper) TruncateTable(tableName string) error {
	_, err := h.db.Exec(fmt.Sprintf("TRUNCATE TABLE %s CASCADE", tableName))
	return err
}

// InsertTestData 插入测试数据
func (h *DatabaseTestHelper) InsertTestData() error {
	users := []struct {
		username string
		email    string
	}{
		{"user1", "user1@example.com"},
		{"user2", "user2@example.com"},
		{"user3", "user3@example.com"},
	}

	for _, user := range users {
		_, err := h.db.Exec(
			"INSERT INTO users (username, email) VALUES ($1, $2)",
			user.username, user.email,
		)
		if err != nil {
			return err
		}
	}

	return nil
}

// 使用示例
func TestUserRepositoryWithHelper(t *testing.T) {
	dbHelper := NewTestDatabase(t)
	defer dbHelper.Cleanup()

	// 创建表
	err := dbHelper.CreateUsersTable()
	require.NoError(t, err)

	// 插入测试数据
	err = dbHelper.InsertTestData()
	require.NoError(t, err)

	repo := NewUserRepository(dbHelper.DB())

	// 测试用例
	t.Run("GetUser", func(t *testing.T) {
		user, err := repo.GetByID(context.Background(), 1)
		require.NoError(t, err)
		assert.Equal(t, "user1", user.Username)
	})
}
```

## 集成测试最佳实践

### 1. 测试环境管理

**使用Testcontainers**
```go
// 推荐使用Testcontainers进行集成测试
func TestWithRealDatabase(t *testing.T) {
    // 自动创建和管理容器
    container := setupTestContainer(t)
    defer container.Cleanup()

    // 执行测试
    runTests(t, container)
}
```

**环境变量配置**
```go
func TestWithEnvironment(t *testing.T) {
    // 设置测试环境变量
    os.Setenv("TEST_MODE", "true")
    defer os.Setenv("TEST_MODE", "")

    // 执行测试
    runTests(t)
}
```

### 2. 测试数据管理

**使用工厂模式创建测试数据**
```go
// testdata/factory.go
package testdata

type UserFactory struct {
	baseUser *User
}

func NewUserFactory() *UserFactory {
	return &UserFactory{
		baseUser: &User{
			Username: "testuser",
			Email:    "test@example.com",
			IsActive: true,
		},
	}
}

func (f *UserFactory) Create(overrides ...func(*User)) *User {
	user := &User{
		Username: f.baseUser.Username,
		Email:    f.baseUser.Email,
		IsActive: f.baseUser.IsActive,
	}

	for _, override := range overrides {
		override(user)
	}

	return user
}

// 使用示例
func TestUserCreation(t *testing.T) {
	factory := NewUserFactory()

	// 创建默认用户
	user := factory.Create()

	// 创建自定义用户
	adminUser := factory.Create(func(u *User) {
		u.Username = "admin"
		u.Email = "admin@example.com"
		u.IsActive = true
	})
}
```

### 3. 异步测试处理

**处理异步操作**
```go
func TestAsyncOperation(t *testing.T) {
	// 启动异步操作
	go asyncOperation()

	// 等待操作完成
	assert.Eventually(t, func() bool {
		return checkOperationComplete()
	}, 5*time.Second, 100*time.Millisecond, "Operation should complete")
}
```

### 4. 测试性能考虑

**设置合理的超时**
```go
func TestWithTimeout(t *testing.T) {
	ctx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
	defer cancel()

	// 执行测试
	err := performOperation(ctx)
	assert.NoError(t, err)
}
```

### 5. 测试隔离和清理

**确保测试隔离**
```go
func TestWithCleanup(t *testing.T) {
	// 每个测试前清理
	cleanupDatabase()

	// 执行测试
	t.Run("Test1", func(t *testing.T) {
		// 测试代码
	})

	t.Run("Test2", func(t *testing.T) {
		// 测试代码
	})
}
```

## 集成测试策略总结

### 1. 测试范围选择
- **关键路径**: 测试核心业务流程
- **外部依赖**: 测试与外部系统的集成
- **数据一致性**: 测试数据在不同组件间的流转
- **错误处理**: 测试异常情况的处理

### 2. 测试环境策略
- **容器化**: 使用Docker容器确保环境一致性
- **模拟服务**: 对于难以集成的外部服务使用模拟
- **数据管理**: 合理管理测试数据的创建和清理

### 3. 测试执行策略
- **并行执行**: 提高测试执行效率
- **分级测试**: 根据重要性分级执行测试
- **持续集成**: 集成到CI/CD流程中

### 4. 测试维护策略
- **定期更新**: 跟随业务变化更新测试
- **监控覆盖**: 监控测试覆盖率
- **性能监控**: 关注测试执行时间

通过合理应用这些策略和技巧，可以构建出稳定、可靠的集成测试套件，确保Go应用程序的质量和可靠性。

*最后更新: 2025年9月*