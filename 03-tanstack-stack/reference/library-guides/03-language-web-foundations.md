# TanStack 之前的标准能力：语言、Web API 与数据契约

前置：会编写变量、函数、数组和对象。目标：进入 Query、Router、Table、Form 前，能够解释数据转换、失败传播、参数解析和不可变更新。TanStack 是一组框架库，不存在“TanStack 语言关键词”或“TanStack 标准库”；它依赖的基础能力由 ECMAScript、TypeScript 和宿主平台分别提供。

## 1. 查阅时先确定谁提供这个能力

| 层级 | 典型能力 | 学习入口 | 不负责什么 |
|---|---|---|---|
| JavaScript 语言与内置对象 | const、async/await、Array、Map、Set、Promise、JSON | [关键词](../../../shared-resources/javascript-keywords.md)、[内置函数与方法](../../../shared-resources/javascript-builtins.md)、[核心语义](../../../02-nextjs-frontend/reference/language-concepts/09-js-core-semantics.md) | 不规定浏览器 DOM、请求 Cookie 或文件系统 |
| TypeScript 类型系统 | unknown、泛型、联合、Pick、Partial、Record | [TypeScript 模式](../language-concepts/05-typescript-patterns.md)、[类型收窄](../../../02-nextjs-frontend/reference/language-concepts/07-type-narrowing-guards.md) | 类型断言和接口不能在运行时验证服务器响应 |
| Web 标准 API | URL、URLSearchParams、fetch、AbortController、FormData | [Web 平台 API 与完整实验](../../../02-nextjs-frontend/reference/language-concepts/10-web-platform-apis.md) | 不替你定义业务缓存键、字段约束或用户权限 |
| React | 组件、state、effect、context | [React 语法](../../../02-nextjs-frontend/reference/language-concepts/01-react-syntax-cheatsheet.md) | 不自动把远程数据变成可失效缓存 |
| TanStack | Query 缓存、Router 路由、Table 行模型、Form 字段状态 | [Query 核心](../language-concepts/01-query-core-api.md)、[Router 核心](../language-concepts/03-router-core-api.md) | 不取代 HTTP 服务、数据库和服务端认证 |

先掌握 Array 的 map/filter/find、不可变更新、Promise 失败传播与 URL 参数，再学习 Query 的 select/queryFn/queryKey。这样能分辨“语言行为导致的问题”和“框架配置导致的问题”。

## 2. URL 输入需要解析规则，不能只加类型断言

URL 查询参数是文本，可能缺失、重复、含空格或超出范围。下面定义一个明确契约：page 缺失时取 1；仅接受 1 到 100 的十进制正整数，不接受 `2x`、`01`、`2.5` 和重复 page。tag 保留第一次出现的顺序并去重。

可运行示例，保存为 `search-input.mjs`，执行 `node search-input.mjs`。预期六行：`1:js,ts`、`3:js`、`invalid page`、`invalid page`、`invalid page`、`duplicate page`。

<!-- foundation-case: search-input -->
```js
function parseSearch(search) {
  const params = new URLSearchParams(search);
  const pages = params.getAll('page');
  if (pages.length > 1) throw new TypeError('duplicate page');
  const raw = pages[0] ?? '1';
  if (!/^[1-9]\d*$/.test(raw)) throw new TypeError('invalid page');
  const page = Number(raw);
  if (!Number.isSafeInteger(page) || page > 100) {
    throw new TypeError('invalid page');
  }
  const tags = [...new Set(params.getAll('tag').map((tag) => tag.trim()).filter(Boolean))];
  return { page, tags };
}
for (const input of [
  '?tag=js&tag=ts&tag=js', '?page=3&tag=js', '?page=2x',
  '?page=0', '?page=101', '?page=1&page=2',
]) {
  try {
    const { page, tags } = parseSearch(input);
    console.log(`${page}:${tags.join(',')}`);
  } catch (error) { console.log(error.message); }
}
```

`parseInt('2x', 10)` 得到 2，因此不适合验证整个文本符合页码格式。`Number('')` 得到 0，因此也必须先定义空输入含义。业务可以允许前导零或重复参数，但必须明确规则并测试；不能让断言 `as number` 掩盖未转换的字符串。

Router 的 validateSearch 接收的是路由器已经解析的搜索对象，不能把上述接收原始查询串的函数直接照搬进去。复用的是业务约束，适配的是输入形状；见 [搜索参数](../language-concepts/11-search-params.md)。

## 3. 修改缓存数据前先掌握不可变更新

复制外层数组后，内部对象仍可能与原数组共享。`const copied = [...items]; copied[0].title = 'new'` 会修改原对象；需要对被修改的那一层也创建新对象。相反，不变对象应尽量复用引用，避免无意义的全量深克隆。

可运行示例，保存为 `immutable-data.mjs`，执行 `node immutable-data.mjs`。预期五行：`false,true`、`false,true`、`true`、`true`、`true`。

<!-- foundation-case: immutable-data -->
```js
function toggle(items, id) {
  let changed = false;
  const next = items.map((item) => {
    if (item.id !== id) return item;
    changed = true;
    return { ...item, done: !item.done };
  });
  return changed ? next : items;
}
const original = [
  { id: 1, title: 'Read', done: false },
  { id: 2, title: 'Practice', done: false },
];
const next = toggle(original, 1);
console.log([original[0].done, next[0].done].join(','));
console.log([original === next, original[1] === next[1]].join(','));
console.log(toggle(original, 999) === original);
console.log(original[0] !== next[0]);
console.log(toggle([], 1).length === 0);
```

契约要求 id 唯一；如果后端允许重复 id，更新语义必须另行定义。Query 的 setQueryData updater 中可以使用同类纯函数；乐观更新还必须处理取消在途请求、回滚、服务器结果对账，这些不是一次 map 能解决的，见[乐观更新](../language-concepts/06-optimistic-update.md)。

## 4. queryFn 是 Promise 契约，失败不能伪装成空数组

[Query 函数官方说明](https://tanstack.com/query/v5/docs/framework/react/guides/query-functions)要求查询函数返回 Promise，成功产生数据，失败抛出错误或返回被拒绝的 Promise。fetch 在 HTTP 404/500 时仍可能成功返回 Response，因此 queryFn 必须检查业务认定的失败状态；成功返回 undefined 也不符合 Query 数据契约。

常见错误是 `catch { return [] }`：网络失败会被缓存为“成功的空列表”，UI 无法区分“尚无任务”和“服务器不可用”。应该保留失败，让错误界面与重试策略处理。HTTP 状态成功后还需解析 JSON 并校验字段；`fetch(...).then(r => r.json()) as Promise<Task[]>` 没有增加任何运行时保护。

取消时把 Query 提供的 signal 传递给请求层。Promise.all 不自动取消已经发出的其他请求；页面不再需要结果也不证明服务器撤销了写操作。学习请求契约可直接运行 Web API 参考中的 `response-contract.mjs`，再接入 [Query 框架要点](../framework-essentials/01-query-essentials.md)。

## 5. 必须掌握的基础能力索引

| 具体任务 | 优先查阅 | 需要解释的边界 |
|---|---|---|
| 清洗列表、提取列、判断存在 | Array.map/filter/find/some/every | 空数组行为、是否修改原数组、对象引用是否共享 |
| 计数、分组、去重 | Map、Set、reduce | 对象按身份比较；空 reduce 需要初始值 |
| 收集并发结果 | Promise.all/allSettled | 结果顺序与完成顺序不同；失败不会自动撤销其他请求 |
| 加载取消与超时 | AbortController、AbortSignal | 谁持有 controller、signal 是否已取消、写操作是否仍可能生效 |
| 参数构造与解析 | URL、URLSearchParams | 编码、重复键、缺失值、数字转换规则 |
| 表单字段和文件 | FormData、File、Blob | get 返回值可能为字符串、File 或 null；上传边界交给请求实现 |
| JSON 数据进入业务层 | JSON.parse + 类型收窄/Schema | JSON 合法不等于结构合法；TS 类型不执行验证 |
| 复制快照 | 对象展开、structuredClone | 浅复制与支持类型；不能复制函数和任意类行为 |

详细方法签名与输出边界以[共享内置参考](../../../shared-resources/javascript-builtins.md)为统一入口；标准原始目录见 [ECMAScript 全局对象](https://tc39.es/ecma262/multipage/global-object.html)，宿主行为见 [Fetch](https://fetch.spec.whatwg.org/) 与 [URL](https://url.spec.whatwg.org/) 标准。

## 练习与验收

按“解析搜索参数 → 生成请求 → 校验响应 → 不可变更新列表”的顺序做一个任务列表。先使用本文纯函数和本地 Response，再接入 Query。要求覆盖无 page、重复 page、空列表、HTTP 500、结构错误、切换筛选、更新不存在 id 七种输入。

验收：每个失败能定位到输入、传输、解析或更新层；错误不能显示成成功空列表；原列表不被修改；筛选条件变化后 queryKey 同步变化；旧请求不会覆盖新筛选结果。最后能说明哪些代码属于标准能力、哪些依赖 TanStack。

<!-- learning-navigation -->
## 阅读导航

[本模块理解地图](../../LEARNING_GUIDE.md) · [完整目录与版本](../../README.md) · [相关库选择](02-related-libs.md)
