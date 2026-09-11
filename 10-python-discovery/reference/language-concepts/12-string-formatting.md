# 字符串格式化 — f-string 全语法与 t-string

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#f-string` `#t-string` `#格式化` `#PEP750` |
| **更新日期** | `2026年9月` |

## 📌 定义

f-string（格式化字符串字面量）是在字符串前加 `f`、内嵌 `{表达式}` 的插值语法，是现代 Python 输出格式的默认选择。t-string（模板字符串，PEP 750）与 f-string 同形但返回**模板对象**而非 `str`，插值如何渲染交由消费库决定，主打安全的延迟渲染（HTML 转义、SQL 参数化）。

## 📖 语法 / 签名

```python
f"{表达式:格式规格}"     # 格式规格 = [[填充]对齐][符号][#][0][宽度][,][.精度][类型]

# 常用格式规格
f"{value:>10}"      # 右对齐宽 10（< 左 / ^ 居中）
f"{price:.2f}"      # 两位小数
f"{n:,}"            # 千分位
f"{ratio:.1%}"      # 百分号
f"{dt:%Y-%m-%d}"    # 日期时间（strftime 规则）
f"{x=}"             # 调试语法：输出 "x=" + repr(x)
f"{obj!r}"          # 转换修饰符：!r repr / !s str / !a ascii

# t-string（模板字符串）
t"Hello {name}"     # 返回 string.templatelib.Template 对象
                    # 含 strings 与 interpolations 两部分，渲染交给库
```

## 💡 示例

```python
name, price, qty = "机械键盘", 399.5, 2

print(f"合计 {price * qty:.2f} 元")        # 合计 799.00 元
print(f"|{name:<10}|")                     # |机械键盘      |（左对齐宽 10）
print(f"|{price:>10.1f}|")                 # |     399.5|（右对齐）
print(f"{price=}, {qty=}")                 # price=399.5, qty=2
print(f"{1234567:,}")                      # 1,234,567
print(f"{0.856:.1%}")                      # 85.6%

# 3.12 起 f-string 内可复用引号、可跨行
data = {"user": {"name": "ada"}}
print(f"用户名: {data["user"]["name"]}")

# t-string：返回模板对象，不立即拼接
title = "<script>攻击</script>"
template = t"<h1>{title}</h1>"   # 由渲染库决定如何转义 title 再输出
```

## ⚠️ 常见陷阱

| 陷阱 | 说明 |
|------|------|
| 忘写 f 前缀 | 漏写 `f` 时 `{...}` 按普通文本输出 |
| 动态构建格式串当模板 | f-string 表达式内不能反引自身变量名做模板；动态模板场景交给 `string.Template` 或 t-string 生态 |
| 浮点显示精度 ≠ 精度修正 | `.2f` 只影响显示，金额运算用 `Decimal` |
| t-string 当 f-string 用 | `t"..."` 不返回 `str`，直接 print 得到的是对象描述，需渲染库处理 |
| 嵌套花括号未转义 | 字面 `{}` 需写成 `{{}}` |
| 日志滥用 f-string | `logger.info(f"{expensive()}")` 无论级别都会求值；改用 `%s` 惰性参数风格 |

## 🔗 相关条目

- 📄 **[变量与类型教程](../../basics/03-variables-types.md)** — f-string 的入门讲法
- 📄 **[数据结构速查](./03-data-structures.md)** — 字符串方法全表
- 📄 **[标准库导航](../library-guides/01-standard-library.md)** — `string`、`textwrap` 等文本工具
- 📄 **[类型注解全表](./05-typing-annotations.md)** — 模板对象的静态描述方式
