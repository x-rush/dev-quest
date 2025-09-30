# 05 - UI组件库与设计系统

## 目录

1. [概述](#概述)
2. [流行UI库对比](#流行ui库对比)
3. [Shadcn/ui深度使用](#shadcnui深度使用)
4. [自定义组件库](#自定义组件库)
5. [设计系统构建](#设计系统构建)
6. [无障碍设计](#无障碍设计)
7. [性能优化](#性能优化)
8. [最佳实践](#最佳实践)
9. [项目实战](#项目实战)
10. [总结](#总结)

## 概述

Next.js 15与现代化的UI组件库完美结合，能够快速构建美观、响应式且无障碍的用户界面。

### 与PHP开发的对比

**传统PHP开发：**
- 手动编写HTML和CSS
- 重复的UI代码
- 缺乏设计一致性
- 响应式设计需要额外工作

**Next.js + UI库：**
- 组件化开发
- 可复用的UI组件
- 统一的设计语言
- 内置响应式和无障碍支持

### Next.js 15 UI库优势

- **Server Components**: 优化首屏加载性能
- **TypeScript支持**: 类型安全的组件开发
- **CSS-in-JS或Tailwind**: 灵活的样式方案
- **React 19特性**: 并发渲染和Actions支持

## 流行UI库对比

### 主要UI库特点对比

```typescript
// 常用UI库配置示例

// 1. MUI (Material-UI)
// 安装
npm install @mui/material @emotion/react @emotion/styled
npm install @mui/icons-material

// 使用示例
import { Button, TextField, Card } from '@mui/material'

function MUIExample() {
  return (
    <Card sx={{ p: 3 }}>
      <TextField label="Name" variant="outlined" fullWidth />
      <Button variant="contained" sx={{ mt: 2 }}>
        Submit
      </Button>
    </Card>
  )
}

// 2. Ant Design
// 安装
npm install antd
npm install @ant-design/icons

// 使用示例
import { Button, Input, Card } from 'antd'
import { UserOutlined } from '@ant-design/icons'

function AntdExample() {
  return (
    <Card title="Form" style={{ width: 300 }}>
      <Input placeholder="Name" prefix={<UserOutlined />} />
      <Button type="primary" style={{ marginTop: 16 }}>
        Submit
      </Button>
    </Card>
  )
}

// 3. Chakra UI
// 安装
npm install @chakra-ui/react @emotion/react @emotion/styled framer-motion

// 使用示例
import { Button, Input, Card, ChakraProvider } from '@chakra-ui/react'

function ChakraExample() {
  return (
    <Card p={6}>
      <Input placeholder="Name" mb={4} />
      <Button colorScheme="blue">Submit</Button>
    </Card>
  )
}

// 4. Shadcn/ui (推荐)
// 基于Radix UI + Tailwind CSS
// 配置见下一节
```

### 选择指南

| UI库 | 适用场景 | 优点 | 缺点 |
|------|----------|------|------|
| **Shadcn/ui** | 现代化应用 | 无样式、可定制、轻量 | 需要手动配置 |
| **MUI** | 企业级应用 | 组件丰富、文档完善 | 包体积较大 |
| **Ant Design** | 管理后台 | 设计统一、组件完整 | 定制性较差 |
| **Chakra UI** | 快速原型 | 开发效率高、无障碍好 | 性能开销较大 |

## Shadcn/ui深度使用

### 初始化配置

```bash
# 安装Shadcn/ui
npx shadcn-ui@latest init

# 选择配置
- Style: Default
- Base color: Slate
- CSS variable: true
- Tailwind CSS path: ./app/tailwind.config.ts
```

```typescript
// components.json 配置文件
{
  "$schema": "https://ui.shadcn.com/schema.json",
  "style": "default",
  "rsc": true,
  "tsx": true,
  "tailwind": {
    "config": "tailwind.config.ts",
    "css": "app/globals.css",
    "baseColor": "slate",
    "cssVariables": true,
    "prefix": ""
  },
  "aliases": {
    "components": "@/components",
    "utils": "@/lib/utils"
  }
}
```

```typescript
// app/globals.css - 全局样式
@tailwind base;
@tailwind components;
@tailwind utilities;

@layer base {
  :root {
    --background: 0 0% 100%;
    --foreground: 222.2 84% 4.9%;
    --card: 0 0% 100%;
    --card-foreground: 222.2 84% 4.9%;
    --popover: 0 0% 100%;
    --popover-foreground: 222.2 84% 4.9%;
    --primary: 222.2 47.4% 11.2%;
    --primary-foreground: 210 40% 98%;
    --secondary: 210 40% 96%;
    --secondary-foreground: 222.2 84% 4.9%;
    --muted: 210 40% 96%;
    --muted-foreground: 215.4 16.3% 46.9%;
    --accent: 210 40% 96%;
    --accent-foreground: 222.2 84% 4.9%;
    --destructive: 0 84.2% 60.2%;
    --destructive-foreground: 210 40% 98%;
    --border: 214.3 31.8% 91.4%;
    --input: 214.3 31.8% 91.4%;
    --ring: 222.2 84% 4.9%;
    --radius: 0.5rem;
  }

  .dark {
    --background: 222.2 84% 4.9%;
    --foreground: 210 40% 98%;
    --card: 222.2 84% 4.9%;
    --card-foreground: 210 40% 98%;
    --popover: 222.2 84% 4.9%;
    --popover-foreground: 210 40% 98%;
    --primary: 210 40% 98%;
    --primary-foreground: 222.2 47.4% 11.2%;
    --secondary: 217.2 32.6% 17.5%;
    --secondary-foreground: 210 40% 98%;
    --muted: 217.2 32.6% 17.5%;
    --muted-foreground: 215 20.2% 65.1%;
    --accent: 217.2 32.6% 17.5%;
    --accent-foreground: 210 40% 98%;
    --destructive: 0 62.8% 30.6%;
    --destructive-foreground: 210 40% 98%;
    --border: 217.2 32.6% 17.5%;
    --input: 217.2 32.6% 17.5%;
    --ring: 212.7 26.8% 83.9%;
  }
}

@layer base {
  * {
    @apply border-border;
  }
  body {
    @apply bg-background text-foreground;
  }
}
```

### 基础组件使用

```typescript
// 添加组件
npx shadcn-ui@latest add button card input label form

// 使用示例
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"

function LoginForm() {
  return (
    <div className="flex min-h-screen items-center justify-center">
      <Card className="w-full max-w-md">
        <CardHeader>
          <CardTitle>Login</CardTitle>
          <CardDescription>
            Enter your credentials to access your account
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="space-y-2">
            <Label htmlFor="email">Email</Label>
            <Input id="email" type="email" placeholder="m@example.com" />
          </div>
          <div className="space-y-2">
            <Label htmlFor="password">Password</Label>
            <Input id="password" type="password" />
          </div>
        </CardContent>
        <CardFooter>
          <Button className="w-full">Login</Button>
        </CardFooter>
      </Card>
    </div>
  )
}
```

### 高级组件组合

```typescript
// npx shadcn-ui@latest add dialog sheet toast dropdown-menu

// 复杂表单组件
"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormDescription, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Checkbox } from "@/components/ui/checkbox"
import { Textarea } from "@/components/ui/textarea"
import { toast } from "@/components/ui/use-toast"

const profileFormSchema = z.object({
  username: z.string().min(2, {
    message: "Username must be at least 2 characters.",
  }),
  email: z.string().email({
    message: "Please enter a valid email address.",
  }),
  bio: z.string().max(160).min(4),
  urls: z.array(z.object({ value: z.string().url() })).optional(),
  marketingEmails: z.boolean().default(false).optional(),
})

type ProfileFormValues = z.infer<typeof profileFormSchema>

const defaultValues: Partial<ProfileFormValues> = {
  bio: "",
  urls: [{ value: "" }, { value: "" }],
  marketingEmails: false,
}

export function ProfileForm() {
  const form = useForm<ProfileFormValues>({
    resolver: zodResolver(profileFormSchema),
    defaultValues,
    mode: "onChange",
  })

  const [loading, setLoading] = useState(false)

  function onSubmit(data: ProfileFormValues) {
    setLoading(true)

    // 模拟API调用
    setTimeout(() => {
      toast({
        title: "Profile updated",
        description: "Your profile has been updated successfully.",
      })
      setLoading(false)
    }, 1000)
  }

  return (
    <Card className="w-full max-w-2xl mx-auto">
      <CardHeader>
        <CardTitle>Profile</CardTitle>
        <CardDescription>
          Update your profile information. Click save when you're done.
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-8">
            <FormField
              control={form.control}
              name="username"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Username</FormLabel>
                  <FormControl>
                    <Input placeholder="username" {...field} />
                  </FormControl>
                  <FormDescription>
                    This is your public display name.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Email</FormLabel>
                  <FormControl>
                    <Input type="email" placeholder="email@example.com" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="bio"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Bio</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Tell us a little bit about yourself"
                      className="resize-none"
                      {...field}
                    />
                  </FormControl>
                  <FormDescription>
                    You can <span>@mention</span> other users and organizations.
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="marketingEmails"
              render={({ field }) => (
                <FormItem className="flex flex-row items-start space-x-3 space-y-0">
                  <FormControl>
                    <Checkbox
                      checked={field.value}
                      onCheckedChange={field.onChange}
                    />
                  </FormControl>
                  <div className="space-y-1 leading-none">
                    <FormLabel>
                      Send me marketing emails
                    </FormLabel>
                    <FormDescription>
                      Receive occasional updates about new features.
                    </FormDescription>
                  </div>
                </FormItem>
              )}
            />

            <Button type="submit" disabled={loading}>
              {loading ? "Saving..." : "Save changes"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
```

### 主题系统

```typescript
// components/theme-provider.tsx
"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"

export function ThemeProvider({ children, ...props }: ThemeProviderProps) {
  return <NextThemesProvider {...props}>{children}</NextThemesProvider>
}

// components/theme-toggle.tsx
"use client"

import * as React from "react"
import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"

import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"

export function ThemeToggle() {
  const { setTheme } = useTheme()

  return (
    <DropdownMenu>
      <DropdownMenuTrigger asChild>
        <Button variant="outline" size="icon">
          <Sun className="h-[1.2rem] w-[1.2rem] rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
          <Moon className="absolute h-[1.2rem] w-[1.2rem] rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          <span className="sr-only">Toggle theme</span>
        </Button>
      </DropdownMenuTrigger>
      <DropdownMenuContent align="end">
        <DropdownMenuItem onClick={() => setTheme("light")}>
          Light
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("dark")}>
          Dark
        </DropdownMenuItem>
        <DropdownMenuItem onClick={() => setTheme("system")}>
          System
        </DropdownMenuItem>
      </DropdownMenuContent>
    </DropdownMenu>
  )
}

// app/layout.tsx - 集成主题提供者
import { ThemeProvider } from "@/components/theme-provider"

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body>
        <ThemeProvider
          attribute="class"
          defaultTheme="system"
          enableSystem
          disableTransitionOnChange
        >
          {children}
        </ThemeProvider>
      </body>
    </html>
  )
}
```

## 自定义组件库

### 基础组件架构

```typescript
// components/ui/base.tsx
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

// 通用样式变体
const baseVariants = {
  // 按钮变体
  button: cva(
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
  ),

  // 输入框变体
  input: cva(
    "flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50",
    {
      variants: {
        variant: {
          default: "",
          error: "border-red-500 focus-visible:ring-red-500",
          success: "border-green-500 focus-visible:ring-green-500",
        },
      },
      defaultVariants: {
        variant: "default",
      },
    }
  ),
}

// 导出变体配置
export { baseVariants }
```

```typescript
// components/ui/custom-button.tsx
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"

const buttonVariants = cva(
  "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:pointer-events-none disabled:opacity-50",
  {
    variants: {
      variant: {
        default: "bg-primary text-primary-foreground hover:bg-primary/90",
        destructive: "bg-destructive text-destructive-foreground hover:bg-destructive/90",
        outline: "border border-input bg-background hover:bg-accent hover:text-accent-foreground",
        secondary: "bg-secondary text-secondary-foreground hover:bg-secondary/80",
        ghost: "hover:bg-accent hover:text-accent-foreground",
        link: "text-primary underline-offset-4 hover:underline",
        gradient: "bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700",
      },
      size: {
        default: "h-10 px-4 py-2",
        sm: "h-9 rounded-md px-3",
        lg: "h-11 rounded-md px-8",
        icon: "h-10 w-10",
        xl: "h-12 rounded-lg px-10",
      },
      loading: {
        true: "cursor-not-allowed opacity-70",
        false: "",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
      loading: false,
    },
  }
)

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean
  leftIcon?: React.ReactNode
  rightIcon?: React.ReactNode
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, leftIcon, rightIcon, children, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, loading, className }))}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
        {!loading && leftIcon && <span className="mr-2">{leftIcon}</span>}
        {children}
        {!loading && rightIcon && <span className="ml-2">{rightIcon}</span>}
      </button>
    )
  }
)
Button.displayName = "Button"

export { Button, buttonVariants }
```

```typescript
// components/ui/custom-card.tsx
import * as React from "react"
import { cva, type VariantProps } from "class-variance-authority"
import { cn } from "@/lib/utils"

const cardVariants = cva(
  "rounded-lg border bg-card text-card-foreground shadow-sm",
  {
    variants: {
      variant: {
        default: "",
        elevated: "shadow-lg",
        outlined: "border-2",
        flat: "border-0 shadow-none",
      },
      size: {
        default: "p-6",
        sm: "p-4",
        lg: "p-8",
        xl: "p-10",
      },
    },
    defaultVariants: {
      variant: "default",
      size: "default",
    },
  }
)

const CardHeaderVariants = cva("flex flex-col space-y-1.5 p-6", {
  variants: {
    spacing: {
      default: "",
      tight: "pb-4",
      loose: "pb-8",
    },
  },
  defaultVariants: {
    spacing: "default",
  },
})

export interface CardProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof cardVariants> {}

export interface CardHeaderProps
  extends React.HTMLAttributes<HTMLDivElement>,
    VariantProps<typeof CardHeaderVariants> {}

const Card = React.forwardRef<HTMLDivElement, CardProps>(
  ({ className, variant, size, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(cardVariants({ variant, size, className }))}
      {...props}
    />
  )
)
Card.displayName = "Card"

const CardHeader = React.forwardRef<HTMLDivElement, CardHeaderProps>(
  ({ className, spacing, ...props }, ref) => (
    <div
      ref={ref}
      className={cn(CardHeaderVariants({ spacing, className }))}
      {...props}
    />
  )
)
CardHeader.displayName = "CardHeader"

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      "text-2xl font-semibold leading-none tracking-tight",
      className
    )}
    {...props}
  />
))
CardTitle.displayName = "CardTitle"

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-muted-foreground", className)}
    {...props}
  />
))
CardDescription.displayName = "CardDescription"

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
))
CardContent.displayName = "CardContent"

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
))
CardFooter.displayName = "CardFooter"

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent }
```

### 高级组件模式

```typescript
// components/ui/combo-box.tsx
"use client"

import * as React from "react"
import * as PopoverPrimitive from "@radix-ui/react-popover"
import { Check, ChevronsUpDown } from "lucide-react"
import { cn } from "@/lib/utils"
import { Button } from "@/components/ui/button"
import {
  Command,
  CommandEmpty,
  CommandGroup,
  CommandInput,
  CommandItem,
} from "@/components/ui/command"

export interface ComboboxOption {
  value: string
  label: string
}

interface ComboboxProps {
  options: ComboboxOption[]
  value?: string
  onValueChange?: (value: string) => void
  placeholder?: string
  searchPlaceholder?: string
  emptyMessage?: string
  className?: string
  disabled?: boolean
}

export function Combobox({
  options,
  value,
  onValueChange,
  placeholder = "Select an option...",
  searchPlaceholder = "Search options...",
  emptyMessage = "No options found.",
  className,
  disabled = false,
}: ComboboxProps) {
  const [open, setOpen] = React.useState(false)

  return (
    <PopoverPrimitive.Root open={open} onOpenChange={setOpen}>
      <PopoverPrimitive.Trigger asChild>
        <Button
          variant="outline"
          role="combobox"
          aria-expanded={open}
          className={cn("w-full justify-between", className)}
          disabled={disabled}
        >
          {value
            ? options.find((option) => option.value === value)?.label
            : placeholder}
          <ChevronsUpDown className="ml-2 h-4 w-4 shrink-0 opacity-50" />
        </Button>
      </PopoverPrimitive.Trigger>
      <PopoverPrimitive.Portal>
        <PopoverPrimitive.Content
          className={cn(
            "w-full p-0",
            "z-50 min-w-[8rem] overflow-hidden rounded-md border bg-popover text-popover-foreground shadow-md",
            "data-[state=open]:animate-in data-[state=closed]:animate-out",
            "data-[state=closed]:fade-out-0 data-[state=open]:fade-in-0",
            "data-[state=closed]:zoom-out-95 data-[state=open]:zoom-in-95",
            "data-[side=bottom]:slide-in-from-top-2 data-[side=left]:slide-in-from-right-2",
            "data-[side=right]:slide-in-from-left-2 data-[side=top]:slide-in-from-bottom-2"
          )}
        >
          <Command>
            <CommandInput placeholder={searchPlaceholder} />
            <CommandEmpty>{emptyMessage}</CommandEmpty>
            <CommandGroup>
              {options.map((option) => (
                <CommandItem
                  key={option.value}
                  onSelect={() => {
                    onValueChange?.(option.value)
                    setOpen(false)
                  }}
                >
                  <Check
                    className={cn(
                      "mr-2 h-4 w-4",
                      value === option.value ? "opacity-100" : "opacity-0"
                    )}
                  />
                  {option.label}
                </CommandItem>
              ))}
            </CommandGroup>
          </Command>
        </PopoverPrimitive.Content>
      </PopoverPrimitive.Portal>
    </PopoverPrimitive.Root>
  )
}

// 使用示例
function ComboBoxExample() {
  const frameworks = [
    { value: "next.js", label: "Next.js" },
    { value: "sveltekit", label: "SvelteKit" },
    { value: "nuxt.js", label: "Nuxt.js" },
    { value: "remix", label: "Remix" },
    { value: "astro", label: "Astro" },
  ]

  const [value, setValue] = React.useState("")

  return (
    <div className="w-full max-w-sm">
      <Combobox
        options={frameworks}
        value={value}
        onValueChange={setValue}
        placeholder="Select a framework..."
        searchPlaceholder="Search frameworks..."
      />
    </div>
  )
}
```

## 设计系统构建

### 设计令牌系统

```typescript
// tokens/design-tokens.ts
export const designTokens = {
  // 颜色
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      200: '#bfdbfe',
      300: '#93c5fd',
      400: '#60a5fa',
      500: '#3b82f6',
      600: '#2563eb',
      700: '#1d4ed8',
      800: '#1e40af',
      900: '#1e3a8a',
    },
    neutral: {
      50: '#f9fafb',
      100: '#f3f4f6',
      200: '#e5e7eb',
      300: '#d1d5db',
      400: '#9ca3af',
      500: '#6b7280',
      600: '#4b5563',
      700: '#374151',
      800: '#1f2937',
      900: '#111827',
    },
    semantic: {
      success: '#10b981',
      warning: '#f59e0b',
      error: '#ef4444',
      info: '#3b82f6',
    },
  },

  // 间距
  spacing: {
    xs: '0.25rem',   // 4px
    sm: '0.5rem',    // 8px
    md: '1rem',      // 16px
    lg: '1.5rem',    // 24px
    xl: '2rem',      // 32px
    '2xl': '3rem',   // 48px
    '3xl': '4rem',   // 64px
  },

  // 字体
  typography: {
    fontFamily: {
      sans: ['Inter', 'system-ui', 'sans-serif'],
      mono: ['JetBrains Mono', 'monospace'],
    },
    fontSize: {
      xs: ['0.75rem', { lineHeight: '1rem' }],      // 12px
      sm: ['0.875rem', { lineHeight: '1.25rem' }],   // 14px
      base: ['1rem', { lineHeight: '1.5rem' }],       // 16px
      lg: ['1.125rem', { lineHeight: '1.75rem' }],    // 18px
      xl: ['1.25rem', { lineHeight: '1.75rem' }],     // 20px
      '2xl': ['1.5rem', { lineHeight: '2rem' }],       // 24px
      '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
      '4xl': ['2.25rem', { lineHeight: '2.5rem' }],   // 36px
    },
    fontWeight: {
      normal: '400',
      medium: '500',
      semibold: '600',
      bold: '700',
    },
  },

  // 圆角
  borderRadius: {
    none: '0',
    sm: '0.125rem',  // 2px
    md: '0.375rem',  // 6px
    lg: '0.5rem',    // 8px
    xl: '0.75rem',   // 12px
    '2xl': '1rem',   // 16px
    full: '9999px',
  },

  // 阴影
  shadows: {
    sm: '0 1px 2px 0 rgb(0 0 0 / 0.05)',
    md: '0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1)',
    lg: '0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1)',
    xl: '0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1)',
  },

  // 动画
  animation: {
    duration: {
      fast: '150ms',
      normal: '300ms',
      slow: '500ms',
    },
    easing: {
      ease: 'cubic-bezier(0.4, 0, 0.2, 1)',
      easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
      easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
      easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
    },
  },
}

// 生成CSS自定义属性
export function generateCSSProperties() {
  const properties: Record<string, string> = {}

  // 颜色
  Object.entries(designTokens.colors).forEach(([category, colors]) => {
    Object.entries(colors).forEach(([shade, value]) => {
      properties[`--color-${category}-${shade}`] = value
    })
  })

  // 间距
  Object.entries(designTokens.spacing).forEach(([key, value]) => {
    properties[`--spacing-${key}`] = value
  })

  // 字体
  Object.entries(designTokens.typography.fontFamily).forEach(([key, value]) => {
    properties[`--font-${key}`] = value.join(', ')
  })

  return properties
}
```

### 组件变体生成器

```typescript
// lib/component-variants.ts
import { cva } from "class-variance-authority"
import { designTokens } from "@/tokens/design-tokens"

// 通用间距变体
export const spacingVariants = cva("", {
  variants: {
    spacing: {
      none: "",
      xs: "space-y-1",
      sm: "space-y-2",
      md: "space-y-4",
      lg: "space-y-6",
      xl: "space-y-8",
      "2xl": "space-y-12",
    },
    padding: {
      none: "",
      xs: "p-1",
      sm: "p-2",
      md: "p-4",
      lg: "p-6",
      xl: "p-8",
      "2xl": "p-12",
    },
    margin: {
      none: "",
      xs: "m-1",
      sm: "m-2",
      md: "m-4",
      lg: "m-6",
      xl: "m-8",
      "2xl": "m-12",
    },
  },
  defaultVariants: {
    spacing: "md",
    padding: "none",
    margin: "none",
  },
})

// 布局变体
export const layoutVariants = cva("", {
  variants: {
    layout: {
      stack: "flex flex-col",
      horizontal: "flex flex-row",
      grid: "grid",
    },
    align: {
      start: "items-start",
      center: "items-center",
      end: "items-end",
      stretch: "items-stretch",
    },
    justify: {
      start: "justify-start",
      center: "justify-center",
      end: "justify-end",
      between: "justify-between",
      around: "justify-around",
      evenly: "justify-evenly",
    },
    gap: {
      none: "gap-0",
      xs: "gap-1",
      sm: "gap-2",
      md: "gap-4",
      lg: "gap-6",
      xl: "gap-8",
      "2xl": "gap-12",
    },
  },
  defaultVariants: {
    layout: "stack",
    align: "start",
    justify: "start",
    gap: "md",
  },
})

// 响应式变体
export const responsiveVariants = cva("", {
  variants: {
    responsive: {
      mobile: "",
      tablet: "md:",
      desktop: "lg:",
      wide: "xl:",
    },
    hidden: {
      mobile: "hidden",
      tablet: "md:hidden",
      desktop: "lg:hidden",
      wide: "xl:hidden",
    },
    visible: {
      mobile: "",
      tablet: "md:block",
      desktop: "lg:block",
      wide: "xl:block",
    },
  },
  defaultVariants: {
    responsive: "mobile",
    hidden: "",
    visible: "",
  },
})
```

## 无障碍设计

### 无障碍最佳实践

```typescript
// components/ui/accessible-button.tsx
"use client"

import * as React from "react"
import { cn } from "@/lib/utils"
import { Loader2 } from "lucide-react"

interface AccessibleButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  loading?: boolean
  loadingText?: string
  icon?: React.ReactNode
  iconPosition?: "left" | "right"
  variant?: "default" | "destructive" | "outline" | "secondary" | "ghost" | "link"
  size?: "default" | "sm" | "lg" | "icon"
}

const AccessibleButton = React.forwardRef<HTMLButtonElement, AccessibleButtonProps>(
  ({
    className,
    children,
    loading = false,
    loadingText = "Loading...",
    icon,
    iconPosition = "left",
    variant = "default",
    size = "default",
    disabled,
    ...props
  }, ref) => {
    const baseClasses = cn(
      "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors",
      "focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2",
      "disabled:pointer-events-none disabled:opacity-50",
      {
        "bg-primary text-primary-foreground hover:bg-primary/90": variant === "default",
        "bg-destructive text-destructive-foreground hover:bg-destructive/90": variant === "destructive",
        "border border-input bg-background hover:bg-accent hover:text-accent-foreground": variant === "outline",
        "bg-secondary text-secondary-foreground hover:bg-secondary/80": variant === "secondary",
        "hover:bg-accent hover:text-accent-foreground": variant === "ghost",
        "text-primary underline-offset-4 hover:underline": variant === "link",
      },
      {
        "h-10 px-4 py-2": size === "default",
        "h-9 rounded-md px-3": size === "sm",
        "h-11 rounded-md px-8": size === "lg",
        "h-10 w-10": size === "icon",
      },
      className
    )

    const isDisabled = disabled || loading

    return (
      <button
        ref={ref}
        className={baseClasses}
        disabled={isDisabled}
        aria-disabled={isDisabled}
        aria-busy={loading}
        {...props}
      >
        {loading && (
          <>
            <Loader2 className="mr-2 h-4 w-4 animate-spin" />
            <span className="sr-only">{loadingText}</span>
          </>
        )}

        {!loading && icon && iconPosition === "left" && (
          <span className="mr-2" aria-hidden="true">
            {icon}
          </span>
        )}

        <span>{loading ? loadingText : children}</span>

        {!loading && icon && iconPosition === "right" && (
          <span className="ml-2" aria-hidden="true">
            {icon}
          </span>
        )}
      </button>
    )
  }
)
AccessibleButton.displayName = "AccessibleButton"

// 使用示例
function AccessibleExample() {
  return (
    <div className="space-y-4">
      <AccessibleButton
        onClick={() => console.log("Clicked")}
        aria-label="Save changes"
      >
        Save
      </AccessibleButton>

      <AccessibleButton
        loading={true}
        loadingText="Saving..."
        icon={<Loader2 className="h-4 w-4" />}
        variant="outline"
      >
        Save
      </AccessibleButton>
    </div>
  )
}
```

### 键盘导航支持

```typescript
// components/ui/focus-trap.tsx
"use client"

import * as React from "react"
import { createPortal } from "react-dom"

interface FocusTrapProps {
  children: React.ReactNode
  active: boolean
  onEscape?: () => void
}

export function FocusTrap({ children, active, onEscape }: FocusTrapProps) {
  const containerRef = React.useRef<HTMLDivElement>(null)

  React.useEffect(() => {
    if (!active) return

    const container = containerRef.current
    if (!container) return

    // 获取所有可聚焦元素
    const focusableElements = container.querySelectorAll(
      'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
    )

    const firstElement = focusableElements[0] as HTMLElement
    const lastElement = focusableElements[focusableElements.length - 1] as HTMLElement

    // 初始聚焦
    firstElement?.focus()

    // 键盘事件处理
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onEscape?.()
        return
      }

      if (event.key !== 'Tab') return

      // Shift + Tab
      if (event.shiftKey) {
        if (document.activeElement === firstElement) {
          lastElement?.focus()
          event.preventDefault()
        }
      } else {
        // Tab
        if (document.activeElement === lastElement) {
          firstElement?.focus()
          event.preventDefault()
        }
      }
    }

    container.addEventListener('keydown', handleKeyDown)

    return () => {
      container.removeEventListener('keydown', handleKeyDown)
    }
  }, [active, onEscape])

  return (
    <div ref={containerRef} tabIndex={-1}>
      {children}
    </div>
  )
}

// 使用示例 - 模态框
function Modal({ isOpen, onClose, children }: { isOpen: boolean; onClose: () => void; children: React.ReactNode }) {
  if (!isOpen) return null

  return createPortal(
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
      <FocusTrap active={isOpen} onEscape={onClose}>
        <div className="bg-white rounded-lg p-6 max-w-md w-full mx-4">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-lg font-semibold">Modal Title</h2>
            <button
              onClick={onClose}
              aria-label="Close modal"
              className="text-gray-500 hover:text-gray-700"
            >
              ×
            </button>
          </div>
          {children}
        </div>
      </FocusTrap>
    </div>,
    document.body
  )
}
```

### 屏幕阅读器支持

```typescript
// components/ui/live-region.tsx
"use client"

import * as React from "react"

interface LiveRegionProps {
  ariaLive?: "polite" | "assertive" | "off"
  ariaAtomic?: boolean
  ariaRelevant?: "additions" | "removals" | "text" | "all"
  className?: string
  children?: React.ReactNode
}

export function LiveRegion({
  ariaLive = "polite",
  ariaAtomic = true,
  ariaRelevant = "additions text",
  className,
  children,
}: LiveRegionProps) {
  return (
    <div
      aria-live={ariaLive}
      aria-atomic={ariaAtomic}
      aria-relevant={ariaRelevant}
      className={cn("sr-only", className)}
    >
      {children}
    </div>
  )
}

// 使用示例 - 通知组件
function AccessibleToast({ message, type = "info" }: { message: string; type?: "info" | "success" | "warning" | "error" }) {
  const [isVisible, setIsVisible] = React.useState(true)

  React.useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false)
    }, 5000)

    return () => clearTimeout(timer)
  }, [])

  if (!isVisible) return null

  return (
    <>
      <div className="fixed bottom-4 right-4 p-4 rounded-lg shadow-lg z-50">
        <div className={cn(
          "p-4 rounded-lg",
          {
            "bg-blue-500 text-white": type === "info",
            "bg-green-500 text-white": type === "success",
            "bg-yellow-500 text-white": type === "warning",
            "bg-red-500 text-white": type === "error",
          }
        )}>
          {message}
        </div>
      </div>

      {/* 屏幕阅读器通知 */}
      <LiveRegion ariaLive="polite">
        {type === "error" && `Error: ${message}`}
        {type === "success" && `Success: ${message}`}
        {type === "warning" && `Warning: ${message}`}
        {type === "info" && `Information: ${message}`}
      </LiveRegion>
    </>
  )
}
```

## 性能优化

### 懒加载组件

```typescript
// components/lazy/lazy-component.tsx
"use client"

import * as React from "react"
import dynamic from "next/dynamic"
import { ErrorBoundary } from "./error-boundary"

// 懒加载配置接口
interface LazyComponentConfig {
  loading?: React.ComponentType
  error?: React.ComponentType<{ error: Error; retry: () => void }>
  fallback?: React.ReactNode
  ssr?: boolean
  suspense?: boolean
}

// 通用懒加载HOC
export function createLazyComponent<T extends Record<string, any>>(
  importFn: () => Promise<{ default: React.ComponentType<T> }>,
  config: LazyComponentConfig = {}
) {
  const {
    loading: LoadingComponent,
    error: ErrorComponent,
    fallback,
    ssr = false,
    suspense = true,
  } = config

  const LazyComponent = dynamic(importFn, {
    loading: LoadingComponent ? () => <LoadingComponent /> : () => fallback || null,
    ssr,
    suspense,
  })

  const WrappedComponent = (props: T) => {
    if (ErrorComponent) {
      return (
        <ErrorBoundary fallback={(error, retry) => (
          <ErrorComponent error={error} retry={retry} />
        )}>
          <LazyComponent {...props} />
        </ErrorBoundary>
      )
    }

    return <LazyComponent {...props} />
  }

  WrappedComponent.displayName = `LazyComponent(${importFn.name || "Unknown"})`

  return WrappedComponent
}

// 使用示例
const LazyChart = createLazyComponent(
  () => import("@/components/charts/line-chart"),
  {
    loading: () => (
      <div className="h-64 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
      </div>
    ),
    error: ({ error, retry }) => (
      <div className="h-64 flex flex-col items-center justify-center text-red-600">
        <p>Failed to load chart</p>
        <button
          onClick={retry}
          className="mt-2 px-4 py-2 bg-red-500 text-white rounded hover:bg-red-600"
        >
          Retry
        </button>
      </div>
    ),
    ssr: false,
  }
)

// 组件使用
function Dashboard() {
  return (
    <div>
      <h2>Analytics Dashboard</h2>
      <LazyChart data={chartData} />
    </div>
  )
}
```

### 组件预取

```typescript
// hooks/use-component-prefetch.ts
"use client"

import * as React from "react"
import dynamic from "next/dynamic"

interface UseComponentPrefetchOptions {
  prefetchOnHover?: boolean
  prefetchDelay?: number
  prefetchOnVisible?: boolean
  visibilityThreshold?: number
}

export function useComponentPrefetch<T>(
  importFn: () => Promise<{ default: React.ComponentType<T> }>,
  options: UseComponentPrefetchOptions = {}
) {
  const {
    prefetchOnHover = true,
    prefetchDelay = 200,
    prefetchOnVisible = true,
    visibilityThreshold = 0.1,
  } = options

  const [isPrefetched, setIsPrefetched] = React.useState(false)
  const timeoutRef = React.useRef<NodeJS.Timeout>()

  const prefetch = React.useCallback(() => {
    if (!isPrefetched) {
      void importFn()
      setIsPrefetched(true)
    }
  }, [importFn, isPrefetched])

  const handleMouseEnter = React.useCallback(() => {
    if (prefetchOnHover && !isPrefetched) {
      timeoutRef.current = setTimeout(prefetch, prefetchDelay)
    }
  }, [prefetchOnHover, isPrefetched, prefetchDelay, prefetch])

  const handleMouseLeave = React.useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current)
    }
  }, [])

  const handleIntersection = React.useCallback(
    (entries: IntersectionObserverEntry[]) => {
      entries.forEach((entry) => {
        if (
          entry.isIntersecting &&
          entry.intersectionRatio >= visibilityThreshold &&
          !isPrefetched
        ) {
          prefetch()
        }
      })
    },
    [prefetch, isPrefetched, visibilityThreshold]
  )

  React.useEffect(() => {
    if (prefetchOnVisible) {
      const observer = new IntersectionObserver(handleIntersection, {
        threshold: visibilityThreshold,
      })

      const element = document.currentScript
      if (element) {
        observer.observe(element)
      }

      return () => {
        observer.disconnect()
      }
    }
  }, [prefetchOnVisible, handleIntersection, visibilityThreshold])

  React.useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current)
      }
    }
  }, [])

  return {
    prefetch,
    isPrefetched,
    onMouseEnter: handleMouseEnter,
    onMouseLeave: handleMouseLeave,
  }
}

// 使用示例
function PrefetchableComponent() {
  const { onMouseEnter, onMouseLeave } = useComponentPrefetch(
    () => import("@/components/heavy-component"),
    {
      prefetchOnHover: true,
      prefetchDelay: 300,
    }
  )

  return (
    <div
      onMouseEnter={onMouseEnter}
      onMouseLeave={onMouseLeave}
      className="p-4 border rounded hover:bg-gray-50"
    >
      <h3>Heavy Component</h3>
      <p>Hover to prefetch</p>
    </div>
  )
}
```

## 最佳实践

### 1. 组件设计原则

```typescript
// principles/component-design.ts
export interface ComponentDesignPrinciples {
  // 单一职责
  singleResponsibility: boolean

  // 可组合性
  composability: boolean

  // 可重用性
  reusability: boolean

  // 可测试性
  testability: boolean

  // 无障碍
  accessibility: boolean

  // 性能
  performance: boolean
}

// 良好的组件示例
function WellDesignedComponent({ title, content, actions }: {
  title: string
  content: string
  actions: React.ReactNode
}) {
  return (
    <div className="card">
      <h3 className="card-title">{title}</h3>
      <p className="card-content">{content}</p>
      <div className="card-actions">{actions}</div>
    </div>
  )
}

// 使用示例
function Usage() {
  return (
    <WellDesignedComponent
      title="User Profile"
      content="Manage your account settings"
      actions={
        <>
          <button>Edit</button>
          <button>Delete</button>
        </>
      }
    />
  )
}
```

### 2. 组件文档规范

```typescript
// components/ui/button/README.md
# Button Component

## Description

A versatile button component with multiple variants and states.

## Props

| Prop | Type | Default | Description |
|------|------|---------|-------------|
| variant | "default" \| "destructive" \| "outline" \| "secondary" \| "ghost" \| "link" | "default" | Button style variant |
| size | "default" \| "sm" \| "lg" \| "icon" | "default" | Button size |
| loading | boolean | false | Loading state |
| disabled | boolean | false | Disabled state |
| onClick | () => void | - | Click handler |
| children | React.ReactNode | - | Button content |

## Accessibility

- Supports keyboard navigation
- Proper ARIA attributes
- Screen reader announcements for loading state
- Focus management

## Examples

### Basic Usage
```tsx
<Button onClick={() => console.log('Clicked')}>
  Click me
</Button>
```

### Loading State
```tsx
<Button loading onClick={() => {}}>
  Save
</Button>
```

### With Icon
```tsx
<Button icon={<PlusIcon />} onClick={() => {}}>
  Add Item
</Button>
```

## Best Practices

1. Use clear, concise button text
2. Provide loading feedback for async actions
3. Ensure sufficient color contrast
4. Test keyboard navigation
5. Use appropriate button variants for different contexts
```

### 3. 性能优化清单

```typescript
// checklists/performance-checklist.ts
export const performanceChecklist = {
  // 组件级优化
  component: [
    "使用React.memo优化纯组件",
    "避免不必要的重新渲染",
    "使用useCallback和useMemo优化函数和值",
    "拆分大型组件为小型组件",
    "懒加载非关键组件",
  ],

  // 渲染优化
  rendering: [
    "使用虚拟化处理长列表",
    "优化图片加载（懒加载、格式优化）",
    "减少DOM节点数量",
    "使用CSS动画代替JavaScript动画",
    "优化字体加载",
  ],

  // 代码分割
  codeSplitting: [
    "按路由分割代码",
    "按功能分割代码",
    "使用动态导入",
    "预取关键资源",
    "延迟加载非关键功能",
  ],

  // 缓存策略
  caching: [
    "使用React Query缓存数据",
    "实现组件级缓存",
    "优化资源缓存",
    "使用Service Worker",
    "实现离线功能",
  ],
}
```

## 项目实战

### 完整的组件库示例

```typescript
// components/index.ts
export * from './ui/button'
export * from './ui/card'
export * from './ui/input'
export * from './ui/label'
export * from './ui/dialog'
export * from './ui/toast'
export * from './ui/theme-provider'
export * from './ui/combobox'
export * from './ui/accessible-button'
export * from './ui/focus-trap'
export * from './ui/live-region'

// hooks/index.ts
export * from './hooks/use-theme'
export * from './hooks/use-component-prefetch'
export * from './hooks/use-local-storage'
export * from './hooks/use-debounce'

// utils/index.ts
export * from './utils/cn'
export * from './utils/component-variants'
export * from './utils/accessibility-helpers'

// tokens/index.ts
export * from './tokens/design-tokens'
export * from './tokens/color-palette'

// 创建完整的应用组件
import { Button, Card, CardHeader, CardTitle, CardContent } from '@/components'
import { useTheme } from '@/hooks/use-theme'
import { designTokens } from '@/tokens/design-tokens'

function App() {
  const { theme, setTheme } = useTheme()

  return (
    <div className={`min-h-screen ${theme === 'dark' ? 'dark' : ''}`}>
      <div className="bg-background text-foreground">
        <header className="border-b">
          <div className="container mx-auto px-4 py-4">
            <div className="flex justify-between items-center">
              <h1 className="text-2xl font-bold">My App</h1>
              <Button
                variant="ghost"
                onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
              >
                Toggle Theme
              </Button>
            </div>
          </div>
        </header>

        <main className="container mx-auto px-4 py-8">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            <Card>
              <CardHeader>
                <CardTitle>Feature 1</CardTitle>
              </CardHeader>
              <CardContent>
                <p>This is a feature card with consistent styling.</p>
                <Button className="mt-4">Learn More</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Feature 2</CardTitle>
              </CardHeader>
              <CardContent>
                <p>All components follow the design system.</p>
                <Button className="mt-4">Learn More</Button>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>Feature 3</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Accessible and performant by default.</p>
                <Button className="mt-4">Learn More</Button>
              </CardContent>
            </Card>
          </div>
        </main>
      </div>
    </div>
  )
}

export default App
```

## 总结

### 关键要点

1. **UI库选择**
   - Shadcn/ui适合现代化应用开发
   - MUI适合企业级应用
   - Ant Design适合管理后台
   - Chakra UI适合快速原型开发

2. **组件设计原则**
   - 单一职责和可组合性
   - 一致的设计语言
   - 良好的无障碍支持
   - 性能优化考虑

3. **设计系统构建**
   - 设计令牌系统
   - 组件变体生成
   - 主题支持
   - 响应式设计

4. **无障碍最佳实践**
   - 键盘导航支持
   - 屏幕阅读器兼容
   - ARIA属性使用
   - 焦点管理

5. **性能优化**
   - 组件懒加载
   - 代码分割
   - 预取策略
   - 缓存优化

### 最佳实践总结

- **选择合适的UI库**: 根据项目需求选择最适合的UI库
- **构建设计系统**: 建立统一的设计令牌和组件变体
- **注重无障碍**: 确保组件对所有用户都可用
- **性能优先**: 使用懒加载、代码分割等优化技术
- **文档完善**: 提供详细的组件文档和使用示例

### 下一步学习

- 深入学习无障碍设计
- 探索动画和交互设计
- 学习设计工具集成
- 实现组件测试策略

---

通过这个文档，你已经掌握了Next.js 15中UI组件库和设计系统的完整知识体系。这些技能将帮助你构建美观、一致、无障碍且高性能的现代化Web应用。记住选择合适的技术栈，注重用户体验，并持续优化性能。