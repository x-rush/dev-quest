# 外部服务教学契约验证

**验证日期**：2026-09-20  
**范围**：`02-nextjs-frontend/projects/02-ecommerce-store.md` 与 `09-nodejs-backend/projects/03-file-storage-service.md` 新增的支付和对象存储 TypeScript 契约。  
**目的**：确认学习文档以应用端口表达出站依赖，不把某个支付或对象存储供应商、真实账号或密钥当作学习前置条件。

## 环境与命令

使用现有 Docker 的 `node:24-bookworm-slim` 镜像，在临时容器中安装 `typescript@5.9.3`，以严格模式检查从正文提取的 `PaymentGateway` 和 `ObjectStorage` 接口：

```bash
./node_modules/.bin/tsc --strict --noEmit --target ES2022 contracts.ts
```

结果：`PASS external-service teaching contracts type check`。

## 已验证的边界

- 支付创建请求带订单 ID、以最小货币单位表示的金额和幂等键；回调验证的结果带事件 ID、订单 ID 与受限事件类型。
- 对象存储端口把上传 URL、下载 URL 和删除操作表达为业务所需能力，不泄漏某一 SDK 的客户端对象。
- 两份正文明确：接口和伪代码不能拼成完整生产系统；实际接入还需要服务商适配器、凭据、权限、回调来源验证与沙箱验收。

## 不覆盖的内容

本检查不调用支付、对象存储、邮件或任何云服务，也不验证 webhook 加密签名、预签名 URL、网络重试或供应商 SDK 行为。那些内容在知识库中作为设计边界、失败情形与真实接入前的验收事项讲解，而不是本轮运行通过的结论。
