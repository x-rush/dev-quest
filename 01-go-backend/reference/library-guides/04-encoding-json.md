# encoding/json - JSON 序列化与反序列化

> **模块**: `01-go-backend` | **类型**: 字典条目（可独立查阅，按主题准备前置知识，支持任意跳入查阅）

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
| `json:"name,omitempty"` | 空值时省略（空串、0、false、nil 指针，以及长度为 0 的 slice/map/数组）；普通结构体零值不在此列 |
| `json:"-"` | 完全忽略该字段（编码解码都不参与） |
| `json:"-,"` | 字段名就是字面量 `"-"`（注意与上一行的区别） |
| `json:"name,string"` | 数字/布尔在 JSON 里以**字符串**形式编解码（`"42"` ↔ 42） |
| 无 tag | 默认用**原字段名**（保持大小写），如 `UserName` → `"UserName"` |

**大小写匹配规则**：解码时 tag 名或字段名**大小写不敏感**地匹配（`"username"` 能填进 `UserName`）；但编码输出严格使用 tag 名/字段原名的确切拼写。要精确控制就用显式 tag。

**nil slice vs 空 slice**：`var s []int` 编码为 `null`，`s := []int{}` 编码为 `[]`。对外 API 想稳定输出 `[]`，初始化用 `make([]T, 0)` 或自定义 MarshalJSON。

**大数字精度**：解入 any 时数字默认成为 float64；UseNumber 将这些数字保留为 json.Number。直接解入 int64 字段不会先经过 float64，但仍有 int64 范围限制。Number 保留文本不代表通过数值范围校验，调用 Int64 等转换方法仍要检查错误。

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

**自定义编解码接口**（Marshaler/Unmarshaler）：以下是独立片段，需导入 encoding/json、fmt、strings、strconv；接受非负整秒，例如 "30s"，拒绝尾随字符。

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
	if !strings.HasSuffix(s, "s") { return fmt.Errorf("duration must end in s") }
	n, err := strconv.Atoi(strings.TrimSuffix(s, "s"))
	if err != nil { return err }
	if n < 0 { return fmt.Errorf("duration must be non-negative") }
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
- ❌ **错误做法**：以为 `omitempty` 会省略所有类型的零值，包括普通结构体。
- ✅ **正确做法**：omitempty 只认"空值"（0/""/false/nil 指针/nil 或空 slice/map）；结构体本身永远输出，想省略得用指针字段。
- ❌ **错误做法**：在 UnmarshalJSON 里调用 json.Unmarshal 解同一类型造成无限递归。
- ✅ **正确做法**：定义一个不继承原类型方法的新类型 `type plain T` 再解码；这不是 `type plain = T` 类型别名，后者仍保留方法。
- ❌ **错误做法**：流式 body 先 io.ReadAll 再 Unmarshal。
- ✅ **正确做法**：`json.NewDecoder(r.Body).Decode(&v)` 一次完成，且支持 UseNumber/DisallowUnknownFields 等解码选项。

<!-- full-library-explanation -->
## 解码成功之后，还要验证什么

前置是结构体、接口和错误返回值。JSON 解码解决的是文本到 Go 值的转换，不自动证明订单金额为正、用户有权限或者请求只包含一个对象。对 HTTP 输入先限制请求体大小，再 Decode、检查业务约束；若协议只允许一个 JSON 值，还要再 Decode 一次并要求返回 io.EOF，拒绝 `{} {}` 这样的尾随数据。DisallowUnknownFields 可拒绝未知字段，但不等于检查所有重复键与业务规则。

对更新接口尤其要区分“未提供”“提供零值”和“提供 null”。普通 bool 的零值 false 无法单独表达这些状态；*bool 可以区分有值与 nil，但通常仍不能区分未提供与 null，需要额外的存在性记录或自定义解码。编码端的 omitempty 也不会替你设计更新语义。

练习：为一个只接收 age 的请求列出 `{"age":0}`、`{}`、`{"age":-1}`、`{"age":"18"}` 四种输入。若 age 为 int 且没有 string tag，最后一种应产生类型错误；前三种都可能解码成功，其中负数必须由业务校验拒绝。再把 age 换成 *int，观察缺失字段与显式 0 的区别。验收时同时断言错误和结果，不要使用部分解码后的值继续执行写操作。

## 🔗 相关条目

- 📄 **[net/http 包](./03-net-http.md)** - JSON API 服务的标准组合
- 📄 **[接口语义](../language-concepts/13-interface-semantics.md)** - Marshaler 接口的隐式实现
- 📄 **[nil 语义汇总](../language-concepts/15-nil-semantics.md)** - nil slice 序列化差异
- 📄 **[time 包](./08-time.md)** - time.Time 的 RFC3339 JSON 格式
- 🌐 **[pkg.go.dev/encoding/json](https://pkg.go.dev/encoding/json)** - 官方文档（含 "JSON and Go" 文章链接）

---

*最后更新: 2026年9月 | 本条目为模块知识字典的一部分，概念完整解释以此处为单一事实来源*


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
