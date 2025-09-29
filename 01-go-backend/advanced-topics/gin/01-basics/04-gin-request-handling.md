# Gin请求处理与响应

## 目录
- [请求处理概述](#请求处理概述)
- [请求对象处理](#请求对象处理)
- [参数绑定与验证](#参数绑定与验证)
- [响应生成与格式化](#响应生成与格式化)
- [文件上传处理](#文件上传处理)
- [错误处理机制](#错误处理机制)
- [中间件集成](#中间件集成)
- [最佳实践](#最佳实践)

## 请求处理概述

### Gin请求处理流程
```go
package main

import (
    "github.com/gin-gonic/gin"
    "net/http"
)

func main() {
    // 创建Gin引擎
    r := gin.Default()

    // 注册路由
    r.GET("/users", GetUsers)
    r.POST("/users", CreateUser)
    r.GET("/users/:id", GetUser)
    r.PUT("/users/:id", UpdateUser)
    r.DELETE("/users/:id", DeleteUser)

    // 启动服务器
    r.Run(":8080")
}

// 请求处理函数示例
func GetUser(c *gin.Context) {
    // 从路径参数获取ID
    id := c.Param("id")

    // 从查询参数获取字段
    fields := c.DefaultQuery("fields", "id,name,email")

    // 从请求头获取信息
    token := c.GetHeader("Authorization")

    // 处理业务逻辑
    user, err := userService.GetUser(id, fields)
    if err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
        return
    }

    // 返回响应
    c.JSON(http.StatusOK, gin.H{"data": user})
}
```

## 请求对象处理

### 1. 路径参数处理
```go
// 单个路径参数
func GetUserProfile(c *gin.Context) {
    userID := c.Param("id")
    c.JSON(http.StatusOK, gin.H{"user_id": userID})
}

// 多个路径参数
func GetUserPost(c *gin.Context) {
    userID := c.Param("id")
    postID := c.Param("post_id")
    c.JSON(http.StatusOK, gin.H{
        "user_id":  userID,
        "post_id":  postID,
    })
}

// 通配符路由
func GetWildcardUser(c *gin.Context) {
    path := c.Param("*1") // 捕获所有剩余路径
    c.JSON(http.StatusOK, gin.H{"path": path})
}

// 注册路由
r.GET("/users/:id", GetUserProfile)
r.GET("/users/:id/posts/:post_id", GetUserPost)
r.GET("/users/*any", GetWildcardUser)
```

### 2. 查询参数处理
```go
// 基本查询参数
func SearchUsers(c *gin.Context) {
    query := c.Query("q")
    page := c.DefaultQuery("page", "1")
    limit := c.DefaultQuery("limit", "10")
    sort := c.Query("sort")

    c.JSON(http.StatusOK, gin.H{
        "query": query,
        "page":  page,
        "limit": limit,
        "sort":  sort,
    })
}

// 获取所有查询参数
func GetAllQueryParams(c *gin.Context) {
    // 获取所有查询参数
    params := c.Request.URL.Query()

    // 遍历查询参数
    for key, values := range params {
        for _, value := range values {
            fmt.Printf("Key: %s, Value: %s\n", key, value)
        }
    }

    c.JSON(http.StatusOK, gin.H{"params": params})
}

// 数组查询参数
func GetUsersByIDs(c *gin.Context) {
    // 获取数组参数: /users?ids=1&ids=2&ids=3
    ids := c.QueryArray("ids")

    // 获取逗号分隔的数组: /users?ids=1,2,3
    ids2 := c.Query("ids")
    if ids2 != "" {
        // 分割字符串
        idList := strings.Split(ids2, ",")
        ids = append(ids, idList...)
    }

    c.JSON(http.StatusOK, gin.H{"user_ids": ids})
}
```

### 3. 请求头处理
```go
// 基本请求头
func GetHeaders(c *gin.Context) {
    userAgent := c.GetHeader("User-Agent")
    accept := c.GetHeader("Accept")
    contentType := c.GetHeader("Content-Type")
    authorization := c.GetHeader("Authorization")

    c.JSON(http.StatusOK, gin.H{
        "user_agent":     userAgent,
        "accept":         accept,
        "content_type":   contentType,
        "authorization":  authorization,
    })
}

// 自定义请求头处理
func ProcessCustomHeaders(c *gin.Context) {
    // 获取自定义请求头
    requestID := c.GetHeader("X-Request-ID")
    correlationID := c.GetHeader("X-Correlation-ID")
    userID := c.GetHeader("X-User-ID")

    // 处理请求
    c.Set("request_id", requestID)
    c.Set("correlation_id", correlationID)
    c.Set("user_id", userID)

    c.JSON(http.StatusOK, gin.H{
        "message": "Headers processed",
        "request_id": requestID,
    })
}

// 必需请求头验证
func RequireAuthHeader(c *gin.Context) {
    auth := c.GetHeader("Authorization")
    if auth == "" {
        c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
        c.Abort()
        return
    }

    // 验证token
    if !isValidToken(auth) {
        c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid token"})
        c.Abort()
        return
    }

    c.Next()
}

func isValidToken(token string) bool {
    // 实现token验证逻辑
    return strings.HasPrefix(token, "Bearer ")
}
```

## 参数绑定与验证

### 1. 结构体绑定
```go
// 用户模型
type User struct {
    ID        string `json:"id" form:"id"`
    Name      string `json:"name" form:"name" binding:"required,min=2,max=100"`
    Email     string `json:"email" form:"email" binding:"required,email"`
    Age       int    `json:"age" form:"age" binding:"min=18,max=120"`
    Password  string `json:"password" form:"password" binding:"required,min=6"`
    IsActive  bool   `json:"is_active" form:"is_active"`
}

// JSON请求绑定
func CreateUser(c *gin.Context) {
    var user User

    // 绑定JSON请求体
    if err := c.ShouldBindJSON(&user); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 处理业务逻辑
    if err := userService.CreateUser(&user); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
        return
    }

    c.JSON(http.StatusCreated, gin.H{"data": user})
}

// 表单数据绑定
func UpdateUserForm(c *gin.Context) {
    var user User

    // 绑定表单数据
    if err := c.ShouldBind(&user); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 处理业务逻辑
    if err := userService.UpdateUser(&user); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to update user"})
        return
    }

    c.JSON(http.StatusOK, gin.H{"data": user})
}

// 查询参数绑定
func GetUserByQuery(c *gin.Context) {
    var query struct {
        Name   string `form:"name"`
        Email  string `form:"email"`
        Active bool   `form:"active"`
        Page   int    `form:"page" binding:"min=1"`
        Limit  int    `form:"limit" binding:"min=1,max=100"`
    }

    // 绑定查询参数
    if err := c.ShouldBindQuery(&query); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 处理查询
    users, err := userService.GetUsers(query.Name, query.Email, query.Active, query.Page, query.Limit)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get users"})
        return
    }

    c.JSON(http.StatusOK, gin.H{"data": users})
}
```

### 2. 自定义验证
```go
// 自定义验证器
type UserValidator struct {
    User User
}

func (v *UserValidator) Validate() error {
    // 自定义验证逻辑
    if v.User.Name == "" {
        return errors.New("name is required")
    }

    if len(v.User.Password) < 8 {
        return errors.New("password must be at least 8 characters")
    }

    if !strings.Contains(v.User.Password, "!@#$%^&*") {
        return errors.New("password must contain special characters")
    }

    return nil
}

// 使用自定义验证器
func CreateUserWithCustomValidation(c *gin.Context) {
    var user User

    if err := c.ShouldBindJSON(&user); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 自定义验证
    validator := UserValidator{User: user}
    if err := validator.Validate(); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 处理业务逻辑
    if err := userService.CreateUser(&user); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
        return
    }

    c.JSON(http.StatusCreated, gin.H{"data": user})
}
```

### 3. 高级绑定技巧
```go
// 嵌套结构体绑定
type Address struct {
    Street  string `json:"street" binding:"required"`
    City    string `json:"city" binding:"required"`
    State   string `json:"state" binding:"required"`
    ZipCode string `json:"zip_code" binding:"required"`
}

type UserWithAddress struct {
    User
    Address Address `json:"address" binding:"required"`
}

func CreateUserWithAddress(c *gin.Context) {
    var user UserWithAddress

    if err := c.ShouldBindJSON(&user); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 处理业务逻辑
    if err := userService.CreateUserWithAddress(&user); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
        return
    }

    c.JSON(http.StatusCreated, gin.H{"data": user})
}

// 数组绑定
type CreateUsersRequest struct {
    Users []User `json:"users" binding:"required,min=1,max=100"`
}

func CreateUsersBatch(c *gin.Context) {
    var request CreateUsersRequest

    if err := c.ShouldBindJSON(&request); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 处理批量创建
    createdUsers, err := userService.CreateUsersBatch(request.Users)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create users"})
        return
    }

    c.JSON(http.StatusCreated, gin.H{"data": createdUsers})
}

// 文件上传绑定
type UploadRequest struct {
    Title       string                `form:"title" binding:"required"`
    Description string                `form:"description"`
    File        *multipart.FileHeader `form:"file" binding:"required"`
}

func UploadFile(c *gin.Context) {
    var request UploadRequest

    // 绑定表单数据和文件
    if err := c.ShouldBind(&request); err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
        return
    }

    // 保存文件
    filename := filepath.Base(request.File.Filename)
    if err := c.SaveUploadedFile(request.File, "uploads/"+filename); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
        return
    }

    // 处理业务逻辑
    fileRecord := &File{
        Title:       request.Title,
        Description: request.Description,
        Filename:    filename,
        Size:        request.File.Size,
        CreatedAt:   time.Now(),
    }

    if err := fileService.CreateFile(fileRecord); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create file record"})
        return
    }

    c.JSON(http.StatusCreated, gin.H{"data": fileRecord})
}
```

## 响应生成与格式化

### 1. JSON响应
```go
// 基本JSON响应
func GetBasicJSON(c *gin.Context) {
    c.JSON(http.StatusOK, gin.H{
        "message": "Hello, World!",
        "status":  "success",
        "data":    []string{"item1", "item2", "item3"},
    })
}

// 结构化JSON响应
type APIResponse struct {
    Success bool        `json:"success"`
    Message string        `json:"message"`
    Data    interface{} `json:"data,omitempty"`
    Errors  []string     `json:"errors,omitempty"`
}

func GetStructuredResponse(c *gin.Context) {
    users, err := userService.GetAllUsers()
    if err != nil {
        response := APIResponse{
            Success: false,
            Message: "Failed to get users",
            Errors:  []string{err.Error()},
        }
        c.JSON(http.StatusInternalServerError, response)
        return
    }

    response := APIResponse{
        Success: true,
        Message: "Users retrieved successfully",
        Data:    users,
    }
    c.JSON(http.StatusOK, response)
}

// 分页JSON响应
type PaginationResponse struct {
    Success bool        `json:"success"`
    Message string        `json:"message"`
    Data    interface{} `json:"data"`
    Meta    PaginationMeta `json:"meta"`
}

type PaginationMeta struct {
    CurrentPage int `json:"current_page"`
    PerPage     int `json:"per_page"`
    TotalPages  int `json:"total_pages"`
    TotalItems  int `json:"total_items"`
}

func GetPaginatedUsers(c *gin.Context) {
    page := c.DefaultQuery("page", "1")
    limit := c.DefaultQuery("limit", "10")

    // 获取分页数据
    users, total, err := userService.GetPaginatedUsers(page, limit)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
        return
    }

    // 计算分页元数据
    currentPage, _ := strconv.Atoi(page)
    perPage, _ := strconv.Atoi(limit)
    totalPages := (total + perPage - 1) / perPage

    response := PaginationResponse{
        Success: true,
        Message: "Users retrieved successfully",
        Data:    users,
        Meta: PaginationMeta{
            CurrentPage: currentPage,
            PerPage:     perPage,
            TotalPages:  totalPages,
            TotalItems:  total,
        },
    }

    c.JSON(http.StatusOK, response)
}
```

### 2. 其他格式响应
```go
// XML响应
func GetXMLResponse(c *gin.Context) {
    type User struct {
        ID    string `xml:"id"`
        Name  string `xml:"name"`
        Email string `xml:"email"`
    }

    user := User{ID: "1", Name: "John Doe", Email: "john@example.com"}
    c.XML(http.StatusOK, user)
}

// YAML响应
func GetYAMLResponse(c *gin.Context) {
    c.YAML(http.StatusOK, gin.H{
        "message": "Hello, YAML!",
        "status":  "success",
        "data":    map[string]interface{}{"key": "value"},
    })
}

// 纯文本响应
func GetTextResponse(c *gin.Context) {
    c.String(http.StatusOK, "Hello, World!")
}

// HTML响应
func GetHTMLResponse(c *gin.Context) {
    c.HTML(http.StatusOK, "index.tmpl", gin.H{
        "title": "Welcome",
        "message": "Hello, World!",
    })
}

// 文件响应
func DownloadFile(c *gin.Context) {
    filename := "example.txt"
    content := []byte("This is the file content")

    c.Header("Content-Description", "File Transfer")
    c.Header("Content-Transfer-Encoding", "binary")
    c.Header("Content-Disposition", "attachment; filename="+filename)
    c.Data(http.StatusOK, "application/octet-stream", content)
}

// 流式响应
func StreamResponse(c *gin.Context) {
    c.Stream(func(w io.Writer) bool {
        // 模拟数据流
        data := fmt.Sprintf("Data chunk: %d\n", time.Now().Unix())
        w.Write([]byte(data))
        time.Sleep(1 * time.Second)
        return true // 继续流式传输
    })
}
```

### 3. 响应头设置
```go
// 设置响应头
func SetResponseHeaders(c *gin.Context) {
    // 设置基本响应头
    c.Header("Content-Type", "application/json")
    c.Header("X-Custom-Header", "custom-value")
    c.Header("Cache-Control", "no-cache, no-store, must-revalidate")
    c.Header("Pragma", "no-cache")
    c.Header("Expires", "0")

    // 设置CORS头
    c.Header("Access-Control-Allow-Origin", "*")
    c.Header("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
    c.Header("Access-Control-Allow-Headers", "Content-Type, Authorization")

    c.JSON(http.StatusOK, gin.H{"message": "Headers set"})
}

// 条件响应头
func ConditionalResponse(c *gin.Context) {
    user, err := userService.GetUser(c.Param("id"))
    if err != nil {
        c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
        return
    }

    // 设置ETag
    etag := fmt.Sprintf(`"%d"`, user.UpdatedAt.Unix())
    c.Header("ETag", etag)

    // 检查If-None-Match
    ifNoneMatch := c.GetHeader("If-None-Match")
    if ifNoneMatch == etag {
        c.Status(http.StatusNotModified)
        return
    }

    c.JSON(http.StatusOK, user)
}

// 缓存控制
func CacheControlResponse(c *gin.Context) {
    // 设置缓存策略
    c.Header("Cache-Control", "public, max-age=3600")
    c.Header("Last-Modified", time.Now().Format(time.RFC1123))
    c.Header("Vary", "Accept-Encoding")

    c.JSON(http.StatusOK, gin.H{"message": "Cached response"})
}
```

## 文件上传处理

### 1. 单文件上传
```go
// 基本文件上传
func UploadSingleFile(c *gin.Context) {
    file, err := c.FormFile("file")
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "No file uploaded"})
        return
    }

    // 验证文件大小
    if file.Size > 10*1024*1024 { // 10MB
        c.JSON(http.StatusBadRequest, gin.H{"error": "File too large"})
        return
    }

    // 验证文件类型
    if !isValidFileType(file.Filename) {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid file type"})
        return
    }

    // 保存文件
    filename := generateUniqueFilename(file.Filename)
    if err := c.SaveUploadedFile(file, "uploads/"+filename); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
        return
    }

    // 返回成功响应
    c.JSON(http.StatusOK, gin.H{
        "message": "File uploaded successfully",
        "filename": filename,
        "size":     file.Size,
    })
}

func isValidFileType(filename string) bool {
    ext := strings.ToLower(filepath.Ext(filename))
    allowed := []string{".jpg", ".jpeg", ".png", ".gif", ".pdf", ".doc", ".docx"}

    for _, allowedExt := range allowed {
        if ext == allowedExt {
            return true
        }
    }
    return false
}

func generateUniqueFilename(original string) string {
    ext := filepath.Ext(original)
    name := strings.TrimSuffix(original, ext)
    timestamp := time.Now().Unix()
    return fmt.Sprintf("%s_%d%s", name, timestamp, ext)
}
```

### 2. 多文件上传
```go
// 多文件上传
func UploadMultipleFiles(c *gin.Context) {
    form, err := c.MultipartForm()
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "Failed to parse form"})
        return
    }

    files := form.File["files"]
    if len(files) == 0 {
        c.JSON(http.StatusBadRequest, gin.H{"error": "No files uploaded"})
        return
    }

    var uploadedFiles []gin.H
    var uploadErrors []string

    for _, file := range files {
        // 验证文件
        if file.Size > 10*1024*1024 {
            uploadErrors = append(uploadErrors, fmt.Sprintf("File %s too large", file.Filename))
            continue
        }

        if !isValidFileType(file.Filename) {
            uploadErrors = append(uploadErrors, fmt.Sprintf("Invalid file type: %s", file.Filename))
            continue
        }

        // 保存文件
        filename := generateUniqueFilename(file.Filename)
        if err := c.SaveUploadedFile(file, "uploads/"+filename); err != nil {
            uploadErrors = append(uploadErrors, fmt.Sprintf("Failed to save %s", file.Filename))
            continue
        }

        uploadedFiles = append(uploadedFiles, gin.H{
            "filename": filename,
            "size":     file.Size,
            "original": file.Filename,
        })
    }

    response := gin.H{
        "uploaded_files": uploadedFiles,
        "upload_errors":  uploadErrors,
        "total_uploaded": len(uploadedFiles),
        "total_errors":   len(uploadErrors),
    }

    c.JSON(http.StatusOK, response)
}
```

### 3. 高级文件处理
```go
// 文件元数据提取
func UploadWithMetadata(c *gin.Context) {
    file, err := c.FormFile("file")
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "No file uploaded"})
        return
    }

    // 获取文件信息
    fileInfo := gin.H{
        "filename":    file.Filename,
        "size":        file.Size,
        "header":      file.Header,
        "content_type": file.Header.Get("Content-Type"),
    }

    // 保存文件
    filename := generateUniqueFilename(file.Filename)
    if err := c.SaveUploadedFile(file, "uploads/"+filename); err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
        return
    }

    // 获取文件hash
    filePath := "uploads/" + filename
    fileHash, err := calculateFileHash(filePath)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to calculate file hash"})
        return
    }

    response := gin.H{
        "message": "File uploaded successfully",
        "file_info": fileInfo,
        "hash":     fileHash,
        "filename": filename,
    }

    c.JSON(http.StatusOK, response)
}

func calculateFileHash(filePath string) (string, error) {
    file, err := os.Open(filePath)
    if err != nil {
        return "", err
    }
    defer file.Close()

    hash := sha256.New()
    if _, err := io.Copy(hash, file); err != nil {
        return "", err
    }

    return hex.EncodeToString(hash.Sum(nil)), nil
}

// 流式文件处理
func StreamFileUpload(c *gin.Context) {
    // 获取上传的文件
    file, header, err := c.Request.FormFile("file")
    if err != nil {
        c.JSON(http.StatusBadRequest, gin.H{"error": "No file uploaded"})
        return
    }
    defer file.Close()

    // 创建目标文件
    filename := generateUniqueFilename(header.Filename)
    dest, err := os.Create("uploads/" + filename)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create destination file"})
        return
    }
    defer dest.Close()

    // 流式复制文件
    buffer := make([]byte, 32*1024) // 32KB buffer
    written, err := io.CopyBuffer(dest, file, buffer)
    if err != nil {
        c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to save file"})
        return
    }

    c.JSON(http.StatusOK, gin.H{
        "message": "File uploaded successfully",
        "filename": filename,
        "bytes_written": written,
    })
}
```

## 错误处理机制

### 1. 统一错误处理
```go
// 自定义错误类型
type AppError struct {
    Code    int    `json:"code"`
    Message string `json:"message"`
    Details string `json:"details,omitempty"`
}

func (e *AppError) Error() string {
    return e.Message
}

// 错误响应中间件
func ErrorHandlerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        c.Next()

        // 检查是否有错误
        if len(c.Errors) > 0 {
            err := c.Errors.Last().Err

            // 处理自定义错误
            if appErr, ok := err.(*AppError); ok {
                c.JSON(appErr.Code, appErr)
                return
            }

            // 处理验证错误
            if validationErr, ok := err.(validator.ValidationErrors); ok {
                c.JSON(http.StatusBadRequest, gin.H{
                    "code":    400,
                    "message": "Validation failed",
                    "details": formatValidationErrors(validationErr),
                })
                return
            }

            // 处理其他错误
            c.JSON(http.StatusInternalServerError, gin.H{
                "code":    500,
                "message": "Internal server error",
                "details": err.Error(),
            })
        }
    }
}

func formatValidationErrors(errs validator.ValidationErrors) []string {
    var errors []string
    for _, err := range errs {
        errors = append(errors, fmt.Sprintf("%s: %s", err.Field(), err.Tag()))
    }
    return errors
}
```

### 2. 业务错误处理
```go
// 业务错误类型
const (
    ErrCodeUserNotFound      = 1001
    ErrCodeInvalidInput      = 1002
    ErrCodeDatabaseError     = 1003
    ErrCodeUnauthorized     = 1004
    ErrCodeForbidden        = 1005
)

// 业务错误工厂
func NewUserNotFoundError(id string) *AppError {
    return &AppError{
        Code:    ErrCodeUserNotFound,
        Message: "User not found",
        Details: fmt.Sprintf("User with ID %s does not exist", id),
    }
}

func NewInvalidInputError(field, message string) *AppError {
    return &AppError{
        Code:    ErrCodeInvalidInput,
        Message: "Invalid input",
        Details: fmt.Sprintf("%s: %s", field, message),
    }
}

func NewDatabaseError(err error) *AppError {
    return &AppError{
        Code:    ErrCodeDatabaseError,
        Message: "Database error",
        Details: err.Error(),
    }
}

// 错误处理示例
func GetUserWithErrorHandling(c *gin.Context) {
    userID := c.Param("id")

    user, err := userService.GetUser(userID)
    if err != nil {
        if errors.Is(err, ErrUserNotFound) {
            c.Error(NewUserNotFoundError(userID))
            return
        }

        c.Error(NewDatabaseError(err))
        return
    }

    c.JSON(http.StatusOK, gin.H{"data": user})
}
```

## 中间件集成

### 1. 请求日志中间件
```go
// 请求日志中间件
func RequestLoggerMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        raw := c.Request.URL.RawQuery

        // 处理请求
        c.Next()

        // 记录日志
        latency := time.Since(start)
        clientIP := c.ClientIP()
        method := c.Request.Method
        statusCode := c.Writer.Status()
        bodySize := c.Writer.Size()

        log.Printf("[GIN] %s | %3d | %13v | %15s | %-7s %s %s",
            time.Now().Format("2006/01/02 - 15:04:05"),
            statusCode,
            latency,
            clientIP,
            method,
            path,
            raw,
        )
    }
}
```

### 2. 响应时间中间件
```go
// 响应时间中间件
func ResponseTimeMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()

        // 记录开始时间
        c.Set("start_time", start)

        // 处理请求
        c.Next()

        // 计算响应时间
        duration := time.Since(start)

        // 在响应头中添加响应时间
        c.Header("X-Response-Time", fmt.Sprintf("%dms", duration.Milliseconds()))

        // 记录慢请求
        if duration > 500*time.Millisecond {
            log.Printf("Slow request: %s %s took %v", c.Request.Method, c.Request.URL.Path, duration)
        }
    }
}
```

### 3. 请求ID中间件
```go
// 请求ID中间件
func RequestIDMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 生成请求ID
        requestID := c.GetHeader("X-Request-ID")
        if requestID == "" {
            requestID = generateRequestID()
        }

        // 设置请求ID到上下文
        c.Set("request_id", requestID)

        // 在响应头中添加请求ID
        c.Header("X-Request-ID", requestID)

        c.Next()
    }
}

func generateRequestID() string {
    return uuid.New().String()
}
```

## 最佳实践

### 1. 性能优化
```go
// 响应压缩中间件
func CompressionMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 检查是否支持压缩
        acceptEncoding := c.GetHeader("Accept-Encoding")
        supportsGzip := strings.Contains(acceptEncoding, "gzip")

        if supportsGzip {
            c.Header("Content-Encoding", "gzip")
            c.Header("Vary", "Accept-Encoding")
        }

        c.Next()
    }
}

// 请求限制中间件
func RateLimitMiddleware() gin.HandlerFunc {
    limiter := rate.NewLimiter(rate.Limit(100), 10) // 100 requests per second, burst of 10

    return func(c *gin.Context) {
        if !limiter.Allow() {
            c.JSON(http.StatusTooManyRequests, gin.H{"error": "Rate limit exceeded"})
            c.Abort()
            return
        }

        c.Next()
    }
}
```

### 2. 安全最佳实践
```go
// 安全响应头中间件
func SecurityHeadersMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 设置安全响应头
        c.Header("X-Content-Type-Options", "nosniff")
        c.Header("X-Frame-Options", "DENY")
        c.Header("X-XSS-Protection", "1; mode=block")
        c.Header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
        c.Header("Content-Security-Policy", "default-src 'self'")

        c.Next()
    }
}

// 输入验证中间件
func InputValidationMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 验证所有输入
        if c.Request.Method != "GET" && c.Request.Method != "HEAD" {
            contentType := c.GetHeader("Content-Type")
            if contentType != "" && !strings.Contains(contentType, "application/json") {
                c.JSON(http.StatusUnsupportedMediaType, gin.H{"error": "Unsupported media type"})
                c.Abort()
                return
            }
        }

        c.Next()
    }
}
```

### 3. 监控和追踪
```go
// 监控中间件
func MetricsMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        start := time.Now()
        path := c.Request.URL.Path
        method := c.Request.Method

        c.Next()

        duration := time.Since(start)
        statusCode := c.Writer.Status()

        // 记录指标
        metrics.RecordRequest(method, path, statusCode, duration)

        // 记录追踪
        if requestID, exists := c.Get("request_id"); exists {
            metrics.RecordTrace(requestID.(string), method, path, statusCode, duration)
        }
    }
}
```

这个Gin请求处理文档提供了全面的请求处理指南，包括参数绑定、验证、响应生成、文件上传、错误处理和中间件集成。通过这些技术和最佳实践，可以构建高效、安全、可维护的Gin Web应用。