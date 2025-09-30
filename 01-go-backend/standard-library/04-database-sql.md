# Go 标准库：database/sql 包 - 从PHP视角理解

## 📚 概述

`database/sql`包是Go标准库中用于数据库操作的核心包，它提供了一套通用的数据库接口，支持多种数据库驱动。与PHP的PDO类似，Go的database/sql采用了连接池、预处理语句等现代化特性，但具有更强的类型安全性和并发处理能力。

### 🎯 学习目标
- 掌握Go数据库连接和配置
- 理解预处理语句和事务处理
- 学会数据库查询和结果处理
- 熟悉Go数据库操作与PHP的差异

## 🔄 Go vs PHP 数据库操作对比

### PHP 数据库操作
```php
<?php
// PDO连接数据库
try {
    $pdo = new PDO(
        'mysql:host=localhost;dbname=myapp;charset=utf8mb4',
        'username',
        'password',
        [
            PDO::ATTR_ERRMODE => PDO::ERRMODE_EXCEPTION,
            PDO::ATTR_DEFAULT_FETCH_MODE => PDO::FETCH_ASSOC,
            PDO::ATTR_EMULATE_PREPARES => false,
        ]
    );

    // 查询操作
    $stmt = $pdo->prepare("SELECT * FROM users WHERE age > :age");
    $stmt->execute(['age' => 18]);
    $users = $stmt->fetchAll();

    // 插入操作
    $stmt = $pdo->prepare("INSERT INTO users (name, email, age) VALUES (?, ?, ?)");
    $stmt->execute(['张三', 'zhangsan@example.com', 25]);

    // 事务处理
    $pdo->beginTransaction();
    try {
        $stmt = $pdo->prepare("UPDATE accounts SET balance = balance - :amount WHERE id = :id");
        $stmt->execute(['amount' => 100, 'id' => 1]);

        $stmt = $pdo->prepare("UPDATE accounts SET balance = balance + :amount WHERE id = :id");
        $stmt->execute(['amount' => 100, 'id' => 2]);

        $pdo->commit();
    } catch (Exception $e) {
        $pdo->rollBack();
        throw $e;
    }

} catch (PDOException $e) {
    echo "数据库错误: " . $e->getMessage();
}
```

### Go 数据库操作
```go
package main

import (
    "database/sql"
    "fmt"
    "log"

    _ "github.com/go-sql-driver/mysql"
)

type User struct {
    ID    int
    Name  string
    Email string
    Age   int
}

func main() {
    // 连接数据库
    db, err := sql.Open("mysql", "username:password@tcp(localhost:3306)/myapp?parseTime=true")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // 测试连接
    if err := db.Ping(); err != nil {
        log.Fatal(err)
    }

    // 查询操作
    rows, err := db.Query("SELECT id, name, email, age FROM users WHERE age > ?", 18)
    if err != nil {
        log.Fatal(err)
    }
    defer rows.Close()

    var users []User
    for rows.Next() {
        var user User
        if err := rows.Scan(&user.ID, &user.Name, &user.Email, &user.Age); err != nil {
            log.Fatal(err)
        }
        users = append(users, user)
    }

    // 插入操作
    result, err := db.Exec("INSERT INTO users (name, email, age) VALUES (?, ?, ?)",
        "张三", "zhangsan@example.com", 25)
    if err != nil {
        log.Fatal(err)
    }

    id, _ := result.LastInsertId()
    fmt.Printf("插入的用户ID: %d\n", id)

    // 事务处理
    tx, err := db.Begin()
    if err != nil {
        log.Fatal(err)
    }

    if _, err := tx.Exec("UPDATE accounts SET balance = balance - ? WHERE id = ?", 100, 1); err != nil {
        tx.Rollback()
        log.Fatal(err)
    }

    if _, err := tx.Exec("UPDATE accounts SET balance = balance + ? WHERE id = ?", 100, 2); err != nil {
        tx.Rollback()
        log.Fatal(err)
    }

    if err := tx.Commit(); err != nil {
        log.Fatal(err)
    }
}
```

## 📝 数据库连接和配置

### 1. 基础连接设置
```go
package main

import (
    "database/sql"
    "fmt"
    "log"
    "time"

    _ "github.com/go-sql-driver/mysql"
    _ "github.com/lib/pq"           // PostgreSQL驱动
    _ "github.com/mattn/go-sqlite3" // SQLite驱动
)

type DatabaseConfig struct {
    Driver   string
    Host     string
    Port     int
    Username string
    Password string
    Database string
    Options  map[string]string
}

func connectDB(config DatabaseConfig) (*sql.DB, error) {
    // 构建连接字符串
    var dsn string

    switch config.Driver {
    case "mysql":
        dsn = fmt.Sprintf("%s:%s@tcp(%s:%d)/%s",
            config.Username, config.Password,
            config.Host, config.Port, config.Database)

        // 添加连接选项
        if config.Options != nil {
            for key, value := range config.Options {
                dsn += fmt.Sprintf("&%s=%s", key, value)
            }
        }

    case "postgres":
        dsn = fmt.Sprintf("host=%s port=%d user=%s password=%s dbname=%s sslmode=disable",
            config.Host, config.Port, config.Username, config.Password, config.Database)

    case "sqlite3":
        dsn = config.Database
    }

    // 打开数据库连接
    db, err := sql.Open(config.Driver, dsn)
    if err != nil {
        return nil, fmt.Errorf("打开数据库连接失败: %w", err)
    }

    // 设置连接池参数
    db.SetMaxOpenConns(25)                  // 最大打开连接数
    db.SetMaxIdleConns(10)                  // 最大空闲连接数
    db.SetConnMaxLifetime(5 * time.Minute) // 连接最大生命周期
    db.SetConnMaxIdleTime(1 * time.Minute) // 空闲连接最大时间

    // 测试连接
    if err := db.Ping(); err != nil {
        return nil, fmt.Errorf("数据库连接测试失败: %w", err)
    }

    log.Printf("成功连接到 %s 数据库", config.Driver)
    return db, nil
}

func main() {
    // MySQL配置
    mysqlConfig := DatabaseConfig{
        Driver:   "mysql",
        Host:     "localhost",
        Port:     3306,
        Username: "root",
        Password: "password",
        Database: "myapp",
        Options: map[string]string{
            "parseTime":      "true",
            "charset":        "utf8mb4",
            "loc":            "Local",
            "timeout":        "10s",
            "readTimeout":    "30s",
            "writeTimeout":   "30s",
        },
    }

    db, err := connectDB(mysqlConfig)
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // 显示连接池状态
    stats := db.Stats()
    fmt.Printf("连接池状态:\n")
    fmt.Printf("  开放连接数: %d\n", stats.OpenConnections)
    fmt.Printf("  空闲连接数: %d\n", stats.Idle)
    fmt.Printf("  使用中连接数: %d\n", stats.InUse)
}
```

### 2. 连接池管理
```go
func connectionPoolManagement(db *sql.DB) {
    // 获取连接池统计信息
    stats := db.Stats()
    fmt.Printf("连接池统计:\n")
    fmt.Printf("  最大开放连接: %d\n", stats.MaxOpenConnections)
    fmt.Printf("  最大空闲连接: %d\n", stats.MaxIdleConnections)
    fmt.Printf("  等待连接数: %d\n", stats.WaitCount)
    fmt.Printf("  等待总时长: %v\n", stats.WaitDuration)
    fmt.Printf("  最大等待时长: %v\n", stats.MaxWaitDuration)
    fmt.Printf("  总连接数: %d\n", stats.OpenConnections)
    fmt.Printf("  空闲连接数: %d\n", stats.Idle)
    fmt.Printf("  使用中连接数: %d\n", stats.InUse)
    fmt.Printf("  已关闭连接数: %d\n", stats.MaxIdleClosed)
}

func optimizeConnectionPool(db *sql.DB) {
    // 根据应用负载调整连接池参数
    db.SetMaxOpenConns(50)   // 增加最大连接数
    db.SetMaxIdleConns(20)   // 增加空闲连接数
    db.SetConnMaxLifetime(30 * time.Minute) // 延长连接生命周期

    // 监控连接池使用情况
    go monitorConnectionPool(db)
}

func monitorConnectionPool(db *sql.DB) {
    ticker := time.NewTicker(30 * time.Second)
    defer ticker.Stop()

    for range ticker.C {
        stats := db.Stats()
        log.Printf("连接池监控 - 开放: %d, 空闲: %d, 使用中: %d, 等待: %d",
            stats.OpenConnections, stats.Idle, stats.InUse, stats.WaitCount)

        // 如果等待连接数过多，调整参数
        if stats.WaitCount > 100 {
            db.SetMaxOpenConns(db.Stats().MaxOpenConnections + 10)
            log.Printf("增加最大连接数到: %d", db.Stats().MaxOpenConnections)
        }
    }
}
```

## 📝 查询操作

### 1. 基础查询
```go
type Product struct {
    ID          int
    Name        string
    Price       float64
    Description string
    Category    string
    CreatedAt   time.Time
}

func basicQueries(db *sql.DB) error {
    // 查询单个字段
    var count int
    if err := db.QueryRow("SELECT COUNT(*) FROM products").Scan(&count); err != nil {
        return fmt.Errorf("查询产品总数失败: %w", err)
    }
    fmt.Printf("产品总数: %d\n", count)

    // 查询单个记录
    var product Product
    if err := db.QueryRow(
        "SELECT id, name, price, description, category, created_at FROM products WHERE id = ?",
        1,
    ).Scan(&product.ID, &product.Name, &product.Price, &product.Description, &product.Category, &product.CreatedAt); err != nil {
        if err == sql.ErrNoRows {
            fmt.Println("未找到产品")
            return nil
        }
        return fmt.Errorf("查询产品失败: %w", err)
    }
    fmt.Printf("产品详情: %+v\n", product)

    return nil
}
```

### 2. 多行查询
```go
func queryMultipleRows(db *sql.DB) ([]Product, error) {
    rows, err := db.Query(`
        SELECT id, name, price, description, category, created_at
        FROM products
        WHERE price > ?
        ORDER BY price DESC
        LIMIT 10
    `, 100)
    if err != nil {
        return nil, fmt.Errorf("查询产品列表失败: %w", err)
    }
    defer rows.Close()

    var products []Product
    for rows.Next() {
        var product Product
        if err := rows.Scan(
            &product.ID,
            &product.Name,
            &product.Price,
            &product.Description,
            &product.Category,
            &product.CreatedAt,
        ); err != nil {
            return nil, fmt.Errorf("扫描产品数据失败: %w", err)
        }
        products = append(products, product)
    }

    // 检查是否有错误
    if err := rows.Err(); err != nil {
        return nil, fmt.Errorf("遍历产品数据失败: %w", err)
    }

    return products, nil
}
```

### 3. 条件查询和参数化查询
```go
func conditionalQueries(db *sql.DB) error {
    // 使用参数化查询防止SQL注入
    category := "electronics"
    minPrice := 50.0
    maxPrice := 500.0

    // 查询指定分类和价格范围的产品
    rows, err := db.Query(`
        SELECT id, name, price, description, category, created_at
        FROM products
        WHERE category = ? AND price BETWEEN ? AND ?
        ORDER BY name ASC
    `, category, minPrice, maxPrice)
    if err != nil {
        return fmt.Errorf("条件查询失败: %w", err)
    }
    defer rows.Close()

    var products []Product
    for rows.Next() {
        var product Product
        if err := rows.Scan(&product.ID, &product.Name, &product.Price, &product.Description, &product.Category, &product.CreatedAt); err != nil {
            return fmt.Errorf("扫描产品数据失败: %w", err)
        }
        products = append(products, product)
    }

    fmt.Printf("找到 %d 个%s产品，价格范围 %.2f-%.2f\n",
        len(products), category, minPrice, maxPrice)

    return nil
}
```

## 📝 数据操作 (CRUD)

### 1. 插入数据
```go
func insertProduct(db *sql.DB, product *Product) (int64, error) {
    // 使用预处理语句插入数据
    stmt, err := db.Prepare(`
        INSERT INTO products (name, price, description, category, created_at)
        VALUES (?, ?, ?, ?, ?)
    `)
    if err != nil {
        return 0, fmt.Errorf("准备插入语句失败: %w", err)
    }
    defer stmt.Close()

    // 设置创建时间
    product.CreatedAt = time.Now()

    result, err := stmt.Exec(
        product.Name,
        product.Price,
        product.Description,
        product.Category,
        product.CreatedAt,
    )
    if err != nil {
        return 0, fmt.Errorf("插入产品失败: %w", err)
    }

    // 获取插入的ID
    id, err := result.LastInsertId()
    if err != nil {
        return 0, fmt.Errorf("获取插入ID失败: %w", err)
    }

    return id, nil
}

func batchInsertProducts(db *sql.DB, products []Product) error {
    // 使用事务批量插入
    tx, err := db.Begin()
    if err != nil {
        return fmt.Errorf("开始事务失败: %w", err)
    }

    stmt, err := tx.Prepare(`
        INSERT INTO products (name, price, description, category, created_at)
        VALUES (?, ?, ?, ?, ?)
    `)
    if err != nil {
        tx.Rollback()
        return fmt.Errorf("准备插入语句失败: %w", err)
    }
    defer stmt.Close()

    for _, product := range products {
        product.CreatedAt = time.Now()
        _, err := stmt.Exec(
            product.Name,
            product.Price,
            product.Description,
            product.Category,
            product.CreatedAt,
        )
        if err != nil {
            tx.Rollback()
            return fmt.Errorf("插入产品失败: %w", err)
        }
    }

    if err := tx.Commit(); err != nil {
        return fmt.Errorf("提交事务失败: %w", err)
    }

    return nil
}
```

### 2. 更新数据
```go
func updateProduct(db *sql.DB, id int64, updates map[string]interface{}) error {
    // 构建动态更新语句
    var setClauses []string
    var args []interface{}

    for field, value := range updates {
        setClauses = append(setClauses, field+" = ?")
        args = append(args, value)
    }

    if len(setClauses) == 0 {
        return fmt.Errorf("没有要更新的字段")
    }

    query := fmt.Sprintf("UPDATE products SET %s WHERE id = ?", strings.Join(setClauses, ", "))
    args = append(args, id)

    result, err := db.Exec(query, args...)
    if err != nil {
        return fmt.Errorf("更新产品失败: %w", err)
    }

    rowsAffected, err := result.RowsAffected()
    if err != nil {
        return fmt.Errorf("获取受影响行数失败: %w", err)
    }

    if rowsAffected == 0 {
        return fmt.Errorf("未找到要更新的产品")
    }

    fmt.Printf("成功更新 %d 个产品\n", rowsAffected)
    return nil
}

func updateProductPrice(db *sql.DB, id int64, newPrice float64) error {
    // 使用预处理语句更新价格
    result, err := db.Exec("UPDATE products SET price = ? WHERE id = ?", newPrice, id)
    if err != nil {
        return fmt.Errorf("更新产品价格失败: %w", err)
    }

    rowsAffected, err := result.RowsAffected()
    if err != nil {
        return fmt.Errorf("获取受影响行数失败: %w", err)
    }

    if rowsAffected == 0 {
        return fmt.Errorf("未找到要更新的产品")
    }

    fmt.Printf("成功更新产品价格，影响 %d 行\n", rowsAffected)
    return nil
}
```

### 3. 删除数据
```go
func deleteProduct(db *sql.DB, id int64) error {
    // 使用预处理语句删除产品
    result, err := db.Exec("DELETE FROM products WHERE id = ?", id)
    if err != nil {
        return fmt.Errorf("删除产品失败: %w", err)
    }

    rowsAffected, err := result.RowsAffected()
    if err != nil {
        return fmt.Errorf("获取受影响行数失败: %w", err)
    }

    if rowsAffected == 0 {
        return fmt.Errorf("未找到要删除的产品")
    }

    fmt.Printf("成功删除产品，影响 %d 行\n", rowsAffected)
    return nil
}

func deleteProductsByCategory(db *sql.DB, category string) error {
    // 批量删除指定分类的产品
    result, err := db.Exec("DELETE FROM products WHERE category = ?", category)
    if err != nil {
        return fmt.Errorf("批量删除产品失败: %w", err)
    }

    rowsAffected, err := result.RowsAffected()
    if err != nil {
        return fmt.Errorf("获取受影响行数失败: %w", err)
    }

    fmt.Printf("成功删除 %d 个%s产品\n", rowsAffected, category)
    return nil
}
```

## 📝 事务处理

### 1. 基础事务
```go
type Account struct {
    ID      int
    Balance float64
}

func transferMoney(db *sql.DB, fromID, toID int64, amount float64) error {
    // 开始事务
    tx, err := db.Begin()
    if err != nil {
        return fmt.Errorf("开始事务失败: %w", err)
    }

    // 检查转账金额
    if amount <= 0 {
        tx.Rollback()
        return fmt.Errorf("转账金额必须大于0")
    }

    // 检查源账户余额
    var fromBalance float64
    if err := tx.QueryRow("SELECT balance FROM accounts WHERE id = ?", fromID).Scan(&fromBalance); err != nil {
        tx.Rollback()
        return fmt.Errorf("查询源账户余额失败: %w", err)
    }

    if fromBalance < amount {
        tx.Rollback()
        return fmt.Errorf("余额不足")
    }

    // 扣减源账户余额
    if _, err := tx.Exec("UPDATE accounts SET balance = balance - ? WHERE id = ?", amount, fromID); err != nil {
        tx.Rollback()
        return fmt.Errorf("扣减源账户余额失败: %w", err)
    }

    // 增加目标账户余额
    if _, err := tx.Exec("UPDATE accounts SET balance = balance + ? WHERE id = ?", amount, toID); err != nil {
        tx.Rollback()
        return fmt.Errorf("增加目标账户余额失败: %w", err)
    }

    // 记录转账日志
    if _, err := tx.Exec(`
        INSERT INTO transfer_logs (from_account_id, to_account_id, amount, created_at)
        VALUES (?, ?, ?, ?)
    `, fromID, toID, amount, time.Now()); err != nil {
        tx.Rollback()
        return fmt.Errorf("记录转账日志失败: %w", err)
    }

    // 提交事务
    if err := tx.Commit(); err != nil {
        return fmt.Errorf("提交事务失败: %w", err)
    }

    fmt.Printf("转账成功: 从账户 %d 转账 %.2f 到账户 %d\n", fromID, amount, toID)
    return nil
}
```

### 2. 复杂事务
```go
func orderTransaction(db *sql.DB, orderID int64, userID int64, productIDs []int64) error {
    // 开始事务
    tx, err := db.Begin()
    if err != nil {
        return fmt.Errorf("开始事务失败: %w", err)
    }

    // 创建订单
    result, err := tx.Exec(`
        INSERT INTO orders (id, user_id, status, created_at)
        VALUES (?, ?, 'pending', ?)
    `, orderID, userID, time.Now())
    if err != nil {
        tx.Rollback()
        return fmt.Errorf("创建订单失败: %w", err)
    }

    // 添加订单项
    for _, productID := range productIDs {
        // 检查产品库存
        var stock int
        if err := tx.QueryRow("SELECT stock FROM products WHERE id = ?", productID).Scan(&stock); err != nil {
            tx.Rollback()
            return fmt.Errorf("查询产品库存失败: %w", err)
        }

        if stock <= 0 {
            tx.Rollback()
            return fmt.Errorf("产品 %d 库存不足", productID)
        }

        // 减少库存
        if _, err := tx.Exec("UPDATE products SET stock = stock - 1 WHERE id = ?", productID); err != nil {
            tx.Rollback()
            return fmt.Errorf("更新产品库存失败: %w", err)
        }

        // 添加订单项
        if _, err := tx.Exec(`
            INSERT INTO order_items (order_id, product_id, quantity, price)
            SELECT ?, id, 1, price FROM products WHERE id = ?
        `, orderID, productID); err != nil {
            tx.Rollback()
            return fmt.Errorf("添加订单项失败: %w", err)
        }
    }

    // 计算订单总金额
    var totalAmount float64
    if err := tx.QueryRow(`
        SELECT COALESCE(SUM(oi.price * oi.quantity), 0)
        FROM order_items oi
        WHERE oi.order_id = ?
    `, orderID).Scan(&totalAmount); err != nil {
        tx.Rollback()
        return fmt.Errorf("计算订单总金额失败: %w", err)
    }

    // 更新订单状态和金额
    if _, err := tx.Exec(`
        UPDATE orders SET total_amount = ?, status = 'completed' WHERE id = ?
    `, totalAmount, orderID); err != nil {
        tx.Rollback()
        return fmt.Errorf("更新订单状态失败: %w", err)
    }

    // 扣减用户余额
    if _, err := tx.Exec(`
        UPDATE users SET balance = balance - ? WHERE id = ?
    `, totalAmount, userID); err != nil {
        tx.Rollback()
        return fmt.Errorf("扣减用户余额失败: %w", err)
    }

    // 提交事务
    if err := tx.Commit(); err != nil {
        return fmt.Errorf("提交事务失败: %w", err)
    }

    fmt.Printf("订单 %d 处理成功，总金额: %.2f\n", orderID, totalAmount)
    return nil
}
```

## 📝 预处理语句

### 1. 预处理语句的使用
```go
func preparedStatementExample(db *sql.DB) error {
    // 准备查询语句
    stmt, err := db.Prepare(`
        SELECT id, name, price, description, category, created_at
        FROM products
        WHERE category = ? AND price > ?
        ORDER BY name
    `)
    if err != nil {
        return fmt.Errorf("准备查询语句失败: %w", err)
    }
    defer stmt.Close()

    // 多次使用同一个预处理语句
    categories := []string{"electronics", "books", "clothing"}
    for _, category := range categories {
        rows, err := stmt.Query(category, 50.0)
        if err != nil {
            return fmt.Errorf("查询产品失败: %w", err)
        }

        var products []Product
        for rows.Next() {
            var product Product
            if err := rows.Scan(&product.ID, &product.Name, &product.Price, &product.Description, &product.Category, &product.CreatedAt); err != nil {
                rows.Close()
                return fmt.Errorf("扫描产品数据失败: %w", err)
            }
            products = append(products, product)
        }
        rows.Close()

        fmt.Printf("%s分类产品数量: %d\n", category, len(products))
    }

    return nil
}
```

### 2. 预处理语句池
```go
type StatementPool struct {
    db      *sql.DB
    stmts   map[string]*sql.Stmt
    mu      sync.RWMutex
}

func NewStatementPool(db *sql.DB) *StatementPool {
    return &StatementPool{
        db:    db,
        stmts: make(map[string]*sql.Stmt),
    }
}

func (sp *StatementPool) Prepare(query string) (*sql.Stmt, error) {
    sp.mu.RLock()
    stmt, exists := sp.stmts[query]
    sp.mu.RUnlock()

    if exists {
        return stmt, nil
    }

    // 准备新语句
    newStmt, err := sp.db.Prepare(query)
    if err != nil {
        return nil, err
    }

    // 缓存语句
    sp.mu.Lock()
    sp.stmts[query] = newStmt
    sp.mu.Unlock()

    return newStmt, nil
}

func (sp *StatementPool) Close() error {
    sp.mu.Lock()
    defer sp.mu.Unlock()

    var err error
    for _, stmt := range sp.stmts {
        if closeErr := stmt.Close(); closeErr != nil {
            err = closeErr
        }
    }
    sp.stmts = make(map[string]*sql.Stmt)
    return err
}

func useStatementPool(db *sql.DB) error {
    pool := NewStatementPool(db)
    defer pool.Close()

    // 使用预处理语句池
    stmt, err := pool.Prepare("SELECT COUNT(*) FROM products WHERE category = ?")
    if err != nil {
        return fmt.Errorf("准备语句失败: %w", err)
    }

    categories := []string{"electronics", "books", "clothing"}
    for _, category := range categories {
        var count int
        if err := stmt.QueryRow(category).Scan(&count); err != nil {
            return fmt.Errorf("查询产品数量失败: %w", err)
        }
        fmt.Printf("%s分类产品数量: %d\n", category, count)
    }

    return nil
}
```

## 📝 数据库模式操作

### 1. 创建表和索引
```go
func createTables(db *sql.DB) error {
    // 创建用户表
    if _, err := db.Exec(`
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            full_name VARCHAR(100),
            age INT,
            balance DECIMAL(10,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_username (username),
            INDEX idx_email (email)
        )
    `); err != nil {
        return fmt.Errorf("创建用户表失败: %w", err)
    }

    // 创建产品表
    if _, err := db.Exec(`
        CREATE TABLE IF NOT EXISTS products (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) NOT NULL,
            price DECIMAL(10,2) NOT NULL,
            description TEXT,
            category VARCHAR(50) NOT NULL,
            stock INT DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            INDEX idx_name (name),
            INDEX idx_category (category),
            INDEX idx_price (price),
            INDEX idx_category_price (category, price)
        )
    `); err != nil {
        return fmt.Errorf("创建产品表失败: %w", err)
    }

    // 创建订单表
    if _, err := db.Exec(`
        CREATE TABLE IF NOT EXISTS orders (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            status ENUM('pending', 'completed', 'cancelled') DEFAULT 'pending',
            total_amount DECIMAL(10,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            INDEX idx_user_id (user_id),
            INDEX idx_status (status),
            INDEX idx_created_at (created_at)
        )
    `); err != nil {
        return fmt.Errorf("创建订单表失败: %w", err)
    }

    fmt.Println("数据表创建成功")
    return nil
}
```

### 2. 数据迁移
```go
func migrateDatabase(db *sql.DB) error {
    // 创建迁移表
    if _, err := db.Exec(`
        CREATE TABLE IF NOT EXISTS migrations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(100) UNIQUE NOT NULL,
            executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    `); err != nil {
        return fmt.Errorf("创建迁移表失败: %w", err)
    }

    // 定义迁移
    migrations := []struct {
        name     string
        upSQL    string
        downSQL  string
    }{
        {
            name: "create_products_table",
            upSQL: `
                CREATE TABLE IF NOT EXISTS products (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    price DECIMAL(10,2) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            `,
            downSQL: "DROP TABLE IF EXISTS products",
        },
        {
            name: "add_category_to_products",
            upSQL: "ALTER TABLE products ADD COLUMN category VARCHAR(50) DEFAULT 'general'",
            downSQL: "ALTER TABLE products DROP COLUMN category",
        },
        {
            name: "add_stock_to_products",
            upSQL: "ALTER TABLE products ADD COLUMN stock INT DEFAULT 0",
            downSQL: "ALTER TABLE products DROP COLUMN stock",
        },
    }

    // 执行迁移
    for _, migration := range migrations {
        // 检查是否已执行
        var executed bool
        if err := db.QueryRow("SELECT COUNT(*) > 0 FROM migrations WHERE name = ?", migration.name).Scan(&executed); err != nil {
            return fmt.Errorf("检查迁移状态失败: %w", err)
        }

        if executed {
            fmt.Printf("迁移 %s 已跳过\n", migration.name)
            continue
        }

        // 执行迁移
        if _, err := db.Exec(migration.upSQL); err != nil {
            return fmt.Errorf("执行迁移 %s 失败: %w", migration.name, err)
        }

        // 记录迁移
        if _, err := db.Exec("INSERT INTO migrations (name) VALUES (?)", migration.name); err != nil {
            return fmt.Errorf("记录迁移 %s 失败: %w", migration.name, err)
        }

        fmt.Printf("迁移 %s 执行成功\n", migration.name)
    }

    fmt.Println("数据库迁移完成")
    return nil
}
```

## 🧪 实践练习

### 练习1: 完整的CRUD操作
```go
package main

import (
    "database/sql"
    "fmt"
    "log"
    "time"

    _ "github.com/go-sql-driver/mysql"
)

type User struct {
    ID        int       `json:"id"`
    Username  string    `json:"username"`
    Email     string    `json:"email"`
    FullName  string    `json:"full_name"`
    Age       int       `json:"age"`
    Balance   float64   `json:"balance"`
    CreatedAt time.Time `json:"created_at"`
}

func main() {
    // 连接数据库
    db, err := sql.Open("mysql", "root:password@tcp(localhost:3306)/myapp?parseTime=true")
    if err != nil {
        log.Fatal(err)
    }
    defer db.Close()

    // 测试连接
    if err := db.Ping(); err != nil {
        log.Fatal(err)
    }

    // 创建用户表
    if err := createUserTable(db); err != nil {
        log.Fatal(err)
    }

    // 执行CRUD操作
    performCRUDOperations(db)
}

func createUserTable(db *sql.DB) error {
    query := `
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE NOT NULL,
            email VARCHAR(100) UNIQUE NOT NULL,
            full_name VARCHAR(100),
            age INT,
            balance DECIMAL(10,2) DEFAULT 0.00,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    `

    if _, err := db.Exec(query); err != nil {
        return fmt.Errorf("创建用户表失败: %w", err)
    }

    fmt.Println("用户表创建成功")
    return nil
}

func performCRUDOperations(db *sql.DB) {
    // 1. 创建用户
    user := &User{
        Username: "johndoe",
        Email:    "john@example.com",
        FullName: "John Doe",
        Age:      25,
        Balance:  1000.00,
    }

    id, err := createUser(db, user)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("创建用户成功，ID: %d\n", id)
    user.ID = id

    // 2. 读取用户
    retrievedUser, err := getUser(db, id)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("读取用户: %+v\n", retrievedUser)

    // 3. 更新用户
    user.FullName = "John Smith"
    user.Age = 26
    if err := updateUser(db, user); err != nil {
        log.Fatal(err)
    }
    fmt.Printf("更新用户成功\n")

    // 4. 删除用户
    if err := deleteUser(db, id); err != nil {
        log.Fatal(err)
    }
    fmt.Printf("删除用户成功\n")

    // 5. 列出所有用户
    users, err := listUsers(db)
    if err != nil {
        log.Fatal(err)
    }
    fmt.Printf("用户列表 (%d 个用户):\n", len(users))
    for _, u := range users {
        fmt.Printf("  - %s (%s)\n", u.Username, u.Email)
    }
}

func createUser(db *sql.DB, user *User) (int64, error) {
    result, err := db.Exec(`
        INSERT INTO users (username, email, full_name, age, balance)
        VALUES (?, ?, ?, ?, ?)
    `, user.Username, user.Email, user.FullName, user.Age, user.Balance)
    if err != nil {
        return 0, fmt.Errorf("创建用户失败: %w", err)
    }

    id, err := result.LastInsertId()
    if err != nil {
        return 0, fmt.Errorf("获取用户ID失败: %w", err)
    }

    return id, nil
}

func getUser(db *sql.DB, id int64) (*User, error) {
    var user User
    if err := db.QueryRow(`
        SELECT id, username, email, full_name, age, balance, created_at
        FROM users WHERE id = ?
    `, id).Scan(&user.ID, &user.Username, &user.Email, &user.FullName, &user.Age, &user.Balance, &user.CreatedAt); err != nil {
        if err == sql.ErrNoRows {
            return nil, fmt.Errorf("用户未找到")
        }
        return nil, fmt.Errorf("查询用户失败: %w", err)
    }

    return &user, nil
}

func updateUser(db *sql.DB, user *User) error {
    result, err := db.Exec(`
        UPDATE users SET username = ?, email = ?, full_name = ?, age = ?, balance = ?
        WHERE id = ?
    `, user.Username, user.Email, user.FullName, user.Age, user.Balance, user.ID)
    if err != nil {
        return fmt.Errorf("更新用户失败: %w", err)
    }

    rowsAffected, err := result.RowsAffected()
    if err != nil {
        return fmt.Errorf("获取受影响行数失败: %w", err)
    }

    if rowsAffected == 0 {
        return fmt.Errorf("用户未找到")
    }

    return nil
}

func deleteUser(db *sql.DB, id int64) error {
    result, err := db.Exec("DELETE FROM users WHERE id = ?", id)
    if err != nil {
        return fmt.Errorf("删除用户失败: %w", err)
    }

    rowsAffected, err := result.RowsAffected()
    if err != nil {
        return fmt.Errorf("获取受影响行数失败: %w", err)
    }

    if rowsAffected == 0 {
        return fmt.Errorf("用户未找到")
    }

    return nil
}

func listUsers(db *sql.DB) ([]User, error) {
    rows, err := db.Query(`
        SELECT id, username, email, full_name, age, balance, created_at
        FROM users ORDER BY created_at DESC
    `)
    if err != nil {
        return nil, fmt.Errorf("查询用户列表失败: %w", err)
    }
    defer rows.Close()

    var users []User
    for rows.Next() {
        var user User
        if err := rows.Scan(&user.ID, &user.Username, &user.Email, &user.FullName, &user.Age, &user.Balance, &user.CreatedAt); err != nil {
            return nil, fmt.Errorf("扫描用户数据失败: %w", err)
        }
        users = append(users, user)
    }

    if err := rows.Err(); err != nil {
        return nil, fmt.Errorf("遍历用户数据失败: %w", err)
    }

    return users, nil
}
```

## 📋 最佳实践

### 1. 连接管理最佳实践
- 使用连接池提高性能
- 设置合理的连接池参数
- 正确处理连接关闭
- 监控连接池状态

### 2. 查询优化建议
- 使用预处理语句防止SQL注入
- 合理使用索引提高查询性能
- 避免N+1查询问题
- 使用批量操作减少数据库交互

### 3. 事务处理最佳实践
- 保持事务简短
- 正确处理错误和回滚
- 避免长时间持有锁
- 使用适当的隔离级别

### 4. 安全考虑
- 始终使用参数化查询
- 验证输入数据
- 定期备份数据库
- 监控数据库性能

## 📋 检查清单

- [ ] 掌握数据库连接和配置
- [ ] 理解连接池管理
- [ ] 学会基本查询操作
- [ ] 掌握CRUD操作
- [ ] 理解事务处理
- [ ] 学会预处理语句
- [ ] 掌握数据迁移
- [ ] 理解安全最佳实践
- [ ] 能够处理错误情况
- [ ] 了解性能优化技巧

## 🚀 下一步

掌握database/sql包后，你可以继续学习：
- **ORM框架**: GORM、sqlx等
- **数据库设计**: 数据库架构和设计模式
- **缓存策略**: Redis、Memcached集成
- **微服务架构**: 分布式数据库处理

---

**学习提示**: Go的database/sql包提供了强大而灵活的数据库操作能力。相比PHP的PDO，Go的database/sql提供了更好的类型安全性和并发处理能力。通过掌握database/sql包，你可以构建高性能、可靠的数据库应用。

*最后更新: 2025年9月*