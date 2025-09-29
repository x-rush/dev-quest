# Gin+Redis最佳实践

本文档详细介绍在Gin框架中使用Redis的最佳实践，包括基础配置、缓存策略、会话管理、分布式锁、计数器、排行榜等高级应用场景。

## 1. Redis基础配置

### 1.1 Redis连接配置

```go
package config

import (
    "context"
    "fmt"
    "time"

    "github.com/go-redis/redis/v8"
)

type RedisConfig struct {
    Host         string
    Port         int
    Password     string
    DB           int
    PoolSize     int
    MinIdleConns int
    MaxRetries   int
    DialTimeout  time.Duration
    ReadTimeout  time.Duration
    WriteTimeout time.Duration
    IdleTimeout  time.Duration
}

func NewRedisConfig() *RedisConfig {
    return &RedisConfig{
        Host:         "localhost",
        Port:         6379,
        Password:     "",
        DB:           0,
        PoolSize:     10,
        MinIdleConns: 2,
        MaxRetries:   3,
        DialTimeout:  5 * time.Second,
        ReadTimeout:  3 * time.Second,
        WriteTimeout: 3 * time.Second,
        IdleTimeout:  5 * time.Minute,
    }
}

func (c *RedisConfig) Build() *redis.Client {
    client := redis.NewClient(&redis.Options{
        Addr:         fmt.Sprintf("%s:%d", c.Host, c.Port),
        Password:     c.Password,
        DB:           c.DB,
        PoolSize:     c.PoolSize,
        MinIdleConns: c.MinIdleConns,
        MaxRetries:   c.MaxRetries,
        DialTimeout:  c.DialTimeout,
        ReadTimeout:  c.ReadTimeout,
        WriteTimeout: c.WriteTimeout,
        IdleTimeout:  c.IdleTimeout,
    })

    // 测试连接
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    if err := client.Ping(ctx).Err(); err != nil {
        panic(fmt.Sprintf("Failed to connect to Redis: %v", err))
    }

    return client
}
```

### 1.2 Redis中间件

```go
package middleware

import (
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"
)

func RedisMiddleware(client *redis.Client) gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Set("redis", client)
        c.Next()
    }
}

// 分布式限流中间件
func RateLimitMiddleware(client *redis.Client, rate int, window time.Duration) gin.HandlerFunc {
    return func(c *gin.Context) {
        ctx := c.Request.Context()
        key := fmt.Sprintf("rate_limit:%s", c.ClientIP())

        // 使用Redis实现滑动窗口限流
        now := time.Now().Unix()
        windowStart := now - int64(window.Seconds())

        // 移除窗口外的请求记录
        client.ZRemRangeByScore(ctx, key, "0", fmt.Sprint(windowStart))

        // 添加当前请求
        client.ZAdd(ctx, key, &redis.Z{Score: float64(now), Member: now})

        // 获取当前窗口内的请求数
        count, err := client.ZCount(ctx, key, fmt.Sprint(windowStart), "+inf").Result()
        if err != nil {
            c.AbortWithStatusJSON(http.StatusInternalServerError, gin.H{
                "error": "Rate limit check failed",
            })
            return
        }

        if int(count) > rate {
            c.AbortWithStatusJSON(http.StatusTooManyRequests, gin.H{
                "error": "Rate limit exceeded",
                "limit": rate,
                "window": window.String(),
            })
            return
        }

        // 设置过期时间
        client.Expire(ctx, key, window)

        c.Next()
    }
}
```

## 2. 缓存策略

### 2.1 基础缓存操作

```go
package cache

import (
    "context"
    "encoding/json"
    "time"

    "github.com/go-redis/redis/v8"
)

type RedisCache struct {
    client *redis.Client
    ctx    context.Context
}

func NewRedisCache(client *redis.Client) *RedisCache {
    return &RedisCache{
        client: client,
        ctx:    context.Background(),
    }
}

// 设置缓存
func (r *RedisCache) Set(key string, value interface{}, expiration time.Duration) error {
    serialized, err := json.Marshal(value)
    if err != nil {
        return err
    }

    return r.client.Set(r.ctx, key, serialized, expiration).Err()
}

// 获取缓存
func (r *RedisCache) Get(key string, dest interface{}) error {
    result, err := r.client.Get(r.ctx, key).Result()
    if err != nil {
        return err
    }

    return json.Unmarshal([]byte(result), dest)
}

// 删除缓存
func (r *RedisCache) Delete(key string) error {
    return r.client.Del(r.ctx, key).Err()
}

// 检查缓存是否存在
func (r *RedisCache) Exists(key string) (bool, error) {
    count, err := r.client.Exists(r.ctx, key).Result()
    return count > 0, err
}

// 设置过期时间
func (r *RedisCache) Expire(key string, expiration time.Duration) error {
    return r.client.Expire(r.ctx, key, expiration).Err()
}
```

### 2.2 缓存穿透保护

```go
package cache

import (
    "crypto/sha256"
    "encoding/hex"
    "fmt"
    "time"

    "github.com/go-redis/redis/v8"
)

type CacheWithBloomFilter struct {
    cache      *RedisCache
    bloomFilter *BloomFilter
}

// 布隆过滤器实现
type BloomFilter struct {
    client *redis.Client
    ctx    context.Context
}

func NewBloomFilter(client *redis.Client) *BloomFilter {
    return &BloomFilter{
        client: client,
        ctx:    context.Background(),
    }
}

func (b *BloomFilter) Add(key string) error {
    // 使用多个哈希函数
    hashes := b.getHashes(key)
    pipe := b.client.Pipeline()

    for _, hash := range hashes {
        pipe.SetBit(b.ctx, "bloom_filter", hash, 1)
    }

    _, err := pipe.Exec(b.ctx)
    return err
}

func (b *BloomFilter) Exists(key string) (bool, error) {
    hashes := b.getHashes(key)

    for _, hash := range hashes {
        bit, err := b.client.GetBit(b.ctx, "bloom_filter", hash).Result()
        if err != nil || bit == 0 {
            return false, err
        }
    }

    return true, nil
}

func (b *BloomFilter) getHashes(key string) []int64 {
    // 简单的哈希函数实现
    h1 := sha256.Sum256([]byte(key + "salt1"))
    h2 := sha256.Sum256([]byte(key + "salt2"))

    hash1 := int64(hex.EncodeToString(h1[:])[0:8], 16)
    hash2 := int64(hex.EncodeToString(h2[:])[0:8], 16)

    // 生成多个哈希值
    var hashes []int64
    for i := 0; i < 5; i++ {
        hashes = append(hashes, hash1+int64(i)*hash2)
    }

    return hashes
}

// 带布隆过滤器的缓存
func (c *CacheWithBloomFilter) GetWithBloomFilter(key string, dest interface{}, fallback func() (interface{}, error)) error {
    // 先检查布隆过滤器
    exists, err := c.bloomFilter.Exists(key)
    if err != nil {
        return err
    }

    if !exists {
        // 布隆过滤器确定不存在
        return fmt.Errorf("key does not exist")
    }

    // 尝试从缓存获取
    err = c.cache.Get(key, dest)
    if err == redis.Nil {
        // 缓存不存在，查询数据库
        value, err := fallback()
        if err != nil {
            return err
        }

        // 添加到布隆过滤器
        c.bloomFilter.Add(key)

        // 设置缓存（使用较短的过期时间保护）
        return c.cache.Set(key, value, 5*time.Minute)
    }

    return err
}
```

### 2.3 缓存雪崩保护

```go
package cache

import (
    "crypto/rand"
    "encoding/binary"
    "time"

    "github.com/go-redis/redis/v8"
)

type CacheWithSnowslideProtection struct {
    cache *RedisCache
}

func NewCacheWithSnowslideProtection(cache *RedisCache) *CacheWithSnowslideProtection {
    return &CacheWithSnowslideProtection{
        cache: cache,
    }
}

// 带随机过期时间的缓存设置
func (c *CacheWithSnowslideProtection) SetWithRandomTTL(key string, value interface{}, baseExpiration time.Duration) error {
    // 生成随机过期时间（基础时间的80%-120%）
    randomFactor := c.randomFloat64(0.8, 1.2)
    expiration := time.Duration(float64(baseExpiration) * randomFactor)

    return c.cache.Set(key, value, expiration)
}

// 互斥锁缓存模式
func (c *CacheWithSnowslideProtection) GetWithMutex(key string, dest interface{}, fallback func() (interface{}, error)) error {
    // 尝试从缓存获取
    err := c.cache.Get(key, dest)
    if err == redis.Nil {
        // 缓存不存在，尝试获取互斥锁
        mutexKey := key + ":mutex"
        mutexValue := c.generateMutexValue()

        // 设置互斥锁（带过期时间）
        acquired, err := c.cache.client.SetNX(c.cache.ctx, mutexKey, mutexValue, 30*time.Second).Result()
        if err != nil {
            return err
        }

        if acquired {
            // 获得锁，查询数据库
            defer c.cache.client.Del(c.cache.ctx, mutexKey)

            value, err := fallback()
            if err != nil {
                return err
            }

            // 设置缓存
            return c.SetWithRandomTTL(key, value, 1*time.Hour)
        } else {
            // 未获得锁，等待并重试
            time.Sleep(100 * time.Millisecond)
            return c.GetWithMutex(key, dest, fallback)
        }
    }

    return err
}

func (c *CacheWithSnowslideProtection) randomFloat64(min, max float64) float64 {
    var buf [8]byte
    _, err := rand.Read(buf[:])
    if err != nil {
        return min
    }

    random := float64(binary.BigEndian.Uint64(buf[:])) / float64(1<<64)
    return min + random*(max-min)
}

func (c *CacheWithSnowslideProtection) generateMutexValue() string {
    var buf [16]byte
    rand.Read(buf[:])
    return string(buf[:])
}
```

## 3. 分布式锁

### 3.1 Redis分布式锁实现

```go
package distributed

import (
    "context"
    "errors"
    "fmt"
    "time"

    "github.com/go-redis/redis/v8"
)

var (
    ErrLockNotHeld = errors.New("lock not held")
    ErrLockExpired = errors.New("lock expired")
)

type RedisLock struct {
    client    *redis.Client
    ctx       context.Context
    key       string
    value     string
    ttl       time.Duration
    stopRenew chan struct{}
}

func NewRedisLock(client *redis.Client, key string, ttl time.Duration) *RedisLock {
    return &RedisLock{
        client: client,
        ctx:    context.Background(),
        key:    key,
        ttl:    ttl,
    }
}

// 获取锁
func (l *RedisLock) Acquire() (bool, error) {
    // 生成唯一值
    l.value = l.generateUniqueValue()

    // 使用SET命令实现原子性获取锁
    acquired, err := l.client.SetNX(l.ctx, l.key, l.value, l.ttl).Result()
    if err != nil {
        return false, err
    }

    if acquired {
        // 启动续期协程
        l.startRenewal()
    }

    return acquired, nil
}

// 释放锁
func (l *RedisLock) Release() error {
    // 停止续期
    if l.stopRenew != nil {
        close(l.stopRenew)
    }

    // 使用Lua脚本确保只能释放自己持有的锁
    script := `
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
    `

    result, err := l.client.Eval(l.ctx, script, []string{l.key}, l.value).Result()
    if err != nil {
        return err
    }

    if result.(int64) == 0 {
        return ErrLockNotHeld
    }

    return nil
}

// 锁续期
func (l *RedisLock) startRenewal() {
    l.stopRenew = make(chan struct{})

    go func() {
        ticker := time.NewTicker(l.ttl / 2)
        defer ticker.Stop()

        for {
            select {
            case <-ticker.C:
                // 续期锁
                script := `
                    if redis.call("GET", KEYS[1]) == ARGV[1] then
                        return redis.call("EXPIRE", KEYS[1], ARGV[2])
                    else
                        return 0
                    end
                `

                result, err := l.client.Eval(l.ctx, script, []string{l.key}, l.value, int(l.ttl.Seconds())).Result()
                if err != nil || result.(int64) == 0 {
                    return
                }

            case <-l.stopRenew:
                return
            }
        }
    }()
}

func (l *RedisLock) generateUniqueValue() string {
    return fmt.Sprintf("%d:%d", time.Now().UnixNano(), time.Now().Unix())
}

// 带超时的锁获取
func (l *RedisLock) AcquireWithTimeout(timeout time.Duration) (bool, error) {
    startTime := time.Now()

    for {
        acquired, err := l.Acquire()
        if err != nil {
            return false, err
        }

        if acquired {
            return true, nil
        }

        if time.Since(startTime) >= timeout {
            return false, nil
        }

        time.Sleep(10 * time.Millisecond)
    }
}
```

### 3.2 分布式锁使用示例

```go
package main

import (
    "fmt"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"
)

func main() {
    r := gin.Default()

    // 初始化Redis
    redisClient := redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })

    // 分布式任务处理
    r.POST("/process", func(c *gin.Context) {
        lock := NewRedisLock(redisClient, "task_lock", 30*time.Second)

        // 尝试获取锁
        acquired, err := lock.AcquireWithTimeout(5 * time.Second)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        if !acquired {
            c.JSON(429, gin.H{"error": "Task is already being processed"})
            return
        }

        // 确保锁被释放
        defer lock.Release()

        // 执行任务
        result, err := processTask()
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(200, gin.H{"result": result})
    })

    r.Run(":8080")
}

func processTask() (string, error) {
    // 模拟耗时任务
    time.Sleep(2 * time.Second)
    return "Task completed", nil
}
```

## 4. 会话管理

### 4.1 Redis会话存储

```go
package session

import (
    "encoding/json"
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"
    "github.com/gorilla/sessions"
)

type RedisStore struct {
    client   *redis.Client
    sessions *sessions.CookieStore
    prefix   string
    maxAge   int
}

func NewRedisStore(client *redis.Client, secretKey []byte) *RedisStore {
    return &RedisStore{
        client:   client,
        sessions: sessions.NewCookieStore(secretKey),
        prefix:   "session:",
        maxAge:   86400 * 30, // 30 days
    }
}

// 获取会话
func (s *RedisStore) Get(r *http.Request, name string) (*sessions.Session, error) {
    session := sessions.NewSession(s.sessions, name)

    // 从Redis加载会话数据
    cookie, err := r.Cookie(name)
    if err == nil {
        data, err := s.client.Get(r.Context(), s.prefix+cookie.Value).Result()
        if err == nil {
            json.Unmarshal([]byte(data), &session.Values)
        }
    }

    return session, nil
}

// 保存会话
func (s *RedisStore) Save(r *http.Request, w http.ResponseWriter, session *sessions.Session) error {
    // 生成会话ID
    if session.ID == "" {
        session.ID = s.generateSessionID()
    }

    // 序列化会话数据
    data, err := json.Marshal(session.Values)
    if err != nil {
        return err
    }

    // 保存到Redis
    err = s.client.Set(r.Context(), s.prefix+session.ID, data, time.Duration(s.maxAge)*time.Second).Err()
    if err != nil {
        return err
    }

    // 设置Cookie
    http.SetCookie(w, &http.Cookie{
        Name:     session.Name(),
        Value:    session.ID,
        Path:     "/",
        MaxAge:   s.maxAge,
        HttpOnly: true,
        Secure:   true,
        SameSite: http.SameSiteLaxMode,
    })

    return nil
}

// 删除会话
func (s *RedisStore) Delete(r *http.Request, w http.ResponseWriter, session *sessions.Session) error {
    // 从Redis删除
    s.client.Del(r.Context(), s.prefix+session.ID)

    // 删除Cookie
    http.SetCookie(w, &http.Cookie{
        Name:     session.Name(),
        Value:    "",
        Path:     "/",
        MaxAge:   -1,
        HttpOnly: true,
    })

    return nil
}

func (s *RedisStore) generateSessionID() string {
    return fmt.Sprintf("%d", time.Now().UnixNano())
}

// Gin中间件
func SessionMiddleware(store *RedisStore) gin.HandlerFunc {
    return func(c *gin.Context) {
        session, err := store.Get(c.Request, "session")
        if err != nil {
            c.AbortWithStatusJSON(500, gin.H{"error": "Session error"})
            return
        }

        c.Set("session", session)

        // 保存会话
        defer func() {
            store.Save(c.Request, c.Writer, session)
        }()

        c.Next()
    }
}
```

### 4.2 会话使用示例

```go
package main

import (
    "net/http"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"
)

func main() {
    r := gin.Default()

    // 初始化Redis和会话存储
    redisClient := redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })

    sessionStore := NewRedisStore(redisClient, []byte("secret-key"))

    // 使用会话中间件
    r.Use(SessionMiddleware(sessionStore))

    // 登录
    r.POST("/login", func(c *gin.Context) {
        session := c.MustGet("session").(*sessions.Session)

        var loginData struct {
            Username string `json:"username"`
            Password string `json:"password"`
        }

        if err := c.ShouldBindJSON(&loginData); err != nil {
            c.JSON(400, gin.H{"error": "Invalid input"})
            return
        }

        // 验证用户
        if loginData.Username == "admin" && loginData.Password == "password" {
            session.Values["user_id"] = 1
            session.Values["username"] = loginData.Username
            session.Values["logged_in"] = true

            c.JSON(200, gin.H{"message": "Login successful"})
        } else {
            c.JSON(401, gin.H{"error": "Invalid credentials"})
        }
    })

    // 受保护的路由
    r.GET("/profile", func(c *gin.Context) {
        session := c.MustGet("session").(*sessions.Session)

        if loggedIn, ok := session.Values["logged_in"].(bool); !ok || !loggedIn {
            c.JSON(401, gin.H{"error": "Not authenticated"})
            return
        }

        c.JSON(200, gin.H{
            "user_id":  session.Values["user_id"],
            "username": session.Values["username"],
        })
    })

    // 登出
    r.POST("/logout", func(c *gin.Context) {
        session := c.MustGet("session").(*sessions.Session)
        sessionStore.Delete(c.Request, c.Writer, session)

        c.JSON(200, gin.H{"message": "Logged out"})
    })

    r.Run(":8080")
}
```

## 5. 计数器和排行榜

### 5.1 计数器实现

```go
package counter

import (
    "context"
    "fmt"
    "time"

    "github.com/go-redis/redis/v8"
)

type RedisCounter struct {
    client *redis.Client
    ctx    context.Context
}

func NewRedisCounter(client *redis.Client) *RedisCounter {
    return &RedisCounter{
        client: client,
        ctx:    context.Background(),
    }
}

// 简单计数器
func (r *RedisCounter) Increment(key string) (int64, error) {
    return r.client.Incr(r.ctx, key).Result()
}

// 带过期时间的计数器
func (r *RedisCounter) IncrementWithExpire(key string, expiration time.Duration) (int64, error) {
    pipe := r.client.Pipeline()
    incrCmd := pipe.Incr(r.ctx, key)
    expireCmd := pipe.Expire(r.ctx, key, expiration)

    _, err := pipe.Exec(r.ctx)
    if err != nil {
        return 0, err
    }

    return incrCmd.Result()
}

// 批量递增
func (r *RedisCounter) IncrementMultiple(keys ...string) ([]int64, error) {
    pipe := r.client.Pipeline()
    cmds := make([]*redis.IntCmd, len(keys))

    for i, key := range keys {
        cmds[i] = pipe.Incr(r.ctx, key)
    }

    _, err := pipe.Exec(r.ctx)
    if err != nil {
        return nil, err
    }

    results := make([]int64, len(keys))
    for i, cmd := range cmds {
        results[i], err = cmd.Result()
        if err != nil {
            return nil, err
        }
    }

    return results, nil
}

// 获取计数器值
func (r *RedisCounter) Get(key string) (int64, error) {
    return r.client.Get(r.ctx, key).Int64()
}

// 设置计数器值
func (r *RedisCounter) Set(key string, value int64) error {
    return r.client.Set(r.ctx, key, value, 0).Err()
}

// 删除计数器
func (r *RedisCounter) Delete(key string) error {
    return r.client.Del(r.ctx, key).Err()
}
```

### 5.2 排行榜实现

```go
package leaderboard

import (
    "context"
    "fmt"
    "time"

    "github.com/go-redis/redis/v8"
)

type RedisLeaderboard struct {
    client *redis.Client
    ctx    context.Context
}

func NewRedisLeaderboard(client *redis.Client) *RedisLeaderboard {
    return &RedisLeaderboard{
        client: client,
        ctx:    context.Background(),
    }
}

// 添加分数
func (r *RedisLeaderboard) AddScore(key string, member string, score float64) error {
    return r.client.ZAdd(r.ctx, key, &redis.Z{Score: score, Member: member}).Err()
}

// 批量添加分数
func (r *RedisLeaderboard) AddScores(key string, members []redis.Z) error {
    return r.client.ZAdd(r.ctx, key, members...).Err()
}

// 获取排名
func (r *RedisLeaderboard) GetRank(key string, member string) (int64, error) {
    return r.client.ZRank(r.ctx, key, member).Result()
}

// 获取分数
func (r *RedisLeaderboard) GetScore(key string, member string) (float64, error) {
    return r.client.ZScore(r.ctx, key, member).Result()
}

// 获取前N名
func (r *RedisLeaderboard) GetTopN(key string, n int64) ([]redis.Z, error) {
    return r.client.ZRevRangeWithScores(r.ctx, key, 0, n-1).Result()
}

// 获取用户排名范围内的成员
func (r *RedisLeaderboard) GetRangeByRank(key string, start, stop int64) ([]redis.Z, error) {
    return r.client.ZRangeWithScores(r.ctx, key, start, stop).Result()
}

// 获取分数范围内的成员
func (r *RedisLeaderboard) GetRangeByScore(key string, min, max float64) ([]redis.Z, error) {
    return r.client.ZRangeByScoreWithScores(r.ctx, key, &redis.ZRangeBy{
        Min: fmt.Sprintf("%f", min),
        Max: fmt.Sprintf("%f", max),
    }).Result()
}

// 获取总成员数
func (r *RedisLeaderboard) GetCount(key string) (int64, error) {
    return r.client.ZCard(r.ctx, key).Result()
}

// 移除成员
func (r *RedisLeaderboard) RemoveMember(key string, member string) error {
    return r.client.ZRem(r.ctx, key, member).Err()
}

// 带过期时间的排行榜
func (r *RedisLeaderboard) AddScoreWithExpire(key string, member string, score float64, expiration time.Duration) error {
    pipe := r.client.Pipeline()
    pipe.ZAdd(r.ctx, key, &redis.Z{Score: score, Member: member})
    pipe.Expire(r.ctx, key, expiration)

    _, err := pipe.Exec(r.ctx)
    return err
}
```

### 5.3 游戏排行榜示例

```go
package main

import (
    "net/http"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"
)

type GameScore struct {
    PlayerID string  `json:"player_id"`
    Score    float64 `json:"score"`
}

func main() {
    r := gin.Default()

    // 初始化Redis
    redisClient := redis.NewClient(&redis.Options{
        Addr: "localhost:6379",
    })

    leaderboard := NewRedisLeaderboard(redisClient)

    // 提交分数
    r.POST("/score", func(c *gin.Context) {
        var score GameScore
        if err := c.ShouldBindJSON(&score); err != nil {
            c.JSON(400, gin.H{"error": "Invalid input"})
            return
        }

        err := leaderboard.AddScore("game_scores", score.PlayerID, score.Score)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(200, gin.H{"message": "Score submitted"})
    })

    // 获取排行榜
    r.GET("/leaderboard", func(c *gin.Context) {
        topN, err := leaderboard.GetTopN("game_scores", 10)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(200, gin.H{"leaderboard": topN})
    })

    // 获取玩家排名
    r.GET("/rank/:player_id", func(c *gin.Context) {
        playerID := c.Param("player_id")

        rank, err := leaderboard.GetRank("game_scores", playerID)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        score, err := leaderboard.GetScore("game_scores", playerID)
        if err != nil {
            c.JSON(500, gin.H{"error": err.Error()})
            return
        }

        c.JSON(200, gin.H{
            "player_id": playerID,
            "rank":      rank + 1, // 排名从1开始
            "score":     score,
        })
    })

    r.Run(":8080")
}
```

## 6. 消息队列

### 6.1 Redis消息队列实现

```go
package queue

import (
    "context"
    "encoding/json"
    "fmt"
    "time"

    "github.com/go-redis/redis/v8"
)

type RedisQueue struct {
    client    *redis.Client
    ctx       context.Context
    queueName string
}

type QueueMessage struct {
    ID      string      `json:"id"`
    Type    string      `json:"type"`
    Payload interface{} `json:"payload"`
    Created time.Time   `json:"created"`
}

func NewRedisQueue(client *redis.Client, queueName string) *RedisQueue {
    return &RedisQueue{
        client:    client,
        ctx:       context.Background(),
        queueName: queueName,
    }
}

// 推送消息
func (q *RedisQueue) Push(message *QueueMessage) error {
    message.Created = time.Now()

    data, err := json.Marshal(message)
    if err != nil {
        return err
    }

    return q.client.LPush(q.ctx, q.queueName, data).Err()
}

// 弹出消息
func (q *RedisQueue) Pop() (*QueueMessage, error) {
    result, err := q.client.BRPop(q.ctx, 30*time.Second, q.queueName).Result()
    if err != nil {
        return nil, err
    }

    var message QueueMessage
    err = json.Unmarshal([]byte(result[1]), &message)
    if err != nil {
        return nil, err
    }

    return &message, nil
}

// 批量推送
func (q *RedisQueue) PushBatch(messages []*QueueMessage) error {
    pipe := q.client.Pipeline()

    for _, message := range messages {
        message.Created = time.Now()
        data, err := json.Marshal(message)
        if err != nil {
            return err
        }

        pipe.LPush(q.ctx, q.queueName, data)
    }

    _, err := pipe.Exec(q.ctx)
    return err
}

// 获取队列长度
func (q *RedisQueue) Length() (int64, error) {
    return q.client.LLen(q.ctx, q.queueName).Result()
}

// 清空队列
func (q *RedisQueue) Clear() error {
    return q.client.Del(q.ctx, q.queueName).Err()
}
```

### 6.2 延迟队列实现

```go
package queue

import (
    "context"
    "encoding/json"
    "fmt"
    "time"

    "github.com/go-redis/redis/v8"
)

type DelayedQueue struct {
    client         *redis.Client
    ctx            context.Context
    queueName      string
    processingName string
}

func NewDelayedQueue(client *redis.Client, queueName string) *DelayedQueue {
    return &DelayedQueue{
        client:         client,
        ctx:            context.Background(),
        queueName:      queueName,
        processingName: queueName + ":processing",
    }
}

// 添加延迟消息
func (q *DelayedQueue) PushDelayed(message *QueueMessage, delay time.Duration) error {
    message.Created = time.Now()

    data, err := json.Marshal(message)
    if err != nil {
        return err
    }

    score := float64(time.Now().Add(delay).Unix())
    return q.client.ZAdd(q.ctx, q.queueName, &redis.Z{Score: score, Member: data}).Err()
}

// 获取到期消息
func (q *DelayedQueue) PopDelayed() (*QueueMessage, error) {
    now := time.Now().Unix()

    // 使用Lua脚本原子性地获取到期消息
    script := `
        local messages = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1], 'LIMIT', 0, 1)
        if #messages > 0 then
            redis.call('ZREM', KEYS[1], messages[1])
            return messages[1]
        else
            return nil
        end
    `

    result, err := q.client.Eval(q.ctx, script, []string{q.queueName}, now).Result()
    if err != nil || result == nil {
        return nil, err
    }

    var message QueueMessage
    err = json.Unmarshal([]byte(result.(string)), &message)
    if err != nil {
        return nil, err
    }

    return &message, nil
}

// 移动到期消息到处理队列
func (q *DelayedQueue) MoveToProcessing() (int64, error) {
    now := time.Now().Unix()

    script := `
        local messages = redis.call('ZRANGEBYSCORE', KEYS[1], 0, ARGV[1], 'LIMIT', 0, 10)
        local count = 0

        for i, message in ipairs(messages) do
            if redis.call('ZREM', KEYS[1], message) == 1 then
                redis.call('LPUSH', KEYS[2], message)
                count = count + 1
            end
        end

        return count
    `

    result, err := q.client.Eval(q.ctx, script, []string{q.queueName, q.processingName}, now).Result()
    if err != nil {
        return 0, err
    }

    return result.(int64), nil
}
```

## 7. 性能优化

### 7.1 连接池优化

```go
package redis

import (
    "context"
    "time"

    "github.com/go-redis/redis/v8"
)

// 优化的Redis配置
func NewOptimizedRedisClient() *redis.Client {
    return redis.NewClient(&redis.Options{
        Addr:         "localhost:6379",
        Password:     "",
        DB:           0,

        // 连接池配置
        PoolSize:     100,           // 连接池大小
        MinIdleConns: 10,            // 最小空闲连接数
        MaxConnAge:   30 * time.Minute, // 连接最大生命周期
        PoolTimeout:  30 * time.Second,  // 获取连接超时时间
        IdleTimeout:  5 * time.Minute,   // 空闲连接超时时间

        // 网络配置
        DialTimeout:  5 * time.Second,  // 建立连接超时
        ReadTimeout:  3 * time.Second,  // 读取超时
        WriteTimeout: 3 * time.Second,  // 写入超时

        // 重试配置
        MaxRetries:   3,
        MinRetryBackoff: 8 * time.Millisecond,
        MaxRetryBackoff: 512 * time.Millisecond,
    })
}

// 连接池监控
type PoolMonitor struct {
    client *redis.Client
    ctx    context.Context
}

func NewPoolMonitor(client *redis.Client) *PoolMonitor {
    return &PoolMonitor{
        client: client,
        ctx:    context.Background(),
    }
}

func (p *PoolMonitor) GetStats() *redis.PoolStats {
    return p.client.PoolStats()
}

func (p *PoolMonitor) LogStats() {
    stats := p.GetStats()
    fmt.Printf("Redis Pool Stats:\n")
    fmt.Printf("  Hits: %d\n", stats.Hits)
    fmt.Printf("  Misses: %d\n", stats.Misses)
    fmt.Printf("  Timeouts: %d\n", stats.Timeouts)
    fmt.Printf("  Total Conns: %d\n", stats.TotalConns)
    fmt.Printf("  Idle Conns: %d\n", stats.IdleConns)
    fmt.Printf("  Stale Conns: %d\n", stats.StaleConns)
}
```

### 7.2 Pipeline批量操作

```go
package redis

import (
    "context"
    "fmt"

    "github.com/go-redis/redis/v8"
)

// Pipeline批量操作示例
func BatchOperationsExample(client *redis.Client) error {
    ctx := context.Background()

    // 创建Pipeline
    pipe := client.Pipeline()

    // 批量设置
    pipe.Set(ctx, "key1", "value1", 0)
    pipe.Set(ctx, "key2", "value2", 0)
    pipe.Set(ctx, "key3", "value3", 0)

    // 批量递增
    pipe.Incr(ctx, "counter1")
    pipe.Incr(ctx, "counter2")

    // 批量获取
    get1 := pipe.Get(ctx, "key1")
    get2 := pipe.Get(ctx, "key2")

    // 执行所有操作
    _, err := pipe.Exec(ctx)
    if err != nil {
        return err
    }

    // 获取结果
    val1, err := get1.Result()
    if err != nil {
        return err
    }

    val2, err := get2.Result()
    if err != nil {
        return err
    }

    fmt.Printf("key1: %s, key2: %s\n", val1, val2)
    return nil
}

// 事务操作
func TransactionExample(client *redis.Client) error {
    ctx := context.Background()

    // 使用Watch实现乐观锁
    err := client.Watch(ctx, func(tx *redis.Tx) error {
        // 获取当前值
        current, err := tx.Get(ctx, "balance").Int()
        if err != nil {
            return err
        }

        // 检查余额
        if current < 100 {
            return fmt.Errorf("insufficient balance")
        }

        // 执行事务
        _, err = tx.TxPipelined(ctx, func(pipe redis.Pipeliner) error {
            pipe.Set(ctx, "balance", current-100, 0)
            pipe.Set(ctx, "expense", 100, 0)
            return nil
        })

        return err
    }, "balance")

    return err
}
```

## 8. 监控和诊断

### 8.1 Redis监控中间件

```go
package middleware

import (
    "strconv"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"
    "github.com/prometheus/client_golang/prometheus"
    "github.com/prometheus/client_golang/prometheus/promauto"
)

var (
    redisRequestCount = promauto.NewCounterVec(prometheus.CounterOpts{
        Name: "redis_requests_total",
        Help: "Total number of Redis requests",
    }, []string{"operation", "status"})

    redisRequestDuration = promauto.NewHistogramVec(prometheus.HistogramOpts{
        Name: "redis_request_duration_seconds",
        Help: "Redis request duration in seconds",
    }, []string{"operation"})
)

type RedisMonitor struct {
    client *redis.Client
}

func NewRedisMonitor(client *redis.Client) *RedisMonitor {
    return &RedisMonitor{
        client: client,
    }
}

func (m *RedisMonitor) MonitorMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        // 包装Redis客户端以监控操作
        originalClient := m.client
        monitoredClient := m.wrapClient(originalClient)
        c.Set("redis", monitoredClient)

        c.Next()

        duration := time.Since(start)
        operation := c.GetString("redis_operation")

        if operation != "" {
            redisRequestDuration.WithLabelValues(operation).Observe(duration.Seconds())
            redisRequestCount.WithLabelValues(operation, "success").Inc()
        }
    }
}

func (m *RedisMonitor) wrapClient(client *redis.Client) *redis.Client {
    // 这里简化了实际的包装逻辑
    // 实际实现需要包装每个Redis操作
    return client
}

// 健康检查
func (m *RedisMonitor) HealthCheck() error {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    return m.client.Ping(ctx).Err()
}

// 获取Redis信息
func (m *RedisMonitor) GetInfo() (map[string]string, error) {
    ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
    defer cancel()

    info, err := m.client.Info(ctx).Result()
    if err != nil {
        return nil, err
    }

    // 解析info输出
    result := make(map[string]string)
    lines := strings.Split(info, "\n")

    for _, line := range lines {
        if strings.Contains(line, ":") {
            parts := strings.SplitN(line, ":", 2)
            if len(parts) == 2 {
                result[strings.TrimSpace(parts[0])] = strings.TrimSpace(parts[1])
            }
        }
    }

    return result, nil
}
```

### 8.2 慢查询监控

```go
package monitoring

import (
    "context"
    "fmt"
    "log"
    "time"

    "github.com/go-redis/redis/v8"
)

type SlowQueryMonitor struct {
    client      *redis.Client
    ctx         context.Context
    slowLogChan chan *redis.SlowLog
    threshold   time.Duration
}

func NewSlowQueryMonitor(client *redis.Client, threshold time.Duration) *SlowQueryMonitor {
    return &SlowQueryMonitor{
        client:      client,
        ctx:         context.Background(),
        slowLogChan: make(chan *redis.SlowLog, 100),
        threshold:   threshold,
    }
}

func (m *SlowQueryMonitor) Start() {
    go m.monitor()
    go m.processSlowLogs()
}

func (m *SlowQueryMonitor) monitor() {
    ticker := time.NewTicker(10 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            logs, err := m.client.SlowLogGet(m.ctx, 10).Result()
            if err != nil {
                log.Printf("Failed to get slow logs: %v", err)
                continue
            }

            for _, log := range logs {
                if time.Duration(log.ExecutionTime)*time.Microsecond > m.threshold {
                    m.slowLogChan <- log
                }
            }
        }
    }
}

func (m *SlowQueryMonitor) processSlowLogs() {
    for log := range m.slowLogChan {
        log.Printf("SLOW QUERY DETECTED:\n")
        log.Printf("  Execution Time: %d μs\n", log.ExecutionTime)
        log.Printf("  Timestamp: %d\n", log.Timestamp)
        log.Printf("  Command: %v\n", log.Args)

        // 可以在这里添加告警逻辑
    }
}
```

## 9. 最佳实践总结

### 9.1 配置最佳实践

1. **连接池配置**
   - 根据应用负载调整连接池大小
   - 设置合理的最小空闲连接数
   - 配置连接超时和空闲超时

2. **网络配置**
   - 设置合理的读写超时
   - 启用TCP Keepalive
   - 使用连接复用

3. **安全配置**
   - 启用密码认证
   - 使用TLS加密连接
   - 配置访问控制

### 9.2 缓存最佳实践

1. **缓存策略**
   - 使用合适的缓存模式（Cache-Aside、Read-Through等）
   - 实现缓存穿透和雪崩保护
   - 设置合理的过期时间

2. **缓存设计**
   - 使用有意义的键名
   - 实现缓存预热
   - 监控缓存命中率

3. **数据一致性**
   - 实现缓存失效策略
   - 处理并发更新
   - 使用事务保证一致性

### 9.3 性能最佳实践

1. **批量操作**
   - 使用Pipeline减少网络往返
   - 批量获取和设置数据
   - 合并相关操作

2. **数据结构优化**
   - 选择合适的数据结构
   - 避免大Key和热Key
   - 使用压缩减少内存占用

3. **监控和优化**
   - 监控Redis性能指标
   - 分析慢查询
   - 定期优化数据结构

### 9.4 错误处理最佳实践

1. **连接错误**
   - 实现重试机制
   - 处理连接超时
   - 监控连接状态

2. **数据错误**
   - 验证数据格式
   - 处理序列化错误
   - 实现降级策略

3. **业务错误**
   - 提供有意义的错误信息
   - 实现错误恢复机制
   - 记录错误日志

通过遵循这些最佳实践，你可以在Gin应用中高效、安全地使用Redis，构建高性能的后端服务。