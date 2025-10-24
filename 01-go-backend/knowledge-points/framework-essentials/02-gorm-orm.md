# GORM ORM知识点详解

GORM是Go语言中最流行的ORM库，提供了简洁的API和强大的功能。本文档详细介绍GORM框架的所有重要知识点，从基础使用到高级特性。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `knowledge-points/framework-essentials` |
| **难度** | ⭐⭐ |
| **标签** | `#gorm` `#orm` `#数据库` `#框架` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 1. GORM基础

### 1.1 GORM简介
- **GORM特点**：开发者友好的ORM库
- **核心功能**：模型定义、CRUD操作、关联关系
- **数据库支持**：MySQL, PostgreSQL, SQLite, SQL Server
- **设计理念**：约定优于配置

### 1.2 安装和配置
- **安装GORM**：`go get -u gorm.io/gorm`
- **安装驱动**：`go get gorm.io/driver/postgres`
- **导入GORM**：`import "gorm.io/gorm"`
- **版本管理**：GORM版本兼容性

### 1.3 数据库连接
- **连接配置**：DSN字符串配置
- **连接池**：连接池配置和优化
- **连接测试**：连接健康检查
- **多数据库**：多数据库配置
- **连接管理**：连接生命周期管理

**示例**：
```go
package main

import (
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "log"
)

func main() {
    // 数据库连接
    dsn := "host=localhost user=gorm password=gorm dbname=gorm port=9920 sslmode=disable TimeZone=Asia/Shanghai"
    db, err := gorm.Open(postgres.Open(dsn), &gorm.Config{})
    if err != nil {
        log.Fatal("Failed to connect to database:", err)
    }

    // 获取底层sql.DB
    sqlDB, err := db.DB()
    if err != nil {
        log.Fatal("Failed to get sql.DB:", err)
    }

    // 配置连接池
    sqlDB.SetMaxIdleConns(10)
    sqlDB.SetMaxOpenConns(100)
    sqlDB.SetConnMaxLifetime(time.Hour)

    // 测试连接
    if err := sqlDB.Ping(); err != nil {
        log.Fatal("Database ping failed:", err)
    }

    log.Println("Database connected successfully")
}
```

## 2. 模型定义

### 2.1 模型基础
- **结构体定义**：GORM模型结构体
- **字段标签**：GORM标签和数据库标签
- **表名约定**：表名自动生成规则
- **字段名约定**：字段名转换规则
- **主键定义**：主键字段定义

### 2.2 字段类型
- **基本类型**：Go类型与数据库类型映射
- **时间类型**：时间字段处理
- **JSON类型**：JSON字段支持
- **枚举类型**：枚举字段定义
- **自定义类型**：自定义数据类型

### 2.3 模型标签
- **主键标签**：`gorm:"primaryKey"`
- **自增标签**：`gorm:"autoIncrement"`
- **索引标签**：`gorm:"index"`
- **唯一标签**：`gorm:"unique"`
- **非空标签**：`gorm:"not null"`

**示例**：
```go
package models

import (
    "time"
    "gorm.io/gorm"
)

type User struct {
    ID        uint           `gorm:"primaryKey"`
    Name      string         `gorm:"size:100;not null"`
    Email     string         `gorm:"size:100;unique;not null"`
    Age       int            `gorm:"default:18"`
    Active    bool           `gorm:"default:true"`
    CreatedAt time.Time      `gorm:"autoCreateTime"`
    UpdatedAt time.Time      `gorm:"autoUpdateTime"`
    DeletedAt gorm.DeletedAt `gorm:"index"`

    // 自定义字段
    Metadata  JSON           `gorm:"type:jsonb"`

    // 关联关系
    Profile   *Profile       `gorm:"foreignKey:UserID"`
    Orders    []Order        `gorm:"foreignKey:UserID"`
}

type Profile struct {
    ID        uint   `gorm:"primaryKey"`
    UserID    uint   `gorm:"not null"`
    Avatar    string `gorm:"size:255"`
    Bio       string `gorm:"type:text"`
    User      User   `gorm:"foreignKey:UserID"`
}

type Order struct {
    ID        uint      `gorm:"primaryKey"`
    UserID    uint      `gorm:"not null"`
    Product   string    `gorm:"size:100;not null"`
    Price     float64   `gorm:"type:decimal(10,2)"`
    Status    string    `gorm:"size:20;default:'pending'"`
    CreatedAt time.Time `gorm:"autoCreateTime"`
    User      User      `gorm:"foreignKey:UserID"`
}

// 自定义JSON类型
type JSON map[string]interface{}

func (j JSON) Value() (driver.Value, error) {
    return json.Marshal(j)
}

func (j *JSON) Scan(value interface{}) error {
    return json.Unmarshal(value.([]byte), &j)
}
```

## 3. 数据库迁移

### 3.1 自动迁移
- **AutoMigrate**：自动迁移表结构
- **Migrator接口**：迁移器接口使用
- **迁移选项**：迁移配置选项
- **迁移回滚**：迁移回滚支持
- **迁移错误**：迁移错误处理

### 3.2 手动迁移
- **创建表**：手动创建表
- **修改表**：修改表结构
- **删除表**：删除表操作
- **索引管理**：索引创建和删除
- **约束管理**：约束创建和管理

### 3.3 迁移策略
- **开发环境**：开发环境迁移策略
- **生产环境**：生产环境迁移策略
- **版本控制**：迁移版本控制
- **数据迁移**：数据迁移脚本
- **迁移测试**：迁移测试验证

**示例**：
```go
package main

import (
    "gorm.io/gorm"
    "gorm.io/gorm/clause"
)

// 自动迁移
func AutoMigrate(db *gorm.DB) error {
    return db.AutoMigrate(
        &User{},
        &Profile{},
        &Order{},
    )
}

// 手动迁移
func ManualMigrate(db *gorm.DB) error {
    // 创建表
    if err := db.Migrator().CreateTable(&User{}); err != nil {
        return err
    }

    // 添加字段
    if err := db.Migrator().AddColumn(&User{}, "NewField"); err != nil {
        return err
    }

    // 删除字段
    if err := db.Migrator().DropColumn(&User{}, "OldField"); err != nil {
        return err
    }

    // 创建索引
    if err := db.Migrator().CreateIndex(&User{}, "Email"); err != nil {
        return err
    }

    // 删除索引
    if err := db.Migrator().DropIndex(&User{}, "EmailIndex"); err != nil {
        return err
    }

    return nil
}

// 修改表结构
func ModifyTable(db *gorm.DB) error {
    // 重命名表
    if err := db.Migrator().RenameTable("users", "users_new"); err != nil {
        return err
    }

    // 重命名列
    if err := db.Migrator().RenameColumn(&User{}, "Name", "FullName"); err != nil {
        return err
    }

    // 添加外键约束
    if err := db.Migrator().CreateConstraint(&Profile{}, "User"); err != nil {
        return err
    }

    return nil
}

// 检查表是否存在
func TableExists(db *gorm.DB, tableName string) (bool, error) {
    return db.Migrator().HasTable(tableName)
}

// 检查列是否存在
func ColumnExists(db *gorm.DB, model interface{}, columnName string) (bool, error) {
    return db.Migrator().HasColumn(model, columnName)
}
```

## 4. CRUD操作

### 4.1 创建记录
- **Create方法**：创建单条记录
- **批量创建**：批量创建记录
- **创建选项**：创建配置选项
- **默认值**：默认值处理
- **钩子函数**：创建钩子函数

### 4.2 查询记录
- **First方法**：查询第一条记录
- **Find方法**：查询多条记录
- **Where条件**：条件查询
- **高级查询**：复杂查询条件
- **查询链**：查询链调用

### 4.3 更新记录
- **Save方法**：保存更新
- **Update方法**：字段更新
- **Updates方法**：批量更新
- **更新选项**：更新配置
- **钩子函数**：更新钩子函数

### 4.4 删除记录
- **Delete方法**：删除记录
- **批量删除**：批量删除
- **软删除**：软删除功能
- **永久删除**：永久删除
- **钩子函数**：删除钩子函数

**示例**：
```go
package services

import (
    "gorm.io/gorm"
    "errors"
)

type UserService struct {
    db *gorm.DB
}

func NewUserService(db *gorm.DB) *UserService {
    return &UserService{db: db}
}

// 创建用户
func (s *UserService) CreateUser(user *User) error {
    if err := s.db.Create(user).Error; err != nil {
        return err
    }
    return nil
}

// 批量创建用户
func (s *UserService) BatchCreateUsers(users []*User) error {
    if err := s.db.CreateInBatches(users, 100).Error; err != nil {
        return err
    }
    return nil
}

// 获取用户
func (s *UserService) GetUser(id uint) (*User, error) {
    var user User
    if err := s.db.First(&user, id).Error; err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, errors.New("user not found")
        }
        return nil, err
    }
    return &user, nil
}

// 根据邮箱获取用户
func (s *UserService) GetUserByEmail(email string) (*User, error) {
    var user User
    if err := s.db.Where("email = ?", email).First(&user).Error; err != nil {
        if errors.Is(err, gorm.ErrRecordNotFound) {
            return nil, errors.New("user not found")
        }
        return nil, err
    }
    return &user, nil
}

// 获取用户列表
func (s *UserService) GetUsers(page, limit int) ([]*User, int64, error) {
    var users []*User
    var total int64

    // 计算总数
    if err := s.db.Model(&User{}).Count(&total).Error; err != nil {
        return nil, 0, err
    }

    // 分页查询
    offset := (page - 1) * limit
    if err := s.db.Offset(offset).Limit(limit).Find(&users).Error; err != nil {
        return nil, 0, err
    }

    return users, total, nil
}

// 更新用户
func (s *UserService) UpdateUser(user *User) error {
    if err := s.db.Save(user).Error; err != nil {
        return err
    }
    return nil
}

// 更新用户字段
func (s *UserService) UpdateUserFields(id uint, updates map[string]interface{}) error {
    if err := s.db.Model(&User{}).Where("id = ?", id).Updates(updates).Error; err != nil {
        return err
    }
    return nil
}

// 删除用户
func (s *UserService) DeleteUser(id uint) error {
    if err := s.db.Delete(&User{}, id).Error; err != nil {
        return err
    }
    return nil
}

// 软删除用户
func (s *UserService) SoftDeleteUser(id uint) error {
    if err := s.db.Model(&User{}).Where("id = ?", id).Update("deleted_at", time.Now()).Error; err != nil {
        return err
    }
    return nil
}

// 恢复软删除用户
func (s *UserService) RestoreUser(id uint) error {
    if err := s.db.Model(&User{}).Where("id = ?", id).Update("deleted_at", nil).Error; err != nil {
        return err
    }
    return nil
}

// 永久删除用户
func (s *UserService) PermanentDeleteUser(id uint) error {
    if err := s.db.Unscoped().Delete(&User{}, id).Error; err != nil {
        return err
    }
    return nil
}
```

## 5. 查询构建

### 5.1 基本查询
- **Where条件**：条件查询
- **Order排序**：结果排序
- **Limit限制**：结果限制
- **Offset偏移**：分页偏移
- **Count计数**：记录计数

### 5.2 高级查询
- **Join查询**：表连接查询
- **Group分组**：分组查询
- **Having过滤**：分组过滤
- **Distinct去重**：去重查询
- **子查询**：子查询支持

### 5.3 查询条件
- **比较运算**：=, !=, >, <, >=, <=
- **逻辑运算**：AND, OR, NOT
- **范围查询**：IN, BETWEEN, LIKE
- **空值查询**：IS NULL, IS NOT NULL
- **复杂条件**：复杂条件组合

### 5.4 查询链
- **链式调用**：查询链调用
- **条件组合**：条件组合逻辑
- **查询优化**：查询性能优化
- **查询缓存**：查询结果缓存
- **查询日志**：查询日志记录

**示例**：
```go
package repositories

import (
    "gorm.io/gorm"
    "gorm.io/gorm/clause"
)

type UserRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
    return &UserRepository{db: db}
}

// 复杂查询示例
func (r *UserRepository) GetAdvancedQuery(params map[string]interface{}) ([]*User, error) {
    query := r.db.Model(&User{})

    // 动态条件
    if name, ok := params["name"].(string); ok && name != "" {
        query = query.Where("name LIKE ?", "%"+name+"%")
    }

    if email, ok := params["email"].(string); ok && email != "" {
        query = query.Where("email LIKE ?", "%"+email+"%")
    }

    if ageMin, ok := params["age_min"].(int); ok {
        query = query.Where("age >= ?", ageMin)
    }

    if ageMax, ok := params["age_max"].(int); ok {
        query = query.Where("age <= ?", ageMax)
    }

    if active, ok := params["active"].(bool); ok {
        query = query.Where("active = ?", active)
    }

    // 排序
    if sortBy, ok := params["sort_by"].(string); ok {
        order := sortBy
        if sortOrder, ok := params["sort_order"].(string); ok {
            order += " " + sortOrder
        }
        query = query.Order(order)
    } else {
        query = query.Order("created_at DESC")
    }

    // 分页
    if page, ok := params["page"].(int); ok && page > 0 {
        if limit, ok := params["limit"].(int); ok && limit > 0 {
            offset := (page - 1) * limit
            query = query.Offset(offset).Limit(limit)
        }
    }

    var users []*User
    if err := query.Find(&users).Error; err != nil {
        return nil, err
    }

    return users, nil
}

// Join查询示例
func (r *UserRepository) GetUsersWithProfiles() ([]*UserWithProfile, error) {
    var results []*UserWithProfile

    err := r.db.Model(&User{}).
        Select("users.*, profiles.avatar, profiles.bio").
        Joins("LEFT JOIN profiles ON profiles.user_id = users.id").
        Where("users.active = ?", true).
        Find(&results).Error

    if err != nil {
        return nil, err
    }

    return results, nil
}

// 分组查询示例
func (r *UserRepository) GetUserCountByAge() ([]*AgeGroupCount, error) {
    var results []*AgeGroupCount

    err := r.db.Model(&User{}).
        Select("age, COUNT(*) as count").
        Group("age").
        Order("age").
        Find(&results).Error

    if err != nil {
        return nil, err
    }

    return results, nil
}

// 子查询示例
func (r *UserRepository) GetUsersWithOrders() ([]*User, error) {
    var users []*User

    subQuery := r.db.Model(&Order{}).
        Select("user_id").
        Where("status = ?", "completed").
        Group("user_id").
        Having("COUNT(*) > ?", 5)

    err := r.db.Where("id IN (?)", subQuery).Find(&users).Error
    if err != nil {
        return nil, err
    }

    return users, nil
}

// 原生SQL查询
func (r *UserRepository) GetUsersByRawSQL() ([]*User, error) {
    var users []*User

    sql := `
        SELECT u.*
        FROM users u
        LEFT JOIN profiles p ON u.id = p.user_id
        WHERE u.active = ? AND p.avatar IS NOT NULL
        ORDER BY u.created_at DESC
    `

    err := r.db.Raw(sql, true).Scan(&users).Error
    if err != nil {
        return nil, err
    }

    return users, nil
}

type UserWithProfile struct {
    User
    Avatar string `json:"avatar"`
    Bio    string `json:"bio"`
}

type AgeGroupCount struct {
    Age   int `json:"age"`
    Count int `json:"count"`
}
```

## 6. 关联关系

### 6.1 一对一关系
- **Belongs To**：属于关系
- **Has One**：拥有一对一关系
- **外键定义**：外键字段定义
- **预加载**：关联数据预加载
- **关联查询**：关联数据查询

### 6.2 一对多关系
- **Has Many**：拥有一对多关系
- **外键定义**：外键字段定义
- **关联查询**：关联数据查询
- **关联创建**：关联数据创建
- **关联更新**：关联数据更新

### 6.3 多对多关系
- **Many to Many**：多对多关系
- **中间表**：中间表定义
- **关联查询**：关联数据查询
- **关联创建**：关联数据创建
- **关联更新**：关联数据更新

### 6.4 关联选项
- **外键约束**：外键约束配置
- **级联操作**：级联删除和更新
- **预加载策略**：预加载优化
- **关联验证**：关联数据验证
- **关联钩子**：关联钩子函数

**示例**：
```go
package models

import (
    "gorm.io/gorm"
)

// 一对一关系
type User struct {
    ID      uint    `gorm:"primaryKey"`
    Name    string  `gorm:"size:100;not null"`
    Email   string  `gorm:"size:100;unique;not null"`
    Profile *Profile `gorm:"foreignKey:UserID"`
}

type Profile struct {
    ID     uint   `gorm:"primaryKey"`
    UserID uint   `gorm:"not null;unique"`
    Avatar string `gorm:"size:255"`
    Bio    string `gorm:"type:text"`
    User   User   `gorm:"foreignKey:UserID"`
}

// 一对多关系
type Post struct {
    ID       uint      `gorm:"primaryKey"`
    Title    string    `gorm:"size:200;not null"`
    Content  string    `gorm:"type:text"`
    UserID   uint      `gorm:"not null"`
    User     User      `gorm:"foreignKey:UserID"`
    Comments []Comment `gorm:"foreignKey:PostID"`
}

type Comment struct {
    ID      uint  `gorm:"primaryKey"`
    Content string `gorm:"type:text"`
    PostID  uint  `gorm:"not null"`
    Post    Post  `gorm:"foreignKey:PostID"`
}

// 多对多关系
type Student struct {
    ID        uint       `gorm:"primaryKey"`
    Name      string     `gorm:"size:100;not null"`
    Courses   []*Course  `gorm:"many2many:student_courses;"`
}

type Course struct {
    ID          uint       `gorm:"primaryKey"`
    Name        string     `gorm:"size:100;not null"`
    Description string     `gorm:"type:text"`
    Students    []*Student `gorm:"many2many:student_courses;"`
}

type StudentCourse struct {
    StudentID uint `gorm:"primaryKey"`
    CourseID  uint `gorm:"primaryKey"`
    Grade     int  `gorm:"default:0"`
    CreatedAt time.Time
}

// 关联操作示例
type UserService struct {
    db *gorm.DB
}

func (s *UserService) GetUserWithProfile(id uint) (*User, error) {
    var user User

    // 预加载关联数据
    if err := s.db.Preload("Profile").First(&user, id).Error; err != nil {
        return nil, err
    }

    return &user, nil
}

func (s *UserService) GetUserWithPosts(id uint) (*User, error) {
    var user User

    // 预加载多个关联
    if err := s.db.Preload("Profile").Preload("Posts").First(&user, id).Error; err != nil {
        return nil, err
    }

    return &user, nil
}

func (s *UserService) GetUserWithNestedAssociations(id uint) (*User, error) {
    var user User

    // 嵌套预加载
    if err := s.db.Preload("Profile").Preload("Posts.Comments").First(&user, id).Error; err != nil {
        return nil, err
    }

    return &user, nil
}

func (s *UserService) CreateUserWithProfile(user *User, profile *Profile) error {
    return s.db.Transaction(func(tx *gorm.DB) error {
        // 创建用户
        if err := tx.Create(user).Error; err != nil {
            return err
        }

        // 创建用户档案
        profile.UserID = user.ID
        if err := tx.Create(profile).Error; err != nil {
            return err
        }

        return nil
    })
}

func (s *UserService) UpdateUserProfile(userID uint, profile *Profile) error {
    return s.db.Model(&User{}).Where("id = ?", userID).Updates(profile).Error
}

func (s *UserService) DeleteUserWithAssociations(id uint) error {
    return s.db.Transaction(func(tx *gorm.DB) error {
        // 删除用户档案
        if err := tx.Where("user_id = ?", id).Delete(&Profile{}).Error; err != nil {
            return err
        }

        // 删除用户
        if err := tx.Delete(&User{}, id).Error; err != nil {
            return err
        }

        return nil
    })
}

// 多对多操作示例
type CourseService struct {
    db *gorm.DB
}

func (s *CourseService) GetCourseWithStudents(courseID uint) (*Course, error) {
    var course Course

    if err := s.db.Preload("Students").First(&course, courseID).Error; err != nil {
        return nil, err
    }

    return &course, nil
}

func (s *CourseService) EnrollStudent(courseID, studentID uint, grade int) error {
    // 检查是否已存在关联
    var count int64
    if err := s.db.Model(&StudentCourse{}).
        Where("student_id = ? AND course_id = ?", studentID, courseID).
        Count(&count).Error; err != nil {
        return err
    }

    if count > 0 {
        // 更新成绩
        return s.db.Model(&StudentCourse{}).
            Where("student_id = ? AND course_id = ?", studentID, courseID).
            Update("grade", grade).Error
    }

    // 创建新关联
    return s.db.Create(&StudentCourse{
        StudentID: studentID,
        CourseID:  courseID,
        Grade:     grade,
    }).Error
}

func (s *CourseService) GetStudentCourses(studentID uint) ([]*Course, error) {
    var courses []*Course

    if err := s.db.Model(&Student{}).
        Where("id = ?", studentID).
        Preload("Courses").
        First(&courses).Error; err != nil {
        return nil, err
    }

    return courses, nil
}
```

## 7. 事务处理

### 7.1 事务基础
- **Begin方法**：开始事务
- **Commit方法**：提交事务
- **Rollback方法**：回滚事务
- **Savepoint**：保存点
- **嵌套事务**：嵌套事务支持

### 7.2 事务模式
- **自动提交**：自动提交模式
- **手动事务**：手动事务管理
- **嵌套事务**：嵌套事务处理
- **分布式事务**：分布式事务支持
- **事务超时**：事务超时设置

### 7.3 事务隔离
- **隔离级别**：事务隔离级别
- **脏读**：脏读防范
- **不可重复读**：不可重复读防范
- **幻读**：幻读防范
- **死锁处理**：死锁检测和处理

### 7.4 事务最佳实践
- **事务边界**：事务边界定义
- **事务大小**：事务大小控制
- **事务回滚**：事务回滚策略
- **事务日志**：事务日志记录
- **事务监控**：事务性能监控

**示例**：
```go
package services

import (
    "gorm.io/gorm"
    "errors"
)

type OrderService struct {
    db *gorm.DB
}

func NewOrderService(db *gorm.DB) *OrderService {
    return &OrderService{db: db}
}

// 简单事务示例
func (s *OrderService) CreateOrder(order *Order, items []*OrderItem) error {
    return s.db.Transaction(func(tx *gorm.DB) error {
        // 创建订单
        if err := tx.Create(order).Error; err != nil {
            return err
        }

        // 创建订单项
        for _, item := range items {
            item.OrderID = order.ID
            if err := tx.Create(item).Error; err != nil {
                return err
            }
        }

        return nil
    })
}

// 复杂事务示例
func (s *OrderService) ProcessOrder(orderID uint) error {
    return s.db.Transaction(func(tx *gorm.DB) error {
        // 获取订单
        var order Order
        if err := tx.First(&order, orderID).Error; err != nil {
            return err
        }

        // 检查订单状态
        if order.Status != "pending" {
            return errors.New("order is not in pending status")
        }

        // 更新订单状态
        if err := tx.Model(&order).Update("status", "processing").Error; err != nil {
            return err
        }

        // 扣减库存
        for _, item := range order.Items {
            if err := s.updateInventory(tx, item.ProductID, -item.Quantity); err != nil {
                return err
            }
        }

        // 计算总价
        totalAmount := s.calculateTotalAmount(order.Items)

        // 创建支付记录
        payment := &Payment{
            OrderID:  order.ID,
            Amount:   totalAmount,
            Status:   "pending",
        }

        if err := tx.Create(payment).Error; err != nil {
            return err
        }

        // 更新订单状态为已完成
        if err := tx.Model(&order).Update("status", "completed").Error; err != nil {
            return err
        }

        return nil
    })
}

// 嵌套事务示例
func (s *OrderService) BatchProcessOrders(orderIDs []uint) error {
    return s.db.Transaction(func(tx *gorm.DB) error {
        for _, orderID := range orderIDs {
            if err := s.processSingleOrder(tx, orderID); err != nil {
                return err
            }
        }
        return nil
    })
}

func (s *OrderService) processSingleOrder(tx *gorm.DB, orderID uint) error {
    // 嵌套事务会自动回滚到保存点
    return s.db.Transaction(func(nestedTx *gorm.DB) error {
        var order Order
        if err := nestedTx.First(&order, orderID).Error; err != nil {
            return err
        }

        if order.Status != "pending" {
            return errors.New("order is not pending")
        }

        return nestedTx.Model(&order).Update("status", "processing").Error
    })
}

// 手动事务管理
func (s *OrderService) ManualTransaction() error {
    tx := s.db.Begin()
    defer func() {
        if r := recover(); r != nil {
            tx.Rollback()
        }
    }()

    if err := tx.Error; err != nil {
        return err
    }

    // 执行业务逻辑
    if err := tx.Create(&Order{Status: "pending"}).Error; err != nil {
        tx.Rollback()
        return err
    }

    // 提交事务
    return tx.Commit().Error
}

// 保存点示例
func (s *OrderService) SavepointExample() error {
    tx := s.db.Begin()
    defer func() {
        if r := recover(); r != nil {
            tx.Rollback()
        }
    }()

    if err := tx.Error; err != nil {
        return err
    }

    // 创建保存点
    tx.SavePoint("sp1")

    // 执行一些操作
    if err := tx.Create(&Order{Status: "pending"}).Error; err != nil {
        // 回滚到保存点
        tx.RollbackTo("sp1")
        return err
    }

    // 继续执行
    if err := tx.Create(&Order{Status: "processing"}).Error; err != nil {
        tx.Rollback()
        return err
    }

    return tx.Commit().Error
}

// 更新库存（内部方法）
func (s *OrderService) updateInventory(tx *gorm.DB, productID uint, quantity int) error {
    return tx.Model(&Product{}).
        Where("id = ?", productID).
        UpdateColumn("stock", gorm.Expr("stock + ?", quantity)).Error
}

// 计算总价（内部方法）
func (s *OrderService) calculateTotalAmount(items []*OrderItem) float64 {
    var total float64
    for _, item := range items {
        total += item.Price * float64(item.Quantity)
    }
    return total
}
```

## 8. 钩子函数

### 8.1 生命周期钩子
- **BeforeCreate**：创建前钩子
- **AfterCreate**：创建后钩子
- **BeforeUpdate**：更新前钩子
- **AfterUpdate**：更新后钩子
- **BeforeDelete**：删除前钩子
- **AfterDelete**：删除后钩子
- **BeforeFind**：查找前钩子
- **AfterFind**：查找后钩子

### 8.2 钩子使用
- **钩子定义**：钩子函数定义
- **钩子调用**：钩子函数调用时机
- **钩子错误**：钩子函数错误处理
- **钩子顺序**：钩子函数执行顺序
- **钩子测试**：钩子函数测试

### 8.3 钩子最佳实践
- **业务逻辑**：业务逻辑钩子
- **数据验证**：数据验证钩子
- **数据转换**：数据转换钩子
- **审计日志**：审计日志钩子
- **缓存更新**：缓存更新钩子

**示例**：
```go
package models

import (
    "errors"
    "time"
    "gorm.io/gorm"
)

type User struct {
    ID        uint           `gorm:"primaryKey"`
    Name      string         `gorm:"size:100;not null"`
    Email     string         `gorm:"size:100;unique;not null"`
    Password  string         `gorm:"size:255;not null"`
    Age       int            `gorm:"default:18"`
    Active    bool           `gorm:"default:true"`
    CreatedAt time.Time      `gorm:"autoCreateTime"`
    UpdatedAt time.Time      `gorm:"autoUpdateTime"`
    DeletedAt gorm.DeletedAt `gorm:"index"`
}

// 创建前钩子
func (u *User) BeforeCreate(tx *gorm.DB) error {
    // 密码加密
    if u.Password != "" {
        hashedPassword, err := hashPassword(u.Password)
        if err != nil {
            return err
        }
        u.Password = hashedPassword
    }

    // 设置默认值
    if u.Name == "" {
        u.Name = "Anonymous"
    }

    // 验证邮箱
    if !isValidEmail(u.Email) {
        return errors.New("invalid email format")
    }

    return nil
}

// 创建后钩子
func (u *User) AfterCreate(tx *gorm.DB) error {
    // 发送欢迎邮件
    go sendWelcomeEmail(u.Email, u.Name)

    // 记录审计日志
    go logAudit("USER_CREATED", u.ID, map[string]interface{}{
        "name":  u.Name,
        "email": u.Email,
    })

    return nil
}

// 更新前钩子
func (u *User) BeforeUpdate(tx *gorm.DB) error {
    // 如果密码被修改，重新加密
    if tx.Statement.Changed("Password") {
        hashedPassword, err := hashPassword(u.Password)
        if err != nil {
            return err
        }
        u.Password = hashedPassword
    }

    // 如果邮箱被修改，验证新邮箱
    if tx.Statement.Changed("Email") {
        if !isValidEmail(u.Email) {
            return errors.New("invalid email format")
        }
    }

    return nil
}

// 更新后钩子
func (u *User) AfterUpdate(tx *gorm.DB) error {
    // 记录更新日志
    changes := make(map[string]interface{})

    for _, field := range tx.Statement.ChangedFields() {
        changes[field] = tx.Statement.ReflectValue.FieldByName(field).Interface()
    }

    if len(changes) > 0 {
        go logAudit("USER_UPDATED", u.ID, changes)
    }

    return nil
}

// 删除前钩子
func (u *User) BeforeDelete(tx *gorm.DB) error {
    // 检查是否可以删除
    if u.ID == 1 {
        return errors.New("cannot delete admin user")
    }

    // 检查是否有未完成的订单
    var orderCount int64
    if err := tx.Model(&Order{}).Where("user_id = ? AND status = ?", u.ID, "pending").Count(&orderCount).Error; err != nil {
        return err
    }

    if orderCount > 0 {
        return errors.New("user has pending orders")
    }

    return nil
}

// 删除后钩子
func (u *User) AfterDelete(tx *gorm.DB) error {
    // 清理相关数据
    go func() {
        tx.Model(&Profile{}).Where("user_id = ?", u.ID).Delete(&Profile{})
        tx.Model(&Session{}).Where("user_id = ?", u.ID).Delete(&Session{})
    }()

    // 记录删除日志
    go logAudit("USER_DELETED", u.ID, nil)

    return nil
}

// 查找前钩子
func (u *User) BeforeFind(tx *gorm.DB) error {
    // 自动包含软删除记录的条件
    if !tx.Statement.Unscoped {
        tx.Where("deleted_at IS NULL")
    }

    return nil
}

// 查找后钩子
func (u *User) AfterFind(tx *gorm.DB) error {
    // 加载额外数据
    if u.ID > 0 {
        var profile Profile
        if err := tx.Model(&Profile{}).Where("user_id = ?", u.ID).First(&profile).Error; err == nil {
            // 可以在这里做一些处理
        }
    }

    return nil
}

// 辅助函数
func hashPassword(password string) (string, error) {
    // 实现密码加密逻辑
    return "hashed_" + password, nil
}

func isValidEmail(email string) bool {
    // 实现邮箱验证逻辑
    return strings.Contains(email, "@")
}

func sendWelcomeEmail(email, name string) {
    // 实现发送邮件逻辑
    println("Sending welcome email to", email)
}

func logAudit(action string, userID uint, details map[string]interface{}) {
    // 实现审计日志记录
    println("Audit log:", action, userID, details)
}

// 全局钩子示例
func SetupGlobalHooks(db *gorm.DB) {
    // 全局创建钩子
    db.Callback().Create().Before("gorm:create").Register("global_before_create", func(db *gorm.DB) {
        println("Global before create hook")
    })

    // 全局更新钩子
    db.Callback().Update().Before("gorm:update").Register("global_before_update", func(db *gorm.DB) {
        println("Global before update hook")
    })

    // 全局删除钩子
    db.Callback().Delete().Before("gorm:delete").Register("global_before_delete", func(db *gorm.DB) {
        println("Global before delete hook")
    })
}
```

## 9. 性能优化

### 9.1 查询优化
- **索引优化**：索引创建和使用
- **查询缓存**：查询结果缓存
- **预加载优化**：关联数据预加载
- **批量操作**：批量操作优化
- **查询分析**：查询性能分析

### 9.2 连接池优化
- **连接池配置**：连接池参数调优
- **连接复用**：连接复用策略
- **连接监控**：连接池监控
- **连接泄露**：连接泄露检测
- **连接测试**：连接健康测试

### 9.3 事务优化
- **事务大小**：事务大小控制
- **事务隔离**：事务隔离级别
- **死锁处理**：死锁检测和处理
- **事务监控**：事务性能监控
- **事务重试**：事务重试机制

### 9.4 内存优化
- **内存使用**：内存使用优化
- **内存泄漏**：内存泄漏检测
- **垃圾回收**：垃圾回收优化
- **内存池**：内存池使用
- **内存监控**：内存使用监控

**示例**：
```go
package services

import (
    "gorm.io/gorm"
    "gorm.io/gorm/clause"
)

type OptimizedUserService struct {
    db *gorm.DB
}

func NewOptimizedUserService(db *gorm.DB) *OptimizedUserService {
    return &OptimizedUserService{db: db}
}

// 批量操作优化
func (s *OptimizedUserService) BatchCreateUsers(users []*User) error {
    // 使用批量插入
    return s.db.CreateInBatches(users, 100).Error
}

// 预加载优化
func (s *OptimizedUserService) GetUsersWithOptimizedPreload(page, limit int) ([]*User, int64, error) {
    var users []*User
    var total int64

    // 只在需要时预加载
    preload := func(db *gorm.DB) *gorm.DB {
        return db.Preload("Profile", func(db *gorm.DB) *gorm.DB {
            return db.Select("user_id", "avatar", "bio")
        })
    }

    // 计算总数
    if err := s.db.Model(&User{}).Count(&total).Error; err != nil {
        return nil, 0, err
    }

    // 分页查询
    offset := (page - 1) * limit
    if err := s.db.Offset(offset).Limit(limit).Scopes(preload).Find(&users).Error; err != nil {
        return nil, 0, err
    }

    return users, total, nil
}

// 查询优化 - 使用索引
func (s *OptimizedUserService) GetUsersByIndexSearch(name string, minAge, maxAge int) ([]*User, error) {
    var users []*User

    // 使用索引友好的查询
    query := s.db.Model(&User{}).
        Where("name LIKE ? AND age BETWEEN ? AND ?", name+"%", minAge, maxAge).
        Order("age DESC, name ASC").
        Limit(1000)

    if err := query.Find(&users).Error; err != nil {
        return nil, err
    }

    return users, nil
}

// 原生SQL优化
func (s *OptimizedUserService) GetUsersByOptimizedRawSQL() ([]*User, error) {
    var users []*User

    // 使用优化的原生SQL
    sql := `
        SELECT u.id, u.name, u.email, u.age, u.created_at
        FROM users u
        WHERE u.active = true
        AND u.created_at >= ?
        ORDER BY u.created_at DESC
        LIMIT ?
    `

    oneWeekAgo := time.Now().AddDate(0, 0, -7)

    if err := s.db.Raw(sql, oneWeekAgo, 100).Scan(&users).Error; err != nil {
        return nil, err
    }

    return users, nil
}

// 只选择需要的字段
func (s *OptimizedUserService) GetUserMinimalInfo(id uint) (*UserMinimalInfo, error) {
    var info UserMinimalInfo

    if err := s.db.Model(&User{}).
        Select("id", "name", "email").
        Where("id = ?", id).
        First(&info).Error; err != nil {
        return nil, err
    }

    return &info, nil
}

// 使用COUNT(1)优化
func (s *OptimizedUserService) GetUserCountByCondition(condition string) (int64, error) {
    var count int64

    if err := s.db.Model(&User{}).
        Where(condition).
        Count(&count).Error; err != nil {
        return 0, err
    }

    return count, nil
}

// 事务优化
func (s *OptimizedUserService) OptimizedTransaction() error {
    return s.db.Transaction(func(tx *gorm.DB) error {
        // 批量操作
        users := []*User{
            {Name: "User1", Email: "user1@example.com"},
            {Name: "User2", Email: "user2@example.com"},
        }

        if err := tx.CreateInBatches(users, len(users)).Error; err != nil {
            return err
        }

        // 批量更新
        if err := tx.Model(&User{}).
            Where("name LIKE ?", "User%").
            Update("active", true).Error; err != nil {
            return err
        }

        return nil
    })
}

// 连接池监控
func (s *OptimizedUserService) MonitorConnectionPool() map[string]interface{} {
    sqlDB, err := s.db.DB()
    if err != nil {
        return nil
    }

    stats := sqlDB.Stats()

    return map[string]interface{}{
        "open_connections":     stats.OpenConnections,
        "in_use":              stats.InUse,
        "idle":                stats.Idle,
        "wait_count":          stats.WaitCount,
        "wait_duration":       stats.WaitDuration,
        "max_idle_closed":      stats.MaxIdleClosed,
        "max_idle_time_closed": stats.MaxIdleTimeClosed,
        "max_lifetime_closed":  stats.MaxLifetimeClosed,
    }
}

// 查询性能监控
func (s *OptimizedUserService) ProfileQuery() ([]*User, error) {
    var users []*User

    // 启用查询日志
    s.db.Logger = s.db.Logger.LogMode(4)

    // 执行查询
    err := s.db.Where("active = ?", true).Find(&users).Error

    // 恢复日志级别
    s.db.Logger = s.db.Logger.LogMode(1)

    return users, err
}

// 使用事务重试机制
func (s *OptimizedUserService) RetryTransaction(maxRetries int, operation func(tx *gorm.DB) error) error {
    var lastErr error

    for i := 0; i < maxRetries; i++ {
        err := s.db.Transaction(operation)
        if err == nil {
            return nil
        }

        lastErr = err

        // 检查是否为可重试错误
        if !isRetryableError(err) {
            break
        }

        // 等待一段时间后重试
        time.Sleep(time.Duration(i+1) * time.Second)
    }

    return lastErr
}

func isRetryableError(err error) bool {
    // 判断错误是否为可重试错误
    return strings.Contains(err.Error(), "deadlock") ||
           strings.Contains(err.Error(), "connection reset") ||
           strings.Contains(err.Error(), "timeout")
}

type UserMinimalInfo struct {
    ID    uint  `json:"id"`
    Name  string `json:"name"`
    Email string `json:"email"`
}
```

## 10. 测试

### 10.1 单元测试
- **模型测试**：模型定义测试
- **关联测试**：关联关系测试
- **钩子测试**：钩子函数测试
- **验证测试**：数据验证测试
- **业务逻辑测试**：业务逻辑测试

### 10.2 集成测试
- **数据库测试**：数据库操作测试
- **事务测试**：事务处理测试
- **迁移测试**：迁移功能测试
- **性能测试**：性能基准测试
- **并发测试**：并发安全测试

### 10.3 测试工具
- **测试框架**：测试框架选择
- **Mock对象**：Mock对象创建
- **测试数据库**：测试数据库配置
- **测试数据**：测试数据准备
- **测试断言**：测试断言库

**示例**：
```go
package services_test

import (
    "testing"
    "github.com/stretchr/testify/assert"
    "gorm.io/driver/sqlite"
    "gorm.io/gorm"
    "myapp/models"
    "myapp/services"
)

// 设置测试数据库
func setupTestDB(t *testing.T) *gorm.DB {
    db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
    if err != nil {
        t.Fatal("Failed to connect to test database:", err)
    }

    // 自动迁移
    err = db.AutoMigrate(&models.User{}, &models.Profile{}, &models.Order{})
    if err != nil {
        t.Fatal("Failed to migrate test database:", err)
    }

    return db
}

// 用户服务测试
func TestUserService_CreateUser(t *testing.T) {
    db := setupTestDB(t)
    userService := services.NewUserService(db)

    user := &models.User{
        Name:  "Test User",
        Email: "test@example.com",
        Age:   25,
    }

    err := userService.CreateUser(user)
    assert.NoError(t, err)
    assert.NotZero(t, user.ID)

    // 验证用户是否创建成功
    foundUser, err := userService.GetUser(user.ID)
    assert.NoError(t, err)
    assert.Equal(t, user.Name, foundUser.Name)
    assert.Equal(t, user.Email, foundUser.Email)
}

func TestUserService_GetUserByEmail(t *testing.T) {
    db := setupTestDB(t)
    userService := services.NewUserService(db)

    // 创建测试用户
    user := &models.User{
        Name:  "Test User",
        Email: "test@example.com",
        Age:   25,
    }
    err := userService.CreateUser(user)
    assert.NoError(t, err)

    // 测试通过邮箱查找用户
    foundUser, err := userService.GetUserByEmail("test@example.com")
    assert.NoError(t, err)
    assert.Equal(t, user.ID, foundUser.ID)

    // 测试不存在的邮箱
    _, err = userService.GetUserByEmail("nonexistent@example.com")
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "user not found")
}

func TestUserService_UpdateUser(t *testing.T) {
    db := setupTestDB(t)
    userService := services.NewUserService(db)

    // 创建测试用户
    user := &models.User{
        Name:  "Test User",
        Email: "test@example.com",
        Age:   25,
    }
    err := userService.CreateUser(user)
    assert.NoError(t, err)

    // 更新用户
    user.Name = "Updated User"
    user.Age = 30

    err = userService.UpdateUser(user)
    assert.NoError(t, err)

    // 验证更新
    foundUser, err := userService.GetUser(user.ID)
    assert.NoError(t, err)
    assert.Equal(t, "Updated User", foundUser.Name)
    assert.Equal(t, 30, foundUser.Age)
}

func TestUserService_DeleteUser(t *testing.T) {
    db := setupTestDB(t)
    userService := services.NewUserService(db)

    // 创建测试用户
    user := &models.User{
        Name:  "Test User",
        Email: "test@example.com",
        Age:   25,
    }
    err := userService.CreateUser(user)
    assert.NoError(t, err)

    // 删除用户
    err = userService.DeleteUser(user.ID)
    assert.NoError(t, err)

    // 验证删除
    _, err = userService.GetUser(user.ID)
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "user not found")
}

// 事务测试
func TestUserService_Transaction(t *testing.T) {
    db := setupTestDB(t)
    userService := services.NewUserService(db)

    // 测试事务回滚
    err := userService.db.Transaction(func(tx *gorm.DB) error {
        user := &models.User{
            Name:  "Transaction User",
            Email: "transaction@example.com",
            Age:   25,
        }

        // 创建用户
        if err := tx.Create(user).Error; err != nil {
            return err
        }

        // 故意返回错误以触发回滚
        return assert.AnError
    })

    assert.Error(t, err)

    // 验证用户未创建
    _, err = userService.GetUserByEmail("transaction@example.com")
    assert.Error(t, err)
    assert.Contains(t, err.Error(), "user not found")
}

// 批量操作测试
func TestUserService_BatchCreateUsers(t *testing.T) {
    db := setupTestDB(t)
    userService := services.NewUserService(db)

    // 创建批量用户
    users := []*models.User{
        {Name: "User1", Email: "user1@example.com", Age: 25},
        {Name: "User2", Email: "user2@example.com", Age: 30},
        {Name: "User3", Email: "user3@example.com", Age: 35},
    }

    err := userService.BatchCreateUsers(users)
    assert.NoError(t, err)

    // 验证所有用户都创建成功
    for _, user := range users {
        foundUser, err := userService.GetUserByEmail(user.Email)
        assert.NoError(t, err)
        assert.Equal(t, user.Name, foundUser.Name)
    }
}

// 钩子函数测试
func TestUser_Hooks(t *testing.T) {
    db := setupTestDB(t)
    userService := services.NewUserService(db)

    // 测试创建钩子
    user := &models.User{
        Name:     "Hook User",
        Email:    "hook@example.com",
        Password: "password123", // 应该被加密
        Age:      25,
    }

    err := userService.CreateUser(user)
    assert.NoError(t, err)

    // 验证密码被加密
    assert.NotEqual(t, "password123", user.Password)
    assert.Contains(t, user.Password, "hashed_")

    // 测试更新钩子
    user.Password = "newpassword123"
    err = userService.UpdateUser(user)
    assert.NoError(t, err)

    // 验证新密码被加密
    assert.NotEqual(t, "newpassword123", user.Password)
    assert.Contains(t, user.Password, "hashed_")
}

// 关联关系测试
func TestUser_Associations(t *testing.T) {
    db := setupTestDB(t)
    userService := services.NewUserService(db)

    // 创建用户
    user := &models.User{
        Name:  "Association User",
        Email: "association@example.com",
        Age:   25,
    }

    err := userService.CreateUser(user)
    assert.NoError(t, err)

    // 创建用户档案
    profile := &models.Profile{
        UserID: user.ID,
        Avatar: "avatar.jpg",
        Bio:    "Test bio",
    }

    err = userService.CreateUserProfile(profile)
    assert.NoError(t, err)

    // 测试预加载
    userWithProfile, err := userService.GetUserWithProfile(user.ID)
    assert.NoError(t, err)
    assert.NotNil(t, userWithProfile.Profile)
    assert.Equal(t, profile.Avatar, userWithProfile.Profile.Avatar)
}

// 性能基准测试
func BenchmarkUserService_CreateUser(b *testing.B) {
    db := setupTestDB(b)
    userService := services.NewUserService(db)

    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        for pb.Next() {
            user := &models.User{
                Name:  "Benchmark User",
                Email: "benchmark@example.com",
                Age:   25,
            }

            err := userService.CreateUser(user)
            if err != nil {
                b.Error(err)
            }
        }
    })
}

func BenchmarkUserService_GetUser(b *testing.B) {
    db := setupTestDB(b)
    userService := services.NewUserService(db)

    // 创建测试用户
    user := &models.User{
        Name:  "Benchmark User",
        Email: "benchmark@example.com",
        Age:   25,
    }

    err := userService.CreateUser(user)
    if err != nil {
        b.Fatal(err)
    }

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        _, err := userService.GetUser(user.ID)
        if err != nil {
            b.Error(err)
        }
    }
}
```

## 11. 错误处理

### 11.1 错误类型
- **GORM错误**：GORM内置错误类型
- **数据库错误**：数据库相关错误
- **验证错误**：数据验证错误
- **事务错误**：事务处理错误
- **连接错误**：数据库连接错误

### 11.2 错误处理
- **错误检查**：错误检查和处理
- **错误转换**：错误类型转换
- **错误日志**：错误日志记录
- **错误恢复**：错误恢复策略
- **错误监控**：错误监控和告警

### 11.3 自定义错误
- **错误定义**：自定义错误类型
- **错误包装**：错误信息包装
- **错误链**：错误链追踪
- **错误码**：错误码定义
- **错误文档**：错误文档管理

**示例**：
```go
package errors

import (
    "errors"
    "fmt"
    "gorm.io/gorm"
)

// 自定义错误类型
type GormError struct {
    Code    string
    Message string
    Details interface{}
    Err     error
}

func (e *GormError) Error() string {
    return fmt.Sprintf("[%s] %s", e.Code, e.Message)
}

func (e *GormError) Unwrap() error {
    return e.Err
}

// 错误码定义
const (
    ErrCodeNotFound        = "NOT_FOUND"
    ErrCodeDuplicate       = "DUPLICATE"
    ErrCodeInvalidInput    = "INVALID_INPUT"
    ErrCodeDatabase        = "DATABASE_ERROR"
    ErrCodeTransaction     = "TRANSACTION_ERROR"
    ErrCodeValidation      = "VALIDATION_ERROR"
    ErrCodeConnection      = "CONNECTION_ERROR"
)

// 错误处理函数
func HandleGormError(err error) *GormError {
    if err == nil {
        return nil
    }

    switch {
    case errors.Is(err, gorm.ErrRecordNotFound):
        return &GormError{
            Code:    ErrCodeNotFound,
            Message: "Record not found",
            Err:     err,
        }
    case errors.Is(err, gorm.ErrInvalidTransaction):
        return &GormError{
            Code:    ErrCodeTransaction,
            Message: "Invalid transaction",
            Err:     err,
        }
    case errors.Is(err, gorm.ErrNotImplemented):
        return &GormError{
            Code:    ErrCodeDatabase,
            Message: "Not implemented",
            Err:     err,
        }
    case errors.Is(err, gorm.ErrMissingWhereClause):
        return &GormError{
            Code:    ErrCodeInvalidInput,
            Message: "Missing where clause",
            Err:     err,
        }
    case errors.Is(err, gorm.ErrUnsupportedRelation):
        return &GormError{
            Code:    ErrCodeInvalidInput,
            Message: "Unsupported relation",
            Err:     err,
        }
    case errors.Is(err, gorm.ErrPrimaryKeyRequired):
        return &GormError{
            Code:    ErrCodeValidation,
            Message: "Primary key required",
            Err:     err,
        }
    case errors.Is(err, gorm.ErrModelValueRequired):
        return &GormError{
            Code:    ErrCodeValidation,
            Message: "Model value required",
            Err:     err,
        }
    case errors.Is(err, gorm.ErrInvalidData):
        return &GormError{
            Code:    ErrCodeInvalidInput,
            Message: "Invalid data",
            Err:     err,
        }
    }

    // 处理数据库特定错误
    if isDuplicateKeyError(err) {
        return &GormError{
            Code:    ErrCodeDuplicate,
            Message: "Duplicate key error",
            Err:     err,
        }
    }

    if isConnectionError(err) {
        return &GormError{
            Code:    ErrCodeConnection,
            Message: "Database connection error",
            Err:     err,
        }
    }

    // 默认错误
    return &GormError{
        Code:    ErrCodeDatabase,
        Message: "Database error",
        Details: err.Error(),
        Err:     err,
    }
}

// 检查是否为重复键错误
func isDuplicateKeyError(err error) bool {
    return strings.Contains(err.Error(), "duplicate key") ||
           strings.Contains(err.Error(), "Duplicate entry") ||
           strings.Contains(err.Error(), "unique constraint")
}

// 检查是否为连接错误
func isConnectionError(err error) bool {
    return strings.Contains(err.Error(), "connection refused") ||
           strings.Contains(err.Error(), "no connection") ||
           strings.Contains(err.Error(), "connection reset") ||
           strings.Contains(err.Error(), "timeout")
}

// 包装错误
func WrapGormError(err error, message string) *GormError {
    if err == nil {
        return nil
    }

    gormErr := HandleGormError(err)
    gormErr.Message = message + ": " + gormErr.Message

    return gormErr
}

// 创建错误
func NewGormError(code, message string, details interface{}) *GormError {
    return &GormError{
        Code:    code,
        Message: message,
        Details: details,
    }
}

// 使用示例
package services

import (
    "myapp/errors"
    "gorm.io/gorm"
)

type UserService struct {
    db *gorm.DB
}

func (s *UserService) GetUser(id uint) (*User, error) {
    var user User

    err := s.db.First(&user, id).Error
    if err != nil {
        gormErr := errors.HandleGormError(err)
        return nil, gormErr
    }

    return &user, nil
}

func (s *UserService) CreateUser(user *User) error {
    err := s.db.Create(user).Error
    if err != nil {
        gormErr := errors.WrapGormError(err, "Failed to create user")
        gormErr.Details = map[string]interface{}{
            "name":  user.Name,
            "email": user.Email,
        }
        return gormErr
    }

    return nil
}

func (s *UserService) UpdateUser(user *User) error {
    err := s.db.Save(user).Error
    if err != nil {
        return errors.WrapGormError(err, "Failed to update user")
    }

    return nil
}

func (s *UserService) DeleteUser(id uint) error {
    err := s.db.Delete(&User{}, id).Error
    if err != nil {
        gormErr := errors.HandleGormError(err)
        if gormErr.Code == errors.ErrCodeNotFound {
            // 找不到记录不算错误
            return nil
        }
        return gormErr
    }

    return nil
}

// 事务错误处理
func (s *UserService) ProcessOrder(orderID uint) error {
    err := s.db.Transaction(func(tx *gorm.DB) error {
        var order Order
        if err := tx.First(&order, orderID).Error; err != nil {
            return errors.WrapGormError(err, "Failed to get order")
        }

        // 处理订单逻辑
        if err := s.processOrderInternal(tx, &order); err != nil {
            return err
        }

        return nil
    })

    if err != nil {
        return errors.WrapGormError(err, "Failed to process order")
    }

    return nil
}

// 错误中间件
func ErrorHandler() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()

        // 检查是否有错误
        if len(c.Errors) > 0 {
            err := c.Errors[0].Err

            // 转换为GORM错误
            gormErr := errors.HandleGormError(err)

            // 根据错误码返回不同的HTTP状态码
            var statusCode int
            switch gormErr.Code {
            case errors.ErrCodeNotFound:
                statusCode = 404
            case errors.ErrCodeInvalidInput, errors.ErrCodeValidation:
                statusCode = 400
            case errors.ErrCodeDuplicate:
                statusCode = 409
            case errors.ErrCodeConnection:
                statusCode = 503
            default:
                statusCode = 500
            }

            c.JSON(statusCode, gin.H{
                "code":    gormErr.Code,
                "message": gormErr.Message,
                "details": gormErr.Details,
            })
        }
    }
}
```

## 12. GORM最佳实践

### 12.1 项目结构
```
myapp/
├── cmd/
│   └── main.go
├── internal/
│   ├── models/
│   │   ├── user.go
│   │   ├── profile.go
│   │   └── migrations.go
│   ├── repositories/
│   │   ├── user_repository.go
│   │   └── order_repository.go
│   ├── services/
│   │   ├── user_service.go
│   │   └── order_service.go
│   ├── errors/
│   │   └── gorm_errors.go
│   └── config/
│       └── database.go
├── pkg/
│   ├── database/
│   │   └── gorm.go
│   └── logger/
│       └── logger.go
├── migrations/
│   ├── 001_create_users_table.up.sql
│   └── 001_create_users_table.down.sql
├── tests/
│   ├── services/
│   │   └── user_service_test.go
│   └── repositories/
│       └── user_repository_test.go
└── docs/
    └── gorm_guide.md
```

### 12.2 模型设计
- **命名约定**：遵循GORM命名约定
- **字段类型**：选择合适的字段类型
- **索引设计**：合理的索引设计
- **关联关系**：清晰的关联关系
- **验证规则**：数据验证规则

### 12.3 查询优化
- **索引使用**：合理使用索引
- **查询简化**：简化查询逻辑
- **批量操作**：使用批量操作
- **预加载优化**：优化预加载
- **缓存策略**：使用查询缓存

### 12.4 事务管理
- **事务边界**：明确事务边界
- **错误处理**：完善的错误处理
- **重试机制**：事务重试机制
- **性能监控**：事务性能监控
- **日志记录**：事务日志记录

### 12.5 错误处理
- **错误分类**：错误分类和处理
- **错误恢复**：错误恢复策略
- **错误日志**：错误日志记录
- **错误监控**：错误监控告警
- **用户反馈**：用户友好的错误信息

---

这个GORM ORM知识点文档涵盖了GORM框架的所有重要方面，从基础使用到高级特性，从开发实践到部署运维。掌握这些知识点将帮助你成为一名熟练的GORM框架开发者。