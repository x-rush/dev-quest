# 单元测试指南 (Unit Testing Guide)

> **PHP开发者视角**: 从PHPUnit到Vitest的转变，了解现代前端测试工具和最佳实践。

## 单元测试基础

### 什么是单元测试

单元测试是针对程序中最小可测试单元（如函数、方法、类）进行的测试。在Next.js中，单元测试主要用于测试：

- 工具函数（Utility Functions）
- React组件的渲染逻辑
- 自定义Hooks
- 业务逻辑函数
- 数据验证函数

### 为什么需要单元测试

1. **代码质量保证**: 确保代码按照预期工作
2. **重构安全性**: 在重构时提供安全网
3. **文档作用**: 测试用例作为代码的使用示例
4. **快速反馈**: 开发过程中快速发现问题
5. **维护成本降低**: 减少回归bug

## 测试工具栈

### 1. Vitest - 现代测试框架

```bash
# 安装Vitest
npm install -D vitest @vitest/ui jsdom @vitest/coverage-v8

# 配置测试脚本
{
  "scripts": {
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:coverage": "vitest --coverage"
  }
}
```

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
    setupFiles: "./src/test/setup.ts",
  },
  resolve: {
    alias: {
      "@": path.resolve(__dirname, "./src"),
    },
  },
})
```

### 2. Testing Library - React测试工具

```bash
npm install -D @testing-library/react @testing-library/jest-dom @testing-library/user-event
```

```typescript
// src/test/setup.ts
import "@testing-library/jest-dom"
import { vi } from "vitest"

// 模拟next/router
vi.mock("next/router", () => ({
  useRouter() {
    return {
      route: "/",
      pathname: "/",
      query: {},
      asPath: "/",
      push: vi.fn(),
      pop: vi.fn(),
      reload: vi.fn(),
      back: vi.fn(),
      prefetch: vi.fn().mockResolvedValue(undefined),
      beforePopState: vi.fn(),
      events: {
        on: vi.fn(),
        off: vi.fn(),
        emit: vi.fn(),
      },
      isFallback: false,
    }
  },
}))

// 模拟next/navigation
vi.mock("next/navigation", () => ({
  useRouter() {
    return {
      push: vi.fn(),
      replace: vi.fn(),
      back: vi.fn(),
      forward: vi.fn(),
      refresh: vi.fn(),
    }
  },
  useSearchParams() {
    return new URLSearchParams()
  },
  usePathname() {
    return "/"
  },
}))
```

## 测试工具函数

### 1. 工具函数测试

```typescript
// src/lib/utils/date.ts
export function formatDate(date: Date | string): string {
  const d = new Date(date)
  return d.toLocaleDateString("zh-CN", {
    year: "numeric",
    month: "long",
    day: "numeric",
  })
}

export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text
  return text.slice(0, maxLength) + "..."
}

export function generateSlug(text: string): string {
  return text
    .toLowerCase()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-")
    .trim()
}
```

```typescript
// __tests__/utils/date.test.ts
import { formatDate, isValidEmail, truncateText, generateSlug } from "@/lib/utils/date"

describe("Date Utils", () => {
  describe("formatDate", () => {
    it("应该正确格式化日期", () => {
      const date = new Date("2024-01-15")
      const result = formatDate(date)
      expect(result).toBe("2024年1月15日")
    })

    it("应该能处理字符串日期", () => {
      const result = formatDate("2024-01-15")
      expect(result).toBe("2024年1月15日")
    })

    it("应该能处理当前日期", () => {
      const today = new Date()
      const result = formatDate(today)
      expect(result).toContain(today.getFullYear().toString())
    })
  })

  describe("isValidEmail", () => {
    it("应该验证有效的邮箱地址", () => {
      expect(isValidEmail("test@example.com")).toBe(true)
      expect(isValidEmail("user.name@domain.co.uk")).toBe(true)
      expect(isValidEmail("user+tag@example.org")).toBe(true)
    })

    it("应该拒绝无效的邮箱地址", () => {
      expect(isValidEmail("invalid-email")).toBe(false)
      expect(isValidEmail("@example.com")).toBe(false)
      expect(isValidEmail("test@")).toBe(false)
      expect(isValidEmail("")).toBe(false)
    })
  })

  describe("truncateText", () => {
    it("不应该截断短文本", () => {
      const text = "短文本"
      const result = truncateText(text, 10)
      expect(result).toBe(text)
    })

    it("应该正确截断长文本", () => {
      const text = "这是一个很长的文本，需要被截断"
      const result = truncateText(text, 10)
      expect(result).toBe("这是一个很长的...")
      expect(result.length).toBeLessThanOrEqual(13) // 10 + "..."
    })
  })

  describe("generateSlug", () => {
    it("应该生成正确的slug", () => {
      expect(generateSlug("Hello World")).toBe("hello-world")
      expect(generateSlug("React & Next.js")).toBe("react-nextjs")
      expect(generateSlug("  Spaces  ")).toBe("spaces")
      expect(generateSlug("Multiple---Dashes")).toBe("multiple-dashes")
    })
  })
})
```

### 2. 数据验证函数测试

```typescript
// src/lib/validation/schemas.ts
import { z } from "zod"

export const userSchema = z.object({
  name: z.string().min(2, "姓名至少需要2个字符").max(50, "姓名不能超过50个字符"),
  email: z.string().email("请输入有效的邮箱地址"),
  age: z.number().min(18, "年龄必须大于18岁").max(120, "年龄不能超过120岁"),
  bio: z.string().max(500, "个人简介不能超过500字符").optional(),
  website: z.string().url("请输入有效的网址").optional().or(z.literal("")),
})

export const postSchema = z.object({
  title: z.string().min(1, "标题不能为空").max(100, "标题不能超过100字符"),
  content: z.string().min(1, "内容不能为空").max(10000, "内容不能超过10000字符"),
  tags: z.array(z.string()).max(5, "最多添加5个标签"),
  published: z.boolean().default(false),
})

export type UserInput = z.infer<typeof userSchema>
export type PostInput = z.infer<typeof postSchema>
```

```typescript
// __tests__/validation/schemas.test.ts
import { userSchema, postSchema } from "@/lib/validation/schemas"

describe("Validation Schemas", () => {
  describe("userSchema", () => {
    it("应该验证有效的用户数据", () => {
      const validUser = {
        name: "张三",
        email: "zhangsan@example.com",
        age: 25,
        bio: "前端开发者",
        website: "https://example.com",
      }

      const result = userSchema.safeParse(validUser)
      expect(result.success).toBe(true)
    })

    it("应该拒绝无效的邮箱", () => {
      const invalidUser = {
        name: "张三",
        email: "invalid-email",
        age: 25,
      }

      const result = userSchema.safeParse(invalidUser)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0].message).toContain("邮箱")
      }
    })

    it("应该验证年龄范围", () => {
      const youngUser = {
        name: "小明",
        email: "xiaoming@example.com",
        age: 15, // 太年轻
      }

      const result = userSchema.safeParse(youngUser)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0].message).toContain("年龄")
      }
    })

    it("应该允许可选字段为空", () => {
      const minimalUser = {
        name: "李四",
        email: "lisi@example.com",
        age: 30,
      }

      const result = userSchema.safeParse(minimalUser)
      expect(result.success).toBe(true)
    })
  })

  describe("postSchema", () => {
    it("应该验证有效的帖子数据", () => {
      const validPost = {
        title: "我的第一篇博客",
        content: "这是博客内容...",
        tags: ["React", "Next.js"],
        published: true,
      }

      const result = postSchema.safeParse(validPost)
      expect(result.success).toBe(true)
    })

    it("应该拒绝空标题", () => {
      const invalidPost = {
        title: "",
        content: "内容...",
        tags: [],
      }

      const result = postSchema.safeParse(invalidPost)
      expect(result.success).toBe(false)
    })

    it("应该限制标签数量", () => {
      const postWithManyTags = {
        title: "标签测试",
        content: "内容...",
        tags: ["标签1", "标签2", "标签3", "标签4", "标签5", "标签6"], // 6个标签
      }

      const result = postSchema.safeParse(postWithManyTags)
      expect(result.success).toBe(false)
      if (!result.success) {
        expect(result.error.errors[0].message).toContain("标签")
      }
    })
  })
})
```

## React组件测试

### 1. 基础组件测试

```typescript
// src/components/ui/button.tsx
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium ring-offset-background transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  asChild?: boolean
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, asChild = false, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

```typescript
// __tests__/components/ui/button.test.tsx
import { render, screen } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { Button } from "@/components/ui/button"

describe("Button Component", () => {
  it("应该渲染默认样式的按钮", () => {
    render(<Button>点击我</Button>)
    const button = screen.getByRole("button", { name: /点击我/i })
    expect(button).toBeInTheDocument()
    expect(button).toHaveClass("bg-primary")
  })

  it("应该支持不同的变体", () => {
    const { rerender } = render(<Button variant="destructive">删除</Button>)
    let button = screen.getByRole("button", { name: /删除/i })
    expect(button).toHaveClass("bg-destructive")

    rerender(<Button variant="outline">边框</Button>)
    button = screen.getByRole("button", { name: /边框/i })
    expect(button).toHaveClass("border")
  })

  it("应该支持不同的尺寸", () => {
    const { rerender } = render(<Button size="sm">小按钮</Button>)
    let button = screen.getByRole("button", { name: /小按钮/i })
    expect(button).toHaveClass("h-9")

    rerender(<Button size="lg">大按钮</Button>)
    button = screen.getByRole("button", { name: /大按钮/i })
    expect(button).toHaveClass("h-11")
  })

  it("应该正确处理点击事件", async () => {
    const handleClick = vi.fn()
    const user = userEvent.setup()

    render(<Button onClick={handleClick}>点击我</Button>)
    const button = screen.getByRole("button", { name: /点击我/i })

    await user.click(button)
    expect(handleClick).toHaveBeenCalledTimes(1)
  })

  it("应该支持禁用状态", () => {
    render(<Button disabled>禁用按钮</Button>)
    const button = screen.getByRole("button", { name: /禁用按钮/i })
    expect(button).toBeDisabled()
    expect(button).toHaveClass("disabled:opacity-50")
  })

  it("应该支持自定义className", () => {
    render(<Button className="custom-class">自定义</Button>)
    const button = screen.getByRole("button", { name: /自定义/i })
    expect(button).toHaveClass("custom-class")
  })

  it("应该正确传递额外的props", () => {
    render(<Button data-testid="custom-button">测试</Button>)
    const button = screen.getByTestId("custom-button")
    expect(button).toBeInTheDocument()
  })
})
```

### 2. 复杂组件测试

```typescript
// src/components/forms/contact-form.tsx
"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "react-hot-toast"

const contactSchema = z.object({
  name: z.string().min(2, "姓名至少需要2个字符"),
  email: z.string().email("请输入有效的邮箱地址"),
  subject: z.string().min(5, "主题至少需要5个字符"),
  message: z.string().min(10, "消息至少需要10个字符"),
})

type ContactFormData = z.infer<typeof contactSchema>

interface ContactFormProps {
  onSubmit: (data: ContactFormData) => Promise<void>
}

export function ContactForm({ onSubmit }: ContactFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
    defaultValues: {
      name: "",
      email: "",
      subject: "",
      message: "",
    },
  })

  const handleSubmit = async (data: ContactFormData) => {
    setIsSubmitting(true)
    try {
      await onSubmit(data)
      form.reset()
      toast.success("消息已发送！")
    } catch (error) {
      toast.error("发送失败，请重试")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
        <FormField
          control={form.control}
          name="name"
          render={({ field }) => (
            <FormItem>
              <FormLabel>姓名</FormLabel>
              <FormControl>
                <Input placeholder="您的姓名" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel>邮箱</FormLabel>
              <FormControl>
                <Input type="email" placeholder="your@email.com" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="subject"
          render={({ field }) => (
            <FormItem>
              <FormLabel>主题</FormLabel>
              <FormControl>
                <Input placeholder="消息主题" {...field} />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <FormField
          control={form.control}
          name="message"
          render={({ field }) => (
            <FormItem>
              <FormLabel>消息</FormLabel>
              <FormControl>
                <Textarea
                  placeholder="您的消息..."
                  className="min-h-[100px]"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        <Button type="submit" disabled={isSubmitting} className="w-full">
          {isSubmitting ? "发送中..." : "发送消息"}
        </Button>
      </form>
    </Form>
  )
}
```

```typescript
// __tests__/components/forms/contact-form.test.tsx
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { ContactForm } from "@/components/forms/contact-form"
import { toast } from "react-hot-toast"

// 模拟toast
vi.mock("react-hot-toast", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

describe("ContactForm Component", () => {
  const mockOnSubmit = vi.fn()

  beforeEach(() => {
    mockOnSubmit.mockClear()
    vi.clearAllMocks()
  })

  it("应该渲染所有表单字段", () => {
    render(<ContactForm onSubmit={mockOnSubmit} />)

    expect(screen.getByLabelText(/姓名/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/邮箱/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/主题/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/消息/i)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /发送消息/i })).toBeInTheDocument()
  })

  it("应该显示验证错误信息", async () => {
    const user = userEvent.setup()
    render(<ContactForm onSubmit={mockOnSubmit} />)

    // 尝试提交空表单
    await user.click(screen.getByRole("button", { name: /发送消息/i }))

    // 等待验证错误显示
    await waitFor(() => {
      expect(screen.getByText("姓名至少需要2个字符")).toBeInTheDocument()
      expect(screen.getByText("请输入有效的邮箱地址")).toBeInTheDocument()
      expect(screen.getByText("主题至少需要5个字符")).toBeInTheDocument()
      expect(screen.getByText("消息至少需要10个字符")).toBeInTheDocument()
    })

    // 不应该调用onSubmit
    expect(mockOnSubmit).not.toHaveBeenCalled()
  })

  it("应该在输入正确数据时成功提交", async () => {
    const user = userEvent.setup()
    const mockPromise = Promise.resolve()
    mockOnSubmit.mockReturnValue(mockPromise)

    render(<ContactForm onSubmit={mockOnSubmit} />)

    // 填写表单
    await user.type(screen.getByLabelText(/姓名/i), "张三")
    await user.type(screen.getByLabelText(/邮箱/i), "zhangsan@example.com")
    await user.type(screen.getByLabelText(/主题/i), "咨询产品")
    await user.type(screen.getByLabelText(/消息/i), "我想了解更多关于您的产品信息")

    // 提交表单
    await user.click(screen.getByRole("button", { name: /发送消息/i }))

    // 等待提交
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith({
        name: "张三",
        email: "zhangsan@example.com",
        subject: "咨询产品",
        message: "我想了解更多关于您的产品信息",
      })
    })

    // 显示成功消息
    await waitFor(() => {
      expect(toast.success).toHaveBeenCalledWith("消息已发送！")
    })
  })

  it("应该处理提交错误", async () => {
    const user = userEvent.setup()
    const mockError = new Error("提交失败")
    mockOnSubmit.mockRejectedValue(mockError)

    render(<ContactForm onSubmit={mockOnSubmit} />)

    // 填写表单
    await user.type(screen.getByLabelText(/姓名/i), "张三")
    await user.type(screen.getByLabelText(/邮箱/i), "zhangsan@example.com")
    await user.type(screen.getByLabelText(/主题/i), "咨询产品")
    await user.type(screen.getByLabelText(/消息/i), "我想了解更多关于您的产品信息")

    // 提交表单
    await user.click(screen.getByRole("button", { name: /发送消息/i }))

    // 显示错误消息
    await waitFor(() => {
      expect(toast.error).toHaveBeenCalledWith("发送失败，请重试")
    })
  })

  it("应该在提交时禁用按钮", async () => {
    const user = userEvent.setup()
    const mockPromise = new Promise(() => {}) // 永不resolve的promise
    mockOnSubmit.mockReturnValue(mockPromise)

    render(<ContactForm onSubmit={mockOnSubmit} />)

    // 填写表单
    await user.type(screen.getByLabelText(/姓名/i), "张三")
    await user.type(screen.getByLabelText(/邮箱/i), "zhangsan@example.com")
    await user.type(screen.getByLabelText(/主题/i), "咨询产品")
    await user.type(screen.getByLabelText(/消息/i), "我想了解更多关于您的产品信息")

    // 提交表单
    await user.click(screen.getByRole("button", { name: /发送消息/i }))

    // 按钮应该被禁用
    expect(screen.getByRole("button", { name: /发送中/i })).toBeDisabled()
  })

  it("应该在成功提交后重置表单", async () => {
    const user = userEvent.setup()
    const mockPromise = Promise.resolve()
    mockOnSubmit.mockReturnValue(mockPromise)

    render(<ContactForm onSubmit={mockOnSubmit} />)

    // 填写表单
    const nameInput = screen.getByLabelText(/姓名/i)
    await user.type(nameInput, "张三")

    // 提交表单
    await user.click(screen.getByRole("button", { name: /发送消息/i }))

    // 等待提交完成
    await waitFor(() => {
      expect(nameInput).toHaveValue("") // 表单应该被重置
    })
  })
})
```

## 自定义Hooks测试

### 1. 状态管理Hooks

```typescript
// src/hooks/use-local-storage.ts
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
// __tests__/hooks/use-local-storage.test.tsx
import { renderHook, act } from "@testing-library/react"
import { useLocalStorage } from "@/hooks/use-local-storage"

describe("useLocalStorage", () => {
  beforeEach(() => {
    // 清理localStorage
    localStorage.clear()

    // 模拟window对象
    Object.defineProperty(window, "localStorage", {
      value: {
        getItem: vi.fn(),
        setItem: vi.fn(),
        removeItem: vi.fn(),
        clear: vi.fn(),
      },
      writable: true,
    })
  })

  it("应该返回初始值当localStorage为空时", () => {
    const { result } = renderHook(() => useLocalStorage("test-key", "initial-value"))

    expect(result.current[0]).toBe("initial-value")
  })

  it("应该从localStorage读取值", () => {
    const storedValue = JSON.stringify("stored-value")
    vi.spyOn(localStorage, "getItem").mockReturnValue(storedValue)

    const { result } = renderHook(() => useLocalStorage("test-key", "initial-value"))

    expect(result.current[0]).toBe("stored-value")
    expect(localStorage.getItem).toHaveBeenCalledWith("test-key")
  })

  it("应该设置值到localStorage", () => {
    const { result } = renderHook(() => useLocalStorage("test-key", "initial-value"))
    const [, setValue] = result.current

    act(() => {
      setValue("new-value")
    })

    expect(result.current[0]).toBe("new-value")
    expect(localStorage.setItem).toHaveBeenCalledWith("test-key", JSON.stringify("new-value"))
  })

  it("应该支持函数式更新", () => {
    const { result } = renderHook(() => useLocalStorage("counter", 0))
    const [, setCounter] = result.current

    act(() => {
      setCounter(prev => prev + 1)
    })

    expect(result.current[0]).toBe(1)
    expect(localStorage.setItem).toHaveBeenCalledWith("counter", JSON.stringify(1))
  })

  it("应该处理localStorage错误", () => {
    const consoleSpy = vi.spyOn(console, "error").mockImplementation(() => {})

    vi.spyOn(localStorage, "getItem").mockImplementation(() => {
      throw new Error("Storage error")
    })

    const { result } = renderHook(() => useLocalStorage("test-key", "fallback-value"))

    expect(result.current[0]).toBe("fallback-value")
    expect(consoleSpy).toHaveBeenCalled()

    consoleSpy.mockRestore()
  })

  it("应该在服务器端返回初始值", () => {
    // 模拟服务器端环境
    const originalWindow = global.window
    delete (global as any).window

    const { result } = renderHook(() => useLocalStorage("test-key", "server-value"))

    expect(result.current[0]).toBe("server-value")

    // 恢复window对象
    global.window = originalWindow
  })
})
```

### 2. 数据获取Hooks

```typescript
// src/hooks/use-debounce.ts
import { useState, useEffect } from "react"

export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value)

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value)
    }, delay)

    return () => {
      clearTimeout(handler)
    }
  }, [value, delay])

  return debouncedValue
}
```

```typescript
// __tests__/hooks/use-debounce.test.tsx
import { renderHook, act } from "@testing-library/react"
import { useDebounce } from "@/hooks/use-debounce"
import { vi, beforeEach, afterEach } from "vitest"

describe("useDebounce", () => {
  beforeEach(() => {
    vi.useFakeTimers()
  })

  afterEach(() => {
    vi.useRealTimers()
  })

  it("应该立即返回初始值", () => {
    const { result } = renderHook(() => useDebounce("test", 500))
    expect(result.current).toBe("test")
  })

  it("应该在延迟后更新值", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "initial", delay: 500 } }
    )

    // 更新值
    rerender({ value: "updated", delay: 500 })

    // 延迟前应该还是旧值
    expect(result.current).toBe("initial")

    // 快进时间
    act(() => {
      vi.advanceTimersByTime(500)
    })

    // 延迟后应该更新为新值
    expect(result.current).toBe("updated")
  })

  it("应该在多次更新时只使用最后一次值", () => {
    const { result, rerender } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "initial", delay: 500 } }
    )

    // 多次快速更新
    rerender({ value: "update1", delay: 500 })
    rerender({ value: "update2", delay: 500 })
    rerender({ value: "update3", delay: 500 })

    // 快进时间
    act(() => {
      vi.advanceTimersByTime(500)
    })

    // 应该只有最后一次更新生效
    expect(result.current).toBe("update3")
  })

  it("应该在组件卸载时清除定时器", () => {
    const { result, rerender, unmount } = renderHook(
      ({ value, delay }) => useDebounce(value, delay),
      { initialProps: { value: "initial", delay: 500 } }
    )

    const clearTimeoutSpy = vi.spyOn(global, "clearTimeout")

    // 更新值
    rerender({ value: "updated", delay: 500 })

    // 卸载组件
    unmount()

    // 应该清除定时器
    expect(clearTimeoutSpy).toHaveBeenCalled()

    clearTimeoutSpy.mockRestore()
  })
})
```

## 异步函数测试

### 1. API函数测试

```typescript
// src/lib/api/user.ts
import { prisma } from "@/lib/prisma"
import { userSchema } from "@/lib/validation/schemas"

export async function createUser(data: {
  name: string
  email: string
  age: number
  bio?: string
}) {
  const validatedData = userSchema.parse(data)

  const user = await prisma.user.create({
    data: {
      name: validatedData.name,
      email: validatedData.email,
      age: validatedData.age,
      bio: validatedData.bio,
    },
  })

  return user
}

export async function getUserById(id: string) {
  const user = await prisma.user.findUnique({
    where: { id },
    select: {
      id: true,
      name: true,
      email: true,
      age: true,
      bio: true,
      createdAt: true,
      updatedAt: true,
    },
  })

  if (!user) {
    throw new Error("用户不存在")
  }

  return user
}

export async function updateUser(id: string, data: {
  name?: string
  email?: string
  age?: number
  bio?: string
}) {
  const existingUser = await prisma.user.findUnique({
    where: { id },
  })

  if (!existingUser) {
    throw new Error("用户不存在")
  }

  const updatedUser = await prisma.user.update({
    where: { id },
    data,
  })

  return updatedUser
}

export async function deleteUser(id: string) {
  const existingUser = await prisma.user.findUnique({
    where: { id },
  })

  if (!existingUser) {
    throw new Error("用户不存在")
  }

  await prisma.user.delete({
    where: { id },
  })

  return { success: true }
}
```

```typescript
// __tests__/lib/api/user.test.ts
import { createUser, getUserById, updateUser, deleteUser } from "@/lib/api/user"
import { prisma } from "@/lib/prisma"

// 模拟Prisma
vi.mock("@/lib/prisma", () => ({
  prisma: {
    user: {
      create: vi.fn(),
      findUnique: vi.fn(),
      update: vi.fn(),
      delete: vi.fn(),
    },
  },
}))

describe("User API", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("createUser", () => {
    it("应该成功创建用户", async () => {
      const mockUser = {
        id: "1",
        name: "张三",
        email: "zhangsan@example.com",
        age: 25,
        bio: "测试用户",
        createdAt: new Date(),
        updatedAt: new Date(),
      }

      vi.mocked(prisma.user.create).mockResolvedValue(mockUser)

      const result = await createUser({
        name: "张三",
        email: "zhangsan@example.com",
        age: 25,
        bio: "测试用户",
      })

      expect(result).toEqual(mockUser)
      expect(prisma.user.create).toHaveBeenCalledWith({
        data: {
          name: "张三",
          email: "zhangsan@example.com",
          age: 25,
          bio: "测试用户",
        },
      })
    })

    it("应该验证输入数据", async () => {
      const invalidData = {
        name: "", // 无效的姓名
        email: "invalid-email", // 无效的邮箱
        age: 15, // 无效的年龄
      }

      await expect(createUser(invalidData as any)).rejects.toThrow()
      expect(prisma.user.create).not.toHaveBeenCalled()
    })
  })

  describe("getUserById", () => {
    it("应该返回存在的用户", async () => {
      const mockUser = {
        id: "1",
        name: "张三",
        email: "zhangsan@example.com",
        age: 25,
        bio: "测试用户",
        createdAt: new Date(),
        updatedAt: new Date(),
      }

      vi.mocked(prisma.user.findUnique).mockResolvedValue(mockUser)

      const result = await getUserById("1")

      expect(result).toEqual(mockUser)
      expect(prisma.user.findUnique).toHaveBeenCalledWith({
        where: { id: "1" },
        select: {
          id: true,
          name: true,
          email: true,
          age: true,
          bio: true,
          createdAt: true,
          updatedAt: true,
        },
      })
    })

    it("应该为不存在的用户抛出错误", async () => {
      vi.mocked(prisma.user.findUnique).mockResolvedValue(null)

      await expect(getUserById("non-existent")).rejects.toThrow("用户不存在")
    })
  })

  describe("updateUser", () => {
    it("应该成功更新用户", async () => {
      const existingUser = {
        id: "1",
        name: "张三",
        email: "zhangsan@example.com",
        age: 25,
        bio: "测试用户",
      }

      const updatedUser = {
        ...existingUser,
        name: "李四",
        age: 26,
      }

      vi.mocked(prisma.user.findUnique).mockResolvedValue(existingUser)
      vi.mocked(prisma.user.update).mockResolvedValue(updatedUser)

      const result = await updateUser("1", {
        name: "李四",
        age: 26,
      })

      expect(result).toEqual(updatedUser)
      expect(prisma.user.update).toHaveBeenCalledWith({
        where: { id: "1" },
        data: {
          name: "李四",
          age: 26,
        },
      })
    })

    it("应该为不存在的用户抛出错误", async () => {
      vi.mocked(prisma.user.findUnique).mockResolvedValue(null)

      await expect(updateUser("non-existent", { name: "新名字" })).rejects.toThrow("用户不存在")
    })
  })

  describe("deleteUser", () => {
    it("应该成功删除用户", async () => {
      const existingUser = {
        id: "1",
        name: "张三",
        email: "zhangsan@example.com",
        age: 25,
      }

      vi.mocked(prisma.user.findUnique).mockResolvedValue(existingUser)
      vi.mocked(prisma.user.delete).mockResolvedValue(existingUser)

      const result = await deleteUser("1")

      expect(result).toEqual({ success: true })
      expect(prisma.user.delete).toHaveBeenCalledWith({
        where: { id: "1" },
      })
    })

    it("应该为不存在的用户抛出错误", async () => {
      vi.mocked(prisma.user.findUnique).mockResolvedValue(null)

      await expect(deleteUser("non-existent")).rejects.toThrow("用户不存在")
    })
  })
})
```

## 测试最佳实践

### 1. 测试组织结构

```
__tests__/
├── components/
│   ├── ui/
│   │   ├── button.test.tsx
│   │   ├── input.test.tsx
│   │   └── ...
│   ├── forms/
│   │   ├── contact-form.test.tsx
│   │   └── ...
│   └── layout/
│       ├── header.test.tsx
│       └── ...
├── hooks/
│   ├── use-local-storage.test.tsx
│   ├── use-debounce.test.tsx
│   └── ...
├── lib/
│   ├── utils/
│   │   ├── date.test.ts
│   │   └── ...
│   ├── api/
│   │   ├── user.test.ts
│   │   └── ...
│   └── validation/
│       └── schemas.test.ts
└── e2e/
    └── ...
```

### 2. 测试命名规范

```typescript
// 好的测试命名
describe("Button Component", () => {
  it("应该渲染默认样式的按钮", () => {
    // 测试代码
  })

  it("应该在点击时触发onClick事件", () => {
    // 测试代码
  })

  it("应该正确处理禁用状态", () => {
    // 测试代码
  })
})

// 不好的测试命名
describe("Button", () => {
  it("test button render", () => {
    // 测试代码
  })

  it("click works", () => {
    // 测试代码
  })
})
```

### 3. 测试覆盖率配置

```typescript
// vitest.config.ts
import { defineConfig } from "vitest/config"

export default defineConfig({
  test: {
    coverage: {
      provider: "v8",
      reporter: ["text", "json", "html"],
      include: ["src/**/*"],
      exclude: [
        "src/**/*.d.ts",
        "src/**/*.stories.tsx",
        "src/test/**/*",
      ],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
  },
})
```

### 4. 测试工具函数

```typescript
// src/test/utils.ts
import { render, RenderOptions } from "@testing-library/react"
import { ReactElement } from "react"

// 自定义render函数
export function renderWithProviders(
  ui: ReactElement,
  options?: Omit<RenderOptions, "wrapper">
) {
  return render(ui, options)
}

// 创建模拟数据
export function createMockUser(overrides?: Partial<User>) {
  return {
    id: "1",
    name: "测试用户",
    email: "test@example.com",
    age: 25,
    bio: "这是一个测试用户",
    createdAt: new Date(),
    updatedAt: new Date(),
    ...overrides,
  }
}

// 等待异步操作
export async function waitForLoadingToFinish() {
  return await new Promise(resolve => setTimeout(resolve, 0))
}
```

## 总结

通过本指南，我们学习了Next.js项目中单元测试的各个方面：

### 核心概念
- 单元测试的基本概念和重要性
- 现代测试工具栈的选择和配置
- 测试环境的搭建和最佳实践

### 测试类型
- 工具函数的单元测试
- React组件的渲染和交互测试
- 自定义Hooks的状态管理测试
- 异步函数和API调用的测试

### 实践技巧
- 测试组织和命名规范
- Mock和Stub的使用
- 异步测试的处理
- 测试覆盖率的配置

### 从PHP开发者角度
- 从PHPUnit到Vitest的转变
- 前端测试的特殊考虑
- 组件测试与单元测试的区别

## 🔗 相关资源链接

### 官方资源
- [Vitest 官方文档](https://vitest.dev/)
- [Testing Library 官方文档](https://testing-library.com/)
- [React Testing Library](https://testing-library.com/docs/react-testing-library/intro/)
- [Zod 官方文档](https://zod.dev/)

### 技术文章
- [现代前端测试最佳实践](https://kentcdodds.com/blog/common-testing-mistakes)
- [Vitest vs Jest 对比](https://vitest.dev/guide/comparisons.html)
- [React组件测试策略](https://testing-library.com/docs/react-testing-library/example-intro)
- [Mock策略和最佳实践](https://kentcdodds.com/blog/the-merits-of-mocking)

### 工具和资源
- [Vitest UI](https://vitest.dev/guide/ui.html)
- [React Hook Form Testing](https://react-hook-form.com/advanced-usage#testing)
- [MSW (Mock Service Worker)](https://mswjs.io/)

## 📚 模块内相关文档

### 同模块相关文档
- [端到端测试指南](./03-e2e-testing.md) - 学习完整的E2E测试策略和实践

### 相关知识模块
- [框架相关模块](../frameworks/01-nextjs-15-complete.md) - Next.js 15的架构为测试提供的基础
- [框架相关模块](../frameworks/02-react-19-integration.md) - React 19组件的测试策略
- [框架相关模块](../frameworks/03-full-stack-patterns.md) - 全栈应用的API测试和集成测试

### 基础前置知识
- [JavaScript 测试基础](../../../00-javascript-foundation/basics/03-javascript-testing.md) - JavaScript测试的基础概念
- [TypeScript 类型检查](../../../00-javascript-foundation/advanced/01-typescript-type-system.md) - TypeScript在测试中的应用
- [React Hooks 完全指南](../../../01-react-foundation/advanced/03-react-hooks-deep-dive.md) - React Hooks的测试原理

---

## ✨ 总结

### 核心技术要点
1. **现代测试框架**: Vitest的配置和使用，相比传统测试工具的优势
2. **组件测试策略**: React Testing Library的测试哲学和最佳实践
3. **Hook测试模式**: 自定义Hook的测试技巧和模拟策略
4. **异步测试处理**: Promise、定时器和API调用的测试方法
5. **Mock和Stub**: 有效的模拟策略和依赖注入技术

### 学习成果自检
- [ ] 理解现代前端测试的核心理念和测试金字塔
- [ ] 掌握Vitest和React Testing Library的配置和使用
- [ ] 能够编写高质量的React组件单元测试
- [ ] 熟练测试自定义Hooks和异步函数
- [ ] 能够制定合理的测试策略和覆盖率目标

---

## 🤝 贡献与反馈

### 贡献指南
欢迎提交Issue和Pull Request来改进本模块内容！请遵循以下步骤：

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/amazing-feature`)
3. 提交变更 (`git commit -m 'Add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

### 反馈渠道
- **问题反馈**: [GitHub Issues](https://github.com/your-username/dev-quest/issues)
- **内容建议**: [Discussion板块](https://github.com/your-username/dev-quest/discussions)
- **技术交流**: 欢迎提交PR或Issue参与讨论

### 贡献者
- Dev Quest Team - 核心内容开发
- 社区贡献者 - 内容完善和纠错

---

**📜 文档版本**: v1.0.0
**📅 最后更新**: 2025年10月
**🏷️ 标签**: `#unit-testing` `#vitest` `#testing-library` `#react-testing` `#mocking`
**⭐ 推荐指数**: ⭐⭐⭐⭐⭐

**💡 提示**: 本模块专注于现代前端单元测试实践，建议结合实际项目进行练习。

**🎯 学习建议**:
- 建议学习周期: 1-2周
- 理论与实践时间比例: 4:6
- 重点掌握组件测试和Hook测试
- 从简单工具函数开始，逐步过渡到复杂组件测试