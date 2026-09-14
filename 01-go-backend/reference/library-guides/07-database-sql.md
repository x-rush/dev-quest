# database/sql - SQL 数据库访问层

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

标准库 SQL 访问的**统一抽象层**：它不自带任何数据库驱动，只定义接口，由第三方驱动（如 `jackc/pgx` 配 `stdlib` 包装）注册接入。核心心智模型——`*sql.DB` **不是连接，而是连接池**；`Rows/Stmt` 是必须 Close 的资源句柄。

## 📖 语法 / 签名

```go
// 连接池模型：DB 是并发安全的长生命周期对象，全局一个
db, err := sql.Open("pgx", dsn) // Open 惰性：此时不建连接
db.SetMaxOpenConns(25)          // 池内最大连接数（0 = 无限制）
db.SetMaxIdleConns(25)          // 最大空闲连接数（默认 2，过小会频繁重建）
db.SetConnMaxLifetime(5 * time.Minute)  // 连接最长寿命，防代际漂移
db.SetConnMaxIdleTime(10 * time.Minute) // 空闲超时回收

// 三种执行语义
row := db.QueryRowContext(ctx, "SELECT name FROM users WHERE id=$1", id)
err := row.Scan(&name)                 // 恰一行；无行 → sql.ErrNoRows

rows, err := db.QueryContext(ctx, "SELECT id, name FROM users") // 多行
defer rows.Close()                     // 必须！否则连接被占用直至泄漏

res, err := db.ExecContext(ctx, "UPDATE ...", args...)
n, _ := res.RowsAffected()             // 影响行数；res.LastInsertId()（PG 不支持）

// 预处理语句：参数化反复执行时复用服务端计划
stmt, err := db.PrepareContext(ctx, "INSERT INTO logs(msg) VALUES($1)")
defer stmt.Close()
_, err = stmt.ExecContext(ctx, "hello")
```

**Query vs Exec**：需要返回行用 `Query*`；只关心影响（INSERT/UPDATE/DELETE/DDL）用 `Exec*`。`Scan` 的目标数量必须与列数一致，类型按驱动转换规则匹配。

**sql.Null\* 类型**：可空列映射——`sql.NullString/NullInt64/NullFloat64/NullBool/NullTime`，字段 `String`+`Valid`（其他类型同理）；`Valid=false` 表示 NULL。也可用指针字段 `*string` 或 Go 1.22+ 的 `sql.Null[T]` 泛型。

## 💡 示例

```go
package main

import (
	"context"
	"database/sql"
	"errors"
	"fmt"
)

type User struct {
	ID    int64
	Name  string
	Email sql.NullString // 可空列：NULL 不是错误而是状态
	Bio   *string        // 指针写法等价
}

var ErrNotFound = errors.New("not found")

func getUser(ctx context.Context, db *sql.DB, id int64) (*User, error) {
	const q = `SELECT id, name, email, bio FROM users WHERE id = $1`

	var u User
	err := db.QueryRowContext(ctx, q, id).Scan(&u.ID, &u.Name, &u.Email, &u.Bio)
	if errors.Is(err, sql.ErrNoRows) {
		return nil, fmt.Errorf("user %d: %w", id, ErrNotFound)
	}
	if err != nil {
		return nil, fmt.Errorf("query user %d: %w", id, err)
	}
	return &u, nil
}

func main() {
	// NullString 的读取姿势（字段由 Scan 填充，这里手动演示）
	var email sql.NullString
	email = sql.NullString{String: "a@b.c", Valid: true}
	if email.Valid {
		fmt.Println(email.String) // a@b.c
	}

	fmt.Println(errors.Is(sql.ErrNoRows, sql.ErrNoRows)) // true
	_ = context.Background()
}
```

**遍历多行的标准骨架**（生产代码直抄）：

```go
func listNames(ctx context.Context, db *sql.DB) ([]string, error) {
	rows, err := db.QueryContext(ctx, `SELECT name FROM users ORDER BY id`)
	if err != nil {
		return nil, err
	}
	defer rows.Close() // 早于遍历结束的 return 也要释放连接

	names := make([]string, 0)
	for rows.Next() {
		var n string
		if err := rows.Scan(&n); err != nil {
			return nil, err
		}
		names = append(names, n)
	}
	return names, rows.Err() // 遍历完必须检查 rows.Err（迭代中隐藏的驱动错误）
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：每次请求 `sql.Open` 新建 DB。
- ✅ **正确做法**：DB 是连接池，应用启动时 Open 一次全局复用；Open 不做网络 IO，配置错误可能延迟到首次查询才暴露，可用 `db.PingContext` 探活。
- ❌ **错误做法**：遍历 rows 中途 return 或 panic，不 Close。
- ✅ **正确做法**：拿到 rows 立即 `defer rows.Close()`；未 Close 的 Rows 会占死一条连接，池小则整库"卡死"。
- ❌ **错误做法**：循环内忘记 `rows.Err()`，把迭代中断当成"没有更多数据"。
- ✅ **正确做法**：循环结束后返回 `rows.Err()`。
- ❌ **错误做法**：用 `fmt.Sprintf` 拼接查询参数。
- ✅ **正确做法**：占位符参数化（`$1`/`?` 随驱动）防注入；`Prepare` 复用仅在高频同语句时才有收益。
- ❌ **错误做法**：NULL 列直接 Scan 到 `string`。
- ✅ **正确做法**：用 `sql.NullString`、`*string` 或 `COALESCE`；否则报 `converting NULL to string is unsupported`。
- ❌ **错误做法**：以为 `QueryRow` 找不到行返回 nil。
- ✅ **正确做法**：返回 `sql.ErrNoRows`，必须用 `errors.Is` 识别（sentinel 模式）。
- ❌ **错误做法**：PostgreSQL 里调用 `res.LastInsertId()`。
- ✅ **正确做法**：PG 用 `INSERT ... RETURNING id` + QueryRow 取回自增 ID。

## 🔗 相关条目

- 📄 **[context 包](./05-context.md)** - QueryContext 超时链路
- 📄 **[errors 标准库](./09-errors.md)** - sql.ErrNoRows 与 errors.Is
- 📄 **[nil 语义汇总](../language-concepts/15-nil-semantics.md)** - NULL 与 nil 的映射
- 📄 **[net/http 包](./03-net-http.md)** - HTTP 层持有 DB 的服务结构
- 🌐 **[pkg.go.dev/database/sql](https://pkg.go.dev/database/sql)** - 官方文档
- 🌐 **[Accessing relational databases（官方教程）](https://go.dev/doc/database)** - 官方实操指南

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
