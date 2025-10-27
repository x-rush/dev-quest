# CSS-in-JS 和现代样式模式速查手册

> **文档简介**: 现代CSS解决方案快速参考，涵盖CSS-in-JS、Tailwind CSS、CSS Modules等主流样式方案
>
> **目标读者**: 前端开发者，需要快速查阅现代CSS写法的开发者
>
> **前置知识**: CSS基础、JavaScript基础、React基础
>
> **预计时长**: 20-40分钟

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `knowledge-points` |
| **难度** | ⭐⭐⭐ (3/5星) |
| **标签** | `#css-in-js` `#tailwindcss` `#styling-patterns` `#responsive-design` `#cheatsheet` |
| **更新日期** | `2025年10月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

---

## 🎨 Tailwind CSS 语法

### 基础类名
```jsx
// 文本样式
<h1 className="text-4xl font-bold text-gray-900 mb-4">
  标题文本
</h1>

<p className="text-base text-gray-600 leading-relaxed">
  正文内容，使用基础字号和灰色文本
</p>

// 颜色系统
<div className="bg-blue-500 text-white p-4 rounded-lg">
  蓝色背景白色文本的卡片
</div>

<button className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-2 rounded-md transition-colors">
  按钮组件
</button>

// 间距系统
<div className="p-4 m-2">
  // padding: 1rem, margin: 0.5rem
  <div className="px-6 py-3">
    // padding-x: 1.5rem, padding-y: 0.75rem
    内容区域
  </div>
</div>
```

### 响应式设计
```jsx
// 响应式前缀
<div className="w-full md:w-1/2 lg:w-1/3">
  // mobile: 全宽
  // medium: 一半宽度
  // large: 三分之一宽度
</div>

// 响应式文本
<h1 className="text-2xl sm:text-3xl md:text-4xl lg:text-5xl">
  响应式标题
</h1>

// 响应式布局
<div className="flex flex-col md:flex-row gap-4">
  <div className="flex-1">左侧内容</div>
  <div className="flex-1">右侧内容</div>
</div>

// 响应式显示/隐藏
<div className="hidden md:block">
  只在medium及以上显示
</div>

<div className="block md:hidden">
  只在mobile显示
</div>
```

### 状态和变体
```jsx
// 悬停状态
<button className="bg-blue-500 hover:bg-blue-700 text-white font-bold py-2 px-4 rounded">
  Hover效果
</button>

// 焦点状态
<input
  className="border border-gray-300 focus:border-blue-500 focus:ring-2 focus:ring-blue-200 rounded-md px-3 py-2"
  placeholder="输入框"
/>

// 激活状态
<button className="bg-green-500 active:bg-green-600 text-white px-4 py-2 rounded">
  点击按钮
</button>

// 禁用状态
<button
  className="bg-gray-400 text-gray-200 cursor-not-allowed px-4 py-2 rounded"
  disabled
>
  禁用按钮
</button>

// 组合状态
<button className="
  bg-blue-500
  hover:bg-blue-600
  focus:outline-none
  focus:ring-2
  focus:ring-blue-500
  focus:ring-offset-2
  text-white
  font-medium
  py-2
  px-4
  rounded-lg
  transition-colors
">
  完整状态按钮
</button>
```

### 组件样式
```jsx
// 卡片组件
function Card({ children, className = "" }) {
  return (
    <div className={`
      bg-white
      rounded-lg
      shadow-md
      border
      border-gray-200
      overflow-hidden
      ${className}
    `}>
      {children}
    </div>
  )
}

// 按钮组件变体
function Button({ variant = 'primary', size = 'medium', children, ...props }) {
  const baseClasses = "font-medium rounded-md transition-colors focus:outline-none focus:ring-2 focus:ring-offset-2"

  const variantClasses = {
    primary: "bg-blue-600 text-white hover:bg-blue-700 focus:ring-blue-500",
    secondary: "bg-gray-200 text-gray-900 hover:bg-gray-300 focus:ring-gray-500",
    danger: "bg-red-600 text-white hover:bg-red-700 focus:ring-red-500"
  }

  const sizeClasses = {
    small: "px-3 py-1.5 text-sm",
    medium: "px-4 py-2 text-base",
    large: "px-6 py-3 text-lg"
  }

  return (
    <button
      className={`${baseClasses} ${variantClasses[variant]} ${sizeClasses[size]}`}
      {...props}
    >
      {children}
    </button>
  )
}

// 使用组件
<Card className="p-6 mb-4">
  <h2 className="text-xl font-bold mb-2">卡片标题</h2>
  <p className="text-gray-600">卡片内容</p>
  <div className="mt-4 flex gap-2">
    <Button variant="primary">主要按钮</Button>
    <Button variant="secondary">次要按钮</Button>
  </div>
</Card>
```

---

## 🎯 CSS Modules

### 基础用法
```jsx
// styles.module.css
.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.title {
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.text {
  color: #6b7280;
  line-height: 1.6;
}

.button {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;
}

.button:hover {
  background: #2563eb;
}

// 组件中使用
import styles from './styles.module.css'

function Card({ title, content }) {
  return (
    <div className={styles.card}>
      <h2 className={styles.title}>{title}</h2>
      <p className={styles.text}>{content}</p>
      <button className={styles.button}>
        点击按钮
      </button>
    </div>
  )
}
```

### 组合和条件类名
```jsx
// styles.module.css
.button {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.primary {
  background: #3b82f6;
  color: white;
}

.secondary {
  background: #f3f4f6;
  color: #1f2937;
}

.large {
  padding: 0.75rem 1.5rem;
  font-size: 1.125rem;
}

.small {
  padding: 0.25rem 0.75rem;
  font-size: 0.875rem;
}

.disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

// 组件中使用 clsx 或 classnames
import clsx from 'clsx'
import styles from './Button.module.css'

function Button({
  variant = 'primary',
  size = 'medium',
  disabled = false,
  children,
  className,
  ...props
}) {
  return (
    <button
      className={clsx(
        styles.button,
        styles[variant],
        styles[size],
        disabled && styles.disabled,
        className
      )}
      disabled={disabled}
      {...props}
    >
      {children}
    </button>
  )
}
```

### CSS Variables 和 Modules
```jsx
// styles.module.css
:root {
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-secondary: #f3f4f6;
  --color-text: #1f2937;
  --color-text-light: #6b7280;
  --border-radius: 8px;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.card {
  background: white;
  border-radius: var(--border-radius);
  box-shadow: var(--shadow);
  padding: 1.5rem;
  margin-bottom: 1rem;
}

.themed {
  --color-primary: #10b981;
  --color-primary-hover: #059669;
}

// 组件中使用
import styles from './Card.module.css'

function Card({ theme = 'default', children }) {
  return (
    <div className={clsx(styles.card, theme === 'dark' && styles.themed)}>
      {children}
    </div>
  )
}
```

---

## 🎨 Styled Components (CSS-in-JS)

### 基础语法
```jsx
import styled from 'styled-components'

// 创建styled组件
const Button = styled.button`
  background: ${props => props.primary ? '#3b82f6' : '#f3f4f6'};
  color: ${props => props.primary ? 'white' : '#1f2937'};
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    background: ${props => props.primary ? '#2563eb' : '#e5e7eb'};
  }

  &:focus {
    outline: none;
    box-shadow: 0 0 0 2px ${props => props.primary ? '#3b82f6' : '#9ca3af'};
  }

  &:disabled {
    opacity: 0.5;
    cursor: not-allowed;
  }
`

// 使用styled组件
function App() {
  return (
    <div>
      <Button primary>主要按钮</Button>
      <Button>次要按钮</Button>
      <Button disabled>禁用按钮</Button>
    </div>
  )
}
```

### 继承和扩展
```jsx
// 基础按钮
const BaseButton = styled.button`
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
`

// 继承扩展
const PrimaryButton = styled(BaseButton)`
  background: #3b82f6;
  color: white;

  &:hover {
    background: #2563eb;
  }
`

const SecondaryButton = styled(BaseButton)`
  background: #f3f4f6;
  color: #1f2937;

  &:hover {
    background: #e5e7eb;
  }
`

// 使用attr添加属性
const Input = styled.input.attrs({ type: 'text' })`
  padding: 0.5rem;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 1rem;

  &:focus {
    outline: none;
    border-color: #3b82f6;
    box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.1);
  }
`
```

### 主题和上下文
```jsx
import styled, { ThemeProvider } from 'styled-components'

// 定义主题
const lightTheme = {
  colors: {
    primary: '#3b82f6',
    secondary: '#f3f4f6',
    text: '#1f2937',
    textLight: '#6b7280'
  },
  spacing: {
    small: '0.5rem',
    medium: '1rem',
    large: '1.5rem'
  }
}

const darkTheme = {
  colors: {
    primary: '#60a5fa',
    secondary: '#374151',
    text: '#f9fafb',
    textLight: '#d1d5db'
  },
  spacing: {
    small: '0.5rem',
    medium: '1rem',
    large: '1.5rem'
  }
}

// 使用主题的styled组件
const Card = styled.div`
  background: ${props => props.theme.colors.secondary};
  color: ${props => props.theme.colors.text};
  padding: ${props => props.theme.spacing.large};
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
`

// 使用ThemeProvider
function App() {
  const [theme, setTheme] = useState('light')

  return (
    <ThemeProvider theme={theme === 'light' ? lightTheme : darkTheme}>
      <Card>
        <h1>主题化卡片</h1>
        <button onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}>
          切换主题
        </button>
      </Card>
    </ThemeProvider>
  )
}
```

---

## 🎭 CSS-in-JS 库对比

### Emotion
```jsx
/** @jsxImportSource @emotion/react */
import { css, styled } from '@emotion/react'

// CSS prop 写法
const buttonStyle = css`
  background: ${props => props.primary ? '#3b82f6' : '#f3f4f6'};
  color: ${props => props.primary ? 'white' : '#1f2937'};
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.2s;

  &:hover {
    opacity: 0.8;
  }
`

function Button({ primary, children, ...props }) {
  return (
    <button css={buttonStyle} primary={primary} {...props}>
      {children}
    </button>
  )
}

// styled 写法
const StyledCard = styled.div`
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 1.5rem;

  h2 {
    margin: 0 0 0.5rem 0;
    color: #1f2937;
  }
`

// 动态样式
function DynamicComponent({ size, color }) {
  return (
    <div
      css={css`
        width: ${size}px;
        height: ${size}px;
        background: ${color};
        border-radius: 50%;
      `}
    />
  )
}
```

### Linaria (零运行时)
```jsx
import { styled } from '@linaria/react'
import { css } from '@linaria/core'

// 编译时CSS
const StyledButton = styled.button`
  background: ${props => props.primary ? '#3b82f6' : '#f3f4f6'};
  color: ${props => props.primary ? 'white' : '#1f2937'};
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 4px;
  cursor: pointer;

  &:hover {
    opacity: 0.8;
  }
`

// CSS标签
const titleStyle = css`
  font-size: 1.5rem;
  font-weight: bold;
  color: #1f2937;
  margin-bottom: 0.5rem;
`

function Card({ title, children }) {
  return (
    <div className="card">
      <h2 className={titleStyle}>{title}</h2>
      {children}
    </div>
  )
}
```

---

## 📱 响应式设计模式

### 移动优先设计
```jsx
// Tailwind CSS 移动优先
<div className="w-full md:w-3/4 lg:w-1/2 xl:w-1/3">
  <!-- 默认全宽，medium屏幕75%，large屏幕50%，xlarge屏幕33% -->
</div>

// CSS Modules 响应式
/* styles.module.css */
.container {
  width: 100%;
  padding: 1rem;
}

@media (min-width: 768px) {
  .container {
    width: 750px;
    margin: 0 auto;
    padding: 2rem;
  }
}

@media (min-width: 1024px) {
  .container {
    width: 1000px;
  }
}

// Styled Components 响应式
const ResponsiveGrid = styled.div`
  display: grid;
  gap: 1rem;
  grid-template-columns: 1fr;

  @media (min-width: 768px) {
    grid-template-columns: repeat(2, 1fr);
  }

  @media (min-width: 1024px) {
    grid-template-columns: repeat(3, 1fr);
  }
`
```

### 容器查询
```jsx
// CSS容器查询
/* styles.module.css */
.cardContainer {
  container-type: inline-size;
}

@container (min-width: 400px) {
  .card {
    display: flex;
    align-items: center;
    gap: 1rem;
  }

  .cardImage {
    width: 100px;
    height: 100px;
  }
}

// 组件中使用
function Card({ title, content, image }) {
  return (
    <div className={styles.cardContainer}>
      <div className={styles.card}>
        <img src={image} alt={title} className={styles.cardImage} />
        <div>
          <h3>{title}</h3>
          <p>{content}</p>
        </div>
      </div>
    </div>
  )
}
```

---

## 🎨 高级CSS技巧

### CSS变量动态主题
```jsx
// 主题变量定义
:root {
  --color-primary: #3b82f6;
  --color-primary-hover: #2563eb;
  --color-secondary: #f3f4f6;
  --color-text: #1f2937;
  --border-radius: 8px;
  --transition: all 0.2s ease;
}

[data-theme="dark"] {
  --color-primary: #60a5fa;
  --color-primary-hover: #3b82f6;
  --color-secondary: #374151;
  --color-text: #f9fafb;
}

// React组件中使用
function ThemedButton({ children, ...props }) {
  const [theme, setTheme] = useState('light')

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
  }, [theme])

  return (
    <button
      style={{
        background: 'var(--color-primary)',
        color: 'var(--color-text)',
        borderRadius: 'var(--border-radius)',
        transition: 'var(--transition)',
        padding: '0.5rem 1rem',
        border: 'none',
        cursor: 'pointer'
      }}
      onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
      {...props}
    >
      {children}
    </button>
  )
}
```

### 动画和过渡
```jsx
// Tailwind CSS 动画
<button className="
  transform
  transition-all
  duration-200
  ease-in-out
  hover:scale-105
  active:scale-95
">
  动画按钮
</button>

// CSS Modules 动画
/* styles.module.css */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fadeIn {
  animation: fadeIn 0.3s ease-out;
}

// Styled Components 动画
const AnimatedCard = styled.div`
  background: white;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(20px);
  opacity: 0;
  animation: slideIn 0.3s ease-out forwards;

  @keyframes slideIn {
    to {
      transform: translateY(0);
      opacity: 1;
    }
  }
`
```

---

## 🔧 性能优化

### CSS-in-JS 性能技巧
```jsx
// 使用 styled-components 的 shouldForwardProp
const OptimizedButton = styled.button.withConfig({
  shouldForwardProp: (prop) => !['primary', 'size'].includes(prop)
})`
  background: ${props => props.primary ? '#3b82f6' : '#f3f4f6'};
  padding: ${props => props.size === 'large' ? '1rem' : '0.5rem'};
`

// 使用 Emotion 的 @emotion/babel-plugin
// 配置后编译时提取CSS

// 使用 Linaria 零运行时方案
import { styled } from '@linaria/react'

const Button = styled.button`
  /* 编译时提取，运行时零开销 */
  background: #3b82f6;
`
```

### CSS 优化技巧
```jsx
// 避免内联样式
// ❌ 不推荐
<div style={{ backgroundColor: '#3b82f6', padding: '1rem' }}>

// ✅ 推荐
<div className="bg-blue-500 p-4">

// 使用CSS变量减少重复
:root {
  --spacing-1: 0.25rem;
  --spacing-2: 0.5rem;
  --spacing-4: 1rem;
}

// 关键CSS内联
// 将首屏CSS内联到HTML中
// 其他CSS异步加载

// 使用 content-visibility 优化长列表
.long-list {
  content-visibility: auto;
  contain-intrinsic-size: 500px;
}
```

---

## 🔄 文档交叉引用

### 相关文档
- 📄 **[React 语法速查](./01-react-syntax-cheatsheet.md)**: React组件中的样式应用
- 📄 **[Next.js API 参考](./02-nextjs-api-reference.md)**: Next.js中的样式配置和优化
- 📄 **[现代 JavaScript 语法速查](./04-javascript-modern.md)**: JavaScript操作CSS的现代化方法
- 📄 **[TypeScript 类型速查](./03-typescript-types.md)**: CSS-in-JS的TypeScript类型定义

### 参考章节
- 📖 **[App Router 模式](../framework-patterns/01-app-router-patterns.md)**: Next.js 13+中的样式布局模式
- 📖 **[客户端组件模式](../framework-patterns/03-client-components-patterns.md)**: React组件的样式策略
- 📖 **[状态管理模式](../framework-patterns/05-state-management-patterns.md)**: 状态变化时的样式响应
- 📖 **[表单验证模式](../framework-patterns/06-form-validation-patterns.md)**: 表单样式和验证状态的视觉反馈
- 📖 **[Tailwind CSS 样式](../../basics/05-styling-with-tailwind.md)**: Tailwind CSS在Next.js项目中的实际应用
- 📖 **[样式工具](../development-tools/02-styling-tools.md)**: CSS开发工具和调试技巧
- 📖 **[渲染优化](../performance-optimization/01-rendering-optimization.md)**: CSS性能优化和最佳实践

## 📝 总结

### 核心要点回顾
1. **Tailwind CSS**: 掌握了原子化CSS框架的使用，包括类名系统、响应式设计和状态管理
2. **CSS Modules**: 学会了局部作用域CSS的使用，避免样式冲突和命名污染
3. **CSS-in-JS**: 理解了Styled Components、Emotion等现代CSS解决方案的优势和应用场景
4. **响应式设计**: 掌握了移动优先的设计理念和不同屏幕尺寸的适配方案
5. **性能优化**: 学会了CSS性能优化技巧，包括零运行时方案和关键CSS优化

### 学习成果检查
- [ ] 是否能够熟练使用Tailwind CSS进行快速样式开发？
- [ ] 是否理解CSS Modules的作用域优势和适用场景？
- [ ] 是否能够选择合适的CSS-in-JS方案并正确使用？
- [ ] 是否能够实现响应式设计和移动优先布局？
- [ ] 是否具备了CSS性能优化和最佳实践的能力？

## 🤝 贡献与反馈

### 内容改进
如果你发现本文档有改进空间，欢迎：
- 🐛 **报告问题**: 在Issues中提出具体问题
- 💡 **建议改进**: 提出修改建议和补充内容
- 📝 **参与贡献**: 提交PR完善文档内容

### 学习反馈
分享你的学习体验：
- ✅ **有用内容**: 哪些部分对你最有帮助
- ❓ **疑问点**: 哪些内容需要进一步澄清
- 🎯 **建议**: 希望增加什么内容

## 🔗 外部资源

### 官方文档
- 📖 **[Tailwind CSS 文档](https://tailwindcss.com/docs)**: Tailwind CSS 完整官方文档
- 📖 **[CSS Modules 文档](https://github.com/css-modules/css-modules)**: CSS Modules 使用指南和规范
- 📖 **[Styled Components 文档](https://styled-components.com/docs)**: CSS-in-JS 库完整文档
- 📖 **[Emotion 文档](https://emotion.sh/docs/introduction)**: 高性能CSS-in-JS库文档
- 📖 **[现代CSS解决方案](https://moderncss.dev/)**: 现代CSS技术和最佳实践

### 快速参考

### Tailwind CSS 类名
- `text-{size}` - 文本大小 (text-sm, text-lg, text-xl)
- `bg-{color}` - 背景颜色 (bg-blue-500, bg-gray-100)
- `p-{size}` - 内边距 (p-4, px-6, py-2)
- `m-{size}` - 外边距 (m-4, mx-auto, my-2)
- `w-{size}` - 宽度 (w-full, w-1/2, w-64)
- `h-{size}` - 高度 (h-full, h-screen, h-32)

### 响应式前缀
- `sm:` - 640px+ (小屏幕)
- `md:` - 768px+ (中等屏幕)
- `lg:` - 1024px+ (大屏幕)
- `xl:` - 1280px+ (超大屏幕)
- `2xl:` - 1536px+ (超超大屏幕)

### 状态前缀
- `hover:` - 悬停状态
- `focus:` - 焦点状态
- `active:` - 激活状态
- `disabled:` - 禁用状态
- `group-hover:` - 群组悬停状态

### CSS-in-JS 方案选择
- **Tailwind CSS** - 原子化CSS，快速开发，团队协作友好
- **CSS Modules** - 局部作用域，传统CSS语法，构建时处理
- **Styled Components** - CSS-in-JS，动态样式，主题支持
- **Emotion** - 高性能CSS-in-JS，灵活的API设计
- **Linaria** - 零运行时CSS-in-JS，编译时优化

### 性能优化技巧
- 避免内联样式，使用CSS类名
- 使用CSS变量减少重复代码
- 关键CSS内联，非关键CSS异步加载
- 使用content-visibility优化长列表
- 选择合适的CSS-in-JS方案

---

**文档状态**: ✅ 已完成
**最后更新**: 2025年10月
**版本**: v1.0.0