# Python 一行式速查

## 概述

高频惯用表达的一行式片段集：每个模式一行代码 + 注释示例。按场景分组，可作 REPL 伴侣。

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `10-python-discovery` |
| **象限** | 字典 |
| **难度** | ⭐ |
| **标签** | `#速查` `#一行式` `#惯用法` |
| **更新日期** | `2026年9月` |

---

## 1. 字符串

```python
s = "  Hello, World  "
s.strip().lower()                          # 清洗并归一化
" ".join(words)                            # 列表 → 字符串
s.replace("World", "Python")               # 替换
s.split(",")                               # 分割
f"{price:>10,.2f}"                         # 右对齐+千分位+两位小数
s.startswith(("http", "https"))            # 多前缀判断
text.count("\n") + 1                       # 行数
```

## 2. 列表与字典

```python
[x for x in xs if x % 2 == 0]              # 过滤
[len(x) for x in words]                    # 映射
{v: k for k, v in d.items()}               # 键值反转
sorted(xs, key=lambda x: (-x.score, x.name))   # 多级排序（负号降序）
list(dict.fromkeys(xs))                    # 保序去重
max(xs, key=len)                           # 按规则取极值
sum(x.price for x in cart)                 # 生成器求和
list(zip(names, scores))                   # 配对
a, *rest = xs                              # 解包
```

## 3. 集合运算

```python
set(a) & set(b)                            # 交集
set(a) | set(b)                            # 并集
set(a) - set(b)                            # 差集
len(set(xs)) == len(xs)                    # 是否无重复
```

## 4. 条件与逻辑

```python
grade = "A" if s >= 90 else "B"            # 三元
value = d.get("k") or "default"            # 真值兜底（区分 0/"" 用 in 判断）
any(x > 0 for x in xs)                     # 存在判断
all(x > 0 for x in xs)                     # 全称判断
value if value is not None else fallback   # 精确 None 判断
```

## 5. 文件与路径

```python
Path("f.txt").read_text(encoding="utf-8").splitlines()    # 读行列表
Path("out.txt").write_text("\n".join(lines), encoding="utf-8")
with open("f.json", encoding="utf-8") as f: json.load(f)  # 读 JSON
[line for line in open("big.log") if "ERROR" in line]     # 惰性过滤大文件
```

## 6. 常用内置组合

```python
dict(Counter(words).most_common(5))        # Top-N 计数
dict(zip(keys, values))                    # 双列表 → 字典
list(itertools.chain.from_iterable(nested)) # 二维展平
list(itertools.islice(gen, 5))             # 生成器取前 N
round(sum(xs) / len(xs), 2)                # 均值
os.cpu_count()                             # CPU 核数
```

## 7. REPL 调试

```python
print(f"{var=}")                           # 变量名+值
print(*xs, sep="\n")                       # 逐行打印
repr(obj)[:200]                            # 截断调试输出
sys.version                                # 解释器版本
```

## 8. 时间与随机

```python
datetime.now(timezone.utc).isoformat()     # UTC 时间戳（ISO 格式）
int(time.time())                           # Unix 秒
random.choice(xs); random.sample(xs, 3)    # 随机取
secrets.token_hex(16)                      # 安全令牌（勿用 random）
```

---

## 使用原则

- 一行式服务于**简单转换**；两步以上逻辑写正常函数
- REPL 里先试一行式，成型后落盘
- 生成器表达式优先于建中间列表

---

## 🔗 相关文档

- 📄 **[控制流与推导式](../../basics/05-control-flow.md)** — 推导式的教程讲解
- 📄 **[数据结构速查](../language-concepts/03-data-structures.md)** — 一行式背后的容器操作
- 📄 **[标准库导航](../library-guides/01-standard-library.md)** — itertools/collections 全貌
