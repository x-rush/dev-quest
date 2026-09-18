# Go Mock和桩测试详解

> **文档简介**: 全面介绍Go语言中的Mock和桩测试技术，涵盖gomock、testify/mock等主流框架的使用方法和最佳实践

> **目标读者**: Go开发者，需要编写高质量单元测试和集成测试的开发者

> **前置知识**: Go语言基础、单元测试基础、接口设计基础

> **预计时长**: 4-6小时完整学习

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `testing/quality-assurance` |
| **难度** | ⭐⭐⭐ (3/5) |
| **标签** | `#testing` `#mock` `#stub` `#test-doubles` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 学习目标

### 核心技能
- **Mock概念**: 理解Mock、Stub、Fake、Spy的区别和使用场景
- **gomock框架**: 掌握 gomock 风格的 mock 生成与期望验证
- **testify/mock**: 熟练使用testify框架的mock功能
- **接口设计**: 学会设计可测试的接口和依赖注入

### 实践能力
- **接口Mock**: 能够为任意接口生成Mock实现
- **行为验证**: 验证Mock对象的调用次数、参数、返回值
- **测试隔离**: 通过Mock实现测试间的完全隔离
- **测试驱动**: 运用Mock技术进行测试驱动开发

## 📖 Mock测试基础概念

### Test Doubles分类

#### 1. Mock对象
**定义**: 预编程对象，带有关于预期调用的验证
```go
// Mock对象示例
type MockDatabase struct {
    mock.Mock
}

func (m *MockDatabase) GetUser(id int) (*User, error) {
    args := m.Called(id)
    if args.Get(0) == nil { return nil, args.Error(1) }
    return args.Get(0).(*User), args.Error(1)
}
```

#### 2. Stub对象
**定义**: 预编程对象，提供固定返回值，无验证功能
```go
// Stub对象示例
type StubPaymentGateway struct {
    shouldSucceed bool
}

func (s *StubPaymentGateway) ProcessPayment(amount float64) error {
    if s.shouldSucceed {
        return nil
    }
    return errors.New("payment failed")
}
```

#### 3. Fake对象
**定义**: 简化实现，具有真实业务逻辑，适合测试
```go
// Fake对象示例
type FakeUserRepository struct {
    users map[int]*User
}

func (f *FakeUserRepository) GetUser(id int) (*User, error) {
    if user, exists := f.users[id]; exists {
        return user, nil
    }
    return nil, errors.New("user not found")
}
```

## 🛠️ gomock框架详解

### 安装和设置

#### 1. 安装gomock工具
```bash
# 安装gomock工具和mockgen
# （golang 组织下的原 mock 仓库已归档，社区维护的后续项目为 go.uber.org/mock；迁移时核对导入路径与版本说明）
go install go.uber.org/mock/mockgen@latest

# 验证安装
mockgen -version
```

#### 2. 生成Mock代码
```bash
# 为接口生成Mock代码
mockgen -source=user_service.go -destination=mocks/mock_user_service.go -package=mocks

# 或使用反射模式
mockgen -package=mocks github.com/yourproject/interfaces UserRepository
```

### 完整的gomock示例

#### 1. 定义接口
```go
// interfaces/user_service.go
package interfaces

import "context"

type UserService interface {
    GetUser(ctx context.Context, id int) (*User, error)
    CreateUser(ctx context.Context, user *User) error
    UpdateUser(ctx context.Context, user *User) error
    DeleteUser(ctx context.Context, id int) error
}

type User struct {
    ID    int    `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}
```

#### 2. 生成Mock代码
```bash
mockgen -source=interfaces/user_service.go -destination=mocks/mock_user_service.go -package=mocks
```

#### 3. 使用Mock进行测试
```go
// user_service_test.go
package services_test

import (
    "context"
    "testing"

    "go.uber.org/mock/gomock"
    "github.com/stretchr/testify/assert"

    "yourproject/interfaces"
    "yourproject/mocks"
    "yourproject/services"
)

func TestUserService_GetUser(t *testing.T) {
    // 创建gomock控制器
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    // 创建Mock对象
    mockUserService := mocks.NewMockUserService(ctrl)

    // 设置期望
    expectedUser := &interfaces.User{
        ID:    1,
        Name:  "John Doe",
        Email: "john@example.com",
    }

    mockUserService.
        EXPECT().
        GetUser(gomock.Any(), gomock.Eq(1)).
        Return(expectedUser, nil).
        Times(1)

    // 执行测试
    user, err := mockUserService.GetUser(context.Background(), 1)

    // 验证结果
    assert.NoError(t, err)
    assert.Equal(t, expectedUser, user)
}
```

### gomock高级用法

#### 1. 参数匹配器
```go
func TestUserService_AdvancedMatching(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockUserService := mocks.NewMockUserService(ctrl)

    // 使用不同的匹配器
    mockUserService.
        EXPECT().
        GetUser(gomock.Any(), gomock.Any()). // 任意参数
        Return(nil, errors.New("not found")).
        AnyTimes() // 任意次数

    mockUserService.
        EXPECT().
        CreateUser(gomock.Any(), gomock.Not(gomock.Nil())). // 非nil参数
        Return(nil).
        Times(1)

    mockUserService.
        EXPECT().
        UpdateUser(gomock.Any(), gomock.Any()).
        Do(func(ctx context.Context, user *interfaces.User) {
            // 自定义验证逻辑
            assert.NotEmpty(t, user.Name)
            assert.Contains(t, user.Email, "@")
        }).
        Return(nil)

    // 测试逻辑...
}
```

#### 2. 自定义匹配器
```go
// 自定义匹配器
type UserMatcher struct {
    expected *interfaces.User
}

func NewUserMatcher(user *interfaces.User) gomock.Matcher {
    return &UserMatcher{expected: user}
}

func (m *UserMatcher) Matches(x interface{}) bool {
    user, ok := x.(*interfaces.User)
    if !ok {
        return false
    }

    return user.ID == m.expected.ID &&
           user.Name == m.expected.Name
}

func (m *UserMatcher) String() string {
    return fmt.Sprintf("matches user with ID=%d, Name=%s",
        m.expected.ID, m.expected.Name)
}

// 使用自定义匹配器
func TestUserService_CustomMatcher(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockUserService := mocks.NewMockUserService(ctrl)

    expectedUser := &interfaces.User{ID: 1, Name: "John"}

    mockUserService.
        EXPECT().
        UpdateUser(gomock.Any(), NewUserMatcher(expectedUser)).
        Return(nil)

    // 测试逻辑...
}
```

## 🔧 testify/mock框架详解

### 基本使用方法

#### 1. 安装testify
```bash
go get github.com/stretchr/testify
```

#### 2. 简单Mock示例
```go
package services_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/mock"

    "yourproject/interfaces"
)

// 自定义Mock对象
type MockUserService struct {
    mock.Mock
}

func (m *MockUserService) GetUser(ctx context.Context, id int) (*interfaces.User, error) {
    args := m.Called(ctx, id)
    if args.Get(0) == nil {
        return nil, args.Error(1)
    }
    return args.Get(0).(*interfaces.User), args.Error(1)
}

func (m *MockUserService) CreateUser(ctx context.Context, user *interfaces.User) error {
    args := m.Called(ctx, user)
    return args.Error(0)
}

func TestUserService_TestifyMock(t *testing.T) {
    // 创建Mock对象
    mockUserService := new(MockUserService)

    // 设置期望
    expectedUser := &interfaces.User{
        ID:    1,
        Name:  "Jane Doe",
        Email: "jane@example.com",
    }

    mockUserService.
        On("GetUser", mock.Anything, 1).
        Return(expectedUser, nil).
        Once()

    mockUserService.
        On("CreateUser", mock.Anything, mock.AnythingOfType("*interfaces.User")).
        Return(nil).
        Once()

    // 执行测试
    user, err := mockUserService.GetUser(context.Background(), 1)

    // 验证结果
    assert.NoError(t, err)
    assert.Equal(t, expectedUser, user)

    // 验证期望是否满足
    assert.True(t, mockUserService.AssertExpectations(t))
}
```

### testify/mock高级功能

#### 1. 参数约束和验证
```go
func TestAdvancedMockConstraints(t *testing.T) {
    mockUserService := new(MockUserService)

    // 使用不同的参数约束
    mockUserService.
        On("GetUser", mock.Anything, mock.GreaterThan(0)).
        Return(&interfaces.User{ID: 1}, nil)

    mockUserService.
        On("GetUser", mock.Anything, mock.LessOrEqual(0)).
        Return(nil, errors.New("invalid id"))

    mockUserService.
        On("CreateUser", mock.Anything, mock.MatchedBy(func(user *interfaces.User) bool {
            return len(user.Name) > 0 && strings.Contains(user.Email, "@")
        })).
        Return(nil)

    // 测试逻辑...
}
```

#### 2. 链式调用和序列返回
```go
func TestSequentialReturns(t *testing.T) {
    mockUserService := new(MockUserService)

    // 设置序列返回值
    mockUserService.
        On("GetUser", mock.Anything, 1).
        Return(&interfaces.User{Name: "First"}, nil).
        Once().
        On("GetUser", mock.Anything, 1).
        Return(&interfaces.User{Name: "Second"}, nil).
        Once().
        On("GetUser", mock.Anything, 1).
        Return(nil, errors.New("not found"))

    // 测试多次调用
    user1, err1 := mockUserService.GetUser(context.Background(), 1)
    assert.NoError(t, err1)
    assert.Equal(t, "First", user1.Name)

    user2, err2 := mockUserService.GetUser(context.Background(), 1)
    assert.NoError(t, err2)
    assert.Equal(t, "Second", user2.Name)

    user3, err3 := mockUserService.GetUser(context.Background(), 1)
    assert.Error(t, err3)
    assert.Nil(t, user3)
}
```

## 🏗️ 依赖注入与Mock测试

### 接口设计最佳实践

#### 1. 定义清晰的接口边界
```go
// repositories/user_repository.go
package repositories

import "context"

type UserRepository interface {
    // CRUD操作
    Create(ctx context.Context, user *User) error
    GetByID(ctx context.Context, id int) (*User, error)
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id int) error

    // 查询操作
    FindByEmail(ctx context.Context, email string) (*User, error)
    Search(ctx context.Context, query SearchQuery) ([]*User, error)
}

type User struct {
    ID        int       `json:"id"`
    Name      string    `json:"name"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
    UpdatedAt time.Time `json:"updated_at"`
}

type SearchQuery struct {
    Name  string
    Email string
    Limit int
    Offset int
}
```

#### 2. 使用依赖注入的服务层
```go
// services/user_service.go
package services

import "context"

type UserService struct {
    userRepo UserRepository
    emailService EmailService
    logger Logger
}

func NewUserService(repo UserRepository, email EmailService, logger Logger) *UserService {
    return &UserService{
        userRepo: repo,
        emailService: email,
        logger: logger,
    }
}

func (s *UserService) CreateUser(ctx context.Context, req *CreateUserRequest) (*User, error) {
    // 参数验证
    if err := req.Validate(); err != nil {
        s.logger.Error("Invalid request", "error", err)
        return nil, err
    }

    // 检查邮箱是否已存在
    existingUser, err := s.userRepo.FindByEmail(ctx, req.Email)
    if err != nil {
        s.logger.Error("Failed to check existing user", "error", err)
        return nil, err
    }
    if existingUser != nil {
        return nil, errors.New("email already exists")
    }

    // 创建用户
    user := &User{
        Name:  req.Name,
        Email: req.Email,
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
    }

    if err := s.userRepo.Create(ctx, user); err != nil {
        s.logger.Error("Failed to create user", "error", err)
        return nil, err
    }

    // 发送欢迎邮件
    if err := s.emailService.SendWelcomeEmail(ctx, user.Email, user.Name); err != nil {
        s.logger.Warn("Failed to send welcome email", "error", err, "user_id", user.ID)
        // 不让邮件错误影响用户创建
    }

    s.logger.Info("User created successfully", "user_id", user.ID)
    return user, nil
}

type CreateUserRequest struct {
    Name  string `json:"name" validate:"required,min=2"`
    Email string `json:"email" validate:"required,email"`
}

func (r *CreateUserRequest) Validate() error {
    if r.Name == "" || len(r.Name) < 2 {
        return errors.New("name must be at least 2 characters")
    }
    if r.Email == "" || !strings.Contains(r.Email, "@") {
        return errors.New("invalid email format")
    }
    return nil
}
```

### 完整的测试示例
```go
// services/user_service_test.go
package services_test

import (
    "context"
    "errors"
    "testing"
    "time"

    "go.uber.org/mock/gomock"
    "github.com/stretchr/testify/assert"
    "github.com/stretchr/testify/require"

    "yourproject/services"
    "yourproject/mocks"
)

func TestUserService_CreateUser_Success(t *testing.T) {
    // 设置
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := mocks.NewMockUserRepository(ctrl)
    mockEmail := mocks.NewMockEmailService(ctrl)
    mockLogger := mocks.NewMockLogger(ctrl)

    userService := services.NewUserService(mockRepo, mockEmail, mockLogger)

    // 准备测试数据
    req := &services.CreateUserRequest{
        Name:  "John Doe",
        Email: "john@example.com",
    }

    // 设置Mock期望
    mockRepo.
        EXPECT().
        FindByEmail(gomock.Any(), req.Email).
        Return(nil, nil) // 用户不存在

    mockRepo.
        EXPECT().
        Create(gomock.Any(), gomock.Any()).
        Do(func(ctx context.Context, user *services.User) {
            assert.Equal(t, req.Name, user.Name)
            assert.Equal(t, req.Email, user.Email)
            assert.NotZero(t, user.CreatedAt)
            assert.NotZero(t, user.UpdatedAt)
        }).
        Return(nil)

    mockEmail.
        EXPECT().
        SendWelcomeEmail(gomock.Any(), req.Email, req.Name).
        Return(nil)

    mockLogger.
        EXPECT().
        Info("User created successfully", "user_id", gomock.Any()).
        AnyTimes()

    // 执行
    user, err := userService.CreateUser(context.Background(), req)

    // 验证
    require.NoError(t, err)
    require.NotNil(t, user)
    assert.Equal(t, req.Name, user.Name)
    assert.Equal(t, req.Email, user.Email)
    assert.NotZero(t, user.CreatedAt)
}

func TestUserService_CreateUser_EmailAlreadyExists(t *testing.T) {
    // 设置
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := mocks.NewMockUserRepository(ctrl)
    mockEmail := mocks.NewMockEmailService(ctrl)
    mockLogger := mocks.NewMockLogger(ctrl)

    userService := services.NewUserService(mockRepo, mockEmail, mockLogger)

    req := &services.CreateUserRequest{
        Name:  "John Doe",
        Email: "john@example.com",
    }

    existingUser := &services.User{
        ID:    1,
        Name:  "Existing User",
        Email: "john@example.com",
    }

    // 设置Mock期望 - 邮箱已存在
    mockRepo.
        EXPECT().
        FindByEmail(gomock.Any(), req.Email).
        Return(existingUser, nil)

    mockLogger.
        EXPECT().
        Error("Invalid request", gomock.Any()).
        AnyTimes()

    // 执行
    user, err := userService.CreateUser(context.Background(), req)

    // 验证
    assert.Error(t, err)
    assert.Nil(t, user)
    assert.Contains(t, err.Error(), "email already exists")
}
```

## 🎨 Mock测试最佳实践

### 1. 测试结构设计
```go
// 使用测试套件结构
type UserServiceTestSuite struct {
    suite.Suite
    ctrl       *gomock.Controller
    mockRepo   *mocks.MockUserRepository
    mockEmail  *mocks.MockEmailService
    mockLogger *mocks.MockLogger
    service    *services.UserService
}

func (suite *UserServiceTestSuite) SetupTest() {
    suite.ctrl = gomock.NewController(suite.T())
    suite.mockRepo = mocks.NewMockUserRepository(suite.ctrl)
    suite.mockEmail = mocks.NewMockEmailService(suite.ctrl)
    suite.mockLogger = mocks.NewMockLogger(suite.ctrl)
    suite.service = services.NewUserService(
        suite.mockRepo,
        suite.mockEmail,
        suite.mockLogger,
    )
}

func (suite *UserServiceTestSuite) TearDownTest() {
    suite.ctrl.Finish()
}

func (suite *UserServiceTestSuite) TestCreateUser_Success() {
    // 测试逻辑
}

func TestUserServiceSuite(t *testing.T) {
    suite.Run(t, new(UserServiceTestSuite))
}
```

### 2. 测试数据工厂
```go
// factories/user_factory.go
package factories

import "yourproject/services"

func NewUser() *services.User {
    return &services.User{
        ID:        1,
        Name:      "Test User",
        Email:     "test@example.com",
        CreatedAt: time.Now(),
        UpdatedAt: time.Now(),
    }
}

func NewCreateUserRequest() *services.CreateUserRequest {
    return &services.CreateUserRequest{
        Name:  "Test User",
        Email: "test@example.com",
    }
}

func NewUserWithEmail(email string) *services.User {
    user := NewUser()
    user.Email = email
    return user
}
```

### 3. 测试辅助函数
```go
// helpers/test_helpers.go
package helpers

import (
    "context"
    "testing"
    "go.uber.org/mock/gomock"
    "github.com/stretchr/testify/require"
)

func SetupUserServiceMocks(t *testing.T) (*gomock.Controller, *mocks.MockUserRepository, *mocks.MockEmailService, *mocks.MockLogger, *services.UserService) {
    ctrl := gomock.NewController(t)
    mockRepo := mocks.NewMockUserRepository(ctrl)
    mockEmail := mocks.NewMockEmailService(ctrl)
    mockLogger := mocks.NewMockLogger(ctrl)

    // 设置默认的logger期望
    mockLogger.
        EXPECT().
        Info(gomock.Any(), gomock.Any()).
        AnyTimes()
    mockLogger.
        EXPECT().
        Error(gomock.Any(), gomock.Any()).
        AnyTimes()
    mockLogger.
        EXPECT().
        Warn(gomock.Any(), gomock.Any()).
        AnyTimes()

    service := services.NewUserService(mockRepo, mockEmail, mockLogger)

    return ctrl, mockRepo, mockEmail, mockLogger, service
}

func AssertUserCreated(t *testing.T, expected, actual *services.User) {
    require.NotNil(t, actual)
    assert.Equal(t, expected.Name, actual.Name)
    assert.Equal(t, expected.Email, actual.Email)
    assert.NotZero(t, actual.CreatedAt)
    assert.NotZero(t, actual.UpdatedAt)
}
```

## 🔍 常见问题和解决方案

### 1. Mock对象未调用
```go
// 问题：Mock期望未被满足
func TestMockNotCalled(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := mocks.NewMockUserRepository(ctrl)

    // 设置期望但未调用
    mockRepo.EXPECT().GetUser(gomock.Any(), 1).Return(nil, nil)

    // 测试结束时会出现：FAIL: Expected call, but received none
}
```

**解决方案**：
```go
// 使用Optional()或Times(0)
mockRepo.EXPECT().GetUser(gomock.Any(), 1).Return(nil, nil).Maybe() // 可选调用
// 或
mockRepo.EXPECT().GetUser(gomock.Any(), 1).Return(nil, nil).Times(0) // 0次调用
```

### 2. 参数不匹配
```go
// 问题：参数不匹配导致测试失败
func TestParameterMismatch(t *testing.T) {
    ctrl := gomock.NewController(t)
    defer ctrl.Finish()

    mockRepo := mocks.NewMockUserRepository(ctrl)

    // 期望特定参数
    mockRepo.EXPECT().GetUser(context.Background(), 1).Return(nil, nil)

    // 但调用时参数不同
    ctx := context.WithValue(context.Background(), "key", "value") // 不同的context
    mockRepo.GetUser(ctx, 1) // 参数不匹配
}
```

**解决方案**：
```go
// 使用更宽松的匹配器
mockRepo.EXPECT().GetUser(gomock.Any(), 1).Return(nil, nil)
// 或使用自定义匹配器
mockRepo.EXPECT().GetUser(gomock.Any(), gomock.Eq(1)).Return(nil, nil)
```

### 3. 接口方法签名错误
```go
// 问题：接口方法签名与Mock不匹配
type UserRepository interface {
    GetUser(id int) (*User, error) // 缺少context参数
}

// 但实现时使用了context
func (r *UserRepo) GetUser(ctx context.Context, id int) (*User, error) {
    // 实现包含context参数
}
```

**解决方案**：
```go
// 确保接口和实现签名一致
type UserRepository interface {
    GetUser(ctx context.Context, id int) (*User, error)
    // 或者如果不需要context，移除实现中的context参数
}
```

## 🔄 文档交叉引用

### 相关文档
- 📄 **[单元测试]**: [testing/01-unit-testing.md](01-unit-testing.md) - Go单元测试基础
- 📄 **[集成测试]**: [testing/03-integration-testing.md](03-integration-testing.md) - 系统集成测试
- 📄 **[性能测试]**: [testing/04-benchmarking.md](04-benchmarking.md) - 基准测试和性能分析

### 参考章节
- 📖 **[Gin框架测试]**: [frameworks/01-gin-framework-basics.md](../frameworks/01-gin-framework-basics.md) - Web框架测试
- 📖 **[项目实战]**: [projects/01-rest-api-server.md](../projects/01-rest-api-server.md) - 完整项目的测试实践

## 📝 总结

### 核心要点回顾
1. **Mock概念**: 理解不同类型Test Doubles的使用场景
2. **gomock框架**: 掌握官方Mock工具的使用方法
3. **testify/mock**: 熟悉社区流行框架的功能特性
4. **依赖注入**: 学会设计可测试的代码架构

### 学习成果检查
- [ ] 是否理解Mock、Stub、Fake的区别？
- [ ] 是否能够使用gomock生成和使用Mock对象？
- [ ] 是否掌握testify/mock的高级功能？
- [ ] 是否能够设计可测试的代码架构？

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0

---

> 💡 **实践建议**:
> - 优先考虑使用接口而不是具体实现
> - 保持Mock测试的简单和可维护性
> - 不要过度Mock，只在需要隔离外部依赖时使用
> - 定期检查Mock测试的有效性，避免测试与实现脱节

<!-- full-library-explanation -->
## 替身模拟的是边界，不是另一个生产系统

前置是接口与单元测试。Stub 提供固定响应，适合制造超时、未找到等分支；Fake 有可工作的简化实现，例如内存仓储；Mock 验证约定交互，如发送通知是否只发生一次。不同工具并无高低之分，优先选择能说明测试意图的最简单替身。一个小接口往往只需几十行手写实现，不必为了使用 mock 框架扩大生产接口。

替身容易与真实系统行为漂移。内存 map 不能模拟数据库唯一约束、事务隔离和 SQL 方言；HTTP stub 不证明 TLS 与代理配置正确。因此业务规则用替身快速验证，适配器再用集成测试检验真实契约。生成 mock 时固定生成器版本，接口改动后检查生成文件同步，不能以“编译通过”代替语义正确。

练习：为支付服务写一个返回超时的 Stub，验证上层不会把超时显示成成功；再用 Spy 记录通知参数，要求支付未确认成功时不发“已付款”。若业务允许重试，明确幂等键是否沿用，而不是只断言调用次数恰好为一。测试失败应说明业务后果，不应只给出框架的复杂参数匹配错误。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../LEARNING_GUIDE.md) · [完整目录与版本](../README.md) · [通用术语](../../shared-resources/glossary.md)
