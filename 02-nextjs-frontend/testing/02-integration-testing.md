# 集成测试指南 (Integration Testing Guide)

> **PHP开发者视角**: 从Laravel的BrowserKit测试到现代前端集成测试的转变，了解如何测试组件间的交互和数据流。

## 集成测试基础

### 什么是集成测试

集成测试是测试多个组件、模块或系统一起工作时的行为。在Next.js中，集成测试主要用于：

- 测试组件间的交互
- 测试数据流和状态管理
- 测试API路由和数据库交互
- 测试用户流程和页面导航
- 测试第三方服务集成

### 集成测试 vs 单元测试

| 特性 | 单元测试 | 集成测试 |
|------|----------|----------|
| 测试范围 | 单个函数/组件 | 多个组件/模块 |
| 依赖 | Mock外部依赖 | 真实或模拟的依赖 |
| 速度 | 快速 | 中等 |
| 目标 | 验证单元正确性 | 验证交互正确性 |
| 维护成本 | 低 | 中等 |

## 测试环境配置

### 1. 测试数据库设置

```typescript
// __tests__/setup/database.ts
import { PrismaClient } from "@prisma/client"

const prisma = new PrismaClient()

export async function setupTestDatabase() {
  // 清理所有数据
  await prisma.user.deleteMany()
  await prisma.post.deleteMany()
  await prisma.comment.deleteMany()
  await prisma.like.deleteMany()

  // 创建测试数据
  const testUser = await prisma.user.create({
    data: {
      name: "测试用户",
      email: "test@example.com",
      age: 25,
      bio: "这是一个测试用户",
    },
  })

  const testPost = await prisma.post.create({
    data: {
      title: "测试文章",
      content: "这是一篇测试文章的内容",
      userId: testUser.id,
    },
  })

  return { testUser, testPost }
}

export async function cleanupTestDatabase() {
  await prisma.user.deleteMany()
  await prisma.post.deleteMany()
  await prisma.comment.deleteMany()
  await prisma.like.deleteMany()
  await prisma.$disconnect()
}

export { prisma }
```

### 2. API路由测试设置

```typescript
// __tests__/setup/api.ts
import { createMocks } from "node-mocks-http"
import { NextApiRequest, NextApiResponse } from "next"

export function createApiMocks({
  method = "GET",
  query = {},
  body = {},
  headers = {},
}: Partial<NextApiRequest> = {}) {
  const { req, res } = createMocks<NextApiRequest, NextApiResponse>({
    method,
    query,
    body,
    headers,
  })

  return { req, res }
}

export async function testApiHandler(
  handler: (req: NextApiRequest, res: NextApiResponse) => Promise<void>,
  options: Partial<NextApiRequest> = {}
) {
  const { req, res } = createApiMocks(options)

  await handler(req, res)

  return {
    status: res._getStatusCode(),
    data: JSON.parse(res._getData()),
    headers: res.getHeaders(),
  }
}
```

## 页面组件集成测试

### 1. 用户资料页面测试

```typescript
// src/app/profile/[username]/page.tsx
import { notFound } from "next/navigation"
import { db } from "@/lib/db"
import { Bio } from "@/components/profile/bio"
import { Posts } from "@/components/profile/posts"
import { FollowButton } from "@/components/follow/follow-button"

interface ProfilePageProps {
  params: {
    username: string
  }
}

export default async function ProfilePage({ params }: ProfilePageProps) {
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

                <FollowButton userId={profileUser.id} />

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
            </div>
          </div>

          <div className="md:w-2/3">
            <Posts posts={profileUser.posts} />
          </div>
        </div>
      </div>
    </div>
  )
}
```

```typescript
// __tests__/pages/profile.test.tsx
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { setupTestDatabase, cleanupTestDatabase } from "@/__tests__/setup/database"
import ProfilePage from "@/app/profile/[username]/page"

// 模拟数据库
vi.mock("@/lib/db", () => ({
  db: {
    user: {
      findUnique: vi.fn(),
    },
  },
}))

// 模拟组件
vi.mock("@/components/profile/bio", () => ({
  Bio: ({ bio }: { bio: string | null }) => (
    <div data-testid="bio">{bio || "暂无简介"}</div>
  ),
}))

vi.mock("@/components/profile/posts", () => ({
  Posts: ({ posts }: { posts: any[] }) => (
    <div data-testid="posts">
      {posts.map((post) => (
        <div key={post.id} data-testid="post">
          {post.title}
        </div>
      ))}
    </div>
  ),
}))

vi.mock("@/components/follow/follow-button", () => ({
  FollowButton: ({ userId }: { userId: string }) => (
    <button data-testid="follow-button">关注</button>
  ),
}))

vi.mock("next/navigation", () => ({
  notFound: vi.fn(),
}))

describe("ProfilePage", () => {
  const mockDb = require("@/lib/db").db

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("应该渲染用户资料页面", async () => {
    const mockUser = {
      id: "1",
      name: "张三",
      username: "zhangsan",
      email: "zhangsan@example.com",
      bio: "前端开发者",
      image: "/avatar.jpg",
      posts: [
        {
          id: "1",
          title: "第一篇博客",
          content: "博客内容",
          createdAt: new Date(),
        },
      ],
      followers: [],
      following: [],
      _count: {
        followers: 10,
        following: 5,
        posts: 1,
      },
    }

    mockDb.user.findUnique.mockResolvedValue(mockUser)

    render(await ProfilePage({ params: { username: "zhangsan" } }))

    await waitFor(() => {
      expect(screen.getByText("张三")).toBeInTheDocument()
      expect(screen.getByText("@zhangsan")).toBeInTheDocument()
      expect(screen.getByTestId("bio")).toHaveTextContent("前端开发者")
      expect(screen.getByTestId("posts")).toBeInTheDocument()
      expect(screen.getByTestId("follow-button")).toBeInTheDocument()
    })

    expect(screen.getByText("1")).toBeInTheDocument() // 动态数量
    expect(screen.getByText("10")).toBeInTheDocument() // 关注者数量
    expect(screen.getByText("5")).toBeInTheDocument() // 正在关注数量
  })

  it("应该处理用户不存在的情况", async () => {
    mockDb.user.findUnique.mockResolvedValue(null)
    const { notFound } = require("next/navigation")

    await ProfilePage({ params: { username: "nonexistent" } })

    expect(notFound).toHaveBeenCalled()
  })

  it("应该处理空bio的情况", async () => {
    const mockUser = {
      id: "1",
      name: "张三",
      username: "zhangsan",
      email: "zhangsan@example.com",
      bio: null,
      image: "/avatar.jpg",
      posts: [],
      followers: [],
      following: [],
      _count: {
        followers: 0,
        following: 0,
        posts: 0,
      },
    }

    mockDb.user.findUnique.mockResolvedValue(mockUser)

    render(await ProfilePage({ params: { username: "zhangsan" } }))

    await waitFor(() => {
      expect(screen.getByTestId("bio")).toHaveTextContent("暂无简介")
    })
  })

  it("应该正确显示没有文章的情况", async () => {
    const mockUser = {
      id: "1",
      name: "张三",
      username: "zhangsan",
      email: "zhangsan@example.com",
      bio: "前端开发者",
      image: "/avatar.jpg",
      posts: [],
      followers: [],
      following: [],
      _count: {
        followers: 0,
        following: 0,
        posts: 0,
      },
    }

    mockDb.user.findUnique.mockResolvedValue(mockUser)

    render(await ProfilePage({ params: { username: "zhangsan" } }))

    await waitFor(() => {
      expect(screen.getByText("0")).toBeInTheDocument() // 动态数量
      expect(screen.getByTestId("posts")).toBeInTheDocument()
      expect(screen.queryByTestId("post")).not.toBeInTheDocument()
    })
  })
})
```

### 2. 博客文章页面测试

```typescript
// src/app/blog/[slug]/page.tsx
import { notFound } from "next/navigation"
import { db } from "@/lib/db"
import { BlogPost } from "@/components/blog/blog-post"
import { Comments } from "@/components/blog/comments"
import { RelatedPosts } from "@/components/blog/related-posts"

interface BlogPostPageProps {
  params: {
    slug: string
  }
}

export default async function BlogPostPage({ params }: BlogPostPageProps) {
  const post = await db.post.findUnique({
    where: {
      slug: params.slug,
    },
    include: {
      user: {
        select: {
          id: true,
          name: true,
          username: true,
          image: true,
        },
      },
      tags: true,
      comments: {
        include: {
          user: {
            select: {
              id: true,
              name: true,
              username: true,
              image: true,
            },
          },
        },
        orderBy: {
          createdAt: "desc",
        },
      },
      _count: {
        select: {
          likes: true,
          comments: true,
        },
      },
    },
  })

  if (!post) {
    notFound()
  }

  const relatedPosts = await db.post.findMany({
    where: {
      id: {
        not: post.id,
      },
      OR: [
        {
          tags: {
            some: {
              id: {
                in: post.tags.map((tag) => tag.id),
              },
            },
          },
        },
        {
          userId: post.userId,
        },
      ],
    },
    take: 3,
    include: {
      user: {
        select: {
          id: true,
          name: true,
          username: true,
          image: true,
        },
      },
    },
  })

  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <BlogPost post={post} />
        <Comments postId={post.id} comments={post.comments} />
        <RelatedPosts posts={relatedPosts} />
      </div>
    </div>
  )
}
```

```typescript
// __tests__/pages/blog-post.test.tsx
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import BlogPostPage from "@/app/blog/[slug]/page"

// 模拟数据库
vi.mock("@/lib/db", () => ({
  db: {
    post: {
      findUnique: vi.fn(),
      findMany: vi.fn(),
    },
  },
}))

// 模拟组件
vi.mock("@/components/blog/blog-post", () => ({
  BlogPost: ({ post }: { post: any }) => (
    <article data-testid="blog-post">
      <h1>{post.title}</h1>
      <div data-testid="post-content">{post.content}</div>
      <div data-testid="post-meta">
        作者: {post.user.name} · {post._count.likes} 点赞
      </div>
    </article>
  ),
}))

vi.mock("@/components/blog/comments", () => ({
  Comments: ({ postId, comments }: { postId: string; comments: any[] }) => (
    <div data-testid="comments">
      <div>评论 ({comments.length})</div>
      {comments.map((comment) => (
        <div key={comment.id} data-testid="comment">
          {comment.content}
        </div>
      ))}
    </div>
  ),
}))

vi.mock("@/components/blog/related-posts", () => ({
  RelatedPosts: ({ posts }: { posts: any[] }) => (
    <div data-testid="related-posts">
      <h3>相关文章</h3>
      {posts.map((post) => (
        <div key={post.id} data-testid="related-post">
          {post.title}
        </div>
      ))}
    </div>
  ),
}))

vi.mock("next/navigation", () => ({
  notFound: vi.fn(),
}))

describe("BlogPostPage", () => {
  const mockDb = require("@/lib/db").db

  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("应该渲染博客文章页面", async () => {
    const mockPost = {
      id: "1",
      title: "测试文章",
      content: "这是一篇测试文章的内容",
      slug: "test-post",
      createdAt: new Date(),
      user: {
        id: "1",
        name: "张三",
        username: "zhangsan",
        image: "/avatar.jpg",
      },
      tags: [
        { id: "1", name: "React" },
        { id: "2", name: "Next.js" },
      ],
      comments: [
        {
          id: "1",
          content: "很好的文章！",
          user: {
            id: "2",
            name: "李四",
            username: "lisi",
            image: "/avatar2.jpg",
          },
          createdAt: new Date(),
        },
      ],
      _count: {
        likes: 10,
        comments: 1,
      },
    }

    const mockRelatedPosts = [
      {
        id: "2",
        title: "相关文章1",
        slug: "related-post-1",
        user: {
          id: "1",
          name: "张三",
          username: "zhangsan",
          image: "/avatar.jpg",
        },
      },
      {
        id: "3",
        title: "相关文章2",
        slug: "related-post-2",
        user: {
          id: "2",
          name: "李四",
          username: "lisi",
          image: "/avatar2.jpg",
        },
      },
    ]

    mockDb.post.findUnique.mockResolvedValue(mockPost)
    mockDb.post.findMany.mockResolvedValue(mockRelatedPosts)

    render(await BlogPostPage({ params: { slug: "test-post" } }))

    await waitFor(() => {
      expect(screen.getByText("测试文章")).toBeInTheDocument()
      expect(screen.getByTestId("blog-post")).toBeInTheDocument()
      expect(screen.getByTestId("comments")).toBeInTheDocument()
      expect(screen.getByTestId("related-posts")).toBeInTheDocument()
    })

    expect(screen.getByText("很好的文章！")).toBeInTheDocument()
    expect(screen.getByText("评论 (1)")).toBeInTheDocument()
    expect(screen.getByText("相关文章")).toBeInTheDocument()
  })

  it("应该处理文章不存在的情况", async () => {
    mockDb.post.findUnique.mockResolvedValue(null)
    const { notFound } = require("next/navigation")

    await BlogPostPage({ params: { slug: "nonexistent" } })

    expect(notFound).toHaveBeenCalled()
  })

  it("应该处理没有评论的情况", async () => {
    const mockPost = {
      id: "1",
      title: "测试文章",
      content: "这是一篇测试文章的内容",
      slug: "test-post",
      createdAt: new Date(),
      user: {
        id: "1",
        name: "张三",
        username: "zhangsan",
        image: "/avatar.jpg",
      },
      tags: [],
      comments: [],
      _count: {
        likes: 0,
        comments: 0,
      },
    }

    mockDb.post.findUnique.mockResolvedValue(mockPost)
    mockDb.post.findMany.mockResolvedValue([])

    render(await BlogPostPage({ params: { slug: "test-post" } }))

    await waitFor(() => {
      expect(screen.getByText("评论 (0)")).toBeInTheDocument()
      expect(screen.queryByTestId("comment")).not.toBeInTheDocument()
    })
  })

  it("应该处理没有相关文章的情况", async () => {
    const mockPost = {
      id: "1",
      title: "测试文章",
      content: "这是一篇测试文章的内容",
      slug: "test-post",
      createdAt: new Date(),
      user: {
        id: "1",
        name: "张三",
        username: "zhangsan",
        image: "/avatar.jpg",
      },
      tags: [],
      comments: [],
      _count: {
        likes: 0,
        comments: 0,
      },
    }

    mockDb.post.findUnique.mockResolvedValue(mockPost)
    mockDb.post.findMany.mockResolvedValue([])

    render(await BlogPostPage({ params: { slug: "test-post" } }))

    await waitFor(() => {
      expect(screen.getByTestId("related-posts")).toBeInTheDocument()
      expect(screen.queryByTestId("related-post")).not.toBeInTheDocument()
    })
  })
})
```

## API路由集成测试

### 1. 用户API测试

```typescript
// src/app/api/users/route.ts
import { NextRequest, NextResponse } from "next/server"
import { db } from "@/lib/db"
import { userSchema } from "@/lib/validation/schemas"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get("page") || "1")
    const limit = parseInt(searchParams.get("limit") || "10")
    const search = searchParams.get("search") || ""

    const skip = (page - 1) * limit

    const where = search
      ? {
          OR: [
            {
              name: {
                contains: search,
                mode: "insensitive",
              },
            },
            {
              email: {
                contains: search,
                mode: "insensitive",
              },
            },
          ],
        }
      : {}

    const [users, total] = await Promise.all([
      db.user.findMany({
        where,
        skip,
        take: limit,
        select: {
          id: true,
          name: true,
          email: true,
          age: true,
          bio: true,
          createdAt: true,
          updatedAt: true,
        },
        orderBy: {
          createdAt: "desc",
        },
      }),
      db.user.count({ where }),
    ])

    return NextResponse.json({
      users,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    })
  } catch (error) {
    return NextResponse.json(
      { error: "获取用户列表失败" },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()

    const validatedData = userSchema.parse(body)

    const existingUser = await db.user.findUnique({
      where: { email: validatedData.email },
    })

    if (existingUser) {
      return NextResponse.json(
        { error: "邮箱已被使用" },
        { status: 400 }
      )
    }

    const user = await db.user.create({
      data: validatedData,
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

    return NextResponse.json(user, { status: 201 })
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "数据验证失败", details: error.errors },
        { status: 400 }
      )
    }

    return NextResponse.json(
      { error: "创建用户失败" },
      { status: 500 }
    )
  }
}
```

```typescript
// __tests__/api/users.test.ts
import { NextRequest } from "next/server"
import { GET, POST } from "@/app/api/users/route"
import { prisma } from "@/lib/prisma"

// 模拟Prisma
vi.mock("@/lib/prisma", () => ({
  prisma: {
    user: {
      findMany: vi.fn(),
      findUnique: vi.fn(),
      count: vi.fn(),
      create: vi.fn(),
    },
  },
}))

describe("Users API", () => {
  const mockPrisma = prisma as any

  beforeEach(() => {
    vi.clearAllMocks()
  })

  describe("GET /api/users", () => {
    it("应该返回用户列表", async () => {
      const mockUsers = [
        {
          id: "1",
          name: "张三",
          email: "zhangsan@example.com",
          age: 25,
          bio: "前端开发者",
          createdAt: new Date(),
          updatedAt: new Date(),
        },
        {
          id: "2",
          name: "李四",
          email: "lisi@example.com",
          age: 30,
          bio: "后端开发者",
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ]

      mockPrisma.user.findMany.mockResolvedValue(mockUsers)
      mockPrisma.user.count.mockResolvedValue(2)

      const request = new NextRequest("http://localhost:3000/api/users")
      const response = await GET(request)

      expect(response.status).toBe(200)
      const data = await response.json()

      expect(data.users).toHaveLength(2)
      expect(data.pagination.page).toBe(1)
      expect(data.pagination.limit).toBe(10)
      expect(data.pagination.total).toBe(2)
    })

    it("应该支持分页", async () => {
      const mockUsers = [
        {
          id: "1",
          name: "张三",
          email: "zhangsan@example.com",
          age: 25,
          bio: "前端开发者",
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ]

      mockPrisma.user.findMany.mockResolvedValue(mockUsers)
      mockPrisma.user.count.mockResolvedValue(15)

      const request = new NextRequest("http://localhost:3000/api/users?page=2&limit=5")
      const response = await GET(request)

      expect(response.status).toBe(200)
      const data = await response.json()

      expect(data.pagination.page).toBe(2)
      expect(data.pagination.limit).toBe(5)
      expect(data.pagination.totalPages).toBe(3)

      expect(mockPrisma.user.findMany).toHaveBeenCalledWith({
        skip: 5,
        take: 5,
        select: expect.any(Object),
        orderBy: { createdAt: "desc" },
      })
    })

    it("应该支持搜索", async () => {
      const mockUsers = [
        {
          id: "1",
          name: "张三",
          email: "zhangsan@example.com",
          age: 25,
          bio: "前端开发者",
          createdAt: new Date(),
          updatedAt: new Date(),
        },
      ]

      mockPrisma.user.findMany.mockResolvedValue(mockUsers)
      mockPrisma.user.count.mockResolvedValue(1)

      const request = new NextRequest("http://localhost:3000/api/users?search=张三")
      const response = await GET(request)

      expect(response.status).toBe(200)

      expect(mockPrisma.user.findMany).toHaveBeenCalledWith({
        where: {
          OR: [
            {
              name: {
                contains: "张三",
                mode: "insensitive",
              },
            },
            {
              email: {
                contains: "张三",
                mode: "insensitive",
              },
            },
          ],
        },
        skip: 0,
        take: 10,
        select: expect.any(Object),
        orderBy: { createdAt: "desc" },
      })
    })

    it("应该处理错误", async () => {
      mockPrisma.user.findMany.mockRejectedValue(new Error("数据库错误"))

      const request = new NextRequest("http://localhost:3000/api/users")
      const response = await GET(request)

      expect(response.status).toBe(500)
      const data = await response.json()
      expect(data.error).toBe("获取用户列表失败")
    })
  })

  describe("POST /api/users", () => {
    it("应该创建新用户", async () => {
      const mockUser = {
        id: "1",
        name: "张三",
        email: "zhangsan@example.com",
        age: 25,
        bio: "前端开发者",
        createdAt: new Date(),
        updatedAt: new Date(),
      }

      mockPrisma.user.findUnique.mockResolvedValue(null)
      mockPrisma.user.create.mockResolvedValue(mockUser)

      const request = new NextRequest("http://localhost:3000/api/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: "张三",
          email: "zhangsan@example.com",
          age: 25,
          bio: "前端开发者",
        }),
      })

      const response = await POST(request)

      expect(response.status).toBe(201)
      const data = await response.json()

      expect(data.name).toBe("张三")
      expect(data.email).toBe("zhangsan@example.com")
    })

    it("应该拒绝重复的邮箱", async () => {
      const existingUser = {
        id: "1",
        name: "张三",
        email: "zhangsan@example.com",
        age: 25,
      }

      mockPrisma.user.findUnique.mockResolvedValue(existingUser)

      const request = new NextRequest("http://localhost:3000/api/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: "李四",
          email: "zhangsan@example.com", // 重复邮箱
          age: 30,
        }),
      })

      const response = await POST(request)

      expect(response.status).toBe(400)
      const data = await response.json()
      expect(data.error).toBe("邮箱已被使用")
    })

    it("应该验证输入数据", async () => {
      const request = new NextRequest("http://localhost:3000/api/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: "", // 无效姓名
          email: "invalid-email", // 无效邮箱
          age: 15, // 无效年龄
        }),
      })

      const response = await POST(request)

      expect(response.status).toBe(400)
      const data = await response.json()
      expect(data.error).toBe("数据验证失败")
      expect(data.details).toHaveLength(3)
    })
  })
})
```

## 表单交互集成测试

### 1. 注册表单测试

```typescript
// src/components/auth/register-form.tsx
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
import { useRouter } from "next/navigation"
import { toast } from "react-hot-toast"

const registerSchema = z.object({
  name: z.string().min(2, "姓名至少需要2个字符").max(50, "姓名不能超过50个字符"),
  email: z.string().email("请输入有效的邮箱地址"),
  password: z.string().min(6, "密码至少需要6个字符"),
  confirmPassword: z.string(),
  age: z.number().min(18, "年龄必须大于18岁").max(120, "年龄不能超过120岁"),
}).refine((data) => data.password === data.confirmPassword, {
  message: "密码不匹配",
  path: ["confirmPassword"],
})

type RegisterFormData = z.infer<typeof registerSchema>

export function RegisterForm() {
  const [isSubmitting, setIsSubmitting] = useState(false)
  const router = useRouter()

  const form = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
    defaultValues: {
      name: "",
      email: "",
      password: "",
      confirmPassword: "",
      age: 18,
    },
  })

  const onSubmit = async (data: RegisterFormData) => {
    setIsSubmitting(true)
    try {
      const response = await fetch("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: data.name,
          email: data.email,
          password: data.password,
          age: data.age,
        }),
      })

      if (response.ok) {
        toast.success("注册成功！")
        router.push("/login")
      } else {
        const error = await response.json()
        toast.error(error.error || "注册失败")
      }
    } catch (error) {
      toast.error("注册失败，请重试")
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <Card className="w-[400px]">
      <CardHeader>
        <CardTitle>注册</CardTitle>
        <CardDescription>
          创建您的账户
        </CardDescription>
      </CardHeader>
      <CardContent>
        <Form {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-4">
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
              name="age"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>年龄</FormLabel>
                  <FormControl>
                    <Input
                      type="number"
                      placeholder="25"
                      {...field}
                      onChange={(e) => field.onChange(parseInt(e.target.value) || 0)}
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
                    <Input type="password" placeholder="******" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <FormField
              control={form.control}
              name="confirmPassword"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>确认密码</FormLabel>
                  <FormControl>
                    <Input type="password" placeholder="******" {...field} />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            <Button type="submit" className="w-full" disabled={isSubmitting}>
              {isSubmitting ? "注册中..." : "注册"}
            </Button>
          </form>
        </Form>
      </CardContent>
    </Card>
  )
}
```

```typescript
// __tests__/components/auth/register-form.test.tsx
import { render, screen, waitFor } from "@testing-library/react"
import userEvent from "@testing-library/user-event"
import { RegisterForm } from "@/components/auth/register-form"
import { toast } from "react-hot-toast"

// 模拟依赖
vi.mock("next/navigation", () => ({
  useRouter: () => ({
    push: vi.fn(),
  }),
}))

vi.mock("react-hot-toast", () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}))

// 模拟fetch
global.fetch = vi.fn()

describe("RegisterForm", () => {
  const mockPush = vi.fn()
  const mockToastSuccess = vi.fn()
  const mockToastError = vi.fn()

  beforeEach(() => {
    vi.clearAllMocks()
    const { useRouter } = require("next/navigation")
    useRouter.mockReturnValue({ push: mockPush })
    const { toast } = require("react-hot-toast")
    toast.success = mockToastSuccess
    toast.error = mockToastError
  })

  it("应该渲染注册表单", () => {
    render(<RegisterForm />)

    expect(screen.getByLabelText(/姓名/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/邮箱/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/年龄/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/密码/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/确认密码/i)).toBeInTheDocument()
    expect(screen.getByRole("button", { name: /注册/i })).toBeInTheDocument()
  })

  it("应该显示验证错误", async () => {
    const user = userEvent.setup()
    render(<RegisterForm />)

    // 尝试提交空表单
    await user.click(screen.getByRole("button", { name: /注册/i }))

    await waitFor(() => {
      expect(screen.getByText("姓名至少需要2个字符")).toBeInTheDocument()
      expect(screen.getByText("请输入有效的邮箱地址")).toBeInTheDocument()
      expect(screen.getByText("密码至少需要6个字符")).toBeInTheDocument()
    })
  })

  it("应该验证密码匹配", async () => {
    const user = userEvent.setup()
    render(<RegisterForm />)

    await user.type(screen.getByLabelText(/姓名/i), "张三")
    await user.type(screen.getByLabelText(/邮箱/i), "test@example.com")
    await user.type(screen.getByLabelText(/密码/i), "password123")
    await user.type(screen.getByLabelText(/确认密码/i), "different123")

    await user.click(screen.getByRole("button", { name: /注册/i }))

    await waitFor(() => {
      expect(screen.getByText("密码不匹配")).toBeInTheDocument()
    })
  })

  it("应该成功提交表单", async () => {
    const user = userEvent.setup()
    const mockResponse = {
      ok: true,
      json: vi.fn().mockResolvedValue({}),
    }

    ;(fetch as any).mockResolvedValue(mockResponse)

    render(<RegisterForm />)

    await user.type(screen.getByLabelText(/姓名/i), "张三")
    await user.type(screen.getByLabelText(/邮箱/i), "test@example.com")
    await user.type(screen.getByLabelText(/年龄/i), "25")
    await user.type(screen.getByLabelText(/密码/i), "password123")
    await user.type(screen.getByLabelText(/确认密码/i), "password123")

    await user.click(screen.getByRole("button", { name: /注册/i }))

    await waitFor(() => {
      expect(fetch).toHaveBeenCalledWith("/api/auth/register", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          name: "张三",
          email: "test@example.com",
          password: "password123",
          age: 25,
        }),
      })
    })

    await waitFor(() => {
      expect(mockToastSuccess).toHaveBeenCalledWith("注册成功！")
      expect(mockPush).toHaveBeenCalledWith("/login")
    })
  })

  it("应该处理注册失败", async () => {
    const user = userEvent.setup()
    const mockResponse = {
      ok: false,
      json: vi.fn().mockResolvedValue({ error: "邮箱已被使用" }),
    }

    ;(fetch as any).mockResolvedValue(mockResponse)

    render(<RegisterForm />)

    await user.type(screen.getByLabelText(/姓名/i), "张三")
    await user.type(screen.getByLabelText(/邮箱/i), "test@example.com")
    await user.type(screen.getByLabelText(/年龄/i), "25")
    await user.type(screen.getByLabelText(/密码/i), "password123")
    await user.type(screen.getByLabelText(/确认密码/i), "password123")

    await user.click(screen.getByRole("button", { name: /注册/i }))

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith("邮箱已被使用")
    })
  })

  it("应该处理网络错误", async () => {
    const user = userEvent.setup()
    ;(fetch as any).mockRejectedValue(new Error("网络错误"))

    render(<RegisterForm />)

    await user.type(screen.getByLabelText(/姓名/i), "张三")
    await user.type(screen.getByLabelText(/邮箱/i), "test@example.com")
    await user.type(screen.getByLabelText(/年龄/i), "25")
    await user.type(screen.getByLabelText(/密码/i), "password123")
    await user.type(screen.getByLabelText(/确认密码/i), "password123")

    await user.click(screen.getByRole("button", { name: /注册/i }))

    await waitFor(() => {
      expect(mockToastError).toHaveBeenCalledWith("注册失败，请重试")
    })
  })

  it("应该在提交时禁用按钮", async () => {
    const user = userEvent.setup()
    ;(fetch as any).mockImplementation(() => new Promise(() => {}))

    render(<RegisterForm />)

    await user.type(screen.getByLabelText(/姓名/i), "张三")
    await user.type(screen.getByLabelText(/邮箱/i), "test@example.com")
    await user.type(screen.getByLabelText(/年龄/i), "25")
    await user.type(screen.getByLabelText(/密码/i), "password123")
    await user.type(screen.getByLabelText(/确认密码/i), "password123")

    await user.click(screen.getByRole("button", { name: /注册/i }))

    expect(screen.getByRole("button", { name: /注册中/i })).toBeDisabled()
  })
})
```

## 状态管理集成测试

### 1. 全局状态管理测试

```typescript
// src/store/cart-store.ts
import { create } from "zustand"
import { persist } from "zustand/middleware"

interface CartItem {
  id: string
  name: string
  price: number
  quantity: number
  image?: string
}

interface CartStore {
  items: CartItem[]
  addItem: (item: Omit<CartItem, "quantity">) => void
  removeItem: (id: string) => void
  updateQuantity: (id: string, quantity: number) => void
  clearCart: () => void
  getTotalItems: () => number
  getTotalPrice: () => number
}

export const useCartStore = create<CartStore>()(
  persist(
    (set, get) => ({
      items: [],

      addItem: (item) => {
        const items = get().items
        const existingItem = items.find((i) => i.id === item.id)

        if (existingItem) {
          set({
            items: items.map((i) =>
              i.id === item.id
                ? { ...i, quantity: i.quantity + 1 }
                : i
            ),
          })
        } else {
          set({
            items: [...items, { ...item, quantity: 1 }],
          })
        }
      },

      removeItem: (id) => {
        set({
          items: get().items.filter((item) => item.id !== id),
        })
      },

      updateQuantity: (id, quantity) => {
        if (quantity <= 0) {
          get().removeItem(id)
        } else {
          set({
            items: get().items.map((item) =>
              item.id === id ? { ...item, quantity } : item
            ),
          })
        }
      },

      clearCart: () => {
        set({ items: [] })
      },

      getTotalItems: () => {
        return get().items.reduce((total, item) => total + item.quantity, 0)
      },

      getTotalPrice: () => {
        return get().items.reduce(
          (total, item) => total + item.price * item.quantity,
          0
        )
      },
    }),
    {
      name: "cart-storage",
    }
  )
)
```

```typescript
// __tests__/store/cart-store.test.ts
import { useCartStore } from "@/store/cart-store"

describe("CartStore", () => {
  beforeEach(() => {
    // 清理localStorage
    localStorage.clear()

    // 重置store
    useCartStore.setState({
      items: [],
    })
  })

  it("应该添加新商品到购物车", () => {
    const item = {
      id: "1",
      name: "测试商品",
      price: 100,
      image: "/test.jpg",
    }

    useCartStore.getState().addItem(item)

    expect(useCartStore.getState().items).toHaveLength(1)
    expect(useCartStore.getState().items[0]).toEqual({
      ...item,
      quantity: 1,
    })
  })

  it("应该增加现有商品的数量", () => {
    const item = {
      id: "1",
      name: "测试商品",
      price: 100,
    }

    // 第一次添加
    useCartStore.getState().addItem(item)

    // 第二次添加相同商品
    useCartStore.getState().addItem(item)

    expect(useCartStore.getState().items).toHaveLength(1)
    expect(useCartStore.getState().items[0].quantity).toBe(2)
  })

  it("应该从购物车中移除商品", () => {
    const item1 = {
      id: "1",
      name: "商品1",
      price: 100,
    }
    const item2 = {
      id: "2",
      name: "商品2",
      price: 200,
    }

    useCartStore.getState().addItem(item1)
    useCartStore.getState().addItem(item2)

    expect(useCartStore.getState().items).toHaveLength(2)

    useCartStore.getState().removeItem("1")

    expect(useCartStore.getState().items).toHaveLength(1)
    expect(useCartStore.getState().items[0].id).toBe("2")
  })

  it("应该更新商品数量", () => {
    const item = {
      id: "1",
      name: "测试商品",
      price: 100,
    }

    useCartStore.getState().addItem(item)
    useCartStore.getState().updateQuantity("1", 3)

    expect(useCartStore.getState().items[0].quantity).toBe(3)
  })

  it("应该在数量为0时移除商品", () => {
    const item = {
      id: "1",
      name: "测试商品",
      price: 100,
    }

    useCartStore.getState().addItem(item)
    useCartStore.getState().updateQuantity("1", 0)

    expect(useCartStore.getState().items).toHaveLength(0)
  })

  it("应该清空购物车", () => {
    const item1 = {
      id: "1",
      name: "商品1",
      price: 100,
    }
    const item2 = {
      id: "2",
      name: "商品2",
      price: 200,
    }

    useCartStore.getState().addItem(item1)
    useCartStore.getState().addItem(item2)

    expect(useCartStore.getState().items).toHaveLength(2)

    useCartStore.getState().clearCart()

    expect(useCartStore.getState().items).toHaveLength(0)
  })

  it("应该正确计算总商品数量", () => {
    const item1 = {
      id: "1",
      name: "商品1",
      price: 100,
    }
    const item2 = {
      id: "2",
      name: "商品2",
      price: 200,
    }

    useCartStore.getState().addItem(item1)
    useCartStore.getState().addItem(item1) // 同一商品添加两次
    useCartStore.getState().addItem(item2)

    const totalItems = useCartStore.getState().getTotalItems()
    expect(totalItems).toBe(3) // 2个商品1 + 1个商品2
  })

  it("应该正确计算总价格", () => {
    const item1 = {
      id: "1",
      name: "商品1",
      price: 100,
    }
    const item2 = {
      id: "2",
      name: "商品2",
      price: 200,
    }

    useCartStore.getState().addItem(item1)
    useCartStore.getState().addItem(item1) // 商品1 x2 = 200
    useCartStore.getState().addItem(item2) // 商品2 x1 = 200

    const totalPrice = useCartStore.getState().getTotalPrice()
    expect(totalPrice).toBe(400)
  })

  it("应该持久化到localStorage", () => {
    const item = {
      id: "1",
      name: "测试商品",
      price: 100,
    }

    useCartStore.getState().addItem(item)

    const localStorageData = localStorage.getItem("cart-storage")
    expect(localStorageData).toBeDefined()

    const parsedData = JSON.parse(localStorageData!)
    expect(parsedData.state.items).toHaveLength(1)
    expect(parsedData.state.items[0].name).toBe("测试商品")
  })
})
```

## 性能测试集成

### 1. 组件渲染性能测试

```typescript
// __tests__/performance/rendering.test.tsx
import { render, screen } from "@testing-library/react"
import { LargeList } from "@/components/performance/large-list"
import { vi } from "vitest"

// 模拟performance API
const mockPerformance = {
  now: vi.fn(),
  mark: vi.fn(),
  measure: vi.fn(),
}

global.performance = mockPerformance as any

describe("Component Rendering Performance", () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it("应该在合理时间内渲染大型列表", () => {
    const items = Array.from({ length: 1000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
    }))

    // 模拟时间戳
    mockPerformance.now.mockReturnValueOnce(0) // 开始时间
    mockPerformance.now.mockReturnValueOnce(100) // 结束时间

    const startTime = performance.now()
    render(<LargeList items={items} />)
    const endTime = performance.now()

    expect(endTime - startTime).toBeLessThan(500) // 应该在500ms内完成
    expect(screen.getAllByText(/Item \d+/)).toHaveLength(1000)
  })

  it("应该使用虚拟化处理大量数据", () => {
    const items = Array.from({ length: 10000 }, (_, i) => ({
      id: i,
      name: `Item ${i}`,
    }))

    // 检查是否使用了虚拟化
    const VirtualizedComponent = vi.fn()
    vi.doMock("@/components/virtualized-list", () => ({
      default: VirtualizedComponent,
    }))

    render(<LargeList items={items} />)

    expect(VirtualizedComponent).toHaveBeenCalledWith(
      expect.objectContaining({
        items: expect.arrayContaining(items),
      }),
      {}
    )
  })
})
```

## 测试最佳实践

### 1. 测试策略

```typescript
// 测试策略示例
describe("集成测试策略", () => {
  it("应该测试完整的用户流程", async () => {
    // 1. 用户访问首页
    render(<HomePage />)

    // 2. 用户点击登录
    await userEvent.click(screen.getByText("登录"))

    // 3. 用户填写登录表单
    await userEvent.type(screen.getByLabelText(/邮箱/i), "test@example.com")
    await userEvent.type(screen.getByLabelText(/密码/i), "password123")

    // 4. 用户提交表单
    await userEvent.click(screen.getByRole("button", { name: /登录/i }))

    // 5. 验证登录成功后的状态
    await waitFor(() => {
      expect(screen.getByText("欢迎回来")).toBeInTheDocument()
    })
  })
})
```

### 2. 测试数据管理

```typescript
// __tests__/fixtures/index.ts
export const testUsers = [
  {
    id: "1",
    name: "张三",
    email: "zhangsan@example.com",
    age: 25,
    bio: "前端开发者",
  },
  {
    id: "2",
    name: "李四",
    email: "lisi@example.com",
    age: 30,
    bio: "后端开发者",
  },
]

export const testPosts = [
  {
    id: "1",
    title: "测试文章1",
    content: "测试内容1",
    userId: "1",
  },
  {
    id: "2",
    title: "测试文章2",
    content: "测试内容2",
    userId: "2",
  },
]

export const createTestDatabase = () => {
  return {
    users: testUsers,
    posts: testPosts,
  }
}
```

### 3. 测试工具函数

```typescript
// __tests__/utils/api-helpers.ts
import { NextApiRequest, NextApiResponse } from "next"

export function createMockRequest(
  method: string = "GET",
  body?: any,
  query?: any
): NextApiRequest {
  return {
    method,
    body,
    query,
    headers: {},
  } as NextApiRequest
}

export function createMockResponse(): NextApiResponse {
  const res: any = {}
  res.status = vi.fn().mockReturnThis()
  res.json = vi.fn().mockReturnThis()
  res.end = vi.fn().mockReturnThis()
  return res as NextApiResponse
}

export async function testApiEndpoint(
  handler: (req: NextApiRequest, res: NextApiResponse) => void,
  request: NextApiRequest
): Promise<{ status: number; data: any }> {
  const res = createMockResponse()
  await handler(request, res)

  return {
    status: (res as any).status.mock.calls[0]?.[0] || 200,
    data: (res as any).json.mock.calls[0]?.[0],
  }
}
```

## 总结

通过本指南，我们学习了Next.js项目中集成测试的各个方面：

### 核心概念
- 集成测试的定义和作用
- 与单元测试的区别和互补关系
- 测试环境的配置和设置

### 测试类型
- 页面组件的集成测试
- API路由的集成测试
- 表单交互的集成测试
- 状态管理的集成测试
- 性能测试集成

### 实践技巧
- 测试数据库设置和清理
- Mock和真实依赖的选择
- 异步测试的处理
- 测试数据的组织和管理

### 从PHP开发者角度
- 从Laravel的测试体系转变
- 前端特有的测试考虑
- 组件测试的新范式

掌握这些集成测试技能，将帮助您构建更加健壮、可靠的Next.js应用程序。集成测试确保了各个组件和模块之间的正确交互，是构建高质量应用的重要保障。