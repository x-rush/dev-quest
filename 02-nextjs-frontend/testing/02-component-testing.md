# React组件测试指南 (Component Testing Guide)

> **文档简介**: 从PHP开发者视角深入理解React组件测试，掌握Next.js 16 + React 19现代测试工具栈和最佳实践。

> **目标读者**: 具备React基础，希望系统学习组件测试的中级开发者

> **前置知识**: React组件开发、JavaScript/TypeScript基础、测试基本概念

> **预计时长**: 3-4小时（理论学习）+ 2-3小时（实践练习）

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `02-nextjs-frontend` |
| **分类** | `testing` |
| **难度** | ⭐⭐⭐⭐ (4/5星) |
| **标签** | `#react-testing` `#component-testing` `#rtl` `#vitest` `#nextjs16` |
| **更新日期** | `2026年9月` |
| **作者** | Dev Quest Team |
| **状态** | ✅ 已完成 |

## 🎯 学习目标

完成本模块后，你将能够：

- ✅ **掌握React Testing Library**: 熟练使用RTL进行组件测试
- ✅ **编写有效测试**: 创建可维护、可读性强的测试用例
- ✅ **测试用户交互**: 模拟用户操作和验证组件响应
- ✅ **处理异步操作**: 测试API调用、状态更新等异步场景
- ✅ **Mock策略**: 合理使用Mock和Stub隔离测试
- ✅ **测试覆盖率**: 理解和提升测试覆盖率

## 📖 概述

组件测试是React应用测试的核心，它介于单元测试和集成测试之间，专注于验证组件的渲染、交互和状态管理。与传统的单元测试不同，React组件测试更关注用户行为而非实现细节，确保组件按用户预期工作。

### 为什么组件测试重要

1. **用户体验保证**: 验证组件从用户视角的正确性
2. **重构安全性**: 在组件重构时提供回归保护
3. **文档作用**: 测试用例展示组件的使用方式
4. **开发效率**: 快速验证组件修改的正确性
5. **团队协作**: 为团队成员提供组件行为规范

## 🛠️ 工具栈介绍

### 1. React Testing Library (RTL)
**核心理念**: 测试组件的方式与用户使用组件的方式相同

```bash
# 安装RTL
npm install -D @testing-library/react @testing-library/jest-dom
```

**关键特性**:
- 基于查询API（getByRole, getByText等）
- 支持异步操作测试
- 内置重试机制
- 专注于可访问性

### 2. Vitest
**现代测试框架**: 基于Vite的快速测试运行器

```bash
# Vitest配置支持
npm install -D vitest @vitest/ui jsdom @vitest/coverage-v8
```

**优势**:
- 与Vite无缝集成
- 快速的热重载测试
- 原生支持TypeScript
- 丰富的断言库

### 3. MSW (Mock Service Worker)
**API模拟工具**: 在测试中模拟网络请求

```bash
# 安装MSW
npm install -D msw
```

**特点**:
- 拦截实际网络请求
- 支持REST和GraphQL
- 与真实API行为一致

## 🔧 环境配置

### 1. 基础配置

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config"
import react from "@vitejs/plugin-react"
import path from "path"

export default defineConfig({
  plugins: [react()],
  test: {
    globals: true,
    environment: "jsdom",
    setupFiles: ["./__tests__/setup.ts"],
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "json"],
      exclude: [
        "node_modules/",
        "__tests__/",
        "**/*.d.ts",
        "**/*.config.*",
      ],
    },
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./"),
    },
  },
})
```

### 2. 测试设置文件

```typescript
// __tests__/setup.ts
import "@testing-library/jest-dom"
import { beforeAll, afterEach, afterAll } from "vitest"
import { setupServer } from "msw/node"
import { rest } from "msw"

// Mock API服务器
export const server = setupServer(
  // 示例API端点
  rest.get("/api/users", (req, res, ctx) => {
    return res(
      ctx.json([
        { id: 1, name: "John Doe", email: "john@example.com" },
        { id: 2, name: "Jane Smith", email: "jane@example.com" },
      ])
    )
  })
)

// 启动和关闭服务器
beforeAll(() => server.listen())
afterEach(() => server.resetHandlers())
afterAll(() => server.close())
```

### 3. 测试工具配置

```typescript
// __tests__/utils/test-utils.tsx
import { ReactElement } from "react"
import { render, RenderOptions } from "@testing-library/react"
import { QueryClient, QueryClientProvider } from "@tanstack/react-query"
import { BrowserRouter } from "react-router-dom"

// 创建测试用的QueryClient
const createTestQueryClient = () =>
  new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  })

// 自定义渲染函数
const AllTheProviders = ({ children }: { children: React.ReactNode }) => {
  const queryClient = createTestQueryClient()
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        {children}
      </BrowserRouter>
    </QueryClientProvider>
  )
}

const customRender = (
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper">
) => render(ui, { wrapper: AllTheProviders, ...options })

export * from "@testing-library/react"
export { customRender as render }
```

## 📋 测试策略

### 单元测试策略

**测试范围**:
- 组件渲染结果
- Props传递和处理
- 状态管理逻辑
- 事件处理函数

**测试原则**:
- 单一职责：每个测试关注一个功能点
- 隔离性：避免依赖外部状态
- 可重复性：测试结果应该一致
- 快速执行：避免不必要的等待

### 集成测试策略

**测试范围**:
- 组件间交互
- 父子组件通信
- Context使用
- 路由导航

**测试方法**:
- 使用真实组件而非Mock
- 测试完整用户流程
- 验证副作用和状态变化

### E2E测试策略

**与组件测试的边界**:
- E2E：完整业务流程验证
- 组件测试：组件行为验证
- 单元测试：函数逻辑验证

## 💻 实战示例

### 基础测试示例

#### 1. 简单组件测试

```typescript
// components/Button.tsx
interface ButtonProps {
  children: React.ReactNode
  onClick?: () => void
  variant?: "primary" | "secondary"
  disabled?: boolean
}

export const Button: React.FC<ButtonProps> = ({
  children,
  onClick,
  variant = "primary",
  disabled = false,
}) => {
  return (
    <button
      className={`btn btn-${variant}`}
      onClick={onClick}
      disabled={disabled}
    >
      {children}
    </button>
  )
}
```

```typescript
// __tests__/components/Button.test.tsx
import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { Button } from "@/components/Button"

describe("Button Component", () => {
  it("renders children correctly", () => {
    render(<Button>Click me</Button>)
    expect(screen.getByRole("button", { name: "Click me" })).toBeInTheDocument()
  })

  it("applies correct variant classes", () => {
    render(<Button variant="secondary">Button</Button>)
    const button = screen.getByRole("button")
    expect(button).toHaveClass("btn", "btn-secondary")
  })

  it("calls onClick when clicked", () => {
    const handleClick = vi.fn()
    render(<Button onClick={handleClick}>Click me</Button>)

    fireEvent.click(screen.getByRole("button"))
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it("is disabled when disabled prop is true", () => {
    render(<Button disabled>Disabled Button</Button>)
    const button = screen.getByRole("button")
    expect(button).toBeDisabled()
  })
})
```

#### 2. 表单组件测试

```typescript
// components/ContactForm.tsx
interface ContactFormProps {
  onSubmit: (data: { name: string; email: string; message: string }) => void
}

export const ContactForm: React.FC<ContactFormProps> = ({ onSubmit }) => {
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    message: "",
  })
  const [errors, setErrors] = useState<Record<string, string>>({})

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = e.target
    setFormData(prev => ({ ...prev, [name]: value }))
    // 清除对应字段的错误
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: "" }))
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    const newErrors: Record<string, string> = {}

    if (!formData.name.trim()) newErrors.name = "Name is required"
    if (!formData.email.trim()) newErrors.email = "Email is required"
    if (!formData.message.trim()) newErrors.message = "Message is required"

    if (Object.keys(newErrors).length === 0) {
      onSubmit(formData)
      setFormData({ name: "", email: "", message: "" })
    } else {
      setErrors(newErrors)
    }
  }

  return (
    <form onSubmit={handleSubmit} data-testid="contact-form">
      <div>
        <label htmlFor="name">Name</label>
        <input
          id="name"
          name="name"
          type="text"
          value={formData.name}
          onChange={handleChange}
          aria-invalid={!!errors.name}
          aria-describedby={errors.name ? "name-error" : undefined}
        />
        {errors.name && (
          <span id="name-error" role="alert">
            {errors.name}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="email">Email</label>
        <input
          id="email"
          name="email"
          type="email"
          value={formData.email}
          onChange={handleChange}
          aria-invalid={!!errors.email}
          aria-describedby={errors.email ? "email-error" : undefined}
        />
        {errors.email && (
          <span id="email-error" role="alert">
            {errors.email}
          </span>
        )}
      </div>

      <div>
        <label htmlFor="message">Message</label>
        <textarea
          id="message"
          name="message"
          value={formData.message}
          onChange={handleChange}
          rows={4}
          aria-invalid={!!errors.message}
          aria-describedby={errors.message ? "message-error" : undefined}
        />
        {errors.message && (
          <span id="message-error" role="alert">
            {errors.message}
          </span>
        )}
      </div>

      <button type="submit">Submit</button>
    </form>
  )
}
```

```typescript
// __tests__/components/ContactForm.test.tsx
import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { ContactForm } from "@/components/ContactForm"

describe("ContactForm Component", () => {
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    mockOnSubmit.mockClear()
  })

  it("renders form fields correctly", () => {
    render(<ContactForm onSubmit={mockOnSubmit} />)

    expect(screen.getByLabelText(/name/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/message/i)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /submit/i })).toBeInTheDocument()
  })

  it("shows validation errors for empty fields", async () => {
    const user = userEvent.setup()
    render(<ContactForm onSubmit={mockOnSubmit} />)

    const submitButton = screen.getByRole("button", { name: /submit/i })
    await user.click(submitButton)

    expect(screen.getByText("Name is required")).toBeInTheDocument()
    expect(screen.getByText("Email is required")).toBeInTheDocument()
    expect(screen.getByText("Message is required")).toBeInTheDocument()
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it("clears errors when user starts typing", async () => {
    const user = userEvent.setup()
    render(<ContactForm onSubmit={mockOnSubmit} />)

    // 先触发错误
    const submitButton = screen.getByRole("button", { name: /submit/i })
    await user.click(submitButton)

    expect(screen.getByText("Name is required")).toBeInTheDocument()

    // 开始输入名字
    const nameInput = screen.getByLabelText(/name/i)
    await user.type(nameInput, "John")

    expect(screen.queryByText("Name is required")).not.toBeInTheDocument()
  })

  it("submits form with valid data", async () => {
    const user = userEvent.setup()
    render(<ContactForm onSubmit={mockOnSubmit} />)

    // 填写表单
    await user.type(screen.getByLabelText(/name/i), "John Doe")
    await user.type(screen.getByLabelText(/email/i), "john@example.com")
    await user.type(screen.getByLabelText(/message/i), "Hello, world!")

    // 提交表单
    await user.click(screen.getByRole("button", { name: /submit/i }))

    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: "John Doe",
        email: "john@example.com",
        message: "Hello, world!",
      })
    })

    // 验证表单被重置
    expect(screen.getByLabelText(/name/i)).toHaveValue("")
    expect(screen.getByLabelText(/email/i)).toHaveValue("")
    expect(screen.getByLabelText(/message/i)).toHaveValue("")
  })

  it("has proper accessibility attributes", () => {
    render(<ContactForm onSubmit={mockOnSubmit} />)

    const form = screen.getByTestId("contact-form")
    expect(form).toHaveAttribute("role", "form")

    const nameInput = screen.getByLabelText(/name/i)
    expect(nameInput).toHaveAttribute("aria-invalid", "false")
  })
})
```

### 高级测试场景

#### 1. 异步组件测试

```typescript
// components/UserProfile.tsx
import { useQuery } from "@tanstack/react-query"

interface User {
  id: number
  name: string
  email: string
  avatar: string
}

export const UserProfile: React.FC<{ userId: number }> = ({ userId }) => {
  const { data: user, isLoading, error } = useQuery({
    queryKey: ["user", userId],
    queryFn: async () => {
      const response = await fetch(`/api/users/${userId}`)
      if (!response.ok) {
        throw new Error("Failed to fetch user")
      }
      return response.json()
    },
  })

  if (isLoading) return <div>Loading user profile...</div>
  if (error) return <div>Error loading user: {error.message}</div>
  if (!user) return <div>User not found</div>

  return (
    <div className="user-profile">
      <img src={user.avatar} alt={`${user.name}'s avatar`} />
      <h2>{user.name}</h2>
      <p>{user.email}</p>
    </div>
  )
}
```

```typescript
// __tests__/components/UserProfile.test.tsx
import { describe, it, expect, beforeEach } from "vitest"
import { render, screen, waitFor } from "@testing-library/react"
import { QueryClient } from "@tanstack/react-query"
import { UserProfile } from "@/components/UserProfile"
import { server } from "../setup"
import { rest } from "msw"

describe("UserProfile Component", () => {
  let queryClient: QueryClient

  beforeEach(() => {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: { retry: false },
      },
    })
  })

  it("shows loading state initially", () => {
    render(
      <QueryClientProvider client={queryClient}>
        <UserProfile userId={1} />
      </QueryClientProvider>
    )

    expect(screen.getByText("Loading user profile...")).toBeInTheDocument()
  })

  it("displays user data when fetch succeeds", async () => {
    const mockUser = {
      id: 1,
      name: "John Doe",
      email: "john@example.com",
      avatar: "https://example.com/avatar.jpg",
    }

    server.use(
      rest.get("/api/users/1", (req, res, ctx) => {
        return res(ctx.json(mockUser))
      })
    )

    render(
      <QueryClientProvider client={queryClient}>
        <UserProfile userId={1} />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText("John Doe")).toBeInTheDocument()
      expect(screen.getByText("john@example.com")).toBeInTheDocument()
    })

    const avatar = screen.getByAltText("John Doe's avatar")
    expect(avatar).toHaveAttribute("src", "https://example.com/avatar.jpg")
  })

  it("displays error message when fetch fails", async () => {
    server.use(
      rest.get("/api/users/1", (req, res, ctx) => {
        return res(ctx.status(500), ctx.json({ error: "Server error" }))
      })
    )

    render(
      <QueryClientProvider client={queryClient}>
        <UserProfile userId={1} />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText(/Error loading user/)).toBeInTheDocument()
    })
  })

  it("shows not found when user does not exist", async () => {
    server.use(
      rest.get("/api/users/999", (req, res, ctx) => {
        return res(ctx.status(404), ctx.json({}))
      })
    )

    render(
      <QueryClientProvider client={queryClient}>
        <UserProfile userId={999} />
      </QueryClientProvider>
    )

    await waitFor(() => {
      expect(screen.getByText("User not found")).toBeInTheDocument()
    })
  })
})
```

#### 2. 自定义Hook测试

```typescript
// hooks/useLocalStorage.ts
import { useState, useEffect } from "react"

export function useLocalStorage<T>(key: string, initialValue: T) {
  const [storedValue, setStoredValue] = useState<T>(() => {
    if (typeof window === "undefined") {
      return initialValue
    }
    try {
      const item = window.localStorage.getItem(key)
      return item ? JSON.parse(item) : initialValue
    } catch (error) {
      console.error(`Error reading localStorage key "${key}":`, error)
      return initialValue
    }
  })

  const setValue = (value: T | ((val: T) => T)) => {
    try {
      const valueToStore = value instanceof Function ? value(storedValue) : value
      setStoredValue(valueToStore)
      if (typeof window !== "undefined") {
        window.localStorage.setItem(key, JSON.stringify(valueToStore))
      }
    } catch (error) {
      console.error(`Error setting localStorage key "${key}":`, error)
    }
  }

  return [storedValue, setValue] as const
}
```

```typescript
// __tests__/hooks/useLocalStorage.test.ts
import { describe, it, expect, beforeEach, afterEach } from "vitest"
import { renderHook, act } from "@testing-library/react"
import { useLocalStorage } from "@/hooks/useLocalStorage"

describe("useLocalStorage Hook", () => {
  beforeEach(() => {
    // 清除localStorage
    localStorage.clear()
  })

  afterEach(() => {
    localStorage.clear()
  })

  it("returns initial value when localStorage is empty", () => {
    const { result } = renderHook(() => useLocalStorage("test-key", "initial-value"))

    const [value] = result.current
    expect(value).toBe("initial-value")
  })

  it("returns stored value from localStorage", () => {
    localStorage.setItem("test-key", JSON.stringify("stored-value"))

    const { result } = renderHook(() => useLocalStorage("test-key", "initial-value"))

    const [value] = result.current
    expect(value).toBe("stored-value")
  })

  it("updates localStorage when value changes", () => {
    const { result } = renderHook(() => useLocalStorage("test-key", "initial-value"))

    const [, setValue] = result.current

    act(() => {
      setValue("new-value")
    })

    expect(result.current[0]).toBe("new-value")
    expect(localStorage.getItem("test-key")).toBe(JSON.stringify("new-value"))
  })

  it("works with function updater", () => {
    const { result } = renderHook(() => useLocalStorage("counter", 0))

    const [, setCounter] = result.current

    act(() => {
      setCounter(prev => prev + 1)
    })

    expect(result.current[0]).toBe(1)
    expect(localStorage.getItem("counter")).toBe("1")
  })

  it("handles complex objects", () => {
    const initialObject = { name: "John", age: 30 }
    const { result } = renderHook(() => useLocalStorage("user", initialObject))

    const [, setUser] = result.current

    act(() => {
      setUser({ ...initialObject, age: 31 })
    })

    expect(result.current[0]).toEqual({ name: "John", age: 31 })
    expect(localStorage.getItem("user")).toBe(JSON.stringify({ name: "John", age: 31 }))
  })
})
```

#### 3. Context Provider测试

```typescript
// context/AuthContext.tsx
interface AuthContextType {
  user: User | null
  login: (email: string, password: string) => Promise<boolean>
  logout: () => void
  isLoading: boolean
}

const AuthContext = createContext<AuthContextType | undefined>(undefined)

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  const login = async (email: string, password: string): Promise<boolean> => {
    setIsLoading(true)
    try {
      const response = await fetch("/api/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      })

      if (response.ok) {
        const userData = await response.json()
        setUser(userData)
        return true
      }
      return false
    } catch (error) {
      console.error("Login error:", error)
      return false
    } finally {
      setIsLoading(false)
    }
  }

  const logout = () => {
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider")
  }
  return context
}
```

```typescript
// __tests__/context/AuthContext.test.tsx
import { describe, it, expect, beforeEach } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { AuthProvider, useAuth } from "@/context/AuthContext"
import { server } from "../setup"
import { rest } from "msw"

// 测试组件
const TestComponent = () => {
  const { user, login, logout, isLoading } = useAuth()

  const handleLogin = async () => {
    const success = await login("test@example.com", "password")
    if (success) {
      console.log("Login successful")
    }
  }

  return (
    <div>
      {isLoading && <div data-testid="loading">Loading...</div>}
      {user ? (
        <div>
          <span data-testid="user-email">{user.email}</span>
          <button onClick={logout}>Logout</button>
        </div>
      ) : (
        <button onClick={handleLogin}>Login</button>
      )}
    </div>
  )
}

describe("AuthContext", () => {
  const mockUser = { id: 1, email: "test@example.com", name: "Test User" }

  beforeEach(() => {
    server.resetHandlers()
  })

  it("provides initial context values", () => {
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    expect(screen.getByRole("button", { name: "Login" })).toBeInTheDocument()
    expect(screen.queryByTestId("user-email")).not.toBeInTheDocument()
  })

  it("handles successful login", async () => {
    server.use(
      rest.post("/api/auth/login", (req, res, ctx) => {
        return res(ctx.json(mockUser))
      })
    )

    const user = userEvent.setup()
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await user.click(screen.getByRole("button", { name: "Login" }))

    await waitFor(() => {
      expect(screen.getByTestId("user-email")).toHaveTextContent("test@example.com")
    })
  })

  it("handles login failure", async () => {
    server.use(
      rest.post("/api/auth/login", (req, res, ctx) => {
        return res(ctx.status(401), ctx.json({ error: "Invalid credentials" }))
      })
    )

    const user = userEvent.setup()
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await user.click(screen.getByRole("button", { name: "Login" }))

    // 确保没有显示用户信息
    expect(screen.queryByTestId("user-email")).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Login" })).toBeInTheDocument()
  })

  it("handles logout", async () => {
    server.use(
      rest.post("/api/auth/login", (req, res, ctx) => {
        return res(ctx.json(mockUser))
      })
    )

    const user = userEvent.setup()
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    // 先登录
    await user.click(screen.getByRole("button", { name: "Login" }))

    await waitFor(() => {
      expect(screen.getByTestId("user-email")).toBeInTheDocument()
    })

    // 然后登出
    await user.click(screen.getByRole("button", { name: "Logout" }))

    expect(screen.queryByTestId("user-email")).not.toBeInTheDocument()
    expect(screen.getByRole("button", { name: "Login" })).toBeInTheDocument()
  })

  it("shows loading state during login", async () => {
    server.use(
      rest.post("/api/auth/login", (req, res, ctx) => {
        return res(ctx.delay(100), ctx.json(mockUser))
      })
    )

    const user = userEvent.setup()
    render(
      <AuthProvider>
        <TestComponent />
      </AuthProvider>
    )

    await user.click(screen.getByRole("button", { name: "Login" }))

    expect(screen.getByTestId("loading")).toBeInTheDocument()

    await waitFor(() => {
      expect(screen.queryByTestId("loading")).not.toBeInTheDocument()
    })
  })
})
```

### 复杂组件测试

#### 1. 数据表格组件

```typescript
// components/DataTable.tsx
interface Column<T> {
  key: keyof T
  title: string
  render?: (value: any, record: T) => React.ReactNode
  sortable?: boolean
}

interface DataTableProps<T> {
  data: T[]
  columns: Column<T>[]
  loading?: boolean
  onSort?: (key: keyof T, direction: "asc" | "desc") => void
  onRowClick?: (record: T) => void
}

export function DataTable<T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  onSort,
  onRowClick,
}: DataTableProps<T>) {
  const [sortKey, setSortKey] = useState<keyof T | null>(null)
  const [sortDirection, setSortDirection] = useState<"asc" | "desc">("asc")

  const handleSort = (key: keyof T) => {
    if (!onSort) return

    const newDirection = sortKey === key && sortDirection === "asc" ? "desc" : "asc"
    setSortKey(key)
    setSortDirection(newDirection)
    onSort(key, newDirection)
  }

  if (loading) {
    return <div data-testid="loading">Loading data...</div>
  }

  return (
    <div className="data-table">
      <table>
        <thead>
          <tr>
            {columns.map((column) => (
              <th key={String(column.key)}>
                {column.sortable ? (
                  <button
                    onClick={() => handleSort(column.key)}
                    aria-label={`Sort by ${column.title}`}
                  >
                    {column.title}
                    {sortKey === column.key && (
                      <span>{sortDirection === "asc" ? " ↑" : " ↓"}</span>
                    )}
                  </button>
                ) : (
                  column.title
                )}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((record, index) => (
            <tr
              key={index}
              onClick={() => onRowClick?.(record)}
              style={{ cursor: onRowClick ? "pointer" : "default" }}
            >
              {columns.map((column) => (
                <td key={String(column.key)}>
                  {column.render
                    ? column.render(record[column.key], record)
                    : record[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {data.length === 0 && (
        <div data-testid="no-data">No data available</div>
      )}
    </div>
  )
}
```

```typescript
// __tests__/components/DataTable.test.tsx
import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { DataTable } from "@/components/DataTable"

interface TestData {
  id: number
  name: string
  email: string
  status: "active" | "inactive"
}

describe("DataTable Component", () => {
  const mockData: TestData[] = [
    { id: 1, name: "John Doe", email: "john@example.com", status: "active" },
    { id: 2, name: "Jane Smith", email: "jane@example.com", status: "inactive" },
  ]

  const columns = [
    { key: "id" as keyof TestData, title: "ID" },
    { key: "name" as keyof TestData, title: "Name" },
    { key: "email" as keyof TestData, title: "Email" },
    {
      key: "status" as keyof TestData,
      title: "Status",
      render: (status: string) => (
        <span className={`status-${status}`}>{status}</span>
      ),
      sortable: true,
    },
  ]

  it("renders table with data correctly", () => {
    render(<DataTable data={mockData} columns={columns} />)

    expect(screen.getByText("ID")).toBeInTheDocument()
    expect(screen.getByText("Name")).toBeInTheDocument()
    expect(screen.getByText("Email")).toBeInTheDocument()
    expect(screen.getByText("Status")).toBeInTheDocument()

    expect(screen.getByText("John Doe")).toBeInTheDocument()
    expect(screen.getByText("john@example.com")).toBeInTheDocument()
    expect(screen.getByText("jane@example.com")).toBeInTheDocument()
  })

  it("shows loading state", () => {
    render(<DataTable data={[]} columns={columns} loading={true} />)

    expect(screen.getByTestId("loading")).toHaveTextContent("Loading data...")
    expect(screen.queryByRole("table")).not.toBeInTheDocument()
  })

  it("shows no data message when data is empty", () => {
    render(<DataTable data={[]} columns={columns} />)

    expect(screen.getByTestId("no-data")).toHaveTextContent("No data available")
  })

  it("renders custom cell content", () => {
    render(<DataTable data={mockData} columns={columns} />)

    const statusElements = screen.getAllByText(/active|inactive/)
    expect(statusElements).toHaveLength(2)
    expect(statusElements[0]).toHaveClass("status-active")
    expect(statusElements[1]).toHaveClass("status-inactive")
  })

  it("handles row click", async () => {
    const mockOnRowClick = vi.fn()
    const user = userEvent.setup()

    render(
      <DataTable data={mockData} columns={columns} onRowClick={mockOnRowClick} />
    )

    const firstRow = screen.getByText("John Doe").closest("tr")
    await user.click(firstRow!)

    expect(mockOnRowClick).toHaveBeenCalledWith(mockData[0])
  })

  it("handles column sorting", async () => {
    const mockOnSort = vi.fn()
    const user = userEvent.setup()

    render(
      <DataTable data={mockData} columns={columns} onSort={mockOnSort} />
    )

    const sortButton = screen.getByLabelText(/Sort by Status/)
    await user.click(sortButton)

    expect(mockOnSort).toHaveBeenCalledWith("status", "asc")
  })

  it("updates sort direction on same column click", async () => {
    const mockOnSort = vi.fn()
    const user = userEvent.setup()

    render(
      <DataTable data={mockData} columns={columns} onSort={mockOnSort} />
    )

    const sortButton = screen.getByLabelText(/Sort by Status/)

    // 第一次点击
    await user.click(sortButton)
    expect(mockOnSort).toHaveBeenLastCalledWith("status", "asc")

    // 第二次点击同一列
    await user.click(sortButton)
    expect(mockOnSort).toHaveBeenLastCalledWith("status", "desc")
  })

  it("does not call onSort when column is not sortable", () => {
    const mockOnSort = vi.fn()

    render(
      <DataTable data={mockData} columns={columns} onSort={mockOnSort} />
    )

    // 尝试点击不可排序的列标题
    const nameHeader = screen.getByText("Name")
    expect(nameHeader.tagName).toBe("TH")
    expect(nameHeader.closest("button")).toBeNull()
  })
})
```

### 异步操作测试

#### 1. 防抖搜索组件

```typescript
// components/SearchInput.tsx
import { useDebounce } from "@/hooks/useDebounce"

interface SearchInputProps {
  onSearch: (query: string) => Promise<void>
  placeholder?: string
  debounceMs?: number
}

export const SearchInput: React.FC<SearchInputProps> = ({
  onSearch,
  placeholder = "Search...",
  debounceMs = 300,
}) => {
  const [query, setQuery] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const debouncedQuery = useDebounce(query, debounceMs)

  useEffect(() => {
    if (debouncedQuery.trim()) {
      setIsLoading(true)
      onSearch(debouncedQuery).finally(() => {
        setIsLoading(false)
      })
    }
  }, [debouncedQuery, onSearch])

  return (
    <div className="search-input">
      <input
        type="text"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        placeholder={placeholder}
        aria-label="Search"
      />
      {isLoading && <span data-testid="search-loading">Searching...</span>}
    </div>
  )
}
```

```typescript
// __tests__/components/SearchInput.test.tsx
import { describe, it, expect, vi, beforeEach } from "vitest"
import { render, screen, fireEvent, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { SearchInput } from "@/components/SearchInput"

describe("SearchInput Component", () => {
  const mockOnSearch = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it("renders input with placeholder", () => {
    render(<SearchInput onSearch={mockOnSearch} placeholder="Search users..." />)

    const input = screen.getByLabelText("Search")
    expect(input).toBeInTheDocument()
    expect(input).toHaveAttribute("placeholder", "Search users...")
  })

  it("does not call onSearch immediately on input change", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(<SearchInput onSearch={mockOnSearch} />)

    const input = screen.getByLabelText("Search")
    await user.type(input, "test")

    // 立即检查，不应该调用onSearch
    expect(mockOnSearch).not.toHaveBeenCalled()
  })

  it("calls onSearch after debounce delay", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(<SearchInput onSearch={mockOnSearch} debounceMs={500} />)

    const input = screen.getByLabelText("Search")
    await user.type(input, "test query")

    // 等待防抖延迟
    vi.advanceTimersByTime(500)

    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith("test query")
    })
  })

  it("does not call onSearch for empty query", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(<SearchInput onSearch={mockOnSearch} />)

    const input = screen.getByLabelText("Search")
    await user.type(input, "   ")

    vi.advanceTimersByTime(300)

    await waitFor(() => {
      expect(mockOnSearch).not.toHaveBeenCalled()
    })
  })

  it("shows loading state during search", async () => {
    const mockPromise = new Promise<void>((resolve) => {
      setTimeout(resolve, 100)
    })
    mockOnSearch.mockReturnValue(mockPromise)

    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(<SearchInput onSearch={mockOnSearch} />)

    const input = screen.getByLabelText("Search")
    await user.type(input, "test")

    vi.advanceTimersByTime(300)

    // 检查loading状态
    await waitFor(() => {
      expect(screen.getByTestId("search-loading")).toBeInTheDocument()
    })

    // 完成搜索
    vi.advanceTimersByTime(100)

    await waitFor(() => {
      expect(screen.queryByTestId("search-loading")).not.toBeInTheDocument()
    })
  })

  it("resets debounce timer on rapid input changes", async () => {
    const user = userEvent.setup({ advanceTimers: vi.advanceTimersByTime })
    render(<SearchInput onSearch={mockOnSearch} debounceMs={500} />)

    const input = screen.getByLabelText("Search")

    // 快速输入多个字符
    await user.type(input, "a")
    vi.advanceTimersByTime(250)

    await user.type(input, "b")
    vi.advanceTimersByTime(250)

    await user.type(input, "c")
    vi.advanceTimersByTime(500)

    // 只有最后一次输入应该触发搜索
    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledTimes(1)
      expect(mockOnSearch).toHaveBeenCalledWith("abc")
    })
  })
})
```

### 错误边界测试

```typescript
// components/ErrorBoundary.tsx
interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

export class ErrorBoundary extends React.Component<
  React.PropsWithChildren<{}>,
  ErrorBoundaryState
> {
  constructor(props: React.PropsWithChildren<{}>) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error("ErrorBoundary caught an error:", error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div data-testid="error-boundary">
          <h2>Something went wrong</h2>
          <p>{this.state.error?.message}</p>
          <button onClick={() => this.setState({ hasError: false })}>
            Try again
          </button>
        </div>
      )
    }

    return this.props.children
  }
}
```

```typescript
// __tests__/components/ErrorBoundary.test.tsx
import { describe, it, expect, vi } from "vitest"
import { render, screen, fireEvent } from "@testing-library/react"
import { ErrorBoundary } from "@/components/ErrorBoundary"

// 会抛出错误的组件
const ThrowError: React.FC<{ shouldThrow?: boolean }> = ({ shouldThrow = true }) => {
  if (shouldThrow) {
    throw new Error("Test error")
  }
  return <div>No error</div>
}

describe("ErrorBoundary Component", () => {
  // 抑制控制台错误输出
  beforeEach(() => {
    vi.spyOn(console, "error").mockImplementation(() => {})
  })

  afterEach(() => {
    vi.restoreAllMocks()
  })

  it("renders children when there is no error", () => {
    render(
      <ErrorBoundary>
        <div>Normal content</div>
      </ErrorBoundary>
    )

    expect(screen.getByText("Normal content")).toBeInTheDocument()
    expect(screen.queryByTestId("error-boundary")).not.toBeInTheDocument()
  })

  it("catches and displays error when child component throws", () => {
    render(
      <ErrorBoundary>
        <ThrowError />
      </ErrorBoundary>
    )

    expect(screen.getByTestId("error-boundary")).toBeInTheDocument()
    expect(screen.getByText("Something went wrong")).toBeInTheDocument()
    expect(screen.getByText("Test error")).toBeInTheDocument()
  })

  it("provides reset functionality", () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowError shouldThrow={true} />
      </ErrorBoundary>
    )

    expect(screen.getByTestId("error-boundary")).toBeInTheDocument()

    // 点击重置按钮
    fireEvent.click(screen.getByText("Try again"))

    // 重新渲染不抛错的组件
    rerender(
      <ErrorBoundary>
        <ThrowError shouldThrow={false} />
      </ErrorBoundary>
    )

    expect(screen.queryByTestId("error-boundary")).not.toBeInTheDocument()
    expect(screen.getByText("No error")).toBeInTheDocument()
  })
})
```

## 🎨 测试最佳实践

### 测试组织结构

**文件组织**:
```
__tests__/
├── components/          # 组件测试
│   ├── Button.test.tsx
│   ├── Form.test.tsx
│   └── utils.test.ts
├── hooks/              # Hook测试
│   └── useLocalStorage.test.ts
├── pages/              # 页面测试
│   └── HomePage.test.tsx
├── utils/              # 工具函数测试
│   └── formatters.test.ts
├── setup.ts            # 测试设置
├── utils.tsx           # 测试工具
└── mocks/              # Mock数据
    └── handlers.ts
```

**测试分组策略**:
- 按功能模块分组
- 按组件复杂度分层
- 集成测试与单元测试分离

### 命名规范

**测试文件命名**:
- 组件测试: `ComponentName.test.tsx`
- Hook测试: `useHookName.test.ts`
- 工具函数测试: `utilityFunction.test.ts`
- 页面测试: `PageName.test.tsx`

**测试描述规范**:
```typescript
describe("ComponentName", () => {
  describe("when props are valid", () => {
    it("renders correctly")
    it("handles user interactions")
  })

  describe("when props are invalid", () => {
    it("shows error states")
    it("handles edge cases")
  })
})
```

### 测试数据管理

**使用工厂模式创建测试数据**:
```typescript
// __tests__/factories/userFactory.ts
export const createUser = (overrides?: Partial<User>): User => ({
  id: 1,
  name: "Test User",
  email: "test@example.com",
  avatar: "https://example.com/avatar.jpg",
  ...overrides,
})

export const createUsers = (count: number, overrides?: Partial<User>): User[] =>
  Array.from({ length: count }, (_, index) =>
    createUser({ id: index + 1, ...overrides })
  )
```

**使用Fixtures管理共享数据**:
```typescript
// __tests__/fixtures/data.ts
export const FIXTURES = {
  users: [
    { id: 1, name: "John Doe", email: "john@example.com" },
    { id: 2, name: "Jane Smith", email: "jane@example.com" },
  ],
  posts: [
    { id: 1, title: "First Post", userId: 1 },
    { id: 2, title: "Second Post", userId: 2 },
  ],
} as const
```

### Mock和Stub策略

**API Mock最佳实践**:
```typescript
// __tests__/mocks/handlers.ts
import { rest } from "msw"

export const handlers = [
  // 成功响应
  rest.get("/api/users", (req, res, ctx) => {
    return res(
      ctx.status(200),
      ctx.json([{ id: 1, name: "John Doe" }])
    )
  }),

  // 错误响应
  rest.get("/api/users/:id", (req, res, ctx) => {
    const { id } = req.params
    if (id === "999") {
      return res(ctx.status(404), ctx.json({ error: "User not found" }))
    }
    return res(ctx.status(500), ctx.json({ error: "Server error" }))
  }),

  // 延迟响应（测试loading状态）
  rest.post("/api/users", (req, res, ctx) => {
    return res(
      ctx.delay(1000),
      ctx.status(201),
      ctx.json({ id: 2, name: "New User" })
    )
  }),
]
```

**组件Mock策略**:
```typescript
// Mock子组件
vi.mock("@/components/ChildComponent", () => ({
  ChildComponent: ({ children }: { children: React.ReactNode }) => (
    <div data-testid="mock-child-component">{children}</div>
  ),
}))

// Mock自定义Hook
vi.mock("@/hooks/useAuth", () => ({
  useAuth: () => ({
    user: { id: 1, name: "Test User" },
    login: vi.fn(),
    logout: vi.fn(),
    isLoading: false,
  }),
}))
```

## 🔍 高级测试技术

### 测试覆盖率

**配置覆盖率目标**:
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    coverage: {
      provider: "v8",
      reporter: ["text", "html", "json", "lcov"],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
      exclude: [
        "node_modules/",
        "__tests__/",
        "**/*.d.ts",
        "**/*.config.*",
        "coverage/",
      ],
    },
  },
})
```

**覆盖率报告分析**:
```bash
# 生成覆盖率报告
npm run test:coverage

# 查看HTML报告
open coverage/index.html

# 检查未覆盖的文件
npx vitest --coverage --reporter=verbose
```

### 测试性能优化

**并行测试执行**:
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    pool: "threads", // 使用多线程
    poolOptions: {
      threads: {
        maxThreads: 4, // 限制线程数
      },
    },
    isolate: true, // 隔离测试环境
  },
})
```

**智能测试选择**:
```bash
# 只运行相关测试
npx vitest --run src/components/Button

# 运行变更文件的测试
npx vitest --run --changed

# 监听模式，只运行相关测试
npx vitest src/
```

### 并发测试

**测试并发场景**:
```typescript
describe("Concurrent Operations", () => {
  it("handles concurrent state updates", async () => {
    const { result } = renderHook(() => useCounter())

    // 并发执行多个更新
    await Promise.all([
      act(() => result.current.increment()),
      act(() => result.current.increment()),
      act(() => result.current.increment()),
    ])

    expect(result.current.count).toBe(3)
  })
})
```

### 可视化回归测试

**使用Chromatic进行视觉测试**:
```typescript
// .storybook/main.ts
import type { StorybookConfig } from "@storybook/nextjs"

const config: StorybookConfig = {
  stories: ["../src/**/*.stories.@(js|jsx|ts|tsx|mdx)"],
  addons: [
    "@storybook/addon-essentials",
    "@storybook/addon-interactions",
    "@chromatic-com/storybook",
  ],
  framework: {
    name: "@storybook/nextjs",
    options: {},
  },
}

export default config
```

## 🚀 CI/CD集成

### 自动化测试流程

**GitHub Actions配置**:
```yaml
# .github/workflows/test.yml
name: Tests

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    strategy:
      matrix:
        node-version: [18.x, 20.x]

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: "npm"

      - name: Install dependencies
        run: npm ci

      - name: Run type check
        run: npm run type-check

      - name: Run linting
        run: npm run lint

      - name: Run tests
        run: npm run test:coverage

      - name: Upload coverage to Codecov
        uses: codecov/codecov-action@v3
        with:
          file: ./coverage/lcov.info
          flags: unittests
          name: codecov-umbrella

      - name: Run E2E tests
        run: npm run test:e2e
```

### 测试报告

**生成测试报告**:
```typescript
// vitest.config.ts
export default defineConfig({
  test: {
    reporter: ["verbose", "html", "json"],
    outputFile: {
      json: "./test-results/results.json",
      html: "./test-results/index.html",
    },
  },
})
```

### 质量门禁

**SonarQube集成**:
```yaml
# .github/workflows/quality.yml
- name: SonarCloud Scan
  uses: SonarSource/sonarcloud-github-action@master
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
    SONAR_TOKEN: ${{ secrets.SONAR_TOKEN }}
```

**质量检查脚本**:
```bash
#!/bin/bash
# scripts/quality-check.sh

echo "Running quality checks..."

# 运行测试
npm run test:coverage
COVERAGE_EXIT_CODE=$?

# 检查覆盖率阈值
COVERAGE=$(npx vitest run --coverage --reporter=json | jq -r '.coverageMap.total.lines.pct')
if (( $(echo "$COVERAGE < 80" | bc -l) )); then
  echo "Coverage below threshold: $COVERAGE%"
  exit 1
fi

# 运行类型检查
npm run type-check
TYPE_CHECK_EXIT_CODE=$?

# 运行linting
npm run lint
LINT_EXIT_CODE=$?

# 综合退出码
if [ $COVERAGE_EXIT_CODE -eq 0 ] && [ $TYPE_CHECK_EXIT_CODE -eq 0 ] && [ $LINT_EXIT_CODE -eq 0 ]; then
  echo "All quality checks passed!"
  exit 0
else
  echo "Some quality checks failed!"
  exit 1
fi
```

## 📊 测试监控和分析

### 测试结果分析

**测试性能监控**:
```typescript
// __tests__/utils/performance.ts
export const measureTestPerformance = (testName: string, testFn: () => void) => {
  const start = performance.now()
  testFn()
  const end = performance.now()

  console.log(`${testName} took ${end - start} milliseconds`)

  if (end - start > 1000) {
    console.warn(`${testName} is taking too long!`)
  }
}
```

**Flaky测试检测**:
```typescript
// __tests__/utils/flakyDetector.ts
export const runTestMultipleTimes = async (
  testFn: () => Promise<void>,
  times: number = 3
) => {
  const results = []

  for (let i = 0; i < times; i++) {
    try {
      await testFn()
      results.push({ success: true, attempt: i + 1 })
    } catch (error) {
      results.push({ success: false, attempt: i + 1, error })
    }
  }

  const failures = results.filter(r => !r.success)
  if (failures.length > 0) {
    console.warn(`Test failed ${failures.length}/${times} times:`, failures)
  }

  return results
}
```

### 质量指标追踪

**测试指标仪表板**:
```typescript
// __tests__/utils/metrics.ts
export interface TestMetrics {
  totalTests: number
  passedTests: number
  failedTests: number
  coverage: number
  averageTestTime: number
  flakyTests: string[]
}

export const generateTestReport = async (): Promise<TestMetrics> => {
  // 运行测试并收集指标
  const testResults = await runTests()
  const coverageReport = await generateCoverageReport()

  return {
    totalTests: testResults.total,
    passedTests: testResults.passed,
    failedTests: testResults.failed,
    coverage: coverageReport.total,
    averageTestTime: testResults.averageTime,
    flakyTests: testResults.flaky,
  }
}
```

### 性能基准测试

**组件性能测试**:
```typescript
// __tests__/performance/ComponentPerformance.test.tsx
import { render, measurePerformance } from "@testing-library/react"
import { HeavyComponent } from "@/components/HeavyComponent"

describe("Component Performance", () => {
  it("renders within acceptable time", async () => {
    const { duration } = await measurePerformance(() =>
      render(<HeavyComponent data={largeDataSet} />)
    )

    expect(duration).toBeLessThan(100) // 100ms阈值
  })

  it("handles large datasets efficiently", async () => {
    const largeDataSet = Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
    }))

    const { duration } = await measurePerformance(() =>
      render(<HeavyComponent data={largeDataSet} />)
    )

    expect(duration).toBeLessThan(500) // 大数据集阈值
  })
})
```

## 🔄 文档交叉引用

### 相关文档
- 📄 **[单元测试指南](./01-unit-testing.md)**: 单元测试基础知识和工具使用
- 📄 **[E2E测试指南](./03-e2e-testing.md)**: 端到端测试策略和Playwright使用
- 📄 **[性能测试指南](./04-performance-testing.md)**: 应用性能测试和监控
- 📄 **[测试工具详解](../reference/development-tools/01-testing-tools.md)**: 测试工具深度指南

### 参考章节
- 📖 **[React基础知识](../reference/language-concepts/01-react-syntax-cheatsheet.md)**: React组件开发基础
- 📖 **[状态管理](../reference/framework-patterns/05-state-management-patterns.md)**: React状态管理模式
- 📖 **[企业落地项目](../projects/01-corporate-landing.md)**: 实际项目中的测试实践
- 📖 **[电商平台项目](../projects/02-ecommerce-store.md)**: 复杂应用的测试策略

## 📝 总结

### 核心要点回顾

1. **测试理念**: React Testing Library强调测试用户行为而非实现细节
2. **工具选择**: Vitest + RTL + MSW构成现代React测试栈
3. **测试策略**: 合理组合单元测试、集成测试和E2E测试
4. **异步处理**: 掌握异步组件和API调用的测试方法
5. **Mock策略**: 合理使用Mock隔离依赖，确保测试可靠性
6. **质量保证**: 通过覆盖率、CI/CD和质量门禁确保测试质量

### 学习成果检查

- [ ] 是否理解了React Testing Library的核心概念？
- [ ] 是否能够编写组件渲染和交互测试？
- [ ] 是否掌握了异步组件测试方法？
- [ ] 是否能够处理复杂的测试场景（Context、Hook等）？
- [ ] 是否了解测试工具的配置和优化？
- [ ] 是否能够设计合理的测试策略？

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
- **React Testing Library**: [官方文档](https://testing-library.com/docs/react-testing-library/intro/) - 权威指南和API参考
- **Vitest**: [官方文档](https://vitest.dev/) - 现代测试框架完整指南
- **MSW**: [官方文档](https://mswjs.io/) - API Mock工具详细说明

### 推荐资源
- **测试最佳实践**: [Kent C. Dodds的博客](https://kentcdodds.com/blog/common-mistakes-with-react-testing-library) - 测试专家的建议
- **React测试模式**: [TestingJavaScript.com](https://testingjavascript.com/) - 系统性测试课程
- **组件测试策略**: [Component Testing Guide](https://robinwieruch.de/react-testing-library/) - 实用测试指南

### 工具和插件
- **VS Code扩展**: [Testing Library Extension](https://marketplace.visualstudio.com/items?itemName=ms-playwright.playwright) - 提升测试开发效率
- **Chrome DevTools**: [React Developer Tools](https://chrome.google.com/webstore/detail/react-developer-tools/) - 调试React组件
- **覆盖率工具**: [Istanbul/NYC](https://istanbul.js.org/) - 代码覆盖率分析

---

**文档状态**: ✅ 已完成
**最后更新**: 2026年9月
**版本**: v1.0.0