# 安全最佳实践速查手册

## 输入验证与清理

### 客户端输入验证

```typescript
// 1. 使用 Zod 进行 Schema 验证
import { z } from 'zod';

// 用户注册表单验证
const userRegistrationSchema = z.object({
  username: z.string()
    .min(3, 'Username must be at least 3 characters')
    .max(50, 'Username must be at most 50 characters')
    .regex(/^[a-zA-Z0-9_]+$/, 'Username can only contain letters, numbers, and underscores'),

  email: z.string()
    .email('Invalid email address')
    .min(5, 'Email must be at least 5 characters')
    .max(100, 'Email must be at most 100 characters'),

  password: z.string()
    .min(8, 'Password must be at least 8 characters')
    .max(128, 'Password must be at most 128 characters')
    .regex(/[A-Z]/, 'Password must contain at least one uppercase letter')
    .regex(/[a-z]/, 'Password must contain at least one lowercase letter')
    .regex(/[0-9]/, 'Password must contain at least one number')
    .regex(/[^A-Za-z0-9]/, 'Password must contain at least one special character'),

  age: z.number()
    .min(13, 'Must be at least 13 years old')
    .max(120, 'Age must be less than 120'),

  agreeToTerms: z.boolean()
    .refine(val => val === true, 'You must agree to the terms and conditions')
});

// 联系表单验证
const contactFormSchema = z.object({
  name: z.string()
    .min(2, 'Name must be at least 2 characters')
    .max(100, 'Name must be at most 100 characters')
    .regex(/^[a-zA-Z\s'-]+$/, 'Name can only contain letters, spaces, hyphens, and apostrophes'),

  email: z.string().email('Invalid email address'),

  subject: z.string()
    .min(5, 'Subject must be at least 5 characters')
    .max(200, 'Subject must be at most 200 characters'),

  message: z.string()
    .min(10, 'Message must be at least 10 characters')
    .max(5000, 'Message must be at most 5000 characters'),

  phone: z.string()
    .optional()
    .refine(
      (phone) => !phone || /^\+?[\d\s-()]+$/.test(phone),
      'Invalid phone number format'
    )
});

// React Hook Form 集成
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

function RegistrationForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
    setError
  } = useForm({
    resolver: zodResolver(userRegistrationSchema)
  });

  const onSubmit = async (data) => {
    try {
      // 提交表单
      await submitRegistration(data);
    } catch (error) {
      if (error.response?.data?.errors) {
        // 处理服务器端验证错误
        error.response.data.errors.forEach(err => {
          setError(err.field, { message: err.message });
        });
      }
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('username')} placeholder="Username" />
      {errors.username && <span className="error">{errors.username.message}</span>}

      <input type="email" {...register('email')} placeholder="Email" />
      {errors.email && <span className="error">{errors.email.message}</span>}

      <input type="password" {...register('password')} placeholder="Password" />
      {errors.password && <span className="error">{errors.password.message}</span>}

      <input type="number" {...register('age', { valueAsNumber: true })} placeholder="Age" />
      {errors.age && <span className="error">{errors.age.message}</span>}

      <label>
        <input type="checkbox" {...register('agreeToTerms')} />
        I agree to the terms and conditions
      </label>
      {errors.agreeToTerms && <span className="error">{errors.agreeToTerms.message}</span>}

      <button type="submit">Register</button>
    </form>
  );
}
```

### 自定义验证器

```typescript
// 1. 创建自定义验证器
class InputValidator {
  static sanitizeString(input: string): string {
    return input
      .trim()
      .replace(/[<>]/g, '') // 移除潜在的 HTML 标签
      .replace(/javascript:/gi, '') // 移除 javascript: 协议
      .replace(/on\w+\s*=/gi, ''); // 移除事件处理器
  }

  static validateEmail(email: string): boolean {
    const emailRegex = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    return emailRegex.test(email);
  }

  static validatePasswordStrength(password: string): {
    isValid: boolean;
    score: number;
    feedback: string[];
  } {
    const feedback = [];
    let score = 0;

    if (password.length >= 8) score += 1;
    else feedback.push('Password must be at least 8 characters long');

    if (password.length >= 12) score += 1;
    else feedback.push('Consider using a longer password (12+ characters)');

    if (/[A-Z]/.test(password)) score += 1;
    else feedback.push('Include uppercase letters');

    if (/[a-z]/.test(password)) score += 1;
    else feedback.push('Include lowercase letters');

    if (/[0-9]/.test(password)) score += 1;
    else feedback.push('Include numbers');

    if (/[^A-Za-z0-9]/.test(password)) score += 1;
    else feedback.push('Include special characters');

    return {
      isValid: score >= 4,
      score,
      feedback
    };
  }

  static validateURL(url: string): boolean {
    try {
      const urlObj = new URL(url);
      return ['http:', 'https:'].includes(urlObj.protocol);
    } catch {
      return false;
    }
  }

  static sanitizeHTML(html: string): string {
    // 使用 DOMPurify 进行 HTML 清理
    if (typeof DOMPurify !== 'undefined') {
      return DOMPurify.sanitize(html);
    }

    // 基础 HTML 清理（DOMPurify 的简化版本）
    return html
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/<iframe\b[^<]*(?:(?!<\/iframe>)<[^<]*)*<\/iframe>/gi, '')
      .replace(/on\w+="[^"]*"/gi, '')
      .replace(/on\w+='[^']*'/gi, '')
      .replace(/on\w+=[^\s>]+/gi, '');
  }

  static validateFileSize(file: File, maxSize: number = 5 * 1024 * 1024): boolean {
    return file.size <= maxSize;
  }

  static validateFileType(file: File, allowedTypes: string[]): boolean {
    return allowedTypes.includes(file.type);
  }

  static validatePhoneNumber(phone: string): boolean {
    const phoneRegex = /^\+?[\d\s\-\(\)]+$/;
    return phoneRegex.test(phone) && phone.replace(/\D/g, '').length >= 10;
  }
}

// 2. 文件上传验证
interface FileUploadOptions {
  maxSize?: number; // in bytes
  allowedTypes?: string[];
  allowedExtensions?: string[];
  maxFiles?: number;
}

class FileUploadValidator {
  static async validateFile(
    file: File,
    options: FileUploadOptions = {}
  ): Promise<{ isValid: boolean; errors: string[] }> {
    const errors: string[] = [];
    const {
      maxSize = 5 * 1024 * 1024, // 5MB default
      allowedTypes = [],
      allowedExtensions = [],
    } = options;

    // 检查文件大小
    if (file.size > maxSize) {
      errors.push(`File size exceeds maximum allowed size of ${maxSize / 1024 / 1024}MB`);
    }

    // 检查文件类型
    if (allowedTypes.length > 0 && !allowedTypes.includes(file.type)) {
      errors.push(`File type ${file.type} is not allowed`);
    }

    // 检查文件扩展名
    if (allowedExtensions.length > 0) {
      const extension = file.name.split('.').pop()?.toLowerCase();
      if (!extension || !allowedExtensions.includes(extension)) {
        errors.push(`File extension .${extension} is not allowed`);
      }
    }

    // 检查文件内容（如果支持）
    if (file.type.startsWith('image/')) {
      try {
        await this.validateImageFile(file);
      } catch (error) {
        errors.push(error.message);
      }
    }

    return {
      isValid: errors.length === 0,
      errors
    };
  }

  private static async validateImageFile(file: File): Promise<void> {
    return new Promise((resolve, reject) => {
      const img = new Image();
      const url = URL.createObjectURL(file);

      img.onload = () => {
        URL.revokeObjectURL(url);

        // 检查图片尺寸
        if (img.width > 4096 || img.height > 4096) {
          reject(new Error('Image dimensions exceed maximum allowed size (4096x4096)'));
          return;
        }

        // 检查宽高比
        const aspectRatio = img.width / img.height;
        if (aspectRatio > 10 || aspectRatio < 0.1) {
          reject(new Error('Image aspect ratio is too extreme'));
          return;
        }

        resolve();
      };

      img.onerror = () => {
        URL.revokeObjectURL(url);
        reject(new Error('Invalid image file'));
      };

      img.src = url;
    });
  }

  static generateSafeFileName(originalName: string): string {
    const extension = originalName.split('.').pop();
    const baseName = originalName.substring(0, originalName.lastIndexOf('.'));

    // 移除特殊字符，只保留字母、数字、连字符和下划线
    const sanitizedName = baseName
      .toLowerCase()
      .replace(/[^a-z0-9\s\-_]/g, '')
      .replace(/\s+/g, '-')
      .substring(0, 50); // 限制长度

    return `${sanitizedName}-${Date.now()}.${extension}`;
  }
}

// 3. 表单验证中间件
class FormValidator {
  static validateForm<T>(
    schema: z.ZodSchema<T>,
    data: unknown
  ): { success: true; data: T } | { success: false; errors: z.ZodError } {
    const result = schema.safeParse(data);

    if (result.success) {
      return { success: true, data: result.data };
    } else {
      return { success: false, errors: result.error };
    }
  }

  static createFormHandler<T>(
    schema: z.ZodSchema<T>,
    handler: (data: T) => Promise<any>
  ) {
    return async (formData: FormData) => {
      // 转换 FormData 为对象
      const data: Record<string, any> = {};
      for (const [key, value] of formData.entries()) {
        data[key] = value;
      }

      // 验证数据
      const validation = this.validateForm(schema, data);

      if (!validation.success) {
        return {
          success: false,
          errors: validation.errors.flatten().fieldErrors
        };
      }

      try {
        const result = await handler(validation.data);
        return { success: true, data: result };
      } catch (error) {
        return {
          success: false,
          errors: { general: [error.message] }
        };
      }
    };
  }
}
```

### 服务端输入验证

```typescript
// 1. API 路由验证
// app/api/auth/register/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const registrationSchema = z.object({
  username: z.string().min(3).max(50),
  email: z.string().email(),
  password: z.string().min(8),
  firstName: z.string().min(1).max(50),
  lastName: z.string().min(1).max(50),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // 验证输入
    const validatedData = registrationSchema.parse(body);

    // 额外的业务逻辑验证
    const existingUser = await findUserByEmail(validatedData.email);
    if (existingUser) {
      return NextResponse.json(
        { error: 'Email already registered' },
        { status: 400 }
      );
    }

    const existingUsername = await findUserByUsername(validatedData.username);
    if (existingUsername) {
      return NextResponse.json(
        { error: 'Username already taken' },
        { status: 400 }
      );
    }

    // 创建用户
    const user = await createUser(validatedData);

    return NextResponse.json({
      success: true,
      user: {
        id: user.id,
        username: user.username,
        email: user.email
      }
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: 'Validation failed', details: error.errors },
        { status: 400 }
      );
    }

    console.error('Registration error:', error);
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

// 2. 验证中间件
// lib/validation-middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { ZodSchema } from 'zod';

export function withValidation<T>(
  schema: ZodSchema<T>,
  handler: (req: NextRequest, data: T) => Promise<NextResponse>
) {
  return async (req: NextRequest): Promise<NextResponse> => {
    try {
      const body = await req.json();
      const validatedData = schema.parse(body);
      return await handler(req, validatedData);
    } catch (error) {
      if (error instanceof z.ZodError) {
        return NextResponse.json(
          {
            error: 'Validation failed',
            details: error.errors.map(err => ({
              field: err.path.join('.'),
              message: err.message
            }))
          },
          { status: 400 }
        );
      }

      return NextResponse.json(
        { error: 'Internal server error' },
        { status: 500 }
      );
    }
  };
}

// 使用示例
// app/api/users/route.ts
import { withValidation } from '@/lib/validation-middleware';

const createUserSchema = z.object({
  name: z.string().min(1).max(100),
  email: z.string().email(),
  role: z.enum(['user', 'admin']).default('user'),
});

async function createUserHandler(req: NextRequest, data: any) {
  const user = await User.create(data);
  return NextResponse.json(user, { status: 201 });
}

export const POST = withValidation(createUserSchema, createUserHandler);

// 3. 参数验证
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  const { id } = await params;

  // 验证 ID 格式
  if (!/^[0-9a-fA-F]{24}$/.test(id)) {
    return NextResponse.json(
      { error: 'Invalid user ID format' },
      { status: 400 }
    );
  }

  // 查询用户
  const user = await User.findById(id);
  if (!user) {
    return NextResponse.json(
      { error: 'User not found' },
      { status: 404 }
    );
  }

  return NextResponse.json(user);
}
```

## XSS 防护

### 内容安全策略 (CSP)

```typescript
// next.config.js
const securityHeaders = [
  {
    key: 'Content-Security-Policy',
    value: [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://cdn.example.com",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "img-src 'self' data: https://cdn.example.com https://example.com",
      "font-src 'self' https://fonts.gstatic.com",
      "connect-src 'self' https://api.example.com",
      "frame-src 'none'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "frame-ancestors 'none'",
      "block-all-mixed-content",
      "upgrade-insecure-requests"
    ].join('; ')
  },
  {
    key: 'X-Content-Type-Options',
    value: 'nosniff'
  },
  {
    key: 'X-Frame-Options',
    value: 'DENY'
  },
  {
    key: 'X-XSS-Protection',
    value: '1; mode=block'
  },
  {
    key: 'Referrer-Policy',
    value: 'strict-origin-when-cross-origin'
  },
  {
    key: 'Permissions-Policy',
    value: 'camera=(), microphone=(), geolocation=()'
  }
];

module.exports = {
  async headers() {
    return [
      {
        source: '/:path*',
        headers: securityHeaders
      }
    ];
  }
};
```

### 输出编码

```typescript
// lib/sanitize.ts
import DOMPurify from 'dompurify';

class ContentSanitizer {
  // HTML 清理
  static sanitizeHTML(html: string, options?: DOMPurify.Config): string {
    const defaultOptions: DOMPurify.Config = {
      ALLOWED_TAGS: [
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'p', 'br', 'hr',
        'ul', 'ol', 'li',
        'strong', 'em', 'b', 'i',
        'a', 'img',
        'blockquote', 'code', 'pre',
        'div', 'span'
      ],
      ALLOWED_ATTR: [
        'href', 'src', 'alt', 'title',
        'class', 'id', 'style',
        'target', 'rel'
      ],
      FORBID_ATTR: ['onclick', 'onload', 'onerror', 'onmouseover'],
      FORCE_BODY: true,
      ...options
    };

    return DOMPurify.sanitize(html, defaultOptions);
  }

  // URL 清理
  static sanitizeURL(url: string): string {
    try {
      const parsedUrl = new URL(url);

      // 只允许特定协议
      const allowedProtocols = ['http:', 'https:', 'mailto:', 'tel:'];
      if (!allowedProtocols.includes(parsedUrl.protocol)) {
        return '#';
      }

      // 移除危险字符
      parsedUrl.hash = '';
      parsedUrl.username = '';
      parsedUrl.password = '';

      return parsedUrl.toString();
    } catch {
      return '#';
    }
  }

  // CSS 清理
  static sanitizeCSS(css: string): string {
    // 移除危险的 CSS 属性和值
    const dangerousPatterns = [
      /expression\s*\(/i,
      /javascript\s*:/i,
      /behavior\s*:/i,
      /binding\s*:/i,
      /include-source\s*:/i
    ];

    let sanitizedCSS = css;
    dangerousPatterns.forEach(pattern => {
      sanitizedCSS = sanitizedCSS.replace(pattern, '');
    });

    return sanitizedCSS;
  }

  // 属性清理
  static sanitizeAttribute(value: string, attributeName: string): string {
    switch (attributeName) {
      case 'href':
      case 'src':
        return this.sanitizeURL(value);

      case 'style':
        return this.sanitizeCSS(value);

      case 'class':
      case 'id':
        // 只允许字母、数字、连字符和下划线
        return value.replace(/[^a-zA-Z0-9\-_]/g, '');

      default:
        // 移除引号和 HTML 特殊字符
        return value
          .replace(/["']/g, '')
          .replace(/[<>]/g, '');
    }
  }
}

// React 组件中使用
import React from 'react';
import { ContentSanitizer } from '@/lib/sanitize';

interface SafeHTMLProps {
  html: string;
  tagName?: keyof JSX.IntrinsicElements;
  className?: string;
}

const SafeHTML: React.FC<SafeHTMLProps> = ({
  html,
  tagName = 'div',
  className
}) => {
  const sanitizedHTML = ContentSanitizer.sanitizeHTML(html);

  return React.createElement(tagName, {
    dangerouslySetInnerHTML: { __html: sanitizedHTML },
    className
  });
};

// 使用示例
function UserComment({ comment }: { comment: { content: string } }) {
  return (
    <div className="comment">
      <SafeHTML
        html={comment.content}
        tagName="div"
        className="comment-content"
      />
    </div>
  );
}
```

### 输入过滤

```typescript
// lib/input-filter.ts
class InputFilter {
  // 过滤用户输入
  static filterInput(input: string, options: {
    allowHTML?: boolean;
    allowScripts?: boolean;
    maxLength?: number;
  } = {}): string {
    const {
      allowHTML = false,
      allowScripts = false,
      maxLength = 10000
    } = options;

    let filtered = input.substring(0, maxLength);

    if (!allowHTML) {
      filtered = this.stripHTML(filtered);
    }

    if (!allowScripts) {
      filtered = this.stripScripts(filtered);
    }

    return filtered;
  }

  // 移除 HTML 标签
  private static stripHTML(html: string): string {
    return html
      .replace(/<[^>]*>/g, '')
      .replace(/&lt;/g, '<')
      .replace(/&gt;/g, '>')
      .replace(/&amp;/g, '&');
  }

  // 移除脚本和事件处理器
  private static stripScripts(html: string): string {
    return html
      .replace(/<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>/gi, '')
      .replace(/on\w+\s*=\s*"[^"]*"/gi, '')
      .replace(/on\w+\s*=\s*'[^']*'/gi, '')
      .replace(/on\w+\s*=\s*[^"'][^\s>]*/gi, '')
      .replace(/javascript\s*:/gi, '')
      .replace(/vbscript\s*:/gi, '')
      .replace(/data\s*:\s*text\/html/gi, '');
  }

  // 过滤查询参数
  static filterQueryParams(params: Record<string, any>): Record<string, any> {
    const filtered: Record<string, any> = {};

    for (const [key, value] of Object.entries(params)) {
      // 过滤键名
      const filteredKey = key.replace(/[^\w\-]/g, '');

      if (filteredKey) {
        filtered[filteredKey] = this.filterValue(value);
      }
    }

    return filtered;
  }

  // 递归过滤值
  private static filterValue(value: any): any {
    if (typeof value === 'string') {
      return this.filterInput(value);
    } else if (Array.isArray(value)) {
      return value.map(item => this.filterValue(item));
    } else if (typeof value === 'object' && value !== null) {
      const filtered: Record<string, any> = {};
      for (const [key, val] of Object.entries(value)) {
        const filteredKey = key.replace(/[^\w\-]/g, '');
        if (filteredKey) {
          filtered[filteredKey] = this.filterValue(val);
        }
      }
      return filtered;
    }
    return value;
  }

  // 过滤文件名
  static filterFileName(filename: string): string {
    return filename
      .replace(/[^\w\-\.]/g, '_')
      .replace(/\.\./g, '')
      .replace(/^\/+/, '')
      .replace(/\/+$/, '');
  }
}

// 中间件示例
// lib/middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { InputFilter } from './input-filter';

export async function securityMiddleware(req: NextRequest) {
  // 过滤查询参数
  const url = new URL(req.url);
  const filteredParams = InputFilter.filterQueryParams(
    Object.fromEntries(url.searchParams)
  );

  // 更新 URL
  url.search = new URLSearchParams(filteredParams).toString();

  // 如果 URL 发生变化，重定向
  if (url.toString() !== req.url) {
    return NextResponse.redirect(url);
  }

  return NextResponse.next();
}
```

## CSRF 防护

### CSRF Token 实现

```typescript
// lib/csrf.ts
import { NextRequest, NextResponse } from 'next/server';
import { randomBytes, createHash, timingSafeEqual } from 'crypto';

class CSRFProtection {
  // 生成 CSRF Token
  static generateToken(): string {
    return randomBytes(32).toString('hex');
  }

  // 验证 CSRF Token
  static validateToken(token: string, sessionToken: string): boolean {
    try {
      const tokenBuffer = Buffer.from(token, 'hex');
      const sessionBuffer = Buffer.from(sessionToken, 'hex');

      return tokenBuffer.length === sessionBuffer.length &&
             timingSafeEqual(tokenBuffer, sessionBuffer);
    } catch {
      return false;
    }
  }

  // 创建 CSRF Token 的哈希值
  static createTokenHash(token: string, secret: string): string {
    return createHash('sha256')
      .update(token + secret)
      .digest('hex');
  }

  // 中间件
  static middleware() {
    return async (req: NextRequest): Promise<NextResponse | null> => {
      // 对于 GET、HEAD、OPTIONS 请求，不需要 CSRF 验证
      if (['GET', 'HEAD', 'OPTIONS'].includes(req.method)) {
        return null;
      }

      // 从 cookie 获取 CSRF token
      const csrfCookie = req.cookies.get('csrf-token');
      if (!csrfCookie) {
        return NextResponse.json(
          { error: 'Missing CSRF token' },
          { status: 403 }
        );
      }

      // 从 header 获取 CSRF token
      const csrfHeader = req.headers.get('x-csrf-token');
      if (!csrfHeader) {
        return NextResponse.json(
          { error: 'Missing CSRF header' },
          { status: 403 }
        );
      }

      // 验证 token
      if (!this.validateToken(csrfHeader, csrfCookie.value)) {
        return NextResponse.json(
          { error: 'Invalid CSRF token' },
          { status: 403 }
        );
      }

      return null;
    };
  }
}

// 在 API 路由中使用
// app/api/users/route.ts
import { CSRFProtection } from '@/lib/csrf';

export async function POST(req: NextRequest) {
  // CSRF 验证
  const csrfResult = CSRFProtection.middleware()(req);
  if (csrfResult) {
    return csrfResult;
  }

  // 处理请求
  // ...
}

// 在客户端设置 CSRF Token
// lib/csrf-client.ts
class CSRFClient {
  private static instance: CSRFClient;
  private token: string | null = null;

  static getInstance(): CSRFClient {
    if (!CSRFClient.instance) {
      CSRFClient.instance = new CSRFClient();
    }
    return CSRFClient.instance;
  }

  async initialize(): Promise<void> {
    if (this.token) return;

    try {
      const response = await fetch('/api/csrf-token', {
        method: 'GET',
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to fetch CSRF token');
      }

      const data = await response.json();
      this.token = data.token;
    } catch (error) {
      console.error('CSRF initialization failed:', error);
    }
  }

  getToken(): string | null {
    return this.token;
  }

  async fetchWithCSRF(
    url: string,
    options: RequestInit = {}
  ): Promise<Response> {
    await this.initialize();

    const headers = new Headers(options.headers || {});
    if (this.token) {
      headers.set('x-csrf-token', this.token);
    }

    return fetch(url, {
      ...options,
      headers,
      credentials: 'include'
    });
  }
}

// React Hook 使用
function useCSRF() {
  const [csrfToken, setCsrfToken] = useState<string | null>(null);

  useEffect(() => {
    const csrfClient = CSRFClient.getInstance();
    csrfClient.initialize().then(() => {
      setCsrfToken(csrfClient.getToken());
    });
  }, []);

  const fetchWithCSRF = useCallback(async (
    url: string,
    options: RequestInit = {}
  ) => {
    const csrfClient = CSRFClient.getInstance();
    return csrfClient.fetchWithCSRF(url, options);
  }, []);

  return { csrfToken, fetchWithCSRF };
}

// 使用示例
function UserProfile() {
  const { csrfToken, fetchWithCSRF } = useCSRF();

  const updateProfile = async (data: any) => {
    const response = await fetchWithCSRF('/api/user/profile', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });

    return response.json();
  };

  return (
    <form onSubmit={(e) => {
      e.preventDefault();
      const formData = new FormData(e.target as HTMLFormElement);
      updateProfile(Object.fromEntries(formData));
    }}>
      {/* 表单内容 */}
      <input type="hidden" name="csrf_token" value={csrfToken || ''} />
    </form>
  );
}
```

### SameSite Cookie 配置

```typescript
// lib/auth.ts
import { serialize } from 'cookie';

class AuthManager {
  // 设置认证 Cookie
  static setAuthCookie(
    response: NextResponse,
    token: string,
    options: {
      httpOnly?: boolean;
      secure?: boolean;
      sameSite?: 'strict' | 'lax' | 'none';
      domain?: string;
      path?: string;
      maxAge?: number;
    } = {}
  ): void {
    const {
      httpOnly = true,
      secure = process.env.NODE_ENV === 'production',
      sameSite = 'lax',
      domain,
      path = '/',
      maxAge = 7 * 24 * 60 * 60 // 7 days
    } = options;

    const authCookie = serialize('auth-token', token, {
      httpOnly,
      secure,
      sameSite,
      domain,
      path,
      maxAge,
    });

    const csrfCookie = serialize('csrf-token', CSRFProtection.generateToken(), {
      httpOnly: false, // JavaScript 需要访问
      secure,
      sameSite,
      domain,
      path,
      maxAge,
    });

    response.headers.set('Set-Cookie', `${authCookie}, ${csrfCookie}`);
  }

  // 清除认证 Cookie
  static clearAuthCookie(response: NextResponse): void {
    const authCookie = serialize('auth-token', '', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: 0,
    });

    const csrfCookie = serialize('csrf-token', '', {
      httpOnly: false,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      path: '/',
      maxAge: 0,
    });

    response.headers.set('Set-Cookie', `${authCookie}, ${csrfCookie}`);
  }
}

// 在登录 API 中使用
// app/api/auth/login/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { AuthManager } from '@/lib/auth';

export async function POST(req: NextRequest) {
  try {
    const { email, password } = await req.json();

    // 验证用户凭据
    const user = await authenticateUser(email, password);
    if (!user) {
      return NextResponse.json(
        { error: 'Invalid credentials' },
        { status: 401 }
      );
    }

    // 生成 JWT token
    const token = generateJWT(user);

    // 创建响应
    const response = NextResponse.json({
      success: true,
      user: {
        id: user.id,
        email: user.email,
        name: user.name
      }
    });

    // 设置认证 Cookie
    AuthManager.setAuthCookie(response, token);

    return response;
  } catch (error) {
    return NextResponse.json(
      { error: 'Login failed' },
      { status: 500 }
    );
  }
}
```

## 认证与授权

### JWT 实现

```typescript
// lib/jwt.ts
import jwt from 'jsonwebtoken';

interface JWTPayload {
  userId: string;
  email: string;
  role: string;
  iat: number;
  exp: number;
}

class JWTManager {
  private static readonly SECRET = process.env.JWT_SECRET || 'your-secret-key';
  private static readonly REFRESH_SECRET = process.env.JWT_REFRESH_SECRET || 'your-refresh-secret';
  private static readonly ACCESS_TOKEN_EXPIRES_IN = '15m';
  private static readonly REFRESH_TOKEN_EXPIRES_IN = '7d';

  // 生成访问令牌
  static generateAccessToken(payload: Omit<JWTPayload, 'iat' | 'exp'>): string {
    return jwt.sign(payload, this.SECRET, {
      expiresIn: this.ACCESS_TOKEN_EXPIRES_IN
    });
  }

  // 生成刷新令牌
  static generateRefreshToken(userId: string): string {
    return jwt.sign({ userId }, this.REFRESH_SECRET, {
      expiresIn: this.REFRESH_TOKEN_EXPIRES_IN
    });
  }

  // 验证访问令牌
  static verifyAccessToken(token: string): JWTPayload | null {
    try {
      return jwt.verify(token, this.SECRET) as JWTPayload;
    } catch (error) {
      return null;
    }
  }

  // 验证刷新令牌
  static verifyRefreshToken(token: string): { userId: string } | null {
    try {
      return jwt.verify(token, this.REFRESH_SECRET) as { userId: string };
    } catch (error) {
      return null;
    }
  }

  // 从请求头获取令牌
  static getTokenFromHeaders(headers: Headers): string | null {
    const authHeader = headers.get('authorization');
    if (!authHeader?.startsWith('Bearer ')) {
      return null;
    }
    return authHeader.substring(7);
  }

  // 从 Cookie 获取令牌
  static getTokenFromCookie(request: NextRequest): string | null {
    return request.cookies.get('auth-token')?.value || null;
  }
}

// 认证中间件
// lib/auth-middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { JWTManager } from './jwt';

interface AuthUser {
  userId: string;
  email: string;
  role: string;
}

export async function authenticateRequest(
  req: NextRequest
): Promise<{ user: AuthUser } | NextResponse> {
  // 从 Cookie 或 Header 获取令牌
  const token = JWTManager.getTokenFromCookie(req) ||
               JWTManager.getTokenFromHeaders(req.headers);

  if (!token) {
    return NextResponse.json(
      { error: 'Authentication required' },
      { status: 401 }
    );
  }

  // 验证令牌
  const payload = JWTManager.verifyAccessToken(token);
  if (!payload) {
    return NextResponse.json(
      { error: 'Invalid or expired token' },
      { status: 401 }
    );
  }

  return {
    user: {
      userId: payload.userId,
      email: payload.email,
      role: payload.role
    }
  };
}

// 角色授权中间件
export function authorizeRoles(allowedRoles: string[]) {
  return async (req: NextRequest): Promise<NextResponse | null> => {
    const authResult = await authenticateRequest(req);

    if (authResult instanceof NextResponse) {
      return authResult;
    }

    const { user } = authResult;

    if (!allowedRoles.includes(user.role)) {
      return NextResponse.json(
        { error: 'Insufficient permissions' },
        { status: 403 }
      );
    }

    return null;
  };
}

// 使用示例
// app/api/admin/users/route.ts
import { authorizeRoles } from '@/lib/auth-middleware';

export async function GET(req: NextRequest) {
  // 检查管理员权限
  const authResult = await authorizeRoles(['admin'])(req);
  if (authResult) {
    return authResult;
  }

  // 获取用户列表
  const users = await User.find({});
  return NextResponse.json(users);
}
```

### 权限控制

```typescript
// lib/permissions.ts
interface Permission {
  resource: string;
  action: 'create' | 'read' | 'update' | 'delete';
  conditions?: Record<string, any>;
}

interface Role {
  name: string;
  permissions: Permission[];
}

class PermissionManager {
  private static roles: Map<string, Role> = new Map();

  // 初始化角色和权限
  static initialize(): void {
    // 超级管理员
    this.roles.set('superadmin', {
      name: 'Super Admin',
      permissions: [
        { resource: '*', action: 'create' },
        { resource: '*', action: 'read' },
        { resource: '*', action: 'update' },
        { resource: '*', action: 'delete' }
      ]
    });

    // 管理员
    this.roles.set('admin', {
      name: 'Admin',
      permissions: [
        { resource: 'users', action: 'read' },
        { resource: 'users', action: 'update', conditions: { own: true } },
        { resource: 'posts', action: 'create' },
        { resource: 'posts', action: 'read' },
        { resource: 'posts', action: 'update', conditions: { own: true } },
        { resource: 'posts', action: 'delete', conditions: { own: true } }
      ]
    });

    // 编辑者
    this.roles.set('editor', {
      name: 'Editor',
      permissions: [
        { resource: 'posts', action: 'create' },
        { resource: 'posts', action: 'read' },
        { resource: 'posts', action: 'update', conditions: { own: true } }
      ]
    });

    // 普通用户
    this.roles.set('user', {
      name: 'User',
      permissions: [
        { resource: 'profile', action: 'read', conditions: { own: true } },
        { resource: 'profile', action: 'update', conditions: { own: true } }
      ]
    });
  }

  // 检查权限
  static async hasPermission(
    userId: string,
    resource: string,
    action: string,
    context?: Record<string, any>
  ): Promise<boolean> {
    const user = await User.findById(userId).populate('role');
    if (!user) return false;

    const role = this.roles.get(user.role.name);
    if (!role) return false;

    // 检查每个权限
    for (const permission of role.permissions) {
      // 通配符资源
      if (permission.resource === '*' || permission.resource === resource) {
        if (permission.action === action) {
          // 检查条件
          if (permission.conditions) {
            return this.checkConditions(permission.conditions, context);
          }
          return true;
        }
      }
    }

    return false;
  }

  // 检查权限条件
  private static checkConditions(
    conditions: Record<string, any>,
    context: Record<string, any>
  ): boolean {
    for (const [key, value] of Object.entries(conditions)) {
      switch (key) {
        case 'own':
          if (context.userId !== context.resourceOwnerId) {
            return false;
          }
          break;

        case 'department':
          if (context.userDepartment !== context.resourceDepartment) {
            return false;
          }
          break;

        // 添加更多条件检查
        default:
          if (context[key] !== value) {
            return false;
          }
      }
    }
    return true;
  }

  // 获取用户权限
  static async getUserPermissions(userId: string): Promise<string[]> {
    const user = await User.findById(userId).populate('role');
    if (!user) return [];

    const role = this.roles.get(user.role.name);
    if (!role) return [];

    return role.permissions.map(p => `${p.resource}:${p.action}`);
  }
}

// React Hook 使用
function usePermission() {
  const { user } = useAuth();

  const checkPermission = useCallback(async (
    resource: string,
    action: string,
    context?: Record<string, any>
  ): Promise<boolean> => {
    if (!user) return false;
    return PermissionManager.hasPermission(user.id, resource, action, context);
  }, [user]);

  return { checkPermission };
}

// 使用示例
function PostActions({ post }: { post: Post }) {
  const { user } = useAuth();
  const { checkPermission } = usePermission();
  const [canEdit, setCanEdit] = useState(false);
  const [canDelete, setCanDelete] = useState(false);

  useEffect(() => {
    const checkPermissions = async () => {
      const editPermission = await checkPermission('posts', 'update', {
        userId: user?.id,
        resourceOwnerId: post.authorId
      });

      const deletePermission = await checkPermission('posts', 'delete', {
        userId: user?.id,
        resourceOwnerId: post.authorId
      });

      setCanEdit(editPermission);
      setCanDelete(deletePermission);
    };

    checkPermissions();
  }, [user, post, checkPermission]);

  return (
    <div className="post-actions">
      {canEdit && (
        <button onClick={() => editPost(post)}>Edit</button>
      )}
      {canDelete && (
        <button onClick={() => deletePost(post)}>Delete</button>
      )}
    </div>
  );
}
```

## 数据安全

### 敏感数据处理

```typescript
// lib/data-security.ts
import crypto from 'crypto';

class DataSecurity {
  private static readonly ENCRYPTION_KEY = process.env.ENCRYPTION_KEY;
  private static readonly ENCRYPTION_IV = crypto.randomBytes(16);

  // 加密数据
  static encrypt(text: string): string {
    if (!this.ENCRYPTION_KEY) {
      throw new Error('Encryption key not configured');
    }

    const cipher = crypto.createCipheriv(
      'aes-256-cbc',
      Buffer.from(this.ENCRYPTION_KEY, 'hex'),
      this.ENCRYPTION_IV
    );

    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    return `${this.ENCRYPTION_IV.toString('hex')}:${encrypted}`;
  }

  // 解密数据
  static decrypt(encryptedText: string): string {
    if (!this.ENCRYPTION_KEY) {
      throw new Error('Encryption key not configured');
    }

    const [ivHex, encrypted] = encryptedText.split(':');
    const iv = Buffer.from(ivHex, 'hex');

    const decipher = crypto.createDecipheriv(
      'aes-256-cbc',
      Buffer.from(this.ENCRYPTION_KEY, 'hex'),
      iv
    );

    let decrypted = decipher.update(encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }

  // 生成哈希
  static hash(text: string, salt?: string): { hash: string; salt: string } {
    const generatedSalt = salt || crypto.randomBytes(16).toString('hex');
    const hash = crypto
      .pbkdf2Sync(text, generatedSalt, 10000, 64, 'sha512')
      .toString('hex');

    return { hash, salt: generatedSalt };
  }

  // 验证哈希
  static verifyHash(text: string, hash: string, salt: string): boolean {
    const { hash: computedHash } = this.hash(text, salt);
    return computedHash === hash;
  }

  // 生成安全随机字符串
  static generateRandomString(length: number = 32): string {
    return crypto
      .randomBytes(length)
      .toString('hex')
      .substring(0, length);
  }

  // 屏蔽敏感信息
  static maskSensitiveData(data: any, sensitiveFields: string[] = []): any {
    if (typeof data !== 'object' || data === null) {
      return data;
    }

    if (Array.isArray(data)) {
      return data.map(item => this.maskSensitiveData(item, sensitiveFields));
    }

    const masked: any = {};
    for (const [key, value] of Object.entries(data)) {
      if (sensitiveFields.includes(key)) {
        masked[key] = this.maskValue(value);
      } else {
        masked[key] = this.maskSensitiveData(value, sensitiveFields);
      }
    }

    return masked;
  }

  // 屏蔽值
  private static maskValue(value: any): any {
    if (typeof value === 'string') {
      if (value.length <= 8) {
        return '*'.repeat(value.length);
      }
      return value.substring(0, 4) + '*'.repeat(value.length - 8) + value.substring(value.length - 4);
    }
    return '***';
  }

  // 安全的 JSON 序列化
  static safeStringify(obj: any, sensitiveFields: string[] = []): string {
    const masked = this.maskSensitiveData(obj, sensitiveFields);
    return JSON.stringify(masked);
  }
}

// 数据脱敏中间件
// lib/data-sanitization-middleware.ts
import { NextRequest, NextResponse } from 'next/server';

class DataSanitization {
  private static sensitiveFields = [
    'password',
    'creditCard',
    'ssn',
    'phoneNumber',
    'email',
    'address'
  ];

  // 响应数据脱敏
  static sanitizeResponse(data: any): any {
    return DataSecurity.maskSensitiveData(data, this.sensitiveFields);
  }

  // 请求日志脱敏
  static sanitizeLogData(data: any): any {
    const logSensitiveFields = [
      ...this.sensitiveFields,
      'token',
      'secret',
      'key',
      'authorization'
    ];

    return DataSecurity.maskSensitiveData(data, logSensitiveFields);
  }

  // 中间件
  static middleware() {
    return async (req: NextRequest): Promise<NextResponse> => {
      // 克隆响应以便修改
      const response = NextResponse.next();

      // 监听响应完成事件
      response.cookies.get('test'); // 触发 cookie 处理

      return response;
    };
  }
}

// 使用示例
// app/api/users/route.ts
import { DataSanitization } from '@/lib/data-sanitization-middleware';

export async function GET(req: NextRequest) {
  const users = await User.find({});

  // 脱敏敏感数据
  const sanitizedUsers = DataSanitization.sanitizeResponse(users);

  return NextResponse.json(sanitizedUsers);
}
```

### 数据库安全

```typescript
// lib/database-security.ts
import { PrismaClient } from '@prisma/client';

class DatabaseSecurity {
  private static prisma = new PrismaClient({
    log: ['query', 'info', 'warn', 'error'],
  });

  // 安全查询
  static async safeQuery<T>(
    queryFn: () => Promise<T>,
    options: {
      maxRows?: number;
      timeout?: number;
    } = {}
  ): Promise<T> {
    const { maxRows = 1000, timeout = 5000 } = options;

    // 设置查询超时
    const timeoutPromise = new Promise<never>((_, reject) => {
      setTimeout(() => reject(new Error('Query timeout')), timeout);
    });

    try {
      const result = await Promise.race([
        queryFn(),
        timeoutPromise
      ]);

      // 检查结果行数
      if (Array.isArray(result) && result.length > maxRows) {
        throw new Error(`Query returned too many rows: ${result.length}`);
      }

      return result;
    } catch (error) {
      console.error('Database query error:', error);
      throw new Error('Database operation failed');
    }
  }

  // 参数化查询
  static async parameterizedQuery(
    sql: string,
    params: any[]
  ): Promise<any> {
    // 使用 Prisma 的查询构建器或参数化查询
    return this.prisma.$queryRawUnsafe(sql, ...params);
  }

  // SQL 注入防护
  static sanitizeSQLInput(input: string): string {
    return input
      .replace(/'/g, "''")
      .replace(/;/g, '')
      .replace(/--/g, '')
      .replace(/\/\*[\s\S]*?\*\//g, '')
      .replace(/\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b/gi, '');
  }

  // 连接池安全配置
  static configureConnectionPool() {
    return new PrismaClient({
      log: ['query'],
      connectionLimit: 10,
      acquireTimeout: 60000,
      timeout: 60000,
      reconnect: true,
    });
  }

  // 事务安全
  static async safeTransaction<T>(
    operation: (tx: any) => Promise<T>
  ): Promise<T> {
    try {
      return await this.prisma.$transaction(operation);
    } catch (error) {
      console.error('Transaction failed:', error);
      throw new Error('Transaction failed');
    }
  }
}

// 模型安全配置
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model User {
  id        String   @id @default(cuid())
  email     String   @unique
  password  String
  name      String?
  role      String   @default("user")
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // 安全字段
  passwordResetToken String?
  passwordResetExpires DateTime?

  // 关系
  posts Post[]

  @@map("users")
}

model Post {
  id        String   @id @default(cuid())
  title     String
  content   String
  published Boolean  @default(false)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // 关系
  author   User   @relation(fields: [authorId], references: [id])
  authorId String

  @@map("posts")
}

// 数据访问层
// lib/data-access.ts
class UserDataAccess {
  // 创建用户（安全）
  static async createUser(data: {
    email: string;
    password: string;
    name?: string;
  }) {
    // 加密密码
    const { hash, salt } = DataSecurity.hash(data.password);

    return await DatabaseSecurity.safeQuery(() =>
      prisma.user.create({
        data: {
          email: data.email,
          password: hash,
          passwordSalt: salt,
          name: data.name,
        },
        select: {
          id: true,
          email: true,
          name: true,
          createdAt: true,
          // 排除敏感字段
          password: false,
          passwordSalt: false,
        },
      })
    );
  }

  // 安全查找用户
  static async findUserByEmail(email: string) {
    const sanitizedEmail = DatabaseSecurity.sanitizeSQLInput(email);

    return await DatabaseSecurity.safeQuery(() =>
      prisma.user.findUnique({
        where: { email: sanitizedEmail },
        select: {
          id: true,
          email: true,
          name: true,
          role: true,
          // 排除敏感字段
          password: false,
          passwordSalt: false,
        },
      })
    );
  }

  // 更新用户（安全）
  static async updateUser(
    userId: string,
    data: any,
    requestingUserId: string
  ) {
    // 验证权限
    const canUpdate = await PermissionManager.hasPermission(
      requestingUserId,
      'users',
      'update',
      { userId, resourceOwnerId: userId }
    );

    if (!canUpdate) {
      throw new Error('Insufficient permissions');
    }

    // 过滤更新字段
    const allowedFields = ['name', 'email'];
    const filteredData = Object.keys(data)
      .filter(key => allowedFields.includes(key))
      .reduce((obj: any, key) => {
        obj[key] = data[key];
        return obj;
      }, {});

    return await DatabaseSecurity.safeTransaction(async (tx) => {
      return tx.user.update({
        where: { id: userId },
        data: filteredData,
      });
    });
  }
}
```

这个安全最佳实践速查手册涵盖了现代前端应用安全开发的各个方面，包括输入验证、XSS防护、CSRF防护、认证授权和数据安全等关键技术。每个部分都提供了实用的代码示例和最佳实践，可以作为开发过程中的安全参考指南。