# Go安全最佳实践

本文档详细介绍Go语言在Web开发中的安全最佳实践，包括认证授权、输入验证、数据保护、网络安全、常见漏洞防护等方面的内容。

## 1. 认证和授权

### 1.1 JWT认证实现

```go
package auth

import (
    "errors"
    "fmt"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/golang-jwt/jwt/v5"
)

type JWTConfig struct {
    SecretKey      string
    Issuer         string
    Audience       string
    TokenDuration  time.Duration
    RefreshDuration time.Duration
}

type Claims struct {
    UserID   string                 `json:"user_id"`
    Username string                 `json:"username"`
    Roles    []string               `json:"roles"`
    Custom   map[string]interface{} `json:"custom"`
    jwt.RegisteredClaims
}

type JWTManager struct {
    config *JWTConfig
}

func NewJWTManager(config *JWTConfig) *JWTManager {
    return &JWTManager{
        config: config,
    }
}

// 生成访问令牌
func (j *JWTManager) GenerateAccessToken(userID, username string, roles []string) (string, error) {
    claims := &Claims{
        UserID:   userID,
        Username: username,
        Roles:    roles,
        Custom:   make(map[string]interface{}),
        RegisteredClaims: jwt.RegisteredClaims{
            Issuer:    j.config.Issuer,
            Audience:  []string{j.config.Audience},
            ExpiresAt: jwt.NewNumericDate(time.Now().Add(j.config.TokenDuration)),
            IssuedAt:  jwt.NewNumericDate(time.Now()),
            NotBefore: jwt.NewNumericDate(time.Now()),
        },
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString([]byte(j.config.SecretKey))
}

// 生成刷新令牌
func (j *JWTManager) GenerateRefreshToken(userID string) (string, error) {
    claims := &jwt.RegisteredClaims{
        Subject:   userID,
        ExpiresAt: jwt.NewNumericDate(time.Now().Add(j.config.RefreshDuration)),
        IssuedAt:  jwt.NewNumericDate(time.Now()),
        NotBefore: jwt.NewNumericDate(time.Now()),
    }

    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString([]byte(j.config.SecretKey))
}

// 验证令牌
func (j *JWTManager) VerifyToken(tokenString string) (*Claims, error) {
    token, err := jwt.ParseWithClaims(tokenString, &Claims{}, func(token *jwt.Token) (interface{}, error) {
        // 验证签名算法
        if _, ok := token.Method.(*jwt.SigningMethodHMAC); !ok {
            return nil, fmt.Errorf("unexpected signing method: %v", token.Header["alg"])
        }
        return []byte(j.config.SecretKey), nil
    })

    if err != nil {
        return nil, err
    }

    claims, ok := token.Claims.(*Claims)
    if !ok || !token.Valid {
        return nil, errors.New("invalid token")
    }

    return claims, nil
}

// JWT中间件
func JWTMiddleware(jwtManager *JWTManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        authHeader := c.GetHeader("Authorization")
        if authHeader == "" {
            c.AbortWithStatusJSON(401, gin.H{"error": "Authorization header required"})
            return
        }

        // 提取Bearer token
        tokenString := authHeader
        if len(authHeader) > 7 && authHeader[:7] == "Bearer " {
            tokenString = authHeader[7:]
        }

        // 验证token
        claims, err := jwtManager.VerifyToken(tokenString)
        if err != nil {
            c.AbortWithStatusJSON(401, gin.H{"error": "Invalid token"})
            return
        }

        // 设置用户信息到上下文
        c.Set("user_id", claims.UserID)
        c.Set("username", claims.Username)
        c.Set("roles", claims.Roles)
        c.Set("claims", claims)

        c.Next()
    }
}

// 角色权限中间件
func RoleMiddleware(roles ...string) gin.HandlerFunc {
    return func(c *gin.Context) {
        userRoles, exists := c.Get("roles")
        if !exists {
            c.AbortWithStatusJSON(401, gin.H{"error": "User not authenticated"})
            return
        }

        roleList, ok := userRoles.([]string)
        if !ok {
            c.AbortWithStatusJSON(401, gin.H{"error": "Invalid user roles"})
            return
        }

        // 检查用户是否有任一所需角色
        hasRole := false
        for _, userRole := range roleList {
            for _, requiredRole := range roles {
                if userRole == requiredRole {
                    hasRole = true
                    break
                }
            }
            if hasRole {
                break
            }
        }

        if !hasRole {
            c.AbortWithStatusJSON(403, gin.H{"error": "Insufficient permissions"})
            return
        }

        c.Next()
    }
}
```

### 1.2 OAuth2集成

```go
package oauth2

import (
    "context"
    "encoding/json"
    "fmt"
    "io"
    "net/http"
    "net/url"

    "golang.org/x/oauth2"
    "golang.org/x/oauth2/google"
)

type OAuth2Config struct {
    ClientID     string
    ClientSecret string
    RedirectURL  string
    Scopes       []string
}

type OAuth2Manager struct {
    config *oauth2.Config
    provider string
}

func NewGoogleOAuth2Manager(oauthConfig *OAuth2Config) *OAuth2Manager {
    config := &oauth2.Config{
        ClientID:     oauthConfig.ClientID,
        ClientSecret: oauthConfig.ClientSecret,
        RedirectURL:  oauthConfig.RedirectURL,
        Scopes:       oauthConfig.Scopes,
        Endpoint:     google.Endpoint,
    }

    return &OAuth2Manager{
        config: config,
        provider: "google",
    }
}

func (m *OAuth2Manager) GetAuthURL(state string) string {
    return m.config.AuthCodeURL(state, oauth2.AccessTypeOffline)
}

func (m *OAuth2Manager) ExchangeCode(code string) (*oauth2.Token, error) {
    return m.config.Exchange(context.Background(), code)
}

func (m *OAuth2Manager) GetUserInfo(token *oauth2.Token) (*UserInfo, error) {
    client := m.config.Client(context.Background(), token)

    var userInfoURL string
    switch m.provider {
    case "google":
        userInfoURL = "https://www.googleapis.com/oauth2/v2/userinfo"
    default:
        return nil, fmt.Errorf("unsupported provider: %s", m.provider)
    }

    resp, err := client.Get(userInfoURL)
    if err != nil {
        return nil, err
    }
    defer resp.Body.Close()

    body, err := io.ReadAll(resp.Body)
    if err != nil {
        return nil, err
    }

    var userInfo UserInfo
    if err := json.Unmarshal(body, &userInfo); err != nil {
        return nil, err
    }

    return &userInfo, nil
}

type UserInfo struct {
    ID      string `json:"id"`
    Email   string `json:"email"`
    Name    string `json:"name"`
    Picture string `json:"picture"`
}

// OAuth2中间件
func OAuth2Middleware(manager *OAuth2Manager) gin.HandlerFunc {
    return func(c *gin.Context) {
        tokenString := c.GetHeader("Authorization")
        if tokenString == "" {
            c.AbortWithStatusJSON(401, gin.H{"error": "Authorization header required"})
            return
        }

        // 验证token
        token := &oauth2.Token{AccessToken: tokenString}
        userInfo, err := manager.GetUserInfo(token)
        if err != nil {
            c.AbortWithStatusJSON(401, gin.H{"error": "Invalid token"})
            return
        }

        // 设置用户信息到上下文
        c.Set("user_id", userInfo.ID)
        c.Set("user_email", userInfo.Email)
        c.Set("user_name", userInfo.Name)
        c.Set("user_info", userInfo)

        c.Next()
    }
}
```

## 2. 输入验证和清理

### 2.1 输入验证

```go
package validation

import (
    "fmt"
    "net/http"
    "regexp"
    "strings"
    "unicode"

    "github.com/gin-gonic/gin"
    "github.com/go-playground/validator/v10"
)

type Validator struct {
    validator *validator.Validate
}

func NewValidator() *Validator {
    return &Validator{
        validator: validator.New(),
    }
}

// 验证结构体
func (v *Validator) ValidateStruct(s interface{}) error {
    return v.validator.Struct(s)
}

// 自定义验证规则
func (v *Validator) RegisterCustomValidators() {
    // 密码强度验证
    v.validator.RegisterValidation("strong_password", func(fl validator.FieldLevel) bool {
        password := fl.Field().String()

        if len(password) < 8 {
            return false
        }

        hasUpper := false
        hasLower := false
        hasDigit := false
        hasSpecial := false

        for _, char := range password {
            switch {
            case unicode.IsUpper(char):
                hasUpper = true
            case unicode.IsLower(char):
                hasLower = true
            case unicode.IsDigit(char):
                hasDigit = true
            case unicode.IsPunct(char) || unicode.IsSymbol(char):
                hasSpecial = true
            }
        }

        return hasUpper && hasLower && hasDigit && hasSpecial
    })

    // 用户名验证
    v.validator.RegisterValidation("username", func(fl validator.FieldLevel) bool {
        username := fl.Field().String()

        if len(username) < 3 || len(username) > 20 {
            return false
        }

        // 只允许字母、数字、下划线
        match, _ := regexp.MatchString(`^[a-zA-Z0-9_]+$`, username)
        return match
    })

    // 安全字符串验证
    v.validator.RegisterValidation("safe_string", func(fl validator.FieldLevel) bool {
        str := fl.Field().String()

        // 检查潜在的XSS攻击
        xssPatterns := []string{
            `<script`, `</script>`, `javascript:`, `onload=`, `onerror=`,
            `onclick=`, `onmouseover=`, `alert(`, `eval(`, `document.`,
        }

        for _, pattern := range xssPatterns {
            if strings.Contains(strings.ToLower(str), pattern) {
                return false
            }
        }

        return true
    })
}

// 输入清理
func SanitizeInput(input string) string {
    // 移除危险字符
    dangerous := []string{
        "<", ">", "'", "\"", ";", "(", ")", "{", "}", "[", "]", "|", "&", "$",
        "`", "\\", "..", "/", "//", "/*", "*/", "--", "/*", "*/",
    }

    result := input
    for _, char := range dangerous {
        result = strings.ReplaceAll(result, char, "")
    }

    return result
}

// 文件名安全化
func SanitizeFilename(filename string) string {
    // 移除路径遍历字符
    filename = strings.ReplaceAll(filename, "../", "")
    filename = strings.ReplaceAll(filename, "..\\", "")
    filename = strings.ReplaceAll(filename, "/", "_")
    filename = strings.ReplaceAll(filename, "\\", "_")

    // 移除特殊字符
    reg := regexp.MustCompile(`[^\w\s.-]`)
    filename = reg.ReplaceAllString(filename, "_")

    return filename
}

// 中间件：输入验证
func ValidationMiddleware(validator *Validator) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 验证查询参数
        for key, values := range c.Request.URL.Query() {
            for _, value := range values {
                if !validator.IsValidInput(value) {
                    c.AbortWithStatusJSON(400, gin.H{
                        "error": fmt.Sprintf("Invalid input parameter: %s", key),
                    })
                    return
                }
            }
        }

        // 验证表单数据
        if c.Request.Method == "POST" || c.Request.Method == "PUT" {
            if err := c.Request.ParseForm(); err != nil {
                c.AbortWithStatusJSON(400, gin.H{"error": "Invalid form data"})
                return
            }

            for key, values := range c.Request.PostForm {
                for _, value := range values {
                    if !validator.IsValidInput(value) {
                        c.AbortWithStatusJSON(400, gin.H{
                            "error": fmt.Sprintf("Invalid form field: %s", key),
                        })
                        return
                    }
                }
            }
        }

        c.Next()
    }
}

// 检查输入是否有效
func (v *Validator) IsValidInput(input string) bool {
    // 检查输入长度
    if len(input) > 1000 { // 防止过长的输入
        return false
    }

    // 检查潜在的SQL注入
    sqlPatterns := []string{
        "SELECT ", "INSERT ", "UPDATE ", "DELETE ", "DROP ", "CREATE ",
        "ALTER ", "EXEC(", "UNION ", "WHERE ", "OR ", "AND ", "HAVING ",
    }

    inputUpper := strings.ToUpper(input)
    for _, pattern := range sqlPatterns {
        if strings.Contains(inputUpper, pattern) {
            return false
        }
    }

    // 检查潜在的XSS攻击
    xssPatterns := []string{
        "<script", "</script>", "javascript:", "onload=", "onerror=",
        "onclick=", "onmouseover=", "alert(", "eval(", "document.",
    }

    inputLower := strings.ToLower(input)
    for _, pattern := range xssPatterns {
        if strings.Contains(inputLower, pattern) {
            return false
        }
    }

    return true
}

// 使用示例
type UserInput struct {
    Username string `json:"username" binding:"required,username"`
    Email    string `json:"email" binding:"required,email"`
    Password string `json:"password" binding:"required,strong_password"`
    Age      int    `json:"age" binding:"required,gte=18,lte=120"`
    Bio      string `json:"bio" binding:"required,safe_string"`
}

func ValidationExample() {
    r := gin.Default()
    validator := NewValidator()
    validator.RegisterCustomValidators()

    r.POST("/register", func(c *gin.Context) {
        var input UserInput
        if err := c.ShouldBindJSON(&input); err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }

        // 验证通过，处理注册逻辑
        c.JSON(200, gin.H{"message": "User registered successfully"})
    })

    r.Run(":8080")
}
```

### 2.2 文件上传安全

```go
package upload

import (
    "bytes"
    "crypto/sha256"
    "encoding/hex"
    "fmt"
    "image"
    "image/jpeg"
    "image/png"
    "io"
    "mime/multipart"
    "net/http"
    "os"
    "path/filepath"
    "strings"

    "github.com/gin-gonic/gin"
)

type FileUploadConfig struct {
    MaxSize      int64   // 最大文件大小（字节）
    AllowedTypes []string // 允许的文件类型
    UploadDir    string  // 上传目录
    AllowedExts  []string // 允许的文件扩展名
}

type FileUploadManager struct {
    config *FileUploadConfig
}

func NewFileUploadManager(config *FileUploadConfig) *FileUploadManager {
    // 确保上传目录存在
    os.MkdirAll(config.UploadDir, 0755)

    return &FileUploadManager{
        config: config,
    }
}

// 安全文件上传
func (m *FileUploadManager) UploadFile(file *multipart.FileHeader) (string, error) {
    // 验证文件大小
    if file.Size > m.config.MaxSize {
        return "", fmt.Errorf("file size exceeds limit of %d bytes", m.config.MaxSize)
    }

    // 验证文件扩展名
    ext := strings.ToLower(filepath.Ext(file.Filename))
    if !m.isAllowedExtension(ext) {
        return "", fmt.Errorf("file extension %s is not allowed", ext)
    }

    // 验证文件类型
    f, err := file.Open()
    if err != nil {
        return "", err
    }
    defer f.Close()

    // 读取文件头进行类型检测
    buffer := make([]byte, 512)
    _, err = f.Read(buffer)
    if err != nil {
        return "", err
    }

    // 重置文件指针
    _, err = f.Seek(0, 0)
    if err != nil {
        return "", err
    }

    // 验证文件内容类型
    contentType := http.DetectContentType(buffer)
    if !m.isAllowedContentType(contentType) {
        return "", fmt.Errorf("file content type %s is not allowed", contentType)
    }

    // 对于图片文件，进行额外的验证
    if m.isImageType(contentType) {
        if err := m.validateImage(f); err != nil {
            return "", err
        }
        _, err = f.Seek(0, 0)
        if err != nil {
            return "", err
        }
    }

    // 生成安全的文件名
    safeFilename := m.generateSafeFilename(file.Filename, ext)

    // 计算文件哈希
    hash, err := m.calculateFileHash(f)
    if err != nil {
        return "", err
    }

    // 保存文件
    filePath := filepath.Join(m.config.UploadDir, safeFilename)
    if err := m.saveFile(f, filePath); err != nil {
        return "", err
    }

    return safeFilename, nil
}

// 验证图片文件
func (m *FileUploadManager) validateImage(f io.Reader) error {
    // 尝试解码图片
    _, format, err := image.DecodeConfig(f)
    if err != nil {
        return fmt.Errorf("invalid image file: %v", err)
    }

    // 检查图片格式
    allowedFormats := []string{"jpeg", "png", "gif"}
    isAllowed := false
    for _, allowedFormat := range allowedFormats {
        if strings.ToLower(format) == allowedFormat {
            isAllowed = true
            break
        }
    }

    if !isAllowed {
        return fmt.Errorf("image format %s is not allowed", format)
    }

    return nil
}

// 生成安全的文件名
func (m *FileUploadManager) generateSafeFilename(originalName, ext string) string {
    // 使用原始文件名（安全化处理）
    name := strings.TrimSuffix(originalName, ext)
    safeName := sanitizeFilename(name)

    // 添加时间戳和随机数
    timestamp := time.Now().Unix()
    random := rand.Intn(10000)

    return fmt.Sprintf("%s_%d_%d%s", safeName, timestamp, random, ext)
}

// 计算文件哈希
func (m *FileUploadManager) calculateFileHash(f io.Reader) (string, error) {
    hasher := sha256.New()
    if _, err := io.Copy(hasher, f); err != nil {
        return "", err
    }

    return hex.EncodeToString(hasher.Sum(nil)), nil
}

// 保存文件
func (m *FileUploadManager) saveFile(f multipart.File, filePath string) error {
    // 创建目标文件
    dst, err := os.Create(filePath)
    if err != nil {
        return err
    }
    defer dst.Close()

    // 复制文件内容
    if _, err := io.Copy(dst, f); err != nil {
        return err
    }

    // 设置文件权限
    return os.Chmod(filePath, 0644)
}

// 检查是否允许的扩展名
func (m *FileUploadManager) isAllowedExtension(ext string) bool {
    for _, allowedExt := range m.config.AllowedExts {
        if strings.ToLower(ext) == strings.ToLower(allowedExt) {
            return true
        }
    }
    return false
}

// 检查是否允许的内容类型
func (m *FileUploadManager) isAllowedContentType(contentType string) bool {
    for _, allowedType := range m.config.AllowedTypes {
        if strings.Contains(contentType, allowedType) {
            return true
        }
    }
    return false
}

// 检查是否为图片类型
func (m *FileUploadManager) isImageType(contentType string) bool {
    imageTypes := []string{"image/", "jpeg", "png", "gif"}
    for _, imageType := range imageTypes {
        if strings.Contains(contentType, imageType) {
            return true
        }
    }
    return false
}

// 文件名安全化
func sanitizeFilename(filename string) string {
    // 移除路径信息
    filename = filepath.Base(filename)

    // 移除特殊字符
    reg := regexp.MustCompile(`[^\w\s.-]`)
    filename = reg.ReplaceAllString(filename, "_")

    // 移除连续的下划线
    reg = regexp.MustCompile(`_+`)
    filename = reg.ReplaceAllString(filename, "_")

    // 移除前后的下划线和空格
    filename = strings.TrimSpace(filename)
    filename = strings.Trim(filename, "_")

    return filename
}

// 上传中间件
func FileUploadMiddleware(manager *FileUploadManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 检查是否为文件上传请求
        if !strings.Contains(c.GetHeader("Content-Type"), "multipart/form-data") {
            c.Next()
            return
        }

        // 限制请求大小
        c.Request.Body = http.MaxBytesReader(c.Writer, c.Request.Body, manager.config.MaxSize)

        // 解析multipart表单
        if err := c.Request.ParseMultipartForm(manager.config.MaxSize); err != nil {
            c.AbortWithStatusJSON(413, gin.H{"error": "Request too large"})
            return
        }

        // 验证上传的文件
        files := c.Request.MultipartForm.File
        for fieldName, fileHeaders := range files {
            for _, fileHeader := range fileHeaders {
                if err := manager.validateFileHeader(fileHeader); err != nil {
                    c.AbortWithStatusJSON(400, gin.H{
                        "error": fmt.Sprintf("Invalid file %s: %v", fieldName, err),
                    })
                    return
                }
            }
        }

        c.Next()
    }
}

// 验证文件头
func (m *FileUploadManager) validateFileHeader(fileHeader *multipart.FileHeader) error {
    // 验证文件大小
    if fileHeader.Size > m.config.MaxSize {
        return fmt.Errorf("file too large")
    }

    // 验证文件扩展名
    ext := strings.ToLower(filepath.Ext(fileHeader.Filename))
    if !m.isAllowedExtension(ext) {
        return fmt.Errorf("file extension not allowed")
    }

    return nil
}

// 使用示例
func FileUploadExample() {
    r := gin.Default()

    config := &FileUploadConfig{
        MaxSize:      10 * 1024 * 1024, // 10MB
        AllowedTypes: []string{"image/", "text/plain", "application/pdf"},
        UploadDir:    "./uploads",
        AllowedExts:  []string{".jpg", ".jpeg", ".png", ".gif", ".txt", ".pdf"},
    }

    manager := NewFileUploadManager(config)

    r.POST("/upload", FileUploadMiddleware(manager), func(c *gin.Context) {
        file, err := c.FormFile("file")
        if err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }

        filename, err := manager.UploadFile(file)
        if err != nil {
            c.JSON(400, gin.H{"error": err.Error()})
            return
        }

        c.JSON(200, gin.H{
            "message":  "File uploaded successfully",
            "filename": filename,
            "size":     file.Size,
        })
    })

    r.Run(":8080")
}
```

## 3. 数据保护

### 3.1 密码安全

```go
package security

import (
    "crypto/rand"
    "encoding/hex"
    "fmt"
    "golang.org/x/crypto/bcrypt"
    "golang.org/x/crypto/scrypt"
)

type PasswordManager struct {
    bcryptCost int
}

func NewPasswordManager() *PasswordManager {
    return &PasswordManager{
        bcryptCost: 12, // bcrypt cost参数
    }
}

// 使用bcrypt哈希密码
func (p *PasswordManager) HashPassword(password string) (string, error) {
    hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), p.bcryptCost)
    if err != nil {
        return "", err
    }
    return string(hashedPassword), nil
}

// 验证密码
func (p *PasswordManager) VerifyPassword(password, hashedPassword string) error {
    return bcrypt.CompareHashAndPassword([]byte(hashedPassword), []byte(password))
}

// 使用scrypt哈希密码（更安全但更慢）
func (p *PasswordManager) HashPasswordScrypt(password string) (string, error) {
    // 生成随机salt
    salt := make([]byte, 32)
    if _, err := rand.Read(salt); err != nil {
        return "", err
    }

    // scrypt参数
    N := 32768
    r := 8
    p_param := 1
    keyLen := 64

    // 生成哈希
    hash, err := scrypt.Key([]byte(password), salt, N, r, p_param, keyLen)
    if err != nil {
        return "", err
    }

    // 组合salt和hash
    result := append(salt, hash...)
    return hex.EncodeToString(result), nil
}

// 验证scrypt密码
func (p *PasswordManager) VerifyPasswordScrypt(password, hashedPassword string) error {
    // 解码哈希值
    decoded, err := hex.DecodeString(hashedPassword)
    if err != nil {
        return err
    }

    // 提取salt和hash
    if len(decoded) < 32 {
        return fmt.Errorf("invalid hashed password")
    }

    salt := decoded[:32]
    expectedHash := decoded[32:]

    // 生成哈希并比较
    N := 32768
    r := 8
    p_param := 1
    keyLen := 64

    hash, err := scrypt.Key([]byte(password), salt, N, r, p_param, keyLen)
    if err != nil {
        return err
    }

    if len(hash) != len(expectedHash) {
        return fmt.Errorf("password mismatch")
    }

    for i := range hash {
        if hash[i] != expectedHash[i] {
            return fmt.Errorf("password mismatch")
        }
    }

    return nil
}

// 生成随机密码
func (p *PasswordManager) GenerateRandomPassword(length int) (string, error) {
    const charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>?"

    password := make([]byte, length)
    for i := range password {
        num, err := rand.Int(rand.Reader, big.NewInt(int64(len(charset))))
        if err != nil {
            return "", err
        }
        password[i] = charset[num.Int64()]
    }

    return string(password), nil
}

// 检查密码强度
func (p *PasswordManager) CheckPasswordStrength(password string) error {
    if len(password) < 8 {
        return fmt.Errorf("password must be at least 8 characters long")
    }

    var hasUpper, hasLower, hasDigit, hasSpecial bool

    for _, char := range password {
        switch {
        case unicode.IsUpper(char):
            hasUpper = true
        case unicode.IsLower(char):
            hasLower = true
        case unicode.IsDigit(char):
            hasDigit = true
        case unicode.IsPunct(char) || unicode.IsSymbol(char):
            hasSpecial = true
        }
    }

    if !hasUpper {
        return fmt.Errorf("password must contain at least one uppercase letter")
    }
    if !hasLower {
        return fmt.Errorf("password must contain at least one lowercase letter")
    }
    if !hasDigit {
        return fmt.Errorf("password must contain at least one digit")
    }
    if !hasSpecial {
        return fmt.Errorf("password must contain at least one special character")
    }

    return nil
}

// 使用示例
func PasswordExample() {
    passwordManager := NewPasswordManager()

    // 哈希密码
    password := "MySecurePassword123!"
    hashedPassword, err := passwordManager.HashPassword(password)
    if err != nil {
        panic(err)
    }

    // 验证密码
    err = passwordManager.VerifyPassword(password, hashedPassword)
    if err != nil {
        panic(err)
    }

    // 检查密码强度
    err = passwordManager.CheckPasswordStrength(password)
    if err != nil {
        panic(err)
    }

    // 生成随机密码
    randomPassword, err := passwordManager.GenerateRandomPassword(16)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Random password: %s\n", randomPassword)
}
```

### 3.2 数据加密

```go
package encryption

import (
    "crypto/aes"
    "crypto/cipher"
    "crypto/rand"
    "crypto/rsa"
    "crypto/sha256"
    "crypto/x509"
    "encoding/base64"
    "encoding/pem"
    "errors"
    "fmt"
    "io"
)

type AESEncryptor struct {
    key []byte
}

func NewAESEncryptor(key string) (*AESEncryptor, error) {
    // AES-256需要32字节的key
    if len(key) < 32 {
        return nil, errors.New("key must be at least 32 characters long")
    }

    // 使用SHA-256生成固定长度的key
    hash := sha256.Sum256([]byte(key))

    return &AESEncryptor{
        key: hash[:],
    }, nil
}

// 加密数据
func (a *AESEncryptor) Encrypt(plaintext []byte) ([]byte, error) {
    block, err := aes.NewCipher(a.key)
    if err != nil {
        return nil, err
    }

    // 创建GCM模式的加密器
    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }

    // 生成nonce
    nonce := make([]byte, gcm.NonceSize())
    if _, err = io.ReadFull(rand.Reader, nonce); err != nil {
        return nil, err
    }

    // 加密
    ciphertext := gcm.Seal(nonce, nonce, plaintext, nil)

    return ciphertext, nil
}

// 解密数据
func (a *AESEncryptor) Decrypt(ciphertext []byte) ([]byte, error) {
    block, err := aes.NewCipher(a.key)
    if err != nil {
        return nil, err
    }

    gcm, err := cipher.NewGCM(block)
    if err != nil {
        return nil, err
    }

    nonceSize := gcm.NonceSize()
    if len(ciphertext) < nonceSize {
        return nil, errors.New("ciphertext too short")
    }

    nonce, ciphertext := ciphertext[:nonceSize], ciphertext[nonceSize:]

    plaintext, err := gcm.Open(nil, nonce, ciphertext, nil)
    if err != nil {
        return nil, err
    }

    return plaintext, nil
}

// 加密字符串
func (a *AESEncryptor) EncryptString(plaintext string) (string, error) {
    ciphertext, err := a.Encrypt([]byte(plaintext))
    if err != nil {
        return "", err
    }

    return base64.StdEncoding.EncodeToString(ciphertext), nil
}

// 解密字符串
func (a *AESEncryptor) DecryptString(ciphertext string) (string, error) {
    data, err := base64.StdEncoding.DecodeString(ciphertext)
    if err != nil {
        return "", err
    }

    plaintext, err := a.Decrypt(data)
    if err != nil {
        return "", err
    }

    return string(plaintext), nil
}

type RSAEncryptor struct {
    privateKey *rsa.PrivateKey
    publicKey  *rsa.PublicKey
}

func NewRSAEncryptor() (*RSAEncryptor, error) {
    // 生成RSA密钥对
    privateKey, err := rsa.GenerateKey(rand.Reader, 2048)
    if err != nil {
        return nil, err
    }

    return &RSAEncryptor{
        privateKey: privateKey,
        publicKey:  &privateKey.PublicKey,
    }, nil
}

// 从PEM字符串加载私钥
func NewRSAEncryptorFromPEM(privateKeyPEM string) (*RSAEncryptor, error) {
    block, _ := pem.Decode([]byte(privateKeyPEM))
    if block == nil {
        return nil, errors.New("failed to decode PEM block")
    }

    privateKey, err := x509.ParsePKCS1PrivateKey(block.Bytes)
    if err != nil {
        return nil, err
    }

    return &RSAEncryptor{
        privateKey: privateKey,
        publicKey:  &privateKey.PublicKey,
    }, nil
}

// 使用公钥加密
func (r *RSAEncryptor) Encrypt(plaintext []byte) ([]byte, error) {
    hash := sha256.New()
    return rsa.EncryptOAEP(hash, rand.Reader, r.publicKey, plaintext, nil)
}

// 使用私钥解密
func (r *RSAEncryptor) Decrypt(ciphertext []byte) ([]byte, error) {
    hash := sha256.New()
    return rsa.DecryptOAEP(hash, rand.Reader, r.privateKey, ciphertext, nil)
}

// 导出公钥为PEM格式
func (r *RSAEncryptor) ExportPublicKey() (string, error) {
    pubBytes, err := x509.MarshalPKIXPublicKey(r.publicKey)
    if err != nil {
        return "", err
    }

    pubBlock := &pem.Block{
        Type:  "PUBLIC KEY",
        Bytes: pubBytes,
    }

    return string(pem.EncodeToMemory(pubBlock)), nil
}

// 导出私钥为PEM格式
func (r *RSAEncryptor) ExportPrivateKey() (string, error) {
    privBytes := x509.MarshalPKCS1PrivateKey(r.privateKey)

    privBlock := &pem.Block{
        Type:  "RSA PRIVATE KEY",
        Bytes: privBytes,
    }

    return string(pem.EncodeToMemory(privBlock)), nil
}

// 使用示例
func EncryptionExample() {
    // AES加密
    aesKey := "my-secret-key-for-aes-encryption-123456"
    aesEncryptor, err := NewAESEncryptor(aesKey)
    if err != nil {
        panic(err)
    }

    plaintext := "This is a secret message"
    encrypted, err := aesEncryptor.EncryptString(plaintext)
    if err != nil {
        panic(err)
    }

    decrypted, err := aesEncryptor.DecryptString(encrypted)
    if err != nil {
        panic(err)
    }

    fmt.Printf("Original: %s\n", plaintext)
    fmt.Printf("Encrypted: %s\n", encrypted)
    fmt.Printf("Decrypted: %s\n", decrypted)

    // RSA加密
    rsaEncryptor, err := NewRSAEncryptor()
    if err != nil {
        panic(err)
    }

    rsaEncrypted, err := rsaEncryptor.Encrypt([]byte("Secret RSA message"))
    if err != nil {
        panic(err)
    }

    rsaDecrypted, err := rsaEncryptor.Decrypt(rsaEncrypted)
    if err != nil {
        panic(err)
    }

    fmt.Printf("RSA Decrypted: %s\n", string(rsaDecrypted))
}
```

## 4. 网络安全

### 4.1 安全头部设置

```go
package middleware

import (
    "github.com/gin-gonic/gin"
)

// 安全头部中间件
func SecurityHeadersMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 防止MIME类型嗅探
        c.Header("X-Content-Type-Options", "nosniff")

        // 防止点击劫持
        c.Header("X-Frame-Options", "DENY")

        // 启用XSS保护
        c.Header("X-XSS-Protection", "1; mode=block")

        // 强制HTTPS
        c.Header("Strict-Transport-Security", "max-age=31536000; includeSubDomains; preload")

        // 内容安全策略
        c.Header("Content-Security-Policy", "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self'; frame-src 'none'; object-src 'none'")

        // 引用策略
        c.Header("Referrer-Policy", "strict-origin-when-cross-origin")

        // 权限策略
        c.Header("Permissions-Policy", "camera=(), microphone=(), geolocation=(), payment=()")

        // 缓存控制
        c.Header("Cache-Control", "no-cache, no-store, must-revalidate")
        c.Header("Pragma", "no-cache")
        c.Header("Expires", "0")

        // 移除服务器信息
        c.Header("Server", "")

        c.Next()
    }
}

// CORS中间件
func CORSMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Header("Access-Control-Allow-Origin", "*")
        c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
        c.Header("Access-Control-Allow-Headers", "Origin, Content-Type, Accept, Authorization")
        c.Header("Access-Control-Max-Age", "86400")

        if c.Request.Method == "OPTIONS" {
            c.AbortWithStatus(204)
            return
        }

        c.Next()
    }
}

// HTTPS重定向中间件
func HTTPSRedirectMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        if c.Request.TLS == nil {
            // 重定向到HTTPS
            url := "https://" + c.Request.Host + c.Request.URL.Path
            if c.Request.URL.RawQuery != "" {
                url += "?" + c.Request.URL.RawQuery
            }

            c.Redirect(http.StatusMovedPermanently, url)
            c.Abort()
            return
        }

        c.Next()
    }
}
```

### 4.2 速率限制

```go
package ratelimit

import (
    "net/http"
    "time"

    "github.com/gin-gonic/gin"
    "github.com/go-redis/redis/v8"
    "golang.org/x/time/rate"
)

// 基于内存的速率限制
type MemoryRateLimiter struct {
    limiters map[string]*rate.Limiter
    mu       sync.Mutex
}

func NewMemoryRateLimiter() *MemoryRateLimiter {
    return &MemoryRateLimiter{
        limiters: make(map[string]*rate.Limiter),
    }
}

func (m *MemoryRateLimiter) GetLimiter(key string, r rate.Limit, b int) *rate.Limiter {
    m.mu.Lock()
    defer m.mu.Unlock()

    if limiter, exists := m.limiters[key]; exists {
        return limiter
    }

    limiter := rate.NewLimiter(r, b)
    m.limiters[key] = limiter
    return limiter
}

func (m *MemoryRateLimiter) Middleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        key := c.ClientIP()
        limiter := m.GetLimiter(key, rate.Limit(10), 20) // 每秒10个请求，突发20个

        if !limiter.Allow() {
            c.AbortWithStatusJSON(429, gin.H{
                "error": "Rate limit exceeded",
            })
            return
        }

        c.Next()
    }
}

// 基于Redis的分布式速率限制
type RedisRateLimiter struct {
    client *redis.Client
}

func NewRedisRateLimiter(client *redis.Client) *RedisRateLimiter {
    return &RedisRateLimiter{
        client: client,
    }
}

func (r *RedisRateLimiter) Middleware(window time.Duration, limit int) gin.HandlerFunc {
    return func(c *gin.Context) {
        key := "rate_limit:" + c.ClientIP()
        now := time.Now().Unix()
        windowStart := now - int64(window.Seconds())

        // 移除窗口外的请求记录
        r.client.ZRemRangeByScore(c.Request.Context(), key, "0", fmt.Sprint(windowStart))

        // 添加当前请求
        r.client.ZAdd(c.Request.Context(), key, &redis.Z{Score: float64(now), Member: now})

        // 获取当前窗口内的请求数
        count, err := r.client.ZCount(c.Request.Context(), key, fmt.Sprint(windowStart), "+inf").Result()
        if err != nil {
            c.AbortWithStatusJSON(500, gin.H{"error": "Rate limit check failed"})
            return
        }

        if int(count) > limit {
            c.AbortWithStatusJSON(429, gin.H{
                "error": "Rate limit exceeded",
                "limit": limit,
                "window": window.String(),
            })
            return
        }

        // 设置过期时间
        r.client.Expire(c.Request.Context(), key, window)

        c.Next()
    }
}

// 使用示例
func RateLimitExample() {
    r := gin.Default()

    // 使用内存速率限制
    memoryLimiter := NewMemoryRateLimiter()
    r.Use(memoryLimiter.Middleware())

    // 或者使用Redis速率限制
    // redisClient := redis.NewClient(&redis.Options{Addr: "localhost:6379"})
    // redisLimiter := NewRedisRateLimiter(redisClient)
    // r.Use(redisLimiter.Middleware(1*time.Minute, 100))

    r.GET("/api/test", func(c *gin.Context) {
        c.JSON(200, gin.H{"message": "Hello, World!"})
    })

    r.Run(":8080")
}
```

## 5. 常见漏洞防护

### 5.1 SQL注入防护

```go
package sql

import (
    "database/sql"
    "fmt"
    "strings"

    "github.com/gin-gonic/gin"
)

// 安全的查询构建器
type SafeQueryBuilder struct {
    query   strings.Builder
    args    []interface{}
    where   strings.Builder
    orderBy strings.Builder
    limit   string
    offset  string
}

func NewSafeQueryBuilder() *SafeQueryBuilder {
    return &SafeQueryBuilder{
        args: make([]interface{}, 0),
    }
}

func (b *SafeQueryBuilder) Select(columns ...string) *SafeQueryBuilder {
    b.query.WriteString("SELECT ")
    b.query.WriteString(strings.Join(columns, ", "))
    return b
}

func (b *SafeQueryBuilder) From(table string) *SafeQueryBuilder {
    b.query.WriteString(" FROM ")
    b.query.WriteString(table)
    return b
}

func (b *SafeQueryBuilder) Where(condition string, args ...interface{}) *SafeQueryBuilder {
    if b.where.Len() == 0 {
        b.where.WriteString(" WHERE ")
    } else {
        b.where.WriteString(" AND ")
    }
    b.where.WriteString(condition)
    b.args = append(b.args, args...)
    return b
}

func (b *SafeQueryBuilder) OrWhere(condition string, args ...interface{}) *SafeQueryBuilder {
    if b.where.Len() == 0 {
        b.where.WriteString(" WHERE ")
    } else {
        b.where.WriteString(" OR ")
    }
    b.where.WriteString(condition)
    b.args = append(b.args, args...)
    return b
}

func (b *SafeQueryBuilder) OrderBy(column string, direction string) *SafeQueryBuilder {
    // 验证排序方向
    if direction != "ASC" && direction != "DESC" {
        direction = "ASC"
    }

    // 验证列名（防止SQL注入）
    if !isValidColumn(column) {
        column = "id"
    }

    if b.orderBy.Len() == 0 {
        b.orderBy.WriteString(" ORDER BY ")
    } else {
        b.orderBy.WriteString(", ")
    }
    b.orderBy.WriteString(column)
    b.orderBy.WriteString(" ")
    b.orderBy.WriteString(direction)
    return b
}

func (b *SafeQueryBuilder) Limit(limit int) *SafeQueryBuilder {
    b.limit = fmt.Sprintf(" LIMIT %d", limit)
    return b
}

func (b *SafeQueryBuilder) Offset(offset int) *SafeQueryBuilder {
    b.offset = fmt.Sprintf(" OFFSET %d", offset)
    return b
}

func (b *SafeQueryBuilder) Build() (string, []interface{}) {
    query := b.query.String()
    query += b.where.String()
    query += b.orderBy.String()
    query += b.limit
    query += b.offset

    return query, b.args
}

// 验证列名是否安全
func isValidColumn(column string) bool {
    // 允许的字符
    allowedChars := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

    for _, char := range column {
        if !strings.ContainsRune(allowedChars, char) {
            return false
        }
    }

    // 检查保留字
    reservedWords := []string{
        "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "CREATE", "ALTER",
        "UNION", "OR", "AND", "WHERE", "HAVING", "GROUP", "ORDER",
    }

    upperColumn := strings.ToUpper(column)
    for _, word := range reservedWords {
        if upperColumn == word {
            return false
        }
    }

    return true
}

// 安全的查询执行
func SafeQuery(db *sql.DB, query string, args ...interface{}) (*sql.Rows, error) {
    // 验证查询是否包含危险的关键字
    dangerousKeywords := []string{
        "DROP ", "DELETE ", "UPDATE ", "INSERT ", "CREATE ", "ALTER ",
        "UNION ", "OR ", "AND ", "HAVING ", "GROUP ", "ORDER ",
    }

    upperQuery := strings.ToUpper(query)
    for _, keyword := range dangerousKeywords {
        if strings.Contains(upperQuery, keyword) {
            return nil, fmt.Errorf("query contains dangerous keyword: %s", keyword)
        }
    }

    return db.Query(query, args...)
}

// 安全的查询执行（单行）
func SafeQueryRow(db *sql.DB, query string, args ...interface{}) *sql.Row {
    // 验证查询
    dangerousKeywords := []string{
        "DROP ", "DELETE ", "UPDATE ", "INSERT ", "CREATE ", "ALTER ",
        "UNION ", "OR ", "AND ", "HAVING ", "GROUP ", "ORDER ",
    }

    upperQuery := strings.ToUpper(query)
    for _, keyword := range dangerousKeywords {
        if strings.Contains(upperQuery, keyword) {
            return db.QueryRow("SELECT 1") // 返回空结果
        }
    }

    return db.QueryRow(query, args...)
}

// 使用示例
func SQLExample() {
    db, err := sql.Open("postgres", "your-connection-string")
    if err != nil {
        panic(err)
    }
    defer db.Close()

    // 构建安全查询
    builder := NewSafeQueryBuilder().
        Select("id", "name", "email").
        From("users").
        Where("active = ?", true).
        Where("age > ?", 18).
        OrderBy("created_at", "DESC").
        Limit(10)

    query, args := builder.Build()

    rows, err := SafeQuery(db, query, args...)
    if err != nil {
        panic(err)
    }
    defer rows.Close()

    // 处理结果
    for rows.Next() {
        var id int
        var name, email string
        if err := rows.Scan(&id, &name, &email); err != nil {
            panic(err)
        }
        fmt.Printf("User: %d, %s, %s\n", id, name, email)
    }
}
```

### 5.2 XSS防护

```go
package xss

import (
    "html"
    "regexp"
    "strings"

    "github.com/gin-gonic/gin"
)

// HTML清理器
type HTMLCleaner struct {
    allowedTags map[string]bool
    allowedAttrs map[string]bool
}

func NewHTMLCleaner() *HTMLCleaner {
    return &HTMLCleaner{
        allowedTags: map[string]bool{
            "p": true, "br": true, "strong": true, "em": true,
            "u": true, "ol": true, "ul": true, "li": true,
            "blockquote": true, "code": true, "pre": true,
        },
        allowedAttrs: map[string]bool{
            "href": true, "title": true, "alt": true,
        },
    }
}

// 清理HTML内容
func (c *HTMLCleaner) CleanHTML(htmlContent string) string {
    // 移除危险的事件处理器
    content := c.removeEventHandlers(htmlContent)

    // 移除危险的属性
    content = c.removeDangerousAttributes(content)

    // 移除危险的标签
    content = c.removeDangerousTags(content)

    // HTML转义剩余的内容
    content = html.EscapeString(content)

    return content
}

// 移除事件处理器
func (c *HTMLCleaner) removeEventHandlers(content string) string {
    eventPatterns := []string{
        `on\w+\s*=`, `javascript:`, `data:`, `vbscript:`,
        `onload=`, `onerror=`, `onclick=`, `onmouseover=`,
    }

    result := content
    for _, pattern := range eventPatterns {
        re := regexp.MustCompile(`(?i)`+pattern)
        result = re.ReplaceAllString(result, "")
    }

    return result
}

// 移除危险的属性
func (c *HTMLCleaner) removeDangerousAttributes(content string) string {
    dangerousAttrs := []string{
        "style", "class", "id", "name", "onclick",
        "ondblclick", "onmousedown", "onmouseup", "onmouseover",
        "onmousemove", "onmouseout", "onkeypress", "onkeydown",
        "onkeyup", "onfocus", "onblur", "onchange", "onselect",
        "onsubmit", "onreset", "onabort", "onerror",
    }

    result := content
    for _, attr := range dangerousAttrs {
        re := regexp.MustCompile(`(?i)`+attr+`\s*=\s*["'][^"']*["']`)
        result = re.ReplaceAllString(result, "")
    }

    return result
}

// 移除危险的标签
func (c *HTMLCleaner) removeDangerousTags(content string) string {
    dangerousTags := []string{
        "script", "iframe", "object", "embed", "applet",
        "form", "input", "button", "select", "textarea",
        "meta", "link", "base", "style",
    }

    result := content
    for _, tag := range dangerousTags {
        re := regexp.MustCompile(`(?i)<`+tag+`[^>]*>.*?</`+tag+`>`)
        result = re.ReplaceAllString(result, "")

        re = regexp.MustCompile(`(?i)<`+tag+`[^>]*/>`)
        result = re.ReplaceAllString(result, "")
    }

    return result
}

// XSS防护中间件
func XSSProtectionMiddleware(cleaner *HTMLCleaner) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 清理查询参数
        if err := c.Request.ParseForm(); err == nil {
            for key, values := range c.Request.Form {
                cleanedValues := make([]string, len(values))
                for i, value := range values {
                    cleanedValues[i] = cleaner.CleanHTML(value)
                }
                c.Request.Form[key] = cleanedValues
            }
        }

        // 清理POST数据
        if c.Request.Method == "POST" || c.Request.Method == "PUT" {
            if err := c.Request.ParseForm(); err == nil {
                for key, values := range c.Request.PostForm {
                    cleanedValues := make([]string, len(values))
                    for i, value := range values {
                        cleanedValues[i] = cleaner.CleanHTML(value)
                    }
                    c.Request.PostForm[key] = cleanedValues
                }
            }
        }

        c.Next()
    }
}

// 安全的JSON响应
func SafeJSONResponse(c *gin.Context, data interface{}) {
    // 设置内容类型
    c.Header("Content-Type", "application/json; charset=utf-8")

    // 添加XSS保护头
    c.Header("X-Content-Type-Options", "nosniff")

    c.JSON(200, data)
}

// 使用示例
func XSSExample() {
    r := gin.Default()
    cleaner := NewHTMLCleaner()

    // 使用XSS防护中间件
    r.Use(XSSProtectionMiddleware(cleaner))

    r.POST("/comment", func(c *gin.Context) {
        var comment struct {
            Content string `json:"content"`
        }

        if err := c.ShouldBindJSON(&comment); err != nil {
            SafeJSONResponse(c, gin.H{"error": err.Error()})
            return
        }

        // 清理HTML内容
        cleanedContent := cleaner.CleanHTML(comment.Content)

        // 存储清理后的内容
        // storeComment(cleanedContent)

        SafeJSONResponse(c, gin.H{
            "message": "Comment posted successfully",
            "content": cleanedContent,
        })
    })

    r.Run(":8080")
}
```

## 6. 安全监控和审计

### 6.1 安全日志记录

```go
package logging

import (
    "encoding/json"
    "log"
    "os"
    "time"

    "github.com/gin-gonic/gin"
)

type SecurityLogger struct {
    file *os.File
    logger *log.Logger
}

type SecurityEvent struct {
    Timestamp   time.Time              `json:"timestamp"`
    Level       string                 `json:"level"`
    EventType   string                 `json:"event_type"`
    Message     string                 `json:"message"`
    IPAddress   string                 `json:"ip_address"`
    UserAgent   string                 `json:"user_agent"`
    UserID      string                 `json:"user_id,omitempty"`
    RequestURI  string                 `json:"request_uri"`
    Method      string                 `json:"method"`
    Details     map[string]interface{} `json:"details,omitempty"`
}

func NewSecurityLogger(logFile string) (*SecurityLogger, error) {
    file, err := os.OpenFile(logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
    if err != nil {
        return nil, err
    }

    return &SecurityLogger{
        file:   file,
        logger: log.New(file, "", log.LstdFlags),
    }, nil
}

func (s *SecurityLogger) LogSecurityEvent(event *SecurityEvent) error {
    event.Timestamp = time.Now()

    data, err := json.Marshal(event)
    if err != nil {
        return err
    }

    s.logger.Println(string(data))
    return nil
}

func (s *SecurityLogger) LogAuthFailure(ip, userAgent, message string, details map[string]interface{}) {
    event := &SecurityEvent{
        Level:      "WARNING",
        EventType:  "AUTH_FAILURE",
        Message:    message,
        IPAddress:  ip,
        UserAgent:  userAgent,
        Details:    details,
    }

    s.LogSecurityEvent(event)
}

func (s *SecurityLogger) LogAuthSuccess(userID, ip, userAgent string) {
    event := &SecurityEvent{
        Level:      "INFO",
        EventType:  "AUTH_SUCCESS",
        Message:    "User authentication successful",
        IPAddress:  ip,
        UserAgent:  userAgent,
        UserID:     userID,
    }

    s.LogSecurityEvent(event)
}

func (s *SecurityLogger) LogSecurityThreat(ip, userAgent, requestURI, method, threatType string) {
    event := &SecurityEvent{
        Level:      "ERROR",
        EventType:  "SECURITY_THREAT",
        Message:    "Potential security threat detected",
        IPAddress:  ip,
        UserAgent:  userAgent,
        RequestURI: requestURI,
        Method:     method,
        Details:    map[string]interface{}{"threat_type": threatType},
    }

    s.LogSecurityEvent(event)
}

func (s *SecurityLogger) LogAccessViolation(ip, userAgent, requestURI, method, violation string) {
    event := &SecurityEvent{
        Level:      "ERROR",
        EventType:  "ACCESS_VIOLATION",
        Message:    "Access violation detected",
        IPAddress:  ip,
        UserAgent:  userAgent,
        RequestURI: requestURI,
        Method:     method,
        Details:    map[string]interface{}{"violation": violation},
    }

    s.LogSecurityEvent(event)
}

func (s *SecurityLogger) Close() error {
    return s.file.Close()
}

// 安全监控中间件
func SecurityMonitoringMiddleware(logger *SecurityLogger) gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        // 记录请求开始
        c.Set("request_start", start)

        c.Next()

        // 记录请求完成
        duration := time.Since(start)
        statusCode := c.Writer.Status()

        // 检查异常行为
        if statusCode >= 400 {
            event := &SecurityEvent{
                Level:      "WARNING",
                EventType:  "HTTP_ERROR",
                Message:    fmt.Sprintf("HTTP error response: %d", statusCode),
                IPAddress:  c.ClientIP(),
                UserAgent:  c.Request.UserAgent(),
                RequestURI: c.Request.URL.Path,
                Method:     c.Request.Method,
                Details: map[string]interface{}{
                    "status_code": statusCode,
                    "duration":   duration.String(),
                },
            }
            logger.LogSecurityEvent(event)
        }

        // 检查异常长的请求时间
        if duration > 5*time.Second {
            event := &SecurityEvent{
                Level:      "WARNING",
                EventType:  "SLOW_REQUEST",
                Message:    "Slow request detected",
                IPAddress:  c.ClientIP(),
                UserAgent:  c.Request.UserAgent(),
                RequestURI: c.Request.URL.Path,
                Method:     c.Request.Method,
                Details: map[string]interface{}{
                    "duration": duration.String(),
                },
            }
            logger.LogSecurityEvent(event)
        }
    }
}

// 检测潜在攻击的中间件
func AttackDetectionMiddleware(logger *SecurityLogger) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 检查SQL注入
        if s.detectSQLInjection(c.Request) {
            logger.LogSecurityThreat(
                c.ClientIP(),
                c.Request.UserAgent(),
                c.Request.URL.Path,
                c.Request.Method,
                "SQL_INJECTION",
            )
            c.AbortWithStatusJSON(403, gin.H{"error": "Security threat detected"})
            return
        }

        // 检查XSS攻击
        if s.detectXSS(c.Request) {
            logger.LogSecurityThreat(
                c.ClientIP(),
                c.Request.UserAgent(),
                c.Request.URL.Path,
                c.Request.Method,
                "XSS_ATTACK",
            )
            c.AbortWithStatusJSON(403, gin.H{"error": "Security threat detected"})
            return
        }

        // 检查路径遍历攻击
        if s.detectPathTraversal(c.Request) {
            logger.LogSecurityThreat(
                c.ClientIP(),
                c.Request.UserAgent(),
                c.Request.URL.Path,
                c.Request.Method,
                "PATH_TRAVERSAL",
            )
            c.AbortWithStatusJSON(403, gin.H{"error": "Security threat detected"})
            return
        }

        c.Next()
    }
}

// 检测SQL注入
func (s *SecurityLogger) detectSQLInjection(r *http.Request) bool {
    patterns := []string{
        "SELECT ", "INSERT ", "UPDATE ", "DELETE ", "DROP ", "CREATE ",
        "UNION ", "OR ", "AND ", "HAVING ", "WHERE ", "--", "/*", "*/",
        "1=1", "1=2", "SLEEP(", "WAITFOR DELAY", "BENCHMARK(",
    }

    checkString := func(str string) bool {
        upperStr := strings.ToUpper(str)
        for _, pattern := range patterns {
            if strings.Contains(upperStr, pattern) {
                return true
            }
        }
        return false
    }

    // 检查查询参数
    for _, values := range r.URL.Query() {
        for _, value := range values {
            if checkString(value) {
                return true
            }
        }
    }

    // 检查POST数据
    if err := r.ParseForm(); err == nil {
        for _, values := range r.PostForm {
            for _, value := range values {
                if checkString(value) {
                    return true
                }
            }
        }
    }

    return false
}

// 检测XSS攻击
func (s *SecurityLogger) detectXSS(r *http.Request) bool {
    patterns := []string{
        "<script", "</script>", "javascript:", "onload=", "onerror=",
        "onclick=", "onmouseover=", "alert(", "eval(", "document.",
        "window.", "String.fromCharCode", "fromCharCode",
    }

    checkString := func(str string) bool {
        lowerStr := strings.ToLower(str)
        for _, pattern := range patterns {
            if strings.Contains(lowerStr, pattern) {
                return true
            }
        }
        return false
    }

    // 检查查询参数
    for _, values := range r.URL.Query() {
        for _, value := range values {
            if checkString(value) {
                return true
            }
        }
    }

    // 检查POST数据
    if err := r.ParseForm(); err == nil {
        for _, values := range r.PostForm {
            for _, value := range values {
                if checkString(value) {
                    return true
                }
            }
        }
    }

    return false
}

// 检测路径遍历攻击
func (s *SecurityLogger) detectPathTraversal(r *http.Request) bool {
    patterns := []string{
        "../", "..\\", "..;/", "%2e%2e%2f", "%2e%2e/",
        "..%2f", "..%5c", "%2e%2e%5c",
    }

    checkString := func(str string) bool {
        for _, pattern := range patterns {
            if strings.Contains(str, pattern) {
                return true
            }
        }
        return false
    }

    // 检查URL路径
    if checkString(r.URL.Path) {
        return true
    }

    // 检查查询参数
    for _, values := range r.URL.Query() {
        for _, value := range values {
            if checkString(value) {
                return true
            }
        }
    }

    return false
}

// 使用示例
func SecurityLoggingExample() {
    r := gin.Default()

    // 初始化安全日志记录器
    logger, err := NewSecurityLogger("security.log")
    if err != nil {
        panic(err)
    }
    defer logger.Close()

    // 使用安全监控中间件
    r.Use(SecurityMonitoringMiddleware(logger))
    r.Use(AttackDetectionMiddleware(logger))

    r.POST("/login", func(c *gin.Context) {
        var login struct {
            Username string `json:"username"`
            Password string `json:"password"`
        }

        if err := c.ShouldBindJSON(&login); err != nil {
            logger.LogAuthFailure(
                c.ClientIP(),
                c.Request.UserAgent(),
                "Login failed: invalid input",
                map[string]interface{}{"username": login.Username},
            )
            c.JSON(400, gin.H{"error": "Invalid input"})
            return
        }

        // 验证用户
        if login.Username == "admin" && login.Password == "password" {
            logger.LogAuthSuccess("1", c.ClientIP(), c.Request.UserAgent())
            c.JSON(200, gin.H{"message": "Login successful"})
        } else {
            logger.LogAuthFailure(
                c.ClientIP(),
                c.Request.UserAgent(),
                "Login failed: invalid credentials",
                map[string]interface{}{"username": login.Username},
            )
            c.JSON(401, gin.H{"error": "Invalid credentials"})
        }
    })

    r.Run(":8080")
}
```

## 7. 安全最佳实践总结

### 7.1 认证授权最佳实践

1. **密码安全**
   - 使用强哈希算法（bcrypt、scrypt）
   - 实现密码强度检查
   - 定期更新密码策略
   - 启用多因素认证

2. **令牌管理**
   - 使用HTTPS传输令牌
   - 设置合理的令牌过期时间
   - 实现令牌刷新机制
   - 安全存储令牌

3. **会话管理**
   - 使用安全的会话标识符
   - 设置会话超时
   - 实现会话固定防护
   - 记录会话活动

### 7.2 输入验证最佳实践

1. **输入清理**
   - 验证所有用户输入
   - 移除危险字符
   - 限制输入长度
   - 使用参数化查询

2. **文件上传安全**
   - 验证文件类型和扩展名
   - 限制文件大小
   - 使用安全的文件名
   - 隔离上传文件

3. **输出编码**
   - 对输出进行HTML编码
   - 使用安全的JSON编码
   - 实现CSP策略
   - 防止XSS攻击

### 7.3 数据保护最佳实践

1. **加密存储**
   - 加密敏感数据
   - 使用强加密算法
   - 安全管理密钥
   - 定期更新密钥

2. **传输安全**
   - 使用HTTPS
   - 实现HSTS
   - 验证证书
   - 使用安全的协议

3. **访问控制**
   - 实现最小权限原则
   - 定期审计权限
   - 监控异常访问
   - 记录访问日志

### 7.4 网络安全最佳实践

1. **安全头部**
   - 设置安全HTTP头部
   - 实现CORS策略
   - 启用XSS保护
   - 防止点击劫持

2. **速率限制**
   - 实现请求速率限制
   - 防止暴力破解
   - 监控异常请求
   - 实现IP黑名单

3. **监控和审计**
   - 记录安全事件
   - 监控异常行为
   - 定期安全审计
   - 实时告警机制

通过遵循这些安全最佳实践，你可以构建安全可靠的Go Web应用程序，有效防范各种安全威胁。