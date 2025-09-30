# 全栈社交媒体平台实战 (Full-Stack Social Media Platform)

> **PHP开发者视角**: 从Laravel全栈开发到Next.js全栈开发的转变，了解现代全栈应用的最佳实践和性能优化策略。

## 项目概述

### 技术栈
- **前端**: Next.js 15, React 19, TypeScript, Tailwind CSS
- **后端**: Next.js API Routes, Server Actions
- **数据库**: PostgreSQL + Prisma ORM
- **认证**: NextAuth.js v5
- **实时通信**: WebSocket, Pusher
- **文件存储**: AWS S3
- **缓存**: Redis
- **部署**: Vercel + Railway

### 核心功能
- 用户认证和授权系统
- 动态发布和互动（点赞、评论、分享）
- 实时通知系统
- 即时消息功能
- 图片/视频上传和处理
- 用户资料和设置
- 搜索和推荐算法
- 管理员后台

## 项目初始化

### 1. 创建项目结构

```bash
# 创建Next.js项目
npx create-next-app@latest social-media-platform --typescript --tailwind --eslint --app --src-dir --import-alias "@/*"

# 进入项目目录
cd social-media-platform

# 安装依赖
npm install @prisma/client prisma next-auth@beta @auth/prisma-adapter
npm install @uploadthing/react uploadthing @tanstack/react-query
npm install @radix-ui/react-icons lucide-react class-variance-authority
npm install clsx tailwind-merge react-hook-form @hookform/resolvers zod
npm install recharts framer-motion react-hot-toast
npm install pusher-js @pusher/ruby-server socket.io-client
npm install sharp ffmpeg-static

# 开发依赖
npm install -D @types/node @types/react prisma-dbml-generator
```

### 2. 配置环境变量

```env
# .env.local
# 数据库
DATABASE_URL="postgresql://username:password@localhost:5432/social_media"

# NextAuth.js
NEXTAUTH_SECRET="your-nextauth-secret"
NEXTAUTH_URL="http://localhost:3000"

# OAuth提供者
GITHUB_CLIENT_ID="your-github-client-id"
GITHUB_CLIENT_SECRET="your-github-client-secret"
GOOGLE_CLIENT_ID="your-google-client-id"
GOOGLE_CLIENT_SECRET="your-google-client-secret"

# 文件上传
UPLOADTHING_SECRET="your-uploadthing-secret"
UPLOADTHING_APP_ID="your-uploadthing-app-id"

# Redis (用于缓存)
REDIS_URL="redis://localhost:6379"

# Pusher (实时通信)
PUSHER_APP_ID="your-pusher-app-id"
PUSHER_KEY="your-pusher-key"
PUSHER_SECRET="your-pusher-secret"
PUSHER_CLUSTER="your-pusher-cluster"

# AWS S3
AWS_ACCESS_KEY_ID="your-aws-access-key"
AWS_SECRET_ACCESS_KEY="your-aws-secret-key"
AWS_REGION="your-aws-region"
AWS_S3_BUCKET="your-s3-bucket"
```

### 3. 数据库设计

```prisma
// prisma/schema.prisma
generator client {
  provider = "prisma-client-js"
}

datasource db {
  provider = "postgresql"
  url      = env("DATABASE_URL")
}

model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String?
  access_token      String?
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String?
  session_state     String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
}

model User {
  id            String    @id @default(cuid())
  name          String?
  email         String    @unique
  emailVerified DateTime?
  image         String?
  bio           String?
  username      String?   @unique
  website      String?
  location      String?
  birthDate     DateTime?
  gender        String?
  isPrivate     Boolean   @default(false)
  isAdmin       Boolean   @default(false)
  createdAt     DateTime  @default(now())
  updatedAt     DateTime  @updatedAt

  accounts      Account[]
  sessions      Session[]
  posts         Post[]
  comments      Comment[]
  likes         Like[]
  followers     Follow[] @relation("UserFollowing")
  following     Follow[] @relation("UserFollowers")
  notifications Notification[]
  messages      Message[] @relation("MessageSender")
  receivedMessages Message[] @relation("MessageReceiver")
}

model Post {
  id        String   @id @default(cuid())
  content   String?
  image     String?
  video     String?
  userId    String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  user     User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  comments Comment[]
  likes    Like[]
  shares   Share[]
}

model Comment {
  id        String   @id @default(cuid())
  content   String
  userId    String
  postId    String
  parentId  String?
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  user     User      @relation(fields: [userId], references: [id], onDelete: Cascade)
  post     Post      @relation(fields: [postId], references: [id], onDelete: Cascade)
  parent   Comment?  @relation("CommentReplies", fields: [parentId], references: [id])
  replies  Comment[] @relation("CommentReplies")
  likes    Like[]
}

model Like {
  id        String   @id @default(cuid())
  userId    String
  postId    String?
  commentId String?
  createdAt DateTime @default(now())

  user    User     @relation(fields: [userId], references: [id], onDelete: Cascade)
  post    Post?    @relation(fields: [postId], references: [id], onDelete: Cascade)
  comment Comment? @relation(fields: [commentId], references: [id], onDelete: Cascade)

  @@unique([userId, postId])
  @@unique([userId, commentId])
}

model Share {
  id        String   @id @default(cuid())
  userId    String
  postId    String
  content   String?
  createdAt DateTime @default(now())

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
  post Post @relation(fields: [postId], references: [id], onDelete: Cascade)
}

model Follow {
  id          String   @id @default(cuid())
  followerId  String
  followingId String
  createdAt   DateTime @default(now())

  follower  User @relation("UserFollowing", fields: [followerId], references: [id], onDelete: Cascade)
  following User @relation("UserFollowers", fields: [followingId], references: [id], onDelete: Cascade)

  @@unique([followerId, followingId])
}

model Notification {
  id        String           @id @default(cuid())
  userId    String
  type      NotificationType
  title     String
  message   String
  read      Boolean          @default(false)
  createdAt DateTime         @default(now())

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)
}

model Message {
  id        String   @id @default(cuid())
  content   String
  senderId  String
  receiverId String
  read      Boolean  @default(false)
  createdAt DateTime @default(now())

  sender   User @relation("MessageSender", fields: [senderId], references: [id], onDelete: Cascade)
  receiver User @relation("MessageReceiver", fields: [receiverId], references: [id], onDelete: Cascade)
}

enum NotificationType {
  LIKE
  COMMENT
  FOLLOW
  SHARE
  MESSAGE
  MENTION
}
```

## 认证系统实现

### 1. 配置NextAuth.js

```typescript
// lib/auth.ts
import NextAuth from "next-auth"
import { PrismaAdapter } from "@auth/prisma-adapter"
import authConfig from "@/auth.config"
import { prisma } from "@/lib/prisma"

export const {
  handlers: { GET, POST },
  auth,
  signIn,
  signOut,
} = NextAuth({
  adapter: PrismaAdapter(prisma),
  session: { strategy: "jwt" },
  callbacks: {
    async jwt({ token, user }) {
      if (user) {
        token.username = user.username
        token.id = user.id
      }
      return token
    },
    async session({ session, token }) {
      if (token) {
        session.user.id = token.id as string
        session.user.username = token.username as string
      }
      return session
    },
  },
  ...authConfig,
})
```

```typescript
// auth.config.ts
import type { NextAuthConfig } from "next-auth"
import GitHub from "next-auth/providers/github"
import Google from "next-auth/providers/google"
import Credentials from "next-auth/providers/credentials"
import { LoginSchema } from "@/schemas"
import { getUserByEmail } from "@/data/user"
import bcrypt from "bcryptjs"

export default {
  providers: [
    GitHub({
      clientId: process.env.GITHUB_CLIENT_ID,
      clientSecret: process.env.GITHUB_CLIENT_SECRET,
    }),
    Google({
      clientId: process.env.GOOGLE_CLIENT_ID,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET,
    }),
    Credentials({
      async authorize(credentials) {
        const validatedFields = LoginSchema.safeParse(credentials)

        if (validatedFields.success) {
          const { email, password } = validatedFields.data

          const user = await getUserByEmail(email)
          if (!user || !user.password) return null

          const passwordsMatch = await bcrypt.compare(password, user.password)
          if (passwordsMatch) return user
        }

        return null
      }
    })
  ],
} satisfies NextAuthConfig
```

### 2. 创建认证组件

```typescript
// components/auth/login-form.tsx
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
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { SocialButtons } from "./social-buttons"
import { useTransition } from "react"
import { useRouter } from "next/navigation"
import { toast } from "react-hot-toast"

const LoginSchema = z.object({
  email: z.string().email({
    message: "请输入有效的邮箱地址",
  }),
  password: z.string().min(1, {
    message: "密码不能为空",
  }),
})

export function LoginForm() {
  const [isPending, startTransition] = useTransition()
  const router = useRouter()

  const form = useForm<z.infer<typeof LoginSchema>>({
    resolver: zodResolver(LoginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  })

  const onSubmit = (values: z.infer<typeof LoginSchema>) => {
    startTransition(() => {
      signIn("credentials", {
        email: values.email,
        password: values.password,
        redirect: false,
      }).then((callback) => {
        if (callback?.ok) {
          toast.success("登录成功")
          router.push("/dashboard")
          router.refresh()
        }
        if (callback?.error) {
          toast.error("登录失败")
        }
      })
    })
  }

  return (
    <Card className="w-[400px]">
      <CardHeader>
        <CardTitle>登录</CardTitle>
        <CardDescription>
          使用您的账号登录
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
            <FormField
              control={form.control}
              name="email"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>邮箱</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder="john@example.com"
                      type="email"
                      disabled={isPending}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <FormField
              control={form.control}
              name="password"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>密码</FormLabel>
                  <FormControl>
                    <Input
                      {...field}
                      placeholder="******"
                      type="password"
                      disabled={isPending}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />
            <Button type="submit" className="w-full" disabled={isPending}>
              登录
            </Button>
          </form>
        </Form>
        <div className="mt-6">
          <div className="relative">
            <div className="absolute inset-0 flex items-center">
              <span className="w-full border-t" />
            </div>
            <div className="relative flex justify-center text-xs uppercase">
              <span className="bg-background px-2 text-muted-foreground">
                或者
              </span>
            </div>
          </div>
          <SocialButtons />
        </div>
      </CardContent>
    </Card>
  )
}
```

## 用户系统实现

### 1. 用户资料页面

```typescript
// app/profile/[username]/page.tsx
import { notFound } from "next/navigation"
import { currentUser } from "@/lib/auth"
import { db } from "@/lib/db"
import { Bio } from "@/components/profile/bio"
import { Posts } from "@/components/profile/posts"
import { FollowButton } from "@/components/follow/follow-button"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import { EditProfileButton } from "@/components/profile/edit-profile-button"

interface ProfilePageProps {
  params: {
    username: string
  }
}

export default async function ProfilePage({ params }: ProfilePageProps) {
  const user = await currentUser()

  const profileUser = await db.user.findUnique({
    where: {
      username: params.username,
    },
    include: {
      posts: {
        orderBy: {
          createdAt: "desc",
        },
        include: {
          user: true,
          likes: true,
          comments: true,
          shares: true,
        },
      },
      followers: true,
      following: true,
      _count: {
        select: {
          followers: true,
          following: true,
          posts: true,
        },
      },
    },
  })

  if (!profileUser) {
    notFound()
  }

  const isOwnProfile = user?.id === profileUser.id
  const isFollowing = user ? await db.follow.findUnique({
    where: {
      followerId_followingId: {
        followerId: user.id,
        followingId: profileUser.id,
      },
    },
  }) : null

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <div className="flex flex-col md:flex-row gap-8">
          <div className="md:w-1/3">
            <div className="bg-white rounded-lg shadow p-6">
              <div className="flex flex-col items-center">
                <img
                  src={profileUser.image || "/default-avatar.png"}
                  alt={profileUser.name || profileUser.username}
                  className="w-32 h-32 rounded-full mb-4"
                />
                <h1 className="text-2xl font-bold mb-2">
                  {profileUser.name}
                </h1>
                <p className="text-gray-600 mb-4">@{profileUser.username}</p>

                {isOwnProfile ? (
                  <EditProfileButton />
                ) : (
                  <FollowButton
                    userId={profileUser.id}
                    isFollowing={!!isFollowing}
                  />
                )}

                <div className="flex gap-6 mt-6">
                  <div className="text-center">
                    <div className="font-bold text-lg">
                      {profileUser._count.posts}
                    </div>
                    <div className="text-gray-600">动态</div>
                  </div>
                  <div className="text-center">
                    <div className="font-bold text-lg">
                      {profileUser._count.followers}
                    </div>
                    <div className="text-gray-600">关注者</div>
                  </div>
                  <div className="text-center">
                    <div className="font-bold text-lg">
                      {profileUser._count.following}
                    </div>
                    <div className="text-gray-600">正在关注</div>
                  </div>
                </div>
              </div>

              <Bio bio={profileUser.bio} />

              {profileUser.location && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">位置</h3>
                  <p className="text-gray-600">{profileUser.location}</p>
                </div>
              )}

              {profileUser.website && (
                <div className="mt-4">
                  <h3 className="font-semibold mb-2">网站</h3>
                  <a
                    href={profileUser.website}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    {profileUser.website}
                  </a>
                </div>
              )}
            </div>
          </div>

          <div className="md:w-2/3">
            <Tabs defaultValue="posts" className="w-full">
              <TabsList className="grid w-full grid-cols-3">
                <TabsTrigger value="posts">动态</TabsTrigger>
                <TabsTrigger value="replies">回复</TabsTrigger>
                <TabsTrigger value="media">媒体</TabsTrigger>
              </TabsList>

              <TabsContent value="posts">
                <Posts
                  posts={profileUser.posts}
                  currentUserId={user?.id}
                />
              </TabsContent>

              <TabsContent value="replies">
                <div className="text-center py-8 text-gray-500">
                  回复功能开发中...
                </div>
              </TabsContent>

              <TabsContent value="media">
                <div className="text-center py-8 text-gray-500">
                  媒体功能开发中...
                </div>
              </TabsContent>
            </Tabs>
          </div>
        </div>
      </div>
    </div>
  )
}
```

### 2. 动态发布功能

```typescript
// components/posts/post-creator.tsx
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
  FormMessage,
} from "@/components/ui/form"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent } from "@/components/ui/card"
import { ImageUpload } from "@/components/upload/image-upload"
import { useMutation, useQueryClient } from "@tanstack/react-query"
import { toast } from "react-hot-toast"
import { createPost } from "@/actions/posts"

const PostSchema = z.object({
  content: z.string().min(1, "内容不能为空").max(500, "内容不能超过500字符"),
  image: z.string().optional(),
  video: z.string().optional(),
})

export function PostCreator() {
  const [image, setImage] = useState<string | null>(null)
  const [video, setVideo] = useState<string | null>(null)
  const queryClient = useQueryClient()

  const form = useForm<z.infer<typeof PostSchema>>({
    resolver: zodResolver(PostSchema),
    defaultValues: {
      content: "",
      image: "",
      video: "",
    },
  })

  const mutation = useMutation({
    mutationFn: createPost,
    onSuccess: () => {
      toast.success("发布成功！")
      form.reset()
      setImage(null)
      setVideo(null)
      queryClient.invalidateQueries({ queryKey: ["posts"] })
    },
    onError: (error) => {
      toast.error("发布失败，请重试")
    },
  })

  const onSubmit = (values: z.infer<typeof PostSchema>) => {
    mutation.mutate({
      ...values,
      image: image || undefined,
      video: video || undefined,
    })
  }

  return (
    <Card className="mb-6">
      <CardContent className="pt-6">
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
            <FormField
              control={form.control}
              name="content"
              render={({ field }) => (
                <FormItem>
                  <FormControl>
                    <Textarea
                      placeholder="分享您的想法..."
                      className="min-h-[100px] resize-none border-none p-0 focus-visible:ring-0 text-lg"
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {(image || video) && (
              <div className="mt-4">
                {image ? (
                  <img
                    src={image}
                    alt="上传的图片"
                    className="max-w-full h-auto rounded-lg"
                  />
                ) : (
                  <video
                    src={video || ""}
                    controls
                    className="max-w-full h-auto rounded-lg"
                  />
                )}
              </div>
            )}

            <div className="flex items-center justify-between pt-4 border-t">
              <div className="flex gap-2">
                <ImageUpload
                  onImageUpload={setImage}
                  onVideoUpload={setVideo}
                  disabled={mutation.isPending}
                />
              </div>

              <Button
                type="submit"
                disabled={mutation.isPending || !form.formState.isValid}
              >
                {mutation.isPending ? "发布中..." : "发布"}
              </Button>
            </div>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
```

## 实时通知系统

### 1. 设置Pusher

```typescript
// lib/pusher.ts
import Pusher from "pusher"

export const pusher = new Pusher({
  appId: process.env.PUSHER_APP_ID!,
  key: process.env.PUSHER_KEY!,
  secret: process.env.PUSHER_SECRET!,
  cluster: process.env.PUSHER_CLUSTER!,
  useTLS: true,
})
```

### 2. 通知API路由

```typescript
// app/api/notifications/route.ts
import { NextRequest, NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authConfig } from "@/auth.config"
import { db } from "@/lib/db"
import { pusher } from "@/lib/pusher"

export async function GET() {
  try {
    const session = await getServerSession(authConfig)
    if (!session?.user?.id) {
      return NextResponse.json({ error: "未授权" }, { status: 401 })
    }

    const notifications = await db.notification.findMany({
      where: {
        userId: session.user.id,
      },
      orderBy: {
        createdAt: "desc",
      },
      take: 20,
    })

    return NextResponse.json(notifications)
  } catch (error) {
    return NextResponse.json(
      { error: "获取通知失败" },
      { status: 500 }
    )
  }
}

export async function PATCH(request: NextRequest) {
  try {
    const session = await getServerSession(authConfig)
    if (!session?.user?.id) {
      return NextResponse.json({ error: "未授权" }, { status: 401 })
    }

    const { notificationIds } = await request.json()

    await db.notification.updateMany({
      where: {
        id: {
          in: notificationIds,
        },
        userId: session.user.id,
      },
      data: {
        read: true,
      },
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    return NextResponse.json(
      { error: "标记已读失败" },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const { userId, type, title, message } = await request.json()

    const notification = await db.notification.create({
      data: {
        userId,
        type,
        title,
        message,
      },
    })

    // 发送实时通知
    await pusher.trigger(`user-${userId}`, "notification", notification)

    return NextResponse.json(notification)
  } catch (error) {
    return NextResponse.json(
      { error: "创建通知失败" },
      { status: 500 }
    )
  }
}
```

### 3. 实时通知组件

```typescript
// components/notifications/notification-provider.tsx
"use client"

import { useEffect } from "react"
import { PusherClient } from "pusher-js"
import { useQueryClient } from "@tanstack/react-query"
import { useSession } from "next-auth/react"

const pusherClient = new PusherClient(process.env.NEXT_PUBLIC_PUSHER_KEY!, {
  cluster: process.env.NEXT_PUBLIC_PUSHER_CLUSTER!,
})

interface NotificationProviderProps {
  children: React.ReactNode
}

export function NotificationProvider({ children }: NotificationProviderProps) {
  const { data: session } = useSession()
  const queryClient = useQueryClient()

  useEffect(() => {
    if (!session?.user?.id) return

    const channel = pusherClient.subscribe(`user-${session.user.id}`)

    channel.bind("notification", (data: any) => {
      queryClient.setQueryData(["notifications"], (oldData: any) => {
        return [data, ...(oldData || [])]
      })
    })

    return () => {
      pusherClient.unsubscribe(`user-${session.user.id}`)
    }
  }, [session?.user?.id, queryClient])

  return <>{children}</>
}
```

## 即时消息功能

### 1. 消息页面

```typescript
// app/messages/page.tsx
import { currentUser } from "@/lib/auth"
import { db } from "@/lib/db"
import { redirect } from "next/navigation"
import { MessageList } from "@/components/messages/message-list"
import { ChatWindow } from "@/components/messages/chat-window"

export default async function MessagesPage() {
  const user = await currentUser()
  if (!user) redirect("/login")

  const conversations = await db.user.findMany({
    where: {
      OR: [
        {
          sentMessages: {
            some: {
              receiverId: user.id,
            },
          },
        },
        {
          receivedMessages: {
            some: {
              senderId: user.id,
            },
          },
        },
      ],
    },
    include: {
      sentMessages: {
        where: {
          receiverId: user.id,
        },
        orderBy: {
          createdAt: "desc",
        },
        take: 1,
      },
      receivedMessages: {
        where: {
          senderId: user.id,
        },
        orderBy: {
          createdAt: "desc",
        },
        take: 1,
      },
    },
  })

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto h-[calc(100vh-200px)]">
        <div className="grid grid-cols-1 md:grid-cols-3 h-full">
          <div className="border-r">
            <MessageList conversations={conversations} currentUserId={user.id} />
          </div>
          <div className="hidden md:block md:col-span-2">
            <ChatWindow />
          </div>
        </div>
      </div>
    </div>
  )
}
```

### 2. WebSocket消息处理

```typescript
// lib/socket.ts
import { Server as ServerIO } from "socket.io"
import { Server as NetServer } from "http"

export type NextApiResponseServerIO = NextApiResponse & {
  socket: {
    server: NetServer & {
      io?: ServerIO
    }
  }
}

export const config = {
  api: {
    bodyParser: false,
  },
}

const ioHandler = (req: NextApiRequest, res: NextApiResponseServerIO) => {
  if (!res.socket.server.io) {
    const path = "/api/socket/io"
    const httpServer: NetServer = res.socket.server as any
    const io = new ServerIO(httpServer, {
      path,
      addTrailingSlash: false,
    })
    res.socket.server.io = io
  }

  res.end()
}

export default ioHandler
```

## 文件上传功能

### 1. 配置UploadThing

```typescript
// app/api/uploadthing/core.ts
import { createUploadthing, type FileRouter } from "uploadthing/next"
import { getServerSession } from "next-auth"
import { authConfig } from "@/auth.config"

const f = createUploadthing()

export const ourFileRouter = {
  imageUploader: f({ image: { maxFileSize: "4MB", maxFileCount: 1 } })
    .middleware(async ({ req }) => {
      const session = await getServerSession(authConfig)

      if (!session?.user?.id) throw new Error("未授权")

      return { userId: session.user.id }
    })
    .onUploadComplete(async ({ metadata, file }) => {
      return { uploadedBy: metadata.userId }
    }),

  videoUploader: f({ video: { maxFileSize: "64MB", maxFileCount: 1 } })
    .middleware(async ({ req }) => {
      const session = await getServerSession(authConfig)

      if (!session?.user?.id) throw new Error("未授权")

      return { userId: session.user.id }
    })
    .onUploadComplete(async ({ metadata, file }) => {
      return { uploadedBy: metadata.userId }
    }),
} satisfies FileRouter

export type OurFileRouter = typeof ourFileRouter
```

### 2. 图片上传组件

```typescript
// components/upload/image-upload.tsx
"use client"

import { useState } from "react"
import { UploadButton } from "@/components/uploadthing/upload-button"
import { UploadDropzone } from "@/components/uploadthing/upload-dropzone"
import { toast } from "react-hot-toast"

interface ImageUploadProps {
  onImageUpload: (url: string) => void
  onVideoUpload: (url: string) => void
  disabled?: boolean
}

export function ImageUpload({ onImageUpload, onVideoUpload, disabled }: ImageUploadProps) {
  const [showUploadZone, setShowUploadZone] = useState(false)

  return (
    <div className="relative">
      <button
        type="button"
        onClick={() => setShowUploadZone(!showUploadZone)}
        disabled={disabled}
        className="p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-full transition-colors"
      >
        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </button>

      {showUploadZone && (
        <div className="absolute z-10 mt-2 w-80">
          <div className="bg-white rounded-lg shadow-lg border p-4">
            <h3 className="font-semibold mb-3">上传图片或视频</h3>

            <div className="space-y-3">
              <UploadDropzone
                endpoint="imageUploader"
                onClientUploadComplete={(res) => {
                  if (res?.[0]?.url) {
                    onImageUpload(res[0].url)
                    toast.success("图片上传成功")
                  }
                  setShowUploadZone(false)
                }}
                onUploadError={(error: Error) => {
                  toast.error(`上传失败: ${error.message}`)
                }}
              />

              <UploadDropzone
                endpoint="videoUploader"
                onClientUploadComplete={(res) => {
                  if (res?.[0]?.url) {
                    onVideoUpload(res[0].url)
                    toast.success("视频上传成功")
                  }
                  setShowUploadZone(false)
                }}
                onUploadError={(error: Error) => {
                  toast.error(`上传失败: ${error.message}`)
                }}
              />
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
```

## 搜索功能

### 1. 搜索API

```typescript
// app/api/search/route.ts
import { NextRequest, NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authConfig } from "@/auth.config"
import { db } from "@/lib/db"

export async function GET(request: NextRequest) {
  try {
    const session = await getServerSession(authConfig)
    if (!session?.user?.id) {
      return NextResponse.json({ error: "未授权" }, { status: 401 })
    }

    const { searchParams } = new URL(request.url)
    const query = searchParams.get("q")
    const type = searchParams.get("type") || "all"

    if (!query || query.length < 2) {
      return NextResponse.json({ results: [] })
    }

    const results = {
      users: type === "all" || type === "users" ? await searchUsers(query, session.user.id) : [],
      posts: type === "all" || type === "posts" ? await searchPosts(query) : [],
    }

    return NextResponse.json(results)
  } catch (error) {
    return NextResponse.json(
      { error: "搜索失败" },
      { status: 500 }
    )
  }
}

async function searchUsers(query: string, currentUserId: string) {
  return db.user.findMany({
    where: {
      OR: [
        {
          username: {
            contains: query,
            mode: "insensitive",
          },
        },
        {
          name: {
            contains: query,
            mode: "insensitive",
          },
        },
      ],
      NOT: {
        id: currentUserId,
      },
    },
    select: {
      id: true,
      username: true,
      name: true,
      image: true,
      bio: true,
      _count: {
        select: {
          followers: true,
          following: true,
        },
      },
    },
    take: 10,
  })
}

async function searchPosts(query: string) {
  return db.post.findMany({
    where: {
      OR: [
        {
          content: {
            contains: query,
            mode: "insensitive",
          },
        },
        {
          user: {
            OR: [
              {
                username: {
                  contains: query,
                  mode: "insensitive",
                },
              },
              {
                name: {
                  contains: query,
                  mode: "insensitive",
                },
              },
            ],
          },
        },
      ],
    },
    include: {
      user: {
        select: {
          id: true,
          username: true,
          name: true,
          image: true,
        },
      },
      likes: true,
      comments: true,
      shares: true,
      _count: {
        select: {
          likes: true,
          comments: true,
          shares: true,
        },
      },
    },
    orderBy: {
      createdAt: "desc",
    },
    take: 20,
  })
}
```

### 2. 搜索组件

```typescript
// components/search/search-box.tsx
"use client"

import { useState, useEffect, useRef } from "react"
import { useRouter } from "next/navigation"
import { useQuery } from "@tanstack/react-query"
import { Search, Users, FileText } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Card, CardContent } from "@/components/ui/card"
import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar"
import { searchContent } from "@/actions/search"

interface SearchResult {
  users: Array<{
    id: string
    username: string
    name: string | null
    image: string | null
    bio: string | null
    _count: {
      followers: number
      following: number
    }
  }>
  posts: Array<{
    id: string
    content: string | null
    createdAt: string
    user: {
      id: string
      username: string
      name: string | null
      image: string | null
    }
    _count: {
      likes: number
      comments: number
      shares: number
    }
  }>
}

export function SearchBox() {
  const [query, setQuery] = useState("")
  const [showResults, setShowResults] = useState(false)
  const [selectedTab, setSelectedTab] = useState<"all" | "users" | "posts">("all")
  const router = useRouter()
  const searchRef = useRef<HTMLDivElement>(null)

  const { data: results, isLoading } = useQuery<SearchResult>({
    queryKey: ["search", query, selectedTab],
    queryFn: () => searchContent(query, selectedTab),
    enabled: query.length >= 2,
  })

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (searchRef.current && !searchRef.current.contains(event.target as Node)) {
        setShowResults(false)
      }
    }

    document.addEventListener("mousedown", handleClickOutside)
    return () => document.removeEventListener("mousedown", handleClickOutside)
  }, [])

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (query.trim()) {
      router.push(`/search?q=${encodeURIComponent(query)}`)
      setShowResults(false)
    }
  }

  return (
    <div ref={searchRef} className="relative">
      <form onSubmit={handleSearch} className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
        <Input
          type="text"
          placeholder="搜索用户或内容..."
          value={query}
          onChange={(e) => {
            setQuery(e.target.value)
            setShowResults(true)
          }}
          onFocus={() => setShowResults(true)}
          className="pl-10 pr-4 w-64"
        />
      </form>

      {showResults && query.length >= 2 && (
        <Card className="absolute top-full mt-2 w-full max-w-md z-50 shadow-lg">
          <CardContent className="p-0">
            {isLoading ? (
              <div className="p-4 text-center text-gray-500">搜索中...</div>
            ) : results && (results.users.length > 0 || results.posts.length > 0) ? (
              <>
                <div className="border-b">
                  <div className="flex">
                    <Button
                      variant="ghost"
                      className={`flex-1 rounded-none ${selectedTab === "all" ? "bg-gray-100" : ""}`}
                      onClick={() => setSelectedTab("all")}
                    >
                      全部
                    </Button>
                    <Button
                      variant="ghost"
                      className={`flex-1 rounded-none ${selectedTab === "users" ? "bg-gray-100" : ""}`}
                      onClick={() => setSelectedTab("users")}
                    >
                      用户
                    </Button>
                    <Button
                      variant="ghost"
                      className={`flex-1 rounded-none ${selectedTab === "posts" ? "bg-gray-100" : ""}`}
                      onClick={() => setSelectedTab("posts")}
                    >
                      内容
                    </Button>
                  </div>
                </div>

                <div className="max-h-96 overflow-y-auto">
                  {(selectedTab === "all" || selectedTab === "users") && results.users.length > 0 && (
                    <div>
                      <div className="px-4 py-2 text-sm font-semibold text-gray-500 flex items-center gap-2">
                        <Users className="w-4 h-4" />
                        用户
                      </div>
                      {results.users.map((user) => (
                        <div
                          key={user.id}
                          className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b"
                          onClick={() => {
                            router.push(`/${user.username}`)
                            setShowResults(false)
                          }}
                        >
                          <div className="flex items-center gap-3">
                            <Avatar>
                              <AvatarImage src={user.image || ""} />
                              <AvatarFallback>{user.name?.[0] || user.username[0]}</AvatarFallback>
                            </Avatar>
                            <div>
                              <div className="font-semibold">{user.name || user.username}</div>
                              <div className="text-sm text-gray-500">@{user.username}</div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {(selectedTab === "all" || selectedTab === "posts") && results.posts.length > 0 && (
                    <div>
                      <div className="px-4 py-2 text-sm font-semibold text-gray-500 flex items-center gap-2">
                        <FileText className="w-4 h-4" />
                        内容
                      </div>
                      {results.posts.map((post) => (
                        <div
                          key={post.id}
                          className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b"
                          onClick={() => {
                            router.push(`/post/${post.id}`)
                            setShowResults(false)
                          }}
                        >
                          <div className="flex items-start gap-3">
                            <Avatar>
                              <AvatarImage src={post.user.image || ""} />
                              <AvatarFallback>{post.user.name?.[0] || post.user.username[0]}</AvatarFallback>
                            </Avatar>
                            <div className="flex-1">
                              <div className="font-semibold">{post.user.name || post.user.username}</div>
                              <p className="text-sm text-gray-600 mt-1 line-clamp-2">
                                {post.content}
                              </p>
                              <div className="text-xs text-gray-500 mt-2">
                                {post._count.likes} 点赞 · {post._count.comments} 评论
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </>
            ) : (
              <div className="p-4 text-center text-gray-500">未找到相关内容</div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  )
}
```

## 管理员后台

### 1. 管理员页面

```typescript
// app/admin/page.tsx
import { currentUser } from "@/lib/auth"
import { redirect } from "next/navigation"
import { db } from "@/lib/db"
import { AdminStats } from "@/components/admin/admin-stats"
import { UserManagement } from "@/components/admin/user-management"
import { ContentModeration } from "@/components/admin/content-moderation"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"

export default async function AdminPage() {
  const user = await currentUser()
  if (!user?.isAdmin) redirect("/")

  const [totalUsers, totalPosts, totalReports] = await Promise.all([
    db.user.count(),
    db.post.count(),
    db.report.count(),
  ])

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">管理员后台</h1>
        <p className="text-gray-600 mt-2">管理平台用户和内容</p>
      </div>

      <AdminStats
        totalUsers={totalUsers}
        totalPosts={totalPosts}
        totalReports={totalReports}
      />

      <Tabs defaultValue="users" className="mt-8">
        <TabsList>
          <TabsTrigger value="users">用户管理</TabsTrigger>
          <TabsTrigger value="content">内容审核</TabsTrigger>
          <TabsTrigger value="analytics">数据分析</TabsTrigger>
          <TabsTrigger value="settings">系统设置</TabsTrigger>
        </TabsList>

        <TabsContent value="users">
          <UserManagement />
        </TabsContent>

        <TabsContent value="content">
          <ContentModeration />
        </TabsContent>

        <TabsContent value="analytics">
          <div className="text-center py-8 text-gray-500">
            数据分析功能开发中...
          </div>
        </TabsContent>

        <TabsContent value="settings">
          <div className="text-center py-8 text-gray-500">
            系统设置功能开发中...
          </div>
        </TabsContent>
      </Tabs>
    </div>
  )
}
```

## 性能优化

### 1. 数据库索引优化

```sql
-- 用户表索引
CREATE INDEX idx_user_email ON users(email);
CREATE INDEX idx_user_username ON users(username);
CREATE INDEX idx_user_created_at ON users(created_at);

-- 动态表索引
CREATE INDEX idx_post_user_id ON posts(user_id);
CREATE INDEX idx_post_created_at ON posts(created_at);
CREATE INDEX idx_post_content_search ON posts USING gin(to_tsvector('english', content));

-- 评论表索引
CREATE INDEX idx_comment_post_id ON comments(post_id);
CREATE INDEX idx_comment_user_id ON comments(user_id);
CREATE INDEX idx_comment_parent_id ON comments(parent_id);

-- 点赞表索引
CREATE INDEX idx_like_user_id ON likes(user_id);
CREATE INDEX idx_like_post_id ON likes(post_id);
CREATE INDEX idx_like_comment_id ON likes(comment_id);
CREATE UNIQUE INDEX idx_like_unique ON likes(user_id, post_id, comment_id) WHERE post_id IS NOT NULL;
CREATE UNIQUE INDEX idx_like_unique_comment ON likes(user_id, comment_id, post_id) WHERE comment_id IS NOT NULL;

-- 关注表索引
CREATE INDEX idx_follow_follower_id ON follows(follower_id);
CREATE INDEX idx_follow_following_id ON follows(following_id);
CREATE UNIQUE INDEX idx_follow_unique ON follows(follower_id, following_id);

-- 通知表索引
CREATE INDEX idx_notification_user_id ON notifications(user_id);
CREATE INDEX idx_notification_created_at ON notifications(created_at);
CREATE INDEX idx_notification_read ON notifications(read);

-- 消息表索引
CREATE INDEX idx_message_sender_id ON messages(sender_id);
CREATE INDEX idx_message_receiver_id ON messages(receiver_id);
CREATE INDEX idx_message_created_at ON messages(created_at);
```

### 2. Redis缓存策略

```typescript
// lib/redis.ts
import { Redis } from "ioredis"

const redis = new Redis(process.env.REDIS_URL!)

export default redis

// 缓存键生成器
export const cacheKeys = {
  user: (userId: string) => `user:${userId}`,
  userPosts: (userId: string) => `user:${userId}:posts`,
  post: (postId: string) => `post:${postId}`,
  postLikes: (postId: string) => `post:${postId}:likes`,
  userFeed: (userId: string) => `user:${userId}:feed`,
  trendingPosts: "trending:posts",
  searchResults: (query: string) => `search:${query}`,
}

// 缓存装饰器
export function cache<T>(
  key: string,
  ttl: number = 3600,
  fetcher: () => Promise<T>
): Promise<T> {
  return new Promise(async (resolve, reject) => {
    try {
      const cached = await redis.get(key)
      if (cached) {
        resolve(JSON.parse(cached))
        return
      }

      const data = await fetcher()
      await redis.setex(key, ttl, JSON.stringify(data))
      resolve(data)
    } catch (error) {
      reject(error)
    }
  })
}

// 缓存失效
export async function invalidateCache(patterns: string[]) {
  const pipeline = redis.pipeline()

  for (const pattern of patterns) {
    const keys = await redis.keys(pattern)
    if (keys.length > 0) {
      pipeline.del(...keys)
    }
  }

  await pipeline.exec()
}
```

### 3. CDN和图片优化

```typescript
// lib/image-optimization.ts
import sharp from "sharp"
import { UploadThingError } from "uploadthing/server"

export async function optimizeImage(buffer: Buffer) {
  try {
    // 基础优化
    const optimized = await sharp(buffer)
      .resize(1200, 1200, {
        fit: "inside",
        withoutEnlargement: true,
      })
      .jpeg({ quality: 80, progressive: true })
      .toBuffer()

    // 生成缩略图
    const thumbnail = await sharp(buffer)
      .resize(300, 300, {
        fit: "cover",
      })
      .jpeg({ quality: 60 })
      .toBuffer()

    return {
      optimized,
      thumbnail,
    }
  } catch (error) {
    throw new UploadThingError("图片处理失败")
  }
}

// 图片CDN URL生成器
export function getImageUrl(imageId: string, size: "original" | "thumbnail" = "original") {
  const baseUrl = process.env.CDN_BASE_URL || ""
  return `${baseUrl}/${imageId}/${size === "thumbnail" ? "thumb" : "original"}.jpg`
}
```

## 部署配置

### 1. Vercel部署配置

```json
// vercel.json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "env": {
    "DATABASE_URL": "@database_url",
    "NEXTAUTH_SECRET": "@nextauth_secret",
    "NEXTAUTH_URL": "@nextauth_url",
    "GITHUB_CLIENT_ID": "@github_client_id",
    "GITHUB_CLIENT_SECRET": "@github_client_secret",
    "GOOGLE_CLIENT_ID": "@google_client_id",
    "GOOGLE_CLIENT_SECRET": "@google_client_secret",
    "UPLOADTHING_SECRET": "@uploadthing_secret",
    "UPLOADTHING_APP_ID": "@uploadthing_app_id",
    "REDIS_URL": "@redis_url",
    "PUSHER_APP_ID": "@pusher_app_id",
    "PUSHER_KEY": "@pusher_key",
    "PUSHER_SECRET": "@pusher_secret",
    "PUSHER_CLUSTER": "@pusher_cluster",
    "AWS_ACCESS_KEY_ID": "@aws_access_key_id",
    "AWS_SECRET_ACCESS_KEY": "@aws_secret_access_key",
    "AWS_REGION": "@aws_region",
    "AWS_S3_BUCKET": "@aws_s3_bucket"
  },
  "crons": [
    {
      "path": "/api/cleanup/expired-sessions",
      "schedule": "0 0 * * *"
    },
    {
      "path": "/api/cleanup/orphaned-files",
      "schedule": "0 2 * * *"
    }
  ]
}
```

### 2. Docker配置

```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json yarn.lock* package-lock.json* pnpm-lock.yaml* ./
RUN \
  if [ -f yarn.lock ]; then yarn --frozen-lockfile; \
  elif [ -f package-lock.json ]; then npm ci; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm i --frozen-lockfile; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Environment variable needed for build
ENV NEXT_TELEMETRY_DISABLED=1

RUN \
  if [ -f yarn.lock ]; then yarn run build; \
  elif [ -f package-lock.json ]; then npm run build; \
  elif [ -f pnpm-lock.yaml ]; then corepack enable pnpm && pnpm run build; \
  else echo "Lockfile not found." && exit 1; \
  fi

# Production image, copy all the files and run next
FROM base AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

COPY --from=builder /app/public ./public

# Set the correct permission for prerender cache
RUN mkdir .next
RUN chown nextjs:nodejs .next

# Automatically leverage output traces to reduce image size
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]
```

```yaml
# docker-compose.yml
version: '3.8'

services:
  app:
    build: .
    ports:
      - "3000:3000"
    environment:
      - DATABASE_URL=postgresql://postgres:password@db:5432/social_media
      - REDIS_URL=redis://redis:6379
    depends_on:
      - db
      - redis
    volumes:
      - ./uploads:/app/uploads

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: social_media
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  postgres_data:
```

## 监控和分析

### 1. 性能监控

```typescript
// lib/monitoring.ts
import { NextResponse } from "next/server"

export class Monitoring {
  private static metrics = new Map<string, number>()

  static increment(name: string, value: number = 1) {
    const current = this.metrics.get(name) || 0
    this.metrics.set(name, current + value)
  }

  static decrement(name: string, value: number = 1) {
    const current = this.metrics.get(name) || 0
    this.metrics.set(name, Math.max(0, current - value))
  }

  static timing(name: string, duration: number) {
    const key = `${name}_timing`
    const current = this.metrics.get(key) || 0
    const count = this.metrics.get(`${key}_count`) || 0
    this.metrics.set(key, current + duration)
    this.metrics.set(`${key}_count`, count + 1)
  }

  static getMetrics() {
    return Object.fromEntries(this.metrics)
  }

  static async withTiming<T>(
    name: string,
    fn: () => Promise<T>
  ): Promise<T> {
    const start = Date.now()
    try {
      const result = await fn()
      this.timing(name, Date.now() - start)
      return result
    } catch (error) {
      this.increment(`${name}_errors`)
      throw error
    }
  }
}

// 中间件包装器
export function withMonitoring(handler: any) {
  return async (req: any, res: any) => {
    const start = Date.now()
    try {
      const result = await handler(req, res)
      Monitoring.timing("api_response_time", Date.now() - start)
      return result
    } catch (error) {
      Monitoring.increment("api_errors")
      throw error
    }
  }
}
```

### 2. 错误追踪

```typescript
// lib/error-tracking.ts
interface ErrorEvent {
  message: string
  stack?: string
  type: string
  timestamp: number
  userAgent?: string
  url?: string
  userId?: string
}

class ErrorTracker {
  private errors: ErrorEvent[] = []
  private maxErrors = 100

  track(error: Error, context?: { userId?: string; url?: string }) {
    const errorEvent: ErrorEvent = {
      message: error.message,
      stack: error.stack,
      type: error.name,
      timestamp: Date.now(),
      ...context,
    }

    this.errors.push(errorEvent)

    if (this.errors.length > this.maxErrors) {
      this.errors.shift()
    }

    // 发送到错误追踪服务
    this.sendToService(errorEvent)
  }

  private async sendToService(errorEvent: ErrorEvent) {
    // 这里可以集成Sentry、LogRocket等服务
    console.error("Error tracked:", errorEvent)
  }

  getRecentErrors(limit: number = 10) {
    return this.errors.slice(-limit)
  }

  clear() {
    this.errors = []
  }
}

export const errorTracker = new ErrorTracker()
```

## 总结

通过这个全栈社交媒体平台项目，我们学习了：

### 核心技术栈
- **Next.js 15**: 完整的全栈框架，支持SSR、SSG、ISR
- **React 19**: 最新的React特性和优化
- **TypeScript**: 类型安全和开发体验
- **Prisma**: 现代数据库ORM
- **NextAuth.js**: 完整的认证解决方案

### 关键功能实现
- 用户认证和授权系统
- 动态发布和互动功能
- 实时通知系统
- 即时消息功能
- 文件上传和媒体处理
- 搜索和推荐功能
- 管理员后台

### 性能优化策略
- 数据库索引优化
- Redis缓存策略
- CDN和图片优化
- 懒加载和代码分割
- 实时通信优化

### 部署和运维
- Vercel部署配置
- Docker容器化
- CI/CD流程
- 监控和错误追踪

这个项目展示了如何使用现代技术栈构建一个功能完整、性能优秀的全栈应用。从PHP开发者的角度来看，Next.js提供了一个更加一体化和高效的开发体验，特别是在处理前端渲染、API路由和数据库交互方面。

通过学习这个项目，您已经掌握了构建现代Web应用所需的核心技能，可以应用到各种类型的Web应用开发中。