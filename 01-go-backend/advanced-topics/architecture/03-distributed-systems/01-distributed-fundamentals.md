# 分布式系统基础

## 概述

分布式系统是由多个独立计算机组成的系统，这些计算机通过网络进行通信和协调，共同完成共同的任务。本文档将深入探讨分布式系统的核心概念、设计原则和实现方式。

## 目录

- [分布式系统概述](#分布式系统概述)
- [CAP理论](#cap理论)
- [BASE理论](#base理论)
- [一致性模型](#一致性模型)
- [分布式事务](#分布式事务)
- [分布式锁](#分布式锁)
- [服务发现](#服务发现)
- [负载均衡](#负载均衡)
- [容错机制](#容错机制)
- [监控和可观测性](#监控和可观测性)
- [最佳实践总结](#最佳实践总结)

## 分布式系统概述

### 分布式系统特点

```go
// internal/pkg/distributed/fundamentals.go
package distributed

// 分布式系统特点
/*
1. 透明性：用户无需关心系统的分布特性
2. 可扩展性：可以通过添加节点来扩展系统
3. 可靠性：单个节点的故障不会影响整个系统
4. 高可用性：系统可以持续提供服务
5. 一致性：所有节点看到的数据是一致的
6. 分区容忍性：系统在网络分区时仍能工作
*/

// 分布式系统配置
type DistributedSystemConfig struct {
    // 节点配置
    Nodes []NodeConfig `yaml:"nodes"`

    // 网络配置
    Network NetworkConfig `yaml:"network"`

    // 一致性配置
    Consistency ConsistencyConfig `yaml:"consistency"`

    // 容错配置
    FaultTolerance FaultToleranceConfig `yaml:"fault_tolerance"`

    // 监控配置
    Monitoring MonitoringConfig `yaml:"monitoring"`
}

// 节点配置
type NodeConfig struct {
    ID       string            `yaml:"id"`
    Address  string            `yaml:"address"`
    Port     int               `yaml:"port"`
    Role     NodeRole          `yaml:"role"`
    Metadata map[string]string `yaml:"metadata"`
}

// 节点角色
type NodeRole string

const (
    RoleLeader     NodeRole = "leader"
    RoleFollower   NodeRole = "follower"
    RoleCandidate  NodeRole = "candidate"
    RoleWorker     NodeRole = "worker"
    RoleCoordinator NodeRole = "coordinator"
)

// 网络配置
type NetworkConfig struct {
    // 心跳间隔
    HeartbeatInterval time.Duration `yaml:"heartbeat_interval"`

    // 选举超时
    ElectionTimeout time.Duration `yaml:"election_timeout"`

    // RPC超时
    RPCTimeout time.Duration `yaml:"rpc_timeout"`

    // 重试配置
    Retry RetryConfig `yaml:"retry"`

    // 负载均衡配置
    LoadBalancer LoadBalancerConfig `yaml:"load_balancer"`
}

// 重试配置
type RetryConfig struct {
    MaxAttempts int           `yaml:"max_attempts"`
    InitialDelay time.Duration `yaml:"initial_delay"`
    MaxDelay    time.Duration `yaml:"max_delay"`
    Backoff     float64       `yaml:"backoff"`
}

// 负载均衡配置
type LoadBalancerConfig struct {
    Strategy LoadBalancingStrategy `yaml:"strategy"`
    HealthCheck HealthCheckConfig   `yaml:"health_check"`
}

// 负载均衡策略
type LoadBalancingStrategy string

const (
    StrategyRoundRobin   LoadBalancingStrategy = "round_robin"
    StrategyLeastConn    LoadBalancingStrategy = "least_connection"
    StrategyRandom       LoadBalancingStrategy = "random"
    StrategyConsistentHash LoadBalancingStrategy = "consistent_hash"
)

// 健康检查配置
type HealthCheckConfig struct {
    Interval   time.Duration `yaml:"interval"`
    Timeout    time.Duration `yaml:"timeout"`
    Threshold  int           `yaml:"threshold"`
    Path       string        `yaml:"path"`
}

// 一致性配置
type ConsistencyConfig struct {
    // 一致性级别
    Level ConsistencyLevel `yaml:"level"`

    // 复制因子
    ReplicationFactor int `yaml:"replication_factor"`

    // 写一致性级别
    WriteConsistency WriteConsistencyLevel `yaml:"write_consistency"`

    // 读一致性级别
    ReadConsistency ReadConsistencyLevel `yaml:"read_consistency"`
}

// 一致性级别
type ConsistencyLevel string

const (
    ConsistencyStrong   ConsistencyLevel = "strong"
    ConsistencyEventual ConsistencyLevel = "eventual"
    ConsistencyWeak     ConsistencyLevel = "weak"
)

// 写一致性级别
type WriteConsistencyLevel string

const (
    WriteConsistencyOne    WriteConsistencyLevel = "one"
    WriteConsistencyQuorum  WriteConsistencyLevel = "quorum"
    WriteConsistencyAll    WriteConsistencyLevel = "all"
)

// 读一致性级别
type ReadConsistencyLevel string

const (
    ReadConsistencyOne    ReadConsistencyLevel = "one"
    ReadConsistencyQuorum  ReadConsistencyLevel = "quorum"
    ReadConsistencyAll    ReadConsistencyLevel = "all"
)

// 容错配置
type FaultToleranceConfig struct {
    // 副本数量
    Replicas int `yaml:"replicas"`

    // 故障检测
    FailureDetection FailureDetectionConfig `yaml:"failure_detection"`

    // 恢复策略
    Recovery RecoveryConfig `yaml:"recovery"`
}

// 故障检测配置
type FailureDetectionConfig struct {
    // 故障检测超时
    Timeout time.Duration `yaml:"timeout"`

    // 心跳间隔
    HeartbeatInterval time.Duration `yaml:"heartbeat_interval"`

    // 可疑阈值
    SuspicionThreshold int `yaml:"suspicion_threshold"`

    // 故障阈值
    FailureThreshold int `yaml:"failure_threshold"`
}

// 恢复配置
type RecoveryConfig struct {
    // 自动恢复
    AutoRecovery bool `yaml:"auto_recovery"`

    // 恢复超时
    RecoveryTimeout time.Duration `yaml:"recovery_timeout"`

    // 数据同步策略
    DataSyncStrategy DataSyncStrategy `yaml:"data_sync_strategy"`
}

// 数据同步策略
type DataSyncStrategy string

const (
    SyncStrategyFull    DataSyncStrategy = "full"
    SyncStrategyDelta   DataSyncStrategy = "delta"
    SyncStrategySnapshot DataSyncStrategy = "snapshot"
)

// 监控配置
type MonitoringConfig struct {
    // 指标收集
    Metrics MetricsConfig `yaml:"metrics"`

    // 日志收集
    Logging LoggingConfig `yaml:"logging"`

    // 追踪
    Tracing TracingConfig `yaml:"tracing"`
}

// 指标配置
type MetricsConfig struct {
    Enabled   bool     `yaml:"enabled"`
    Endpoints []string `yaml:"endpoints"`
    Interval  time.Duration `yaml:"interval"`
}

// 日志配置
type LoggingConfig struct {
    Level  string   `yaml:"level"`
    Format string   `yaml:"format"`
    Output string   `yaml:"output"`
    Topics []string `yaml:"topics"`
}

// 追踪配置
type TracingConfig struct {
    Enabled bool   `yaml:"enabled"`
    Service string `yaml:"service"`
    Sample  float64 `yaml:"sample"`
}
```

### 节点管理

```go
// internal/pkg/distributed/node.go
package distributed

import (
    "context"
    "sync"
    "time"
)

// 分布式节点
type DistributedNode struct {
    config     *NodeConfig
    state      NodeState
    cluster    *Cluster
    services   map[string]interface{}
    mutex      sync.RWMutex
    started    bool
    stopped    bool
}

// 节点状态
type NodeState struct {
    ID        string
    Address   string
    Port      int
    Role      NodeRole
    Status    NodeStatus
    LastSeen  time.Time
    Metadata  map[string]interface{}
    Version   int
}

// 节点状态
type NodeStatus string

const (
    StatusStarting   NodeStatus = "starting"
    StatusRunning    NodeStatus = "running"
    StatusStopping  NodeStatus = "stopping"
    StatusStopped   NodeStatus = "stopped"
    StatusFailed    NodeStatus = "failed"
    StatusUnknown   NodeStatus = "unknown"
)

// 创建分布式节点
func NewDistributedNode(config *NodeConfig) *DistributedNode {
    return &DistributedNode{
        config:   config,
        state: NodeState{
            ID:       config.ID,
            Address:  config.Address,
            Port:     config.Port,
            Role:     config.Role,
            Status:   StatusStarting,
            LastSeen: time.Now(),
            Metadata: make(map[string]interface{}),
            Version:  1,
        },
        services: make(map[string]interface{}),
    }
}

// 启动节点
func (dn *DistributedNode) Start(ctx context.Context) error {
    dn.mutex.Lock()
    defer dn.mutex.Unlock()

    if dn.started {
        return errors.New("node already started")
    }

    // 初始化集群连接
    if err := dn.initializeCluster(ctx); err != nil {
        return fmt.Errorf("failed to initialize cluster: %w", err)
    }

    // 启动服务
    if err := dn.startServices(ctx); err != nil {
        return fmt.Errorf("failed to start services: %w", err)
    }

    // 启动心跳
    go dn.heartbeatLoop(ctx)

    // 启动健康检查
    go dn.healthCheckLoop(ctx)

    dn.state.Status = StatusRunning
    dn.started = true

    return nil
}

// 停止节点
func (dn *DistributedNode) Stop(ctx context.Context) error {
    dn.mutex.Lock()
    defer dn.mutex.Unlock()

    if dn.stopped {
        return errors.New("node already stopped")
    }

    dn.state.Status = StatusStopping

    // 停止服务
    if err := dn.stopServices(ctx); err != nil {
        return fmt.Errorf("failed to stop services: %w", err)
    }

    // 离开集群
    if dn.cluster != nil {
        if err := dn.cluster.Leave(ctx, dn.state.ID); err != nil {
            return fmt.Errorf("failed to leave cluster: %w", err)
        }
    }

    dn.state.Status = StatusStopped
    dn.stopped = true

    return nil
}

// 初始化集群
func (dn *DistributedNode) initializeCluster(ctx context.Context) error {
    // 创建集群连接
    cluster, err := NewCluster(dn.config, dn)
    if err != nil {
        return err
    }

    // 加入集群
    if err := cluster.Join(ctx, &dn.state); err != nil {
        return err
    }

    dn.cluster = cluster
    return nil
}

// 启动服务
func (dn *DistributedNode) startServices(ctx context.Context) error {
    // 根据节点角色启动不同的服务
    switch dn.config.Role {
    case RoleLeader:
        if err := dn.startLeaderServices(ctx); err != nil {
            return err
        }
    case RoleWorker:
        if err := dn.startWorkerServices(ctx); err != nil {
            return err
        }
    case RoleCoordinator:
        if err := dn.startCoordinatorServices(ctx); err != nil {
            return err
        }
    }

    return nil
}

// 心跳循环
func (dn *DistributedNode) heartbeatLoop(ctx context.Context) {
    ticker := time.NewTicker(5 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            if err := dn.sendHeartbeat(ctx); err != nil {
                log.Printf("Failed to send heartbeat: %v", err)
            }
        case <-ctx.Done():
            return
        }
    }
}

// 发送心跳
func (dn *DistributedNode) sendHeartbeat(ctx context.Context) error {
    dn.mutex.Lock()
    dn.state.LastSeen = time.Now()
    dn.state.Version++
    state := dn.state
    dn.mutex.Unlock()

    if dn.cluster != nil {
        return dn.cluster.Heartbeat(ctx, state.ID, &state)
    }

    return nil
}

// 健康检查循环
func (dn *DistributedNode) healthCheckLoop(ctx context.Context) {
    ticker := time.NewTicker(10 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            if err := dn.checkHealth(ctx); err != nil {
                log.Printf("Health check failed: %v", err)
            }
        case <-ctx.Done():
            return
        }
    }
}

// 健康检查
func (dn *DistributedNode) checkHealth(ctx context.Context) error {
    // 检查服务健康状态
    for name, service := range dn.services {
        if healthChecker, ok := service.(HealthChecker); ok {
            if !healthChecker.IsHealthy() {
                log.Printf("Service %s is unhealthy", name)
            }
        }
    }

    return nil
}

// 注册服务
func (dn *DistributedNode) RegisterService(name string, service interface{}) {
    dn.mutex.Lock()
    defer dn.mutex.Unlock()
    dn.services[name] = service
}

// 获取服务
func (dn *DistributedNode) GetService(name string) (interface{}, bool) {
    dn.mutex.RLock()
    defer dn.mutex.RUnlock()
    service, exists := dn.services[name]
    return service, exists
}

// 健康检查器接口
type HealthChecker interface {
    IsHealthy() bool
}
```

## CAP理论

### CAP理论实现

```go
// internal/pkg/distributed/cap.go
package distributed

// CAP理论中的权衡
/*
C (Consistency): 一致性
A (Availability): 可用性
P (Partition Tolerance): 分区容忍性

在分布式系统中，只能同时满足其中的两个特性：
- CP: 一致性和分区容忍性（牺牲可用性）
- AP: 可用性和分区容忍性（牺牲一致性）
- CA: 一致性和可用性（牺牲分区容忍性）
*/

// CAP配置
type CAPConfig struct {
    // CAP策略
    Strategy CAPStrategy `yaml:"strategy"`

    // 一致性配置
    Consistency ConsistencyConfig `yaml:"consistency"`

    // 可用性配置
    Availability AvailabilityConfig `yaml:"availability"`

    // 分区容忍性配置
    PartitionTolerance PartitionToleranceConfig `yaml:"partition_tolerance"`
}

// CAP策略
type CAPStrategy string

const (
    StrategyCP CAPStrategy = "cp" // 一致性和分区容忍性
    StrategyAP CAPStrategy = "ap" // 可用性和分区容忍性
    StrategyCA CAPStrategy = "ca" // 一致性和可用性
)

// 可用性配置
type AvailabilityConfig struct {
    // 最小可用节点数
    MinAvailableNodes int `yaml:"min_available_nodes"`

    // 降级策略
    Degradation DegradationConfig `yaml:"degradation"`

    // 限流配置
    RateLimit RateLimitConfig `yaml:"rate_limit"`
}

// 降级配置
type DegradationConfig struct {
    // 自动降级
    AutoDegradation bool `yaml:"auto_degradation"`

    // 降级阈值
    DegradationThreshold float64 `yaml:"degradation_threshold"`

    // 降级策略
    DegradationStrategy DegradationStrategy `yaml:"degradation_strategy"`
}

// 降级策略
type DegradationStrategy string

const (
    DegradationStrategyCacheOnly   DegradationStrategy = "cache_only"
    DegradationStrategyReadReplica DegradationStrategy = "read_replica"
    DegradationStrategyFallback    DegradationStrategy = "fallback"
)

// 限流配置
type RateLimitConfig struct {
    // 每秒请求数限制
    RequestsPerSecond int `yaml:"requests_per_second"`

    // 突发请求数限制
    BurstSize int `yaml:"burst_size"`

    // 限流策略
    Strategy RateLimitStrategy `yaml:"strategy"`
}

// 限流策略
type RateLimitStrategy string

const (
    RateLimitStrategyTokenBucket   RateLimitStrategy = "token_bucket"
    RateLimitStrategySlidingWindow RateLimitStrategy = "sliding_window"
    RateLimitStrategyLeakyBucket   RateLimitStrategy = "leaky_bucket"
)

// 分区容忍性配置
type PartitionToleranceConfig struct {
    // 分区检测策略
    PartitionDetection PartitionDetectionConfig `yaml:"partition_detection"`

    // 分区恢复策略
    PartitionRecovery PartitionRecoveryConfig `yaml:"partition_recovery"`

    // 数据同步策略
    DataSynchronization DataSyncConfig `yaml:"data_synchronization"`
}

// 分区检测配置
type PartitionDetectionConfig struct {
    // 检测间隔
    Interval time.Duration `yaml:"interval"`

    // 超时时间
    Timeout time.Duration `yaml:"timeout"`

    // 检测策略
    Strategy PartitionDetectionStrategy `yaml:"strategy"`
}

// 分区检测策略
type PartitionDetectionStrategy string

const (
    PartitionDetectionStrategyHeartbeat PartitionDetectionStrategy = "heartbeat"
    PartitionDetectionStrategyGossip    PartitionDetectionStrategy = "gossip"
    PartitionDetectionStrategyPing      PartitionDetectionStrategy = "ping"
)

// 分区恢复配置
type PartitionRecoveryConfig struct {
    // 自动恢复
    AutoRecovery bool `yaml:"auto_recovery"`

    // 恢复策略
    RecoveryStrategy RecoveryStrategy `yaml:"recovery_strategy"`

    // 数据合并策略
    DataMergeStrategy DataMergeStrategy `yaml:"data_merge_strategy"`
}

// 恢复策略
type RecoveryStrategy string

const (
    RecoveryStrategyLeaderElection  RecoveryStrategy = "leader_election"
    RecoveryStrategyDataSync       RecoveryStrategy = "data_sync"
    RecoveryStrategyStateTransfer  RecoveryStrategy = "state_transfer"
)

// 数据合并策略
type DataMergeStrategy string

const (
    DataMergeStrategyLastWriteWins  DataMergeStrategy = "last_write_wins"
    DataMergeStrategyVersionVector  DataMergeStrategy = "version_vector"
    DataMergeStrategyConflictFree   DataMergeStrategy = "conflict_free"
)

// 数据同步配置
type DataSyncConfig struct {
    // 同步策略
    Strategy DataSyncStrategy `yaml:"strategy"`

    // 同步间隔
    Interval time.Duration `yaml:"interval"`

    // 批量大小
    BatchSize int `yaml:"batch_size"`

    // 压缩配置
    Compression CompressionConfig `yaml:"compression"`
}

// 压缩配置
type CompressionConfig struct {
    Enabled bool   `yaml:"enabled"`
    Algorithm string `yaml:"algorithm"`
    Level    int    `yaml:"level"`
}

// CAP管理器
type CAPManager struct {
    config *CAPConfig
    node   *DistributedNode
    cluster *Cluster

    // 一致性管理
    consistencyManager *ConsistencyManager

    // 可用性管理
    availabilityManager *AvailabilityManager

    // 分区管理
    partitionManager *PartitionManager

    // 状态
    currentCAPState CAPState
}

// CAP状态
type CAPState struct {
    Strategy CAPStrategy
    Mode      CAPMode
    Partition bool
    Degraded  bool
}

// CAP模式
type CAPMode string

const (
    CAPModeNormal   CAPMode = "normal"
    CAPModeDegraded CAPMode = "degraded"
    CAPModeRecovery CAPMode = "recovery"
)

// 创建CAP管理器
func NewCAPManager(config *CAPConfig, node *DistributedNode, cluster *Cluster) *CAPManager {
    return &CAPManager{
        config: config,
        node:   node,
        cluster: cluster,

        consistencyManager: NewConsistencyManager(&config.Consistency),
        availabilityManager: NewAvailabilityManager(&config.Availability),
        partitionManager: NewPartitionManager(&config.PartitionTolerance),

        currentCAPState: CAPState{
            Strategy: config.Strategy,
            Mode:      CAPModeNormal,
            Partition: false,
            Degraded:  false,
        },
    }
}

// 初始化CAP管理器
func (cm *CAPManager) Initialize(ctx context.Context) error {
    // 初始化一致性管理器
    if err := cm.consistencyManager.Initialize(ctx); err != nil {
        return err
    }

    // 初始化可用性管理器
    if err := cm.availabilityManager.Initialize(ctx); err != nil {
        return err
    }

    // 初始化分区管理器
    if err := cm.partitionManager.Initialize(ctx); err != nil {
        return err
    }

    // 启动监控
    go cm.monitorCAPState(ctx)

    return nil
}

// 监控CAP状态
func (cm *CAPManager) monitorCAPState(ctx context.Context) {
    ticker := time.NewTicker(5 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            cm.updateCAPState(ctx)
        case <-ctx.Done():
            return
        }
    }
}

// 更新CAP状态
func (cm *CAPManager) updateCAPState(ctx context.Context) {
    // 检查分区状态
    partition := cm.partitionManager.HasPartition()

    // 检查系统健康状态
    degraded := cm.availabilityManager.IsDegraded()

    // 根据策略和状态决定当前模式
    mode := CAPModeNormal
    if partition || degraded {
        switch cm.config.Strategy {
        case StrategyCP:
            if partition {
                mode = CAPModeDegraded
            }
        case StrategyAP:
            if degraded {
                mode = CAPModeDegraded
            }
        case StrategyCA:
            if partition {
                mode = CAPModeDegraded
            }
        }
    }

    // 更新状态
    cm.currentCAPState = CAPState{
        Strategy: cm.config.Strategy,
        Mode:      mode,
        Partition: partition,
        Degraded:  degraded,
    }

    // 根据状态调整系统行为
    cm.adjustSystemBehavior(ctx)
}

// 调整系统行为
func (cm *CAPManager) adjustSystemBehavior(ctx context.Context) {
    switch cm.currentCAPState.Mode {
    case CAPModeNormal:
        // 正常模式，所有功能正常
        cm.consistencyManager.SetLevel(cm.config.Consistency.Level)
        cm.availabilityManager.EnableFullAvailability()
        cm.partitionManager.EnableFullSync()

    case CAPModeDegraded:
        // 降级模式，根据策略调整
        switch cm.config.Strategy {
        case StrategyCP:
            // 优先保证一致性，可能牺牲可用性
            cm.consistencyManager.SetLevel(ConsistencyStrong)
            cm.availabilityManager.EnableLimitedAvailability()
        case StrategyAP:
            // 优先保证可用性，可能牺牲一致性
            cm.consistencyManager.SetLevel(ConsistencyEventual)
            cm.availabilityManager.EnableFullAvailability()
        case StrategyCA:
            // 保证一致性和可用性，不处理分区
            cm.consistencyManager.SetLevel(ConsistencyStrong)
            cm.availabilityManager.EnableFullAvailability()
        }

    case CAPModeRecovery:
        // 恢复模式
        cm.consistencyManager.SetLevel(ConsistencyEventual)
        cm.availabilityManager.EnableLimitedAvailability()
        cm.partitionManager.EnableRecoverySync()
    }
}

// 获取当前CAP状态
func (cm *CAPManager) GetCAPState() CAPState {
    return cm.currentCAPState
}

// 处理分区事件
func (cm *CAPManager) HandlePartitionEvent(ctx context.Context, event PartitionEvent) {
    switch event.Type {
    case PartitionDetected:
        cm.partitionManager.OnPartitionDetected(ctx, event)
    case PartitionResolved:
        cm.partitionManager.OnPartitionResolved(ctx, event)
    }
}

// 处理降级事件
func (cm *CAPManager) HandleDegradationEvent(ctx context.Context, event DegradationEvent) {
    switch event.Type {
    case DegradationStarted:
        cm.availabilityManager.OnDegradationStarted(ctx, event)
    case DegradationEnded:
        cm.availabilityManager.OnDegradationEnded(ctx, event)
    }
}

// 分区事件
type PartitionEvent struct {
    Type      PartitionEventType
    Nodes     []string
    Timestamp time.Time
}

// 分区事件类型
type PartitionEventType string

const (
    PartitionDetected PartitionEventType = "detected"
    PartitionResolved PartitionEventType = "resolved"
)

// 降级事件
type DegradationEvent struct {
    Type        DegradationEventType
    Reason      string
    AffectedServices []string
    Timestamp   time.Time
}

// 降级事件类型
type DegradationEventType string

const (
    DegradationStarted DegradationEventType = "started"
    DegradationEnded   DegradationEventType = "ended"
)
```

## 分布式锁

### 分布式锁实现

```go
// internal/pkg/distributed/lock.go
package distributed

import (
    "context"
    "time"
)

// 分布式锁接口
type DistributedLock interface {
    Acquire(ctx context.Context, key string, ttl time.Duration) (bool, error)
    Release(ctx context.Context, key string) error
    Renew(ctx context.Context, key string, ttl time.Duration) (bool, error)
    IsLocked(ctx context.Context, key string) (bool, error)
}

// Redis分布式锁
type RedisDistributedLock struct {
    client *redis.Client
    prefix string
}

// 创建Redis分布式锁
func NewRedisDistributedLock(client *redis.Client, prefix string) *RedisDistributedLock {
    return &RedisDistributedLock{
        client: client,
        prefix: prefix,
    }
}

// 获取锁
func (rdl *RedisDistributedLock) Acquire(ctx context.Context, key string, ttl time.Duration) (bool, error) {
    fullKey := rdl.prefix + key

    // 使用SETNX命令获取锁
    result, err := rdl.client.SetNX(ctx, fullKey, "locked", ttl).Result()
    if err != nil {
        return false, fmt.Errorf("failed to acquire lock: %w", err)
    }

    return result, nil
}

// 释放锁
func (rdl *RedisDistributedLock) Release(ctx context.Context, key string) error {
    fullKey := rdl.prefix + key

    // 使用Lua脚本确保只有锁的持有者才能释放锁
    script := `
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("DEL", KEYS[1])
        else
            return 0
        end
    `

    _, err := rdl.client.Eval(ctx, script, []string{fullKey}, "locked").Result()
    if err != nil {
        return fmt.Errorf("failed to release lock: %w", err)
    }

    return nil
}

// 续约锁
func (rdl *RedisDistributedLock) Renew(ctx context.Context, key string, ttl time.Duration) (bool, error) {
    fullKey := rdl.prefix + key

    // 检查锁是否存在并属于当前客户端
    script := `
        if redis.call("GET", KEYS[1]) == ARGV[1] then
            return redis.call("EXPIRE", KEYS[1], ARGV[2])
        else
            return 0
        end
    `

    result, err := rdl.client.Eval(ctx, script, []string{fullKey}, "locked", int(ttl.Seconds())).Result()
    if err != nil {
        return false, fmt.Errorf("failed to renew lock: %w", err)
    }

    return result.(int64) == 1, nil
}

// 检查锁状态
func (rdl *RedisDistributedLock) IsLocked(ctx context.Context, key string) (bool, error) {
    fullKey := rdl.prefix + key

    result, err := rdl.client.Exists(ctx, fullKey).Result()
    if err != nil {
        return false, fmt.Errorf("failed to check lock status: %w", err)
    }

    return result > 0, nil
}

// ZooKeeper分布式锁
type ZooKeeperDistributedLock struct {
    client *zk.Conn
    prefix string
}

// 创建ZooKeeper分布式锁
func NewZooKeeperDistributedLock(client *zk.Conn, prefix string) *ZooKeeperDistributedLock {
    return &ZooKeeperDistributedLock{
        client: client,
        prefix: prefix,
    }
}

// 获取锁
func (zdl *ZooKeeperDistributedLock) Acquire(ctx context.Context, key string, ttl time.Duration) (bool, error) {
    path := zdl.prefix + "/" + key

    // 创建临时节点
    flags := int32(zk.FlagEphemeral)
    acl := zk.WorldACL(zk.PermAll)

    createdPath, err := zdl.client.Create(path, []byte("locked"), flags, acl)
    if err != nil {
        if err == zk.ErrNodeExists {
            return false, nil
        }
        return false, fmt.Errorf("failed to create lock node: %w", err)
    }

    // 监听锁节点
    _, _, events, err := zdl.client.GetW(path)
    if err != nil {
        return false, fmt.Errorf("failed to watch lock node: %w", err)
    }

    // 等待锁释放或上下文取消
    select {
    case event := <-events:
        if event.Type == zk.EventNodeDeleted {
            return true, nil
        }
    case <-ctx.Done():
        return false, ctx.Err()
    }

    return false, nil
}

// 释放锁
func (zdl *ZooKeeperDistributedLock) Release(ctx context.Context, key string) error {
    path := zdl.prefix + "/" + key

    if err := zdl.client.Delete(path, -1); err != nil {
        return fmt.Errorf("failed to release lock: %w", err)
    }

    return nil
}

// 续约锁
func (zdl *ZooKeeperDistributedLock) Renew(ctx context.Context, key string, ttl time.Duration) (bool, error) {
    // ZooKeeper的临时节点会自动处理过期
    return true, nil
}

// 检查锁状态
func (zdl *ZooKeeperDistributedLock) IsLocked(ctx context.Context, key string) (bool, error) {
    path := zdl.prefix + "/" + key

    exists, _, err := zdl.client.Exists(path)
    if err != nil {
        return false, fmt.Errorf("failed to check lock status: %w", err)
    }

    return exists, nil
}

// 分布式锁管理器
type DistributedLockManager struct {
    locks map[string]DistributedLock
    mutex sync.RWMutex
}

// 创建分布式锁管理器
func NewDistributedLockManager() *DistributedLockManager {
    return &DistributedLockManager{
        locks: make(map[string]DistributedLock),
    }
}

// 注册锁实现
func (dlm *DistributedLockManager) RegisterLock(name string, lock DistributedLock) {
    dlm.mutex.Lock()
    defer dlm.mutex.Unlock()
    dlm.locks[name] = lock
}

// 获取锁
func (dlm *DistributedLockManager) GetLock(name string) (DistributedLock, bool) {
    dlm.mutex.RLock()
    defer dlm.mutex.RUnlock()
    lock, exists := dlm.locks[name]
    return lock, exists
}

// 锁包装器
type LockWrapper struct {
    lock     DistributedLock
    key      string
    acquired bool
    ttl      time.Duration
}

// 获取锁包装器
func (dlm *DistributedLockManager) AcquireLock(ctx context.Context, lockName, key string, ttl time.Duration) (*LockWrapper, error) {
    lock, exists := dlm.GetLock(lockName)
    if !exists {
        return nil, fmt.Errorf("lock %s not found", lockName)
    }

    acquired, err := lock.Acquire(ctx, key, ttl)
    if err != nil {
        return nil, err
    }

    return &LockWrapper{
        lock:     lock,
        key:      key,
        acquired: acquired,
        ttl:      ttl,
    }, nil
}

// 释放锁
func (lw *LockWrapper) Release(ctx context.Context) error {
    if !lw.acquired {
        return nil
    }

    err := lw.lock.Release(ctx, lw.key)
    if err == nil {
        lw.acquired = false
    }

    return err
}

// 自动续约的锁
func (lw *LockWrapper) WithAutoRenew(ctx context.Context, fn func() error) error {
    if !lw.acquired {
        return errors.New("lock not acquired")
    }

    // 启动续约协程
    renewCtx, cancel := context.WithCancel(ctx)
    defer cancel()

    go func() {
        ticker := time.NewTicker(lw.ttl / 2)
        defer ticker.Stop()

        for {
            select {
            case <-ticker.C:
                if renewed, err := lw.lock.Renew(renewCtx, lw.key, lw.ttl); !renewed || err != nil {
                    return
                }
            case <-renewCtx.Done():
                return
            }
        }
    }()

    // 执行函数
    err := fn()

    // 释放锁
    if releaseErr := lw.Release(ctx); releaseErr != nil {
        return fmt.Errorf("function error: %v, lock release error: %w", err, releaseErr)
    }

    return err
}
```

## 服务发现

### 服务发现实现

```go
// internal/pkg/distributed/discovery.go
package distributed

import (
    "context"
    "time"
)

// 服务发现接口
type ServiceDiscovery interface {
    Register(ctx context.Context, service *ServiceInfo) error
    Deregister(ctx context.Context, serviceID string) error
    Discover(ctx context.Context, serviceName string) ([]*ServiceInfo, error)
    Watch(ctx context.Context, serviceName string) (<-chan []*ServiceInfo, error)
    HealthCheck(ctx context.Context, serviceID string) error
}

// 服务信息
type ServiceInfo struct {
    ID       string            `json:"id"`
    Name     string            `json:"name"`
    Address  string            `json:"address"`
    Port     int               `json:"port"`
    Metadata map[string]string `json:"metadata"`
    Version  string            `json:"version"`
    Status   ServiceStatus     `json:"status"`
}

// 服务状态
type ServiceStatus string

const (
    ServiceStatusHealthy   ServiceStatus = "healthy"
    ServiceStatusUnhealthy ServiceStatus = "unhealthy"
    ServiceStatusUnknown   ServiceStatus = "unknown"
)

// Redis服务发现
type RedisServiceDiscovery struct {
    client *redis.Client
    prefix string
    ttl    time.Duration
}

// 创建Redis服务发现
func NewRedisServiceDiscovery(client *redis.Client, prefix string, ttl time.Duration) *RedisServiceDiscovery {
    return &RedisServiceDiscovery{
        client: client,
        prefix: prefix,
        ttl:    ttl,
    }
}

// 注册服务
func (rsd *RedisServiceDiscovery) Register(ctx context.Context, service *ServiceInfo) error {
    key := rsd.prefix + ":" + service.Name + ":" + service.ID

    // 序列化服务信息
    data, err := json.Marshal(service)
    if err != nil {
        return fmt.Errorf("failed to marshal service info: %w", err)
    }

    // 使用SET命令注册服务
    err = rsd.client.Set(ctx, key, data, rsd.ttl).Err()
    if err != nil {
        return fmt.Errorf("failed to register service: %w", err)
    }

    // 添加到服务列表
    listKey := rsd.prefix + ":" + service.Name
    err = rsd.client.SAdd(ctx, listKey, service.ID).Err()
    if err != nil {
        return fmt.Errorf("failed to add service to list: %w", err)
    }

    return nil
}

// 注销服务
func (rsd *RedisServiceDiscovery) Deregister(ctx context.Context, serviceID string) error {
    // 查找服务
    var keys []string
    pattern := rsd.prefix + ":*:" + serviceID
    iter := rsd.client.Scan(ctx, 0, pattern, 0).Iterator()
    for iter.Next(ctx) {
        keys = append(keys, iter.Val())
    }

    if err := iter.Err(); err != nil {
        return fmt.Errorf("failed to scan services: %w", err)
    }

    // 删除服务信息
    for _, key := range keys {
        if err := rsd.client.Del(ctx, key).Err(); err != nil {
            return fmt.Errorf("failed to delete service: %w", err)
        }
    }

    // 从服务列表中移除
    for _, key := range keys {
        parts := strings.Split(key, ":")
        if len(parts) >= 3 {
            listKey := rsd.prefix + ":" + parts[1]
            if err := rsd.client.SRem(ctx, listKey, serviceID).Err(); err != nil {
                return fmt.Errorf("failed to remove service from list: %w", err)
            }
        }
    }

    return nil
}

// 发现服务
func (rsd *RedisServiceDiscovery) Discover(ctx context.Context, serviceName string) ([]*ServiceInfo, error) {
    listKey := rsd.prefix + ":" + serviceName

    // 获取服务ID列表
    serviceIDs, err := rsd.client.SMembers(ctx, listKey).Result()
    if err != nil {
        return nil, fmt.Errorf("failed to get service IDs: %w", err)
    }

    var services []*ServiceInfo
    for _, serviceID := range serviceIDs {
        key := rsd.prefix + ":" + serviceName + ":" + serviceID

        // 获取服务信息
        data, err := rsd.client.Get(ctx, key).Result()
        if err != nil {
            if err == redis.Nil {
                continue
            }
            return nil, fmt.Errorf("failed to get service info: %w", err)
        }

        var service ServiceInfo
        if err := json.Unmarshal([]byte(data), &service); err != nil {
            return nil, fmt.Errorf("failed to unmarshal service info: %w", err)
        }

        services = append(services, &service)
    }

    return services, nil
}

// 监控服务变化
func (rsd *RedisServiceDiscovery) Watch(ctx context.Context, serviceName string) (<-chan []*ServiceInfo, error) {
    ch := make(chan []*ServiceInfo, 10)

    go func() {
        defer close(ch)

        ticker := time.NewTicker(5 * time.Second)
        defer ticker.Stop()

        var lastServices []*ServiceInfo

        for {
            select {
            case <-ticker.C:
                services, err := rsd.Discover(ctx, serviceName)
                if err != nil {
                    log.Printf("Failed to discover services: %v", err)
                    continue
                }

                if !equalServices(services, lastServices) {
                    ch <- services
                    lastServices = services
                }
            case <-ctx.Done():
                return
            }
        }
    }()

    return ch, nil
}

// 健康检查
func (rsd *RedisServiceDiscovery) HealthCheck(ctx context.Context, serviceID string) error {
    // 实现健康检查逻辑
    return nil
}

// 比较服务列表
func equalServices(a, b []*ServiceInfo) bool {
    if len(a) != len(b) {
        return false
    }

    aMap := make(map[string]*ServiceInfo)
    for _, service := range a {
        aMap[service.ID] = service
    }

    for _, service := range b {
        if aMap[service.ID] == nil {
            return false
        }
        delete(aMap, service.ID)
    }

    return len(aMap) == 0
}

// Consul服务发现
type ConsulServiceDiscovery struct {
    client *consul.Client
    prefix string
    ttl    time.Duration
}

// 创建Consul服务发现
func NewConsulServiceDiscovery(client *consul.Client, prefix string, ttl time.Duration) *ConsulServiceDiscovery {
    return &ConsulServiceDiscovery{
        client: client,
        prefix: prefix,
        ttl:    ttl,
    }
}

// 注册服务
func (csd *ConsulServiceDiscovery) Register(ctx context.Context, service *ServiceInfo) error {
    registration := &consul.AgentServiceRegistration{
        ID:      service.ID,
        Name:    service.Name,
        Address: service.Address,
        Port:    service.Port,
        Meta:    service.Metadata,
        Check: &consul.AgentServiceCheck{
            TTL:                            csd.ttl.String(),
            DeregisterCriticalServiceAfter: "30s",
        },
    }

    return csd.client.Agent().ServiceRegister(registration)
}

// 注销服务
func (csd *ConsulServiceDiscovery) Deregister(ctx context.Context, serviceID string) error {
    return csd.client.Agent().ServiceDeregister(serviceID)
}

// 发现服务
func (csd *ConsulServiceDiscovery) Discover(ctx context.Context, serviceName string) ([]*ServiceInfo, error) {
    services, _, err := csd.client.Health().Service(serviceName, "", true, nil)
    if err != nil {
        return nil, fmt.Errorf("failed to discover services: %w", err)
    }

    var result []*ServiceInfo
    for _, service := range services {
        result = append(result, &ServiceInfo{
            ID:       service.Service.ID,
            Name:     service.Service.Service,
            Address:  service.Service.Address,
            Port:     service.Service.Port,
            Metadata: service.Service.Meta,
            Status:   csd.convertStatus(service.Checks),
        })
    }

    return result, nil
}

// 监控服务变化
func (csd *ConsulServiceDiscovery) Watch(ctx context.Context, serviceName string) (<-chan []*ServiceInfo, error) {
    ch := make(chan []*ServiceInfo, 10)

    go func() {
        defer close(ch)

        options := &consul.QueryOptions{
            WaitIndex: 0,
        }

        for {
            select {
            case <-ctx.Done():
                return
            default:
                services, meta, err := csd.client.Health().Service(serviceName, "", true, options)
                if err != nil {
                    log.Printf("Failed to watch services: %v", err)
                    time.Sleep(5 * time.Second)
                    continue
                }

                var result []*ServiceInfo
                for _, service := range services {
                    result = append(result, &ServiceInfo{
                        ID:       service.Service.ID,
                        Name:     service.Service.Service,
                        Address:  service.Service.Address,
                        Port:     service.Service.Port,
                        Metadata: service.Service.Meta,
                        Status:   csd.convertStatus(service.Checks),
                    })
                }

                ch <- result
                options.WaitIndex = meta.LastIndex
            }
        }
    }()

    return ch, nil
}

// 健康检查
func (csd *ConsulServiceDiscovery) HealthCheck(ctx context.Context, serviceID string) error {
    return csd.client.Agent().UpdateTTL("service:"+serviceID, "healthy", "pass")
}

// 转换状态
func (csd *ConsulServiceDiscovery) convertStatus(checks []*consul.HealthCheck) ServiceStatus {
    for _, check := range checks {
        if check.Status == "critical" {
            return ServiceStatusUnhealthy
        }
    }
    return ServiceStatusHealthy
}

// 服务发现管理器
type ServiceDiscoveryManager struct {
    discoverers map[string]ServiceDiscovery
    mutex       sync.RWMutex
}

// 创建服务发现管理器
func NewServiceDiscoveryManager() *ServiceDiscoveryManager {
    return &ServiceDiscoveryManager{
        discoverers: make(map[string]ServiceDiscovery),
    }
}

// 注册服务发现实现
func (sdm *ServiceDiscoveryManager) RegisterDiscovery(name string, discovery ServiceDiscovery) {
    sdm.mutex.Lock()
    defer sdm.mutex.Unlock()
    sdm.discoverers[name] = discovery
}

// 获取服务发现实现
func (sdm *ServiceDiscoveryManager) GetDiscovery(name string) (ServiceDiscovery, bool) {
    sdm.mutex.RLock()
    defer sdm.mutex.RUnlock()
    discovery, exists := sdm.discoverers[name]
    return discovery, exists
}

// 自动注册服务
type AutoRegisterService struct {
    discovery ServiceDiscovery
    service   *ServiceInfo
    ctx       context.Context
    cancel    context.CancelFunc
    wg        sync.WaitGroup
}

// 创建自动注册服务
func NewAutoRegisterService(discovery ServiceDiscovery, service *ServiceInfo) *AutoRegisterService {
    return &AutoRegisterService{
        discovery: discovery,
        service:   service,
    }
}

// 启动自动注册
func (ars *AutoRegisterService) Start(ctx context.Context) error {
    ars.ctx, ars.cancel = context.WithCancel(ctx)

    // 注册服务
    if err := ars.discovery.Register(ars.ctx, ars.service); err != nil {
        return fmt.Errorf("failed to register service: %w", err)
    }

    // 启动定期续约
    ars.wg.Add(1)
    go ars.renewLoop()

    return nil
}

// 停止自动注册
func (ars *AutoRegisterService) Stop() {
    if ars.cancel != nil {
        ars.cancel()
    }
    ars.wg.Wait()

    // 注销服务
    if ars.discovery != nil {
        ars.discovery.Deregister(context.Background(), ars.service.ID)
    }
}

// 续约循环
func (ars *AutoRegisterService) renewLoop() {
    defer ars.wg.Done()

    ticker := time.NewTicker(10 * time.Second)
    defer ticker.Stop()

    for {
        select {
        case <-ticker.C:
            if err := ars.discovery.Register(ars.ctx, ars.service); err != nil {
                log.Printf("Failed to renew service registration: %v", err)
            }
        case <-ars.ctx.Done():
            return
        }
    }
}
```

## 最佳实践总结

### 分布式系统设计最佳实践

1. **理解CAP权衡**：根据业务需求选择合适的CAP策略
2. **设计容错机制**：系统能够在节点故障时继续工作
3. **实现最终一致性**：在分布式环境中接受最终一致性
4. **使用分布式锁**：避免并发冲突和竞态条件
5. **实现服务发现**：动态管理服务实例的注册和发现

### 性能优化最佳实践

1. **减少网络调用**：尽量减少跨网络边界的调用
2. **使用缓存**：在适当的层级使用缓存减少数据库访问
3. **批量处理**：对多个操作进行批量处理
4. **异步处理**：使用消息队列进行异步处理
5. **负载均衡**：合理分配负载到各个节点

### 监控和可观测性最佳实践

1. **全面监控**：监控系统的各个层面
2. **分布式追踪**：实现端到端的请求追踪
3. **集中日志**：集中收集和分析日志
4. **告警机制**：设置合理的告警阈值
5. **性能分析**：定期进行性能分析和优化

### 安全最佳实践

1. **认证和授权**：实现严格的安全控制
2. **数据加密**：在传输和存储过程中加密数据
3. **网络安全**：保护网络通信安全
4. **访问控制**：实现细粒度的访问控制
5. **安全审计**：记录安全相关的操作和事件

通过遵循这些最佳实践，可以构建可靠、可扩展、高性能的分布式系统。关键是要根据具体的业务需求和场景，选择合适的技术和策略。