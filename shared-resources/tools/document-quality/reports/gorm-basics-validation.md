# GORM 入门最小工程验证

**执行时间：** 2026-09-20  
**运行环境：** `golang:1.27` Docker 容器  
**锁定依赖：** `gorm.io/gorm v1.31.2`、`gorm.io/driver/sqlite v1.6.0`

## 结果

脚本从 [GORM 完整学习指南](../../../../01-go-backend/frameworks/03-gorm-orm-complete.md) 原样提取 `verify:gorm-basics-main` 与 `verify:gorm-basics-test` 围栏，写入临时 Go 模块并执行：

```bash
docker run --rm -v <temporary-directory>:/src -w /src golang:1.27 go test -mod=mod ./...
```

结果为 **PASS**。实例覆盖：

- `AutoMigrate` 建表后可以创建记录，且 `Create` 回填主键；
- `First` 能按主键读取刚创建的记录；
- 缺失行返回可由 `errors.Is(err, gorm.ErrRecordNotFound)` 识别的错误；
- 事务中第一步写入、第二步返回错误后，第一步记录不保留。

## 范围与边界

SQLite 使用 `:memory:` 临时数据库，只验证这一组 GORM API 语义。它没有验证 MySQL、PostgreSQL 或 SQL Server 的类型、DDL、锁、隔离级别、连接池、并发客户端、迁移策略或部署。机器可读结果及围栏哈希见 [gorm-basics-validation.json](gorm-basics-validation.json)，复现脚本见 [verify_gorm_basics.py](../verify_gorm_basics.py)。版本来源为 [GORM 发布页](https://github.com/go-gorm/gorm/releases) 与 [GORM SQLite 官方驱动](https://github.com/go-gorm/sqlite)。
