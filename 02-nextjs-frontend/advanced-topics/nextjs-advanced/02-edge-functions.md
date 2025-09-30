# Next.js 15 Edge Functions 深度解析

## 📋 概述

Next.js 15 的 Edge Functions 让你能够在全球边缘网络上运行代码，提供更快的响应时间和更好的用户体验。Edge Functions 运行在 V8 引擎中，支持 Web APIs，并且能够访问请求和响应对象。

## 🎯 Edge Functions 基础

### 1. 什么是 Edge Functions？

Edge Functions 是在 CDN 边缘网络上运行的 JavaScript 函数，它们：

- **低延迟**：在用户地理位置附近运行
- **高可用性**：自动扩展和故障转移
- **轻量级**：冷启动时间极短
- **Web API 兼容**：支持 Fetch API、Request、Response 等

### 2. 与 API Routes 的对比

| 特性 | API Routes | Edge Functions |
|------|------------|----------------|
| 运行环境 | Node.js | V8 Isolate |
| 冷启动 | 较慢 | 极快 |
| 运行位置 | 区域服务器 | 全球边缘节点 |
| 内存限制 | 1GB | 128MB |
| 执行时间 | 30秒 | 30秒 |
| Web APIs | Node.js API | Web APIs |

## 🚀 Edge Functions 实现

### 1. 基本 Edge Function

```typescript
// app/api/edge/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const name = searchParams.get('name') || 'World';

  // 访问请求头
  const userAgent = request.headers.get('user-agent');
  const ip = request.ip;

  // 访问地理位置信息
  const country = request.geo?.country;
  const city = request.geo?.city;

  return NextResponse.json({
    message: `Hello ${name}!`,
    userAgent,
    ip,
    location: {
      country,
      city,
    },
    timestamp: new Date().toISOString(),
    edge: true,
  });
}

export async function POST(request: NextRequest) {
  const body = await request.json();

  // 处理文件上传
  const formData = await request.formData();
  const file = formData.get('file') as File;

  if (file) {
    // 处理文件
    const arrayBuffer = await file.arrayBuffer();
    const buffer = new Uint8Array(arrayBuffer);

    // 可以上传到对象存储
    // const result = await uploadToS3(buffer, file.name);
  }

  return NextResponse.json({
    received: body,
    processed: true,
  });
}
```

### 2. 中间件 Edge Function

```typescript
// middleware.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const config = {
  matcher: [
    '/((?!_next/static|_next/image|favicon.ico).*)',
  ],
};

export function middleware(request: NextRequest) {
  // 1. 认证检查
  const token = request.cookies.get('auth-token')?.value;
  const isAuthPage = request.nextUrl.pathname.startsWith('/auth');
  const isProtectedRoute = request.nextUrl.pathname.startsWith('/dashboard');

  if (isProtectedRoute && !token) {
    return NextResponse.redirect(new URL('/auth/login', request.url));
  }

  if (isAuthPage && token) {
    return NextResponse.redirect(new URL('/dashboard', request.url));
  }

  // 2. 地理位置重定向
  const country = request.geo?.country;
  if (country === 'CN' && !request.nextUrl.pathname.startsWith('/cn')) {
    return NextResponse.redirect(new URL('/cn', request.url));
  }

  // 3. A/B 测试
  const abTestVariant = request.cookies.get('ab-test-variant')?.value;
  if (!abTestVariant) {
    const variant = Math.random() > 0.5 ? 'A' : 'B';
    const response = NextResponse.next();
    response.cookies.set('ab-test-variant', variant);
    return response;
  }

  // 4. 设备检测
  const userAgent = request.headers.get('user-agent') || '';
  const isMobile = /Mobile|Android|iPhone/.test(userAgent);

  if (isMobile && !request.nextUrl.pathname.startsWith('/mobile')) {
    return NextResponse.redirect(new URL('/mobile', request.url));
  }

  // 5. 缓存控制
  const response = NextResponse.next();
  response.headers.set('Cache-Control', 'public, max-age=3600');

  // 6. 安全头
  response.headers.set('X-Frame-Options', 'DENY');
  response.headers.set('X-Content-Type-Options', 'nosniff');
  response.headers.set('Referrer-Policy', 'origin-when-cross-origin');

  return response;
}
```

### 3. 静态站点生成（SSG）Edge Function

```typescript
// app/ssg/page.tsx
import { unstable_cache } from 'next/cache';

async function getData() {
  const response = await fetch('https://api.example.com/data');
  return response.json();
}

const getCachedData = unstable_cache(
  async () => getData(),
  ['data-cache'],
  {
    revalidate: 3600, // 1小时
    tags: ['data'],
  }
);

export default async function SSGPage() {
  const data = await getCachedData();

  return (
    <div>
      <h1>Static Site Generation with Edge</h1>
      <pre>{JSON.stringify(data, null, 2)}</pre>
    </div>
  );
}

export async function generateMetadata() {
  return {
    title: 'SSG with Edge Functions',
    description: 'Generated at the edge',
  };
}
```

## 🎨 高级 Edge Functions 模式

### 1. 代理和转发

```typescript
// app/api/proxy/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const targetUrl = request.nextUrl.searchParams.get('url');

  if (!targetUrl) {
    return NextResponse.json(
      { error: 'Missing URL parameter' },
      { status: 400 }
    );
  }

  try {
    const response = await fetch(targetUrl, {
      headers: {
        // 转发请求头
        'User-Agent': request.headers.get('user-agent') || '',
        'Accept': request.headers.get('accept') || '',
      },
    });

    const data = await response.json();

    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Proxy request failed' },
      { status: 500 }
    );
  }
}

// 代理文件下载
export async function POST(request: NextRequest) {
  const { url, filename } = await request.json();

  const response = await fetch(url);
  const arrayBuffer = await response.arrayBuffer();

  return new NextResponse(arrayBuffer, {
    headers: {
      'Content-Type': 'application/octet-stream',
      'Content-Disposition': `attachment; filename="${filename}"`,
    },
  });
}
```

### 2. 实时数据处理

```typescript
// app/api/realtime/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  // 1. 实时天气数据
  const city = request.nextUrl.searchParams.get('city') || 'beijing';
  const weatherResponse = await fetch(
    `https://api.weather.com/v1/weather?q=${city}&appid=${process.env.WEATHER_API_KEY}`
  );
  const weatherData = await weatherResponse.json();

  // 2. 实时汇率转换
  const baseCurrency = request.nextUrl.searchParams.get('base') || 'USD';
  const targetCurrency = request.nextUrl.searchParams.get('target') || 'CNY';
  const rateResponse = await fetch(
    `https://api.exchangerate-api.com/v4/latest/${baseCurrency}`
  );
  const rateData = await rateResponse.json();

  // 3. 实时股票价格
  const symbol = request.nextUrl.searchParams.get('symbol') || 'AAPL';
  const stockResponse = await fetch(
    `https://api.twelvedata.com/time_series?symbol=${symbol}&interval=1min&apikey=${process.env.STOCK_API_KEY}`
  );
  const stockData = await stockResponse.json();

  return NextResponse.json({
    weather: weatherData,
    exchange: {
      base: baseCurrency,
      target: targetCurrency,
      rate: rateData.rates[targetCurrency],
    },
    stock: stockData,
    timestamp: new Date().toISOString(),
  });
}
```

### 3. 内容优化和转换

```typescript
// app/api/optimize/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const file = formData.get('image') as File;

  if (!file) {
    return NextResponse.json(
      { error: 'No image provided' },
      { status: 400 }
    );
  }

  try {
    // 1. 图像优化
    const arrayBuffer = await file.arrayBuffer();
    const buffer = new Uint8Array(arrayBuffer);

    // 2. 格式转换
    const format = formData.get('format') || 'webp';
    const quality = parseInt(formData.get('quality') as string) || 80;

    // 3. 尺寸调整
    const width = parseInt(formData.get('width') as string) || 800;
    const height = parseInt(formData.get('height') as string) || 600;

    // 注意：这里需要使用适当的图像处理库
    // 由于Edge Functions的限制，可能需要调用外部API

    return NextResponse.json({
      message: 'Image optimized successfully',
      format,
      quality,
      dimensions: { width, height },
      originalSize: file.size,
      optimizedSize: Math.floor(file.size * (quality / 100)),
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Image optimization failed' },
      { status: 500 }
    );
  }
}
```

## 🔄 集成外部服务

### 1. 数据库集成

```typescript
// app/api/database/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const id = request.nextUrl.searchParams.get('id');

  try {
    // 使用 PlanetScale (Edge-compatible database)
    const response = await fetch(`${process.env.DATABASE_URL}/query`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.DATABASE_TOKEN}`,
      },
      body: JSON.stringify({
        sql: 'SELECT * FROM users WHERE id = ?',
        params: [id],
      }),
    });

    const data = await response.json();

    return NextResponse.json(data);
  } catch (error) {
    return NextResponse.json(
      { error: 'Database query failed' },
      { status: 500 }
    );
  }
}
```

### 2. 第三方API集成

```typescript
// app/api/integration/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  const { service, data } = await request.json();

  try {
    let result;

    switch (service) {
      case 'email':
        // 发送邮件
        result = await fetch('https://api.sendgrid.com/v3/mail/send', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${process.env.SENDGRID_API_KEY}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(data),
        });
        break;

      case 'sms':
        // 发送短信
        result = await fetch('https://api.twilio.com/2010-04-01/Accounts', {
          method: 'POST',
          headers: {
            'Authorization': `Basic ${process.env.TWILIO_AUTH}`,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams(data).toString(),
        });
        break;

      case 'payment':
        // 处理支付
        result = await fetch('https://api.stripe.com/v1/payment_intents', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${process.env.STRIPE_SECRET_KEY}`,
            'Content-Type': 'application/x-www-form-urlencoded',
          },
          body: new URLSearchParams(data).toString(),
        });
        break;

      default:
        return NextResponse.json(
          { error: 'Unknown service' },
          { status: 400 }
        );
    }

    const responseData = await result.json();

    return NextResponse.json({
      success: result.ok,
      data: responseData,
    });
  } catch (error) {
    return NextResponse.json(
      { error: 'Integration failed' },
      { status: 500 }
    );
  }
}
```

### 3. CDN 和缓存集成

```typescript
// app/api/cdn/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const path = request.nextUrl.searchParams.get('path');
  const purge = request.nextUrl.searchParams.get('purge') === 'true';

  if (!path) {
    return NextResponse.json(
      { error: 'Missing path parameter' },
      { status: 400 }
    );
  }

  try {
    if (purge) {
      // 清除CDN缓存
      const purgeResponse = await fetch(`${process.env.CDN_API}/purge`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${process.env.CDN_TOKEN}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ files: [path] }),
      });

      if (!purgeResponse.ok) {
        throw new Error('CDN purge failed');
      }

      return NextResponse.json({
        message: 'CDN cache purged successfully',
        path,
      });
    } else {
      // 预热CDN缓存
      const warmResponse = await fetch(`https://cdn.example.com${path}`);

      return NextResponse.json({
        message: 'CDN cache warmed successfully',
        path,
        status: warmResponse.status,
      });
    }
  } catch (error) {
    return NextResponse.json(
      { error: 'CDN operation failed' },
      { status: 500 }
    );
  }
}
```

## 🎯 安全和性能最佳实践

### 1. 安全验证

```typescript
// app/api/security/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  const { token, data } = await request.json();

  // 1. Token验证
  if (!token || token !== process.env.API_TOKEN) {
    return NextResponse.json(
      { error: 'Invalid token' },
      { status: 401 }
    );
  }

  // 2. Rate limiting (使用KV存储)
  const ip = request.ip;
  const key = `rate_limit:${ip}`;
  const current = await KV.get(key);

  if (current && parseInt(current) > 100) {
    return NextResponse.json(
      { error: 'Rate limit exceeded' },
      { status: 429 }
    );
  }

  await KV.put(key, (parseInt(current || '0') + 1).toString(), {
    expirationTtl: 60, // 1分钟
  });

  // 3. 数据验证
  if (!data || typeof data !== 'object') {
    return NextResponse.json(
      { error: 'Invalid data format' },
      { status: 400 }
    );
  }

  // 4. 处理业务逻辑
  return NextResponse.json({
    message: 'Request processed successfully',
    data,
  });
}
```

### 2. 性能监控

```typescript
// app/api/monitor/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const startTime = Date.now();

  try {
    // 模拟业务逻辑
    await new Promise(resolve => setTimeout(resolve, 100));

    const endTime = Date.now();
    const duration = endTime - startTime;

    // 记录性能指标
    const metrics = {
      duration,
      timestamp: endTime,
      endpoint: request.nextUrl.pathname,
      method: request.method,
      userAgent: request.headers.get('user-agent'),
      ip: request.ip,
      geo: request.geo,
    };

    // 发送到监控服务
    await fetch(process.env.MONITORING_WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(metrics),
    });

    return NextResponse.json({
      status: 'ok',
      metrics,
    });
  } catch (error) {
    const endTime = Date.now();
    const duration = endTime - startTime;

    // 记录错误
    await fetch(process.env.ERROR_WEBHOOK, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        error: error.message,
        duration,
        endpoint: request.nextUrl.pathname,
        timestamp: endTime,
      }),
    });

    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    );
  }
}
```

## 🚨 常见模式和用例

### 1. A/B 测试框架

```typescript
// app/api/ab-test/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function GET(request: NextRequest) {
  const experiment = request.nextUrl.searchParams.get('experiment');
  const userId = request.headers.get('x-user-id');

  if (!experiment || !userId) {
    return NextResponse.json(
      { error: 'Missing parameters' },
      { status: 400 }
    );
  }

  // 从KV获取用户变体分配
  const variantKey = `ab:${experiment}:${userId}`;
  let variant = await KV.get(variantKey);

  if (!variant) {
    // 分配新用户到变体
    const hash = await crypto.subtle.digest(
      'SHA-256',
      new TextEncoder().encode(`${experiment}:${userId}`)
    );
    const hashArray = new Uint8Array(hash);
    const variantIndex = hashArray[0] % 2;
    variant = variantIndex === 0 ? 'A' : 'B';

    // 保存分配结果
    await KV.put(variantKey, variant, {
      expirationTtl: 86400, // 24小时
    });
  }

  // 获取变体配置
  const configKey = `ab:${experiment}:${variant}`;
  const config = await KV.get(configKey);

  return NextResponse.json({
    experiment,
    variant,
    config: config ? JSON.parse(config) : null,
    timestamp: Date.now(),
  });
}
```

### 2. 实时分析

```typescript
// app/api/analytics/route.ts
import { NextResponse } from 'next/server';
import type { NextRequest } from 'next/server';

export const runtime = 'edge';

export async function POST(request: NextRequest) {
  const { event, properties } = await request.json();

  // 验证事件数据
  if (!event || !properties) {
    return NextResponse.json(
      { error: 'Invalid event data' },
      { status: 400 }
    );
  }

  // 添加上下文信息
  const enrichedEvent = {
    event,
    properties: {
      ...properties,
      timestamp: Date.now(),
      userAgent: request.headers.get('user-agent'),
      ip: request.ip,
      geo: request.geo,
      url: request.url,
    },
  };

  // 批量处理事件
  const batchKey = `analytics_batch:${Date.now()}`;
  const existingBatch = await KV.get(batchKey);
  const batch = existingBatch ? JSON.parse(existingBatch) : [];
  batch.push(enrichedEvent);

  await KV.put(batchKey, JSON.stringify(batch), {
    expirationTtl: 300, // 5分钟
  });

  // 如果批次达到一定大小，立即处理
  if (batch.length >= 10) {
    await processAnalyticsBatch(batch);
    await KV.delete(batchKey);
  }

  return NextResponse.json({
    success: true,
    eventId: enrichedEvent.properties.timestamp,
  });
}

async function processAnalyticsBatch(batch: any[]) {
  // 发送到分析服务
  await fetch(process.env.ANALYTICS_ENDPOINT, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ batch }),
  });
}
```

## 🎯 总结

Next.js 15 的 Edge Functions 提供了强大的边缘计算能力，让开发者能够在全球边缘网络上运行高性能的代码。通过合理使用 Edge Functions，可以显著提升应用的性能和用户体验。

### 关键要点：

1. **性能优势**：低延迟、高可用性、快速冷启动
2. **使用场景**：中间件、API代理、实时数据处理、内容优化
3. **集成能力**：数据库、第三方服务、CDN缓存
4. **最佳实践**：安全验证、性能监控、错误处理
5. **模式应用**：A/B测试、实时分析、地理个性化

Edge Functions 是现代Web应用架构的重要组成部分，特别适合需要全球部署和高性能的场景。通过掌握这些技术，可以构建出真正意义上的全球应用。