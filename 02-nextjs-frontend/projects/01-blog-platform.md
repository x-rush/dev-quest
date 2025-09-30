# 01 - 博客平台实战项目

## 目录

1. [项目概述](#项目概述)
2. [技术栈选择](#技术栈选择)
3. [项目结构](#项目结构)
4. [核心功能实现](#核心功能实现)
5. [数据管理](#数据管理)
6. [用户认证](#用户认证)
7. [性能优化](#性能优化)
8. [SEO优化](#seo优化)
9. [部署配置](#部署配置)
10. [总结与扩展](#总结与扩展)

## 项目概述

我们将构建一个现代化的博客平台，具备完整的CMS功能、用户认证、评论系统、搜索功能和SEO优化。

### 功能特性

- **文章管理**: 创建、编辑、删除、发布文章
- **用户系统**: 注册、登录、个人资料管理
- **评论系统**: 实时评论、回复、点赞
- **搜索功能**: 全文搜索、标签过滤
- **SEO优化**: 动态元数据、结构化数据
- **响应式设计**: 移动端适配
- **暗色模式**: 主题切换
- **性能优化**: 图片优化、缓存策略

### 与PHP博客系统的对比

**传统PHP博客（如WordPress）：**
- 服务器端渲染
- 数据库查询密集
- 插件系统复杂
- 主题开发限制

**Next.js博客平台：**
- 混合渲染策略
- 静态生成 + 增量更新
- 组件化架构
- 现代化开发体验

## 技术栈选择

### 前端技术栈

```json
{
  "framework": "Next.js 15",
  "language": "TypeScript",
  "styling": "Tailwind CSS + Shadcn/ui",
  "state": "Zustand + TanStack Query",
  "form": "React Hook Form + Zod",
  "ui": "Radix UI + Lucide React",
  "animation": "Framer Motion",
  "image": "next/image",
  "deployment": "Vercel"
}
```

### 后端技术栈

```json
{
  "api": "Next.js API Routes",
  "database": "PostgreSQL + Prisma",
  "auth": "NextAuth.js",
  "storage": "Vercel Blob / AWS S3",
  "search": "Algolia",
  "analytics": "Vercel Analytics",
  "monitoring": "Sentry"
}
```

### 开发工具

```json
{
  "packageManager": "pnpm",
  "testing": "Vitest + Testing Library + Playwright",
  "linting": "ESLint + Prettier",
  "typeChecking": "TypeScript",
  "build": "Next.js Build",
  "deployment": "Vercel CLI"
}
```

## 项目结构

```
blog-platform/
├── app/
│   ├── (auth)/
│   │   ├── login/
│   │   ├── register/
│   │   └── layout.tsx
│   ├── (dashboard)/
│   │   ├── posts/
│   │   ├── settings/
│   │   └── layout.tsx
│   ├── blog/
│   │   ├── [slug]/
│   │   ├── tag/[tag]/
│   │   └── page.tsx
│   ├── api/
│   │   ├── auth/
│   │   ├── posts/
│   │   ├── comments/
│   │   └── search/
│   ├── globals.css
│   ├── layout.tsx
│   └── page.tsx
├── components/
│   ├── ui/
│   ├── blog/
│   ├── auth/
│   ├── dashboard/
│   └── layout/
├── lib/
│   ├── auth.ts
│   ├── db.ts
│   ├── utils.ts
│   └── validations.ts
├── hooks/
├── types/
├── public/
└── prisma/
```

## 核心功能实现

### 1. 文章管理系统

```typescript
// app/(dashboard)/posts/create/page.tsx
"use client"

import { useState } from "react"
import { useForm } from "react-hook-form"
import { zodResolver } from "@hookform/resolvers/zod"
import * as z from "zod"
import { useRouter } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Textarea } from "@/components/ui/textarea"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Form, FormControl, FormField, FormItem, FormLabel, FormMessage } from "@/components/ui/form"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { Badge } from "@/components/ui/badge"
import { toast } from "react-hot-toast"
import { createPost } from "@/lib/api/posts"
import { PostSchema } from "@/lib/validations"

const tags = ["Next.js", "React", "TypeScript", "Tailwind CSS", "Prisma", "PostgreSQL"]

export default function CreatePostPage() {
  const router = useRouter()
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  const form = useForm<z.infer<typeof PostSchema>>({
    resolver: zodResolver(PostSchema),
    defaultValues: {
      title: "",
      content: "",
      excerpt: "",
      status: "draft",
      featuredImage: "",
    },
  })

  const onSubmit = async (values: z.infer<typeof PostSchema>) => {
    setIsSubmitting(true)
    try {
      await createPost({
        ...values,
        tags: selectedTags,
      })
      toast.success("Post created successfully!")
      router.push("/dashboard/posts")
    } catch (error) {
      toast.error("Failed to create post")
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleTagToggle = (tag: string) => {
    setSelectedTags(prev =>
      prev.includes(tag)
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    )
  }

  return (
    <div className="max-w-4xl mx-auto p-6">
      <Card>
        <CardHeader>
          <CardTitle>Create New Post</CardTitle>
        </CardHeader>
        <CardContent>
          <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
              <FormField
                control={form.control}
                name="title"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Title</FormLabel>
                    <FormControl>
                      <Input placeholder="Enter post title" {...field} />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="excerpt"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Excerpt</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Write a brief excerpt"
                        className="h-20"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="featuredImage"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Featured Image URL</FormLabel>
                    <FormControl>
                      <Input
                        placeholder="https://example.com/image.jpg"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div>
                <FormLabel>Tags</FormLabel>
                <div className="flex flex-wrap gap-2 mt-2">
                  {tags.map((tag) => (
                    <Badge
                      key={tag}
                      variant={selectedTags.includes(tag) ? "default" : "outline"}
                      className="cursor-pointer"
                      onClick={() => handleTagToggle(tag)}
                    >
                      {tag}
                    </Badge>
                  ))}
                </div>
              </div>

              <FormField
                control={form.control}
                name="status"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Status</FormLabel>
                    <Select onValueChange={field.onChange} defaultValue={field.value}>
                      <FormControl>
                        <SelectTrigger>
                          <SelectValue placeholder="Select status" />
                        </SelectTrigger>
                      </FormControl>
                      <SelectContent>
                        <SelectItem value="draft">Draft</SelectItem>
                        <SelectItem value="published">Published</SelectItem>
                      </SelectContent>
                    </Select>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <FormField
                control={form.control}
                name="content"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Content</FormLabel>
                    <FormControl>
                      <Textarea
                        placeholder="Write your post content..."
                        className="min-h-[400px]"
                        {...field}
                      />
                    </FormControl>
                    <FormMessage />
                  </FormItem>
                )}
              />

              <div className="flex gap-4">
                <Button type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Creating..." : "Create Post"}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => router.back()}
                >
                  Cancel
                </Button>
              </div>
            </form>
          </Form>
        </CardContent>
      </Card>
    </div>
  )
}
```

### 2. 文章详情页面

```typescript
// app/blog/[slug]/page.tsx
import { notFound } from "next/navigation"
import { Metadata } from "next"
import { Suspense } from "react"
import Image from "next/image"
import Link from "next/link"
import { Calendar, User, Tag, Clock } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Separator } from "@/components/ui/separator"
import { CommentSection } from "@/components/blog/comment-section"
import { RelatedPosts } from "@/components/blog/related-posts"
import { TableOfContents } from "@/components/blog/table-of-contents"
import { ShareButtons } from "@/components/blog/share-buttons"
import { getPostBySlug, getRelatedPosts } from "@/lib/api/posts"
import { formatDate } from "@/lib/utils"
import { PostLoading } from "@/components/blog/post-loading"

// 生成静态参数
export async function generateStaticParams() {
  const posts = await getAllPosts()
  return posts.map((post) => ({
    slug: post.slug,
  }))
}

// 生成元数据
export async function generateMetadata({ params }: { params: { slug: string } }): Promise<Metadata> {
  const post = await getPostBySlug(params.slug)

  if (!post) {
    return {
      title: 'Post Not Found',
    }
  }

  return {
    title: `${post.title} | My Blog`,
    description: post.excerpt,
    keywords: post.tags.join(', '),
    openGraph: {
      title: post.title,
      description: post.excerpt,
      images: post.featuredImage ? [post.featuredImage] : [],
      type: 'article',
      publishedTime: post.publishedAt,
      authors: [post.author.name],
      tags: post.tags,
    },
    twitter: {
      card: 'summary_large_image',
      title: post.title,
      description: post.excerpt,
      images: post.featuredImage ? [post.featuredImage] : [],
    },
  }
}

async function PostContent({ slug }: { slug: string }) {
  const post = await getPostBySlug(slug)
  const relatedPosts = await getRelatedPosts(post.id, post.tags)

  if (!post) {
    notFound()
  }

  return (
    <article className="max-w-4xl mx-auto">
      {/* 文章头部 */}
      <header className="mb-8">
        <div className="flex flex-wrap gap-2 mb-4">
          {post.tags.map((tag) => (
            <Badge key={tag} variant="secondary">
              <Tag className="w-3 h-3 mr-1" />
              {tag}
            </Badge>
          ))}
        </div>

        <h1 className="text-4xl font-bold mb-4 leading-tight">{post.title}</h1>

        <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-6">
          <div className="flex items-center gap-2">
            <User className="w-4 h-4" />
            <Link href={`/author/${post.author.slug}`} className="hover:text-blue-600">
              {post.author.name}
            </Link>
          </div>
          <div className="flex items-center gap-2">
            <Calendar className="w-4 h-4" />
            <time dateTime={post.publishedAt}>
              {formatDate(post.publishedAt)}
            </time>
          </div>
          <div className="flex items-center gap-2">
            <Clock className="w-4 h-4" />
            <span>{post.readingTime} min read</span>
          </div>
        </div>

        {post.featuredImage && (
          <div className="relative h-64 md:h-96 mb-8 rounded-lg overflow-hidden">
            <Image
              src={post.featuredImage}
              alt={post.title}
              fill
              className="object-cover"
              priority
            />
          </div>
        )}

        <p className="text-lg text-gray-700 mb-8">{post.excerpt}</p>
      </header>

      {/* 文章主体 */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        <div className="lg:col-span-3">
          <div
            className="prose prose-lg max-w-none"
            dangerouslySetInnerHTML={{ __html: post.content }}
          />

          <Separator className="my-8" />

          {/* 分享按钮 */}
          <div className="mb-8">
            <h3 className="text-lg font-semibold mb-4">Share this post</h3>
            <ShareButtons
              title={post.title}
              url={`https://myblog.com/blog/${post.slug}`}
              excerpt={post.excerpt}
            />
          </div>

          {/* 评论系统 */}
          <CommentSection postId={post.id} />
        </div>

        {/* 侧边栏 */}
        <div className="lg:col-span-1">
          <div className="sticky top-8">
            <TableOfContents content={post.content} />
          </div>
        </div>
      </div>

      {/* 相关文章 */}
      {relatedPosts.length > 0 && (
        <div className="mt-12">
          <h2 className="text-2xl font-bold mb-6">Related Posts</h2>
          <RelatedPosts posts={relatedPosts} />
        </div>
      )}
    </article>
  )
}

export default function PostPage({ params }: { params: { slug: string } }) {
  return (
    <div className="min-h-screen bg-background">
      <Suspense fallback={<PostLoading />}>
        <PostContent slug={params.slug} />
      </Suspense>
    </div>
  )
}
```

### 3. 搜索功能

```typescript
// components/blog/search-posts.tsx
"use client"

import { useState, useEffect, useCallback } from "react"
import { useDebouncedCallback } from "use-debounce"
import { Search, Filter, X } from "lucide-react"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { Card, CardContent } from "@/components/ui/card"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import { searchPosts, SearchFilters } from "@/lib/api/search"
import { PostCard } from "@/components/blog/post-card"
import { PostLoading } from "@/components/blog/post-loading"

interface SearchPostsProps {
  initialQuery?: string
  initialFilters?: Partial<SearchFilters>
}

export function SearchPosts({ initialQuery = "", initialFilters = {} }: SearchPostsProps) {
  const [query, setQuery] = useState(initialQuery)
  const [filters, setFilters] = useState<SearchFilters>({
    tags: [],
    sortBy: "relevance",
    dateRange: "all",
    ...initialFilters,
  })
  const [results, setResults] = useState<any[]>([])
  const [loading, setLoading] = useState(false)
  const [showFilters, setShowFilters] = useState(false)

  // 防抖搜索
  const debouncedSearch = useDebouncedCallback(
    async (searchQuery: string, searchFilters: SearchFilters) => {
      if (!searchQuery.trim() && searchFilters.tags.length === 0) {
        setResults([])
        return
      }

      setLoading(true)
      try {
        const searchResults = await searchPosts(searchQuery, searchFilters)
        setResults(searchResults)
      } catch (error) {
        console.error("Search failed:", error)
      } finally {
        setLoading(false)
      }
    },
    300
  )

  useEffect(() => {
    debouncedSearch(query, filters)
  }, [query, filters, debouncedSearch])

  const handleSearch = (e: React.ChangeEvent<HTMLInputElement>) => {
    setQuery(e.target.value)
  }

  const handleTagToggle = (tag: string) => {
    setFilters(prev => ({
      ...prev,
      tags: prev.tags.includes(tag)
        ? prev.tags.filter(t => t !== tag)
        : [...prev.tags, tag],
    }))
  }

  const handleSortChange = (sortBy: string) => {
    setFilters(prev => ({ ...prev, sortBy }))
  }

  const handleDateRangeChange = (dateRange: string) => {
    setFilters(prev => ({ ...prev, dateRange }))
  }

  const clearFilters = () => {
    setFilters({
      tags: [],
      sortBy: "relevance",
      dateRange: "all",
    })
  }

  const availableTags = ["Next.js", "React", "TypeScript", "Tailwind CSS", "Prisma", "JavaScript", "CSS", "HTML"]

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="mb-8">
        <div className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
          <Input
            type="text"
            placeholder="Search posts..."
            value={query}
            onChange={handleSearch}
            className="pl-10 pr-12 h-12 text-base"
          />
          <Button
            variant="ghost"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="absolute right-2 top-1/2 transform -translate-y-1/2"
          >
            <Filter className="w-5 h-5" />
          </Button>
        </div>

        {/* 过滤器面板 */}
        {showFilters && (
          <Card className="mt-4">
            <CardContent className="p-6">
              <div className="flex justify-between items-center mb-4">
                <h3 className="font-semibold">Filters</h3>
                <Button variant="ghost" size="sm" onClick={clearFilters}>
                  <X className="w-4 h-4 mr-1" />
                  Clear all
                </Button>
              </div>

              <div className="space-y-4">
                <div>
                  <label className="text-sm font-medium mb-2 block">Sort by</label>
                  <Select value={filters.sortBy} onValueChange={handleSortChange}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="relevance">Relevance</SelectItem>
                      <SelectItem value="newest">Newest first</SelectItem>
                      <SelectItem value="oldest">Oldest first</SelectItem>
                      <SelectItem value="popular">Most popular</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Date range</label>
                  <Select value={filters.dateRange} onValueChange={handleDateRangeChange}>
                    <SelectTrigger>
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="all">All time</SelectItem>
                      <SelectItem value="today">Today</SelectItem>
                      <SelectItem value="week">This week</SelectItem>
                      <SelectItem value="month">This month</SelectItem>
                      <SelectItem value="year">This year</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div>
                  <label className="text-sm font-medium mb-2 block">Tags</label>
                  <div className="flex flex-wrap gap-2">
                    {availableTags.map((tag) => (
                      <Badge
                        key={tag}
                        variant={filters.tags.includes(tag) ? "default" : "outline"}
                        className="cursor-pointer"
                        onClick={() => handleTagToggle(tag)}
                      >
                        {tag}
                      </Badge>
                    ))}
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        )}

        {/* 活跃过滤器 */}
        {(query || filters.tags.length > 0) && (
          <div className="flex items-center gap-2 mt-4">
            <span className="text-sm text-gray-600">Active filters:</span>
            {query && (
              <Badge variant="secondary">
                Search: "{query}"
                <X
                  className="w-3 h-3 ml-1 cursor-pointer"
                  onClick={() => setQuery("")}
                />
              </Badge>
            )}
            {filters.tags.map((tag) => (
              <Badge key={tag} variant="secondary">
                {tag}
                <X
                  className="w-3 h-3 ml-1 cursor-pointer"
                  onClick={() => handleTagToggle(tag)}
                />
              </Badge>
            ))}
          </div>
        )}
      </div>

      {/* 搜索结果 */}
      <div>
        {loading ? (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[...Array(6)].map((_, i) => <PostLoading key={i} />)}
          </div>
        ) : (
          <>
            {results.length > 0 ? (
              <>
                <p className="text-sm text-gray-600 mb-4">
                  Found {results.length} result{results.length !== 1 ? 's' : ''}
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {results.map((post) => (
                    <PostCard key={post.id} post={post} />
                  ))}
                </div>
              </>
            ) : (
              <div className="text-center py-12">
                <Search className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  No results found
                </h3>
                <p className="text-gray-600">
                  Try adjusting your search or filters
                </p>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  )
}
```

## 数据管理

### Prisma模型定义

```typescript
// prisma/schema.prisma
// This is your Prisma schema file,
// learn more about it in the docs: https://pris.ly/d/prisma-schema

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
  name      String?
  username  String?  @unique
  bio       String?
  avatar    String?
  role      Role     @default(USER)
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  posts     Post[]
  comments  Comment[]
  accounts  Account[]
  sessions  Session[]

  @@map("users")
}

model Post {
  id            String      @id @default(cuid())
  title         String
  slug          String      @unique
  excerpt       String?
  content       String
  featuredImage String?
  status        PostStatus  @default(DRAFT)
  publishedAt   DateTime?
  readingTime   Int?        // in minutes
  views         Int         @default(0)
  createdAt     DateTime    @default(now())
  updatedAt     DateTime    @updatedAt

  // Relations
  authorId  String
  author    User      @relation(fields: [authorId], references: [id], onDelete: Cascade)
  tags      PostTag[]
  comments  Comment[]
  likes     Like[]

  @@map("posts")
}

model Tag {
  id          String @id @default(cuid())
  name        String @unique
  slug        String @unique
  description String?
  color       String?
  createdAt   DateTime @default(now())

  // Relations
  posts PostTag[]

  @@map("tags")
}

model PostTag {
  postId String
  tagId  String

  post Post @relation(fields: [postId], references: [id], onDelete: Cascade)
  tag  Tag  @relation(fields: [tagId], references: [id], onDelete: Cascade)

  @@id([postId, tagId])
  @@map("post_tags")
}

model Comment {
  id        String   @id @default(cuid())
  content   String
  createdAt DateTime @default(now())
  updatedAt DateTime @updatedAt

  // Relations
  postId   String
  post     Post   @relation(fields: [postId], references: [id], onDelete: Cascade)
  authorId String
  author   User   @relation(fields: [authorId], references: [id], onDelete: Cascade)
  parentId String?
  parent   Comment? @relation("CommentReplies", fields: [parentId], references: [id])
  replies  Comment[] @relation("CommentReplies")

  @@map("comments")
}

model Like {
  id        String   @id @default(cuid())
  createdAt DateTime @default(now())

  // Relations
  postId String
  post   Post   @relation(fields: [postId], references: [id], onDelete: Cascade)
  userId String
  user   User   @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([postId, userId])
  @@map("likes")
}

// NextAuth.js models
model Account {
  id                String  @id @default(cuid())
  userId            String
  type              String
  provider          String
  providerAccountId String
  refresh_token     String? @db.Text
  access_token      String? @db.Text
  expires_at        Int?
  token_type        String?
  scope             String?
  id_token          String? @db.Text
  session_state     String?

  user User @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@unique([provider, providerAccountId])
  @@map("accounts")
}

model Session {
  id           String   @id @default(cuid())
  sessionToken String   @unique
  userId       String
  expires      DateTime
  user         User     @relation(fields: [userId], references: [id], onDelete: Cascade)

  @@map("sessions")
}

model VerificationToken {
  identifier String
  token      String   @unique
  expires    DateTime

  @@unique([identifier, token])
  @@map("verification_tokens")
}

// Enums
enum Role {
  USER
  ADMIN
  MODERATOR
}

enum PostStatus {
  DRAFT
  PUBLISHED
  ARCHIVED
}
```

### API路由实现

```typescript
// app/api/posts/route.ts
import { NextRequest, NextResponse } from "next/server"
import { getServerSession } from "next-auth"
import { authOptions } from "@/lib/auth"
import { prisma } from "@/lib/db"
import { postSchema } from "@/lib/validations"
import { z } from "zod"

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const page = parseInt(searchParams.get("page") || "1")
    const limit = parseInt(searchParams.get("limit") || "10")
    const tag = searchParams.get("tag")
    const author = searchParams.get("author")
    const status = searchParams.get("status") || "PUBLISHED"

    const skip = (page - 1) * limit

    const where: any = { status }

    if (tag) {
      where.tags = {
        some: {
          tag: {
            slug: tag,
          },
        },
      }
    }

    if (author) {
      where.author = {
        username: author,
      }
    }

    const [posts, total] = await Promise.all([
      prisma.post.findMany({
        where,
        include: {
          author: {
            select: {
              id: true,
              name: true,
              username: true,
              avatar: true,
            },
          },
          tags: {
            include: {
              tag: true,
            },
          },
          _count: {
            select: {
              comments: true,
              likes: true,
            },
          },
        },
        orderBy: [
          { publishedAt: "desc" },
          { createdAt: "desc" },
        ],
        skip,
        take: limit,
      }),
      prisma.post.count({ where }),
    ])

    return NextResponse.json({
      posts: posts.map((post) => ({
        ...post,
        tags: post.tags.map((pt) => pt.tag),
      })),
      pagination: {
        page,
        limit,
        total,
        pages: Math.ceil(total / limit),
      },
    })
  } catch (error) {
    console.error("Error fetching posts:", error)
    return NextResponse.json(
      { error: "Failed to fetch posts" },
      { status: 500 }
    )
  }
}

export async function POST(request: NextRequest) {
  try {
    const session = await getServerSession(authOptions)

    if (!session?.user?.id) {
      return NextResponse.json(
        { error: "Unauthorized" },
        { status: 401 }
      )
    }

    const body = await request.json()
    const validatedData = postSchema.parse(body)

    // Generate slug from title
    const slug = validatedData.title
      .toLowerCase()
      .replace(/[^a-z0-9]+/g, "-")
      .replace(/(^-|-$)/g, "")

    // Check if slug already exists
    const existingPost = await prisma.post.findUnique({
      where: { slug },
    })

    if (existingPost) {
      return NextResponse.json(
        { error: "A post with this title already exists" },
        { status: 400 }
      )
    }

    // Calculate reading time (rough estimate)
    const wordsPerMinute = 200
    const wordCount = validatedData.content.split(/\s+/).length
    const readingTime = Math.ceil(wordCount / wordsPerMinute)

    // Create post
    const post = await prisma.post.create({
      data: {
        title: validatedData.title,
        slug,
        excerpt: validatedData.excerpt,
        content: validatedData.content,
        featuredImage: validatedData.featuredImage,
        status: validatedData.status,
        readingTime,
        authorId: session.user.id,
        publishedAt: validatedData.status === "PUBLISHED" ? new Date() : null,
        tags: {
          create: validatedData.tags.map((tagName: string) => ({
            tag: {
              connectOrCreate: {
                where: {
                  slug: tagName.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
                },
                create: {
                  name: tagName,
                  slug: tagName.toLowerCase().replace(/[^a-z0-9]+/g, "-"),
                },
              },
            },
          })),
        },
      },
      include: {
        author: {
          select: {
            id: true,
            name: true,
            username: true,
          },
        },
        tags: {
          include: {
            tag: true,
          },
        },
      },
    })

    return NextResponse.json(
      {
        message: "Post created successfully",
        post: {
          ...post,
          tags: post.tags.map((pt) => pt.tag),
        },
      },
      { status: 201 }
    )
  } catch (error) {
    if (error instanceof z.ZodError) {
      return NextResponse.json(
        { error: "Validation failed", details: error.errors },
        { status: 400 }
      )
    }

    console.error("Error creating post:", error)
    return NextResponse.json(
      { error: "Failed to create post" },
      { status: 500 }
    )
  }
}
```

## 用户认证

### NextAuth.js配置

```typescript
// lib/auth.ts
import NextAuth from "next-auth"
import { PrismaAdapter } from "@next-auth/prisma-adapter"
import GoogleProvider from "next-auth/providers/google"
import GitHubProvider from "next-auth/providers/github"
import EmailProvider from "next-auth/providers/email"
import { prisma } from "./db"

export const authOptions = {
  adapter: PrismaAdapter(prisma),
  providers: [
    GoogleProvider({
      clientId: process.env.GOOGLE_CLIENT_ID!,
      clientSecret: process.env.GOOGLE_CLIENT_SECRET!,
    }),
    GitHubProvider({
      clientId: process.env.GITHUB_ID!,
      clientSecret: process.env.GITHUB_SECRET!,
    }),
    EmailProvider({
      server: {
        host: process.env.EMAIL_SERVER_HOST,
        port: process.env.EMAIL_SERVER_PORT,
        auth: {
          user: process.env.EMAIL_SERVER_USER,
          pass: process.env.EMAIL_SERVER_PASSWORD,
        },
      },
      from: process.env.EMAIL_FROM,
    }),
  ],
  callbacks: {
    session: async ({ session, token }) => {
      if (session?.user) {
        session.user.id = token.sub as string
      }
      return session
    },
    jwt: async ({ user, token }) => {
      if (user) {
        token.uid = user.id
      }
      return token
    },
  },
  session: {
    strategy: "jwt" as const,
  },
  pages: {
    signIn: "/auth/signin",
    signOut: "/auth/signout",
    error: "/auth/error",
  },
}

export default NextAuth(authOptions)
```

### 认证中间件

```typescript
// middleware.ts
import { withAuth } from "next-auth/middleware"
import { NextResponse } from "next/server"

export default withAuth(
  function middleware(req) {
    // Add custom middleware logic here
    const { pathname } = req.nextUrl
    const token = req.nextauth.token

    // Check if user is admin for admin routes
    if (pathname.startsWith("/admin") && token?.role !== "ADMIN") {
      return NextResponse.redirect(new URL("/unauthorized", req.url))
    }

    // Check if user is verified for certain routes
    if (pathname.startsWith("/dashboard") && !token?.emailVerified) {
      return NextResponse.redirect(new URL("/verify-email", req.url))
    }

    return NextResponse.next()
  },
  {
    callbacks: {
      authorized: ({ token }) => !!token,
    },
  }
)

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/admin/:path*",
    "/api/protected/:path*",
    "/create-post",
    "/edit/:path*",
  ],
}
```

## 性能优化

### 图片优化

```typescript
// components/optimized-image.tsx
"use client"

import Image from "next/image"
import { useState } from "react"

interface OptimizedImageProps {
  src: string
  alt: string
  width?: number
  height?: number
  className?: string
  priority?: boolean
  placeholder?: "blur" | "empty"
  blurDataURL?: string
}

export function OptimizedImage({
  src,
  alt,
  width,
  height,
  className,
  priority = false,
  placeholder = "blur",
  blurDataURL,
}: OptimizedImageProps) {
  const [isLoading, setLoading] = useState(true)
  const [error, setError] = useState(false)

  return (
    <div className={`relative overflow-hidden ${className || ""}`}>
      {isLoading && (
        <div className="absolute inset-0 bg-gray-200 animate-pulse" />
      )}

      {error ? (
        <div className="flex items-center justify-center h-full bg-gray-100 text-gray-400">
          <svg
            className="w-12 h-12"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            />
          </svg>
        </div>
      ) : (
        <Image
          src={src}
          alt={alt}
          width={width}
          height={height}
          className={`
            duration-700 ease-in-out
            ${isLoading ? "scale-110 blur-2xl grayscale" : "scale-100 blur-0 grayscale-0"}
          `}
          onLoadingComplete={() => setLoading(false)}
          onError={() => setError(true)}
          priority={priority}
          placeholder={placeholder}
          blurDataURL={blurDataURL}
          sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 33vw"
        />
      )}
    </div>
  )
}
```

### 缓存策略

```typescript
// lib/cache.ts
import { unstable_cache } from 'next/cache'

// 缓存文章数据
export const getCachedPost = unstable_cache(
  async (slug: string) => {
    const post = await prisma.post.findUnique({
      where: { slug },
      include: {
        author: {
          select: {
            id: true,
            name: true,
            username: true,
            avatar: true,
          },
        },
        tags: {
          include: {
            tag: true,
          },
        },
      },
    })

    return post
  },
  ['post'],
  {
    revalidate: 3600, // 1 hour
    tags: ['post'],
  }
)

// 缓存相关文章
export const getCachedRelatedPosts = unstable_cache(
  async (postId: string, tags: string[]) => {
    const relatedPosts = await prisma.post.findMany({
      where: {
        id: { not: postId },
        status: 'PUBLISHED',
        tags: {
          some: {
            tag: {
              name: {
                in: tags,
              },
            },
          },
        },
      },
      include: {
        author: {
          select: {
            id: true,
            name: true,
            username: true,
          },
        },
        tags: {
          include: {
            tag: true,
          },
        },
      },
      orderBy: [
        { views: 'desc' },
        { publishedAt: 'desc' },
      ],
      take: 3,
    })

    return relatedPosts
  },
  ['related-posts'],
  {
    revalidate: 1800, // 30 minutes
    tags: ['related-posts'],
  }
)

// 手动重新验证
export async function revalidatePostCache(slug: string) {
  const revalidateTag = require('next/cache').revalidateTag
  revalidateTag('post')
  revalidateTag('related-posts')
  revalidateTag(`post-${slug}`)
}
```

## SEO优化

### 结构化数据

```typescript
// components/structured-data.tsx
interface StructuredDataProps {
  type: "Article" | "Blog" | "BreadcrumbList" | "Person"
  data: any
}

export function StructuredData({ type, data }: StructuredDataProps) {
  const generateStructuredData = () => {
    switch (type) {
      case "Article":
        return {
          "@context": "https://schema.org",
          "@type": "Article",
          headline: data.title,
          description: data.excerpt,
          image: data.featuredImage,
          datePublished: data.publishedAt,
          dateModified: data.updatedAt,
          author: {
            "@type": "Person",
            name: data.author.name,
            url: `https://myblog.com/author/${data.author.username}`,
          },
          publisher: {
            "@type": "Organization",
            name: "My Blog",
            logo: {
              "@type": "ImageObject",
              url: "https://myblog.com/logo.png",
            },
          },
        }

      case "BreadcrumbList":
        return {
          "@context": "https://schema.org",
          "@type": "BreadcrumbList",
          itemListElement: data.items.map((item: any, index: number) => ({
            "@type": "ListItem",
            position: index + 1,
            name: item.name,
            item: item.url,
          })),
        }

      default:
        return null
    }
  }

  const structuredData = generateStructuredData()

  if (!structuredData) return null

  return (
    <script
      type="application/ld+json"
      dangerouslySetInnerHTML={{
        __html: JSON.stringify(structuredData),
      }}
    />
  )
}

// 使用示例
function BlogPost({ post }: { post: any }) {
  const breadcrumbData = {
    items: [
      { name: "Home", url: "https://myblog.com" },
      { name: "Blog", url: "https://myblog.com/blog" },
      { name: post.title, url: `https://myblog.com/blog/${post.slug}` },
    ],
  }

  return (
    <>
      <StructuredData type="Article" data={post} />
      <StructuredData type="BreadcrumbList" data={breadcrumbData} />
      {/* 文章内容 */}
    </>
  )
}
```

### sitemap生成

```typescript
// app/sitemap.ts
import { MetadataRoute } from 'next'
import { getAllPosts, getAllTags, getAllAuthors } from '@/lib/api'

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const baseUrl = 'https://myblog.com'

  // 获取所有内容
  const [posts, tags, authors] = await Promise.all([
    getAllPosts(),
    getAllTags(),
    getAllAuthors(),
  ])

  // 静态页面
  const staticPages = [
    { url: baseUrl, lastModified: new Date() },
    { url: `${baseUrl}/blog`, lastModified: new Date() },
    { url: `${baseUrl}/about`, lastModified: new Date() },
    { url: `${baseUrl}/contact`, lastModified: new Date() },
  ]

  // 博客文章
  const postSitemaps = posts.map((post) => ({
    url: `${baseUrl}/blog/${post.slug}`,
    lastModified: new Date(post.updatedAt),
    changeFrequency: 'weekly' as const,
    priority: 0.8,
  }))

  // 标签页面
  const tagSitemaps = tags.map((tag) => ({
    url: `${baseUrl}/tag/${tag.slug}`,
    lastModified: new Date(),
    changeFrequency: 'weekly' as const,
    priority: 0.6,
  }))

  // 作者页面
  const authorSitemaps = authors.map((author) => ({
    url: `${baseUrl}/author/${author.username}`,
    lastModified: new Date(),
    changeFrequency: 'monthly' as const,
    priority: 0.5,
  }))

  return [...staticPages, ...postSitemaps, ...tagSitemaps, ...authorSitemaps]
}
```

## 部署配置

### Vercel配置

```json
// vercel.json
{
  "builds": [
    {
      "src": "package.json",
      "use": "@vercel/next"
    }
  ],
  "routes": [
    {
      "src": "/sitemap.xml",
      "dest": "/sitemap.xml"
    },
    {
      "src": "/robots.txt",
      "dest": "/robots.txt"
    }
  ],
  "env": {
    "DATABASE_URL": "@database_url",
    "NEXTAUTH_URL": "@nextauth_url",
    "GOOGLE_CLIENT_ID": "@google_client_id",
    "GOOGLE_CLIENT_SECRET": "@google_client_secret",
    "GITHUB_ID": "@github_id",
    "GITHUB_SECRET": "@github_secret",
    "EMAIL_SERVER_HOST": "@email_server_host",
    "EMAIL_SERVER_PORT": "@email_server_port",
    "EMAIL_SERVER_USER": "@email_server_user",
    "EMAIL_SERVER_PASSWORD": "@email_server_password",
    "EMAIL_FROM": "@email_from",
    "NEXTAUTH_SECRET": "@nextauth_secret"
  },
  "crons": [
    {
      "path": "/api/cron/sitemap",
      "schedule": "0 0 * * *"
    },
    {
      "path": "/api/cron/analytics",
      "schedule": "0 */6 * * *"
    }
  ]
}
```

### Docker配置

```dockerfile
# Dockerfile
FROM node:18-alpine AS base

# Install dependencies only when needed
FROM base AS deps
RUN apk add --no-cache libc6-compat
WORKDIR /app

# Install dependencies based on the preferred package manager
COPY package.json pnpm-lock.yaml* ./
RUN \
  if [ -f pnpm-lock.yaml ]; then \
    corepack enable pnpm && pnpm i --frozen-lockfile; \
  elif [ -f package-lock.json ]; then \
    npm ci; \
  elif [ -f yarn.lock ]; then \
    corepack enable yarn && yarn install --frozen-lockfile; \
  else \
    echo "Lockfile not found." && exit 1; \
  fi

# Rebuild the source code only when needed
FROM base AS builder
WORKDIR /app
COPY --from=deps /app/node_modules ./node_modules
COPY . .

# Environment variable needed for build
ENV NEXT_TELEMETRY_DISABLED=1

RUN \
  if [ -f pnpm-lock.yaml ]; then \
    corepack enable pnpm && pnpm run build; \
  elif [ -f package-lock.json ]; then \
    npm run build; \
  elif [ -f yarn.lock ]; then \
    corepack enable yarn && yarn run build; \
  else \
    echo "Lockfile not found." && exit 1; \
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

## 总结与扩展

### 项目特点

1. **现代化技术栈**
   - Next.js 15 with App Router
   - TypeScript for type safety
   - Tailwind CSS for styling
   - Prisma ORM for database management

2. **完整的CMS功能**
   - 文章管理CRUD
   - 标签系统
   - 用户认证
   - 评论系统

3. **性能优化**
   - 图片优化
   - 缓存策略
   - 代码分割
   - 懒加载

4. **SEO友好**
   - 动态元数据
   - 结构化数据
   - Sitemap生成
   - 语义化HTML

### 扩展功能建议

1. **多语言支持**
   - 实现i18n
   - 动态路由本地化
   - 数据库多语言字段

2. **高级搜索**
   - 全文搜索引擎集成
   - 搜索建议
   - 搜索历史

3. **会员系统**
   - 订阅功能
   - 付费内容
   - 会员等级

4. **社交功能**
   - 用户关注
   - 点赞收藏
   - 社交分享

5. **数据分析**
   - 访问统计
   - 用户行为分析
   - 内容表现分析

### 部署选项

1. **Vercel** - 最简单的部署方式
2. **Docker** - 容器化部署
3. **AWS** - 云服务部署
4. **自托管** - 完全控制

---

通过这个博客平台项目，你已经掌握了Next.js 15的完整开发流程，从项目规划到部署上线。这个项目可以作为其他类似应用的基础模板，根据具体需求进行功能扩展和定制。记住持续优化性能，注重用户体验，并保持代码的可维护性。