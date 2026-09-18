# Go 常见问题排查手册

> **文档简介**: Go开发中常见问题和解决方案的快速排查手册
>
> **目标读者**: Go开发者，遇到开发问题时需要快速解决方案的开发者
>
> **前置知识**: Go语言基础、Web开发基础
>
> **预计时长**: 30分钟查阅

<details>
<summary>文档信息（用途、难度与维护记录）</summary>

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `reference/quick-references` |
| **难度** | ⭐⭐ (2/5) |
| **标签** | `#故障排除` `#常见问题` `#调试` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

</details>

## 🎯 编译错误

### 语法错误
```
error: expected ';', found '}'
```
**解决方案**: 从第一条编译错误及上一行检查括号、逗号、换行与语法结构；Go 大部分分号由词法规则自动插入，不要机械补分号。

### 导入错误
```
package xxx is not in GOROOT
```
**解决方案**: 
```bash
go env GOMOD # 先确认当前模块位置
go list ./... # 核对导入路径、包名与模块布局
# 仅确实缺少第三方依赖时，按项目约定添加该模块并整理依赖
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

# 确认是自己启动且可停止的服务后，优先通过终端 Ctrl+C 或服务管理器正常停止
# 也可以为本次练习选择另一个未占用端口
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

<!-- full-library-explanation -->
## 把现象变成可以排除的假设

前置是编译、运行和请求处理的区别。先保存完整错误、Go 版本、触发命令和最小输入，再定位失败属于哪一层。编译错误优先修第一条真实错误；后续报错可能只是连带结果。Go 通常自动插入分号，expected 之类错误也可能来自上一行括号、逗号或多行参数列表，不应机械补分号。

连接失败要按阶段区分：connection refused 通常是目标端口未监听或连接被拒绝；超时可能来自路由、防火墙、池等待或服务过载；认证失败说明已走到协议交互阶段。对同一目标先检查地址解析、监听端口和应用日志，再使用带短超时的最小连接测试。切换依赖版本不能修复地址填错，盲目重试还会掩盖原始错误。

练习：在本地分别使用错误端口、错误数据库凭据和已取消 context，记录三个不同错误并解释发生阶段。出现内存上涨时，对比同等负载和空闲后的 heap、goroutine 数量；缓存预热与真正泄漏不能只凭一张内存曲线区分。修复后重跑最小复现并增加相应回归用例，保留证据说明哪个假设被验证。

## 🔗 相关资源

- **深入学习**: [frameworks/01-gin-framework-basics.md](../../frameworks/01-gin-framework-basics.md)
- **相关文档**: [reference/quick-references/01-syntax-cheatsheet.md](01-syntax-cheatsheet.md)
- **调试工具**: [testing/01-unit-testing.md](../../testing/01-unit-testing.md)

---

**更新日志**: 2026年9月 - 创建常见问题排查手册


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
