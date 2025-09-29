# Gin模板引擎与高级渲染技术

## 📚 目录

- [模板引擎基础](#模板引擎基础)
- [HTML模板渲染](#html模板渲染)
- [模板继承与布局](#模板继承与布局)
- [自定义模板函数](#自定义模板函数)
- [模板数据处理](#模板数据处理)
- [性能优化策略](#性能优化策略)
- [安全防护措施](#安全防护措施)
- [实战案例](#实战案例)

## 🚀 模板引擎基础

### Gin模板引擎概述

Gin框架使用Go标准库的`html/template`包作为模板引擎，提供了强大的模板渲染功能。模板引擎允许开发者将数据与HTML模板分离，实现动态内容的生成。

### 基本配置

```go
package main

import (
    "github.com/gin-gonic/gin"
    "net/http"
)

func main() {
    r := gin.Default()

    // 配置模板引擎
    r.LoadHTMLGlob("templates/*")
    // 或者使用 r.LoadHTMLFiles("templates/index.html", "templates/about.html")

    // 设置模板函数
    r.SetFuncMap(template.FuncMap{
        "formatDate": formatDate,
        "toUpper":    strings.ToUpper,
        "toLower":    strings.ToLower,
    })

    r.Run(":8080")
}

// 自定义模板函数
func formatDate(t time.Time) string {
    return t.Format("2006-01-02")
}
```

### 模板目录结构

```
templates/
├── layouts/
│   ├── base.html
│   └── admin.html
├── pages/
│   ├── index.html
│   ├── about.html
│   └── contact.html
├── partials/
│   ├── header.html
│   ├── footer.html
│   └── sidebar.html
└── components/
    ├── user-card.html
    ├── product-card.html
    └── modal.html
```

## 🎨 HTML模板渲染

### 基本模板渲染

```go
func setupTemplateRoutes(r *gin.Engine) {
    // 渲染简单模板
    r.GET("/", func(c *gin.Context) {
        c.HTML(http.StatusOK, "index.html", gin.H{
            "title":   "首页",
            "message": "欢迎来到Gin模板引擎",
            "time":    time.Now(),
        })
    })

    // 渲染带数据的模板
    r.GET("/users/:id", func(c *gin.Context) {
        userID := c.Param("id")
        user := getUserByID(userID)

        c.HTML(http.StatusOK, "user-detail.html", gin.H{
            "title": "用户详情",
            "user":  user,
            "stats": getUserStats(userID),
        })
    })
}

// 用户数据结构
type User struct {
    ID       int    `json:"id"`
    Name     string `json:"name"`
    Email    string `json:"email"`
    Avatar   string `json:"avatar"`
    Bio      string `json:"bio"`
    JoinDate time.Time `json:"join_date"`
}

// 用户统计结构
type UserStats struct {
    Posts    int `json:"posts"`
    Followers int `json:"followers"`
    Following int `json:"following"`
}
```

### 模板语法基础

```html
<!-- templates/index.html -->
{{ define "index.html" }}
<!DOCTYPE html>
<html>
<head>
    <title>{{ .title }}</title>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body>
    <h1>{{ .message }}</h1>
    <p>当前时间: {{ .time | formatDate }}</p>

    <!-- 条件语句 -->
    {{ if .user }}
        <div class="user-info">
            <h2>欢迎, {{ .user.Name }}</h2>
            <p>{{ .user.Email }}</p>
        </div>
    {{ else }}
        <div class="guest-info">
            <p>请<a href="/login">登录</a></p>
        </div>
    {{ end }}

    <!-- 循环语句 -->
    {{ if .posts }}
        <div class="posts">
            {{ range .posts }}
                <div class="post">
                    <h3>{{ .Title }}</h3>
                    <p>{{ .Content }}</p>
                    <small>发布时间: {{ .CreatedAt | formatDate }}</small>
                </div>
            {{ end }}
        </div>
    {{ end }}
</body>
</html>
{{ end }}
```

## 📋 模板继承与布局

### 基础布局模板

```html
<!-- templates/layouts/base.html -->
{{ define "base.html" }}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ .title }} - 我的网站</title>
    <meta name="description" content="{{ .description }}">

    <!-- CSS -->
    {{ block "styles" . }}
        <link rel="stylesheet" href="/static/css/style.css">
        <link rel="stylesheet" href="/static/css/bootstrap.min.css">
    {{ end }}

    <!-- 自定义头部 -->
    {{ block "head" . }}{{ end }}
</head>
<body>
    <!-- 导航栏 -->
    {{ template "partials/header.html" . }}

    <!-- 主要内容 -->
    <div class="container">
        {{ block "content" . }}{{ end }}
    </div>

    <!-- 侧边栏 -->
    {{ block "sidebar" . }}
        {{ template "partials/sidebar.html" . }}
    {{ end }}

    <!-- 页脚 -->
    {{ template "partials/footer.html" . }}

    <!-- JavaScript -->
    {{ block "scripts" . }}
        <script src="/static/js/main.js"></script>
    {{ end }}

    <!-- 自定义脚本 -->
    {{ block "custom_scripts" . }}{{ end }}
</body>
</html>
{{ end }}
```

### 页面模板继承

```html
<!-- templates/pages/index.html -->
{{ define "index.html" }}
{{ template "base.html" . }}

{{ define "title" }}首页{{ end }}

{{ define "head" . }}
    <meta name="keywords" content="Gin, 模板引擎, Go">
    <link rel="canonical" href="https://example.com/">
{{ end }}

{{ define "content" . }}
    <div class="jumbotron">
        <h1 class="display-4">{{ .welcome_message }}</h1>
        <p class="lead">{{ .description }}</p>
        <a class="btn btn-primary btn-lg" href="/about" role="button">了解更多</a>
    </div>

    <!-- 特色功能 -->
    <div class="row">
        {{ range .features }}
        <div class="col-md-4">
            <div class="card">
                <div class="card-body">
                    <h5 class="card-title">{{ .title }}</h5>
                    <p class="card-text">{{ .description }}</p>
                    <a href="{{ .link }}" class="btn btn-outline-primary">详情</a>
                </div>
            </div>
        </div>
        {{ end }}
    </div>

    <!-- 最新文章 -->
    <div class="latest-posts">
        <h2>最新文章</h2>
        <div class="row">
            {{ range .latest_posts }}
            <div class="col-md-6">
                <div class="post-card">
                    <h3>{{ .title }}</h3>
                    <p>{{ .summary }}</p>
                    <small class="text-muted">
                        作者: {{ .author }} |
                        发布时间: {{ .created_at | formatDate }}
                    </small>
                </div>
            </div>
            {{ end }}
        </div>
    </div>
{{ end }}

{{ define "custom_scripts" . }}
    <script>
        // 首页特定的JavaScript
        $(document).ready(function() {
            console.log('首页已加载');
        });
    </script>
{{ end }}
{{ end }}
```

### 管理员布局模板

```html
<!-- templates/layouts/admin.html -->
{{ define "admin.html" }}
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ .title }} - 管理后台</title>

    <!-- Admin CSS -->
    <link rel="stylesheet" href="/static/css/admin.css">
    <link rel="stylesheet" href="/static/css/fontawesome.min.css">

    {{ block "admin_styles" . }}{{ end }}
</head>
<body class="admin-body">
    <div class="admin-wrapper">
        <!-- 侧边栏 -->
        {{ template "admin/partials/sidebar.html" . }}

        <!-- 主要内容区域 -->
        <div class="main-content">
            <!-- 顶部导航 -->
            {{ template "admin/partials/topbar.html" . }}

            <!-- 页面内容 -->
            <div class="page-content">
                {{ block "admin_content" . }}{{ end }}
            </div>
        </div>
    </div>

    <!-- Admin JavaScript -->
    <script src="/static/js/admin.js"></script>
    {{ block "admin_scripts" . }}{{ end }}
</body>
</html>
{{ end }}
```

## 🔧 自定义模板函数

### 常用模板函数

```go
// 模板函数注册
func setupTemplateFunctions(r *gin.Engine) {
    r.SetFuncMap(template.FuncMap{
        // 字符串处理
        "upper": strings.ToUpper,
        "lower": strings.ToLower,
        "title": strings.Title,
        "trim": strings.TrimSpace,
        "replace": strings.Replace,
        "split": strings.Split,
        "join": strings.Join,

        // 数字处理
        "add": func(a, b int) int { return a + b },
        "sub": func(a, b int) int { return a - b },
        "mul": func(a, b int) int { return a * b },
        "div": func(a, b int) int { return a / b },
        "mod": func(a, b int) int { return a % b },
        "formatNumber": formatNumber,
        "formatCurrency": formatCurrency,

        // 时间处理
        "formatDate": formatDate,
        "formatDateTime": formatDateTime,
        "formatRelative": formatRelativeTime,
        "now": time.Now,
        "dateAdd": dateAdd,

        // HTML处理
        "safeHTML": safeHTML,
        "markdownToHTML": markdownToHTML,
        "truncate": truncate,
        "highlight": highlight,

        // 集合处理
        "first": first,
        "last": last,
        "slice": slice,
        "sortBy": sortBy,
        "groupBy": groupBy,
        "where": where,

        // 安全相关
        "csrfToken": getCSRFToken,
        "nonce": generateNonce,

        // 实用工具
        "default": defaultValue,
        "coalesce": coalesce,
        "ternary": ternary,
        "json": toJSON,
        "base64": base64Encode,
        "hash": hashString,
    })
}

// 格式化数字
func formatNumber(num int) string {
    return fmt.Sprintf("%,d", num)
}

// 格式化货币
func formatCurrency(amount float64, currency string) string {
    switch currency {
    case "CNY":
        return fmt.Sprintf("¥%.2f", amount)
    case "USD":
        return fmt.Sprintf("$%.2f", amount)
    case "EUR":
        return fmt.Sprintf("€%.2f", amount)
    default:
        return fmt.Sprintf("%.2f %s", amount, currency)
    }
}

// 格式化日期
func formatDate(t time.Time) string {
    return t.Format("2006-01-02")
}

// 格式化日期时间
func formatDateTime(t time.Time) string {
    return t.Format("2006-01-02 15:04:05")
}

// 格式化相对时间
func formatRelativeTime(t time.Time) string {
    now := time.Now()
    diff := now.Sub(t)

    switch {
    case diff < time.Minute:
        return "刚刚"
    case diff < time.Hour:
        return fmt.Sprintf("%d分钟前", int(diff.Minutes()))
    case diff < 24*time.Hour:
        return fmt.Sprintf("%d小时前", int(diff.Hours()))
    case diff < 30*24*time.Hour:
        return fmt.Sprintf("%d天前", int(diff.Hours()/24))
    default:
        return t.Format("2006-01-02")
    }
}

// 安全HTML
func safeHTML(html string) template.HTML {
    return template.HTML(html)
}

// Markdown转HTML
func markdownToHTML(markdown string) template.HTML {
    // 使用markdown库转换
    // 这里简化处理
    return template.HTML("<p>" + markdown + "</p>")
}

// 截断文本
func truncate(text string, length int, suffix string) string {
    if len(text) <= length {
        return text
    }
    return text[:length] + suffix
}

// 高亮关键词
func highlight(text, keyword string) template.HTML {
    if keyword == "" {
        return template.HTML(text)
    }

    highlighted := strings.ReplaceAll(text, keyword,
        fmt.Sprintf("<mark>%s</mark>", keyword))
    return template.HTML(highlighted)
}

// 获取第一个元素
func first(slice interface{}) interface{} {
    if slice == nil {
        return nil
    }

    s := reflect.ValueOf(slice)
    if s.Kind() != reflect.Slice || s.Len() == 0 {
        return nil
    }

    return s.Index(0).Interface()
}

// 获取最后一个元素
func last(slice interface{}) interface{} {
    if slice == nil {
        return nil
    }

    s := reflect.ValueOf(slice)
    if s.Kind() != reflect.Slice || s.Len() == 0 {
        return nil
    }

    return s.Index(s.Len() - 1).Interface()
}

// 切片操作
func slice(slice interface{}, start, end int) interface{} {
    if slice == nil {
        return nil
    }

    s := reflect.ValueOf(slice)
    if s.Kind() != reflect.Slice {
        return nil
    }

    length := s.Len()
    if start < 0 {
        start = 0
    }
    if end > length {
        end = length
    }
    if start >= end {
        return make([]interface{}, 0)
    }

    result := make([]interface{}, end-start)
    for i := start; i < end; i++ {
        result[i-start] = s.Index(i).Interface()
    }

    return result
}

// 排序
func sortBy(slice interface{}, field string) interface{} {
    // 实现排序逻辑
    return slice
}

// 分组
func groupBy(slice interface{}, field string) map[string]interface{} {
    // 实现分组逻辑
    return make(map[string]interface{})
}

// 过滤
func where(slice interface{}, field string, value interface{}) interface{} {
    // 实现过滤逻辑
    return slice
}

// 默认值
func defaultValue(value, defaultValue interface{}) interface{} {
    if value == nil || value == "" {
        return defaultValue
    }
    return value
}

// 合并值
func coalesce(values ...interface{}) interface{} {
    for _, value := range values {
        if value != nil && value != "" {
            return value
        }
    }
    return nil
}

// 三元操作
func ternary(condition bool, trueValue, falseValue interface{}) interface{} {
    if condition {
        return trueValue
    }
    return falseValue
}

// 转换为JSON
func toJSON(data interface{}) string {
    bytes, err := json.Marshal(data)
    if err != nil {
        return ""
    }
    return string(bytes)
}

// Base64编码
func base64Encode(data string) string {
    return base64.StdEncoding.EncodeToString([]byte(data))
}

// 哈希字符串
func hashString(data string) string {
    hash := sha256.Sum256([]byte(data))
    return hex.EncodeToString(hash[:])
}
```

### 复杂模板函数

```go
// 分页函数
type Pagination struct {
    Page       int `json:"page"`
    PageSize   int `json:"page_size"`
    TotalItems int `json:"total_items"`
    TotalPages int `json:"total_pages"`
}

func (p *Pagination) Offset() int {
    return (p.Page - 1) * p.PageSize
}

func (p *Pagination) HasPrev() bool {
    return p.Page > 1
}

func (p *Pagination) HasNext() bool {
    return p.Page < p.TotalPages
}

func (p *Pagination) PrevPage() int {
    if p.HasPrev() {
        return p.Page - 1
    }
    return 1
}

func (p *Pagination) NextPage() int {
    if p.HasNext() {
        return p.Page + 1
    }
    return p.TotalPages
}

// 分页模板函数
func setupPaginationFunctions(r *gin.Engine) {
    r.SetFuncMap(template.FuncMap{
        "pagination": paginationHTML,
        "pageURL": pageURL,
        "pageNumbers": pageNumbers,
    })
}

func paginationHTML(p *Pagination, url string) template.HTML {
    if p.TotalPages <= 1 {
        return template.HTML("")
    }

    var html strings.Builder
    html.WriteString("<nav aria-label=\"Page navigation\"><ul class=\"pagination\">")

    // 上一页
    if p.HasPrev() {
        html.WriteString(fmt.Sprintf("<li class=\"page-item\"><a class=\"page-link\" href=\"%s?page=%d\">上一页</a></li>",
            url, p.PrevPage()))
    } else {
        html.WriteString("<li class=\"page-item disabled\"><span class=\"page-link\">上一页</span></li>")
    }

    // 页码
    for _, page := range pageNumbers(p) {
        if page == p.Page {
            html.WriteString(fmt.Sprintf("<li class=\"page-item active\"><span class=\"page-link\">%d</span></li>", page))
        } else {
            html.WriteString(fmt.Sprintf("<li class=\"page-item\"><a class=\"page-link\" href=\"%s?page=%d\">%d</a></li>",
                url, page, page))
        }
    }

    // 下一页
    if p.HasNext() {
        html.WriteString(fmt.Sprintf("<li class=\"page-item\"><a class=\"page-link\" href=\"%s?page=%d\">下一页</a></li>",
            url, p.NextPage()))
    } else {
        html.WriteString("<li class=\"page-item disabled\"><span class=\"page-link\">下一页</span></li>")
    }

    html.WriteString("</ul></nav>")
    return template.HTML(html.String())
}

func pageURL(baseURL string, page int) string {
    return fmt.Sprintf("%s?page=%d", baseURL, page)
}

func pageNumbers(p *Pagination) []int {
    if p.TotalPages <= 10 {
        // 显示所有页码
        pages := make([]int, p.TotalPages)
        for i := 1; i <= p.TotalPages; i++ {
            pages[i-1] = i
        }
        return pages
    }

    // 显示部分页码
    var pages []int

    // 总是显示第一页
    pages = append(pages, 1)

    // 计算显示范围
    start := p.Page - 2
    end := p.Page + 2

    if start < 2 {
        start = 2
    }
    if end > p.TotalPages-1 {
        end = p.TotalPages - 1
    }

    // 添加省略号和页码
    if start > 2 {
        pages = append(pages, 0) // 0表示省略号
    }

    for i := start; i <= end; i++ {
        pages = append(pages, i)
    }

    if end < p.TotalPages-1 {
        pages = append(pages, 0) // 0表示省略号
    }

    // 总是显示最后一页
    if p.TotalPages > 1 {
        pages = append(pages, p.TotalPages)
    }

    return pages
}
```

## 📊 模板数据处理

### 数据结构定义

```go
// 页面数据结构
type PageData struct {
    Title       string                 `json:"title"`
    Description string                 `json:"description"`
    Keywords    string                 `json:"keywords"`
    Data        map[string]interface{} `json:"data"`
    User        *User                  `json:"user,omitempty"`
    Settings    *SiteSettings          `json:"settings,omitempty"`
    Meta        map[string]string      `json:"meta,omitempty"`
}

// 网站设置
type SiteSettings struct {
    SiteName    string `json:"site_name"`
    SiteURL     string `json:"site_url"`
    AdminEmail  string `json:"admin_email"`
    SEO         *SEOSettings  `json:"seo"`
    Theme       *ThemeSettings `json:"theme"`
}

// SEO设置
type SEOSettings struct {
    MetaTitle       string `json:"meta_title"`
    MetaDescription string `json:"meta_description"`
    MetaKeywords    string `json:"meta_keywords"`
    OpenGraph      *OpenGraphSettings `json:"open_graph"`
    Twitter        *TwitterSettings `json:"twitter"`
}

// 主题设置
type ThemeSettings struct {
    PrimaryColor   string `json:"primary_color"`
    SecondaryColor string `json:"secondary_color"`
    Logo           string `json:"logo"`
    Favicon        string `json:"favicon"`
    Theme          string `json:"theme"`
}

// OpenGraph设置
type OpenGraphSettings struct {
    Title       string `json:"title"`
    Description string `json:"description"`
    Type        string `json:"type"`
    URL         string `json:"url"`
    Image       string `json:"image"`
}

// Twitter设置
type TwitterSettings struct {
    Card        string `json:"card"`
    Site        string `json:"site"`
    Creator     string `json:"creator"`
}

// 博客文章
type BlogPost struct {
    ID          int       `json:"id"`
    Title       string    `json:"title"`
    Slug        string    `json:"slug"`
    Content     string    `json:"content"`
    Summary     string    `json:"summary"`
    Author      *User     `json:"author"`
    Category    *Category `json:"category"`
    Tags        []string  `json:"tags"`
    Status      string    `json:"status"`
    Featured    bool      `json:"featured"`
    Views       int       `json:"views"`
    Likes       int       `json:"likes"`
    CreatedAt   time.Time `json:"created_at"`
    UpdatedAt   time.Time `json:"updated_at"`
    PublishedAt time.Time `json:"published_at"`
}

// 分类
type Category struct {
    ID          int       `json:"id"`
    Name        string    `json:"name"`
    Slug        string    `json:"slug"`
    Description string    `json:"description"`
    ParentID    int       `json:"parent_id"`
    SortOrder   int       `json:"sort_order"`
    CreatedAt   time.Time `json:"created_at"`
}

// 评论
type Comment struct {
    ID        int       `json:"id"`
    Content   string    `json:"content"`
    Author    *User     `json:"author"`
    PostID    int       `json:"post_id"`
    ParentID  int       `json:"parent_id"`
    Status    string    `json:"status"`
    CreatedAt time.Time `json:"created_at"`
}
```

### 数据处理函数

```go
// 页面数据构建器
type PageDataBuilder struct {
    data *PageData
}

func NewPageDataBuilder() *PageDataBuilder {
    return &PageDataBuilder{
        data: &PageData{
            Data:   make(map[string]interface{}),
            Meta:   make(map[string]string),
        },
    }
}

func (b *PageDataBuilder) SetTitle(title string) *PageDataBuilder {
    b.data.Title = title
    return b
}

func (b *PageDataBuilder) SetDescription(description string) *PageDataBuilder {
    b.data.Description = description
    return b
}

func (b *PageDataBuilder) SetKeywords(keywords string) *PageDataBuilder {
    b.data.Keywords = keywords
    return b
}

func (b *PageDataBuilder) SetUser(user *User) *PageDataBuilder {
    b.data.User = user
    return b
}

func (b *PageDataBuilder) SetSettings(settings *SiteSettings) *PageDataBuilder {
    b.data.Settings = settings
    return b
}

func (b *PageDataBuilder) AddData(key string, value interface{}) *PageDataBuilder {
    b.data.Data[key] = value
    return b
}

func (b *PageDataBuilder) AddMeta(key, value string) *PageDataBuilder {
    b.data.Meta[key] = value
    return b
}

func (b *PageDataBuilder) Build() *PageData {
    return b.data
}

// 博客页面数据准备
func prepareBlogPageData(posts []*BlogPost, pagination *Pagination) *PageData {
    builder := NewPageDataBuilder().
        SetTitle("博客").
        SetDescription("最新博客文章").
        SetKeywords("博客,文章,技术").
        AddData("posts", posts).
        AddData("pagination", pagination).
        AddData("categories", getAllCategories()).
        AddData("popular_tags", getPopularTags()).
        AddData("recent_posts", getRecentPosts(5)).
        AddData("featured_posts", getFeaturedPosts(3))

    return builder.Build()
}

// 文章详情页面数据准备
func preparePostDetailData(post *BlogPost, comments []*Comment) *PageData {
    // SEO数据
    seo := &SEOSettings{
        MetaTitle:       post.Title,
        MetaDescription: post.Summary,
        MetaKeywords:    strings.Join(post.Tags, ","),
        OpenGraph: &OpenGraphSettings{
            Title:       post.Title,
            Description: post.Summary,
            Type:        "article",
            URL:         fmt.Sprintf("/blog/%s", post.Slug),
            Image:       post.Author.Avatar,
        },
    }

    builder := NewPageDataBuilder().
        SetTitle(post.Title).
        SetDescription(post.Summary).
        SetKeywords(strings.Join(post.Tags, ",")).
        AddData("post", post).
        AddData("comments", comments).
        AddData("related_posts", getRelatedPosts(post.ID, 3)).
        AddData("author_posts", getAuthorPosts(post.Author.ID, 5)).
        AddMeta("article:published_time", post.PublishedAt.Format(time.RFC3339)).
        AddMeta("article:modified_time", post.UpdatedAt.Format(time.RFC3339)).
        AddMeta("article:author", post.Author.Name)

    return builder.Build()
}

// 分类页面数据准备
func prepareCategoryPageData(category *Category, posts []*BlogPost, pagination *Pagination) *PageData {
    builder := NewPageDataBuilder().
        SetTitle(fmt.Sprintf("%s - 博客分类", category.Name)).
        SetDescription(category.Description).
        SetKeywords(fmt.Sprintf("%s,博客,分类", category.Name)).
        AddData("category", category).
        AddData("posts", posts).
        AddData("pagination", pagination).
        AddData("subcategories", getSubcategories(category.ID))

    return builder.Build()
}
```

## ⚡ 性能优化策略

### 模板缓存优化

```go
// 模板缓存管理器
type TemplateCache struct {
    templates map[string]*template.Template
    mutex     sync.RWMutex
    ttl       time.Duration
    lastUpdate time.Time
}

func NewTemplateCache(ttl time.Duration) *TemplateCache {
    return &TemplateCache{
        templates: make(map[string]*template.Template),
        ttl:       ttl,
        lastUpdate: time.Now(),
    }
}

func (tc *TemplateCache) Get(name string) (*template.Template, bool) {
    tc.mutex.RLock()
    defer tc.mutex.RUnlock()

    // 检查缓存是否过期
    if time.Since(tc.lastUpdate) > tc.ttl {
        return nil, false
    }

    tmpl, exists := tc.templates[name]
    return tmpl, exists
}

func (tc *TemplateCache) Set(name string, tmpl *template.Template) {
    tc.mutex.Lock()
    defer tc.mutex.Unlock()

    tc.templates[name] = tmpl
    tc.lastUpdate = time.Now()
}

func (tc *TemplateCache) Clear() {
    tc.mutex.Lock()
    defer tc.mutex.Unlock()

    tc.templates = make(map[string]*template.Template)
    tc.lastUpdate = time.Now()
}

// 模板预编译器
type TemplatePrecompiler struct {
    cache  *TemplateCache
    paths  map[string]string
    funcs  template.FuncMap
}

func NewTemplatePrecompiler(cache *TemplateCache, paths map[string]string, funcs template.FuncMap) *TemplatePrecompiler {
    return &TemplatePrecompiler{
        cache: cache,
        paths: paths,
        funcs: funcs,
    }
}

func (tp *TemplatePrecompiler) Precompile() error {
    for name, path := range tp.paths {
        tmpl, err := tp.compileTemplate(path)
        if err != nil {
            return fmt.Errorf("failed to compile template %s: %v", name, err)
        }

        tp.cache.Set(name, tmpl)
    }
    return nil
}

func (tp *TemplatePrecompiler) compileTemplate(path string) (*template.Template, error) {
    content, err := os.ReadFile(path)
    if err != nil {
        return nil, err
    }

    tmpl := template.New("").Funcs(tp.funcs)
    _, err = tmpl.Parse(string(content))
    if err != nil {
        return nil, err
    }

    return tmpl, nil
}

// 模板片段缓存
type TemplateFragmentCache struct {
    fragments map[string]FragmentCacheEntry
    mutex     sync.RWMutex
    ttl       time.Duration
}

type FragmentCacheEntry struct {
    Content  string
    Expires  time.Time
    Metadata map[string]interface{}
}

func NewTemplateFragmentCache(ttl time.Duration) *TemplateFragmentCache {
    return &TemplateFragmentCache{
        fragments: make(map[string]FragmentCacheEntry),
        ttl:       ttl,
    }
}

func (fc *TemplateFragmentCache) Get(key string) (string, bool) {
    fc.mutex.RLock()
    defer fc.mutex.RUnlock()

    entry, exists := fc.fragments[key]
    if !exists || time.Now().After(entry.Expires) {
        return "", false
    }

    return entry.Content, true
}

func (fc *TemplateFragmentCache) Set(key string, content string, metadata map[string]interface{}) {
    fc.mutex.Lock()
    defer fc.mutex.Unlock()

    fc.fragments[key] = FragmentCacheEntry{
        Content:  content,
        Expires:  time.Now().Add(fc.ttl),
        Metadata: metadata,
    }
}

func (fc *TemplateFragmentCache) Delete(key string) {
    fc.mutex.Lock()
    defer fc.mutex.Unlock()

    delete(fc.fragments, key)
}

func (fc *TemplateFragmentCache) ClearExpired() {
    fc.mutex.Lock()
    defer fc.mutex.Unlock()

    now := time.Now()
    for key, entry := range fc.fragments {
        if now.After(entry.Expires) {
            delete(fc.fragments, key)
        }
    }
}
```

### 渲染性能优化

```go
// 渲染优化器
type RenderOptimizer struct {
    cache        *TemplateFragmentCache
    minify       bool
    compression  bool
    etags        bool
}

func NewRenderOptimizer(cache *TemplateFragmentCache) *RenderOptimizer {
    return &RenderOptimizer{
        cache:       cache,
        minify:      true,
        compression: true,
        etags:       true,
    }
}

func (ro *RenderOptimizer) OptimizeHTML(html string) string {
    if ro.minify {
        html = ro.minifyHTML(html)
    }

    if ro.compression {
        html = ro.compressHTML(html)
    }

    return html
}

func (ro *RenderOptimizer) minifyHTML(html string) string {
    // 简单的HTML压缩
    html = regexp.MustCompile(`\s+`).ReplaceAllString(html, " ")
    html = strings.ReplaceAll(html, "> <", "><")
    html = strings.TrimSpace(html)
    return html
}

func (ro *RenderOptimizer) compressHTML(html string) string {
    // 实现HTML压缩
    return html
}

func (ro *RenderOptimizer) GenerateETag(content string) string {
    hash := sha256.Sum256([]byte(content))
    return fmt.Sprintf("\"%x\"", hash[:8])
}

// 模板渲染中间件
func TemplateRenderMiddleware(optimizer *RenderOptimizer) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 修改gin的HTML渲染方法
        c.HTML = func(code int, name string, obj interface{}) {
            // 检查缓存
            cacheKey := fmt.Sprintf("%s:%v", name, obj)
            if cached, exists := optimizer.cache.Get(cacheKey); exists {
                c.Data(code, "text/html; charset=utf-8", []byte(cached))
                return
            }

            // 渲染模板
            html := renderTemplate(name, obj)

            // 优化HTML
            html = optimizer.OptimizeHTML(html)

            // 缓存结果
            optimizer.cache.Set(cacheKey, html, map[string]interface{}{
                "size": len(html),
                "timestamp": time.Now(),
            })

            // 设置ETag
            if optimizer.etags {
                c.Header("ETag", optimizer.GenerateETag(html))
            }

            c.Data(code, "text/html; charset=utf-8", []byte(html))
        }

        c.Next()
    }
}

// 部分渲染优化
func PartialRenderMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 支持部分渲染
        c.Set("partial_render", func(name string, data interface{}) template.HTML {
            // 渲染部分模板
            html := renderPartialTemplate(name, data)
            return template.HTML(html)
        })

        c.Next()
    }
}

// 模板渲染器
func renderTemplate(name string, data interface{}) string {
    // 实现模板渲染逻辑
    return fmt.Sprintf("<div>Rendered template: %s</div>", name)
}

func renderPartialTemplate(name string, data interface{}) string {
    // 实现部分模板渲染逻辑
    return fmt.Sprintf("<div>Partial template: %s</div>", name)
}
```

## 🛡️ 安全防护措施

### XSS防护

```go
// 安全模板函数
func setupSecurityFunctions(r *gin.Engine) {
    r.SetFuncMap(template.FuncMap{
        "safeHTML":    safeHTML,
        "safeURL":     safeURL,
        "safeCSS":     safeCSS,
        "safeJS":      safeJS,
        "sanitizeHTML": sanitizeHTML,
        "escapeHTML":  template.HTMLEscapeString,
        "escapeJS":    template.JSEscapeString,
        "escapeURL":   template.HTMLEscapeString,
        "cspNonce":    generateCSPNonce,
    })
}

// 安全HTML输出
func safeHTML(html string) template.HTML {
    // 使用HTML清理库
    sanitized := bluemonday.UGCPolicy().Sanitize(html)
    return template.HTML(sanitized)
}

// 安全URL输出
func safeURL(url string) template.URL {
    // 验证并清理URL
    if isValidURL(url) {
        return template.URL(url)
    }
    return template.URL("#")
}

// 安全CSS输出
func safeCSS(css string) template.CSS {
    // 验证CSS
    if isValidCSS(css) {
        return template.CSS(css)
    }
    return template.CSS("")
}

// 安全JavaScript输出
func safeJS(js string) template.JS {
    // 验证JavaScript
    if isValidJS(js) {
        return template.JS(js)
    }
    return template.JS("")
}

// HTML清理
func sanitizeHTML(html string) template.HTML {
    // 使用更严格的HTML清理策略
    p := bluemonday.UGCPolicy()
    p.AllowStandardURLs()
    p.AllowRelativeURLs()
    p.AllowStandardAttributes()
    p.AllowDataAttributes()

    sanitized := p.Sanitize(html)
    return template.HTML(sanitized)
}

// URL验证
func isValidURL(url string) bool {
    if url == "" {
        return false
    }

    // 检查协议
    if strings.HasPrefix(url, "http://") || strings.HasPrefix(url, "https://") {
        return true
    }

    // 检查相对URL
    if strings.HasPrefix(url, "/") {
        return true
    }

    return false
}

// CSS验证
func isValidCSS(css string) bool {
    // 简单的CSS验证
    return !strings.Contains(css, "javascript:") &&
           !strings.Contains(css, "expression(") &&
           !strings.Contains(css, "import ")
}

// JavaScript验证
func isValidJS(js string) bool {
    // 简单的JavaScript验证
    return !strings.Contains(js, "eval(") &&
           !strings.Contains(js, "Function(") &&
           !strings.Contains(js, "setTimeout(") &&
           !strings.Contains(js, "setInterval(")
}

// CSP Nonce生成
func generateCSPNonce() string {
    bytes := make([]byte, 16)
    rand.Read(bytes)
    return base64.StdEncoding.EncodeToString(bytes)
}

// CSP中间件
func CSPMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        nonce := generateCSPNonce()

        // 设置CSP头
        c.Header("Content-Security-Policy", fmt.Sprintf(
            "default-src 'self'; script-src 'self' 'nonce-%s'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self'; connect-src 'self'",
            nonce,
        ))

        // 将nonce存储在上下文中
        c.Set("csp_nonce", nonce)

        c.Next()
    }
}
```

### CSRF防护

```go
// CSRF管理器
type CSRFManager struct {
    secret   []byte
    tokenLen int
    ttl      time.Duration
}

func NewCSRFManager(secret []byte, tokenLen int, ttl time.Duration) *CSRFManager {
    return &CSRFManager{
        secret:   secret,
        tokenLen: tokenLen,
        ttl:      ttl,
    }
}

func (cm *CSRFManager) GenerateToken() string {
    bytes := make([]byte, cm.tokenLen)
    rand.Read(bytes)

    // 添加时间戳
    timestamp := time.Now().Unix()
    payload := fmt.Sprintf("%s:%d", base64.StdEncoding.EncodeToString(bytes), timestamp)

    // 签名
    signature := cm.sign(payload)

    return fmt.Sprintf("%s:%s", payload, signature)
}

func (cm *CSRFManager) ValidateToken(token string) bool {
    parts := strings.Split(token, ":")
    if len(parts) != 3 {
        return false
    }

    // 验证签名
    payload := fmt.Sprintf("%s:%s", parts[0], parts[1])
    signature := cm.sign(payload)

    if !hmac.Equal([]byte(parts[2]), []byte(signature)) {
        return false
    }

    // 验证时间戳
    timestamp, err := strconv.ParseInt(parts[1], 10, 64)
    if err != nil {
        return false
    }

    if time.Now().Unix()-timestamp > int64(cm.ttl.Seconds()) {
        return false
    }

    return true
}

func (cm *CSRFManager) sign(data string) string {
    h := hmac.New(sha256.New, cm.secret)
    h.Write([]byte(data))
    return base64.StdEncoding.EncodeToString(h.Sum(nil))
}

// CSRF中间件
func CSRFMiddleware(manager *CSRFManager) gin.HandlerFunc {
    return func(c *gin.Context) {
        // 跳过安全方法
        if c.Request.Method == "GET" || c.Request.Method == "HEAD" || c.Request.Method == "OPTIONS" {
            c.Next()
            return
        }

        // 获取CSRF token
        token := c.GetHeader("X-CSRF-Token")
        if token == "" {
            token = c.PostForm("csrf_token")
        }

        if token == "" || !manager.ValidateToken(token) {
            c.AbortWithStatusJSON(403, gin.H{"error": "Invalid CSRF token"})
            return
        }

        c.Next()
    }
}

// CSRF Token模板函数
func getCSRFToken(c *gin.Context) string {
    if manager, exists := c.Get("csrf_manager"); exists {
        return manager.(*CSRFManager).GenerateToken()
    }
    return ""
}
```

## 🎯 实战案例

### 完整博客系统模板

```go
// 博客系统模板设置
func setupBlogTemplates(r *gin.Engine) {
    // 配置模板
    r.LoadHTMLGlob("templates/blog/**/*")

    // 设置模板函数
    r.SetFuncMap(template.FuncMap{
        // 基础函数
        "upper": strings.ToUpper,
        "lower": strings.ToLower,
        "formatDate": formatDate,
        "formatDateTime": formatDateTime,
        "formatRelative": formatRelativeTime,

        // 安全函数
        "safeHTML": safeHTML,
        "escapeHTML": template.HTMLEscapeString,
        "cspNonce": generateCSPNonce,

        // 博客特定函数
        "readingTime": calculateReadingTime,
        "wordCount": countWords,
        "excerpt": generateExcerpt,
        "tagURL": generateTagURL,
        "categoryURL": generateCategoryURL,
        "shareURL": generateShareURL,

        // 分页函数
        "pagination": paginationHTML,
        "pageNumbers": pageNumbers,

        // SEO函数
        "metaTitle": generateMetaTitle,
        "metaDescription": generateMetaDescription,
        "structuredData": generateStructuredData,
    })

    // 设置安全中间件
    r.Use(CSPMiddleware())

    // 设置CSRF管理器
    csrfManager := NewCSRFManager([]byte("secret-key"), 32, time.Hour)
    r.Use(CSRFMiddleware(csrfManager))
    r.Set("csrf_manager", csrfManager)

    // 设置渲染优化器
    fragmentCache := NewTemplateFragmentCache(5 * time.Minute)
    optimizer := NewRenderOptimizer(fragmentCache)
    r.Use(TemplateRenderMiddleware(optimizer))

    // 设置路由
    setupBlogRoutes(r)
}

// 博客路由设置
func setupBlogRoutes(r *gin.Engine) {
    blog := r.Group("/blog")
    {
        // 博客首页
        blog.GET("", func(c *gin.Context) {
            page := c.DefaultQuery("page", "1")
            pageSize := 12

            posts, pagination := getBlogPosts(page, pageSize)
            pageData := prepareBlogPageData(posts, pagination)

            c.HTML(200, "blog/index.html", pageData)
        })

        // 文章详情
        blog.GET("/:slug", func(c *gin.Context) {
            slug := c.Param("slug")
            post := getPostBySlug(slug)

            if post == nil {
                c.HTML(404, "errors/404.html", gin.H{"title": "文章未找到"})
                return
            }

            comments := getPostComments(post.ID)
            pageData := preparePostDetailData(post, comments)

            c.HTML(200, "blog/post.html", pageData)
        })

        // 分类页面
        blog.GET("/category/:slug", func(c *gin.Context) {
            slug := c.Param("slug")
            page := c.DefaultQuery("page", "1")

            category := getCategoryBySlug(slug)
            if category == nil {
                c.HTML(404, "errors/404.html", gin.H{"title": "分类未找到"})
                return
            }

            posts, pagination := getCategoryPosts(category.ID, page, 12)
            pageData := prepareCategoryPageData(category, posts, pagination)

            c.HTML(200, "blog/category.html", pageData)
        })

        // 标签页面
        blog.GET("/tag/:tag", func(c *gin.Context) {
            tag := c.Param("tag")
            page := c.DefaultQuery("page", "1")

            posts, pagination := getTagPosts(tag, page, 12)
            pageData := prepareTagPageData(tag, posts, pagination)

            c.HTML(200, "blog/tag.html", pageData)
        })

        // 搜索页面
        blog.GET("/search", func(c *gin.Context) {
            query := c.Query("q")
            page := c.DefaultQuery("page", "1")

            if query == "" {
                c.Redirect(302, "/blog")
                return
            }

            posts, pagination := searchPosts(query, page, 12)
            pageData := prepareSearchPageData(query, posts, pagination)

            c.HTML(200, "blog/search.html", pageData)
        })

        // RSS订阅
        blog.GET("/feed", func(c *gin.Context) {
            posts := getLatestPosts(20)
            feed := generateRSSFeed(posts)

            c.Header("Content-Type", "application/xml; charset=utf-8")
            c.String(200, feed)
        })

        // 站点地图
        blog.GET("/sitemap.xml", func(c *gin.Context) {
            sitemap := generateSitemap()
            c.Header("Content-Type", "application/xml; charset=utf-8")
            c.String(200, sitemap)
        })
    }
}

// 博客特定模板函数
func calculateReadingTime(content string) int {
    words := strings.Fields(content)
    wordCount := len(words)

    // 假设平均阅读速度为每分钟200字
    readingTime := int(math.Ceil(float64(wordCount) / 200))

    if readingTime < 1 {
        return 1
    }

    return readingTime
}

func countWords(content string) int {
    words := strings.Fields(content)
    return len(words)
}

func generateExcerpt(content string, length int) string {
    // 移除HTML标签
    cleanText := regexp.MustCompile(`<[^>]*>`).ReplaceAllString(content, "")

    // 截断文本
    if len(cleanText) <= length {
        return cleanText
    }

    return cleanText[:length] + "..."
}

func generateTagURL(tag string) string {
    return fmt.Sprintf("/blog/tag/%s", url.QueryEscape(tag))
}

func generateCategoryURL(category string) string {
    return fmt.Sprintf("/blog/category/%s", url.QueryEscape(category))
}

func generateShareURL(post *BlogPost) map[string]string {
    baseURL := "https://example.com"
    postURL := fmt.Sprintf("%s/blog/%s", baseURL, post.Slug)

    return map[string]string{
        "twitter": fmt.Sprintf("https://twitter.com/intent/tweet?url=%s&text=%s",
            url.QueryEscape(postURL), url.QueryEscape(post.Title)),
        "facebook": fmt.Sprintf("https://www.facebook.com/sharer/sharer.php?u=%s",
            url.QueryEscape(postURL)),
        "linkedin": fmt.Sprintf("https://www.linkedin.com/sharing/share-offsite/?url=%s",
            url.QueryEscape(postURL)),
        "weibo": fmt.Sprintf("https://service.weibo.com/share/share.php?url=%s&title=%s",
            url.QueryEscape(postURL), url.QueryEscape(post.Title)),
    }
}

func generateMetaTitle(post *BlogPost) string {
    if post.Title != "" {
        return fmt.Sprintf("%s - 我的博客", post.Title)
    }
    return "我的博客"
}

func generateMetaDescription(post *BlogPost) string {
    if post.Summary != "" {
        return post.Summary
    }
    return generateExcerpt(post.Content, 160)
}

func generateStructuredData(post *BlogPost) template.HTML {
    structuredData := map[string]interface{}{
        "@context": "https://schema.org",
        "@type": "BlogPosting",
        "headline": post.Title,
        "description": post.Summary,
        "author": map[string]interface{}{
            "@type": "Person",
            "name": post.Author.Name,
        },
        "datePublished": post.PublishedAt.Format(time.RFC3339),
        "dateModified": post.UpdatedAt.Format(time.RFC3339),
    }

    jsonData, _ := json.Marshal(structuredData)
    return template.HTML(fmt.Sprintf("<script type=\"application/ld+json\">%s</script>", jsonData))
}
```

### 博客模板文件示例

```html
<!-- templates/blog/index.html -->
{{ define "blog/index.html" }}
{{ template "layouts/base.html" . }}

{{ define "title" }}博客首页{{ end }}

{{ define "meta" }}
    <meta name="description" content="最新技术博客文章">
    <meta name="keywords" content="博客,技术,编程">
    {{ if .structuredData }}{{ .structuredData }}{{ end }}
{{ end }}

{{ define "content" }}
<div class="blog-container">
    <div class="row">
        <div class="col-lg-8">
            <!-- 文章列表 -->
            <div class="posts-list">
                {{ range .posts }}
                <article class="post-card">
                    <div class="post-meta">
                        <time datetime="{{ .PublishedAt.Format "2006-01-02" }}">
                            {{ .PublishedAt | formatDate }}
                        </time>
                        <span class="reading-time">{{ .Content | readingTime }}分钟阅读</span>
                    </div>

                    <h2 class="post-title">
                        <a href="/blog/{{ .Slug }}">{{ .Title }}</a>
                    </h2>

                    <div class="post-excerpt">
                        <p>{{ .Content | excerpt 200 }}</p>
                    </div>

                    <div class="post-footer">
                        <div class="author-info">
                            <img src="{{ .Author.Avatar }}" alt="{{ .Author.Name }}" class="author-avatar">
                            <span class="author-name">{{ .Author.Name }}</span>
                        </div>

                        <div class="post-stats">
                            <span class="views">{{ .Views }} 阅读</span>
                            <span class="likes">{{ .Likes }} 点赞</span>
                        </div>
                    </div>

                    {{ if .Tags }}
                    <div class="post-tags">
                        {{ range .Tags }}
                        <a href="{{ . | tagURL }}" class="tag">{{ . }}</a>
                        {{ end }}
                    </div>
                    {{ end }}
                </article>
                {{ end }}
            </div>

            <!-- 分页 -->
            {{ if .pagination }}
            {{ .pagination | pagination "/blog" }}
            {{ end }}
        </div>

        <div class="col-lg-4">
            <!-- 侧边栏 -->
            <div class="sidebar">
                <!-- 搜索框 -->
                <div class="widget search-widget">
                    <form method="GET" action="/blog/search">
                        <input type="text" name="q" placeholder="搜索文章..." class="form-control">
                        <button type="submit" class="btn btn-primary">搜索</button>
                    </form>
                </div>

                <!-- 分类 -->
                <div class="widget categories-widget">
                    <h3>分类</h3>
                    <ul class="categories-list">
                        {{ range .categories }}
                        <li>
                            <a href="{{ .Slug | categoryURL }}">{{ .Name }}</a>
                            <span class="count">({{ .PostCount }})</span>
                        </li>
                        {{ end }}
                    </ul>
                </div>

                <!-- 热门标签 -->
                <div class="widget tags-widget">
                    <h3>热门标签</h3>
                    <div class="tag-cloud">
                        {{ range .popular_tags }}
                        <a href="{{ .Name | tagURL }}" class="tag" style="font-size: {{ .Size }}px;">
                            {{ .Name }}
                        </a>
                        {{ end }}
                    </div>
                </div>

                <!-- 最新文章 -->
                <div class="widget recent-posts-widget">
                    <h3>最新文章</h3>
                    <ul class="recent-posts">
                        {{ range .recent_posts }}
                        <li>
                            <a href="/blog/{{ .Slug }}">{{ .Title }}</a>
                            <small>{{ .PublishedAt | formatDate }}</small>
                        </li>
                        {{ end }}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>
{{ end }}

{{ define "scripts" }}
    <script src="/static/js/blog.js"></script>
    <script nonce="{{ cspNonce }}">
        // 博客首页特定的JavaScript
        document.addEventListener('DOMContentLoaded', function() {
            // 初始化搜索功能
            initializeSearch();

            // 初始化标签云动画
            initializeTagCloud();
        });
    </script>
{{ end }}
{{ end }}

<!-- templates/blog/post.html -->
{{ define "blog/post.html" }}
{{ template "layouts/base.html" . }}

{{ define "title" }}{{ .post.Title }}{{ end }}

{{ define "meta" }}
    <meta name="description" content="{{ .post.Summary }}">
    <meta name="keywords" content="{{ .post.Tags | join "," }}">
    <meta property="og:title" content="{{ .post.Title }}">
    <meta property="og:description" content="{{ .post.Summary }}">
    <meta property="og:type" content="article">
    <meta property="og:url" content="{{ .post | shareURL }}">
    <meta property="article:published_time" content="{{ .post.PublishedAt.Format "2006-01-02T15:04:05Z07:00" }}">
    <meta property="article:modified_time" content="{{ .post.UpdatedAt.Format "2006-01-02T15:04:05Z07:00" }}">
    <meta property="article:author" content="{{ .post.Author.Name }}">
    {{ .post | structuredData }}
{{ end }}

{{ define "content" }}
<article class="blog-post">
    <header class="post-header">
        <h1 class="post-title">{{ .post.Title }}</h1>

        <div class="post-meta">
            <div class="author-info">
                <img src="{{ .post.Author.Avatar }}" alt="{{ .post.Author.Name }}" class="author-avatar">
                <div class="author-details">
                    <span class="author-name">{{ .post.Author.Name }}</span>
                    <time class="post-date" datetime="{{ .post.PublishedAt.Format "2006-01-02" }}">
                        {{ .post.PublishedAt | formatDateTime }}
                    </time>
                </div>
            </div>

            <div class="post-stats">
                <span class="reading-time">{{ .post.Content | readingTime }}分钟阅读</span>
                <span class="word-count">{{ .post.Content | wordCount }}字</span>
                <span class="views">{{ .post.Views }} 阅读</span>
                <span class="likes">{{ .post.Likes }} 点赞</span>
            </div>
        </div>

        {{ if .post.Category }}
        <div class="post-category">
            <a href="{{ .post.Category.Slug | categoryURL }}" class="category-badge">
                {{ .post.Category.Name }}
            </a>
        </div>
        {{ end }}
    </header>

    <div class="post-content">
        {{ .post.Content | safeHTML }}
    </div>

    {{ if .post.Tags }}
    <div class="post-tags">
        <h3>标签</h3>
        <div class="tags-list">
            {{ range .post.Tags }}
            <a href="{{ . | tagURL }}" class="tag">{{ . }}</a>
            {{ end }}
        </div>
    </div>
    {{ end }}

    <div class="post-share">
        <h3>分享</h3>
        <div class="share-buttons">
            {{ $shareURL := .post | shareURL }}
            <a href="{{ $shareURL.twitter }}" class="share-btn twitter" target="_blank">
                Twitter
            </a>
            <a href="{{ $shareURL.facebook }}" class="share-btn facebook" target="_blank">
                Facebook
            </a>
            <a href="{{ $shareURL.linkedin }}" class="share-btn linkedin" target="_blank">
                LinkedIn
            </a>
            <a href="{{ $shareURL.weibo }}" class="share-btn weibo" target="_blank">
                微博
            </a>
        </div>
    </div>

    <!-- 评论区 -->
    <div class="comments-section">
        <h3>评论 ({{ len .comments }})</h3>

        <!-- 评论列表 -->
        <div class="comments-list">
            {{ range .comments }}
            <div class="comment">
                <div class="comment-header">
                    <img src="{{ .Author.Avatar }}" alt="{{ .Author.Name }}" class="comment-avatar">
                    <div class="comment-info">
                        <span class="comment-author">{{ .Author.Name }}</span>
                        <time class="comment-time" datetime="{{ .CreatedAt.Format "2006-01-02" }}">
                            {{ .CreatedAt | formatRelative }}
                        </time>
                    </div>
                </div>
                <div class="comment-content">
                    {{ .Content | safeHTML }}
                </div>
            </div>
            {{ end }}
        </div>

        <!-- 评论表单 -->
        <div class="comment-form">
            <h4>发表评论</h4>
            <form method="POST" action="/blog/{{ .post.Slug }}/comment">
                <input type="hidden" name="csrf_token" value="{{ csrfToken }}">

                <div class="form-group">
                    <textarea name="content" class="form-control" rows="4"
                              placeholder="写下你的评论..." required></textarea>
                </div>

                <button type="submit" class="btn btn-primary">发表评论</button>
            </form>
        </div>
    </div>

    <!-- 相关文章 -->
    {{ if .related_posts }}
    <div class="related-posts">
        <h3>相关文章</h3>
        <div class="related-posts-grid">
            {{ range .related_posts }}
            <div class="related-post">
                <a href="/blog/{{ .Slug }}" class="related-post-link">
                    <h4>{{ .Title }}</h4>
                    <p>{{ .Content | excerpt 100 }}</p>
                    <small>{{ .PublishedAt | formatDate }}</small>
                </a>
            </div>
            {{ end }}
        </div>
    </div>
    {{ end }}
</article>
{{ end }}

{{ define "scripts" }}
    <script src="/static/js/blog-post.js"></script>
    <script nonce="{{ cspNonce }}">
        // 博客文章页面特定的JavaScript
        document.addEventListener('DOMContentLoaded', function() {
            // 初始化代码高亮
            initializeCodeHighlight();

            // 初始化图片懒加载
            initializeLazyLoading();

            // 初始化分享功能
            initializeShareButtons();
        });
    </script>
{{ end }}
{{ end }}
```

这个全面的Gin模板引擎与高级渲染技术文档涵盖了：

1. **模板引擎基础**：配置、目录结构、基本渲染
2. **HTML模板渲染**：基本语法、条件语句、循环结构
3. **模板继承与布局**：布局模板、页面继承、管理后台布局
4. **自定义模板函数**：字符串处理、时间处理、安全函数、分页函数
5. **模板数据处理**：数据结构、页面构建器、数据准备
6. **性能优化策略**：模板缓存、渲染优化、部分渲染
7. **安全防护措施**：XSS防护、CSRF防护、CSP策略
8. **实战案例**：完整博客系统、模板文件示例、安全实现

这个文档为Go开发者提供了Gin框架模板引擎的完整指南，从基础配置到高级优化，帮助开发者构建安全、高效、可维护的Web应用模板系统。