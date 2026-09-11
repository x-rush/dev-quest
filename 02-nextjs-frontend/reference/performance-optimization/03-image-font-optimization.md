# 图片与字体优化（next/image / next/font）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（无难度门槛）
> **分类**: `performance-optimization`

## 📌 定义

`next/image` 是内置的图片组件：自动生成响应式 `srcset`、按需转换现代格式（AVIF/WebP）、懒加载与占位（placeholder）、防止布局偏移（强制 width/height 或 fill）。`next/font` 是内置的字体加载方案：构建期自托管 Google 字体或本地字体文件，自动预加载与 `font-display` 调优，消除字体请求阻塞与布局偏移。二者是 Core Web Vitals（LCP/CLS）优化的第一梯队工具。`next/legacy/image` 已弃用，新代码一律使用 `next/image`。

## 📖 语法/签名

```tsx
import Image from 'next/image';

// 本地图片：自动推导宽高
import hero from '@/public/hero.png';

export function Hero() {
  return (
    <Image
      src={hero}
      alt="首页主图"
      placeholder="blur"   // 本地图可用 blur 占位
      priority             // LCP 图片标记为高优先级预加载
    />
  );
}

// 远程图片：必须先在配置中登记域名
<Image src="https://cdn.example.com/photo.jpg" alt="照片" width={800} height={600} />
```

```typescript
// next.config.ts —— 远程图片与默认值（Next.js 16 语义）
const nextConfig = {
  images: {
    remotePatterns: [
      { protocol: 'https', hostname: 'cdn.example.com' },
    ],
    // images.domains 已弃用，改用 remotePatterns
    minimumCacheTTL: 14400,  // 默认已提升至 4 小时
    qualities: [75],         // 默认仅 [75]，其他质量需显式声明
    imageSizes: [32, 48, 64, 96, 128, 256, 384], // 默认值已移除 16
  },
};
```

```tsx
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], display: 'swap' });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <body className={inter.className}>{children}</body>;
}
```

## 💡 示例

```tsx
// 响应式填充容器 + sizes 提示
<div className="relative aspect-video">
  <Image
    src="/cover.jpg"
    alt="文章封面"
    fill
    sizes="(max-width: 768px) 100vw, 50vw"
    className="object-cover"
  />
</div>
```

```tsx
// 本地字体 + CSS 变量
import localFont from 'next/font/local';

const myFont = localFont({ src: './fonts/MyFont.woff2', variable: '--font-main' });

// 用法：<div className={myFont.variable}>…</div>，配合 tailwind font-family: var(--font-main)
```

## ⚠️ 常见陷阱

- 远程图片域名必须配置 `images.remotePatterns`；本地 src 带查询串还需 `images.localPatterns`（防路径枚举），否则直接报错
- `quality` 传入不在 `qualities` 列表中的值会被强制收敛到最近合法值（Next.js 16 默认仅 75）
- 给非 LCP 图片加 `priority` 会挤占带宽；只给首屏最大内容元素加
- `fill` 模式下父元素必须有 `position: relative/absolute` 与确定尺寸，否则图片塌陷
- 使用 `<img>` 代替 `next/image` 会失去自动优化并触发 lint 警告（`@next/next/no-img-element`）
- `next/font` 在构建期下载字体，CI 无外网或被墙时会构建失败；可改用 `next/font/local` 自托管

## 🔗 相关条目

- [打包优化](./02-bundle-optimization.md)
- [渲染优化](./01-rendering-optimization.md)
- [Core Web Vitals 优化](../../advanced-topics/performance/01-core-web-vitals.md)
