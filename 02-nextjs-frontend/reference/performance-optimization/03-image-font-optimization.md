# 图片与字体优化（next/image / next/font）

> **模块**: `02-nextjs-frontend`
> **类型**: 字典条目（可独立查阅，按主题准备前置知识）
> **分类**: `performance-optimization`

## 📌 定义

`next/image` 是内置的图片组件：自动生成响应式 `srcset`、按需转换现代格式（AVIF/WebP）、懒加载与占位（placeholder）、防止布局偏移（强制 width/height 或 fill）。`next/font` 是内置的字体加载方案：构建期自托管 Google 字体或本地字体文件，自动预加载与 `font-display` 调优，减少外部字体请求并缓解字体切换造成的布局偏移。二者是 Core Web Vitals（LCP/CLS）优化的第一梯队工具。`next/legacy/image` 已弃用，新代码一律使用 `next/image`。

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
      preload              // 已确认是首屏主要图片时才预加载
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
export default nextConfig;
```

```tsx
import { Inter } from 'next/font/google';

const inter = Inter({ subsets: ['latin'], display: 'swap' });

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return <html lang="zh-CN"><body className={inter.className}>{children}</body></html>;
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

- 远程图片需匹配 `images.remotePatterns`；如配置了 `localPatterns`，本地路径及查询串必须符合规则。不能笼统断言所有本地查询串都必须另配规则
- `quality` 传入不在 `qualities` 列表中的值会被强制收敛到最近合法值（Next.js 16 默认仅 75）
- Next.js 16 的 `priority` 已弃用，使用 `preload` 明确预加载意图；避免给大量图片同时预加载
- `fill` 模式下父元素必须有 `position: relative/absolute` 与确定尺寸，否则图片塌陷
- 使用 `<img>` 代替 `next/image` 会失去自动优化并触发 lint 警告（`@next/next/no-img-element`）
- `next/font` 在构建期下载字体，CI 无外网或被墙时会构建失败；可改用 `next/font/local` 自托管

<!-- full-library-explanation -->
## 从布局尺寸理解浏览器选择

width/height 提供固有比例；CSS 决定渲染尺寸；sizes 描述不同视口下预计显示宽度；srcset 提供候选资源。四者不是同一个概念。例如图片实际只占半屏却写 100vw，浏览器可能下载不必要的大图。

本页 fill 示例依赖 Tailwind 工具类。若项目未配置 Tailwind，改用明确 CSS：父容器 `position: relative; aspect-ratio: 16 / 9`，图片 `object-fit: cover`。fill 的绝对定位不会替父容器自动撑开高度。

字体 variable 只把 CSS 变量放入作用域，仍需通过 font-family 使用变量。next/font/google 在构建时获取字体，而 next/font/local 读取仓库内文件；两者都不意味着浏览器完全不用下载字体文件。

**练习：** 给同一张图分别设置符合布局与过大的 sizes，在相同设备像素比下查看 currentSrc 和网络传输大小。再关掉网络重载，区分磁盘缓存命中与新下载。验收不是截图“看起来一样”，而是解释为什么浏览器选中了那个资源。

**自测：** 有宽高属性就一定没有布局偏移吗？不一定，其他内容和 CSS 仍可能移动。预加载更多图必然更快吗？不一定，会争抢带宽。参考 [Image](https://nextjs.org/docs/app/api-reference/components/image) 与 [Font](https://nextjs.org/docs/app/api-reference/components/font)。

## 🔗 相关条目

- [打包优化](./02-bundle-optimization.md)
- [渲染优化](./01-rendering-optimization.md)
- [Core Web Vitals 优化](../../advanced-topics/performance/01-core-web-vitals.md)


<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [通用术语](../../../shared-resources/glossary.md)
