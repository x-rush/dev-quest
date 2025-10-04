# Web 安全最佳实践

## 📚 概述

Web 安全是现代应用开发中的关键考虑因素。本指南涵盖了 Next.js 应用中的身份验证、数据保护、XSS/CSRF 防护、API 安全等安全最佳实践。

## 🔐 身份验证与授权

### JWT 实现
**安全的 JWT 令牌管理**

```typescript
// lib/auth/jwt.ts
import jwt from 'jsonwebtoken';
import { serialize, parse } from 'cookie';

const JWT_SECRET = process.env.JWT_SECRET!;
const JWT_EXPIRES_IN = '7d';
const REFRESH_TOKEN_EXPIRES_IN = '30d';

export interface JWTPayload {
  userId: string;
  email: string;
  role: 'user' | 'admin';
  sessionId: string;
  iat?: number;
  exp?: number;
}

export interface TokenPair {
  accessToken: string;
  refreshToken: string;
  expiresIn: number;
}

export class TokenService {
  // 生成访问令牌
  generateAccessToken(payload: Omit<JWTPayload, 'iat' | 'exp'>): string {
    return jwt.sign(payload, JWT_SECRET, {
      expiresIn: JWT_EXPIRES_IN,
      algorithm: 'HS256',
      issuer: 'your-app',
      audience: 'your-app-users',
    });
  }

  // 生成刷新令牌
  generateRefreshToken(payload: Omit<JWTPayload, 'iat' | 'exp'>): string {
    return jwt.sign(payload, JWT_SECRET, {
      expiresIn: REFRESH_TOKEN_EXPIRES_IN,
      algorithm: 'HS256',
    });
  }

  // 验证令牌
  verifyToken(token: string): JWTPayload {
    try {
      const decoded = jwt.verify(token, JWT_SECRET, {
        algorithms: ['HS256'],
        issuer: 'your-app',
        audience: 'your-app-users',
      }) as JWTPayload;
      return decoded;
    } catch (error) {
      throw new Error('Invalid token');
    }
  }

  // 解码令牌（不验证）
  decodeToken(token: string): JWTPayload | null {
    try {
      return jwt.decode(token) as JWTPayload;
    } catch {
      return null;
    }
  }

  // 生成令牌对
  generateTokenPair(user: {
    id: string;
    email: string;
    role: 'user' | 'admin';
    sessionId: string;
  }): TokenPair {
    const accessToken = this.generateAccessToken(user);
    const refreshToken = this.generateRefreshToken(user);

    return {
      accessToken,
      refreshToken,
      expiresIn: 7 * 24 * 60 * 60, // 7 days in seconds
    };
  }

  // 设置 HttpOnly Cookie
  setAuthCookie(res: any, tokenPair: TokenPair): void {
    // 设置访问令牌 Cookie
    res.setHeader(
      'Set-Cookie',
      serialize('access_token', tokenPair.accessToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: tokenPair.expiresIn,
        path: '/',
      })
    );

    // 设置刷新令牌 Cookie
    res.setHeader(
      'Set-Cookie',
      serialize('refresh_token', tokenPair.refreshToken, {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 30 * 24 * 60 * 60, // 30 days
        path: '/',
      })
    );
  }

  // 清除认证 Cookie
  clearAuthCookie(res: any): void {
    const cookies = [
      serialize('access_token', '', {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 0,
        path: '/',
      }),
      serialize('refresh_token', '', {
        httpOnly: true,
        secure: process.env.NODE_ENV === 'production',
        sameSite: 'lax',
        maxAge: 0,
        path: '/',
      }),
    ];

    cookies.forEach(cookie => {
      res.setHeader('Set-Cookie', cookie);
    });
  }
}

export const tokenService = new TokenService();
```

### 认证中间件
**Next.js 中间件实现认证**

```typescript
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { tokenService } from '@/lib/auth/jwt';

// 定义不需要认证的路径
const publicPaths = [
  '/',
  '/login',
  '/register',
  '/forgot-password',
  '/reset-password',
  '/api/auth/login',
  '/api/auth/register',
  '/api/auth/forgot-password',
  '/api/auth/refresh',
];

// 定义需要管理员权限的路径
const adminPaths = [
  '/admin',
  '/api/admin',
  '/api/users',
];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 检查是否为公开路径
  if (publicPaths.some(path => pathname.startsWith(path))) {
    return NextResponse.next();
  }

  // 获取访问令牌
  const accessToken = request.cookies.get('access_token')?.value;

  if (!accessToken) {
    // 重定向到登录页
    return NextResponse.redirect(new URL('/login', request.url));
  }

  try {
    // 验证令牌
    const payload = tokenService.verifyToken(accessToken);

    // 检查管理员路径
    if (adminPaths.some(path => pathname.startsWith(path)) && payload.role !== 'admin') {
      return NextResponse.redirect(new URL('/unauthorized', request.url));
    }

    // 添加用户信息到请求头
    const requestHeaders = new Headers(request.headers);
    requestHeaders.set('x-user-id', payload.userId);
    requestHeaders.set('x-user-email', payload.email);
    requestHeaders.set('x-user-role', payload.role);

    return NextResponse.next({
      request: {
        headers: requestHeaders,
      },
    });
  } catch (error) {
    // 令牌无效，重定向到登录页
    return NextResponse.redirect(new URL('/login', request.url));
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths except for the ones starting with:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     */
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

### 权限控制组件
**基于角色的权限控制**

```typescript
// components/auth/ProtectedRoute.tsx
import { useAuth } from '@/hooks/useAuth';
import { useRouter } from 'next/router';
import { ReactNode, useEffect } from 'react';

interface ProtectedRouteProps {
  children: ReactNode;
  requiredRole?: 'user' | 'admin';
  fallback?: ReactNode;
}

export function ProtectedRoute({
  children,
  requiredRole = 'user',
  fallback
}: ProtectedRouteProps) {
  const { user, isAuthenticated, isLoading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isLoading, isAuthenticated, router]);

  useEffect(() => {
    if (!isLoading && isAuthenticated && requiredRole) {
      if (requiredRole === 'admin' && user?.role !== 'admin') {
        router.push('/unauthorized');
      }
    }
  }, [isLoading, isAuthenticated, user, requiredRole, router]);

  if (isLoading) {
    return <div>Loading...</div>;
  }

  if (!isAuthenticated) {
    return fallback || <div>Redirecting to login...</div>;
  }

  if (requiredRole && user?.role !== requiredRole) {
    return fallback || <div>Unauthorized</div>;
  }

  return <>{children}</>;
}

// components/auth/PermissionGate.tsx
interface PermissionGateProps {
  children: ReactNode;
  permission: string;
  fallback?: ReactNode;
}

export function PermissionGate({ children, permission, fallback }: PermissionGateProps) {
  const { user, hasPermission } = useAuth();

  if (!user || !hasPermission(permission)) {
    return fallback || <div>Access Denied</div>;
  }

  return <>{children}</>;
};

// hooks/useAuth.ts
import { useState, useEffect } from 'react';
import { tokenService } from '@/lib/auth/jwt';
import type { User } from '@/types/auth.types';

export function useAuth() {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      try {
        const accessToken = document.cookie
          .split('; ')
          .find(row => row.startsWith('access_token='))
          ?.split('=')[1];

        if (!accessToken) {
          setIsLoading(false);
          return;
        }

        const payload = tokenService.verifyToken(accessToken);

        // 获取用户详情
        const response = await fetch('/api/auth/profile', {
          headers: {
            'Authorization': `Bearer ${accessToken}`,
          },
        });

        if (response.ok) {
          const userData = await response.json();
          setUser(userData);
        } else {
          // 令牌失效，清除 Cookie
          document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
        }
      } catch (error) {
        console.error('Auth initialization failed:', error);
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const hasPermission = useCallback((permission: string): boolean => {
    if (!user) return false;

    // 管理员拥有所有权限
    if (user.role === 'admin') return true;

    // 这里可以根据实际的权限系统实现
    // 例如检查用户权限列表
    return false;
  }, [user]);

  const login = useCallback(async (email: string, password: string) => {
    const response = await fetch('/api/auth/login', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    });

    if (!response.ok) {
      throw new Error('Login failed');
    }

    const data = await response.json();
    setUser(data.user);

    return data;
  }, []);

  const logout = useCallback(async () => {
    try {
      await fetch('/api/auth/logout', { method: 'POST' });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      // 清除 Cookie
      document.cookie = 'access_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
      document.cookie = 'refresh_token=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;';
    }
  }, []);

  return {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    hasPermission,
  };
}
```

## 🛡️ XSS 和 CSRF 防护

### XSS 防护
**防止跨站脚本攻击**

```typescript
// lib/security/xss.ts
import DOMPurify from 'dompurify';

export class XSSProtection {
  // 清理 HTML 内容
  static sanitizeHTML(dirty: string): string {
    return DOMPurify.sanitize(dirty, {
      ALLOWED_TAGS: [
        'p', 'br', 'strong', 'em', 'u', 'i', 'b',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'ul', 'ol', 'li',
        'a', 'img',
      ],
      ALLOWED_ATTR: ['href', 'src', 'alt', 'title', 'class'],
      ALLOW_DATA_ATTR: false,
    });
  }

  // 转义用户输入
  static escapeHtml(unsafe: string): string {
    return unsafe
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  // 安全地设置 innerHTML
  static safeSetInnerHTML(element: HTMLElement, html: string): void {
    element.innerHTML = this.sanitizeHTML(html);
  }
}

// components/ui/SafeHTML.tsx
import React from 'react';
import { XSSProtection } from '@/lib/security/xss';

interface SafeHTMLProps {
  html: string;
  className?: string;
}

export function SafeHTML({ html, className }: SafeHTMLProps) {
  const sanitizedHTML = React.useMemo(() => {
    return XSSProtection.sanitizeHTML(html);
  }, [html]);

  return (
    <div
      className={className}
      dangerouslySetInnerHTML={{ __html: sanitizedHTML }}
    />
  );
}

// app/api/posts/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { XSSProtection } from '@/lib/security/xss';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { title, content } = body;

    // 清理用户输入
    const sanitizedTitle = XSSProtection.escapeHtml(title);
    const sanitizedContent = XSSProtection.sanitizeHTML(content);

    // 保存到数据库
    const post = await savePost({
      title: sanitizedTitle,
      content: sanitizedContent,
    });

    return NextResponse.json({ success: true, post });
  } catch (error) {
    return NextResponse.json(
      { success: false, error: 'Invalid request' },
      { status: 400 }
    );
  }
}
```

### CSRF 防护
**防止跨站请求伪造攻击**

```typescript
// lib/security/csrf.ts
import { randomBytes, createHash } from 'crypto';

export class CSRFProtection {
  // 生成 CSRF 令牌
  static generateToken(): string {
    return randomBytes(32).toString('hex');
  }

  // 生成 CSRF 令牌的哈希
  static generateTokenHash(token: string): string {
    return createHash('sha256').update(token).digest('hex');
  }

  // 验证 CSRF 令牌
  static validateToken(token: string, hash: string): boolean {
    const tokenHash = this.generateTokenHash(token);
    return tokenHash === hash;
  }

  // 设置 CSRF Cookie
  static setCSRFCookie(res: any, token: string): void {
    res.setHeader(
      'Set-Cookie',
      `csrf_token=${token}; HttpOnly; Secure; SameSite=Strict; Path=/; Max-Age=3600`
    );
  }
}

// lib/api/csrf.ts
import { NextRequest, NextResponse } from 'next/server';
import { CSRFProtection } from '@/lib/security/csrf';

export async function GET() {
  // 生成新的 CSRF 令牌
  const token = CSRFProtection.generateToken();
  const tokenHash = CSRFProtection.generateTokenHash(token);

  // 设置 CSRF Cookie
  const response = NextResponse.json({ token });
  CSRFProtection.setCSRFCookie(response, token);

  return response;
}

// 表单组件
// components/forms/SecureForm.tsx
import { useState, useEffect } from 'react';

export function SecureForm() {
  const [csrfToken, setCsrfToken] = useState('');

  useEffect(() => {
    // 获取 CSRF 令牌
    fetch('/api/csrf')
      .then(res => res.json())
      .then(data => setCsrfToken(data.token))
      .catch(console.error);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const formData = new FormData(e.currentTarget);
    formData.append('csrf_token', csrfToken);

    try {
      const response = await fetch('/api/submit', {
        method: 'POST',
        body: formData,
        credentials: 'include',
      });

      if (response.ok) {
        // 处理成功
      } else {
        // 处理错误
      }
    } catch (error) {
      console.error('Submit error:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="hidden" name="csrf_token" value={csrfToken} />
      {/* 其他表单字段 */}
      <button type="submit">Submit</button>
    </form>
  );
}

// API 路由中的 CSRF 验证
// app/api/submit/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { CSRFProtection } from '@/lib/security/csrf';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const csrfToken = formData.get('csrf_token') as string;
    const cookieToken = request.cookies.get('csrf_token')?.value;

    if (!csrfToken || !cookieToken) {
      return NextResponse.json(
        { error: 'CSRF token missing' },
        { status: 403 }
      );
    }

    if (!CSRFProtection.validateToken(csrfToken, cookieToken)) {
      return NextResponse.json(
        { error: 'Invalid CSRF token' },
        { status: 403 }
      );
    }

    // 处理表单数据
    // ...

    return NextResponse.json({ success: true });
  } catch (error) {
    return NextResponse.json(
      { error: 'Invalid request' },
      { status: 400 }
    );
  }
}
```

## 🔒 数据保护

### 敏感数据处理
**加密和解密敏感数据**

```typescript
// lib/security/encryption.ts
import crypto from 'crypto';

export class Encryption {
  private static readonly ALGORITHM = 'aes-256-gcm';
  private static readonly ENCRYPTION_KEY = process.env.ENCRYPTION_KEY!;
  private static readonly IV_LENGTH = 16;
  private static readonly TAG_LENGTH = 16;

  // 生成随机 IV
  private static generateIV(): Buffer {
    return crypto.randomBytes(this.IV_LENGTH);
  }

  // 加密数据
  static encrypt(text: string): {
    encrypted: string;
    iv: string;
    tag: string;
  } {
    const iv = this.generateIV();
    const cipher = crypto.createCipher(this.ALGORITHM, this.ENCRYPTION_KEY);
    cipher.setAAD(Buffer.from('additional-data'));

    let encrypted = cipher.update(text, 'utf8', 'hex');
    encrypted += cipher.final('hex');

    const tag = cipher.getAuthTag();

    return {
      encrypted,
      iv: iv.toString('hex'),
      tag: tag.toString('hex'),
    };
  }

  // 解密数据
  static decrypt(encryptedData: {
    encrypted: string;
    iv: string;
    tag: string;
  }): string {
    const decipher = crypto.createDecipher(this.ALGORITHM, this.ENCRYPTION_KEY);
    decipher.setAAD(Buffer.from('additional-data'));
    decipher.setAuthTag(Buffer.from(encryptedData.tag, 'hex'));

    let decrypted = decipher.update(encryptedData.encrypted, 'hex', 'utf8');
    decrypted += decipher.final('utf8');

    return decrypted;
  }

  // 哈希密码
  static hashPassword(password: string): {
    hash: string;
    salt: string;
  } {
    const salt = crypto.randomBytes(32).toString('hex');
    const hash = crypto
      .pbkdf2Sync(password, salt, 100000, 64, 'sha512')
      .toString('hex');

    return { hash, salt };
  }

  // 验证密码
  static verifyPassword(
    password: string,
    hash: string,
    salt: string
  ): boolean {
    const hashVerify = crypto
      .pbkdf2Sync(password, salt, 100000, 64, 'sha512')
      .toString('hex');

    return hash === hashVerify;
  }

  // 生成安全的随机字符串
  static generateRandomString(length: number): string {
    return crypto
      .randomBytes(Math.ceil(length / 2))
      .toString('hex')
      .slice(0, length);
  }
}

// 使用示例
// lib/auth/password.ts
import { Encryption } from '@/lib/security/encryption';

export class PasswordService {
  static async hashPassword(password: string): Promise<string> {
    const { hash, salt } = Encryption.hashPassword(password);
    // 存储密码哈希和盐值
    await savePasswordHash({ hash, salt });
    return hash;
  }

  static async verifyPassword(
    password: string,
    hashedPassword: string
  ): Promise<boolean> {
    const { salt } = await getPasswordHash(hashedPassword);
    return Encryption.verifyPassword(password, hashedPassword, salt);
  }
}
```

### 环境变量保护
**安全地管理环境变量**

```typescript
// lib/config/env.ts
import { z } from 'zod';

// 环境变量 schema
const envSchema = z.object({
  NODE_ENV: z.enum(['development', 'production', 'test']),
  NEXT_PUBLIC_API_URL: z.string().url(),
  NEXT_PUBLIC_APP_URL: z.string().url(),

  // 数据库配置
  DATABASE_URL: z.string(),
  DATABASE_SSL: z.boolean().default(true),

  // 认证配置
  JWT_SECRET: z.string().min(32),
  REFRESH_TOKEN_SECRET: z.string().min(32),

  // 加密配置
  ENCRYPTION_KEY: z.string().min(32),

  // 第三方服务
  GOOGLE_CLIENT_ID: z.string(),
  GOOGLE_CLIENT_SECRET: z.string(),

  // 邮件服务
  SMTP_HOST: z.string(),
  SMTP_PORT: z.number(),
  SMTP_USER: z.string(),
  SMTP_PASS: z.string(),

  // Redis 配置
  REDIS_URL: z.string().optional(),

  // 文件存储
  AWS_ACCESS_KEY_ID: z.string(),
  AWS_SECRET_ACCESS_KEY: z.string(),
  AWS_S3_BUCKET: z.string(),
  AWS_REGION: z.string(),
});

// 验证环境变量
const envValidation = envSchema.safeParse(process.env);

if (!envValidation.success) {
  console.error('❌ Invalid environment variables:', envValidation.error.format());
  throw new Error('Invalid environment variables');
}

export const env = envValidation.data;

// 类型安全的访问器
export const getEnvVar = (key: keyof typeof env) => env[key];

// 客户端可访问的环境变量
export const publicEnv = {
  NEXT_PUBLIC_API_URL: env.NEXT_PUBLIC_API_URL,
  NEXT_PUBLIC_APP_URL: env.NEXT_PUBLIC_APP_URL,
} as const;

// 服务端专用环境变量
export const privateEnv = {
  DATABASE_URL: env.DATABASE_URL,
  JWT_SECRET: env.JWT_SECRET,
  ENCRYPTION_KEY: env.ENCRYPTION_KEY,
  SMTP_HOST: env.SMTP_HOST,
  SMTP_PORT: env.SMTP_PORT,
  SMTP_USER: env.SMTP_USER,
  SMTP_PASS: env.SMTP_PASS,
  REDIS_URL: env.REDIS_URL,
  AWS_ACCESS_KEY_ID: env.AWS_ACCESS_KEY_ID,
  AWS_SECRET_ACCESS_KEY: env.AWS_SECRET_ACCESS_KEY,
  AWS_S3_BUCKET: env.AWS_S3_BUCKET,
  AWS_REGION: env.AWS_REGION,
} as const;

// .env.example
/*
NODE_ENV=development
NEXT_PUBLIC_API_URL=http://localhost:3000/api
NEXT_PUBLIC_APP_URL=http://localhost:3000

DATABASE_URL=postgresql://user:password@localhost:5432/myapp
DATABASE_SSL=true

JWT_SECRET=your-super-secret-jwt-key-at-least-32-characters
REFRESH_TOKEN_SECRET=your-super-secret-refresh-key-at-least-32-characters
ENCRYPTION_KEY=your-super-secret-encryption-key-at-least-32-characters

GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret

SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASS=your-app-password

REDIS_URL=redis://localhost:6379

AWS_ACCESS_KEY_ID=your-aws-access-key
AWS_SECRET_ACCESS_KEY=your-aws-secret-key
AWS_S3_BUCKET=your-s3-bucket
AWS_REGION=us-east-1
*/
```

## 🌐 API 安全

### API 速率限制
**防止 API 滥用**

```typescript
// lib/api/rate-limiter.ts
import { NextRequest } from 'next/server';

interface RateLimitData {
  count: number;
  resetTime: number;
}

class RateLimiter {
  private static store = new Map<string, RateLimitData>();

  static limit(
    identifier: string,
    maxRequests: number,
    windowMs: number
  ): {
    success: boolean;
    remaining: number;
    resetTime: number;
    retryAfter?: number;
  } {
    const now = Date.now();
    const windowStart = now - windowMs;

    // 清理过期记录
    for (const [key, data] of this.store.entries()) {
      if (data.resetTime < windowStart) {
        this.store.delete(key);
      }
    }

    const data = this.store.get(identifier);

    if (!data || data.resetTime < windowStart) {
      // 创建新的记录
      this.store.set(identifier, {
        count: 1,
        resetTime: now + windowMs,
      });

      return {
        success: true,
        remaining: maxRequests - 1,
        resetTime: now + windowMs,
      };
    }

    if (data.count >= maxRequests) {
      return {
        success: false,
        remaining: 0,
        resetTime: data.resetTime,
        retryAfter: Math.ceil((data.resetTime - now) / 1000),
      };
    }

    // 增加计数
    data.count++;
    this.store.set(identifier, data);

    return {
      success: true,
      remaining: maxRequests - data.count,
      resetTime: data.resetTime,
    };
  }

  static clear(identifier: string): void {
    this.store.delete(identifier);
  }
}

// API 路由中的速率限制
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { RateLimiter } from '@/lib/api/rate-limiter';

export async function GET(request: NextRequest) {
  // 获取客户端 IP
  const ip = request.ip ||
    request.headers.get('x-forwarded-for')?.split(',')[0] ||
    'unknown';

  // 应用速率限制：每分钟 100 次请求
  const rateLimitResult = RateLimiter.limit(
    ip,
    100,
    60 * 1000 // 1 minute
  );

  // 设置响应头
  const headers = new Headers({
    'X-RateLimit-Limit': '100',
    'X-RateLimit-Remaining': rateLimitResult.remaining.toString(),
    'X-RateLimit-Reset': rateLimitResult.resetTime.toString(),
  });

  if (!rateLimitResult.success) {
    headers.set('Retry-After', rateLimitResult.retryAfter!.toString());

    return NextResponse.json(
      {
        error: 'Rate limit exceeded',
        message: 'Too many requests. Please try again later.',
        retryAfter: rateLimitResult.retryAfter,
      },
      {
        status: 429,
        headers,
      }
    );
  }

  // 处理正常请求
  const users = await getUsers();

  return NextResponse.json(
    { users },
    { headers }
  );
}

// 基于用户的速率限制
// app/api/posts/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { RateLimiter } from '@/lib/api/rate-limiter';
import { getToken } from 'next-auth/jwt';

export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  // 验证令牌
  const token = await getToken({ req: request });
  if (!token) {
    return NextResponse.json(
      { error: 'Unauthorized' },
      { status: 401 }
    );
  }

  // 基于用户的速率限制：每小时 10 次删除操作
  const rateLimitResult = RateLimiter.limit(
    `delete-posts-${token.sub}`,
    10,
    60 * 60 * 1000 // 1 hour
  );

  if (!rateLimitResult.success) {
    return NextResponse.json(
      {
        error: 'Rate limit exceeded',
        message: 'Too many delete requests. Please try again later.',
      },
      { status: 429 }
    );
  }

  // 处理删除逻辑
  await deletePost(params.id);

  return NextResponse.json(
    { message: 'Post deleted successfully' },
    { status: 200 }
  );
}
```

### API 输入验证
**严格的数据验证**

```typescript
// lib/validation/schemas.ts
import { z } from 'zod';

// 用户注册验证
export const registerSchema = z.object({
  name: z
    .string()
    .min(2, 'Name must be at least 2 characters')
    .max(50, 'Name must be less than 50 characters'),
  email: z
    .string()
    .email('Invalid email address'),
  password: z
    .string()
    .min(8, 'Password must be at least 8 characters')
    .regex(
      /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]/,
      'Password must contain at least one lowercase letter, one uppercase letter, one number, and one special character'
    ),
  confirmPassword: z.string(),
}).refine(
  (data) => data.password === data.confirmPassword,
  {
    message: 'Passwords do not match',
    path: ['confirmPassword'],
  }
);

// 博客文章验证
export const postSchema = z.object({
  title: z
    .string()
    .min(1, 'Title is required')
    .max(200, 'Title must be less than 200 characters'),
  content: z
    .string()
    .min(10, 'Content must be at least 10 characters'),
  excerpt: z
    .string()
    .max(500, 'Excerpt must be less than 500 characters')
    .optional(),
  published: z.boolean().default(false),
  tags: z
    .array(z.string().min(1).max(50))
    .max(10, 'Maximum 10 tags allowed')
    .default([]),
});

// 搜索参数验证
export const searchParamsSchema = z.object({
  q: z.string().min(1).max(100),
  page: z.coerce.number().min(1).default(1),
  limit: z.coerce.number().min(1).max(100).default(20),
  sort: z.enum(['relevance', 'date', 'title']).default('relevance'),
  category: z.string().optional(),
});

// API 路由中使用验证
// app/api/auth/register/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { registerSchema } from '@/lib/validation/schemas';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // 验证输入
    const validatedData = registerSchema.parse(body);

    // 处理注册逻辑
    const user = await registerUser(validatedData);

    return NextResponse.json(
      {
        message: 'User registered successfully',
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
        },
      },
      { status: 201 }
    );
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          error: 'Validation failed',
          details: error.errors.map(err => ({
            field: err.path.join('.'),
            message: err.message,
          })),
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      { error: 'Registration failed' },
      { status: 500 }
    );
  }
}

// 客户端验证 Hook
// hooks/useFormValidation.ts
import { z } from 'zod';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';

export function useValidatedForm<T extends z.ZodSchema>(
  schema: T
) {
  const form = useForm<z.infer<T>>({
    resolver: zodResolver(schema),
    mode: 'onChange',
  });

  const { errors, isSubmitting, isValid } = form.formState;

  return {
    ...form,
    errors,
    isSubmitting,
    isValid,
  };
}

// 使用示例
// components/auth/RegisterForm.tsx
import { registerSchema } from '@/lib/validation/schemas';
import { useValidatedForm } from '@/hooks/useFormValidation';

export function RegisterForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useValidatedForm(registerSchema);

  const onSubmit = async (data: z.infer<typeof registerSchema>) => {
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
      });

      if (response.ok) {
        // 处理成功
      }
    } catch (error) {
      // 处理错误
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>Name</label>
        <input {...register('name')} />
        {errors.name && <span className="error">{errors.name.message}</span>}
      </div>

      <div>
        <label>Email</label>
        <input {...register('email')} />
        {errors.email && <span className="error">{errors.email.message}</span>}
      </div>

      <div>
        <label>Password</label>
        <input {...register('password')} type="password" />
        {errors.password && <span className="error">{errors.password.message}</span>}
      </div>

      <div>
        <label>Confirm Password</label>
        <input {...register('confirmPassword')} type="password" />
        {errors.confirmPassword && (
          <span className="error">{errors.confirmPassword.message}</span>
        )}
      </div>

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? 'Registering...' : 'Register'}
      </button>
    </form>
  );
}
```

## 📊 安全监控

### 安全事件日志
**记录和监控安全事件**

```typescript
// lib/security/logger.ts
interface SecurityEvent {
  timestamp: string;
  level: 'info' | 'warning' | 'error' | 'critical';
  type: string;
  description: string;
  ip?: string;
  userId?: string;
  userAgent?: string;
  details?: any;
}

export class SecurityLogger {
  private static logs: SecurityEvent[] = [];

  static log(event: Omit<SecurityEvent, 'timestamp'>): void {
    const logEntry: SecurityEvent = {
      ...event,
      timestamp: new Date().toISOString(),
    };

    this.logs.push(logEntry);

    // 控制台输出
    const logMethod = this.getConsoleMethod(event.level);
    logMethod(`[${event.level.toUpperCase()}] ${event.type}: ${event.description}`);

    // 发送到日志服务
    this.sendToLogService(logEntry);

    // 清理旧日志（保留最近 1000 条）
    if (this.logs.length > 1000) {
      this.logs = this.logs.slice(-500);
    }
  }

  private static getConsoleMethod(level: SecurityEvent['level']) {
    switch (level) {
      case 'info':
        return console.log;
      case 'warning':
        return console.warn;
      case 'error':
      case 'critical':
        return console.error;
      default:
        return console.log;
    }
  }

  private static async sendToLogService(event: SecurityEvent): Promise<void> {
    try {
      // 发送到外部日志服务
      await fetch('/api/logs/security', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(event),
      });
    } catch (error) {
      console.error('Failed to send log to service:', error);
    }
  }

  // 登录失败
  static logLoginFailure(ip: string, email: string, userAgent: string, reason: string): void {
    this.log({
      level: 'warning',
      type: 'LOGIN_FAILURE',
      description: `Login failed for ${email}: ${reason}`,
      ip,
      userAgent,
      details: { email, reason },
    });
  }

  // 可疑活动
  static logSuspiciousActivity(
    userId: string,
    ip: string,
    activity: string,
    details?: any
  ): void {
    this.log({
      level: 'error',
      type: 'SUSPICIOUS_ACTIVITY',
      description: `Suspicious activity detected: ${activity}`,
      userId,
      ip,
      details,
    });
  }

  // 安全违规
  static logSecurityViolation(
    userId: string,
    ip: string,
    violation: string,
    details?: any
  ): void {
    this.log({
      level: 'critical',
      type: 'SECURITY_VIOLATION',
      description: `Security violation: ${violation}`,
      userId,
      ip,
      details,
    });
  }

  // 获取日志
  static getLogs(): SecurityEvent[] {
    return [...this.logs];
  }
}

// 中间件中的安全日志
// middleware.ts
import { NextRequest, NextResponse } from 'next/server';
import { SecurityLogger } from '@/lib/security/logger';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const ip = request.ip || 'unknown';
  const userAgent = request.headers.get('user-agent') || 'unknown';

  // 记录可疑路径访问
  const suspiciousPaths = [
    '/admin',
    '/api/admin',
    '/.env',
    '/wp-admin',
    '/phpmyadmin',
  ];

  if (suspiciousPaths.some(path => pathname.includes(path))) {
    SecurityLogger.logSuspiciousActivity(
      'anonymous',
      ip,
      'Access to suspicious path',
      { pathname, userAgent }
    );
  }

  // 其他中间件逻辑...

  return NextResponse.next();
}
```

### 安全头设置
**设置安全 HTTP 头**

```typescript
// lib/security/headers.ts
export interface SecurityHeaders {
  // 内容安全策略
  contentSecurityPolicy?: string;

  // XSS 保护
  xXSSProtection?: string;

  // 内容类型选项
  xContentTypeOptions?: string;

  // 框架选项
  xFrameOptions?: string;

  // HSTS
  strictTransportSecurity?: string;

  // 引用策略
  referrerPolicy?: string;

  // 权限策略
  permissionsPolicy?: string;
}

export class SecurityHeaders {
  // 生成 CSP 头
  static generateCSP(nonce?: string): string {
    const directives = [
      "default-src 'self'",
      "script-src 'self' 'unsafe-eval' 'unsafe-inline' https://www.googletagmanager.com https://www.google-analytics.com",
      "style-src 'self' 'unsafe-inline' https://fonts.googleapis.com",
      "font-src 'self' https://fonts.gstatic.com",
      "img-src 'self' data: https:",
      "connect-src 'self' https://api.example.com https://www.google-analytics.com",
      "frame-src 'none'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "upgrade-insecure-requests",
    ];

    if (nonce) {
      directives[1] += ` 'nonce-${nonce}'`;
    }

    return directives.join('; ');
  }

  // 生产环境 CSP
  static getProductionCSP(nonce?: string): string {
    return [
      "default-src 'self'",
      "script-src 'self' https://www.googletagmanager.com https://www.google-analytics.com",
      "style-src 'self' https://fonts.googleapis.com",
      "font-src 'self' https://fonts.gstatic.com",
      "img-src 'self' data: https:",
      "connect-src 'self' https://api.example.com https://www.google-analytics.com",
      "frame-src 'none'",
      "object-src 'none'",
      "base-uri 'self'",
      "form-action 'self'",
      "upgrade-insecure-requests",
    ].join('; ');
  }

  // 获取所有安全头
  static getAllHeaders(isProduction: boolean, nonce?: string): Record<string, string> {
    const headers: Record<string, string> = {
      // XSS 保护
      'X-XSS-Protection': '1; mode=block',

      // 内容类型选项
      'X-Content-Type-Options': 'nosniff',

      // 框架选项
      'X-Frame-Options': 'DENY',

      // 引用策略
      'Referrer-Policy': 'strict-origin-when-cross-origin',

      // 权限策略
      'Permissions-Policy': 'camera=(), microphone=(), geolocation=()',
    };

    // CSP
    if (isProduction) {
      headers['Content-Security-Policy'] = this.getProductionCSP(nonce);
    } else {
      headers['Content-Security-Policy'] = this.generateCSP(nonce);
    }

    // HSTS（仅 HTTPS）
    if (isProduction) {
      headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload';
    }

    return headers;
  }
}

// app/layout.tsx
import { headers } from 'next/headers';
import { SecurityHeaders } from '@/lib/security/headers';

export function RootLayout({ children }: { children: React.ReactNode }) {
  const isProduction = process.env.NODE_ENV === 'production';

  // 生成随机 nonce
  const nonce = crypto.randomBytes(16).toString('base64');

  // 获取安全头
  const securityHeaders = SecurityHeaders.getAllHeaders(isProduction, nonce);

  return (
    <html lang="en">
      <head>
        {Object.entries(securityHeaders).map(([key, value]) => (
          <meta key={key} httpEquiv={key} content={value} />
        ))}
      </head>
      <body>{children}</body>
    </html>
  );
}
```

## 📋 安全检查清单

### 认证安全
- [ ] 使用强密码策略
- [ ] 实施 JWT 令牌管理
- [ ] 使用 HttpOnly Cookie
- [ ] 实现安全的密码重置
- [ ] 启用多因素认证
- [ ] 定期轮换密钥

### 数据保护
- [ ] 加密敏感数据
- [ ] 安全存储密码
- [ ] 保护环境变量
- [ ] 使用 HTTPS 传输
- [ ] 实施数据备份策略
- [ ] 定期安全审计

### API 安全
- [ ] 实施速率限制
- [ ] 验证所有输入
- [ ] 使用 CORS 策略
- [ ] 实施 CSRF 保护
- [ ] 记录安全事件
- [ ] 监控异常行为

### 客户端安全
- [ ] 实施 CSP 策略
- [ ] 设置安全头
- [ ] 防止 XSS 攻击
- [ ] 验证用户输入
- [ ] 使用安全的库
- [ ] 定期更新依赖

## 📖 总结

Web 安全是一个持续的过程，需要多层次的防护：

### 核心安全原则：
1. **最小权限原则**: 只授予必要的权限
2. **深度防御**: 多层安全防护
3. **零信任**: 不信任任何请求
4. **持续监控**: 实时安全监控
5. **定期更新**: 及时更新和修补

### 实施要点：
1. **身份验证**: 强认证机制
2. **数据保护**: 加密和脱敏
3. **输入验证**: 严格的输入检查
4. **输出编码**: 防止注入攻击
5. **监控审计**: 安全事件记录

### 工具支持：
1. **安全扫描**: 自动化安全检测
2. **依赖检查**: 检查已知漏洞
3. **代码审计**: 定期安全代码审查
4. **渗透测试**: 模拟攻击测试
5. **安全培训**: 团队安全意识培训

通过实施这些安全最佳实践，可以大大提高应用的安全性，保护用户数据和系统资源。安全是一个持续的过程，需要不断地评估和改进安全措施。