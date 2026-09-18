# GORM ORM知识点详解

GORM是Go语言中最流行的ORM库，提供了简洁的API和强大的功能。本文档详细介绍GORM框架的所有重要知识点，从基础使用到高级特性。

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `reference/framework-essentials` |
| **难度** | ⭐⭐ |
| **标签** | `#gorm` `#orm` `#数据库` `#框架` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 1. GORM基础

### 1.1 GORM简介

GORM 将 Go 模型与关系数据库操作连接起来，能减少常见 CRUD 的重复代码，但生成 SQL、事务和索引仍需开发者理解。数据库驱动决定具体能力与差异；模型约定方便默认映射，已有表结构则可通过显式配置适配。先完成创建、查询与错误处理再展开关联。

### 1.2 安装和配置

在 Go module 中加入 GORM 和目标数据库驱动，记录并测试所选版本组合。导入 gorm.io/gorm 只提供 ORM API，具体连接还需 postgres 等驱动。不要把 go get -u 当每次安装必需，它可能扩大依赖更新范围；已有工程先审阅升级差异。

### 1.3 数据库连接

DSN 说明地址、数据库与身份等连接参数，不应把生产密码提交到文档或代码。通过 GORM 取得底层 sql.DB 管理池，启动时验证必要连接，退出时关闭。多数据库各有连接、事务和一致性边界，不因为持有多个句柄就自动拥有跨库原子性。

**示例**：
```go
package main

import (
    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "log"
    "time"
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

模型结构体描述字段，标签控制列名、主键或索引等映射，默认命名约定只是在没有显式设置时生效。先查看实际生成的表结构，确认 id、时间字段和可空性符合需求；HTTP 客户端能写哪些字段应另外用输入模型限制。

### 2.2 字段类型

Go 值与数据库类型之间需明确缺失、零值和精度，例如 *string 或 nullable 类型可区分 NULL 与空串，金额不能随意转成 float。JSON、枚举与自定义类型依数据库和驱动支持，必要时实现 Scanner/Valuer 等契约。写入边界值再读回，检查没有精度或时区丢失。

### 2.3 模型标签

primaryKey 标识主键，autoIncrement 请求相应自增行为，index/unique/not null 表达索引或约束意图，最终支持取决于数据库与迁移执行。唯一约束才防止并发下重复插入，“先查询不存在再创建”本身有竞态。验证重复值和 NULL 的实际失败结果。

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

AutoMigrate 根据模型尝试补齐受支持的 schema 变化，返回错误必须处理；它不是带版本历史与自动回滚的完整迁移系统，也不会为保护数据随意删除旧列。生产变更需审阅锁表、数据回填与兼容影响，参见[官方迁移说明](https://gorm.io/docs/migration.html)。

### 3.2 手动迁移

Migrator 提供创建表、修改列和管理索引/约束的接口，但数据库对这些操作的能力与事务支持不同。删除列或表可能永久丢数据，迁移应包含前置检查和恢复设计。先对有代表性旧数据的测试库执行，并验证新旧应用过渡期间都能读写。

### 3.3 迁移策略

开发期可以快速重建合成数据，生产则需要保留已应用变更历史并评估兼容窗口。通常先添加兼容结构、回填数据、切换代码，再移除旧结构；迁移失败后的继续或恢复步骤必须明确。验收同时覆盖空库创建和旧库升级，不能只验证本机新数据库。

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

Create 写入新记录，传入指针可取得回填的主键；传统链式 API 检查 Error，必要时检查 RowsAffected。批量创建减少往返但要控制批大小与失败语义。带默认值标签的字段要特别测试 0、false 等零值，确认数据库默认没有覆盖用户明确意图。

### 4.2 查询记录

First 取得一条记录且可能返回 ErrRecordNotFound，Find 查询集合时零行通常通过空结果/影响行数表达，不能统一按同一种错误判断。Where 与排序决定取到什么，未指定稳定顺序的“第一条”不适合作业务时间顺序承诺。查零条、一条和多条验证契约。

### 4.3 更新记录

Update 处理指定字段，Updates 可修改多个字段，目标是哪些行由 Model 与条件决定；“多字段”不等于必然“多行”。传统 API 的 struct Updates 默认忽略零值，map 或 Select 可显式写入 false/0。Save 的保存语义还可能涉及插入回退，避免在只允许更新的接口盲用，见[官方更新说明](https://gorm.io/docs/update.html)。

### 4.4 删除记录

Delete 需要明确目标条件，避免把空输入误解成全表删除。具有软删除字段的模型通常标记删除时间，普通查询过滤这些记录；Unscoped 等路径可能绕过保护或永久删除。软删除不等于隐私数据已擦除，恢复、保留期与清理要另设策略。

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

Where 筛选、Order 排序、Limit/Offset 分页、Count 统计各承担不同责任。分页需要稳定排序并控制最大页大小，深偏移可能越来越贵。先用固定数据验证各页不重复遗漏，再用实际执行计划判断性能，不以链式调用短就认为 SQL 高效。

### 5.2 高级查询

Join 组合表时可能把一条主记录展开成多行；Group 后 Having 过滤分组结果，而普通 Where 过滤参与分组的行。Distinct 的列集合决定什么算重复。先手工写出少量输入的预期行数，再检查生成 SQL 和 ORM 扫描结果，防止计数或分页被关联放大。

### 5.3 查询条件

参数值通过占位符绑定，列名和排序方向等不能当普通值绑定的部分用允许列表选择。SQL 的 NULL 判断使用 IS NULL 等语义，不等同普通等号；AND/OR 加括号明确优先关系。测试空列表、NULL 和组合条件，避免意外扩大可访问记录范围。

### 5.4 查询链

链式方法累积查询条件，执行方法触发 SQL；复用已带条件的对象时要了解会话行为，防止条件污染下一次查询。查看 SQL 和绑定参数帮助理解真正执行了什么，日志须脱敏。查询结果缓存不是所有 GORM 查询默认提供的功能，需要单独说明实现和失效策略。

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

Belongs To 与 Has One 的关键差别是外键放在哪一侧，例如订单持有 customer_id 表示属于客户，用户的 profile 可能由 profile.user_id 关联。Preload 显式加载关系，不应假定访问字段就自动发起懒查询。验证无关联记录时的结果形状。

### 6.2 一对多关系

Has Many 表示一条主记录关联多条子记录，如用户与订单，子表外键说明归属。加载用户列表后逐个查询订单可能产生 N+1，按需求批量预加载并控制数据量。修改关联和删除子记录是不同操作，执行后重新查询数据库确认效果。

### 6.3 多对多关系

多对多用中间表记录两端关系，例如学生与课程；若关系本身有成绩等属性，可显式建模中间表。唯一约束避免同一关系重复插入。解除关联通常只影响中间表，不等于删除课程或学生；分别测试添加、重复添加和解除关系。

### 6.4 关联选项

外键和级联由数据库约束保护，ORM 的关联保存是应用侧操作，两者不能互相代替。选择删除行为前明确是阻止、级联还是置空，并测试真实数据库结果。预加载会增加数据与查询成本，按接口需要选择字段和关系，而非一次加载所有关联。

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
    var student Student

    if err := s.db.Model(&Student{}).
        Where("id = ?", studentID).
        Preload("Courses").
        First(&student).Error; err != nil {
        return nil, err
    }

    return student.Courses, nil
}
```

## 7. 事务处理

### 7.1 事务基础

一个事务让一组数据库操作一起提交或回滚。使用 Transaction 回调时，内部都用收到的 tx，返回错误触发回滚；手工 Begin/Commit/Rollback 则要检查每一步错误并覆盖所有退出路径。SavePoint/RollbackTo 可回退局部操作，但仍属于外层事务，见[官方事务说明](https://gorm.io/docs/transactions.html)。

### 7.2 事务模式

单次写入的默认事务不等于多次调用自动处在同一事务，需要显式包住完整业务步骤。嵌套事务通常通过保存点表达局部回退；跨数据库或消息系统的原子提交不由普通 GORM 事务自动提供。超时需通过 context/驱动与数据库配合，并确认失败后连接归还。

### 7.3 事务隔离

隔离级别约束并发事务可观察的变化，脏读、不可重复读与幻读分别关注未提交值、重复读值改变及结果集合变化，具体保证以数据库实现为准。更强隔离可能增加等待或重试；用两条并发事务实验验证余额/库存不变量，而不是仅写出级别名称。

### 7.4 事务最佳实践

事务边界覆盖必须一致的写入，例如创建订单与扣库存，不把慢外部请求混入持锁阶段。死锁或序列化冲突可按数据库错误分类考虑重试，但每次应重新执行完整事务并限制次数；重复外部副作用不能随意重放。记录事务耗时与失败原因，测试第二步失败时第一步也撤销。

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

模型写入钩子包括 BeforeSave/BeforeCreate、AfterCreate/AfterSave 以及更新、删除对应阶段；查询模型钩子是 AfterFind，BeforeFind 不是同样自动识别的模型钩子。写入后的 hook 可能仍在提交之前，不能据其名称就发送不可撤销邮件。具体时序见[官方 hooks](https://gorm.io/docs/hooks.html)。

### 8.2 钩子使用

钩子采用框架要求的方法签名，返回错误能中止相应操作并影响当前事务。调用哪些钩子与使用的写入方法、批量形式和跳过配置有关，要测试实际调用路径；把函数命名得像 hook 不会自动让框架调用它。验证一次成功和一次 hook 拒绝时数据库状态。

### 8.3 钩子最佳实践

钩子适合靠近模型的不变量或同事务审计写入，不适合隐藏复杂网络副作用。发送邮件或更新外部缓存若发生在数据库提交之前，后续回滚可能留下错误通知；可靠发送需要提交协调与重试设计。不要在 hook 中启动 goroutine 继续使用 tx，它可能已经结束。

**示例：在同一事务中校验任务并记录审计行**

下面是模型文件，不是独立的 main 程序。调用方先迁移 `Task` 与 `TaskAudit`，再通过 `db.Create(&task)` 创建任务。审计记录使用传入的 `tx` 同步写入；审计失败会让本次创建返回错误。在默认写入事务或调用方显式事务中，两次写入一起提交或回滚。若关闭默认事务且没有外层事务，就不再拥有这个原子性保证。

```go
package models

import (
    "errors"
    "strings"
    "unicode/utf8"

    "gorm.io/gorm"
)

type Task struct {
    ID         uint   `gorm:"primaryKey"`
    Title      string
    TitleRunes int    `gorm:"-"` // 读取后计算，不保存到数据库
}

type TaskAudit struct {
    ID     uint `gorm:"primaryKey"`
    TaskID uint
    Action string
}

func (t *Task) BeforeCreate(tx *gorm.DB) error {
    t.Title = strings.TrimSpace(t.Title)
    if t.Title == "" {
        return errors.New("task title must not be empty")
    }
    return nil
}

func (t *Task) AfterCreate(tx *gorm.DB) error {
    return tx.Create(&TaskAudit{TaskID: t.ID, Action: "created"}).Error
}

func (t *Task) AfterFind(tx *gorm.DB) error {
    t.TitleRunes = utf8.RuneCountInString(t.Title)
    return nil
}
```

这里的字符数是 Unicode 码点数量，不保证等于用户看到的字形数量。AfterFind 只计算字段，不额外查询关联数据，避免查询一页任务时偷偷增加一串数据库请求。

验证时分别尝试：空白标题应返回错误且没有新任务；有效标题应同时产生任务和审计行；在外层 `db.Transaction` 中创建后主动返回错误，两张表都不应保留本次新增行。创建后钩子仍可能位于提交之前，因此发邮件等外部副作用不能照搬这个例子；可靠投递需要在事务里记录待发送事件，再由独立任务处理重试。

## 9. 性能优化

### 9.1 查询优化

先查看慢查询的 SQL、参数规模与执行计划，判断索引是否服务筛选和排序。预加载解决部分 N+1，但加载过多关联也浪费资源；批量操作减少往返却可能扩大单次锁与内存。结果缓存需要另建失效契约，不能把“使用 GORM”当作自动拥有缓存。

### 9.2 连接池优化

池参数从底层 sql.DB 调整，观察等待、使用中和空闲连接，再结合数据库与副本数量设预算。事务未结束、Rows 未关闭都可能延长连接占用。模拟请求取消和查询失败后观察使用中连接回落，不把“连接池设置了数字”当作优化完成。

### 9.3 事务优化

长事务会延长锁和连接持有，拆小前先确认业务是否允许分批成功。死锁可以通过统一锁顺序、减少范围等降低，重试只对已识别暂时性失败使用，并有上限与退避。比较同一负载下等待、失败与完成时间，而不单看每次事务的代码行数。

### 9.4 内存优化

查询过多行和关联会同时增加数据库传输、扫描与 Go 堆分配。先限制结果范围或分批处理，记录峰值与持续负载后的内存，再判断是否存在长期持有。对象池有复用与清理成本，不能为所有模型默认添加；GC 参数也不能修复无界缓存。

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

不依赖数据库的校验和业务计算可以直接测输入输出；模型标签、实际 hook 调用和关系保存则需要相应 ORM/数据库路径验证。用可控失败检查业务没有留下部分状态，避免 mock 掉整个被测行为后只验证调用脚本。

### 10.2 集成测试

集成测试使用与目标数据库语义相符的环境，验证事务回滚、唯一约束、迁移和并发修改。SQLite 方便小实验但不能自动代表 PostgreSQL/MySQL 的隔离、类型和 SQL 方言。每条测试隔离数据，发布迁移还要测试旧结构升级而不仅新库创建。

### 10.3 测试工具

Go testing 提供测试组织，断言库只改善表达，mock 用于明确的外部边界，容器数据库用于验证真实 SQL。夹具采用可识别合成数据，每例清理或重建。选择工具后先故意破坏一条约束，确认测试真的失败，而不是单纯检查命令退出成功。

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

// 设置测试数据库（testing.TB 同时兼容 *testing.T 与 *testing.B）
func setupTestDB(tb testing.TB) *gorm.DB {
    db, err := gorm.Open(sqlite.Open("file::memory:?cache=shared"), &gorm.Config{})
    if err != nil {
        tb.Fatal("Failed to connect to test database:", err)
    }

    // 自动迁移
    err = db.AutoMigrate(&models.User{}, &models.Profile{}, &models.Order{})
    if err != nil {
        tb.Fatal("Failed to migrate test database:", err)
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

区分未找到、唯一约束冲突、连接失败与业务验证错误，因为调用者的恢复动作不同。传统链式 API 通过 Error 取结果，支持的错误翻译还需相应配置；底层数据库错误仍按驱动契约识别。不要靠任意字符串包含关系决定是否重试。

### 11.2 错误处理

发生错误后先判断能否恢复，再补充操作上下文并传播；事务中的失败不能被吞掉后返回 nil。HTTP 边界把内部错误翻译为稳定响应，日志记录必要原因并脱敏。对暂时故障重试前确认幂等和总时限，永久格式错误应及时返回给调用者。

### 11.3 自定义错误

自定义错误保留稳定类别与必要上下文，包装时使用可追溯原因的方式，使 errors.Is/As 仍能判断底层问题。错误码用于客户端决策，文案用于解释，日志用于内部排查，三者不用共享同一条含 SQL 的字符串。为每个公开错误写一个可触发的请求例子。

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

从查询与业务不变量反推模型：哪些字段可空、何者唯一、关联由谁拥有、删除后发生什么。索引根据实际筛选/排序建立，写入成本与存储成本也需考虑。应用校验改善反馈，数据库约束抵御并发竞态，两者共同验证重复值和越界状态。

### 12.3 查询优化

选一个具体慢接口，保存其 SQL、执行计划、数据量与延迟基线；改变索引、投影字段或加载方式后在同等负载复测。不要把批量、预加载和缓存一次全部加入，否则难以知道哪个改动有效，也容易引入新的一致性问题。

### 12.4 事务管理

用一条失败实验定义事务承诺：扣库存成功后创建订单失败，最终库存应保持原值。确保两步使用同一个 tx，提交结果被检查。只有明确可重试的数据库冲突才重新执行整个业务单元，日志记录次数与最终结果而非秘密参数。

### 12.5 错误处理

错误处理的验收是调用方知道能否修改输入、重试或联系支持，运维能够查到真实原因。对未找到、冲突和连接失败分别编写用例，确认状态不同且未泄漏内部信息；恢复动作失败时继续传播，不用返回空列表掩盖数据库不可用。

---

这个GORM ORM知识点文档涵盖了GORM框架的所有重要方面，从基础使用到高级特性，从开发实践到部署运维。掌握这些知识点将帮助你成为一名熟练的GORM框架开发者。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
