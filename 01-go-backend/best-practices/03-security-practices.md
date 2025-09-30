# Go安全实践指南 - 构建安全可靠的应用程序

## 🛡️ 安全开发概述

Go语言以其简洁的语法、强大的标准库和出色的性能表现，成为构建安全可靠应用程序的理想选择。本文档将深入探讨Go开发中的安全最佳实践，帮助开发者构建抵御现代网络威胁的应用程序。

### 安全开发的重要性
- **数据保护**: 保护用户隐私和敏感信息
- **业务连续性**: 防止安全事件导致服务中断
- **合规要求**: 满足GDPR、PCI DSS等法规要求
- **品牌声誉**: 维护用户信任和品牌形象
- **法律风险**: 避免数据泄露的法律责任

### Go安全优势
- **内存安全**: 垃圾回收避免内存泄漏和缓冲区溢出
- **强类型系统**: 编译时类型检查减少运行时错误
- **标准库安全**: crypto包提供经过验证的加密实现
- **并发安全**: 内置的并发模型减少竞态条件
- **静态链接**: 减少动态库依赖攻击面

---

## 🔐 认证与授权

### 1. 密码安全

#### 密码哈希最佳实践
```go
package auth

import (
	"crypto/rand"
	"crypto/subtle"
	"encoding/base64"
	"errors"
	"fmt"
	"time"

	"golang.org/x/crypto/argon2"
)

type Argon2Params struct {
	Memory      uint32
	Iterations  uint32
	Parallelism uint8
	SaltLength  uint32
	KeyLength   uint32
}

var DefaultParams = Argon2Params{
	Memory:      64 * 1024,  // 64MB
	Iterations:  3,
	Parallelism: 4,
	SaltLength:  16,
	KeyLength:   32,
}

func HashPassword(password string, p *Argon2Params) (string, error) {
	if password == "" {
		return "", errors.New("密码不能为空")
	}

	// 生成随机盐值
	salt := make([]byte, p.SaltLength)
	if _, err := rand.Read(salt); err != nil {
		return "", fmt.Errorf("生成盐值失败: %w", err)
	}

	// 使用Argon2id哈希密码
	hash := argon2.IDKey(
		[]byte(password),
		salt,
		p.Iterations,
		p.Memory,
		p.Parallelism,
		p.KeyLength,
	)

	// 返回编码后的哈希值和参数
	encodedHash := fmt.Sprintf(
		"$argon2id$v=%d$m=%d,t=%d,p=%d$%s$%s",
		argon2.Version,
		p.Memory,
		p.Iterations,
		p.Parallelism,
		base64.RawStdEncoding.EncodeToString(salt),
		base64.RawStdEncoding.EncodeToString(hash),
	)

	return encodedHash, nil
}

func VerifyPassword(password, encodedHash string) (bool, error) {
	// 解析编码的哈希值
	p, salt, hash, err := parseHash(encodedHash)
	if err != nil {
		return false, err
	}

	// 计算输入密码的哈希值
	inputHash := argon2.IDKey(
		[]byte(password),
		salt,
		p.Iterations,
		p.Memory,
		p.Parallelism,
		p.KeyLength,
	)

	// 使用恒定时间比较防止时序攻击
	if subtle.ConstantTimeCompare(hash, inputHash) == 1 {
		return true, nil
	}

	return false, nil
}

func parseHash(encodedHash string) (p *Argon2Params, salt, hash []byte, err error) {
	p = &DefaultParams

	// 解析哈希字符串
	_, err = fmt.Sscanf(
		encodedHash,
		"$argon2id$v=%d$m=%d,t=%d,p=%d$%s$%s",
		&p.Version,
		&p.Memory,
		&p.Iterations,
		&p.Parallelism,
		&salt,
		&hash,
	)
	if err != nil {
		return nil, nil, nil, err
	}

	// 解码Base64
	salt, err = base64.RawStdEncoding.DecodeString(string(salt))
	if err != nil {
		return nil, nil, nil, err
	}

	hash, err = base64.RawStdEncoding.DecodeString(string(hash))
	if err != nil {
		return nil, nil, nil, err
	}

	return p, salt, hash, nil
}
```

#### 密码策略验证
```go
package auth

import (
	"regexp"
	"unicode"
)

type PasswordPolicy struct {
	MinLength     int
	MaxLength     int
	RequireUpper  bool
	RequireLower  bool
	RequireNumber bool
	RequireSpecial bool
	ForbiddenPatterns []string
}

var DefaultPasswordPolicy = PasswordPolicy{
	MinLength:     12,
	MaxLength:     128,
	RequireUpper:  true,
	RequireLower:  true,
	RequireNumber: true,
	RequireSpecial: true,
	ForbiddenPatterns: []string{
		"password", "123456", "qwerty", "abc123",
		"admin", "root", "user", "test",
	},
}

func ValidatePassword(password string, policy PasswordPolicy) []error {
	var errors []error

	// 检查长度
	if len(password) < policy.MinLength {
		errors = append(errors, fmt.Errorf("密码长度不能少于%d位", policy.MinLength))
	}
	if policy.MaxLength > 0 && len(password) > policy.MaxLength {
		errors = append(errors, fmt.Errorf("密码长度不能超过%d位", policy.MaxLength))
	}

	// 检查字符类型
	var hasUpper, hasLower, hasNumber, hasSpecial bool
	for _, r := range password {
		switch {
		case unicode.IsUpper(r):
			hasUpper = true
		case unicode.IsLower(r):
			hasLower = true
		case unicode.IsNumber(r):
			hasNumber = true
		case unicode.IsPunct(r) || unicode.IsSymbol(r):
			hasSpecial = true
		}
	}

	if policy.RequireUpper && !hasUpper {
		errors = append(errors, fmt.Errorf("密码必须包含大写字母"))
	}
	if policy.RequireLower && !hasLower {
		errors = append(errors, fmt.Errorf("密码必须包含小写字母"))
	}
	if policy.RequireNumber && !hasNumber {
		errors = append(errors, fmt.Errorf("密码必须包含数字"))
	}
	if policy.RequireSpecial && !hasSpecial {
		errors = append(errors, fmt.Errorf("密码必须包含特殊字符"))
	}

	// 检查禁止模式
	for _, pattern := range policy.ForbiddenPatterns {
		if matched, _ := regexp.MatchString(pattern, password); matched {
			errors = append(errors, fmt.Errorf("密码包含禁止使用的模式"))
			break
		}
	}

	// 检查连续重复字符
	if hasConsecutiveChars(password, 3) {
		errors = append(errors, fmt.Errorf("密码不能包含连续重复字符"))
	}

	return errors
}

func hasConsecutiveChars(s string, maxCount int) bool {
	if len(s) < maxCount {
		return false
	}

	for i := 0; i <= len(s)-maxCount; i++ {
		allSame := true
		for j := 1; j < maxCount; j++ {
			if s[i] != s[i+j] {
				allSame = false
				break
			}
		}
		if allSame {
			return true
		}
	}

	return false
}
```

### 2. JWT认证

#### JWT生成与验证
```go
package auth

import (
	"crypto/rsa"
	"fmt"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

type JWTManager struct {
	privateKey *rsa.PrivateKey
	publicKey  *rsa.PublicKey
	issuer     string
	expiration time.Duration
}

type Claims struct {
	UserID   string                 `json:"user_id"`
	Username string                 `json:"username"`
	Email    string                 `json:"email"`
	Role     string                 `json:"role"`
	Metadata map[string]interface{} `json:"metadata,omitempty"`
	jwt.RegisteredClaims
}

func NewJWTManager(privateKey *rsa.PrivateKey, publicKey *rsa.PublicKey, issuer string, expiration time.Duration) *JWTManager {
	return &JWTManager{
		privateKey: privateKey,
		publicKey:  publicKey,
		issuer:     issuer,
		expiration: expiration,
	}
}

func (m *JWTManager) GenerateToken(userID, username, email, role string, metadata map[string]interface{}) (string, error) {
	now := time.Now()
	claims := &Claims{
		UserID:   userID,
		Username: username,
		Email:    email,
		Role:     role,
		Metadata: metadata,
		RegisteredClaims: jwt.RegisteredClaims{
			Issuer:    m.issuer,
			Subject:   userID,
			ExpiresAt: jwt.NewNumericDate(now.Add(m.expiration)),
			NotBefore: jwt.NewNumericDate(now),
			IssuedAt:  jwt.NewNumericDate(now),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodRS256, claims)
	return token.SignedString(m.privateKey)
}

func (m *JWTManager) VerifyToken(tokenString string) (*Claims, error) {
	token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
		// 验证签名算法
		if _, ok := token.Method.(*jwt.SigningMethodRSA); !ok {
			return nil, fmt.Errorf("意外的签名方法: %v", token.Header["alg"])
		}
		return m.publicKey, nil
	})

	if err != nil {
		return nil, fmt.Errorf("验证token失败: %w", err)
	}

	claims, ok := token.Claims.(*Claims)
	if !ok || !token.Valid {
		return nil, fmt.Errorf("无效的token声明")
	}

	return claims, nil
}

func (m *JWTManager) RefreshToken(tokenString string) (string, error) {
	claims, err := m.VerifyToken(tokenString)
	if err != nil {
		return "", err
	}

	// 检查token是否即将过期（剩余时间少于1小时）
	if time.Until(claims.ExpiresAt.Time) > time.Hour {
		return "", fmt.Errorf("token不需要刷新")
	}

	// 生成新token
	return m.GenerateToken(
		claims.UserID,
		claims.Username,
		claims.Email,
		claims.Role,
		claims.Metadata,
	)
}
```

#### RBAC权限控制
```go
package auth

import (
	"errors"
	"fmt"
	"strings"
)

type Permission struct {
	Resource string
	Action   string
}

type Role struct {
	Name         string
	Permissions  []Permission
	InheritsFrom []string
}

type RBACManager struct {
	roles        map[string]*Role
	roleHierarchy map[string][]string
}

func NewRBACManager() *RBACManager {
	return &RBACManager{
		roles:        make(map[string]*Role),
		roleHierarchy: make(map[string][]string),
	}
}

func (m *RBACManager) AddRole(role *Role) error {
	if _, exists := m.roles[role.Name]; exists {
		return fmt.Errorf("角色已存在: %s", role.Name)
	}

	m.roles[role.Name] = role
	m.roleHierarchy[role.Name] = role.InheritsFrom

	return nil
}

func (m *RBACManager) HasPermission(roleName string, permission Permission) bool {
	// 检查直接权限
	if role, exists := m.roles[roleName]; exists {
		for _, p := range role.Permissions {
			if m.matchPermission(p, permission) {
				return true
			}
		}
	}

	// 检查继承的权限
	for _, parentRole := range m.roleHierarchy[roleName] {
		if m.HasPermission(parentRole, permission) {
			return true
		}
	}

	return false
}

func (m *RBACManager) GetPermissions(roleName string) []Permission {
	var permissions []Permission
	visited := make(map[string]bool)

	m.collectPermissions(roleName, &permissions, visited)

	return permissions
}

func (m *RBACManager) collectPermissions(roleName string, permissions *[]Permission, visited map[string]bool) {
	if visited[roleName] {
		return
	}

	visited[roleName] = true

	if role, exists := m.roles[roleName]; exists {
		*permissions = append(*permissions, role.Permissions...)

		// 收集继承的权限
		for _, parentRole := range role.InheritsFrom {
			m.collectPermissions(parentRole, permissions, visited)
		}
	}
}

func (m *RBACManager) matchPermission(p1, p2 Permission) bool {
	// 支持通配符
	if p1.Resource == "*" || p2.Resource == "*" {
		return p1.Action == p2.Action || p1.Action == "*" || p2.Action == "*"
	}

	if p1.Resource != p2.Resource {
		return false
	}

	return p1.Action == p2.Action || p1.Action == "*" || p2.Action == "*"
}

// 预定义角色和权限
func SetupDefaultRBAC() *RBACManager {
	rbac := NewRBACManager()

	// 定义权限
	userPermissions := []Permission{
		{"profile", "read"},
		{"profile", "update"},
		{"profile", "delete"},
	}

	adminPermissions := append(userPermissions,
		Permission{"users", "read"},
		Permission{"users", "create"},
		Permission{"users", "update"},
		Permission{"users", "delete"},
		Permission{"system", "read"},
		Permission{"system", "update"},
	)

	superAdminPermissions := append(adminPermissions,
		Permission{"system", "delete"},
		Permission{"roles", "read"},
		Permission{"roles", "create"},
		Permission{"roles", "update"},
		Permission{"roles", "delete"},
	)

	// 定义角色
	rbac.AddRole(&Role{
		Name:        "user",
		Permissions: userPermissions,
	})

	rbac.AddRole(&Role{
		Name:         "admin",
		Permissions:  adminPermissions,
		InheritsFrom: []string{"user"},
	})

	rbac.AddRole(&Role{
		Name:         "super_admin",
		Permissions:  superAdminPermissions,
		InheritsFrom: []string{"admin"},
	})

	return rbac
}
```

---

## 🔒 输入验证与数据清理

### 1. 输入验证

#### 通用验证器
```go
package validation

import (
	"errors"
	"fmt"
	"net"
	"net/mail"
	"regexp"
	"strconv"
	"strings"
	"unicode"
)

type Validator struct {
	rules map[string][]ValidationRule
}

type ValidationRule struct {
	Name     string
	Value    interface{}
	Message  string
	Optional bool
}

type ValidationError struct {
	Field   string
	Message string
	Value   interface{}
}

func NewValidator() *Validator {
	return &Validator{
		rules: make(map[string][]ValidationRule),
	}
}

func (v *Validator) AddRule(field string, rule ValidationRule) {
	v.rules[field] = append(v.rules[field], rule)
}

func (v *Validator) Validate(data map[string]interface{}) []ValidationError {
	var errors []ValidationError

	for field, rules := range v.rules {
		value, exists := data[field]
		if !exists {
			// 检查是否为必填字段
			required := true
			for _, rule := range rules {
				if rule.Optional {
					required = false
					break
				}
			}
			if required {
				errors = append(errors, ValidationError{
					Field:   field,
					Message: "字段为必填",
				})
			}
			continue
		}

		// 验证每个规则
		for _, rule := range rules {
			if err := v.validateRule(field, value, rule); err != nil {
				errors = append(errors, *err)
			}
		}
	}

	return errors
}

func (v *Validator) validateRule(field string, value interface{}, rule ValidationRule) *ValidationError {
	switch rule.Name {
	case "required":
		if value == nil || value == "" {
			return &ValidationError{
				Field:   field,
				Message: rule.Message,
				Value:   value,
			}
		}

	case "min_length":
		if str, ok := value.(string); ok {
			minLen := rule.Value.(int)
			if len(str) < minLen {
				return &ValidationError{
					Field:   field,
					Message: fmt.Sprintf(rule.Message, minLen),
					Value:   value,
				}
			}
		}

	case "max_length":
		if str, ok := value.(string); ok {
			maxLen := rule.Value.(int)
			if len(str) > maxLen {
				return &ValidationError{
					Field:   field,
					Message: fmt.Sprintf(rule.Message, maxLen),
					Value:   value,
				}
			}
		}

	case "email":
		if email, ok := value.(string); ok {
			if _, err := mail.ParseAddress(email); err != nil {
				return &ValidationError{
					Field:   field,
					Message: rule.Message,
					Value:   value,
				}
			}
		}

	case "numeric":
		if str, ok := value.(string); ok {
			if _, err := strconv.ParseFloat(str, 64); err != nil {
				return &ValidationError{
					Field:   field,
					Message: rule.Message,
					Value:   value,
				}
			}
		}

	case "alphanumeric":
		if str, ok := value.(string); ok {
			if !isAlphanumeric(str) {
				return &ValidationError{
					Field:   field,
					Message: rule.Message,
					Value:   value,
				}
			}
		}

	case "regex":
		if str, ok := value.(string); ok {
			pattern := rule.Value.(string)
			if matched, _ := regexp.MatchString(pattern, str); !matched {
				return &ValidationError{
					Field:   field,
					Message: rule.Message,
					Value:   value,
				}
			}
		}

	case "in":
		if values, ok := rule.Value.([]interface{}); ok {
			var found bool
			for _, v := range values {
				if v == value {
					found = true
					break
				}
			}
			if !found {
				return &ValidationError{
					Field:   field,
					Message: rule.Message,
					Value:   value,
				}
			}
		}

	case "ipv4":
		if ipStr, ok := value.(string); ok {
			if ip := net.ParseIP(ipStr); ip == nil || ip.To4() == nil {
				return &ValidationError{
					Field:   field,
					Message: rule.Message,
					Value:   value,
				}
			}
		}

	case "ipv6":
		if ipStr, ok := value.(string); ok {
			if ip := net.ParseIP(ipStr); ip == nil || ip.To4() != nil {
				return &ValidationError{
					Field:   field,
					Message: rule.Message,
					Value:   value,
				}
			}
		}

	case "url":
		if urlStr, ok := value.(string); ok {
			if !isValidURL(urlStr) {
				return &ValidationError{
					Field:   field,
					Message: rule.Message,
					Value:   value,
				}
			}
		}
	}

	return nil
}

func isAlphanumeric(s string) bool {
	for _, r := range s {
		if !unicode.IsLetter(r) && !unicode.IsNumber(r) {
			return false
		}
	}
	return true
}

func isValidURL(urlStr string) bool {
	// 简化的URL验证
	urlPattern := `^https?:\/\/(?:www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b(?:[-a-zA-Z0-9()@:%_\+.~#?&\/=]*)$`
	matched, _ := regexp.MatchString(urlPattern, urlStr)
	return matched
}

// 使用示例
func ValidateUserInput(data map[string]interface{}) []ValidationError {
	validator := NewValidator()

	// 用户名验证
	validator.AddRule("username", ValidationRule{
		Name:     "required",
		Message:  "用户名为必填字段",
	})
	validator.AddRule("username", ValidationRule{
		Name:     "min_length",
		Value:    3,
		Message:  "用户名长度不能少于%d位",
	})
	validator.AddRule("username", ValidationRule{
		Name:     "max_length",
		Value:    50,
		Message:  "用户名长度不能超过%d位",
	})
	validator.AddRule("username", ValidationRule{
		Name:     "alphanumeric",
		Message:  "用户名只能包含字母和数字",
	})

	// 邮箱验证
	validator.AddRule("email", ValidationRule{
		Name:     "required",
		Message:  "邮箱为必填字段",
	})
	validator.AddRule("email", ValidationRule{
		Name:     "email",
		Message:  "邮箱格式不正确",
	})

	// 年龄验证
	validator.AddRule("age", ValidationRule{
		Name:     "required",
		Message:  "年龄为必填字段",
	})
	validator.AddRule("age", ValidationRule{
		Name:     "numeric",
		Message:  "年龄必须是数字",
	})
	validator.AddRule("age", ValidationRule{
		Name:     "in",
		Value:    []interface{}{18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30},
		Message:  "年龄必须在18-30岁之间",
	})

	return validator.Validate(data)
}
```

#### SQL注入防护
```go
package security

import (
	"database/sql"
	"fmt"
	"regexp"
	"strings"
)

type SQLInjectionDetector struct {
	patterns []string
}

func NewSQLInjectionDetector() *SQLInjectionDetector {
	return &SQLInjectionDetector{
		patterns: []string{
			`(?i)\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE|UNION|EXEC|EXECUTE|XP_|SP_)\b`,
			`(?i)\b(OR|AND)\s+\d+\s*=\s*\d+`,
			`(?i)\b(OR|AND)\s+\w+\s*=\s*\w+`,
			`(?i)\b(WAITFOR\s+DELAY|SLEEP)\b`,
			`(?i)\b(--|;|\/\*|\*\/)\b`,
			`(?i)\b(XP_cmdshell|XP_execresultset)\b`,
		},
	}
}

func (d *SQLInjectionDetector) Detect(input string) bool {
	for _, pattern := range d.patterns {
		if matched, _ := regexp.MatchString(pattern, input); matched {
			return true
		}
	}
	return false
}

func (d *SQLInjectionDetector) Sanitize(input string) string {
	// 移除特殊字符
	sanitized := strings.ReplaceAll(input, "'", "''")
	sanitized = strings.ReplaceAll(sanitized, "\"", "\"\"")
	sanitized = strings.ReplaceAll(sanitized, ";", "")
	sanitized = strings.ReplaceAll(sanitized, "--", "")
	sanitized = strings.ReplaceAll(sanitized, "/*", "")
	sanitized = strings.ReplaceAll(sanitized, "*/", "")

	return sanitized
}

// 安全的查询构建器
type SafeQueryBuilder struct {
	db *sql.DB
}

func NewSafeQueryBuilder(db *sql.DB) *SafeQueryBuilder {
	return &SafeQueryBuilder{db: db}
}

func (q *SafeQueryBuilder) SafeQuery(query string, args ...interface{}) (*sql.Rows, error) {
	// 验证查询是否包含参数占位符
	if strings.Contains(query, "?") && len(args) == 0 {
		return nil, fmt.Errorf("查询包含参数占位符但未提供参数")
	}

	// 执行参数化查询
	return q.db.Query(query, args...)
}

func (q *SafeQueryBuilder) SafeQueryRow(query string, args ...interface{}) *sql.Row {
	return q.db.QueryRow(query, args...)
}

func (q *SafeQueryBuilder) SafeExec(query string, args ...interface{}) (sql.Result, error) {
	return q.db.Exec(query, args...)
}

// 使用示例
func SecureUserLookup(db *sql.DB, username string) (*User, error) {
	detector := NewSQLInjectionDetector()

	// 检测SQL注入
	if detector.Detect(username) {
		return nil, fmt.Errorf("检测到潜在的SQL注入攻击")
	}

	// 使用参数化查询
	query := "SELECT id, username, email, created_at FROM users WHERE username = ?"

	row := db.QueryRow(query, username)

	var user User
	err := row.Scan(&user.ID, &user.Username, &user.Email, &user.CreatedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("用户不存在")
		}
		return nil, fmt.Errorf("查询失败: %w", err)
	}

	return &user, nil
}
```

### 2. XSS防护

#### HTML转义和清理
```go
package security

import (
	"regexp"
	"strings"
	"unicode"

	"github.com/microcosm-cc/bluemonday"
)

type XSSProtector struct {
	policy     *bluemonday.Policy
	detector   *XSSDetector
}

type XSSDetector struct {
	patterns []string
}

func NewXSSDetector() *XSSDetector {
	return &XSSDetector{
		patterns: []string{
			`<script[^>]*>.*?</script>`,
			`javascript:`,
			`on\w+\s*=`,
			`<iframe[^>]*>.*?</iframe>`,
			`<object[^>]*>.*?</object>`,
			`<embed[^>]*>`,
			`<link[^>]*>`,
			`<meta[^>]*>`,
			`<\?php`,
			`<%`,
			`eval\s*\(`,
			`expression\s*\(`,
			`vbscript:`,
			`data:text/html`,
		},
	}
}

func (d *XSSDetector) Detect(input string) bool {
	for _, pattern := range d.patterns {
		if matched, _ := regexp.MatchString(pattern, input); matched {
			return true
		}
	}
	return false
}

func NewXSSProtector() *XSSProtector {
	// 创建严格的HTML清理策略
	policy := bluemonday.StrictPolicy()

	// 允许基本的格式化标签
	policy.AllowStandardURLs()
	policy.AllowStandardAttributes()
	policy.AllowElements("b", "i", "u", "em", "strong", "p", "br", "ul", "ol", "li")

	return &XSSProtector{
		policy:   policy,
		detector: NewXSSDetector(),
	}
}

func (p *XSSProtector) SanitizeHTML(input string) string {
	return p.policy.Sanitize(input)
}

func (p *XSSProtector) EscapeHTML(input string) string {
	var escaped strings.Builder

	for _, r := range input {
		switch r {
		case '&':
			escaped.WriteString("&amp;")
		case '<':
			escaped.WriteString("&lt;")
		case '>':
			escaped.WriteString("&gt;")
		case '"':
			escaped.WriteString("&quot;")
		case '\'':
			escaped.WriteString("&#39;")
		case '/':
			escaped.WriteString("&#47;")
		default:
			if unicode.IsControl(r) {
				continue
			}
			escaped.WriteRune(r)
		}
	}

	return escaped.String()
}

func (p *XSSProtector) SanitizeAttribute(input string) string {
	// 移除危险的字符
	sanitized := strings.ReplaceAll(input, "'", "")
	sanitized = strings.ReplaceAll(sanitized, "\"", "")
	sanitized = strings.ReplaceAll(sanitized, "<", "")
	sanitized = strings.ReplaceAll(sanitized, ">", "")
	sanitized = strings.ReplaceAll(sanitized, "&", "")

	return sanitized
}

func (p *XSSProtector) ValidateAndSanitize(input string) (string, error) {
	if p.detector.Detect(input) {
		return "", fmt.Errorf("检测到潜在的XSS攻击")
	}

	return p.SanitizeHTML(input), nil
}

// Context-Aware安全输出
type SafeOutput struct {
	protector *XSSProtector
}

func NewSafeOutput() *SafeOutput {
	return &SafeOutput{
		protector: NewXSSProtector(),
	}
}

func (s *SafeOutput) HTML(input string) string {
	return s.protector.SanitizeHTML(input)
}

func (s *SafeOutput) Attribute(input string) string {
	return s.protector.SanitizeAttribute(input)
}

func (s *SafeOutput) JavaScript(input string) string {
	// JavaScript字符串转义
	var escaped strings.Builder

	for _, r := range input {
		switch r {
		case '\\':
			escaped.WriteString("\\\\")
		case '"':
			escaped.WriteString("\\\"")
		case '\'':
			escaped.WriteString("\\'")
		case '\n':
			escaped.WriteString("\\n")
		case '\r':
			escaped.WriteString("\\r")
		case '\t':
			escaped.WriteString("\\t")
		case '<':
			escaped.WriteString("\\x3C")
		case '>':
			escaped.WriteString("\\x3E")
		case '&':
			escaped.WriteString("\\x26")
		default:
			if r < 32 || r > 126 {
				escaped.WriteString(fmt.Sprintf("\\u%04X", r))
			} else {
				escaped.WriteRune(r)
			}
		}
	}

	return escaped.String()
}

func (s *SafeOutput) URL(input string) string {
	// URL编码
	return url.QueryEscape(input)
}
```

---

## 🛡️ 网络安全

### 1. TLS/SSL配置

#### 安全的HTTP服务器
```go
package server

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"io/ioutil"
	"net/http"
	"time"

	"golang.org/x/crypto/acme/autocert"
)

type SecureServer struct {
	server       *http.Server
	certManager  *autocert.Manager
	tlsConfig    *tls.Config
}

type SecureServerConfig struct {
	Host         string
	Port         int
	CertFile     string
	KeyFile      string
	AutoCert     bool
	CacheDir     string
	Domains      []string
	HSTS         bool
	Headers      SecurityHeaders
}

type SecurityHeaders struct {
	ContentTypeOptions      string
	XFrameOptions           string
	XSSProtection           string
	ContentSecurityPolicy   string
	StrictTransportSecurity string
	ReferrerPolicy          string
	PermissionsPolicy       string
}

func NewSecureServer(config SecureServerConfig) (*SecureServer, error) {
	// 创建TLS配置
	tlsConfig, err := createTLSConfig(config)
	if err != nil {
		return nil, fmt.Errorf("创建TLS配置失败: %w", err)
	}

	// 创建HTTP服务器
	server := &http.Server{
		Addr:         fmt.Sprintf("%s:%d", config.Host, config.Port),
		TLSConfig:    tlsConfig,
		ReadTimeout:  10 * time.Second,
		WriteTimeout: 10 * time.Second,
		IdleTimeout:  120 * time.Second,
	}

	secureServer := &SecureServer{
		server:    server,
		tlsConfig: tlsConfig,
	}

	// 配置自动证书管理
	if config.AutoCert {
		secureServer.certManager = &autocert.Manager{
			Prompt:     autocert.AcceptTOS,
			HostPolicy: autocert.HostWhitelist(config.Domains...),
			Cache:      autocert.DirCache(config.CacheDir),
		}
		secureServer.server.TLSConfig.GetCertificate = secureServer.certManager.GetCertificate
	}

	return secureServer, nil
}

func createTLSConfig(config SecureServerConfig) (*tls.Config, error) {
	tlsConfig := &tls.Config{
		MinVersion:               tls.VersionTLS12,
		MaxVersion:               tls.VersionTLS13,
		CurvePreferences:         []tls.CurveID{tls.X25519, tls.CurveP256},
		PreferServerCipherSuites: true,
		CipherSuites: []uint16{
			tls.TLS_AES_256_GCM_SHA384,
			tls.TLS_AES_128_GCM_SHA256,
			tls.TLS_CHACHA20_POLY1305_SHA256,
			tls.TLS_ECDHE_ECDSA_WITH_AES_256_GCM_SHA384,
			tls.TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384,
			tls.TLS_ECDHE_ECDSA_WITH_CHACHA20_POLY1305_SHA256,
			tls.TLS_ECDHE_RSA_WITH_CHACHA20_POLY1305_SHA256,
		},
	}

	// 加载证书和私钥
	if config.CertFile != "" && config.KeyFile != "" {
		cert, err := tls.LoadX509KeyPair(config.CertFile, config.KeyFile)
		if err != nil {
			return nil, fmt.Errorf("加载证书失败: %w", err)
		}
		tlsConfig.Certificates = []tls.Certificate{cert}
	}

	// 配置客户端证书验证（双向TLS）
	tlsConfig.ClientAuth = tls.VerifyClientCertIfGiven
	tlsConfig.ClientCAs = x509.NewCertPool()

	return tlsConfig, nil
}

func (s *SecureServer) UseSecurityHeaders(headers SecurityHeaders) {
	s.server.Handler = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// 设置安全头
		w.Header().Set("X-Content-Type-Options", headers.ContentTypeOptions)
		w.Header().Set("X-Frame-Options", headers.XFrameOptions)
		w.Header().Set("X-XSS-Protection", headers.XSSProtection)
		w.Header().Set("Content-Security-Policy", headers.ContentSecurityPolicy)
		w.Header().Set("Referrer-Policy", headers.ReferrerPolicy)
		w.Header().Set("Permissions-Policy", headers.PermissionsPolicy)

		if headers.StrictTransportSecurity != "" {
			w.Header().Set("Strict-Transport-Security", headers.StrictTransportSecurity)
		}

		// 移除服务器信息
		w.Header().Set("Server", "")

		// 继续处理请求
		s.server.Handler.ServeHTTP(w, r)
	})
}

func (s *SecureServer) UseRateLimit(limiter *RateLimiter) {
	s.server.Handler = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if !limiter.Allow(r.RemoteAddr) {
			http.Error(w, "请求过于频繁", http.StatusTooManyRequests)
			return
		}

		// 继续处理请求
		s.server.Handler.ServeHTTP(w, r)
	})
}

func (s *SecureServer) UseCORS(allowedOrigins []string) {
	corsHandler := NewCORSHandler(allowedOrigins)
	s.server.Handler = http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		corsHandler.ServeHTTP(w, r, func(w http.ResponseWriter, r *http.Request) {
			s.server.Handler.ServeHTTP(w, r)
		})
	})
}

func (s *SecureServer) Start() error {
	if s.certManager != nil {
		// 自动证书模式
		go func() {
			if err := s.server.ListenAndServeTLS("", ""); err != nil && err != http.ErrServerClosed {
				fmt.Printf("服务器启动失败: %v\n", err)
			}
		}()
	} else {
		// 静态证书模式
		go func() {
			if err := s.server.ListenAndServeTLS("", ""); err != nil && err != http.ErrServerClosed {
				fmt.Printf("服务器启动失败: %v\n", err)
			}
		}()
	}
	return nil
}

func (s *SecureServer) Stop() error {
	return s.server.Close()
}

// 默认安全头配置
func DefaultSecurityHeaders() SecurityHeaders {
	return SecurityHeaders{
		ContentTypeOptions:      "nosniff",
		XFrameOptions:           "DENY",
		XSSProtection:           "1; mode=block",
		ContentSecurityPolicy:   "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; font-src 'self'; connect-src 'self'",
		StrictTransportSecurity: "max-age=31536000; includeSubDomains; preload",
		ReferrerPolicy:          "strict-origin-when-cross-origin",
		PermissionsPolicy:       "geolocation=(), microphone=(), camera=()",
	}
}
```

### 2. 限流和防攻击

#### 限流器实现
```go
package security

import (
	"sync"
	"time"
)

type RateLimiter struct {
	limiters map[string]*tokenBucket
	mu       sync.RWMutex
	rate     int
	capacity int
}

type tokenBucket struct {
	tokens     int
	lastRefill time.Time
	capacity   int
	rate       int // tokens per second
	mu         sync.Mutex
}

func NewRateLimiter(rate, capacity int) *RateLimiter {
	return &RateLimiter{
		limiters: make(map[string]*tokenBucket),
		rate:     rate,
		capacity: capacity,
	}
}

func (rl *RateLimiter) Allow(key string) bool {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	limiter, exists := rl.limiters[key]
	if !exists {
		limiter = &tokenBucket{
			tokens:   rl.capacity,
			capacity: rl.capacity,
			rate:     rl.rate,
			lastRefill: time.Now(),
		}
		rl.limiters[key] = limiter
	}

	return limiter.allow()
}

func (tb *tokenBucket) allow() bool {
	tb.mu.Lock()
	defer tb.mu.Unlock()

	// 补充令牌
	now := time.Now()
	elapsed := now.Sub(tb.lastRefill).Seconds()
	tokensToAdd := int(elapsed * float64(tb.rate))

	if tokensToAdd > 0 {
		tb.tokens += tokensToAdd
		if tb.tokens > tb.capacity {
			tb.tokens = tb.capacity
		}
		tb.lastRefill = now
	}

	// 检查是否有足够的令牌
	if tb.tokens > 0 {
		tb.tokens--
		return true
	}

	return false
}

// 滑动窗口限流器
type SlidingWindowLimiter struct {
	windows map[string]*slidingWindow
	mu      sync.RWMutex
	rate    int
	window  time.Duration
}

type slidingWindow struct {
	requests []time.Time
	window   time.Duration
	rate     int
	mu       sync.Mutex
}

func NewSlidingWindowLimiter(rate int, window time.Duration) *SlidingWindowLimiter {
	return &SlidingWindowLimiter{
		windows: make(map[string]*slidingWindow),
		rate:    rate,
		window:  window,
	}
}

func (swl *SlidingWindowLimiter) Allow(key string) bool {
	swl.mu.Lock()
	defer swl.mu.Unlock()

	window, exists := swl.windows[key]
	if !exists {
		window = &slidingWindow{
			requests: make([]time.Time, 0),
			window:   swl.window,
			rate:     swl.rate,
		}
		swl.windows[key] = window
	}

	return window.allow()
}

func (sw *slidingWindow) allow() bool {
	sw.mu.Lock()
	defer sw.mu.Unlock()

	now := time.Now()
	cutoff := now.Add(-sw.window)

	// 移除过期的请求
	validRequests := make([]time.Time, 0)
	for _, req := range sw.requests {
		if req.After(cutoff) {
			validRequests = append(validRequests, req)
		}
	}

	sw.requests = validRequests

	// 检查是否超过限制
	if len(sw.requests) >= sw.rate {
		return false
	}

	// 记录新请求
	sw.requests = append(sw.requests, now)
	return true
}

// IP白名单和黑名单
type IPFilter struct {
	whitelist map[string]bool
	blacklist map[string]bool
	mu        sync.RWMutex
}

func NewIPFilter() *IPFilter {
	return &IPFilter{
		whitelist: make(map[string]bool),
		blacklist: make(map[string]bool),
	}
}

func (f *IPFilter) AddToWhitelist(ip string) {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.whitelist[ip] = true
}

func (f *IPFilter) AddToBlacklist(ip string) {
	f.mu.Lock()
	defer f.mu.Unlock()
	f.blacklist[ip] = true
}

func (f *IPFilter) IsAllowed(ip string) bool {
	f.mu.RLock()
	defer f.mu.RUnlock()

	// 检查黑名单
	if f.blacklist[ip] {
		return false
	}

	// 如果白名单不为空，必须在白名单中
	if len(f.whitelist) > 0 {
		return f.whitelist[ip]
	}

	return true
}
```

---

## 🔐 密钥管理和敏感信息保护

### 1. 密钥管理

#### 环境变量和配置管理
```go
package config

import (
	"crypto/rand"
	"crypto/rsa"
	"encoding/base64"
	"fmt"
	"os"
	"strconv"
	"strings"

	"github.com/joho/godotenv"
	"gopkg.in/yaml.v2"
)

type Config struct {
	Server   ServerConfig   `yaml:"server"`
	Database DatabaseConfig `yaml:"database"`
	Auth     AuthConfig     `yaml:"auth"`
	Security SecurityConfig `yaml:"security"`
}

type ServerConfig struct {
	Host string `yaml:"host"`
	Port int    `yaml:"port"`
	TLS  TLSConfig `yaml:"tls"`
}

type TLSConfig struct {
	Enabled  bool   `yaml:"enabled"`
	CertFile string `yaml:"cert_file"`
	KeyFile  string `yaml:"key_file"`
}

type DatabaseConfig struct {
	Host     string `yaml:"host"`
	Port     int    `yaml:"port"`
	Database string `yaml:"database"`
	Username string `yaml:"username"`
	Password string `yaml:"password"`
	SSLMode  string `yaml:"ssl_mode"`
}

type AuthConfig struct {
	JWTSecret      string        `yaml:"jwt_secret"`
	TokenDuration  string        `yaml:"token_duration"`
	RefreshTimeout string        `yaml:"refresh_timeout"`
	RSAPrivateKey  string        `yaml:"rsa_private_key"`
	RSAPublicKey   string        `yaml:"rsa_public_key"`
}

type SecurityConfig struct {
	EncryptionKey string `yaml:"encryption_key"`
	BCryptCost    int    `yaml:"bcrypt_cost"`
	RateLimit     int    `yaml:"rate_limit"`
	EnableCORS    bool   `yaml:"enable_cors"`
}

func LoadConfig(configPath string) (*Config, error) {
	// 加载环境变量
	if err := godotenv.Load(); err != nil {
		fmt.Printf("警告: 无法加载.env文件: %v\n", err)
	}

	// 读取配置文件
	data, err := os.ReadFile(configPath)
	if err != nil {
		return nil, fmt.Errorf("读取配置文件失败: %w", err)
	}

	var config Config
	if err := yaml.Unmarshal(data, &config); err != nil {
		return nil, fmt.Errorf("解析配置文件失败: %w", err)
	}

	// 从环境变量覆盖敏感配置
	config = config.overrideFromEnv()

	// 验证配置
	if err := config.validate(); err != nil {
		return nil, fmt.Errorf("配置验证失败: %w", err)
	}

	return &config, nil
}

func (c *Config) overrideFromEnv() Config {
	// 数据库配置
	if dbHost := os.Getenv("DB_HOST"); dbHost != "" {
		c.Database.Host = dbHost
	}
	if dbPort := os.Getenv("DB_PORT"); dbPort != "" {
		if port, err := strconv.Atoi(dbPort); err == nil {
			c.Database.Port = port
		}
	}
	if dbName := os.Getenv("DB_NAME"); dbName != "" {
		c.Database.Database = dbName
	}
	if dbUser := os.Getenv("DB_USER"); dbUser != "" {
		c.Database.Username = dbUser
	}
	if dbPass := os.Getenv("DB_PASSWORD"); dbPass != "" {
		c.Database.Password = dbPass
	}

	// 认证配置
	if jwtSecret := os.Getenv("JWT_SECRET"); jwtSecret != "" {
		c.Auth.JWTSecret = jwtSecret
	}
	if encryptionKey := os.Getenv("ENCRYPTION_KEY"); encryptionKey != "" {
		c.Security.EncryptionKey = encryptionKey
	}

	return *c
}

func (c *Config) validate() error {
	// 验证必需的配置
	if c.Database.Host == "" {
		return fmt.Errorf("数据库主机不能为空")
	}
	if c.Database.Database == "" {
		return fmt.Errorf("数据库名称不能为空")
	}
	if c.Auth.JWTSecret == "" {
		return fmt.Errorf("JWT密钥不能为空")
	}
	if c.Security.EncryptionKey == "" {
		return fmt.Errorf("加密密钥不能为空")
	}

	// 验证密钥长度
	if len(c.Auth.JWTSecret) < 32 {
		return fmt.Errorf("JWT密钥长度不能少于32位")
	}
	if len(c.Security.EncryptionKey) < 32 {
		return fmt.Errorf("加密密钥长度不能少于32位")
	}

	return nil
}

// 生成随机密钥
func GenerateRandomKey(length int) (string, error) {
	bytes := make([]byte, length)
	if _, err := rand.Read(bytes); err != nil {
		return "", fmt.Errorf("生成随机密钥失败: %w", err)
	}
	return base64.URLEncoding.EncodeToString(bytes), nil
}

// 生成RSA密钥对
func GenerateRSAKeyPair(bits int) (*rsa.PrivateKey, *rsa.PublicKey, error) {
	privateKey, err := rsa.GenerateKey(rand.Reader, bits)
	if err != nil {
		return nil, nil, fmt.Errorf("生成RSA密钥对失败: %w", err)
	}
	return privateKey, &privateKey.PublicKey, nil
}

// 敏感信息脱敏
func MaskSensitiveInfo(value string, maskChar rune) string {
	if len(value) <= 8 {
		return strings.Repeat(string(maskChar), len(value))
	}

	// 显示前4位和后4位
	prefix := value[:4]
	suffix := value[len(value)-4:]
	masked := strings.Repeat(string(maskChar), len(value)-8)

	return prefix + masked + suffix
}
```

### 2. 数据加密

#### 对称加密
```go
package security

import (
	"crypto/aes"
	"crypto/cipher"
	"crypto/rand"
	"crypto/sha256"
	"encoding/base64"
	"fmt"
	"io"

	"golang.org/x/crypto/scrypt"
)

type Encryptor struct {
	key []byte
}

func NewEncryptor(key string) (*Encryptor, error) {
	if len(key) < 32 {
		return nil, fmt.Errorf("密钥长度不能少于32位")
	}

	// 使用SHA-256生成固定长度的密钥
	hash := sha256.Sum256([]byte(key))

	return &Encryptor{
		key: hash[:],
	}, nil
}

func (e *Encryptor) Encrypt(plaintext []byte) ([]byte, error) {
	block, err := aes.NewCipher(e.key)
	if err != nil {
		return nil, fmt.Errorf("创建加密块失败: %w", err)
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, fmt.Errorf("创建GCM模式失败: %w", err)
	}

	nonce := make([]byte, gcm.NonceSize())
	if _, err = io.ReadFull(rand.Reader, nonce); err != nil {
		return nil, fmt.Errorf("生成nonce失败: %w", err)
	}

	ciphertext := gcm.Seal(nonce, nonce, plaintext, nil)
	return ciphertext, nil
}

func (e *Encryptor) Decrypt(ciphertext []byte) ([]byte, error) {
	block, err := aes.NewCipher(e.key)
	if err != nil {
		return nil, fmt.Errorf("创建加密块失败: %w", err)
	}

	gcm, err := cipher.NewGCM(block)
	if err != nil {
		return nil, fmt.Errorf("创建GCM模式失败: %w", err)
	}

	nonceSize := gcm.NonceSize()
	if len(ciphertext) < nonceSize {
		return nil, fmt.Errorf("密文长度不足")
	}

	nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]
	plaintext, err := gcm.Open(nil, nonce, ciphertext, nil)
	if err != nil {
		return nil, fmt.Errorf("解密失败: %w", err)
	}

	return plaintext, nil
}

func (e *Encryptor) EncryptString(plaintext string) (string, error) {
	ciphertext, err := e.Encrypt([]byte(plaintext))
	if err != nil {
		return "", err
	}
	return base64.URLEncoding.EncodeToString(ciphertext), nil
}

func (e *Encryptor) DecryptString(ciphertext string) (string, error) {
	data, err := base64.URLEncoding.DecodeString(ciphertext)
	if err != nil {
		return "", fmt.Errorf("Base64解码失败: %w", err)
	}

	plaintext, err := e.Decrypt(data)
	if err != nil {
		return "", err
	}

	return string(plaintext), nil
}

// 密钥派生函数
func DeriveKey(password, salt string, keyLen int) ([]byte, error) {
	// 使用scrypt进行密钥派生
	return scrypt.Key([]byte(password), []byte(salt), 32768, 8, 1, keyLen)
}

// 安全的密钥生成器
type SecureKeyGenerator struct {
	encryptionKey []byte
	authKey       []byte
}

func NewSecureKeyGenerator(masterKey string) (*SecureKeyGenerator, error) {
	// 派生加密密钥
	encryptionKey, err := DeriveKey(masterKey, "encryption", 32)
	if err != nil {
		return nil, err
	}

	// 派生认证密钥
	authKey, err := DeriveKey(masterKey, "authentication", 32)
	if err != nil {
		return nil, err
	}

	return &SecureKeyGenerator{
		encryptionKey: encryptionKey,
		authKey:       authKey,
	}, nil
}

func (g *SecureKeyGenerator) GenerateKey() (string, error) {
	key := make([]byte, 32)
	if _, err := rand.Read(key); err != nil {
		return "", fmt.Errorf("生成密钥失败: %w", err)
	}

	// 加密密钥
	encryptor, err := NewEncryptor(string(g.encryptionKey))
	if err != nil {
		return "", err
	}

	encryptedKey, err := encryptor.Encrypt(key)
	if err != nil {
		return "", err
	}

	// 生成HMAC签名
	hmacHash := sha256.New()
	hmacHash.Write(g.authKey)
	hmacHash.Write(encryptedKey)
	signature := hmacHash.Sum(nil)

	// 组合加密密钥和签名
	finalKey := append(encryptedKey, signature...)
	return base64.URLEncoding.EncodeToString(finalKey), nil
}

func (g *SecureKeyGenerator) ValidateKey(encodedKey string) (bool, error) {
	data, err := base64.URLEncoding.DecodeString(encodedKey)
	if err != nil {
		return false, fmt.Errorf("Base64解码失败: %w", err)
	}

	if len(data) < 32 {
		return false, fmt.Errorf("密钥长度不足")
	}

	// 分离加密密钥和签名
	encryptedKey := data[:len(data)-32]
	signature := data[len(data)-32:]

	// 验证签名
	hmacHash := sha256.New()
	hmacHash.Write(g.authKey)
	hmacHash.Write(encryptedKey)
	expectedSignature := hmacHash.Sum(nil)

	if !hashesEqual(signature, expectedSignature) {
		return false, nil
	}

	// 尝试解密
	encryptor, err := NewEncryptor(string(g.encryptionKey))
	if err != nil {
		return false, err
	}

	_, err = encryptor.Decrypt(encryptedKey)
	return err == nil, nil
}

func hashesEqual(a, b []byte) bool {
	if len(a) != len(b) {
		return false
	}

	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}

	return true
}
```

---

## 🧪 安全测试

### 1. 安全测试工具

#### 安全测试框架
```go
package security

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"net/http/httptest"
	"strings"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/require"
)

type SecurityTestSuite struct {
	testing.T
	baseURL    string
	authToken  string
	httpClient *http.Client
}

func NewSecurityTestSuite(t *testing.T, baseURL string) *SecurityTestSuite {
	return &SecurityTestSuite{
		T:          t,
		baseURL:    baseURL,
		httpClient: &http.Client{},
	}
}

func (s *SecurityTestSuite) TestSQLInjection() {
	tests := []struct {
		name        string
		payload     string
		expectError bool
	}{
		{
			name:        "Union注入",
			payload:     "username=admin' UNION SELECT * FROM users--",
			expectError: true,
		},
		{
			name:        "布尔注入",
			payload:     "username=admin' OR 1=1--",
			expectError: true,
		},
		{
			name:        "时间注入",
			payload:     "username=admin' AND (SELECT * FROM (SELECT(SLEEP(5)))a)--",
			expectError: true,
		},
		{
			name:        "堆叠查询",
			payload:     "username=admin'; DROP TABLE users;--",
			expectError: true,
		},
		{
			name:        "正常输入",
			payload:     "username=john_doe",
			expectError: false,
		},
	}

	for _, tt := range tests {
		s.Run(tt.name, func() {
			payload := map[string]string{
				"username": tt.payload,
				"password": "password123",
			}

			jsonData, _ := json.Marshal(payload)
			resp, err := s.httpClient.Post(
				s.baseURL+"/api/login",
				"application/json",
				bytes.NewBuffer(jsonData),
			)

			require.NoError(s.T(), err)
			defer resp.Body.Close()

			body, _ := io.ReadAll(resp.Body)

			if tt.expectError {
				assert.Contains(s.T(), string(body), "error") || assert.Equal(s.T(), http.StatusBadRequest, resp.StatusCode)
			} else {
				assert.Equal(s.T(), http.StatusOK, resp.StatusCode)
			}
		})
	}
}

func (s *SecurityTestSuite) TestXSSAttacks() {
	tests := []struct {
		name        string
		payload     string
		expectError bool
	}{
		{
			name:        "Script标签",
			payload:     "<script>alert('XSS')</script>",
			expectError: true,
		},
		{
			name:        "JavaScript事件",
			payload:     "<img src=x onerror=alert('XSS')>",
			expectError: true,
		},
		{
			name:        "CSS表达式",
			payload:     "<style>body{background:expression(alert('XSS'))}</style>",
			expectError: true,
		},
		{
			name:        "Base64编码",
			payload:     "PHNjcmlwdD5hbGVydCgnWFNTJyk8L3NjcmlwdD4=",
			expectError: true,
		},
		{
			name:        "正常文本",
			payload:     "Hello World",
			expectError: false,
		},
	}

	for _, tt := range tests {
		s.Run(tt.name, func() {
			payload := map[string]string{
				"comment": tt.payload,
			}

			jsonData, _ := json.Marshal(payload)
			resp, err := s.httpClient.Post(
				s.baseURL+"/api/comments",
				"application/json",
				bytes.NewBuffer(jsonData),
			)

			require.NoError(s.T(), err)
			defer resp.Body.Close()

			body, _ := io.ReadAll(resp.Body)

			if tt.expectError {
				assert.Contains(s.T(), string(body), "error") || assert.Equal(s.T(), http.StatusBadRequest, resp.StatusCode)
			} else {
				assert.Equal(s.T(), http.StatusCreated, resp.StatusCode)
			}
		})
	}
}

func (s *SecurityTestSuite) TestCSRFProtection() {
	// 获取表单页面
	resp, err := s.httpClient.Get(s.baseURL + "/settings")
	require.NoError(s.T(), err)
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	bodyStr := string(body)

	// 检查CSRF令牌是否存在
	assert.Contains(s.T(), bodyStr, "csrf_token")

	// 提取CSRF令牌
	csrfToken := extractCSRFToken(bodyStr)
	assert.NotEmpty(s.T(), csrfToken)

	// 尝试不使用CSRF令牌提交表单
	formData := map[string]string{
		"email": "test@example.com",
	}

	formDataEncoded := url.Values{}
	for k, v := range formData {
		formDataEncoded.Set(k, v)
	}

	resp, err = s.httpClient.PostForm(
		s.baseURL+"/api/settings",
		formDataEncoded,
	)

	require.NoError(s.T(), err)
	defer resp.Body.Close()

	// 应该被拒绝
	assert.Equal(s.T(), http.StatusForbidden, resp.StatusCode)

	// 使用正确的CSRF令牌提交
	formDataEncoded.Set("csrf_token", csrfToken)
	resp, err = s.httpClient.PostForm(
		s.baseURL+"/api/settings",
		formDataEncoded,
	)

	require.NoError(s.T(), err)
	defer resp.Body.Close()

	assert.Equal(s.T(), http.StatusOK, resp.StatusCode)
}

func (s *SecurityTestSuite) TestRateLimiting() {
	// 发送大量请求
	for i := 0; i < 10; i++ {
		resp, err := s.httpClient.Get(s.baseURL + "/api/protected")
		require.NoError(s.T(), err)
		defer resp.Body.Close()

		if i >= 5 { // 假设限制为每分钟5次
			assert.Equal(s.T(), http.StatusTooManyRequests, resp.StatusCode)
		} else {
			assert.Equal(s.T(), http.StatusOK, resp.StatusCode)
		}
	}
}

func (s *SecurityTestSuite) TestAuthentication() {
	// 测试无效token
	req, _ := http.NewRequest("GET", s.baseURL+"/api/protected", nil)
	req.Header.Set("Authorization", "Bearer invalid_token")
	resp, err := s.httpClient.Do(req)

	require.NoError(s.T(), err)
	defer resp.Body.Close()
	assert.Equal(s.T(), http.StatusUnauthorized, resp.StatusCode)

	// 测试过期token
	expiredToken := generateExpiredToken()
	req.Header.Set("Authorization", "Bearer "+expiredToken)
	resp, err = s.httpClient.Do(req)

	require.NoError(s.T(), err)
	defer resp.Body.Close()
	assert.Equal(s.T(), http.StatusUnauthorized, resp.StatusCode)

	// 测试有效token
	validToken := generateValidToken()
	req.Header.Set("Authorization", "Bearer "+validToken)
	resp, err = s.httpClient.Do(req)

	require.NoError(s.T(), err)
	defer resp.Body.Close()
	assert.Equal(s.T(), http.StatusOK, resp.StatusCode)
}

func (s *SecurityTestSuite) TestSecurityHeaders() {
	resp, err := s.httpClient.Get(s.baseURL + "/")
	require.NoError(s.T(), err)
	defer resp.Body.Close()

	// 检查安全头
	assert.Equal(s.T(), "nosniff", resp.Header.Get("X-Content-Type-Options"))
	assert.Equal(s.T(), "DENY", resp.Header.Get("X-Frame-Options"))
	assert.Equal(s.T(), "1; mode=block", resp.Header.Get("X-XSS-Protection"))
	assert.Contains(s.T(), resp.Header.Get("Content-Security-Policy"), "default-src")
	assert.Contains(s.T(), resp.Header.Get("Strict-Transport-Security"), "max-age")
}

// 辅助函数
func extractCSRFToken(html string) string {
	// 简化的CSRF令牌提取
	start := strings.Index(html, "name=\"csrf_token\" value=\"")
	if start == -1 {
		return ""
	}
	start += len("name=\"csrf_token\" value=\"")
	end := strings.Index(html[start:], "\"")
	if end == -1 {
		return ""
	}
	return html[start : start+end]
}

func generateExpiredToken() string {
	// 返回过期token的模拟实现
	return "expired_token_12345"
}

func generateValidToken() string {
	// 返回有效token的模拟实现
	return "valid_token_12345"
}
```

### 2. 漏洞扫描

#### 自动化安全扫描
```go
package security

import (
	"fmt"
	"net/http"
	"regexp"
	"strings"
	"time"
)

type VulnerabilityScanner struct {
	client     *http.Client
	target     string
	findings   []VulnerabilityFinding
	scanConfig ScanConfig
}

type VulnerabilityFinding struct {
	Type        string
	Severity    string
	Description string
	URL         string
	Evidence    string
}

type ScanConfig struct {
	EnableSQLi    bool
	EnableXSS     bool
	EnableCSRF    bool
	EnableSSRF    bool
	EnableXXE     bool
	EnableHeaders bool
	EnableTLS     bool
}

func NewVulnerabilityScanner(target string, config ScanConfig) *VulnerabilityScanner {
	return &VulnerabilityScanner{
		client: &http.Client{
			Timeout: 30 * time.Second,
		},
		target:     target,
		scanConfig: config,
		findings:   make([]VulnerabilityFinding, 0),
	}
}

func (s *VulnerabilityScanner) Scan() []VulnerabilityFinding {
	if s.scanConfig.EnableHeaders {
		s.scanSecurityHeaders()
	}

	if s.scanConfig.EnableTLS {
		s.scanTLSConfig()
	}

	if s.scanConfig.EnableSQLi {
		s.scanSQLInjection()
	}

	if s.scanConfig.EnableXSS {
		s.scanXSS()
	}

	if s.scanConfig.EnableCSRF {
		s.scanCSRF()
	}

	return s.findings
}

func (s *VulnerabilityScanner) scanSecurityHeaders() {
	resp, err := s.client.Get(s.target)
	if err != nil {
		s.addFinding("Security Headers", "High", "无法访问目标", s.target, err.Error())
		return
	}
	defer resp.Body.Close()

	headers := resp.Header

	// 检查安全头
	securityHeaders := map[string]string{
		"X-Content-Type-Options":      "nosniff",
		"X-Frame-Options":           "DENY",
		"X-XSS-Protection":           "1; mode=block",
		"Content-Security-Policy":     "default-src",
		"Strict-Transport-Security":   "max-age",
		"Referrer-Policy":            "strict-origin",
		"Permissions-Policy":         "geolocation=()",
	}

	for header, expected := range securityHeaders {
		value := headers.Get(header)
		if value == "" {
			s.addFinding("Missing Security Header", "Medium",
				fmt.Sprintf("缺少安全头: %s", header), s.target, "")
		} else if !strings.Contains(value, expected) {
			s.addFinding("Weak Security Header", "Low",
				fmt.Sprintf("安全头配置不当: %s", header), s.target, value)
		}
	}

	// 检查服务器信息泄露
	server := headers.Get("Server")
	if server != "" && !strings.Contains(server, "nginx") && !strings.Contains(server, "apache") {
		s.addFinding("Information Disclosure", "Low",
			"服务器头信息可能泄露敏感信息", s.target, server)
	}
}

func (s *VulnerabilityScanner) scanTLSConfig() {
	resp, err := s.client.Get(s.target)
	if err != nil {
		return
	}
	defer resp.Body.Close()

	// 检查是否使用HTTPS
	if !strings.HasPrefix(s.target, "https://") {
		s.addFinding("Insecure Protocol", "High",
			"使用HTTP协议而非HTTPS", s.target, "")
		return
	}

	// 检查TLS版本
	if resp.TLS != nil {
		for _, cipherSuite := range resp.TLS.CipherSuites {
			if strings.Contains(cipherSuite.Name, "RC4") ||
			   strings.Contains(cipherSuite.Name, "3DES") ||
			   strings.Contains(cipherSuite.Name, "MD5") {
				s.addFinding("Weak Cipher Suite", "High",
					"使用弱加密套件", s.target, cipherSuite.Name)
			}
		}

		// 检查TLS版本
		if resp.TLS.Version < tls.VersionTLS12 {
			s.addFinding("Outdated TLS Version", "High",
				"使用过时的TLS版本", s.target, fmt.Sprintf("TLS %x", resp.TLS.Version))
		}
	}
}

func (s *VulnerabilityScanner) scanSQLInjection() {
	testPayloads := []string{
		"' OR '1'='1",
		"' UNION SELECT NULL--",
		"' AND SLEEP(5)--",
		"'; DROP TABLE users--",
		"' OR 1=1#",
	}

	for _, payload := range testPayloads {
		testURL := s.target + "/api/users?q=" + url.QueryEscape(payload)
		resp, err := s.client.Get(testURL)
		if err != nil {
			continue
		}
		defer resp.Body.Close()

		// 检查响应时间（时间盲注）
		if resp.StatusCode == http.StatusOK {
			// 这里可以添加更详细的响应分析
			s.addFinding("Potential SQL Injection", "High",
				"可能存在SQL注入漏洞", testURL, payload)
		}
	}
}

func (s *VulnerabilityScanner) scanXSS() {
	testPayloads := []string{
		"<script>alert('XSS')</script>",
		"<img src=x onerror=alert('XSS')>",
		"javascript:alert('XSS')",
		"<svg onload=alert('XSS')>",
		"'><script>alert('XSS')</script>",
	}

	for _, payload := range testPayloads {
		testURL := s.target + "/api/search?q=" + url.QueryEscape(payload)
		resp, err := s.client.Get(testURL)
		if err != nil {
			continue
		}
		defer resp.Body.Close()

		body, _ := io.ReadAll(resp.Body)
		bodyStr := string(body)

		if strings.Contains(bodyStr, payload) {
			s.addFinding("XSS Vulnerability", "High",
				"存在XSS漏洞", testURL, payload)
		}
	}
}

func (s *VulnerabilityScanner) scanCSRF() {
	// 检查表单是否包含CSRF令牌
	resp, err := s.client.Get(s.target + "/login")
	if err != nil {
		return
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	bodyStr := string(body)

	if !strings.Contains(bodyStr, "csrf") &&
	   !strings.Contains(bodyStr, "token") {
		s.addFinding("Missing CSRF Protection", "Medium",
			"表单缺少CSRF保护", s.target, "")
	}
}

func (s *VulnerabilityScanner) addFinding(vType, severity, description, url, evidence string) {
	finding := VulnerabilityFinding{
		Type:        vType,
		Severity:    severity,
		Description: description,
		URL:         url,
		Evidence:    evidence,
	}
	s.findings = append(s.findings, finding)
}

func (s *VulnerabilityScanner) GenerateReport() string {
	var report strings.Builder

	report.WriteString("=== 安全漏洞扫描报告 ===\n\n")
	report.WriteString(fmt.Sprintf("目标: %s\n", s.target))
	report.WriteString(fmt.Sprintf("扫描时间: %s\n\n", time.Now().Format("2006-01-02 15:04:05")))

	// 按严重性分组
	findingsBySeverity := make(map[string][]VulnerabilityFinding)
	for _, finding := range s.findings {
		findingsBySeverity[finding.Severity] = append(findingsBySeverity[finding.Severity], finding)
	}

	severityOrder := []string{"Critical", "High", "Medium", "Low"}
	for _, severity := range severityOrder {
		if findings, exists := findingsBySeverity[severity]; exists {
			report.WriteString(fmt.Sprintf("### %s (%d)\n", severity, len(findings)))
			for _, finding := range findings {
				report.WriteString(fmt.Sprintf("- **%s**: %s\n", finding.Type, finding.Description))
				if finding.Evidence != "" {
					report.WriteString(fmt.Sprintf("  证据: %s\n", finding.Evidence))
				}
			}
			report.WriteString("\n")
		}
	}

	report.WriteString(fmt.Sprintf("总计发现 %d 个安全问题\n", len(s.findings)))
	return report.String()
}
```

---

## 📊 安全监控和日志

### 1. 安全事件日志

```go
package security

import (
	"encoding/json"
	"fmt"
	"log"
	"os"
	"time"
)

type SecurityEvent struct {
	ID          string                 `json:"id"`
	Timestamp   time.Time             `json:"timestamp"`
	EventType   string                 `json:"event_type"`
	Severity    string                 `json:"severity"`
	SourceIP    string                 `json:"source_ip"`
	UserAgent   string                 `json:"user_agent"`
	UserID      string                 `json:"user_id,omitempty"`
	Description string                 `json:"description"`
	Details     map[string]interface{} `json:"details,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

type SecurityLogger struct {
	fileLogger   *log.Logger
	jsonLogger   *log.Logger
	eventChan    chan SecurityEvent
	bufferSize   int
	flushTimeout time.Duration
}

func NewSecurityLogger(logFile string, bufferSize int, flushTimeout time.Duration) (*SecurityLogger, error) {
	file, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return nil, fmt.Errorf("打开日志文件失败: %w", err)
	}

	return &SecurityLogger{
		fileLogger:   log.New(file, "", log.LstdFlags),
		jsonLogger:   log.New(file, "", 0),
		eventChan:    make(chan SecurityEvent, bufferSize),
		bufferSize:   bufferSize,
		flushTimeout: flushTimeout,
	}, nil
}

func (l *SecurityLogger) Start() {
	go l.processEvents()
}

func (l *SecurityLogger) LogEvent(event SecurityEvent) {
	l.eventChan <- event
}

func (l *SecurityLogger) LogAuthEvent(eventType, userID, sourceIP string, success bool) {
	severity := "INFO"
	if !success {
		severity = "WARNING"
	}

	event := SecurityEvent{
		ID:        generateEventID(),
		Timestamp: time.Now(),
		EventType: eventType,
		Severity:  severity,
		SourceIP:  sourceIP,
		UserID:    userID,
		Description: fmt.Sprintf("认证事件: %s, 成功: %v", eventType, success),
		Details: map[string]interface{}{
			"success": success,
		},
	}

	l.eventChan <- event
}

func (l *SecurityLogger) LogSecurityEvent(eventType, description, sourceIP, severity string) {
	event := SecurityEvent{
		ID:          generateEventID(),
		Timestamp:   time.Now(),
		EventType:   eventType,
		Severity:    severity,
		SourceIP:    sourceIP,
		Description: description,
	}

	l.eventChan <- event
}

func (l *SecurityLogger) LogRateLimitEvent(sourceIP, endpoint string, limited bool) {
	severity := "INFO"
	if limited {
		severity = "WARNING"
	}

	event := SecurityEvent{
		ID:          generateEventID(),
		Timestamp:   time.Now(),
		EventType:   "RATE_LIMIT",
		Severity:    severity,
		SourceIP:    sourceIP,
		Description: fmt.Sprintf("限流事件: %s, 被限制: %v", endpoint, limited),
		Details: map[string]interface{}{
			"endpoint": endpoint,
			"limited":  limited,
		},
	}

	l.eventChan <- event
}

func (l *SecurityLogger) processEvents() {
	ticker := time.NewTicker(l.flushTimeout)
	defer ticker.Stop()

	var buffer []SecurityEvent

	for {
		select {
		case event := <-l.eventChan:
			buffer = append(buffer, event)

			// 如果缓冲区满，立即刷新
			if len(buffer) >= l.bufferSize {
				l.flushEvents(buffer)
				buffer = buffer[:0]
			}

		case <-ticker.C:
			// 定时刷新
			if len(buffer) > 0 {
				l.flushEvents(buffer)
				buffer = buffer[:0]
			}
		}
	}
}

func (l *SecurityLogger) flushEvents(events []SecurityEvent) {
	for _, event := range events {
		// 写入格式化日志
		l.fileLogger.Printf("[%s] %s - %s: %s",
			event.Timestamp.Format("2006-01-02 15:04:05"),
			event.Severity,
			event.EventType,
			event.Description,
		)

		// 写入JSON日志
		jsonData, _ := json.Marshal(event)
		l.jsonLogger.Println(string(jsonData))
	}
}

func generateEventID() string {
	return fmt.Sprintf("%d", time.Now().UnixNano())
}

// 安全分析器
type SecurityAnalyzer struct {
	events []SecurityEvent
	rules  []SecurityRule
}

type SecurityRule struct {
	Name        string
	Description string
	Condition   func(SecurityEvent) bool
	Action      func(SecurityEvent)
}

func NewSecurityAnalyzer() *SecurityAnalyzer {
	return &SecurityAnalyzer{
		events: make([]SecurityEvent, 0),
		rules:  make([]SecurityRule, 0),
	}
}

func (a *SecurityAnalyzer) AddRule(rule SecurityRule) {
	a.rules = append(a.rules, rule)
}

func (a *SecurityAnalyzer) ProcessEvent(event SecurityEvent) {
	a.events = append(a.events, event)

	for _, rule := range a.rules {
		if rule.Condition(event) {
			rule.Action(event)
		}
	}
}

func (a *SecurityAnalyzer) AnalyzePatterns() []SecurityAlert {
	alerts := make([]SecurityAlert, 0)

	// 检测暴力破解
	if failedAttempts := a.countFailedAuthAttempts(""); failedAttempts > 5 {
		alerts = append(alerts, SecurityAlert{
			Type:        "BRUTE_FORCE",
			Severity:    "HIGH",
			Description: fmt.Sprintf("检测到可能的暴力破解攻击，失败次数: %d", failedAttempts),
			Evidence:    fmt.Sprintf("%d failed attempts", failedAttempts),
		})
	}

	// 检测异常IP活动
	if suspiciousIPs := a.detectSuspiciousIPs(); len(suspiciousIPs) > 0 {
		for ip, count := range suspiciousIPs {
			alerts = append(alerts, SecurityAlert{
				Type:        "SUSPICIOUS_IP",
				Severity:    "MEDIUM",
				Description: fmt.Sprintf("IP %s 存在异常活动", ip),
				Evidence:    fmt.Sprintf("%d events", count),
			})
		}
	}

	return alerts
}

func (a *SecurityAnalyzer) countFailedAuthAttempts(userID string) int {
	count := 0
	for _, event := range a.events {
		if event.EventType == "LOGIN" {
			if success, ok := event.Details["success"].(bool); ok && !success {
				if userID == "" || event.UserID == userID {
					count++
				}
			}
		}
	}
	return count
}

func (a *SecurityAnalyzer) detectSuspiciousIPs() map[string]int {
	ipActivity := make(map[string]int)
	for _, event := range a.events {
		if event.Severity == "WARNING" || event.Severity == "ERROR" {
			ipActivity[event.SourceIP]++
		}
	}

	// 过滤出异常活跃的IP
	suspiciousIPs := make(map[string]int)
	for ip, count := range ipActivity {
		if count > 10 { // 阈值
			suspiciousIPs[ip] = count
		}
	}

	return suspiciousIPs
}

type SecurityAlert struct {
	Type        string
	Severity    string
	Description string
	Evidence    string
}
```

---

## 🎯 总结

### 安全最佳实践总结

1. **认证和授权**
   - 使用强密码哈希算法（Argon2id）
   - 实现多因素认证
   - 使用JWT或OAuth2.0进行API认证
   - 实施基于角色的访问控制（RBAC）

2. **输入验证**
   - 对所有用户输入进行严格验证
   - 使用参数化查询防止SQL注入
   - 实施XSS防护措施
   - 验证和清理文件上传

3. **网络安全**
   - 强制使用HTTPS和TLS 1.2+
   - 实施安全的HTTP头设置
   - 配置CORS策略
   - 实现限流和IP过滤

4. **密钥管理**
   - 使用安全的密钥存储方案
   - 定期轮换密钥和证书
   - 实施密钥分离原则
   - 使用安全的配置管理

5. **监控和日志**
   - 记录所有安全相关事件
   - 实施实时监控和告警
   - 定期进行安全审计
   - 建立事件响应流程

### Go安全开发检查清单

- [ ] 所有密码都使用Argon2id哈希存储
- [ ] 实施了完整的输入验证机制
- [ ] 所有SQL查询都使用参数化方式
- [ ] 配置了适当的安全HTTP头
- [ ] 实施了CSRF保护机制
- [ ] 所有敏感数据都经过加密传输
- [ ] 实施了限流和防攻击措施
- [ ] 建立了安全事件日志记录
- [ ] 定期进行安全测试和漏洞扫描
- [ ] 实施了最小权限原则

通过遵循这些安全最佳实践，你可以构建出更加安全可靠的Go应用程序，有效抵御常见的网络威胁和攻击。

---

*最后更新: 2025年9月*