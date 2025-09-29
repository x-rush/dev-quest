# GORM+PostgreSQL最佳实践指南

本文档详细介绍GORM与PostgreSQL集成的最佳实践，涵盖模型设计、查询优化、事务处理、性能调优等核心内容。

## 1. 基础配置

### 1.1 数据库连接配置
```go
package database

import (
    "fmt"
    "log"
    "time"

    "gorm.io/driver/postgres"
    "gorm.io/gorm"
    "gorm.io/gorm/logger"
)

// 数据库配置
type DatabaseConfig struct {
    Host            string
    Port            int
    User            string
    Password        string
    DBName          string
    SSLMode         string
    MaxIdleConns    int
    MaxOpenConns    int
    ConnMaxLifetime time.Duration
    ConnMaxIdleTime time.Duration
    LogMode         logger.LogLevel
}

// 默认配置
func DefaultDatabaseConfig() *DatabaseConfig {
    return &DatabaseConfig{
        Host:            "localhost",
        Port:            5432,
        User:            "postgres",
        Password:        "password",
        DBName:          "myapp",
        SSLMode:         "disable",
        MaxIdleConns:    10,
        MaxOpenConns:    100,
        ConnMaxLifetime: 5 * time.Minute,
        ConnMaxIdleTime: 5 * time.Minute,
        LogMode:         logger.Info,
    }
}

// 创建数据库连接
func NewDatabaseConnection(config *DatabaseConfig) (*gorm.DB, error) {
    // 构建DSN
    dsn := fmt.Sprintf("host=%s user=%s password=%s dbname=%s port=%d sslmode=%s TimeZone=Asia/Shanghai",
        config.Host, config.User, config.Password, config.DBName, config.Port, config.SSLMode)

    // GORM配置
    gormConfig := &gorm.Config{
        Logger: logger.Default.LogMode(config.LogMode),
        NamingStrategy: gorm.NamingStrategy{
            TablePrefix:   "",
            SingularTable: false,
            NameReplacer:  nil,
        },
        DisableForeignKeyConstraintWhenMigrating: false,
    }

    // 连接数据库
    db, err := gorm.Open(postgres.Open(dsn), gormConfig)
    if err != nil {
        return nil, fmt.Errorf("failed to connect database: %w", err)
    }

    // 配置连接池
    sqlDB, err := db.DB()
    if err != nil {
        return nil, fmt.Errorf("failed to get sql.DB: %w", err)
    }

    sqlDB.SetMaxIdleConns(config.MaxIdleConns)
    sqlDB.SetMaxOpenConns(config.MaxOpenConns)
    sqlDB.SetConnMaxLifetime(config.ConnMaxLifetime)
    sqlDB.SetConnMaxIdleTime(config.ConnMaxIdleTime)

    // 测试连接
    if err := sqlDB.Ping(); err != nil {
        return nil, fmt.Errorf("failed to ping database: %w", err)
    }

    log.Println("Database connected successfully")
    return db, nil
}

// 健康检查
func CheckDatabaseHealth(db *gorm.DB) error {
    sqlDB, err := db.DB()
    if err != nil {
        return err
    }

    return sqlDB.Ping()
}

// 获取数据库统计信息
func GetDatabaseStats(db *gorm.DB) (*gorm.DBStats, error) {
    sqlDB, err := db.DB()
    if err != nil {
        return nil, err
    }

    stats := sqlDB.Stats()
    return &gorm.DBStats{
        OpenConnections: stats.OpenConnections,
        InUse:          stats.InUse,
        Idle:           stats.Idle,
        WaitCount:      stats.WaitCount,
        WaitDuration:   stats.WaitDuration,
        MaxIdleClosed:  stats.MaxIdleClosed,
        MaxLifetimeClosed: stats.MaxLifetimeClosed,
    }, nil
}

// 数据库统计信息
type DBStats struct {
    OpenConnections     int           `json:"open_connections"`
    InUse              int           `json:"in_use"`
    Idle               int           `json:"idle"`
    WaitCount          int64         `json:"wait_count"`
    WaitDuration       time.Duration `json:"wait_duration"`
    MaxIdleClosed      int64         `json:"max_idle_closed"`
    MaxLifetimeClosed  int64         `json:"max_lifetime_closed"`
}
```

### 1.2 数据库迁移
```go
package migration

import (
    "log"
    "time"

    "gorm.io/gorm"
)

// 迁移管理器
type MigrationManager struct {
    db         *gorm.DB
    migrations []Migration
}

type Migration struct {
    ID        string
    Name      string
    Up        func(*gorm.DB) error
    Down      func(*gorm.DB) error
    CreatedAt time.Time
}

func NewMigrationManager(db *gorm.DB) *MigrationManager {
    return &MigrationManager{
        db: db,
    }
}

// 创建迁移表
func (m *MigrationManager) createMigrationsTable() error {
    return m.db.AutoMigrate(&MigrationHistory{})
}

type MigrationHistory struct {
    ID        string `gorm:"primaryKey"`
    Name      string
    Batch     int
    CreatedAt time.Time
}

// 添加迁移
func (m *MigrationManager) AddMigration(id, name string, up, down func(*gorm.DB) error) {
    m.migrations = append(m.migrations, Migration{
        ID:        id,
        Name:      name,
        Up:        up,
        Down:      down,
        CreatedAt: time.Now(),
    })
}

// 执行迁移
func (m *MigrationManager) Migrate() error {
    if err := m.createMigrationsTable(); err != nil {
        return fmt.Errorf("failed to create migrations table: %w", err)
    }

    // 获取已执行的迁移
    var executedMigrations []MigrationHistory
    if err := m.db.Order("batch DESC").Find(&executedMigrations).Error; err != nil {
        return fmt.Errorf("failed to get executed migrations: %w", err)
    }

    executed := make(map[string]bool)
    for _, migration := range executedMigrations {
        executed[migration.ID] = true
    }

    // 获取当前批次号
    var batch int
    if len(executedMigrations) > 0 {
        batch = executedMigrations[0].Batch + 1
    } else {
        batch = 1
    }

    // 执行未执行的迁移
    for _, migration := range m.migrations {
        if !executed[migration.ID] {
            log.Printf("Executing migration: %s", migration.Name)

            if err := migration.Up(m.db); err != nil {
                return fmt.Errorf("failed to execute migration %s: %w", migration.Name, err)
            }

            // 记录迁移历史
            history := MigrationHistory{
                ID:        migration.ID,
                Name:      migration.Name,
                Batch:     batch,
                CreatedAt: time.Now(),
            }

            if err := m.db.Create(&history).Error; err != nil {
                return fmt.Errorf("failed to record migration %s: %w", migration.Name, err)
            }

            log.Printf("Migration completed: %s", migration.Name)
        }
    }

    return nil
}

// 回滚迁移
func (m *MigrationManager) Rollback(steps int) error {
    // 获取已执行的迁移
    var executedMigrations []MigrationHistory
    if err := m.db.Order("batch DESC").Find(&executedMigrations).Error; err != nil {
        return fmt.Errorf("failed to get executed migrations: %w", err)
    }

    if len(executedMigrations) == 0 {
        return fmt.Errorf("no migrations to rollback")
    }

    // 获取当前批次
    currentBatch := executedMigrations[0].Batch

    // 收集要回滚的迁移
    var toRollback []MigrationHistory
    for _, migration := range executedMigrations {
        if migration.Batch == currentBatch {
            toRollback = append(toRollback, migration)
            if len(toRollback) >= steps {
                break
            }
        }
    }

    // 执行回滚
    for _, migration := range toRollback {
        // 查找迁移定义
        var migrationDef *Migration
        for _, def := range m.migrations {
            if def.ID == migration.ID {
                migrationDef = &def
                break
            }
        }

        if migrationDef == nil {
            return fmt.Errorf("migration definition not found: %s", migration.ID)
        }

        log.Printf("Rolling back migration: %s", migrationDef.Name)

        if err := migrationDef.Down(m.db); err != nil {
            return fmt.Errorf("failed to rollback migration %s: %w", migrationDef.Name, err)
        }

        // 删除迁移记录
        if err := m.db.Delete(&migration).Error; err != nil {
            return fmt.Errorf("failed to delete migration record %s: %w", migrationDef.Name, err)
        }

        log.Printf("Rollback completed: %s", migrationDef.Name)
    }

    return nil
}

// 示例迁移
func SetupMigrations(db *gorm.DB) error {
    manager := NewMigrationManager(db)

    // 用户表迁移
    manager.AddMigration("001", "create_users_table",
        func(db *gorm.DB) error {
            return db.AutoMigrate(&User{})
        },
        func(db *gorm.DB) error {
            return db.Migrator().DropTable(&User{})
        },
    )

    // 产品表迁移
    manager.AddMigration("002", "create_products_table",
        func(db *gorm.DB) error {
            return db.AutoMigrate(&Product{})
        },
        func(db *gorm.DB) error {
            return db.Migrator().DropTable(&Product{})
        },
    )

    // 订单表迁移
    manager.AddMigration("003", "create_orders_table",
        func(db *gorm.DB) error {
            return db.AutoMigrate(&Order{})
        },
        func(db *gorm.DB) error {
            return db.Migrator().DropTable(&Order{})
        },
    )

    // 添加索引
    manager.AddMigration("004", "add_indexes",
        func(db *gorm.DB) error {
            // 用户邮箱索引
            if err := db.Exec("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email ON users(email)").Error; err != nil {
                return err
            }

            // 产品创建时间索引
            if err := db.Exec("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_products_created_at ON products(created_at)").Error; err != nil {
                return err
            }

            // 订单用户索引
            if err := db.Exec("CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_orders_user_id ON orders(user_id)").Error; err != nil {
                return err
            }

            return nil
        },
        func(db *gorm.DB) error {
            // 删除索引
            db.Exec("DROP INDEX CONCURRENTLY IF EXISTS idx_users_email")
            db.Exec("DROP INDEX CONCURRENTLY IF EXISTS idx_products_created_at")
            db.Exec("DROP INDEX CONCURRENTLY IF EXISTS idx_orders_user_id")
            return nil
        },
    )

    return manager.Migrate()
}
```

## 2. 模型设计

### 2.1 基础模型定义
```go
package models

import (
    "time"

    "gorm.io/gorm"
)

// 基础模型
type BaseModel struct {
    ID        uint           `gorm:"primaryKey" json:"id"`
    CreatedAt time.Time      `json:"created_at"`
    UpdatedAt time.Time      `json:"updated_at"`
    DeletedAt gorm.DeletedAt `gorm:"index" json:"deleted_at,omitempty"`
}

// 用户模型
type User struct {
    BaseModel
    Username    string         `gorm:"size:50;uniqueIndex;not null" json:"username"`
    Email       string         `gorm:"size:100;uniqueIndex;not null" json:"email"`
    Password    string         `gorm:"size:255;not null" json:"-"`
    FirstName   string         `gorm:"size:50" json:"first_name"`
    LastName    string         `gorm:"size:50" json:"last_name"`
    Phone       string         `gorm:"size:20" json:"phone"`
    Avatar      string         `gorm:"size:255" json:"avatar"`
    Status      string         `gorm:"size:20;default:'active';index" json:"status"`
    LastLoginAt *time.Time    `json:"last_login_at,omitempty"`
    EmailVerifiedAt *time.Time `json:"email_verified_at,omitempty"`
    Metadata    JSON           `gorm:"type:jsonb" json:"metadata"`
    Profiles    []Profile      `gorm:"foreignKey:UserID" json:"profiles,omitempty"`
    Orders      []Order        `gorm:"foreignKey:UserID" json:"orders,omitempty"`
}

// 用户档案模型
type Profile struct {
    BaseModel
    UserID      uint      `gorm:"not null;index" json:"user_id"`
    User        User      `gorm:"foreignKey:UserID" json:"user,omitempty"`
    Bio         string    `gorm:"type:text" json:"bio"`
    Website     string    `gorm:"size:255" json:"website"`
    Location    string    `gorm:"size:100" json:"location"`
    BirthDate   *time.Time `json:"birth_date,omitempty"`
    Gender      string    `gorm:"size:10" json:"gender"`
    Preferences JSON      `gorm:"type:jsonb" json:"preferences"`
}

// 产品模型
type Product struct {
    BaseModel
    Name        string      `gorm:"size:255;not null;index" json:"name"`
    Slug        string      `gorm:"size:255;uniqueIndex;not null" json:"slug"`
    Description string      `gorm:"type:text" json:"description"`
    Price       float64     `gorm:"type:decimal(10,2);not null" json:"price"`
    CategoryID  uint        `gorm:"index" json:"category_id"`
    Category    Category    `gorm:"foreignKey:CategoryID" json:"category,omitempty"`
    SKU         string      `gorm:"size:100;uniqueIndex" json:"sku"`
    Stock       int         `gorm:"default:0" json:"stock"`
    Images      []ProductImage `gorm:"foreignKey:ProductID" json:"images,omitempty"`
    Tags        []Tag       `gorm:"many2many:product_tags;" json:"tags,omitempty"`
    Variants    []ProductVariant `gorm:"foreignKey:ProductID" json:"variants,omitempty"`
    Status      string      `gorm:"size:20;default:'active';index" json:"status"`
    PublishedAt *time.Time `json:"published_at,omitempty"`
    Metadata    JSON        `gorm:"type:jsonb" json:"metadata"`
}

// 产品图片模型
type ProductImage struct {
    BaseModel
    ProductID   uint   `gorm:"not null;index" json:"product_id"`
    Product     Product `gorm:"foreignKey:ProductID" json:"product,omitempty"`
    URL         string `gorm:"size:500;not null" json:"url"`
    Alt         string `gorm:"size:255" json:"alt"`
    Width       int    `json:"width"`
    Height      int    `json:"height"`
    Size        int64  `json:"size"`
    Position    int    `gorm:"default:0" json:"position"`
    IsPrimary   bool   `gorm:"default:false" json:"is_primary"`
}

// 产品变体模型
type ProductVariant struct {
    BaseModel
    ProductID uint    `gorm:"not null;index" json:"product_id"`
    Product   Product `gorm:"foreignKey:ProductID" json:"product,omitempty"`
    Name      string  `gorm:"size:255;not null" json:"name"`
    SKU       string  `gorm:"size:100;uniqueIndex" json:"sku"`
    Price     float64 `gorm:"type:decimal(10,2);not null" json:"price"`
    Stock     int     `gorm:"default:0" json:"stock"`
    Attributes JSON    `gorm:"type:jsonb" json:"attributes"`
}

// 分类模型
type Category struct {
    BaseModel
    Name        string      `gorm:"size:255;not null;uniqueIndex" json:"name"`
    Slug        string      `gorm:"size:255;uniqueIndex;not null" json:"slug"`
    Description string      `gorm:"type:text" json:"description"`
    ParentID    *uint       `gorm:"index" json:"parent_id,omitempty"`
    Parent      *Category   `gorm:"foreignKey:ParentID" json:"parent,omitempty"`
    Children    []Category  `gorm:"foreignKey:ParentID" json:"children,omitempty"`
    Products    []Product   `gorm:"foreignKey:CategoryID" json:"products,omitempty"`
    Image       string      `gorm:"size:500" json:"image"`
    SortOrder   int         `gorm:"default:0" json:"sort_order"`
    IsActive    bool        `gorm:"default:true;index" json:"is_active"`
}

// 标签模型
type Tag struct {
    BaseModel
    Name        string    `gorm:"size:100;uniqueIndex;not null" json:"name"`
    Slug        string    `gorm:"size:100;uniqueIndex;not null" json:"slug"`
    Description string    `gorm:"type:text" json:"description"`
    Color       string    `gorm:"size:20" json:"color"`
    Products    []Product `gorm:"many2many:product_tags;" json:"products,omitempty"`
}

// 订单模型
type Order struct {
    BaseModel
    OrderNumber string              `gorm:"size:50;uniqueIndex;not null" json:"order_number"`
    UserID      uint                `gorm:"index" json:"user_id"`
    User        User                `gorm:"foreignKey:UserID" json:"user,omitempty"`
    Status      string              `gorm:"size:20;index;default:'pending'" json:"status"`
    TotalAmount float64             `gorm:"type:decimal(10,2);not null" json:"total_amount"`
    Currency    string              `gorm:"size:3;default:'USD'" json:"currency"`
    Items       []OrderItem         `gorm:"foreignKey:OrderID" json:"items,omitempty"`
    Shipping    OrderShipping       `gorm:"foreignKey:OrderID" json:"shipping,omitempty"`
    Payment     OrderPayment        `gorm:"foreignKey:OrderID" json:"payment,omitempty"`
    Notes       string              `gorm:"type:text" json:"notes"`
    Metadata    JSON                `gorm:"type:jsonb" json:"metadata"`
}

// 订单项模型
type OrderItem struct {
    BaseModel
    OrderID     uint             `gorm:"not null;index" json:"order_id"`
    Order       Order            `gorm:"foreignKey:OrderID" json:"order,omitempty"`
    ProductID   uint             `gorm:"not null" json:"product_id"`
    Product     Product          `gorm:"foreignKey:ProductID" json:"product,omitempty"`
    VariantID   *uint            `json:"variant_id,omitempty"`
    Variant     *ProductVariant  `gorm:"foreignKey:VariantID" json:"variant,omitempty"`
    Quantity    int              `gorm:"not null" json:"quantity"`
    UnitPrice   float64          `gorm:"type:decimal(10,2);not null" json:"unit_price"`
    TotalPrice  float64          `gorm:"type:decimal(10,2);not null" json:"total_price"`
    Attributes  JSON             `gorm:"type:jsonb" json:"attributes"`
}

// 订单配送模型
type OrderShipping struct {
    BaseModel
    OrderID       uint           `gorm:"not null;index" json:"order_id"`
    Order         Order          `gorm:"foreignKey:OrderID" json:"order,omitempty"`
    FirstName     string         `gorm:"size:50" json:"first_name"`
    LastName      string         `gorm:"size:50" json:"last_name"`
    Company       string         `gorm:"size:100" json:"company"`
    Address1      string         `gorm:"size:255" json:"address1"`
    Address2      string         `gorm:"size:255" json:"address2"`
    City          string         `gorm:"size:100" json:"city"`
    State         string         `gorm:"size:100" json:"state"`
    PostalCode    string         `gorm:"size:20" json:"postal_code"`
    Country       string         `gorm:"size:50" json:"country"`
    Phone         string         `gorm:"size:20" json:"phone"`
    Method        string         `gorm:"size:50" json:"method"`
    Cost          float64        `gorm:"type:decimal(10,2)" json:"cost"`
    TrackingNumber string       `gorm:"size:100" json:"tracking_number"`
    Status        string         `gorm:"size:20" json:"status"`
    ShippedAt     *time.Time     `json:"shipped_at,omitempty"`
    DeliveredAt   *time.Time     `json:"delivered_at,omitempty"`
}

// 订单支付模型
type OrderPayment struct {
    BaseModel
    OrderID        uint             `gorm:"not null;index" json:"order_id"`
    Order          Order            `gorm:"foreignKey:OrderID" json:"order,omitempty"`
    Method         string           `gorm:"size:50" json:"method"`
    Amount         float64          `gorm:"type:decimal(10,2);not null" json:"amount"`
    Currency       string           `gorm:"size:3;default:'USD'" json:"currency"`
    Status         string           `gorm:"size:20;index" json:"status"`
    TransactionID  string           `gorm:"size:100" json:"transaction_id"`
    LastFour       string           `gorm:"size:4" json:"last_four"`
    CardType       string           `gorm:"size:20" json:"card_type"`
    ExpiresAt      *time.Time       `json:"expires_at,omitempty"`
    RefundedAmount float64          `gorm:"type:decimal(10,2);default:0" json:"refunded_amount"`
    RefundedAt     *time.Time       `json:"refunded_at,omitempty"`
    FailureReason  string           `gorm:"size:255" json:"failure_reason"`
    Metadata       JSON             `gorm:"type:jsonb" json:"metadata"`
}

// JSON字段类型
type JSON map[string]interface{}
```

### 2.2 高级模型特性
```go
package models

import (
    "context"
    "database/sql/driver"
    "encoding/json"
    "errors"
    "fmt"
    "time"

    "gorm.io/gorm"
    "gorm.io/gorm/clause"
)

// 软删除钩子
func (m *BaseModel) BeforeDelete(tx *gorm.DB) error {
    if m.DeletedAt.Valid {
        return errors.New("record already deleted")
    }
    return nil
}

// 用户模型方法
func (u *User) BeforeCreate(tx *gorm.DB) error {
    // 生成用户名（如果未提供）
    if u.Username == "" {
        u.Username = fmt.Sprintf("user_%d", time.Now().Unix())
    }
    return nil
}

func (u *User) BeforeUpdate(tx *gorm.DB) error {
    // 检查邮箱唯一性（如果邮箱被修改）
    if tx.Statement.Changed("Email") {
        var count int64
        if err := tx.Model(&User{}).Where("email = ? AND id != ?", u.Email, u.ID).Count(&count).Error; err != nil {
            return err
        }
        if count > 0 {
            return errors.New("email already exists")
        }
    }
    return nil
}

// 验证方法
func (u *User) Validate() error {
    if u.Email == "" {
        return errors.New("email is required")
    }
    if u.Password == "" {
        return errors.New("password is required")
    }
    return nil
}

// 业务方法
func (u *User) IsActive() bool {
    return u.Status == "active"
}

func (u *User) IsEmailVerified() bool {
    return u.EmailVerifiedAt != nil
}

func (u *User) GetFullName() string {
    if u.FirstName != "" && u.LastName != "" {
        return fmt.Sprintf("%s %s", u.FirstName, u.LastName)
    }
    return u.Username
}

// 产品模型方法
func (p *Product) BeforeCreate(tx *gorm.DB) error {
    // 生成slug
    if p.Slug == "" {
        p.Slug = generateSlug(p.Name)
    }
    return nil
}

func (p *Product) IsAvailable() bool {
    return p.Status == "active" && p.Stock > 0
}

func (p *Product) GetPrimaryImage() *ProductImage {
    for _, image := range p.Images {
        if image.IsPrimary {
            return &image
        }
    }
    if len(p.Images) > 0 {
        return &p.Images[0]
    }
    return nil
}

func (p *Product) GetPriceRange() (min, max float64) {
    if len(p.Variants) == 0 {
        return p.Price, p.Price
    }

    min = p.Price
    max = p.Price

    for _, variant := range p.Variants {
        if variant.Price < min {
            min = variant.Price
        }
        if variant.Price > max {
            max = variant.Price
        }
    }

    return min, max
}

// 订单模型方法
func (o *Order) BeforeCreate(tx *gorm.DB) error {
    // 生成订单号
    if o.OrderNumber == "" {
        o.OrderNumber = generateOrderNumber()
    }
    return nil
}

func (o *Order) CanBeCancelled() bool {
    return o.Status == "pending" || o.Status == "processing"
}

func (o *Order) CanBeRefunded() bool {
    return o.Status == "completed" && o.Payment.Status == "paid"
}

func (o *Order) CalculateTotal() float64 {
    var total float64
    for _, item := range o.Items {
        total += item.TotalPrice
    }

    // 添加配送费
    if o.Shipping.Cost > 0 {
        total += o.Shipping.Cost
    }

    return total
}

// 自定义JSON类型
type JSONField map[string]interface{}

func (j JSONField) Value() (driver.Value, error) {
    if j == nil {
        return nil, nil
    }
    return json.Marshal(j)
}

func (j *JSONField) Scan(value interface{}) error {
    bytes, ok := value.([]byte)
    if !ok {
        return errors.New("type assertion to []byte failed")
    }

    return json.Unmarshal(bytes, &j)
}

// 枚举类型
type OrderStatus string

const (
    OrderStatusPending   OrderStatus = "pending"
    OrderStatusProcessing OrderStatus = "processing"
    OrderStatusShipped   OrderStatus = "shipped"
    OrderStatusDelivered OrderStatus = "delivered"
    OrderStatusCancelled OrderStatus = "cancelled"
    OrderStatusRefunded  OrderStatus = "refunded"
)

func (s OrderStatus) String() string {
    return string(s)
}

func (s OrderStatus) IsValid() bool {
    switch s {
    case OrderStatusPending, OrderStatusProcessing, OrderStatusShipped,
         OrderStatusDelivered, OrderStatusCancelled, OrderStatusRefunded:
        return true
    default:
        return false
    }
}

// 查询作用域
var (
    ActiveUsers = func(db *gorm.DB) *gorm.DB {
        return db.Where("status = ?", "active")
    }

    VerifiedUsers = func(db *gorm.DB) *gorm.DB {
        return db.Where("email_verified_at IS NOT NULL")
    }

    RecentUsers = func(db *gorm.DB) *gorm.DB {
        return db.Where("created_at >= ?", time.Now().AddDate(0, 0, -30))
    }

    AvailableProducts = func(db *gorm.DB) *gorm.DB {
        return db.Where("status = ? AND stock > 0", "active")
    }

    FeaturedProducts = func(db *gorm.DB) *gorm.DB {
        return db.Where("metadata->>'featured' = 'true'")
    }

    PendingOrders = func(db *gorm.DB) *gorm.DB {
        return db.Where("status = ?", "pending")
    }

    CompletedOrders = func(db *gorm.DB) *gorm.DB {
        return db.Where("status = ?", "completed")
    }
)

// 全局钩子
func SetGlobalHooks(db *gorm.DB) {
    // 创建时间钩子
    callback := db.Callback()

    callback.Create().Before("gorm:create").Register("set_created_at", func(db *gorm.DB) {
        if db.Statement.Schema != nil {
            if field := db.Statement.Schema.LookUpField("CreatedAt"); field != nil {
                if _, ok := field.Value.(time.Time); !ok {
                    db.Statement.SetColumn("CreatedAt", time.Now())
                }
            }
        }
    })

    // 更新时间钩子
    callback.Update().Before("gorm:update").Register("set_updated_at", func(db *gorm.DB) {
        if db.Statement.Schema != nil {
            if field := db.Statement.Schema.LookUpField("UpdatedAt"); field != nil {
                if _, ok := field.Value.(time.Time); !ok {
                    db.Statement.SetColumn("UpdatedAt", time.Now())
                }
            }
        }
    })

    // 软删除钩子
    callback.Delete().Before("gorm:delete").Register("set_deleted_at", func(db *gorm.DB) {
        if db.Statement.Schema != nil {
            if field := db.Statement.Schema.LookUpField("DeletedAt"); field != nil {
                db.Statement.SetColumn("DeletedAt", time.Now())
            }
        }
    })
}

// 辅助函数
func generateSlug(name string) string {
    // 实现slug生成逻辑
    // 这里简化处理
    return name
}

func generateOrderNumber() string {
    // 实现订单号生成逻辑
    // 这里简化处理
    return fmt.Sprintf("ORD%d", time.Now().Unix())
}
```

## 3. 查询优化

### 3.1 基础查询优化
```go
package repository

import (
    "fmt"
    "strings"

    "gorm.io/gorm"
    "gorm.io/gorm/clause"
)

// 用户仓库
type UserRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
    return &UserRepository{db: db}
}

// 基础CRUD操作
func (r *UserRepository) Create(user *User) error {
    return r.db.Create(user).Error
}

func (r *UserRepository) GetByID(id uint) (*User, error) {
    var user User
    err := r.db.First(&user, id).Error
    if err != nil {
        return nil, err
    }
    return &user, nil
}

func (r *UserRepository) Update(user *User) error {
    return r.db.Save(user).Error
}

func (r *UserRepository) Delete(id uint) error {
    return r.db.Delete(&User{}, id).Error
}

// 高级查询
func (r *UserRepository) FindByEmail(email string) (*User, error) {
    var user User
    err := r.db.Where("email = ?", email).First(&user).Error
    if err != nil {
        return nil, err
    }
    return &user, nil
}

func (r *UserRepository) FindByUsername(username string) (*User, error) {
    var user User
    err := r.db.Where("username = ?", username).First(&user).Error
    if err != nil {
        return nil, err
    }
    return &user, nil
}

func (r *UserRepository) FindByIDs(ids []uint) ([]User, error) {
    var users []User
    err := r.db.Where("id IN ?", ids).Find(&users).Error
    return users, err
}

// 带条件的查询
func (r *UserRepository) FindActiveUsers(limit, offset int) ([]User, error) {
    var users []User
    err := r.db.Where("status = ?", "active").
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&users).Error
    return users, err
}

func (r *UserRepository) FindVerifiedUsers(limit, offset int) ([]User, error) {
    var users []User
    err := r.db.Where("email_verified_at IS NOT NULL").
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&users).Error
    return users, err
}

// 搜索功能
func (r *UserRepository) Search(query string, limit, offset int) ([]User, error) {
    var users []User
    searchQuery := "%" + strings.ToLower(query) + "%"

    err := r.db.Where("LOWER(username) LIKE ? OR LOWER(email) LIKE ? OR LOWER(first_name) LIKE ? OR LOWER(last_name) LIKE ?",
        searchQuery, searchQuery, searchQuery, searchQuery).
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&users).Error
    return users, err
}

// 统计查询
func (r *UserRepository) Count() (int64, error) {
    var count int64
    err := r.db.Model(&User{}).Count(&count).Error
    return count, err
}

func (r *UserRepository) CountByStatus(status string) (int64, error) {
    var count int64
    err := r.db.Model(&User{}).Where("status = ?", status).Count(&count).Error
    return count, err
}

// 预加载关联
func (r *UserRepository) GetWithProfiles(id uint) (*User, error) {
    var user User
    err := r.db.Preload("Profiles").First(&user, id).Error
    if err != nil {
        return nil, err
    }
    return &user, nil
}

func (r *UserRepository) GetWithOrders(id uint) (*User, error) {
    var user User
    err := r.db.Preload("Orders", func(db *gorm.DB) *gorm.DB {
        return db.Order("created_at DESC")
    }).First(&user, id).Error
    if err != nil {
        return nil, err
    }
    return &user, nil
}

func (r *UserRepository) GetWithAllRelations(id uint) (*User, error) {
    var user User
    err := r.db.Preload("Profiles").
        Preload("Orders", func(db *gorm.DB) *gorm.DB {
            return db.Order("created_at DESC").Limit(10)
        }).
        Preload("Orders.Items").
        Preload("Orders.Shipping").
        Preload("Orders.Payment").
        First(&user, id).Error
    if err != nil {
        return nil, err
    }
    return &user, nil
}

// 产品仓库
type ProductRepository struct {
    db *gorm.DB
}

func NewProductRepository(db *gorm.DB) *ProductRepository {
    return &ProductRepository{db: db}
}

// 产品查询
func (r *ProductRepository) GetBySlug(slug string) (*Product, error) {
    var product Product
    err := r.db.Where("slug = ?", slug).First(&product).Error
    if err != nil {
        return nil, err
    }
    return &product, nil
}

func (r *ProductRepository) GetBySKU(sku string) (*Product, error) {
    var product Product
    err := r.db.Where("sku = ?", sku).First(&product).Error
    if err != nil {
        return nil, err
    }
    return &product, nil
}

func (r *ProductRepository) FindByCategory(categoryID uint, limit, offset int) ([]Product, error) {
    var products []Product
    err := r.db.Where("category_id = ?", categoryID).
        Preload("Category").
        Preload("Images").
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&products).Error
    return products, err
}

func (r *ProductRepository) FindByTag(tagName string, limit, offset int) ([]Product, error) {
    var products []Product
    err := r.db.Joins("JOIN product_tags ON products.id = product_tags.product_id").
        Joins("JOIN tags ON tags.id = product_tags.tag_id AND tags.name = ?", tagName).
        Preload("Category").
        Preload("Images").
        Order("products.created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&products).Error
    return products, err
}

// 价格范围查询
func (r *ProductRepository) FindByPriceRange(min, max float64, limit, offset int) ([]Product, error) {
    var products []Product
    err := r.db.Where("price BETWEEN ? AND ?", min, max).
        Preload("Category").
        Preload("Images").
        Order("price ASC").
        Limit(limit).
        Offset(offset).
        Find(&products).Error
    return products, err
}

// 库存查询
func (r *ProductRepository) FindLowStockProducts(threshold int) ([]Product, error) {
    var products []Product
    err := r.db.Where("stock < ? AND stock > 0", threshold).
        Order("stock ASC").
        Find(&products).Error
    return products, err
}

func (r *ProductRepository) FindOutOfStockProducts() ([]Product, error) {
    var products []Product
    err := r.db.Where("stock <= 0").
        Order("created_at DESC").
        Find(&products).Error
    return products, err
}

// 订单仓库
type OrderRepository struct {
    db *gorm.DB
}

func NewOrderRepository(db *gorm.DB) *OrderRepository {
    return &OrderRepository{db: db}
}

// 订单查询
func (r *OrderRepository) GetByOrderNumber(orderNumber string) (*Order, error) {
    var order Order
    err := r.db.Where("order_number = ?", orderNumber).
        Preload("User").
        Preload("Items").
        Preload("Items.Product").
        Preload("Shipping").
        Preload("Payment").
        First(&order).Error
    if err != nil {
        return nil, err
    }
    return &order, nil
}

func (r *OrderRepository) FindByUserID(userID uint, limit, offset int) ([]Order, error) {
    var orders []Order
    err := r.db.Where("user_id = ?", userID).
        Preload("Items").
        Preload("Shipping").
        Preload("Payment").
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&orders).Error
    return orders, err
}

func (r *OrderRepository) FindByStatus(status string, limit, offset int) ([]Order, error) {
    var orders []Order
    err := r.db.Where("status = ?", status).
        Preload("User").
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&orders).Error
    return orders, err
}

func (r *OrderRepository) FindByDateRange(start, end time.Time, limit, offset int) ([]Order, error) {
    var orders []Order
    err := r.db.Where("created_at BETWEEN ? AND ?", start, end).
        Preload("User").
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&orders).Error
    return orders, err
}

// 复杂查询
func (r *OrderRepository) FindByComplexFilters(filters OrderFilters, limit, offset int) ([]Order, error) {
    var orders []Order
    query := r.db.Model(&Order{})

    // 应用过滤器
    if filters.Status != "" {
        query = query.Where("status = ?", filters.Status)
    }
    if filters.UserID != 0 {
        query = query.Where("user_id = ?", filters.UserID)
    }
    if !filters.StartDate.IsZero() {
        query = query.Where("created_at >= ?", filters.StartDate)
    }
    if !filters.EndDate.IsZero() {
        query = query.Where("created_at <= ?", filters.EndDate)
    }
    if filters.MinAmount > 0 {
        query = query.Where("total_amount >= ?", filters.MinAmount)
    }
    if filters.MaxAmount > 0 {
        query = query.Where("total_amount <= ?", filters.MaxAmount)
    }

    // 预加载
    query = query.Preload("User").
        Preload("Items").
        Preload("Items.Product").
        Preload("Shipping").
        Preload("Payment")

    // 排序和分页
    query = query.Order("created_at DESC").
        Limit(limit).
        Offset(offset)

    err := query.Find(&orders).Error
    return orders, err
}

// 查询过滤器
type OrderFilters struct {
    Status     string
    UserID     uint
    StartDate  time.Time
    EndDate    time.Time
    MinAmount  float64
    MaxAmount  float64
}

// 统计查询
func (r *OrderRepository) GetOrderStats() (*OrderStats, error) {
    var stats OrderStats

    // 总订单数
    if err := r.db.Model(&Order{}).Count(&stats.TotalOrders).Error; err != nil {
        return nil, err
    }

    // 总销售额
    if err := r.db.Model(&Order{}).Select("COALESCE(SUM(total_amount), 0)").Scan(&stats.TotalRevenue).Error; err != nil {
        return nil, err
    }

    // 平均订单价值
    if stats.TotalOrders > 0 {
        stats.AverageOrderValue = stats.TotalRevenue / float64(stats.TotalOrders)
    }

    // 按状态统计
    statusStats := make(map[string]int64)
    var results []struct {
        Status string
        Count  int64
    }

    if err := r.db.Model(&Order{}).Select("status, COUNT(*) as count").Group("status").Scan(&results).Error; err != nil {
        return nil, err
    }

    for _, result := range results {
        statusStats[result.Status] = result.Count
    }
    stats.StatusBreakdown = statusStats

    return &stats, nil
}

type OrderStats struct {
    TotalOrders       int64             `json:"total_orders"`
    TotalRevenue      float64           `json:"total_revenue"`
    AverageOrderValue float64           `json:"average_order_value"`
    StatusBreakdown   map[string]int64  `json:"status_breakdown"`
}

// 批量操作
func (r *UserRepository) BatchUpdateStatus(ids []uint, status string) error {
    return r.db.Model(&User{}).Where("id IN ?", ids).Update("status", status).Error
}

func (r *ProductRepository) BatchUpdateStock(updates map[uint]int) error {
    return r.db.Transaction(func(tx *gorm.DB) error {
        for productID, stock := range updates {
            if err := tx.Model(&Product{}).Where("id = ?", productID).Update("stock", stock).Error; err != nil {
                return err
            }
        }
        return nil
    })
}

// 原生SQL查询
func (r *OrderRepository) GetMonthlyRevenue(year int) ([]MonthlyRevenue, error) {
    var results []MonthlyRevenue

    query := `
        SELECT
            EXTRACT(MONTH FROM created_at) as month,
            EXTRACT(YEAR FROM created_at) as year,
            COALESCE(SUM(total_amount), 0) as revenue
        FROM orders
        WHERE EXTRACT(YEAR FROM created_at) = ?
            AND status = 'completed'
        GROUP BY EXTRACT(MONTH FROM created_at), EXTRACT(YEAR FROM created_at)
        ORDER BY month
    `

    err := r.db.Raw(query, year).Scan(&results).Error
    return results, err
}

type MonthlyRevenue struct {
    Month   int     `json:"month"`
    Year    int     `json:"year"`
    Revenue float64 `json:"revenue"`
}

// 分页查询
type Pagination struct {
    Page     int `form:"page" binding:"min=1"`
    PageSize int `form:"page_size" binding:"min=1,max=100"`
}

type PaginatedResult struct {
    Data       interface{} `json:"data"`
    Pagination PaginationMeta `json:"pagination"`
}

type PaginationMeta struct {
    CurrentPage int   `json:"current_page"`
    PageSize    int   `json:"page_size"`
    TotalItems  int64 `json:"total_items"`
    TotalPages  int   `json:"total_pages"`
    HasNext     bool  `json:"has_next"`
    HasPrev     bool  `json:"has_prev"`
}

func (p *Pagination) GetOffset() int {
    return (p.Page - 1) * p.PageSize
}

func (p *Pagination) GetLimit() int {
    return p.PageSize
}

func GetPaginationMeta(page, pageSize int, total int64) PaginationMeta {
    totalPages := int((total + int64(pageSize) - 1) / int64(pageSize))

    return PaginationMeta{
        CurrentPage: page,
        PageSize:    pageSize,
        TotalItems:  total,
        TotalPages:  totalPages,
        HasNext:     page < totalPages,
        HasPrev:     page > 1,
    }
}
```

### 3.2 性能优化查询
```go
package repository

import (
    "context"
    "fmt"
    "time"

    "gorm.io/gorm"
    "gorm.io/gorm/clause"
)

// 查询性能优化器
type QueryOptimizer struct {
    db *gorm.DB
}

func NewQueryOptimizer(db *gorm.DB) *QueryOptimizer {
    return &QueryOptimizer{db: db}
}

// 使用索引提示
func (q *QueryOptimizer) WithIndex(indexName string) *gorm.DB {
    return q.db.Clauses(clause.UseIndex{Name: indexName})
}

// 强制使用特定索引
func (q *QueryOptimizer) ForceIndex(indexName string) *gorm.DB {
    return q.db.Clauses(clause.ForceIndex{Name: indexName})
}

// 忽略索引
func (q *QueryOptimizer) IgnoreIndex(indexName string) *gorm.DB {
    return q.db.Clauses(clause.IgnoreIndex{Name: indexName})
}

// 查询超时
func (q *QueryOptimizer) WithTimeout(timeout time.Duration) *gorm.DB {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    q.db = q.db.WithContext(ctx)

    // 设置清理函数
    go func() {
        <-ctx.Done()
        cancel()
    }()

    return q.db
}

// 只读查询
func (q *QueryOptimizer) ReadOnly() *gorm.DB {
    return q.db.Raw("SET TRANSACTION READ ONLY")
}

// 锁定查询
func (q *QueryOptimizer) ForUpdate() *gorm.DB {
    return q.db.Clauses(clause.Locking{Strength: "UPDATE"})
}

func (q *QueryOptimizer) ForShare() *gorm.DB {
    return q.db.Clauses(clause.Locking{Strength: "SHARE"})
}

// 批量插入优化
func (q *QueryOptimizer) BatchInsertUsers(users []User) error {
    if len(users) == 0 {
        return nil
    }

    // 分批处理，避免单次插入过多数据
    batchSize := 1000
    for i := 0; i < len(users); i += batchSize {
        end := i + batchSize
        if end > len(users) {
            end = len(users)
        }

        batch := users[i:end]
        if err := q.db.CreateInBatches(batch, batchSize).Error; err != nil {
            return fmt.Errorf("batch insert failed at batch %d: %w", i/batchSize, err)
        }
    }

    return nil
}

// 批量更新优化
func (q *QueryOptimizer) BatchUpdateUsers(updates map[uint]map[string]interface{}) error {
    if len(updates) == 0 {
        return nil
    }

    // 使用CASE语句批量更新
    var caseClauses []string
    var ids []uint

    for id, fields := range updates {
        for field, value := range fields {
            caseClauses = append(caseClauses, fmt.Sprintf("WHEN id = %d THEN ?", id))
            ids = append(ids, id)
        }
    }

    if len(caseClauses) == 0 {
        return nil
    }

    // 构建更新语句
    query := fmt.Sprintf("UPDATE users SET %s WHERE id IN ?",
        strings.Join(caseClauses, ", "))

    return q.db.Exec(query, ids).Error
}

// 复杂查询优化
func (q *QueryOptimizer) GetProductsWithComplexFilters(filters ProductFilters) ([]Product, error) {
    var products []Product

    query := q.db.Model(&Product{})

    // 应用过滤器
    if filters.CategoryID != 0 {
        query = query.Where("category_id = ?", filters.CategoryID)
    }

    if len(filters.Statuses) > 0 {
        query = query.Where("status IN ?", filters.Statuses)
    }

    if filters.MinPrice > 0 {
        query = query.Where("price >= ?", filters.MinPrice)
    }

    if filters.MaxPrice > 0 {
        query = query.Where("price <= ?", filters.MaxPrice)
    }

    if filters.InStock {
        query = query.Where("stock > 0")
    }

    if filters.HasVariants {
        query = query.Where("EXISTS (SELECT 1 FROM product_variants WHERE product_id = products.id)")
    }

    // 搜索条件
    if filters.SearchQuery != "" {
        searchPattern := "%" + filters.SearchQuery + "%"
        query = query.Where("name ILIKE ? OR description ILIKE ?", searchPattern, searchPattern)
    }

    // 标签过滤
    if len(filters.Tags) > 0 {
        query = query.Joins("JOIN product_tags ON products.id = product_tags.product_id").
            Joins("JOIN tags ON tags.id = product_tags.tag_id").
            Where("tags.name IN ?", filters.Tags).
            Group("products.id").
            Having("COUNT(DISTINCT tags.id) = ?", len(filters.Tags))
    }

    // 排序
    switch filters.SortBy {
    case "price_asc":
        query = query.Order("price ASC")
    case "price_desc":
        query = query.Order("price DESC")
    case "name_asc":
        query = query.Order("name ASC")
    case "name_desc":
        query = query.Order("name DESC")
    case "created_desc":
        query = query.Order("created_at DESC")
    default:
        query = query.Order("created_at DESC")
    }

    // 分页
    if filters.Limit > 0 {
        query = query.Limit(filters.Limit)
    }
    if filters.Offset > 0 {
        query = query.Offset(filters.Offset)
    }

    // 预加载关联
    query = query.Preload("Category").
        Preload("Images", func(db *gorm.DB) *gorm.DB {
            return db.Where("is_primary = ?", true).Limit(1)
        }).
        Preload("Tags")

    // 执行查询
    err := query.Find(&products).Error
    return products, err
}

type ProductFilters struct {
    CategoryID  uint
    Statuses    []string
    MinPrice    float64
    MaxPrice    float64
    InStock     bool
    HasVariants bool
    SearchQuery string
    Tags        []string
    SortBy      string
    Limit       int
    Offset      int
}

// 统计查询优化
func (q *QueryOptimizer) GetAdvancedOrderStats(startDate, endDate time.Time) (*AdvancedOrderStats, error) {
    var stats AdvancedOrderStats

    // 使用单个查询获取多个统计信息
    query := `
        SELECT
            COUNT(*) as total_orders,
            COALESCE(SUM(total_amount), 0) as total_revenue,
            COALESCE(AVG(total_amount), 0) as average_order_value,
            COALESCE(MIN(total_amount), 0) as min_order_value,
            COALESCE(MAX(total_amount), 0) as max_order_value,
            COALESCE(SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END), 0) as pending_orders,
            COALESCE(SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END), 0) as completed_orders,
            COALESCE(SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END), 0) as cancelled_orders
        FROM orders
        WHERE created_at BETWEEN ? AND ?
    `

    row := q.db.Raw(query, startDate, endDate).Row()

    err := row.Scan(
        &stats.TotalOrders,
        &stats.TotalRevenue,
        &stats.AverageOrderValue,
        &stats.MinOrderValue,
        &stats.MaxOrderValue,
        &stats.PendingOrders,
        &stats.CompletedOrders,
        &stats.CancelledOrders,
    )

    if err != nil {
        return nil, err
    }

    // 获取每日统计
    dailyStats, err := q.GetDailyOrderStats(startDate, endDate)
    if err != nil {
        return nil, err
    }
    stats.DailyStats = dailyStats

    return &stats, nil
}

func (q *QueryOptimizer) GetDailyOrderStats(startDate, endDate time.Time) ([]DailyOrderStats, error) {
    var stats []DailyOrderStats

    query := `
        SELECT
            DATE(created_at) as date,
            COUNT(*) as order_count,
            COALESCE(SUM(total_amount), 0) as revenue,
            COALESCE(AVG(total_amount), 0) as avg_order_value
        FROM orders
        WHERE created_at BETWEEN ? AND ?
        GROUP BY DATE(created_at)
        ORDER BY date
    `

    err := q.db.Raw(query, startDate, endDate).Scan(&stats).Error
    return stats, err
}

type AdvancedOrderStats struct {
    TotalOrders       int64             `json:"total_orders"`
    TotalRevenue      float64           `json:"total_revenue"`
    AverageOrderValue float64           `json:"average_order_value"`
    MinOrderValue    float64           `json:"min_order_value"`
    MaxOrderValue    float64           `json:"max_order_value"`
    PendingOrders     int64             `json:"pending_orders"`
    CompletedOrders   int64             `json:"completed_orders"`
    CancelledOrders   int64             `json:"cancelled_orders"`
    DailyStats        []DailyOrderStats  `json:"daily_stats"`
}

type DailyOrderStats struct {
    Date          time.Time `json:"date"`
    OrderCount    int64     `json:"order_count"`
    Revenue       float64   `json:"revenue"`
    AvgOrderValue float64   `json:"avg_order_value"`
}

// 使用CTE优化复杂查询
func (q *QueryOptimizer) GetProductPerformanceReport() ([]ProductPerformance, error) {
    var results []ProductPerformance

    query := `
        WITH product_sales AS (
            SELECT
                p.id,
                p.name,
                p.category_id,
                COUNT(DISTINCT oi.order_id) as order_count,
                SUM(oi.quantity) as total_quantity,
                SUM(oi.total_price) as total_revenue,
                AVG(oi.unit_price) as avg_price
            FROM products p
            LEFT JOIN order_items oi ON p.id = oi.product_id
            LEFT JOIN orders o ON oi.order_id = o.id AND o.status = 'completed'
            GROUP BY p.id, p.name, p.category_id
        ),
        category_stats AS (
            SELECT
                c.id,
                c.name as category_name,
                AVG(ps.total_revenue) as avg_category_revenue
            FROM categories c
            LEFT JOIN product_sales ps ON c.id = ps.category_id
            GROUP BY c.id, c.name
        )
        SELECT
            ps.id,
            ps.name,
            ps.category_id,
            cs.category_name,
            ps.order_count,
            ps.total_quantity,
            ps.total_revenue,
            ps.avg_price,
            CASE
                WHEN ps.total_revenue > cs.avg_category_revenue THEN 'Above Average'
                WHEN ps.total_revenue < cs.avg_category_revenue THEN 'Below Average'
                ELSE 'Average'
            END as performance_level,
            ROW_NUMBER() OVER (PARTITION BY ps.category_id ORDER BY ps.total_revenue DESC) as category_rank
        FROM product_sales ps
        LEFT JOIN category_stats cs ON ps.category_id = cs.id
        ORDER BY ps.total_revenue DESC
    `

    err := q.db.Raw(query).Scan(&results).Error
    return results, err
}

type ProductPerformance struct {
    ID               uint     `json:"id"`
    Name             string   `json:"name"`
    CategoryID       uint     `json:"category_id"`
    CategoryName     string   `json:"category_name"`
    OrderCount       int64    `json:"order_count"`
    TotalQuantity    int64    `json:"total_quantity"`
    TotalRevenue     float64  `json:"total_revenue"`
    AvgPrice         float64  `json:"avg_price"`
    PerformanceLevel string   `json:"performance_level"`
    CategoryRank     int      `json:"category_rank"`
}

// 使用窗口函数
func (q *QueryOptimizer) GetUserPurchaseTrends() ([]UserPurchaseTrend, error) {
    var results []UserPurchaseTrend

    query := `
        SELECT
            u.id,
            u.username,
            u.email,
            COUNT(o.id) as total_orders,
            COALESCE(SUM(o.total_amount), 0) as total_spent,
            COALESCE(AVG(o.total_amount), 0) as avg_order_value,
            MAX(o.created_at) as last_order_date,
            ROW_NUMBER() OVER (ORDER BY COALESCE(SUM(o.total_amount), 0) DESC) as spending_rank,
            ROW_NUMBER() OVER (ORDER BY COUNT(o.id) DESC) as frequency_rank,
            CASE
                WHEN COUNT(o.id) = 0 THEN 'New'
                WHEN COUNT(o.id) >= 10 THEN 'VIP'
                WHEN COUNT(o.id) >= 5 THEN 'Regular'
                ELSE 'Occasional'
            END as customer_segment
        FROM users u
        LEFT JOIN orders o ON u.id = o.user_id AND o.status = 'completed'
        GROUP BY u.id, u.username, u.email
        ORDER BY total_spent DESC
    `

    err := q.db.Raw(query).Scan(&results).Error
    return results, err
}

type UserPurchaseTrend struct {
    ID              uint       `json:"id"`
    Username        string     `json:"username"`
    Email           string     `json:"email"`
    TotalOrders     int64      `json:"total_orders"`
    TotalSpent      float64    `json:"total_spent"`
    AvgOrderValue   float64    `json:"avg_order_value"`
    LastOrderDate   *time.Time `json:"last_order_date"`
    SpendingRank    int        `json:"spending_rank"`
    FrequencyRank   int        `json:"frequency_rank"`
    CustomerSegment string     `json:"customer_segment"`
}

// 查询计划分析
func (q *QueryOptimizer) AnalyzeQuery(query string) (*QueryPlan, error) {
    var plan QueryPlan

    explainQuery := "EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) " + query

    var result struct {
        Plan []QueryPlan `json:"Plan"`
    }

    err := q.db.Raw(explainQuery).Scan(&result).Error
    if err != nil {
        return nil, err
    }

    if len(result.Plan) > 0 {
        plan = result.Plan[0]
    }

    return &plan, nil
}

type QueryPlan struct {
    NodeTypet           string                 `json:"Node Type"`
    ParentRelationship   string                 `json:"Parent Relationship"`
    RelationName        string                 `json:"Relation Name"`
    ScanDirection       string                 `json:"Scan Direction"`
    IndexName           string                 `json:"Index Name"`
    IndexCond           string                 `json:"Index Cond"`
    RowsRemovedByFilter int64                  `json:"Rows Removed by Filter"`
    HeapFetches         int64                  `json:"Heap Fetches"`
    ActualRows          int64                  `json:"Actual Rows"`
    ActualLoops         int64                  `json:"Actual Loops"`
    ActualTotalTime     float64                `json:"Actual Total Time"`
    ActualStartupTime   float64                `json:"Actual Startup Time"`
    Plans               []QueryPlan            `json:"Plans"`
}
```

## 4. 事务处理

### 4.1 基础事务操作
```go
package transaction

import (
    "context"
    "errors"
    "fmt"
    "time"

    "gorm.io/gorm"
)

// 事务管理器
type TransactionManager struct {
    db *gorm.DB
}

func NewTransactionManager(db *gorm.DB) *TransactionManager {
    return &TransactionManager{db: db}
}

// 基础事务
func (tm *TransactionManager) Execute(fn func(tx *gorm.DB) error) error {
    return tm.db.Transaction(func(tx *gorm.DB) error {
        return fn(tx)
    })
}

// 带超时的事务
func (tm *TransactionManager) ExecuteWithTimeout(timeout time.Duration, fn func(tx *gorm.DB) error) error {
    ctx, cancel := context.WithTimeout(context.Background(), timeout)
    defer cancel()

    return tm.db.WithContext(ctx).Transaction(func(tx *gorm.DB) error {
        return fn(tx)
    })
}

// 嵌套事务
func (tm *TransactionManager) ExecuteNested(parentTx *gorm.DB, fn func(tx *gorm.DB) error) error {
    return parentTx.Transaction(func(tx *gorm.DB) error {
        return fn(tx)
    })
}

// 业务事务示例
func (tm *TransactionManager) CreateOrder(order *Order, items []OrderItem) error {
    return tm.Execute(func(tx *gorm.DB) error {
        // 创建订单
        if err := tx.Create(order).Error; err != nil {
            return fmt.Errorf("failed to create order: %w", err)
        }

        // 创建订单项
        for i := range items {
            items[i].OrderID = order.ID
            if err := tx.Create(&items[i]).Error; err != nil {
                return fmt.Errorf("failed to create order item: %w", err)
            }

            // 扣减库存
            if err := tx.Model(&Product{}).
                Where("id = ? AND stock >= ?", items[i].ProductID, items[i].Quantity).
                UpdateColumn("stock", gorm.Expr("stock - ?", items[i].Quantity)).Error; err != nil {
                return fmt.Errorf("failed to update product stock: %w", err)
            }
        }

        // 更新订单总额
        totalAmount := order.CalculateTotal()
        if err := tx.Model(order).Update("total_amount", totalAmount).Error; err != nil {
            return fmt.Errorf("failed to update order total: %w", err)
        }

        return nil
    })
}

// 用户注册事务
func (tm *TransactionManager) RegisterUser(user *User, profile *Profile) error {
    return tm.Execute(func(tx *gorm.DB) error {
        // 创建用户
        if err := tx.Create(user).Error; err != nil {
            return fmt.Errorf("failed to create user: %w", err)
        }

        // 创建用户档案
        profile.UserID = user.ID
        if err := tx.Create(profile).Error; err != nil {
            return fmt.Errorf("failed to create profile: %w", err)
        }

        // 发送欢迎邮件（异步）
        go sendWelcomeEmail(user.Email)

        return nil
    })
}

// 产品更新事务
func (tm *TransactionManager) UpdateProduct(productID uint, updates map[string]interface{}, variants []ProductVariant) error {
    return tm.Execute(func(tx *gorm.DB) error {
        // 更新产品基本信息
        if err := tx.Model(&Product{}).Where("id = ?", productID).Updates(updates).Error; err != nil {
            return fmt.Errorf("failed to update product: %w", err)
        }

        // 更新变体
        for _, variant := range variants {
            if err := tx.Model(&ProductVariant{}).
                Where("id = ? AND product_id = ?", variant.ID, productID).
                Updates(map[string]interface{}{
                    "price":     variant.Price,
                    "stock":     variant.Stock,
                    "name":      variant.Name,
                    "attributes": variant.Attributes,
                }).Error; err != nil {
                return fmt.Errorf("failed to update product variant: %w", err)
            }
        }

        return nil
    })
}

// 批量操作事务
func (tm *TransactionManager) BatchUpdateOrderStatus(orderIDs []uint, status string) error {
    return tm.Execute(func(tx *gorm.DB) error {
        // 批量更新订单状态
        if err := tx.Model(&Order{}).
            Where("id IN ?", orderIDs).
            Update("status", status).Error; err != nil {
            return fmt.Errorf("failed to batch update order status: %w", err)
        }

        // 记录状态变更历史
        for _, orderID := range orderIDs {
            history := OrderStatusHistory{
                OrderID:    orderID,
                FromStatus: "unknown", // 这里需要查询原始状态
                ToStatus:   status,
                ChangedAt:  time.Now(),
                ChangedBy:  "system",
            }

            if err := tx.Create(&history).Error; err != nil {
                return fmt.Errorf("failed to create order status history: %w", err)
            }
        }

        return nil
    })
}

// 事务隔离级别
type IsolationLevel string

const (
    IsolationLevelReadUncommitted IsolationLevel = "READ UNCOMMITTED"
    IsolationLevelReadCommitted   IsolationLevel = "READ COMMITTED"
    IsolationLevelRepeatableRead  IsolationLevel = "REPEATABLE READ"
    IsolationLevelSerializable     IsolationLevel = "SERIALIZABLE"
)

func (tm *TransactionManager) ExecuteWithIsolation(level IsolationLevel, fn func(tx *gorm.DB) error) error {
    return tm.db.Transaction(func(tx *gorm.DB) error {
        // 设置事务隔离级别
        if err := tx.Exec(fmt.Sprintf("SET TRANSACTION ISOLATION LEVEL %s", level)).Error; err != nil {
            return err
        }
        return fn(tx)
    })
}

// 事务传播行为
type PropagationBehavior int

const (
    PropagationRequired PropagationBehavior = iota
    PropagationRequiresNew
    PropagationNested
    PropagationSupports
)

func (tm *TransactionManager) ExecuteWithPropagation(behavior PropagationBehavior, fn func(tx *gorm.DB) error) error {
    switch behavior {
    case PropagationRequired:
        return tm.db.Transaction(func(tx *gorm.DB) error {
            return fn(tx)
        })
    case PropagationRequiresNew:
        newTx := tm.db.Begin()
        if err := fn(newTx); err != nil {
            newTx.Rollback()
            return err
        }
        return newTx.Commit().Error
    case PropagationNested:
        return tm.db.Transaction(func(tx *gorm.DB) error {
            return tx.Transaction(func(nestedTx *gorm.DB) error {
                return fn(nestedTx)
            })
        })
    case PropagationSupports:
        // 如果已有事务，使用现有事务；否则不使用事务
        return fn(tm.db)
    default:
        return tm.db.Transaction(func(tx *gorm.DB) error {
            return fn(tx)
        })
    }
}

// 事务模板方法
func (tm *TransactionManager) TransactionTemplate(
    ctx context.Context,
    isolationLevel IsolationLevel,
    propagationBehavior PropagationBehavior,
    timeout time.Duration,
    fn func(tx *gorm.DB) error,
) error {
    // 应用超时
    if timeout > 0 {
        var cancel context.CancelFunc
        ctx, cancel = context.WithTimeout(ctx, timeout)
        defer cancel()
    }

    // 应用传播行为
    var db *gorm.DB
    switch propagationBehavior {
    case PropagationRequiresNew:
        db = tm.db.Begin()
        defer func() {
            if r := recover(); r != nil {
                db.Rollback()
                panic(r)
            }
        }()
    case PropagationSupports:
        db = tm.db
    default:
        db = tm.db
    }

    // 应用隔离级别
    if isolationLevel != "" {
        if err := db.Exec(fmt.Sprintf("SET TRANSACTION ISOLATION LEVEL %s", isolationLevel)).Error; err != nil {
            if propagationBehavior == PropagationRequiresNew {
                db.Rollback()
            }
            return err
        }
    }

    // 执行业务逻辑
    if err := fn(db); err != nil {
        if propagationBehavior == PropagationRequiresNew {
            db.Rollback()
        }
        return err
    }

    // 提交事务
    if propagationBehavior == PropagationRequiresNew {
        return db.Commit().Error
    }

    return nil
}

// 分布式事务模拟（使用本地事务+补偿机制）
func (tm *TransactionManager) ExecuteWithCompensation(
    primaryFn func(tx *gorm.DB) error,
    compensationFn func() error,
) error {
    var tx *gorm.DB
    var err error

    // 执行主操作
    err = tm.db.Transaction(func(transaction *gorm.DB) error {
        tx = transaction
        return primaryFn(transaction)
    })

    if err != nil {
        // 执行补偿操作
        if compErr := compensationFn(); compErr != nil {
            return fmt.Errorf("primary operation failed: %v, compensation also failed: %w", err, compErr)
        }
        return err
    }

    return nil
}

// 事务监控
type TransactionMonitor struct {
    db         *gorm.DB
    metrics    *TransactionMetrics
    slowThreshold time.Duration
}

type TransactionMetrics struct {
    TotalTransactions int64         `json:"total_transactions"`
    Successful       int64         `json:"successful"`
    Failed           int64         `json:"failed"`
    AverageDuration  time.Duration `json:"average_duration"`
    SlowTransactions int64         `json:"slow_transactions"`
}

func NewTransactionMonitor(db *gorm.DB, slowThreshold time.Duration) *TransactionMonitor {
    return &TransactionMonitor{
        db:             db,
        slowThreshold:  slowThreshold,
        metrics:        &TransactionMetrics{},
    }
}

func (tm *TransactionMonitor) ExecuteMonitored(fn func(tx *gorm.DB) error) error {
    start := time.Now()

    err := tm.db.Transaction(func(tx *gorm.DB) error {
        return fn(tx)
    })

    duration := time.Since(start)

    // 更新指标
    tm.metrics.TotalTransactions++
    if err == nil {
        tm.metrics.Successful++
    } else {
        tm.metrics.Failed++
    }

    if duration > tm.slowThreshold {
        tm.metrics.SlowTransactions++
    }

    // 计算平均持续时间
    totalDuration := tm.metrics.AverageDuration*time.Duration(tm.metrics.TotalTransactions-1) + duration
    tm.metrics.AverageDuration = totalDuration / time.Duration(tm.metrics.TotalTransactions)

    return err
}

func (tm *TransactionMonitor) GetMetrics() *TransactionMetrics {
    return tm.metrics
}

// 辅助函数
func sendWelcomeEmail(email string) {
    // 实现邮件发送逻辑
    fmt.Printf("Welcome email sent to: %s\n", email)
}
```

## 5. 完整示例

### 5.1 仓储模式实现
```go
package repository

import (
    "context"
    "errors"
    "fmt"
    "time"

    "gorm.io/gorm"
)

// 仓储接口
type IUserRepository interface {
    Create(ctx context.Context, user *User) error
    GetByID(ctx context.Context, id uint) (*User, error)
    GetByEmail(ctx context.Context, email string) (*User, error)
    Update(ctx context.Context, user *User) error
    Delete(ctx context.Context, id uint) error
    FindActive(ctx context.Context, limit, offset int) ([]User, error)
    Search(ctx context.Context, query string, limit, offset int) ([]User, error)
    Count(ctx context.Context) (int64, error)
}

type IProductRepository interface {
    Create(ctx context.Context, product *Product) error
    GetByID(ctx context.Context, id uint) (*Product, error)
    GetBySlug(ctx context.Context, slug string) (*Product, error)
    Update(ctx context.Context, product *Product) error
    Delete(ctx context.Context, id uint) error
    FindByCategory(ctx context.Context, categoryID uint, limit, offset int) ([]Product, error)
    Search(ctx context.Context, filters ProductFilters) ([]Product, error)
    GetProductStats(ctx context.Context) (*ProductStats, error)
}

type IOrderRepository interface {
    Create(ctx context.Context, order *Order) error
    GetByID(ctx context.Context, id uint) (*Order, error)
    GetByOrderNumber(ctx context.Context, orderNumber string) (*Order, error)
    Update(ctx context.Context, order *Order) error
    FindByUser(ctx context.Context, userID uint, limit, offset int) ([]Order, error)
    FindByStatus(ctx context.Context, status string, limit, offset int) ([]Order, error)
    GetOrderStats(ctx context.Context) (*OrderStats, error)
}

// 用户仓储实现
type UserRepository struct {
    db *gorm.DB
}

func NewUserRepository(db *gorm.DB) *UserRepository {
    return &UserRepository{db: db}
}

func (r *UserRepository) Create(ctx context.Context, user *User) error {
    return r.db.WithContext(ctx).Create(user).Error
}

func (r *UserRepository) GetByID(ctx context.Context, id uint) (*User, error) {
    var user User
    err := r.db.WithContext(ctx).First(&user, id).Error
    if err != nil {
        return nil, err
    }
    return &user, nil
}

func (r *UserRepository) GetByEmail(ctx context.Context, email string) (*User, error) {
    var user User
    err := r.db.WithContext(ctx).Where("email = ?", email).First(&user).Error
    if err != nil {
        return nil, err
    }
    return &user, nil
}

func (r *UserRepository) Update(ctx context.Context, user *User) error {
    return r.db.WithContext(ctx).Save(user).Error
}

func (r *UserRepository) Delete(ctx context.Context, id uint) error {
    return r.db.WithContext(ctx).Delete(&User{}, id).Error
}

func (r *UserRepository) FindActive(ctx context.Context, limit, offset int) ([]User, error) {
    var users []User
    err := r.db.WithContext(ctx).
        Where("status = ?", "active").
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&users).Error
    return users, err
}

func (r *UserRepository) Search(ctx context.Context, query string, limit, offset int) ([]User, error) {
    var users []User
    searchPattern := "%" + query + "%"

    err := r.db.WithContext(ctx).
        Where("username LIKE ? OR email LIKE ? OR first_name LIKE ? OR last_name LIKE ?",
            searchPattern, searchPattern, searchPattern, searchPattern).
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&users).Error
    return users, err
}

func (r *UserRepository) Count(ctx context.Context) (int64, error) {
    var count int64
    err := r.db.WithContext(ctx).Model(&User{}).Count(&count).Error
    return count, err
}

// 产品仓储实现
type ProductRepository struct {
    db *gorm.DB
}

func NewProductRepository(db *gorm.DB) *ProductRepository {
    return &ProductRepository{db: db}
}

func (r *ProductRepository) Create(ctx context.Context, product *Product) error {
    return r.db.WithContext(ctx).Create(product).Error
}

func (r *ProductRepository) GetByID(ctx context.Context, id uint) (*Product, error) {
    var product Product
    err := r.db.WithContext(ctx).
        Preload("Category").
        Preload("Images").
        First(&product, id).Error
    if err != nil {
        return nil, err
    }
    return &product, nil
}

func (r *ProductRepository) GetBySlug(ctx context.Context, slug string) (*Product, error) {
    var product Product
    err := r.db.WithContext(ctx).
        Preload("Category").
        Preload("Images").
        Where("slug = ?", slug).
        First(&product).Error
    if err != nil {
        return nil, err
    }
    return &product, nil
}

func (r *ProductRepository) Update(ctx context.Context, product *Product) error {
    return r.db.WithContext(ctx).Save(product).Error
}

func (r *ProductRepository) Delete(ctx context.Context, id uint) error {
    return r.db.WithContext(ctx).Delete(&Product{}, id).Error
}

func (r *ProductRepository) FindByCategory(ctx context.Context, categoryID uint, limit, offset int) ([]Product, error) {
    var products []Product
    err := r.db.WithContext(ctx).
        Where("category_id = ?", categoryID).
        Preload("Category").
        Preload("Images").
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&products).Error
    return products, err
}

func (r *ProductRepository) Search(ctx context.Context, filters ProductFilters) ([]Product, error) {
    var products []Product
    query := r.db.WithContext(ctx).Model(&Product{})

    // 应用过滤器
    if filters.CategoryID != 0 {
        query = query.Where("category_id = ?", filters.CategoryID)
    }
    if filters.MinPrice > 0 {
        query = query.Where("price >= ?", filters.MinPrice)
    }
    if filters.MaxPrice > 0 {
        query = query.Where("price <= ?", filters.MaxPrice)
    }
    if filters.InStock {
        query = query.Where("stock > 0")
    }

    // 预加载
    query = query.Preload("Category").Preload("Images")

    // 排序和分页
    query = query.Order("created_at DESC")
    if filters.Limit > 0 {
        query = query.Limit(filters.Limit)
    }
    if filters.Offset > 0 {
        query = query.Offset(filters.Offset)
    }

    err := query.Find(&products).Error
    return products, err
}

func (r *ProductRepository) GetProductStats(ctx context.Context) (*ProductStats, error) {
    var stats ProductStats

    // 总产品数
    if err := r.db.WithContext(ctx).Model(&Product{}).Count(&stats.TotalProducts).Error; err != nil {
        return nil, err
    }

    // 按状态统计
    statusStats := make(map[string]int64)
    var results []struct {
        Status string
        Count  int64
    }

    if err := r.db.WithContext(ctx).Model(&Product{}).Select("status, COUNT(*) as count").Group("status").Scan(&results).Error; err != nil {
        return nil, err
    }

    for _, result := range results {
        statusStats[result.Status] = result.Count
    }
    stats.StatusBreakdown = statusStats

    // 库存统计
    var stockStats struct {
        TotalStock      int64
        LowStockCount   int64
        OutOfStockCount int64
    }

    if err := r.db.WithContext(ctx).Model(&Product{}).Select("COALESCE(SUM(stock), 0) as total_stock").Scan(&stockStats.TotalStock).Error; err != nil {
        return nil, err
    }

    if err := r.db.WithContext(ctx).Model(&Product{}).Where("stock < 10 AND stock > 0").Count(&stockStats.LowStockCount).Error; err != nil {
        return nil, err
    }

    if err := r.db.WithContext(ctx).Model(&Product{}).Where("stock <= 0").Count(&stockStats.OutOfStockCount).Error; err != nil {
        return nil, err
    }

    stats.StockStats = stockStats

    return &stats, nil
}

type ProductStats struct {
    TotalProducts   int64               `json:"total_products"`
    StatusBreakdown map[string]int64    `json:"status_breakdown"`
    StockStats      ProductStockStats    `json:"stock_stats"`
}

type ProductStockStats struct {
    TotalStock      int64 `json:"total_stock"`
    LowStockCount   int64 `json:"low_stock_count"`
    OutOfStockCount int64 `json:"out_of_stock_count"`
}

// 订单仓储实现
type OrderRepository struct {
    db *gorm.DB
}

func NewOrderRepository(db *gorm.DB) *OrderRepository {
    return &OrderRepository{db: db}
}

func (r *OrderRepository) Create(ctx context.Context, order *Order) error {
    return r.db.WithContext(ctx).Create(order).Error
}

func (r *OrderRepository) GetByID(ctx context.Context, id uint) (*Order, error) {
    var order Order
    err := r.db.WithContext(ctx).
        Preload("User").
        Preload("Items").
        Preload("Items.Product").
        Preload("Shipping").
        Preload("Payment").
        First(&order, id).Error
    if err != nil {
        return nil, err
    }
    return &order, nil
}

func (r *OrderRepository) GetByOrderNumber(ctx context.Context, orderNumber string) (*Order, error) {
    var order Order
    err := r.db.WithContext(ctx).
        Preload("User").
        Preload("Items").
        Preload("Items.Product").
        Preload("Shipping").
        Preload("Payment").
        Where("order_number = ?", orderNumber).
        First(&order).Error
    if err != nil {
        return nil, err
    }
    return &order, nil
}

func (r *OrderRepository) Update(ctx context.Context, order *Order) error {
    return r.db.WithContext(ctx).Save(order).Error
}

func (r *OrderRepository) FindByUser(ctx context.Context, userID uint, limit, offset int) ([]Order, error) {
    var orders []Order
    err := r.db.WithContext(ctx).
        Where("user_id = ?", userID).
        Preload("Items").
        Preload("Shipping").
        Preload("Payment").
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&orders).Error
    return orders, err
}

func (r *OrderRepository) FindByStatus(ctx context.Context, status string, limit, offset int) ([]Order, error) {
    var orders []Order
    err := r.db.WithContext(ctx).
        Where("status = ?", status).
        Preload("User").
        Order("created_at DESC").
        Limit(limit).
        Offset(offset).
        Find(&orders).Error
    return orders, err
}

func (r *OrderRepository) GetOrderStats(ctx context.Context) (*OrderStats, error) {
    var stats OrderStats

    // 总订单数
    if err := r.db.WithContext(ctx).Model(&Order{}).Count(&stats.TotalOrders).Error; err != nil {
        return nil, err
    }

    // 总销售额
    if err := r.db.WithContext(ctx).Model(&Order{}).Select("COALESCE(SUM(total_amount), 0)").Scan(&stats.TotalRevenue).Error; err != nil {
        return nil, err
    }

    // 平均订单价值
    if stats.TotalOrders > 0 {
        stats.AverageOrderValue = stats.TotalRevenue / float64(stats.TotalOrders)
    }

    // 按状态统计
    statusStats := make(map[string]int64)
    var results []struct {
        Status string
        Count  int64
    }

    if err := r.db.WithContext(ctx).Model(&Order{}).Select("status, COUNT(*) as count").Group("status").Scan(&results).Error; err != nil {
        return nil, err
    }

    for _, result := range results {
        statusStats[result.Status] = result.Count
    }
    stats.StatusBreakdown = statusStats

    return &stats, nil
}

// 业务服务层
type UserService struct {
    userRepo IUserRepository
    txMgr    *TransactionManager
}

func NewUserService(userRepo IUserRepository, txMgr *TransactionManager) *UserService {
    return &UserService{
        userRepo: userRepo,
        txMgr:    txMgr,
    }
}

func (s *UserService) RegisterUser(ctx context.Context, user *User, profile *Profile) error {
    return s.txMgr.Execute(func(tx *gorm.DB) error {
        // 在事务上下文中创建仓储实例
        userRepo := NewUserRepository(tx)

        // 创建用户
        if err := userRepo.Create(ctx, user); err != nil {
            return fmt.Errorf("failed to create user: %w", err)
        }

        // 创建用户档案
        profile.UserID = user.ID
        if err := userRepo.CreateProfile(ctx, profile); err != nil {
            return fmt.Errorf("failed to create profile: %w", err)
        }

        return nil
    })
}

func (s *UserService) GetUserProfile(ctx context.Context, userID uint) (*UserProfile, error) {
    user, err := s.userRepo.GetByID(ctx, userID)
    if err != nil {
        return nil, err
    }

    profile, err := s.userRepo.GetProfileByUserID(ctx, userID)
    if err != nil {
        return nil, err
    }

    return &UserProfile{
        User:    *user,
        Profile: *profile,
    }, nil
}

type UserProfile struct {
    User    User
    Profile Profile
}

// 控制器层
type UserController struct {
    userService *UserService
}

func NewUserController(userService *UserService) *UserController {
    return &UserController{userService: userService}
}

func (c *UserController) RegisterUser(ctx context.Context, req *RegisterUserRequest) (*UserResponse, error) {
    user := &User{
        Username: req.Username,
        Email:    req.Email,
        Password: req.Password,
        Status:   "active",
    }

    profile := &Profile{
        Bio:      req.Bio,
        Location: req.Location,
    }

    if err := c.userService.RegisterUser(ctx, user, profile); err != nil {
        return nil, err
    }

    return &UserResponse{
        ID:        user.ID,
        Username:  user.Username,
        Email:     user.Email,
        CreatedAt: user.CreatedAt,
    }, nil
}

type RegisterUserRequest struct {
    Username string `json:"username" binding:"required"`
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"password" binding:"required"`
    Bio      string `json:"bio"`
    Location string `json:"location"`
}

type UserResponse struct {
    ID        uint      `json:"id"`
    Username  string    `json:"username"`
    Email     string    `json:"email"`
    CreatedAt time.Time `json:"created_at"`
}
```

## 6. 最佳实践

### 6.1 性能最佳实践
- **索引优化**：为查询字段创建合适的索引
- **查询优化**：使用预加载避免N+1查询问题
- **连接池配置**：合理配置数据库连接池
- **批量操作**：使用批量插入和更新
- **分页查询**：实现高效的数据分页

### 6.2 数据完整性
- **事务处理**：使用事务保证数据一致性
- **数据验证**：在应用层和数据库层进行验证
- **外键约束**：使用外键保证引用完整性
- **唯一约束**：使用唯一约束防止重复数据
- **软删除**：使用软删除保留数据历史

### 6.3 安全性建议
- **SQL注入防护**：使用参数化查询
- **敏感数据保护**：加密存储敏感信息
- **访问控制**：实现数据库访问权限控制
- **审计日志**：记录重要操作日志
- **数据备份**：定期备份数据

### 6.4 监控和维护
- **性能监控**：监控查询性能和连接池状态
- **错误处理**：实现完善的错误处理机制
- **日志记录**：记录详细的应用日志
- **定期维护**：定期优化和清理数据
- **版本管理**：管理数据库架构版本

---

这个GORM+PostgreSQL最佳实践指南提供了完整的数据库操作解决方案，涵盖基础配置、模型设计、查询优化、事务处理等各个方面。通过这个指南，你可以构建一个高性能、高可靠的数据库访问层。