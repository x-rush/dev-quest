# Next.js API 路由速查手册

## 📚 概述

Next.js 15 的 API 路由提供了强大的后端功能，支持 RESTful API、GraphQL、流式响应、文件上传等。本手册涵盖了所有 API 路由相关的功能和最佳实践。

## 🏗️ 基础 API 路由

### 路由处理器
**创建基本的 API 端点**

```typescript
// app/api/users/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

// 验证 schema
const createUserSchema = z.object({
  name: z.string().min(2, 'Name must be at least 2 characters'),
  email: z.string().email('Invalid email address'),
  age: z.number().min(18, 'Must be at least 18 years old'),
});

// GET 请求 - 获取所有用户
export async function GET() {
  try {
    const users = await getUsersFromDatabase();
    return NextResponse.json({
      success: true,
      data: users,
      count: users.length,
    });
  } catch (error) {
    console.error('Failed to fetch users:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch users',
        message: 'Internal server error',
      },
      { status: 500 }
    );
  }
}

// POST 请求 - 创建新用户
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    // 验证请求数据
    const validatedData = createUserSchema.parse(body);

    // 检查邮箱是否已存在
    const existingUser = await getUserByEmail(validatedData.email);
    if (existingUser) {
      return NextResponse.json(
        {
          success: false,
          error: 'Email already exists',
          field: 'email',
        },
        { status: 409 }
      );
    }

    const newUser = await createUserInDatabase(validatedData);

    return NextResponse.json({
      success: true,
      data: newUser,
      message: 'User created successfully',
    }, { status: 201 });

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          success: false,
          error: 'Validation failed',
          details: error.errors.map(err => ({
            field: err.path.join('.'),
            message: err.message,
          })),
        },
        { status: 400 }
      );
    }

    console.error('Failed to create user:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to create user',
        message: 'Internal server error',
      },
      { status: 500 }
    );
  }
}

// 数据库操作函数
async function getUsersFromDatabase() {
  // 实际的数据库实现
  return [
    {
      id: 1,
      name: 'John Doe',
      email: 'john@example.com',
      age: 25,
      createdAt: new Date().toISOString(),
    },
    {
      id: 2,
      name: 'Jane Smith',
      email: 'jane@example.com',
      age: 30,
      createdAt: new Date().toISOString(),
    },
  ];
}

async function getUserByEmail(email: string) {
  // 检查邮箱是否已存在
  const users = await getUsersFromDatabase();
  return users.find(user => user.email === email);
}

async function createUserInDatabase(userData: any) {
  // 创建用户的实际实现
  return {
    id: Date.now(),
    ...userData,
    createdAt: new Date().toISOString(),
  };
}
```

### 动态 API 路由
**处理动态参数**

```typescript
// app/api/users/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';

const idSchema = z.string().regex(/^\d+$/, 'Invalid ID format');

// 路由参数验证
function validateId(id: string) {
  const result = idSchema.safeParse(id);
  if (!result.success) {
    return {
      valid: false,
      error: 'Invalid user ID format',
    };
  }
  return { valid: true, parsedId: parseInt(result.data, 10) };
}

// GET 单个用户
export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const validation = validateId(params.id);
  if (!validation.valid) {
    return NextResponse.json(
      {
        success: false,
        error: validation.error,
      },
      { status: 400 }
    );
  }

  try {
    const user = await getUserById(validation.parsedId!);

    if (!user) {
      return NextResponse.json(
        {
          success: false,
          error: 'User not found',
          code: 'USER_NOT_FOUND',
        },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      data: user,
    });

  } catch (error) {
    console.error('Failed to fetch user:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch user',
      },
      { status: 500 }
    );
  }
}

// PUT 更新用户
export async function PUT(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const validation = validateId(params.id);
  if (!validation.valid) {
    return NextResponse.json(
      {
        success: false,
        error: validation.error,
      },
      { status: 400 }
    );
  }

  try {
    const body = await request.json();
    const updatedUser = await updateUserById(validation.parsedId!, body);

    if (!updatedUser) {
      return NextResponse.json(
        {
          success: false,
          error: 'User not found',
        },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      data: updatedUser,
      message: 'User updated successfully',
    });

  } catch (error) {
    console.error('Failed to update user:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to update user',
      },
      { status: 500 }
    );
  }
}

// DELETE 删除用户
export async function DELETE(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  const validation = validateId(params.id);
  if (!validation.valid) {
    return NextResponse.json(
      {
        success: false,
        error: validation.error,
      },
      { status: 400 }
    );
  }

  try {
    const deleted = await deleteUserById(validation.parsedId!);

    if (!deleted) {
      return NextResponse.json(
        {
          success: false,
          error: 'User not found',
        },
        { status: 404 }
      );
    }

    return NextResponse.json({
      success: true,
      message: 'User deleted successfully',
    });

  } catch (error) {
    console.error('Failed to delete user:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to delete user',
      },
      { status: 500 }
    );
  }
}

// 数据库操作函数
async function getUserById(id: number) {
  // 实际实现
  const users = await getUsersFromDatabase();
  return users.find(user => user.id === id);
}

async function updateUserById(id: number, updates: any) {
  // 实际实现
  const user = await getUserById(id);
  if (!user) return null;

  return { ...user, ...updates, updatedAt: new Date().toISOString() };
}

async function deleteUserById(id: number) {
  // 实际实现
  const user = await getUserById(id);
  return !!user;
}
```

## 🔐 认证和授权

### JWT 认证
**实现基于 JWT 的认证系统**

```typescript
// lib/auth.ts
import jwt from 'jsonwebtoken';
import { NextRequest } from 'next/server';

const JWT_SECRET = process.env.JWT_SECRET || 'your-secret-key';
const JWT_EXPIRES_IN = '7d';

export interface JWTPayload {
  userId: number;
  email: string;
  role: 'user' | 'admin';
}

// 生成 JWT
export function generateToken(payload: JWTPayload): string {
  return jwt.sign(payload, JWT_SECRET, { expiresIn: JWT_EXPIRES_IN });
}

// 验证 JWT
export function verifyToken(token: string): JWTPayload | null {
  try {
    return jwt.verify(token, JWT_SECRET) as JWTPayload;
  } catch (error) {
    return null;
  }
}

// 从请求中获取用户信息
export function getUserFromRequest(request: NextRequest): JWTPayload | null {
  const authHeader = request.headers.get('authorization');

  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return null;
  }

  const token = authHeader.substring(7);
  return verifyToken(token);
}

// 检查用户权限
export function requireAuth(
  request: NextRequest,
  requiredRole?: 'admin'
): { user: JWTPayload } | { error: string; status: number } {
  const user = getUserFromRequest(request);

  if (!user) {
    return { error: 'Authentication required', status: 401 };
  }

  if (requiredRole === 'admin' && user.role !== 'admin') {
    return { error: 'Admin access required', status: 403 };
  }

  return { user };
}

// app/api/auth/login/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { z } from 'zod';
import { generateToken } from '../../../lib/auth';

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(6),
});

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { email, password } = loginSchema.parse(body);

    // 验证用户凭据
    const user = await authenticateUser(email, password);
    if (!user) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid email or password',
        },
        { status: 401 }
      );
    }

    // 生成 JWT
    const token = generateToken({
      userId: user.id,
      email: user.email,
      role: user.role,
    });

    return NextResponse.json({
      success: true,
      data: {
        user: {
          id: user.id,
          name: user.name,
          email: user.email,
          role: user.role,
        },
        token,
      },
      message: 'Login successful',
    });

  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid input',
          details: error.errors,
        },
        { status: 400 }
      );
    }

    return NextResponse.json(
      {
        success: false,
        error: 'Login failed',
      },
      { status: 500 }
    );
  }
}

async function authenticateUser(email: string, password: string) {
  // 实际的用户认证实现
  const users = await getUsersFromDatabase();
  const user = users.find(u => u.email === email);

  if (user && await verifyPassword(password, user.password)) {
    return user;
  }

  return null;
}

// app/api/admin/users/route.ts - 受保护的 admin 端点
import { NextRequest, NextResponse } from 'next/server';
import { requireAuth } from '../../../lib/auth';

export async function GET(request: NextRequest) {
  const auth = requireAuth(request, 'admin');

  if ('error' in auth) {
    return NextResponse.json(
      {
        success: false,
        error: auth.error,
      },
      { status: auth.status }
    );
  }

  try {
    const users = await getAllUsers();
    return NextResponse.json({
      success: true,
      data: users,
    });

  } catch (error) {
    return NextResponse.json(
      {
        success: false,
        error: 'Failed to fetch users',
      },
      { status: 500 }
    );
  }
}
```

### Session 认证
**基于 Cookie 的 session 认证**

```typescript
// app/api/auth/session/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { serialize } from 'cookie';
import { createSession, getSession, deleteSession } from '../../../lib/session';

export async function GET(request: NextRequest) {
  const session = await getSession(request);

  if (!session) {
    return NextResponse.json(
      {
        success: false,
        error: 'No active session',
      },
      { status: 401 }
    );
  }

  return NextResponse.json({
    success: true,
    data: session,
  });
}

export async function DELETE(request: NextRequest) {
  await deleteSession();

  const response = NextResponse.json({
    success: true,
    message: 'Session ended successfully',
  });

  // 清除 session cookie
  response.headers.set(
    'Set-Cookie',
    serialize('session', '', {
      httpOnly: true,
      secure: process.env.NODE_ENV === 'production',
      sameSite: 'lax',
      maxAge: 0,
      path: '/',
    })
  );

  return response;
}

// lib/session.ts
import { NextRequest } from 'next/server';
import { encrypt, decrypt } from './encryption';

interface SessionData {
  userId: number;
  email: string;
  role: string;
}

export async function createSession(sessionData: SessionData) {
  const encryptedSession = encrypt(JSON.stringify(sessionData));

  return serialize('session', encryptedSession, {
    httpOnly: true,
    secure: process.env.NODE_ENV === 'production',
    sameSite: 'lax',
    maxAge: 7 * 24 * 60 * 60, // 7 days
    path: '/',
  });
}

export async function getSession(request: NextRequest): Promise<SessionData | null> {
  const sessionCookie = request.cookies.get('session');

  if (!sessionCookie) {
    return null;
  }

  try {
    const decryptedSession = decrypt(sessionCookie.value);
    return JSON.parse(decryptedSession) as SessionData;
  } catch (error) {
    return null;
  }
}

export async function deleteSession() {
  // Session 删除逻辑在调用方处理
}
```

## 📁 文件上传和处理

### 单文件上传
**处理文件上传请求**

```typescript
// app/api/upload/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;

    if (!file) {
      return NextResponse.json(
        {
          success: false,
          error: 'No file provided',
        },
        { status: 400 }
      );
    }

    // 验证文件类型
    const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      return NextResponse.json(
        {
          success: false,
          error: 'Invalid file type',
          allowedTypes,
        },
        { status: 400 }
      );
    }

    // 验证文件大小 (5MB)
    const maxSize = 5 * 1024 * 1024;
    if (file.size > maxSize) {
      return NextResponse.json(
        {
          success: false,
          error: 'File too large',
          maxSize: '5MB',
        },
        { status: 400 }
      );
    }

    // 创建上传目录
    const uploadDir = path.join(process.cwd(), 'public', 'uploads');
    await mkdir(uploadDir, { recursive: true });

    // 生成唯一文件名
    const timestamp = Date.now();
    const fileName = `${timestamp}-${file.name}`;
    const filePath = path.join(uploadDir, fileName);

    // 保存文件
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);
    await writeFile(filePath, buffer);

    return NextResponse.json({
      success: true,
      data: {
        fileName,
        filePath: `/uploads/${fileName}`,
        size: file.size,
        type: file.type,
      },
      message: 'File uploaded successfully',
    });

  } catch (error) {
    console.error('Upload error:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Upload failed',
      },
      { status: 500 }
    );
  }
}
```

### 多文件上传
**处理批量文件上传**

```typescript
// app/api/upload-multiple/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { writeFile, mkdir } from 'fs/promises';
import path from 'path';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const files = formData.getAll('files') as File[];

    if (!files || files.length === 0) {
      return NextResponse.json(
        {
          success: false,
          error: 'No files provided',
        },
        { status: 400 }
      );
    }

    const uploadedFiles = [];
    const errors = [];

    // 创建上传目录
    const uploadDir = path.join(process.cwd(), 'public', 'uploads');
    await mkdir(uploadDir, { recursive: true });

    for (const file of files) {
      try {
        // 验证文件
        const validation = validateFile(file);
        if (!validation.valid) {
          errors.push({
            fileName: file.name,
            error: validation.error,
          });
          continue;
        }

        // 保存文件
        const timestamp = Date.now();
        const fileName = `${timestamp}-${file.name}`;
        const filePath = path.join(uploadDir, fileName);

        const bytes = await file.arrayBuffer();
        const buffer = Buffer.from(bytes);
        await writeFile(filePath, buffer);

        uploadedFiles.push({
          originalName: file.name,
          fileName,
          filePath: `/uploads/${fileName}`,
          size: file.size,
          type: file.type,
        });

      } catch (error) {
        errors.push({
          fileName: file.name,
          error: 'Failed to process file',
        });
      }
    }

    return NextResponse.json({
      success: true,
      data: {
        uploadedFiles,
        errors,
        totalFiles: files.length,
        successfulUploads: uploadedFiles.length,
        failedUploads: errors.length,
      },
    });

  } catch (error) {
    console.error('Multiple upload error:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'Upload failed',
      },
      { status: 500 }
    );
  }
}

function validateFile(file: File) {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
  const maxSize = 5 * 1024 * 1024; // 5MB

  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Invalid file type',
    };
  }

  if (file.size > maxSize) {
    return {
      valid: false,
      error: 'File too large',
    };
  }

  return { valid: true };
}
```

## 🔄 流式响应

### Server-Sent Events
**实现实时数据推送**

```typescript
// app/api/stream/route.ts
import { NextResponse } from 'next/server';

export async function GET() {
  const encoder = new TextEncoder();

  const stream = new ReadableStream({
    async start(controller) {
      try {
        // 发送初始连接消息
        const initialMessage = {
          type: 'connection',
          message: 'Connected to stream',
          timestamp: new Date().toISOString(),
        };
        controller.enqueue(encoder.encode(`data: ${JSON.stringify(initialMessage)}\n\n`));

        // 模拟定期发送数据
        let counter = 0;
        const interval = setInterval(() => {
          counter++;

          const data = {
            type: 'update',
            id: counter,
            message: `Update ${counter}`,
            timestamp: new Date().toISOString(),
            random: Math.random(),
          };

          controller.enqueue(encoder.encode(`data: ${JSON.stringify(data)}\n\n`));

          // 10次后关闭连接
          if (counter >= 10) {
            clearInterval(interval);
            controller.close();
          }
        }, 1000);

        // 清理函数
        return () => {
          clearInterval(interval);
        };

      } catch (error) {
        controller.error(error);
      }
    },
  });

  return new Response(stream, {
    headers: {
      'Content-Type': 'text/event-stream',
      'Cache-Control': 'no-cache',
      'Connection': 'keep-alive',
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'GET',
      'Access-Control-Allow-Headers': 'Content-Type',
    },
  });
}

// 客户端使用示例
'use client';

import { useEffect, useState } from 'react';

function StreamComponent() {
  const [messages, setMessages] = useState<any[]>([]);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    const eventSource = new EventSource('/api/stream');

    eventSource.onopen = () => {
      console.log('Connected to stream');
      setIsConnected(true);
    };

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);
        setMessages(prev => [...prev, data]);
      } catch (error) {
        console.error('Failed to parse message:', error);
      }
    };

    eventSource.onerror = (error) => {
      console.error('Stream error:', error);
      setIsConnected(false);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <div>
      <h2>Real-time Stream</h2>
      <p>Status: {isConnected ? 'Connected' : 'Disconnected'}</p>

      <div>
        {messages.map((msg, index) => (
          <div key={index} style={{ margin: '8px 0', padding: '8px', border: '1px solid #ccc' }}>
            <strong>{msg.type}:</strong> {msg.message}
            <br />
            <small>{new Date(msg.timestamp).toLocaleTimeString()}</small>
          </div>
        ))}
      </div>
    </div>
  );
}
```

### 流式文件下载
**实现大文件流式下载**

```typescript
// app/api/download/[id]/route.ts
import { NextRequest, NextResponse } from 'next/server';
import { createReadStream, statSync } from 'fs';
import path from 'path';

export async function GET(
  request: NextRequest,
  { params }: { params: { id: string } }
) {
  try {
    const fileId = params.id;

    // 获取文件信息
    const filePath = path.join(process.cwd(), 'files', `${fileId}.pdf`);
    const fileStats = statSync(filePath);

    // 设置响应头
    const headers = new Headers({
      'Content-Type': 'application/pdf',
      'Content-Length': fileStats.size.toString(),
      'Content-Disposition': `attachment; filename="document-${fileId}.pdf"`,
      'Cache-Control': 'public, max-age=3600',
    });

    // 处理 Range 请求 (支持断点续传)
    const rangeHeader = request.headers.get('range');

    if (rangeHeader) {
      const parts = rangeHeader.replace(/bytes=/, '').split('-');
      const start = parseInt(parts[0], 10);
      const end = parts[1] ? parseInt(parts[1], 10) : fileStats.size - 1;
      const chunkSize = (end - start) + 1;

      headers.set('Content-Range', `bytes ${start}-${end}/${fileStats.size}`);
      headers.set('Accept-Ranges', 'bytes');
      headers.set('Content-Length', chunkSize.toString());

      const fileStream = createReadStream(filePath, { start, end });

      return new Response(fileStream as any, {
        status: 206, // Partial Content
        headers,
      });
    }

    // 完整文件响应
    const fileStream = createReadStream(filePath);

    return new Response(fileStream as any, {
      status: 200,
      headers,
    });

  } catch (error) {
    console.error('Download error:', error);
    return NextResponse.json(
      {
        success: false,
        error: 'File not found or download failed',
      },
      { status: 404 }
    );
  }
}
```

## 🔄 CORS 和中间件

### CORS 配置
**处理跨域请求**

```typescript
// lib/cors.ts
import { NextRequest, NextResponse } from 'next/server';

const corsOrigins = [
  'http://localhost:3000',
  'https://yourdomain.com',
  'https://www.yourdomain.com',
];

export function handleCors(request: NextRequest, response?: NextResponse) {
  const origin = request.headers.get('origin');

  const isAllowedOrigin = corsOrigins.includes(origin || '');

  const headers = {
    'Access-Control-Allow-Origin': isAllowedOrigin ? origin : 'false',
    'Access-Control-Allow-Methods': 'GET, POST, PUT, DELETE, OPTIONS',
    'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Requested-With',
    'Access-Control-Allow-Credentials': 'true',
    'Access-Control-Max-Age': '86400', // 24 hours
  };

  if (response) {
    Object.entries(headers).forEach(([key, value]) => {
      response.headers.set(key, value);
    });
    return response;
  }

  return new NextResponse(null, { headers });
}

// 在 API 路由中使用
export async function OPTIONS(request: NextRequest) {
  return handleCors(request, new NextResponse(null, { status: 200 }));
}

export async function GET(request: NextRequest) {
  const response = NextResponse.json({ message: 'Hello World' });
  return handleCors(request, response);
}
```

### API 限流
**实现请求频率限制**

```typescript
// lib/rate-limiter.ts
import { NextRequest } from 'next/server';

interface RateLimitData {
  count: number;
  resetTime: number;
}

const rateLimitStore = new Map<string, RateLimitData>();

export function rateLimit(
  request: NextRequest,
  limit: number = 100,
  windowMs: number = 60 * 1000 // 1 minute
): { success: boolean; remaining: number; resetTime: number } {
  const clientId = request.ip || 'unknown';
  const now = Date.now();
  const windowStart = now - windowMs;

  // 清理过期记录
  for (const [key, data] of rateLimitStore.entries()) {
    if (data.resetTime < windowStart) {
      rateLimitStore.delete(key);
    }
  }

  // 获取或创建客户端记录
  let clientData = rateLimitStore.get(clientId);

  if (!clientData || clientData.resetTime < windowStart) {
    clientData = {
      count: 0,
      resetTime: now + windowMs,
    };
    rateLimitStore.set(clientId, clientData);
  }

  // 检查限制
  if (clientData.count >= limit) {
    return {
      success: false,
      remaining: 0,
      resetTime: clientData.resetTime,
    };
  }

  // 增加计数
  clientData.count++;

  return {
    success: true,
    remaining: limit - clientData.count,
    resetTime: clientData.resetTime,
  };
}

// 在 API 路由中使用
export async function POST(request: NextRequest) {
  const rateLimitResult = rateLimit(request, 10, 60 * 1000); // 10 requests per minute

  if (!rateLimitResult.success) {
    return NextResponse.json(
      {
        success: false,
        error: 'Rate limit exceeded',
        retryAfter: Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000),
      },
      {
        status: 429,
        headers: {
          'X-RateLimit-Limit': '10',
          'X-RateLimit-Remaining': '0',
          'X-RateLimit-Reset': rateLimitResult.resetTime.toString(),
          'Retry-After': Math.ceil((rateLimitResult.resetTime - Date.now()) / 1000).toString(),
        },
      }
    );
  }

  // 处理正常请求
  const response = NextResponse.json({
    success: true,
    message: 'Request processed',
  });

  // 添加限流头
  response.headers.set('X-RateLimit-Limit', '10');
  response.headers.set('X-RateLimit-Remaining', rateLimitResult.remaining.toString());
  response.headers.set('X-RateLimit-Reset', rateLimitResult.resetTime.toString());

  return response;
}
```

## 📊 错误处理和日志

### 全局错误处理
**统一的错误处理机制**

```typescript
// lib/api-error.ts
export class APIError extends Error {
  public statusCode: number;
  public code: string;
  public details?: any;

  constructor(
    message: string,
    statusCode: number = 500,
    code: string = 'INTERNAL_ERROR',
    details?: any
  ) {
    super(message);
    this.name = 'APIError';
    this.statusCode = statusCode;
    this.code = code;
    this.details = details;
  }
}

// 预定义错误类型
export class ValidationError extends APIError {
  constructor(message: string, details?: any) {
    super(message, 400, 'VALIDATION_ERROR', details);
  }
}

export class NotFoundError extends APIError {
  constructor(resource: string) {
    super(`${resource} not found`, 404, 'NOT_FOUND');
  }
}

export class UnauthorizedError extends APIError {
  constructor(message: string = 'Unauthorized') {
    super(message, 401, 'UNAUTHORIZED');
  }
}

export class ForbiddenError extends APIError {
  constructor(message: string = 'Forbidden') {
    super(message, 403, 'FORBIDDEN');
  }
}

// 错误处理中间件
export function handleAPIError(error: unknown): NextResponse {
  console.error('API Error:', error);

  if (error instanceof APIError) {
    return NextResponse.json(
      {
        success: false,
        error: error.message,
        code: error.code,
        ...(error.details && { details: error.details }),
      },
      { status: error.statusCode }
    );
  }

  if (error instanceof z.ZodError) {
    return NextResponse.json(
      {
        success: false,
        error: 'Validation failed',
        code: 'VALIDATION_ERROR',
        details: error.errors.map(err => ({
          field: err.path.join('.'),
          message: err.message,
        })),
      },
      { status: 400 }
    );
  }

  // 未知错误
  return NextResponse.json(
    {
      success: false,
      error: 'Internal server error',
      code: 'INTERNAL_ERROR',
    },
    { status: 500 }
  );
}

// 使用示例
export async function POST(request: NextRequest) {
  try {
    const body = await request.json();

    if (!body.email) {
      throw new ValidationError('Email is required');
    }

    // 处理请求逻辑
    const result = await processRequest(body);

    return NextResponse.json({
      success: true,
      data: result,
    });

  } catch (error) {
    return handleAPIError(error);
  }
}
```

### API 日志记录
**记录 API 请求和响应**

```typescript
// lib/logger.ts
export interface LogEntry {
  timestamp: string;
  method: string;
  url: string;
  statusCode: number;
  responseTime: number;
  userAgent?: string;
  ip?: string;
  userId?: string;
  error?: string;
}

class APILogger {
  private logs: LogEntry[] = [];

  log(entry: LogEntry) {
    this.logs.push(entry);

    // 在生产环境中，这里可以发送到日志服务
    if (process.env.NODE_ENV === 'production') {
      this.sendToLogService(entry);
    } else {
      console.log('API Log:', entry);
    }

    // 保持日志数组大小合理
    if (this.logs.length > 1000) {
      this.logs = this.logs.slice(-500);
    }
  }

  private async sendToLogService(entry: LogEntry) {
    try {
      // 发送到外部日志服务 (如 LogRocket, Sentry, 等)
      await fetch('https://logs.example.com/api/logs', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(entry),
      });
    } catch (error) {
      console.error('Failed to send log:', error);
    }
  }

  getLogs(): LogEntry[] {
    return [...this.logs];
  }

  clearLogs() {
    this.logs = [];
  }
}

export const apiLogger = new APILogger();

// 使用中间件包装 API 路由
export function withLogging(handler: Function) {
  return async (request: NextRequest, ...args: any[]) => {
    const startTime = Date.now();
    const url = request.url;
    const method = request.method;

    try {
      const response = await handler(request, ...args);

      const responseTime = Date.now() - startTime;
      const statusCode = response instanceof Response ? response.status : 200;

      apiLogger.log({
        timestamp: new Date().toISOString(),
        method,
        url,
        statusCode,
        responseTime,
        userAgent: request.headers.get('user-agent') || undefined,
        ip: request.ip || undefined,
      });

      return response;

    } catch (error) {
      const responseTime = Date.now() - startTime;

      apiLogger.log({
        timestamp: new Date().toISOString(),
        method,
        url,
        statusCode: 500,
        responseTime,
        userAgent: request.headers.get('user-agent') || undefined,
        ip: request.ip || undefined,
        error: error instanceof Error ? error.message : 'Unknown error',
      });

      throw error;
    }
  };
}
```

## 📖 总结

Next.js 15 的 API 路由提供了完整的后端功能：

### 核心功能：
1. **路由处理器**: 支持 GET、POST、PUT、DELETE 等方法
2. **动态路由**: 处理 URL 参数
3. **认证授权**: JWT 和 Session 认证
4. **文件上传**: 单文件和多文件上传
5. **流式响应**: SSE 和文件流
6. **错误处理**: 统一的错误处理机制

### 最佳实践：
1. **输入验证**: 使用 Zod 进行数据验证
2. **错误处理**: 提供详细的错误信息
3. **安全性**: 实施认证和授权
4. **性能**: 使用缓存和限流
5. **监控**: 记录请求和错误日志

通过这些模式，你可以构建功能完整、安全可靠的 API 服务。