# gRPC 服务开发完整指南

> **文档简介**: 掌握 gRPC 服务端与客户端开发全链路——proto 定义、代码生成、四种通信模式、拦截器与超时治理
>
> **目标读者**: 具备 Go 基础、了解 HTTP 服务开发的开发者
>
> **前置知识**: Go 语言基础（接口、并发）、Protocol Buffers 基本概念、[微服务设计](../advanced-topics/architecture/01-microservices-design.md)（建议先读）
>
> **预计时长**: 3 小时学习 + 2 小时实践

## 📚 文档元数据

| 属性 | 内容 |
|------|------|
| **模块** | `01-go-backend` |
| **分类** | `frameworks/rpc` |
| **难度** | ⭐⭐⭐ (精通) |
| **标签** | `#gRPC` `#Protobuf` `#RPC` `#微服务` |
| **更新日期** | `2026年9月` |
| **状态** | ✅ 已建设 |

## 🎯 学习目标

1. 理解 gRPC 的运行模型：HTTP/2 传输 + Protobuf 序列化 + 接口约定先行
2. 独立完成 proto 文件编写与 `protoc` 代码生成
3. 实现四种通信模式：一元调用、服务端流、客户端流、双向流
4. 使用拦截器实现横切关注点（日志、恢复、认证）
5. 正确处理超时、取消与错误传播

## 🧠 核心概念

gRPC 的三块基石：

- **Protobuf（接口契约）**：`.proto` 文件同时是 IDL（接口定义语言）与序列化格式。服务签名与消息结构先于实现确定，客户端/服务端各自根据同一份契约生成代码。
- **HTTP/2（传输层）**：单连接多路复用、头部压缩、双向流是协议原生能力，而非应用层模拟。
- **代码生成（类型安全）**：`protoc` 插件产出强类型的 client stub 与 server interface，方法名拼错、消息字段不匹配都是编译期错误。

与 REST 的定位差异：gRPC 适合**内部服务间通信**（性能、强契约、流式）；对外 API 仍以 REST/JSON 为主流（可读性、浏览器与通用客户端兼容）。

## 🛠️ 环境准备

安装 protoc 编译器与两个 Go 代码生成插件：

```bash
# protoc 本体（从 https://github.com/protocolbuffers/protobuf/releases 下载对应平台包）
protoc --version

# Go 生成插件
go install google.golang.org/protobuf/cmd/protoc-gen-go@latest
go install google.golang.org/grpc/cmd/protoc-gen-go-grpc@latest
```

新建项目并拉取运行时依赖：

```bash
go mod init example.com/userservice
go get google.golang.org/grpc
go get google.golang.org/protobuf
```

## 📝 第一步：编写 proto 文件

`proto/user.proto`——一个覆盖四种通信模式的服务定义：

```protobuf
syntax = "proto3";

package user.v1;

option go_package = "example.com/userservice/gen/userpb";

// 消息定义
message GetUserRequest {
  int64 id = 1;
}

message User {
  int64 id = 1;
  string name = 2;
  string email = 3;
}

message SearchRequest {
  string keyword = 1;
  int32 limit = 2;
}

message UploadSummary {
  int32 accepted = 1;
  int32 rejected = 2;
}

service UserService {
  // 一元调用：一个请求换一个响应
  rpc GetUser(GetUserRequest) returns (User);

  // 服务端流：一个请求，服务端持续返回多条
  rpc SearchUsers(SearchRequest) returns (stream User);

  // 客户端流：客户端持续发送，服务端最终汇总返回一次
  rpc ImportUsers(stream User) returns (UploadSummary);

  // 双向流：两边各自按需收发，彼此独立
  rpc SyncUsers(stream User) returns (stream User);
}
```

字段编号（`= 1`）是线上兼容性的关键：**一旦发布不可更改、不可复用**，只能新增。

## ⚙️ 第二步：代码生成

```bash
protoc --go_out=. --go_opt=paths=source_relative \
       --go-grpc_out=. --go-grpc_opt=paths=source_relative \
       proto/user.proto
```

产出两个文件：

- `gen/userpb/user.pb.go`：消息类型与序列化代码
- `gen/userpb/user_grpc.pb.go`：`UserServiceClient` 与 `UserServiceServer` 接口

生成目录建议纳入 CI 固定生成步骤，勿手改。

## 🖥️ 第三步：实现服务端

```go
package main

import (
    "context"
    "io"
    "log"
    "net"
    "strings"

    "google.golang.org/grpc"
    "google.golang.org/grpc/codes"
    "google.golang.org/grpc/status"

    pb "example.com/userservice/gen/userpb"
)

type userServer struct {
    // 必须内嵌：protoc 未来给 service 加方法时，服务端不至于编译失败
    pb.UnimplementedUserServiceServer
    users map[int64]*pb.User
}

// 一元调用
func (s *userServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.User, error) {
    u, ok := s.users[req.GetId()]
    if !ok {
        return nil, status.Error(codes.NotFound, "user not found")
    }
    return u, nil
}

// 服务端流：循环 Send，最后 return nil 结束流
func (s *userServer) SearchUsers(req *pb.SearchRequest, stream pb.UserService_SearchUsersServer) error {
    for _, u := range s.users {
        if strings.Contains(u.GetName(), req.GetKeyword()) {
            if err := stream.Send(u); err != nil {
                return err
            }
        }
    }
    return nil // return 即关闭流
}

// 客户端流：循环 Recv 直到 io.EOF，最后 SendAndClose
func (s *userServer) ImportUsers(stream pb.UserService_ImportUsersServer) error {
    summary := &pb.UploadSummary{}
    for {
        u, err := stream.Recv()
        if err == io.EOF {
            return stream.SendAndClose(summary)
        }
        if err != nil {
            return err
        }
        summary.Accepted++
        _ = u
    }
}

// 双向流：Recv 与 Send 独立循环
func (s *userServer) SyncUsers(stream pb.UserService_SyncUsersServer) error {
    for {
        u, err := stream.Recv()
        if err == io.EOF {
            return nil
        }
        if err != nil {
            return err
        }
        if err := stream.Send(u); err != nil {
            return err
        }
    }
}

func main() {
    lis, err := net.Listen("tcp", ":50051")
    if err != nil {
        log.Fatal(err)
    }
    srv := grpc.NewServer()
    pb.RegisterUserServiceServer(srv, &userServer{users: map[int64]*pb.User{}})
    log.Println("listening :50051")
    log.Fatal(srv.Serve(lis))
}
```

## 🔌 第四步：实现客户端

```go
package main

import (
    "context"
    "io"
    "log"
    "time"

    "google.golang.org/grpc"
    "google.golang.org/grpc/credentials/insecure"

    pb "example.com/userservice/gen/userpb"
)

func main() {
    // NewClient 建立的是"频道"而非物理连接：惰性连接，
    // 首次发起 RPC 时才真正拨号（这也是它取代 grpc.Dial 的原因）
    conn, err := grpc.NewClient(
        "localhost:50051",
        grpc.WithTransportCredentials(insecure.NewCredentials()),
    )
    if err != nil {
        log.Fatal(err)
    }
    defer conn.Close()

    client := pb.NewUserServiceClient(conn)

    // 每个调用都应带 deadline
    ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
    defer cancel()

    // 一元调用
    u, err := client.GetUser(ctx, &pb.GetUserRequest{Id: 1})
    if err != nil {
        log.Fatal(err)
    }
    log.Println(u.GetName())

    // 服务端流：Recv 循环消费
    stream, err := client.SearchUsers(ctx, &pb.SearchRequest{Keyword: "li", Limit: 10})
    if err != nil {
        log.Fatal(err)
    }
    for {
        u, err := stream.Recv()
        if err == io.EOF {
            break
        }
        if err != nil {
            log.Fatal(err)
        }
        log.Println("found:", u.GetName())
    }
}
```

## 🧩 拦截器：gRPC 版中间件

服务端一元拦截器等价于 Gin 中间件，用于日志、恢复、认证等横切逻辑：

```go
func loggingInterceptor(ctx context.Context, req any,
    info *grpc.UnaryServerInfo, handler grpc.UnaryHandler,
) (any, error) {
    start := time.Now()
    resp, err := handler(ctx, req) // 调用下一个处理器
    log.Printf("%s took %v err=%v", info.FullMethod, time.Since(start), err)
    return resp, err
}

srv := grpc.NewServer(
    grpc.ChainUnaryInterceptor(
        recoveryInterceptor,
        loggingInterceptor,
        authInterceptor,
    ),
)
```

关键点：`UnaryServerInterceptor` 签名中 `handler(ctx, req)` 是链上的下一个环节——不调用它即短路，调用前后包逻辑即"洋葱模型"。流式方法需要用 `StreamInterceptor`，签名不同，逻辑常需单独实现。

## ⏱️ 超时与取消传播

gRPC 的超时通过 context 跨服务传播：客户端设的 deadline 会随请求元数据传到服务端，服务端再传给它调用的下游服务——**超时预算全链路共享**。

```go
// 客户端：给整个调用 2 秒预算
ctx, cancel := context.WithTimeout(context.Background(), 2*time.Second)
defer cancel()
client.GetUser(ctx, req)

// 服务端：把 ctx 继续传给数据库/下游调用，超时才能层层生效
rows, err := db.QueryContext(ctx, "SELECT ...")
```

## ⚠️ 常见陷阱

- ❌ **错误做法**：继续使用 `grpc.Dial` 新建连接。
- ✅ **正确做法**：用 `grpc.NewClient`（官方已将 Dial 标记弃用）。两者本质差异：NewClient 不做同步拨号，语义是惰性频道。
- ❌ **错误做法**：以为 `NewClient` 返回错误代表连不上服务端——它几乎不会因网络失败而报错。
- ✅ **正确做法**：连接失败体现在后续 RPC 调用的 `err`（`Unavailable` 错误码）上，或在调用前显式调用 `conn.Connect()`。
- ❌ **错误做法**：服务端结构体直接实现接口而内嵌 `UnimplementedUserServiceServer` 报错就删掉它。
- ✅ **正确做法**：必须保留内嵌——这是向前兼容机制，未来 proto 加方法时旧服务端仍可编译。
- ❌ **错误做法**：调用 gRPC 不设 deadline。
- ✅ **正确做法**：每个出站调用都包 `context.WithTimeout`，否则故障会无限挂起调用方。
- ❌ **错误做法**：修改已发布字段的编号，或复用已删除字段的编号。
- ✅ **正确做法**：字段编号只增不改；删除字段时用 `reserved` 占住编号，防止未来误用。
- ❌ **错误做法**：用 `fmt.Errorf` 直接返回服务端错误。
- ✅ **正确做法**：用 `status.Error(codes.NotFound, ...)` 等标准错误码，客户端才能按 `status.Code(err)` 分支处理。

## 🗺️ 下一步

- [微服务设计](../advanced-topics/architecture/01-microservices-design.md)——gRPC 在服务治理体系中的位置
- [微服务演示项目](../projects/02-microservices-demo.md)——在实战项目中应用 gRPC
- [Kubernetes 部署](../deployment/03-kubernetes-deployment.md)——gRPC 服务的探针与负载均衡注意点（HTTP/2 长连接与 L4 负载均衡的配合）

---

*最后更新: 2026年9月*
