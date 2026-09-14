# encoding/json - JSON 序列化与反序列化

> **模块**: `01-go-backend` | **类型**: 字典条目（无难度门槛，支持任意跳入查阅）

## 📌 定义

标准库 JSON 编解码包：`Marshal` 把 Go 值编码为 JSON 字节流，`Unmarshal` 反向填充。心智模型——**struct 字段即 schema，tag 即字段名映射**；编码只处理**导出字段**（大写开头），这是绝大多数"字段丢了"问题的根源。

## 📖 语法 / 签名

```go
func Marshal(v any) ([]byte, error)
func Unmarshal(data []byte, v any) error     // v 必须传指针
func (d *Decoder) Decode(v any) error        // 流式解码（http body 等）
func (e *Encoder) Encode(v any) error        // 流式编码
```

**struct tag 完整语义**（本机 go1.25 实测行为）：

| tag | 效果 |
|-----|------|
| `json:"name"` | 字段映射为 `"name"` |
| `json:"name,omitempty"` | 零值时省略（空串/0/false/nil slice/map/指针） |
| `json:"-"` | 完全忽略该字段（编码解码都不参与） |
| `json:"-,"` | 字段名就是字面量 `"-"`（注意与上一行的区别） |
| `json:"name,string"` | 数字/布尔在 JSON 里以**字符串**形式编解码（`"42"` ↔ 42） |
| 无 tag | 默认用**原字段名**（保持大小写），如 `UserName` → `"UserName"` |

**大小写匹配规则**：解码时 tag 名或字段名**大小写不敏感**地匹配（`"username"` 能填进 `UserName`）；但编码输出严格使用 tag 名/字段原名的确切拼写。要精确控制就用显式 tag。

**nil slice vs 空 slice**：`var s []int` 编码为 `null`，`s := []int{}` 编码为 `[]`。对外 API 想稳定输出 `[]`，初始化用 `make([]T, 0)` 或自定义 MarshalJSON。

**大数字精度**：`int64` 超出 float64 精度（如雪花 ID）时，用 `Decoder.UseNumber()`——数字解码为 `json.Number`（string 底座）而不是 float64。

## 💡 示例

```go
package main

import (
	"encoding/json"
	"fmt"
	"strings"
)

type User struct {
	Name     string   `json:"name"`
	Email    string   `json:"email,omitempty"` // 空串省略
	Age      int      `json:"age,string"`      // JSON 里是 "18" 字符串
	password string   // 未导出：永不编码
	Internal string   `json:"-"`
	Profile  *Profile `json:"profile,omitempty"` // nil 指针省略
}

type Profile struct{ City string }

func main() {
	u := User{Name: "alice", Age: 18}
	b, _ := json.Marshal(u)
	fmt.Println(string(b))
	// {"name":"alice","age":"18"}（email/profile 省略，password/Internal 不出现）

	// 解码：大小写不敏感匹配
	var v User
	json.Unmarshal([]byte(`{"NAME":"bob","AGE":"20"}`), &v)
	fmt.Println(v.Name, v.Age) // bob 20

	// UseNumber：保留大整数精度
	dec := json.NewDecoder(strings.NewReader(`{"id":12345678901234567890}`))
	dec.UseNumber()
	var m map[string]any
	dec.Decode(&m)
	fmt.Println(m["id"], fmt.Sprintf("%T", m["id"])) // 12345678901234567890 json.Number
}
```

**自定义编解码接口**（Marshaler/Unmarshaler，见接口条目的隐式实现）：

```go
type Duration struct{ Seconds int }

func (d Duration) MarshalJSON() ([]byte, error) {
	return []byte(fmt.Sprintf(`"%ds"`, d.Seconds)), nil // 输出 "30s"
}

func (d *Duration) UnmarshalJSON(data []byte) error {
	var s string
	if err := json.Unmarshal(data, &s); err != nil {
		return err
	}
	var n int
	if _, err := fmt.Sscanf(s, "%ds", &n); err != nil {
		return err
	}
	d.Seconds = n
	return nil
}
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：期望小写字段被编码。
- ✅ **正确做法**：只有导出字段（大写开头）参与编解码；私有字段配 tag 也无效。
- ❌ **错误做法**：`var s []T` 当作"空数组"直接返回给前端。
- ✅ **正确做法**：nil slice 编码为 `null`、空 slice 为 `[]`；统一初始化 `make([]T, 0)` 或文档约定 null。
- ❌ **错误做法**：`Unmarshal(data, v)` 忘记传 `&v`。
- ✅ **正确做法**：必须传指针，否则值无处写入并返回 `json: Unmarshal(non-pointer ...)` 错误。
- ❌ **错误做法**：把超长 JSON 数字解到 `float64`，再转 int64 丢精度。
- ✅ **正确做法**：ID 类字段声明为 `string` tag 或用 `Decoder.UseNumber()`。
- ❌ **错误做法**：`omitempty` 期望 bool false / 结构体零值被省略。
- ✅ **正确做法**：omitempty 只认"空值"（0/""/false/nil 指针/nil 或空 slice/map）；结构体本身永远输出，想省略得用指针字段。
- ❌ **错误做法**：在 UnmarshalJSON 里调用 json.Unmarshal 解同一类型造成无限递归。
- ✅ **正确做法**：先定义类型别名剥掉方法 `type alias T` 再解码。
- ❌ **错误做法**：流式 body 先 io.ReadAll 再 Unmarshal。
- ✅ **正确做法**：`json.NewDecoder(r.Body).Decode(&v)` 一次完成，且支持 UseNumber/DisallowUnknownFields 等解码选项。

## 🔗 相关条目

- 📄 **[net/http 包](./03-net-http.md)** - JSON API 服务的标准组合
- 📄 **[接口语义](../language-concepts/13-interface-semantics.md)** - Marshaler 接口的隐式实现
- 📄 **[nil 语义汇总](../language-concepts/15-nil-semantics.md)** - nil slice 序列化差异
- 📄 **[time 包](./08-time.md)** - time.Time 的 RFC3339 JSON 格式
- 🌐 **[pkg.go.dev/encoding/json](https://pkg.go.dev/encoding/json)** - 官方文档（含 "JSON and Go" 文章链接）

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*
