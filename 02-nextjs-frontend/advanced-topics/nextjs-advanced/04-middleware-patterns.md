# Next.js 15 中间件模式与实践

## 📋 概述

Next.js 15 的中间件（Middleware）是一个强大的功能，允许在请求到达页面之前运行代码。中间件运行在边缘网络（Edge Network）上，提供低延迟的请求处理能力。本文将深入探讨 Next.js 15 中间件的各种模式和最佳实践。

## 🎯 中间件基础

### 1. 中间件工作原理

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  // 1. 请求拦截
  console.log('Middleware running for:', request.url);

  // 2. 请求处理
  const response = NextResponse.next();

  // 3. 响应修改
  response.headers.set('X-Custom-Header', 'value');

  // 4. 返回响应
  return response;
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

### 2. 中间件生命周期

```
客户端请求
    ↓
CDN边缘节点
    ↓
Next.js中间件
    ↓
路由处理
    ↓
页面/API路由
    ↓
响应返回
```

## 🚀 高级中间件模式

### 1. 认证和授权模式

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const token = request.cookies.get('auth-token')?.value;

  // 公开路由，无需认证
  const publicRoutes = ['/login', '/register', '/forgot-password'];
  const isPublicRoute = publicRoutes.some(route =>
    pathname.startsWith(route)
  );

  if (isPublicRoute && token) {
    // 已认证用户访问公开页面，重定向到仪表板
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // 受保护路由检查
  const protectedRoutes = ['/dashboard', '/profile', '/settings'];
  const isProtectedRoute = protectedRoutes.some(route =>
    pathname.startsWith(route)
  );

  if (isProtectedRoute && !token) {
    // 未认证用户访问受保护页面，重定向到登录
    const loginUrl = new URL('/login', request.url);
    loginUrl.searchParams.set('redirect', pathname);
    return NextResponse.redirect(loginUrl);
  }

  // 角色基础的访问控制
  const roleProtectedRoutes = {
    '/admin': ['admin'],
    '/moderator': ['admin', 'moderator'],
    '/premium': ['admin', 'moderator', 'premium'],
  };

  for (const [route, allowedRoles] of Object.entries(roleProtectedRoutes)) {
    if (pathname.startsWith(route)) {
      const userRole = request.cookies.get('user-role')?.value;
      if (!userRole || !allowedRoles.includes(userRole)) {
        return NextResponse.redirect(new URL('/unauthorized', request.url));
      }
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|api/auth).*)',
  ],
};
```

### 2. A/B测试模式

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // 获取或创建A/B测试变体
  let variant = request.cookies.get('ab-test-variant')?.value;

  if (!variant) {
    // 基于用户ID或IP分配变体
    const userId = request.cookies.get('user-id')?.value || request.ip;
    const hash = simpleHash(userId || 'anonymous');
    variant = hash % 2 === 0 ? 'A' : 'B';

    // 设置cookie
    response.cookies.set('ab-test-variant', variant, {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 60 * 60 * 24 * 30, // 30天
    });
  }

  // 为特定路由设置A/B测试
  const abTestRoutes = {
    '/landing': {
      A: { background: 'blue', cta: 'Get Started' },
      B: { background: 'green', cta: 'Start Free Trial' },
    },
    '/pricing': {
      A: { layout: 'grid' },
      B: { layout: 'comparison' },
    },
  };

  for (const [route, variants] of Object.entries(abTestRoutes)) {
    if (request.nextUrl.pathname.startsWith(route)) {
      const variantConfig = variants[variant as keyof typeof variants];

      // 在响应头中传递变体信息
      response.headers.set('X-AB-Variant', variant);
      response.headers.set('X-AB-Config', JSON.stringify(variantConfig));
    }
  }

  return response;
}

// 简单哈希函数
function simpleHash(str: string): number {
  let hash = 0;
  for (let i = 0; i < str.length; i++) {
    const char = str.charCodeAt(i);
    hash = ((hash << 5) - hash) + char;
    hash = hash & hash; // 转换为32位整数
  }
  return Math.abs(hash);
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

### 3. 地理位置和本地化模式

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;
  const geo = request.geo;

  // 1. 地理位置重定向
  const country = geo?.country;
  const language = request.headers.get('accept-language')?.split(',')[0];

  // 国家特定的重定向
  const countryRedirects: Record<string, string> = {
    'CN': '/zh',
    'JP': '/ja',
    'KR': '/ko',
    'DE': '/de',
    'FR': '/fr',
    'ES': '/es',
  };

  if (country && countryRedirects[country] && !pathname.startsWith(countryRedirects[country])) {
    return NextResponse.redirect(
      new URL(countryRedirects[country], request.url)
    );
  }

  // 2. 语言检测和设置
  const supportedLanguages = ['en', 'zh', 'ja', 'ko', 'de', 'fr', 'es'];
  let detectedLanguage = 'en';

  if (language) {
    const langCode = language.split('-')[0];
    if (supportedLanguages.includes(langCode)) {
      detectedLanguage = langCode;
    }
  }

  // 设置语言cookie
  const response = NextResponse.next();
  response.cookies.set('preferred-language', detectedLanguage, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 60 * 60 * 24 * 365, // 1年
  });

  // 3. 内容本地化
  response.headers.set('X-Country', country || 'unknown');
  response.headers.set('X-Language', detectedLanguage);
  response.headers.set('X-Timezone', geo?.timezone || 'UTC');

  // 4. 法律合规（GDPR等）
  const gdprCountries = ['DE', 'FR', 'IT', 'ES', 'GB'];
  if (country && gdprCountries.includes(country)) {
    response.headers.set('X-GDPR-Required', 'true');
    response.cookies.set('gdpr-consent', 'required', {
      httpOnly: false,
      secure: true,
      sameSite: 'lax',
    });
  }

  return response;
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico|api).*)',
  ],
};
```

### 4. 性能优化模式

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  const response = NextResponse.next();

  // 1. 缓存控制头
  const { pathname } = request.nextUrl;

  // 静态资源长期缓存
  if (pathname.startsWith('/static/') || pathname.includes('.')) {
    response.headers.set('Cache-Control', 'public, max-age=31536000, immutable');
  }
  // 页面短期缓存
  else if (pathname.startsWith('/blog/')) {
    response.headers.set('Cache-Control', 'public, max-age=3600, stale-while-revalidate=60');
  }
  // 动态内容不缓存
  else if (pathname.startsWith('/dashboard/')) {
    response.headers.set('Cache-Control', 'no-cache, no-store, must-revalidate');
  }

  // 2. 压缩优化
  response.headers.set('Vary', 'Accept-Encoding');

  // 3. 安全头
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('X-XSS-Protection', '1; mode=block');
  response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  response.headers.set('Permissions-Policy', 'camera=(), microphone=(), geolocation=()');

  // 4. CSP头
  if (process.env.NODE_ENV === 'production') {
    response.headers.set(
      'Content-Security-Policy',
      "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' https:; frame-ancestors 'none';"
    );
  }

  // 5. 性能监控
  response.headers.set('X-Response-Time', Date.now().toString());
  response.headers.set('X-Request-ID', crypto.randomUUID());

  return response;
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

## 🎨 高级中间件功能

### 1. API代理和转发

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // API代理模式
  if (pathname.startsWith('/api/external/')) {
    const externalPath = pathname.replace('/api/external/', '');
    const externalUrl = new URL(externalPath, process.env.EXTERNAL_API_URL);

    try {
      // 转发请求
      const response = await fetch(externalUrl, {
        method: request.method,
        headers: {
          // 转发必要的头
          'Content-Type': request.headers.get('content-type') || 'application/json',
          'Authorization': request.headers.get('authorization') || '',
          'User-Agent': request.headers.get('user-agent') || '',
        },
        body: request.body,
        duplex: 'half',
      });

      // 创建响应
      const data = await response.json();
      const proxyResponse = NextResponse.json(data, {
        status: response.status,
      });

      // 添加CORS头
      proxyResponse.headers.set('Access-Control-Allow-Origin', '*');
      proxyResponse.headers.set('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
      proxyResponse.headers.set('Access-Control-Allow-Headers', 'Content-Type, Authorization');

      return proxyResponse;
    } catch (error) {
      return NextResponse.json(
        { error: 'Proxy request failed' },
        { status: 500 }
      );
    }
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/api/external/:path*',
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

### 2. 速率限制和安全防护

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// 简单的内存速率限制器（生产环境应使用Redis等）
const rateLimiter = new Map<string, { count: number; resetTime: number }>();

export async function middleware(request: NextRequest) {
  const ip = request.ip;
  const now = Date.now();

  // 1. 速率限制
  const limit = 100; // 100 requests per minute
  const windowMs = 60 * 1000; // 1 minute

  if (!rateLimiter.has(ip)) {
    rateLimiter.set(ip, { count: 1, resetTime: now + windowMs });
  } else {
    const record = rateLimiter.get(ip)!;

    if (now > record.resetTime) {
      // Reset window
      record.count = 1;
      record.resetTime = now + windowMs;
    } else {
      record.count++;

      if (record.count > limit) {
        return NextResponse.json(
          { error: 'Rate limit exceeded' },
          { status: 429 }
        );
      }
    }
  }

  // 2. Bot检测
  const userAgent = request.headers.get('user-agent') || '';
  const suspiciousPatterns = [
    /bot/i, /crawler/i, /spider/i, /scanner/i,
    /curl/i, /wget/i, /python/i, /postman/i
  ];

  const isSuspicious = suspiciousPatterns.some(pattern => pattern.test(userAgent));

  if (isSuspicious && !request.nextUrl.pathname.startsWith('/api/')) {
    return NextResponse.json(
      { error: 'Access denied' },
      { status: 403 }
    );
  }

  // 3. 安全检查
  const suspiciousParams = request.nextUrl.searchParams.toString();
  const sqlInjectionPattern = /(\b(select|insert|update|delete|drop|union|exec)\b)/i;
  const xssPattern = /(<script|javascript:|on\w+\s*=)/i;

  if (
    sqlInjectionPattern.test(suspiciousParams) ||
    xssPattern.test(suspiciousParams)
  ) {
    return NextResponse.json(
      { error: 'Security violation detected' },
      { status: 400 }
    );
  }

  // 4. IP白名单/黑名单
  const allowedIPs = process.env.ALLOWED_IPS?.split(',') || [];
  const blockedIPs = process.env.BLOCKED_IPS?.split(',') || [];

  if (blockedIPs.includes(ip)) {
    return NextResponse.json(
      { error: 'IP blocked' },
      { status: 403 }
    );
  }

  if (allowedIPs.length > 0 && !allowedIPs.includes(ip)) {
    return NextResponse.json(
      { error: 'IP not allowed' },
      { status: 403 }
    );
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

### 3. 分析和监控中间件

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export async function middleware(request: NextRequest) {
  const startTime = Date.now();
  const response = NextResponse.next();

  // 1. 请求分析
  const analyticsData = {
    timestamp: startTime,
    url: request.url,
    method: request.method,
    userAgent: request.headers.get('user-agent'),
    ip: request.ip,
    geo: request.geo,
    referer: request.headers.get('referer'),
    path: request.nextUrl.pathname,
    searchParams: Object.fromEntries(request.nextUrl.searchParams),
  };

  // 2. 性能监控
  response.headers.set('X-Start-Time', startTime.toString());

  // 3. 异步发送分析数据（不阻塞响应）
  if (process.env.ANALYTICS_WEBHOOK) {
    // 在边缘环境中，我们需要立即发送
    try {
      await fetch(process.env.ANALYTICS_WEBHOOK, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(analyticsData),
      });
    } catch (error) {
      console.error('Failed to send analytics:', error);
    }
  }

  // 4. 自定义指标
  response.headers.set('X-Metrics-Enabled', 'true');

  // 5. A/B测试跟踪
  const variant = request.cookies.get('ab-test-variant')?.value;
  if (variant) {
    response.headers.set('X-AB-Variant', variant);
  }

  // 6. 用户旅程跟踪
  const sessionId = request.cookies.get('session-id')?.value;
  if (sessionId) {
    response.headers.set('X-Session-ID', sessionId);
  }

  return response;
}

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};
```

## 🔄 中间件最佳实践

### 1. 模块化中间件

```typescript
// middleware/auth.ts
export class AuthMiddleware {
  static handle(request: NextRequest) {
    const token = request.cookies.get('auth-token')?.value;
    const { pathname } = request.nextUrl;

    if (!token && this.isProtectedRoute(pathname)) {
      const loginUrl = new URL('/login', request.url);
      loginUrl.searchParams.set('redirect', pathname);
      return NextResponse.redirect(loginUrl);
    }

    return null;
  }

  private static isProtectedRoute(pathname: string): boolean {
    const protectedRoutes = ['/dashboard', '/profile', '/settings'];
    return protectedRoutes.some(route => pathname.startsWith(route));
  }
}

// middleware/rate-limit.ts
export class RateLimitMiddleware {
  private static rateLimits = new Map<string, { count: number; resetTime: number }>();

  static handle(request: NextRequest) {
    const ip = request.ip;
    const now = Date.now();
    const limit = 100; // 100 requests per minute
    const windowMs = 60 * 1000;

    if (!this.rateLimits.has(ip)) {
      this.rateLimits.set(ip, { count: 1, resetTime: now + windowMs });
    } else {
      const record = this.rateLimits.get(ip)!;

      if (now > record.resetTime) {
        record.count = 1;
        record.resetTime = now + windowMs;
      } else {
        record.count++;

        if (record.count > limit) {
          return NextResponse.json(
            { error: 'Rate limit exceeded' },
            { status: 429 }
          );
        }
      }
    }

    return null;
  }
}

// middleware/security.ts
export class SecurityMiddleware {
  static handle(request: NextRequest) {
    const response = NextResponse.next();

    // 安全头
    response.headers.set('X-Frame-Options', 'DENY');
    response.headers.set('X-Content-Type-Options', 'nosniff');
    response.headers.set('X-XSS-Protection', '1; mode=block');
    response.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');

    // CSP
    if (process.env.NODE_ENV === 'production') {
      response.headers.set(
        'Content-Security-Policy',
        "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval';"
      );
    }

    return response;
  }
}

// middleware.ts
import { AuthMiddleware } from './middleware/auth';
import { RateLimitMiddleware } from './middleware/rate-limit';
import { SecurityMiddleware } from './middleware/security';

export function middleware(request: NextRequest) {
  // 1. 速率限制
  const rateLimitResponse = RateLimitMiddleware.handle(request);
  if (rateLimitResponse) return rateLimitResponse;

  // 2. 认证检查
  const authResponse = AuthMiddleware.handle(request);
  if (authResponse) return authResponse;

  // 3. 安全处理
  const securityResponse = SecurityMiddleware.handle(request);
  if (securityResponse) return securityResponse;

  return NextResponse.next();
}
```

### 2. 条件中间件

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

interface MiddlewareCondition {
  test: (request: NextRequest) => boolean;
  handler: (request: NextRequest) => NextResponse | null;
}

const middlewareConditions: MiddlewareCondition[] = [
  {
    test: (request) => request.nextUrl.pathname.startsWith('/api/'),
    handler: (request) => {
      // API特定的处理
      return null;
    },
  },
  {
    test: (request) => request.nextUrl.pathname.startsWith('/dashboard/'),
    handler: (request) => {
      // 仪表板特定的处理
      return null;
    },
  },
  {
    test: (request) => request.headers.get('user-agent')?.includes('Mobile'),
    handler: (request) => {
      // 移动设备特定的处理
      return null;
    },
  },
];

export function middleware(request: NextRequest) {
  // 执行匹配的条件处理器
  for (const condition of middlewareConditions) {
    if (condition.test(request)) {
      const result = condition.handler(request);
      if (result) return result;
    }
  }

  return NextResponse.next();
}
```

## 🚨 常见问题和解决方案

### 1. 中间件性能优化

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

// 预编译正则表达式
const STATIC_PATH_REGEX = /^\/(static|_next\/static|_next\/image|favicon\.ico)/;
const API_PATH_REGEX = /^\/api\//;

export function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // 快速路径：静态资源跳过中间件
  if (STATIC_PATH_REGEX.test(pathname)) {
    return NextResponse.next();
  }

  // 快速路径：API路由
  if (API_PATH_REGEX.test(pathname)) {
    return handleApiRequest(request);
  }

  // 默认处理
  return handlePageRequest(request);
}

function handleApiRequest(request: NextRequest) {
  // API特定的中间件逻辑
  return NextResponse.next();
}

function handlePageRequest(request: NextRequest) {
  // 页面特定的中间件逻辑
  return NextResponse.next();
}
```

### 2. 错误处理和调试

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export function middleware(request: NextRequest) {
  try {
    // 主要中间件逻辑
    return processRequest(request);
  } catch (error) {
    console.error('Middleware error:', error);

    // 返回友好的错误响应
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}

function processRequest(request: NextRequest) {
  // 添加调试头
  const response = NextResponse.next();
  response.headers.set('X-Middleware-Debug', 'true');
  response.headers.set('X-Middleware-Time', Date.now().toString());

  // 调试信息
  if (process.env.NODE_ENV === 'development') {
    console.log('Middleware processing:', {
      url: request.url,
      method: request.method,
      ip: request.ip,
      userAgent: request.headers.get('user-agent'),
    });
  }

  return response;
}
```

## 🎯 总结

Next.js 15 的中间件提供了强大的请求处理能力，运行在边缘网络上，为现代Web应用提供了高性能的请求拦截和处理能力。

### 关键要点：

1. **认证授权**：基于路由和角色的访问控制
2. **A/B测试**：智能的变体分配和测试
3. **地理本地化**：基于地理位置的内容适配
4. **性能优化**：缓存控制、压缩优化、安全头设置
5. **安全防护**：速率限制、Bot检测、安全检查
6. **分析监控**：请求跟踪、性能监控、用户行为分析

### 最佳实践：

- **性能优先**：使用快速路径减少不必要的处理
- **模块化设计**：将不同功能分离到独立的中间件类
- **错误处理**：完善的错误处理和调试机制
- **条件执行**：基于请求特征选择性地执行中间件逻辑
- **安全性**：实施适当的安全措施和防护

通过掌握这些中间件模式，可以构建出安全、高性能、功能丰富的现代Web应用。