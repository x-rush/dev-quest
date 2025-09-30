# 设计系统 - Next.js 15 现代架构实践

## 📋 概述

设计系统是一套可重用的组件、指导原则和文档，用于构建一致的数字产品体验。Next.js 15 结合现代设计工具，为构建强大的设计系统提供了理想的基础设施。

## 🎯 设计系统基础

### 1. 设计系统架构

```
design-system/
├── tokens/                    # 设计令牌
│   ├── colors.ts
│   ├── spacing.ts
│   ├── typography.ts
│   └── breakpoints.ts
├── components/                # 基础组件
│   ├── Button/
│   ├── Input/
│   ├── Card/
│   └── Modal/
├── patterns/                  # 复合模式
│   ├── Form/
│   ├── Navigation/
│   └── DataDisplay/
├── templates/                # 页面模板
│   ├── DashboardTemplate.tsx
│   ├── AuthTemplate.tsx
│   └── MarketingTemplate.tsx
├── hooks/                    # 专用Hooks
│   ├── useTheme.ts
│   ├── useToast.ts
│   └── useModal.ts
├── utils/                    # 工具函数
│   ├── cn.ts
│   ├── cva.ts
│   └── merge-refs.ts
└── docs/                      # 文档
    ├── getting-started.md
    ├── components/
    └── patterns/
```

### 2. 设计令牌（Design Tokens）

```typescript
// tokens/colors.ts
export const colors = {
  // 主色调
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
    950: '#172554',
  },
  // 次要色调
  secondary: {
    50: '#f8fafc',
    100: '#f1f5f9',
    200: '#e2e8f0',
    300: '#cbd5e1',
    400: '#94a3b8',
    500: '#64748b',
    600: '#475569',
    700: '#334155',
    800: '#1e293b',
    900: '#0f172a',
    950: '#020617',
  },
  // 语义化颜色
  success: {
    50: '#f0fdf4',
    500: '#22c55e',
    900: '#14532d',
  },
  warning: {
    50: '#fffbeb',
    500: '#f59e0b',
    900: '#78350f',
  },
  error: {
    50: '#fef2f2',
    500: '#ef4444',
    900: '#7f1d1d',
  },
  // 中性色
  gray: {
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
} as const;

// tokens/spacing.ts
export const spacing = {
  px: '1px',
  0: '0',
  1: '0.25rem',  // 4px
  2: '0.5rem',   // 8px
  3: '0.75rem',  // 12px
  4: '1rem',     // 16px
  5: '1.25rem',  // 20px
  6: '1.5rem',   // 24px
  8: '2rem',     // 32px
  10: '2.5rem',  // 40px
  12: '3rem',    // 48px
  16: '4rem',    // 64px
  20: '5rem',    // 80px
  24: '6rem',    // 96px
} as const;

// tokens/typography.ts
export const typography = {
  fontFamily: {
    sans: ['Inter', 'system-ui', 'sans-serif'],
    mono: ['JetBrains Mono', 'Monaco', 'Consolas', 'monospace'],
  },
  fontSize: {
    xs: ['0.75rem', { lineHeight: '1rem' }],     // 12px
    sm: ['0.875rem', { lineHeight: '1.25rem' }], // 14px
    base: ['1rem', { lineHeight: '1.5rem' }],    // 16px
    lg: ['1.125rem', { lineHeight: '1.75rem' }], // 18px
    xl: ['1.25rem', { lineHeight: '1.75rem' }], // 20px
    '2xl': ['1.5rem', { lineHeight: '2rem' }],  // 24px
    '3xl': ['1.875rem', { lineHeight: '2.25rem' }], // 30px
    '4xl': ['2.25rem', { lineHeight: '2.5rem' }],  // 36px
    '5xl': ['3rem', { lineHeight: '1' }],         // 48px
    '6xl': ['3.75rem', { lineHeight: '1' }],      // 60px
  },
  fontWeight: {
    light: '300',
    normal: '400',
    medium: '500',
    semibold: '600',
    bold: '700',
    extrabold: '800',
  },
  letterSpacing: {
    tight: '-0.025em',
    normal: '0',
    wide: '0.025em',
  },
} as const;

// tokens/breakpoints.ts
export const breakpoints = {
  sm: '640px',   // 40em
  md: '768px',   // 48em
  lg: '1024px',  // 64em
  xl: '1280px',  // 80em
  '2xl': '1536px', // 96em
} as const;
```

## 🚀 基础组件实现

### 1. Button 组件

```typescript
// components/Button/Button.tsx
import * as React from 'react';
import { cva, type VariantProps } from 'class-variance-authority';
import { cn } from '@/utils/cn';
import { Loader2 } from 'lucide-react';

const buttonVariants = cva(
  'inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none ring-offset-background',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground hover:bg-primary/90',
        destructive: 'bg-destructive text-destructive-foreground hover:bg-destructive/90',
        outline: 'border border-input hover:bg-accent hover:text-accent-foreground',
        secondary: 'bg-secondary text-secondary-foreground hover:bg-secondary/80',
        ghost: 'hover:bg-accent hover:text-accent-foreground',
        link: 'underline-offset-4 hover:underline text-primary',
      },
      size: {
        default: 'h-10 py-2 px-4',
        sm: 'h-9 px-3 rounded-md',
        lg: 'h-11 px-8 rounded-md',
        icon: 'h-10 w-10',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'default',
    },
  }
);

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement>,
    VariantProps<typeof buttonVariants> {
  loading?: boolean;
  asChild?: boolean;
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant, size, loading, children, disabled, ...props }, ref) => {
    return (
      <button
        className={cn(buttonVariants({ variant, size, className }))}
        ref={ref}
        disabled={disabled || loading}
        {...props}
      >
        {loading && <Loader2 className=\"mr-2 h-4 w-4 animate-spin\" />}
        {children}
      </button>
    );
  }
);

Button.displayName = 'Button';

export { Button, buttonVariants };
```

### 2. Input 组件

```typescript
// components/Input/Input.tsx
import * as React from 'react';
import { cn } from '@/utils/cn';

export interface InputProps
  extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helperText?: string;
  leftIcon?: React.ReactNode;
  rightIcon?: React.ReactNode;
}

const Input = React.forwardRef<HTMLInputElement, InputProps>(
  ({ className, type, label, error, helperText, leftIcon, rightIcon, ...props }, ref) => {
    return (
      <div className=\"space-y-1\">
        {label && (
          <label
            htmlFor={props.id}
            className=\"text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70\"
          >
            {label}
          </label>
        )}
        <div className=\"relative\">
          {leftIcon && (
            <div className=\"absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground\">
              {leftIcon}
            </div>
          )}
          <input
            type={type}
            className={cn(
              'flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50',
              leftIcon && 'pl-10',
              rightIcon && 'pr-10',
              error && 'border-destructive focus-visible:ring-destructive',
              className
            )}
            ref={ref}
            {...props}
          />
          {rightIcon && (
            <div className=\"absolute right-3 top-1/2 transform -translate-y-1/2 text-muted-foreground\">
              {rightIcon}
            </div>
          )}
        </div>
        {(error || helperText) && (
          <p className={cn(
            'text-xs',
            error ? 'text-destructive' : 'text-muted-foreground'
          )}>
            {error || helperText}
          </p>
        )}
      </div>
    );
  }
);

Input.displayName = 'Input';

export { Input };
```

### 3. Card 组件

```typescript
// components/Card/Card.tsx
import * as React from 'react';
import { cn } from '@/utils/cn';

const Card = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      'rounded-lg border bg-card text-card-foreground shadow-sm',
      className
    )}
    {...props}
  />
));

Card.displayName = 'Card';

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex flex-col space-y-1.5 p-6', className)}
    {...props}
  />
));

CardHeader.displayName = 'CardHeader';

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn(
      'text-2xl font-semibold leading-none tracking-tight',
      className
    )}
    {...props}
  />
));

CardTitle.displayName = 'CardTitle';

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn('text-sm text-muted-foreground', className)}
    {...props}
  />
));

CardDescription.displayName = 'CardDescription';

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn('p-6 pt-0', className)} {...props} />
));

CardContent.displayName = 'CardContent';

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn('flex items-center p-6 pt-0', className)}
    {...props}
  />
));

CardFooter.displayName = 'CardFooter';

export { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent };
```

## 🎨 复合模式（Patterns）

### 1. Form 模式

```typescript
// patterns/Form/Form.tsx
import * as React from 'react';
import { Input } from '@/components/Input';
import { Button } from '@/components/Button';
import { cn } from '@/utils/cn';

export interface FormField {
  name: string;
  label: string;
  type?: string;
  placeholder?: string;
  required?: boolean;
  validation?: (value: string) => string | undefined;
}

export interface FormProps {
  fields: FormField[];
  onSubmit: (data: Record<string, string>) => void;
  submitText?: string;
  className?: string;
}

export function Form({ fields, onSubmit, submitText = 'Submit', className }: FormProps) {
  const [values, setValues] = React.useState<Record<string, string>>({});
  const [errors, setErrors] = React.useState<Record<string, string>>({});
  const [isSubmitting, setIsSubmitting] = React.useState(false);

  const handleChange = (name: string, value: string) => {
    setValues(prev => ({ ...prev, [name]: value }));

    // 清除错误
    if (errors[name]) {
      setErrors(prev => {
        const newErrors = { ...prev };
        delete newErrors[name];
        return newErrors;
      });
    }
  };

  const validateField = (field: FormField, value: string): string | undefined => {
    if (field.required && !value.trim()) {
      return `${field.label} is required`;
    }

    if (field.validation) {
      return field.validation(value);
    }

    return undefined;
  };

  const validateForm = (): boolean => {
    const newErrors: Record<string, string> = {};
    let isValid = true;

    fields.forEach(field => {
      const error = validateField(field, values[field.name] || '');
      if (error) {
        newErrors[field.name] = error;
        isValid = false;
      }
    });

    setErrors(newErrors);
    return isValid;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } catch (error) {
      console.error('Form submission error:', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className={cn('space-y-6', className)}>
      {fields.map(field => (
        <Input
          key={field.name}
          id={field.name}
          label={field.label}
          type={field.type || 'text'}
          placeholder={field.placeholder}
          value={values[field.name] || ''}
          onChange={(e) => handleChange(field.name, e.target.value)}
          error={errors[field.name]}
          required={field.required}
        />
      ))}
      <Button type=\"submit\" loading={isSubmitting} className=\"w-full\">
        {submitText}
      </Button>
    </form>
  );
}
```

### 2. Data Display 模式

```typescript
// patterns/DataDisplay/Table.tsx
import * as React from 'react';
import { cn } from '@/utils/cn';

export interface TableColumn<T> {
  key: keyof T;
  label: string;
  render?: (value: any, item: T) => React.ReactNode;
  className?: string;
}

export interface TableProps<T> {
  data: T[];
  columns: TableColumn<T>[];
  loading?: boolean;
  emptyMessage?: string;
  className?: string;
}

export function Table<T extends Record<string, any>>({
  data,
  columns,
  loading = false,
  emptyMessage = 'No data available',
  className,
}: TableProps<T>) {
  if (loading) {
    return (
      <div className={cn('w-full overflow-hidden rounded-md border', className)}>
        <div className=\"space-y-4 p-6\">
          {[...Array(5)].map((_, i) => (
            <div key={i} className=\"space-y-2\">
              <div className=\"h-4 bg-muted rounded animate-pulse\" />
              <div className=\"h-4 bg-muted rounded animate-pulse w-3/4\" />
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className={cn('w-full overflow-hidden rounded-md border', className)}>
        <div className=\"flex flex-col items-center justify-center p-6 text-center\">
          <div className=\"text-lg font-medium text-muted-foreground\">
            {emptyMessage}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className={cn('w-full overflow-hidden rounded-md border', className)}>
      <table className=\"w-full\">
        <thead className=\"bg-muted\">
          <tr>
            {columns.map(column => (
              <th
                key={column.key as string}
                className={cn(
                  'px-6 py-3 text-left text-xs font-medium text-muted-foreground uppercase tracking-wider',
                  column.className
                )}
              >
                {column.label}
              </th>
            ))}
          </tr>
        </thead>
        <tbody className=\"divide-y divide-border\">
          {data.map((item, index) => (
            <tr key={index} className=\"hover:bg-muted/50\">
              {columns.map(column => (
                <td
                  key={column.key as string}
                  className={cn(
                    'px-6 py-4 whitespace-nowrap text-sm text-foreground',
                    column.className
                  )}
                >
                  {column.render
                    ? column.render(item[column.key], item)
                    : item[column.key]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
```

### 3. Navigation 模式

```typescript
// patterns/Navigation/Breadcrumb.tsx
import * as React from 'react';
import Link from 'next/link';
import { ChevronRight, Home } from 'lucide-react';
import { cn } from '@/utils/cn';

export interface BreadcrumbItem {
  label: string;
  href?: string;
  icon?: React.ReactNode;
}

export interface BreadcrumbProps {
  items: BreadcrumbItem[];
  className?: string;
}

export function Breadcrumb({ items, className }: BreadcrumbProps) {
  return (
    <nav className={cn('flex items-center space-x-1 text-sm text-muted-foreground', className)}>
      <Link href=\"/\" className=\"hover:text-foreground\">
        <Home className=\"h-4 w-4\" />
      </Link>
      {items.map((item, index) => (
        <React.Fragment key={index}>
          <ChevronRight className=\"h-4 w-4\" />
          {item.href && index < items.length - 1 ? (
            <Link href={item.href} className=\"hover:text-foreground\">
              {item.icon && <span className=\"mr-1\">{item.icon}</span>}
              {item.label}
            </Link>
          ) : (
            <span className=\"text-foreground\">
              {item.icon && <span className=\"mr-1\">{item.icon}</span>}
              {item.label}
            </span>
          )}
        </React.Fragment>
      ))}
    </nav>
  );
}
```

## 🔄 专用 Hooks

### 1. useTheme Hook

```typescript
// hooks/useTheme.ts
import * as React from 'react';

type Theme = 'light' | 'dark' | 'system';

export function useTheme() {
  const [theme, setTheme] = React.useState<Theme>('system');
  const [mounted, setMounted] = React.useState(false);

  React.useEffect(() => {
    setMounted(true);
    const stored = localStorage.getItem('theme') as Theme;
    if (stored) {
      setTheme(stored);
    }
  }, []);

  React.useEffect(() => {
    if (!mounted) return;

    const root = window.document.documentElement;

    if (theme === 'system') {
      const systemTheme = window.matchMedia('(prefers-color-scheme: dark)').matches
        ? 'dark'
        : 'light';
      root.classList.remove('light', 'dark');
      root.classList.add(systemTheme);
    } else {
      root.classList.remove('light', 'dark');
      root.classList.add(theme);
    }

    localStorage.setItem('theme', theme);
  }, [theme, mounted]);

  const value = React.useMemo(
    () => ({
      theme,
      setTheme: (theme: Theme) => {
        setTheme(theme);
      },
    }),
    [theme]
  );

  if (!mounted) {
    // 为了避免SSR不匹配，返回一个默认值
    return {
      theme: 'system',
      setTheme: () => {},
    };
  }

  return value;
}
```

### 2. useToast Hook

```typescript
// hooks/useToast.ts
import * as React from 'react';

export interface Toast {
  id: string;
  title?: string;
  description?: string;
  variant?: 'default' | 'destructive';
  action?: React.ReactNode;
}

const TOAST_LIMIT = 1;
const TOAST_REMOVE_DELAY = 1000000;

type ToasterToast = Toast & {
  id: string;
  title?: React.ReactNode;
  description?: React.ReactNode;
  action?: React.ReactNode;
};

const actionTypes = {
  ADD_TOAST: 'ADD_TOAST',
  UPDATE_TOAST: 'UPDATE_TOAST',
  DISMISS_TOAST: 'DISMISS_TOAST',
  REMOVE_TOAST: 'REMOVE_TOAST',
} as const;

let count = 0;

function genId() {
  count = (count + 1) % Number.MAX_SAFE_INTEGER;
  return count.toString();
}

type ActionType = typeof actionTypes;

type Action =
  | {
      type: ActionType['ADD_TOAST'];
      toast: ToasterToast;
    }
  | {
      type: ActionType['UPDATE_TOAST'];
      toast: Partial<ToasterToast>;
    }
  | {
      type: ActionType['DISMISS_TOAST'];
      toastId?: ToasterToast['id'];
    }
  | {
      type: ActionType['REMOVE_TOAST'];
      toastId?: ToasterToast['id'];
    };

interface State {
  toasts: ToasterToast[];
}

const toastTimeouts = new Map<string, ReturnType<typeof setTimeout>>();

const addToRemoveQueue = (toastId: string) => {
  if (toastTimeouts.has(toastId)) {
    return;
  }

  const timeout = setTimeout(() => {
    toastTimeouts.delete(toastId);
    dispatch({
      type: 'REMOVE_TOAST',
      toastId: toastId,
    });
  }, TOAST_REMOVE_DELAY);

  toastTimeouts.set(toastId, timeout);
};

export const reducer = (state: State, action: Action): State => {
  switch (action.type) {
    case 'ADD_TOAST':
      return {
        ...state,
        toasts: [action.toast, ...state.toasts].slice(0, TOAST_LIMIT),
      };

    case 'UPDATE_TOAST':
      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === action.toast.id ? { ...t, ...action.toast } : t
        ),
      };

    case 'DISMISS_TOAST': {
      const { toastId } = action;

      if (toastId) {
        addToRemoveQueue(toastId);
      } else {
        state.toasts.forEach((toast) => {
          addToRemoveQueue(toast.id);
        });
      }

      return {
        ...state,
        toasts: state.toasts.map((t) =>
          t.id === toastId || toastId === undefined
            ? {
                ...t,
                open: false,
              }
            : t
        ),
      };
    }
    case 'REMOVE_TOAST':
      if (action.toastId === undefined) {
        return {
          ...state,
          toasts: [],
        };
      }
      return {
        ...state,
        toasts: state.toasts.filter((t) => t.id !== action.toastId),
      };
  }
};

const listeners: Array<(state: State) => void> = [];

let memoryState: State = { toasts: [] };

function dispatch(action: Action) {
  memoryState = reducer(memoryState, action);
  listeners.forEach((listener) => {
    listener(memoryState);
  });
}

type Toast = Omit<ToasterToast, 'id'>;

function toast({ ...props }: Toast) {
  const id = genId();

  const update = (props: ToasterToast) =>
    dispatch({
      type: 'UPDATE_TOAST',
      toast: { ...props, id },
    });
  const dismiss = () => dispatch({ type: 'DISMISS_TOAST', toastId: id });

  dispatch({
    type: 'ADD_TOAST',
    toast: {
      ...props,
      id,
      open: true,
      onOpenChange: (open) => {
        if (!open) dismiss();
      },
    },
  });

  return {
    id: id,
    dismiss,
    update,
  };
}

function useToast() {
  const [state, setState] = React.useState<State>(memoryState);

  React.useEffect(() => {
    listeners.push(setState);
    return () => {
      const index = listeners.indexOf(setState);
      if (index > -1) {
        listeners.splice(index, 1);
      }
    };
  }, [state]);

  return {
    ...state,
    toast,
    dismiss: (toastId?: string) => dispatch({ type: 'DISMISS_TOAST', toastId }),
  };
}

export { useToast, toast };
```

## 🎯 页面模板

### 1. Dashboard 模板

```typescript
// templates/DashboardTemplate.tsx
import * as React from 'react';
import { Sidebar } from '@/components/Sidebar';
import { Header } from '@/components/Header';
import { Breadcrumb } from '@/patterns/Navigation/Breadcrumb';
import { cn } from '@/utils/cn';

export interface DashboardTemplateProps {
  children: React.ReactNode;
  title?: string;
  breadcrumb?: { label: string; href?: string }[];
  actions?: React.ReactNode;
  className?: string;
}

export function DashboardTemplate({
  children,
  title,
  breadcrumb,
  actions,
  className,
}: DashboardTemplateProps) {
  return (
    <div className=\"min-h-screen bg-background\">
      <div className=\"flex\">
        <Sidebar />
        <div className=\"flex-1\">
          <Header />
          <main className=\"p-6\">
            <div className=\"mb-6\">
              {breadcrumb && (
                <Breadcrumb items={breadcrumb} className=\"mb-4\" />
              )}
              <div className=\"flex items-center justify-between\">
                {title && (
                  <h1 className=\"text-2xl font-bold text-foreground\">
                    {title}
                  </h1>
                )}
                {actions && (
                  <div className=\"flex items-center space-x-2\">
                    {actions}
                  </div>
                )}
              </div>
            </div>
            <div className={cn('space-y-6', className)}>
              {children}
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}
```

### 2. Auth 模板

```typescript
// templates/AuthTemplate.tsx
import * as React from 'react';
import Link from 'next/link';
import { cn } from '@/utils/cn';

export interface AuthTemplateProps {
  children: React.ReactNode;
  title: string;
  description?: string;
  footer?: React.ReactNode;
  className?: string;
}

export function AuthTemplate({
  children,
  title,
  description,
  footer,
  className,
}: AuthTemplateProps) {
  return (
    <div className=\"min-h-screen flex items-center justify-center bg-background py-12 px-4 sm:px-6 lg:px-8\">
      <div className=\"max-w-md w-full space-y-8\">
        <div className=\"text-center\">
          <Link href=\"/\" className=\"text-2xl font-bold text-primary\">
            Logo
          </Link>
          <h2 className=\"mt-6 text-3xl font-extrabold text-foreground\">
            {title}
          </h2>
          {description && (
            <p className=\"mt-2 text-sm text-muted-foreground\">
              {description}
            </p>
          )}
        </div>
        <div className={cn('mt-8 space-y-6', className)}>
          {children}
        </div>
        {footer && (
          <div className=\"mt-6 text-center text-sm text-muted-foreground\">
            {footer}
          </div>
        )}
      </div>
    </div>
  );
}
```

## 🚨 文档和工具

### 1. Storybook 配置

```typescript
// .storybook/main.ts
import type { StorybookConfig } from '@storybook/nextjs';

const config: StorybookConfig = {
  stories: ['../src/**/*.mdx', '../src/**/*.stories.@(js|jsx|ts|tsx)'],
  addons: [
    '@storybook/addon-links',
    '@storybook/addon-essentials',
    '@storybook/addon-interactions',
    '@storybook/addon-themes',
  ],
  framework: {
    name: '@storybook/nextjs',
    options: {},
  },
  docs: {
    autodocs: 'tag',
  },
};

export default config;
```

### 2. 组件文档

```typescript
// components/Button/Button.stories.tsx
import type { Meta, StoryObj } from '@storybook/react';
import { Button } from './Button';

const meta: Meta<typeof Button> = {
  title: 'Components/Button',
  component: Button,
  parameters: {
    docs: {
      description: {
        component: 'Button component with various styles and states.',
      },
    },
  },
  argTypes: {
    variant: {
      control: 'select',
      options: ['default', 'destructive', 'outline', 'secondary', 'ghost', 'link'],
    },
    size: {
      control: 'select',
      options: ['default', 'sm', 'lg', 'icon'],
    },
    loading: {
      control: 'boolean',
    },
    disabled: {
      control: 'boolean',
    },
  },
};

export default meta;
type Story = StoryObj<typeof Button>;

export const Default: Story = {
  args: {
    children: 'Button',
  },
};

export const Variants: Story = {
  render: (args) => (
    <div className=\"flex space-x-2\">
      <Button {...args} variant=\"default\">Default</Button>
      <Button {...args} variant=\"destructive\">Destructive</Button>
      <Button {...args} variant=\"outline\">Outline</Button>
      <Button {...args} variant=\"secondary\">Secondary</Button>
      <Button {...args} variant=\"ghost\">Ghost</Button>
      <Button {...args} variant=\"link\">Link</Button>
    </div>
  ),
};

export const Sizes: Story = {
  render: (args) => (
    <div className=\"flex items-center space-x-2\">
      <Button {...args} size=\"sm\">Small</Button>
      <Button {...args} size=\"default\">Default</Button>
      <Button {...args} size=\"lg\">Large</Button>
      <Button {...args} size=\"icon\">🎨</Button>
    </div>
  ),
};

export const Loading: Story = {
  args: {
    children: 'Loading',
    loading: true,
  },
};
```

## 🎯 总结

Next.js 15 的设计系统为构建一致的、可扩展的用户界面提供了强大的支持。通过合理使用设计令牌、组件库、复合模式和工具链，可以构建出高质量、可维护的Web应用。

### 关键要点：

1. **设计令牌**：颜色、间距、排版、断点等基础设计元素
2. **基础组件**：Button、Input、Card等可重用组件
3. **复合模式**：Form、Table、Navigation等高级模式
4. **专用Hooks**：useTheme、useToast等定制化Hooks
5. **页面模板**：Dashboard、Auth等页面布局模板

### 最佳实践：

- **一致性**：确保所有组件遵循设计规范
- **可访问性**：所有组件都支持无障碍访问
- **可扩展性**：组件应该易于扩展和定制
- **文档完善**：提供详细的使用文档和示例
- **测试覆盖**：确保所有组件都有完整的测试

通过建立完善的设计系统，可以显著提升开发效率和用户体验的一致性。