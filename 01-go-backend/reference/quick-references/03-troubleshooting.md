# Go 常见问题排查手册

> **文档简介**: Go开发中常见问题和解决方案的快速排查手册
>
> **目标读者**: Go开发者，遇到开发问题时需要快速解决方案的开发者
>
> **前置知识**: Go语言基础、Web开发基础
>
> **预计时长**: 30分钟查阅

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `reference/quick-references` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#故障排除` `#常见问题` `#调试` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 编译错误

### 语法错误
```
error: expected ';', found '}'
```
**解决方案**: 检查前面的语句是否缺少分号

### 导入错误
```
package xxx is not in GOROOT
```
**解决方案**: 
```bash
go get -u github.com/xxx/yyy
go mod tidy
```

### 类型错误
```
cannot use xxx (type T) as type U
```
**解决方案**: 检查类型匹配，使用类型转换

## 🎯 运行时错误

### 空指针引用
```
panic: runtime error: invalid memory address or nil pointer dereference
```
**解决方案**: 检查变量是否正确初始化

### 数组越界
```
panic: runtime error: index out of range
```
**解决方案**: 检查数组/切片索引范围

### 并发问题
```
fatal error: all goroutines are asleep - deadlock!
```
**解决方案**: 检查channel操作，确保有发送和接收

## 🎯 网络问题

### 端口占用
```
bind: address already in use
```
**解决方案**:
```bash
# 查找占用端口的进程
lsof -i :8080

# 杀死进程
kill -9 PID
```

### 连接数据库失败
```
dial tcp: connection refused
```
**解决方案**: 检查数据库服务是否启动，连接配置是否正确

## 🎯 性能问题

### 内存泄漏
**症状**: 内存使用持续增长
**解决方案**: 
```go
// 使用pprof分析
import _ "net/http/pprof"

func main() {
    go func() {
        log.Println(http.ListenAndServe("localhost:6060", nil))
    }()
}
```

### 响应慢
**解决方案**: 使用日志记录关键操作耗时

## 🔗 相关资源

- **深入学习**: [frameworks/01-gin-framework-basics.md](../../frameworks/01-gin-framework-basics.md)
- **相关文档**: [reference/quick-references/01-syntax-cheatsheet.md](01-syntax-cheatsheet.md)
- **调试工具**: [testing/01-unit-testing.md](../../testing/01-unit-testing.md)

---

**更新日志**: 2025年10月 - 创建常见问题排查手册
