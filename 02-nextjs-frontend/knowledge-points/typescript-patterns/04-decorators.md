# TypeScript 装饰器使用速查手册

## 📚 概述

装饰器是 TypeScript 的一个实验性特性，提供了在不修改原始代码结构的情况下添加额外功能的能力。本指南涵盖了装饰器的各种类型、使用方法和实际应用场景。

## ⚙️ 启用装饰器

### 配置 TypeScript
**在项目中启用装饰器支持**

```typescript
// tsconfig.json
{
  "compilerOptions": {
    "experimentalDecorators": true,
    "emitDecoratorMetadata": true,
    "target": "ES2017",
    "lib": ["ES2017", "DOM"]
  }
}

// next.config.js (Next.js 项目)
/** @type {import('next').NextConfig} */
const nextConfig = {
  experimental: {
    // 如果使用 SWC，确保装饰器支持
  },
  // 如果使用 Babel，需要配置
  babelConfig: {
    presets: ['next/babel'],
    plugins: [
      ['@babel/plugin-proposal-decorators', { legacy: true }],
      ['@babel/plugin-proposal-class-properties', { loose: true }],
    ],
  },
};

module.exports = nextConfig;
```

### Babel 配置
**使用 Babel 处理装饰器**

```json
// .babelrc
{
  "presets": ["next/babel"],
  "plugins": [
    ["@babel/plugin-proposal-decorators", { "legacy": true }],
    ["@babel/plugin-proposal-class-properties", { "loose": true }]
  ]
}

// 或者在 package.json 中
{
  "babel": {
    "presets": ["next/babel"],
    "plugins": [
      ["@babel/plugin-proposal-decorators", { "legacy": true }],
      ["@babel/plugin-proposal-class-properties", { "loose": true }]
    ]
  }
}
```

## 🏷️ 类装饰器

### 基础类装饰器
**修改类的行为**

```typescript
// 基础类装饰器
function sealed<T extends { new (...args: any[]): {} }>(constructor: T) {
  return class extends constructor {
    constructor(...args: any[]) {
      super(...args);
      console.log('Creating sealed instance');
    }
  };
}

@sealed
class User {
  constructor(public name: string) {}
}

// 使用示例
const user = new User('John'); // 输出: Creating sealed instance

// 实际应用：添加元数据
function entity(tableName: string) {
  return function <T extends { new (...args: any[]): {} }>(constructor: T) {
    return class extends constructor {
      static tableName = tableName;
      constructor(...args: any[]) {
        super(...args);
        console.log(`Entity for table: ${tableName}`);
      }
    };
  };
}

@entity('users')
class UserEntity {
  constructor(
    public id: number,
    public name: string,
    public email: string
  ) {}
}

console.log(UserEntity.tableName); // 'users'
```

### 类增强装饰器
**为类添加方法和属性**

```typescript
// 添加时间戳装饰器
function timestamped<T extends { new (...args: any[]): {} }>(constructor: T) {
  return class extends constructor {
    createdAt: Date;
    updatedAt: Date;

    constructor(...args: any[]) {
      super(...args);
      this.createdAt = new Date();
      this.updatedAt = new Date();
    }

    updateTimestamp() {
      this.updatedAt = new Date();
    }
  };
}

@timestamped
class Document {
  constructor(public content: string) {}
}

const doc = new Document('Hello World');
console.log(doc.createdAt); // 当前时间
doc.updateTimestamp();
console.log(doc.updatedAt); // 更新后的时间

// 实际应用：API 模型装饰器
function apiModel(baseUrl: string) {
  return function <T extends { new (...args: any[]): {} }>(constructor: T) {
    return class extends constructor {
      static baseUrl = baseUrl;

      static async find(id: string | number) {
        const response = await fetch(`${baseUrl}/${id}`);
        return response.json();
      }

      static async findAll() {
        const response = await fetch(baseUrl);
        return response.json();
      }

      async save() {
        const method = (this as any).id ? 'PUT' : 'POST';
        const url = (this as any).id ? `${baseUrl}/${(this as any).id}` : baseUrl;
        const response = await fetch(url, {
          method,
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(this),
        });
        return response.json();
      }
    };
  };
}

@apiModel('https://api.example.com/users')
class User {
  constructor(
    public id?: number,
    public name?: string,
    public email?: string
  ) {}
}

// 使用示例
async function fetchUsers() {
  const users = await User.findAll();
  const user = await User.find(1);

  const newUser = new User(undefined, 'John', 'john@example.com');
  await newUser.save();
}
```

## 🎯 方法装饰器

### 基础方法装饰器
**修改方法行为**

```typescript
// 基础方法装饰器定义
function log(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = function (...args: any[]) {
    console.log(`Calling ${propertyKey} with args:`, args);
    const result = originalMethod.apply(this, args);
    console.log(`${propertyKey} returned:`, result);
    return result;
  };

  return descriptor;
}

class Calculator {
  @log
  add(a: number, b: number): number {
    return a + b;
  }

  @log
  multiply(a: number, b: number): number {
    return a * b;
  }
}

const calc = new Calculator();
calc.add(2, 3); // 输出: Calling add with args: [2, 3], add returned: 5
```

### 性能监控装饰器
**监控方法执行时间**

```typescript
function performance(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = async function (...args: any[]) {
    const start = performance.now();
    try {
      const result = await originalMethod.apply(this, args);
      const end = performance.now();
      console.log(`${propertyKey} took ${(end - start).toFixed(2)}ms`);
      return result;
    } catch (error) {
      const end = performance.now();
      console.log(`${propertyKey} failed after ${(end - start).toFixed(2)}ms`);
      throw error;
    }
  };

  return descriptor;
}

class DataService {
  @performance
  async fetchUsers(): Promise<User[]> {
    // 模拟 API 调用
    await new Promise(resolve => setTimeout(resolve, 1000));
    return [];
  }

  @performance
  async saveUser(user: User): Promise<User> {
    // 模拟保存操作
    await new Promise(resolve => setTimeout(resolve, 500));
    return user;
  }
}
```

### 缓存装饰器
**缓存方法结果**

```typescript
function cache(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  const cache = new Map<string, any>();

  descriptor.value = function (...args: any[]) {
    const key = JSON.stringify(args);

    if (cache.has(key)) {
      console.log(`Cache hit for ${propertyKey}`);
      return cache.get(key);
    }

    console.log(`Cache miss for ${propertyKey}`);
    const result = originalMethod.apply(this, args);
    cache.set(key, result);
    return result;
  };

  return descriptor;
}

class MathService {
  @cache
  fibonacci(n: number): number {
    if (n <= 1) return n;
    return this.fibonacci(n - 1) + this.fibonacci(n - 2);
  }

  @cache
  expensiveCalculation(x: number, y: number): number {
    console.log('Performing expensive calculation...');
    return Math.pow(x, y) * Math.sqrt(x + y);
  }
}

const mathService = new MathService();
mathService.expensiveCalculation(2, 8); // 执行计算
mathService.expensiveCalculation(2, 8); // 从缓存返回
```

### 重试装饰器
**自动重试失败的方法**

```typescript
function retry(attempts: number = 3, delay: number = 1000) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = async function (...args: any[]) {
      let lastError: Error;

      for (let i = 0; i < attempts; i++) {
        try {
          return await originalMethod.apply(this, args);
        } catch (error) {
          lastError = error as Error;
          if (i < attempts - 1) {
            console.log(`Attempt ${i + 1} failed for ${propertyKey}, retrying in ${delay}ms...`);
            await new Promise(resolve => setTimeout(resolve, delay));
          }
        }
      }

      console.error(`All ${attempts} attempts failed for ${propertyKey}`);
      throw lastError!;
    };

    return descriptor;
  };
}

class ApiService {
  @retry(3, 1000)
  async fetchUserData(userId: string): Promise<User> {
    const response = await fetch(`/api/users/${userId}`);
    if (!response.ok) {
      throw new Error(`Failed to fetch user: ${response.statusText}`);
    }
    return response.json();
  }

  @retry(5, 2000)
  async sendEmail(to: string, subject: string, body: string): Promise<void> {
    const response = await fetch('/api/send-email', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ to, subject, body }),
    });
    if (!response.ok) {
      throw new Error(`Failed to send email: ${response.statusText}`);
    }
  }
}
```

## 🔧 属性装饰器

### 基础属性装饰器
**修改属性行为**

```typescript
// 基础属性装饰器
function required(target: any, propertyKey: string) {
  let value: any;

  const getter = () => value;
  const setter = (newValue: any) => {
    if (newValue === undefined || newValue === null) {
      throw new Error(`${propertyKey} is required`);
    }
    value = newValue;
  };

  Object.defineProperty(target, propertyKey, {
    get: getter,
    set: setter,
    enumerable: true,
    configurable: true,
  });
}

class User {
  @required
  name: string = '';

  @required
  email: string = '';

  constructor(name: string, email: string) {
    this.name = name;
    this.email = email;
  }
}

const user = new User('John', 'john@example.com');
// user.name = undefined; // 抛出错误: name is required
```

### 验证装饰器
**为属性添加验证规则**

```typescript
function validate(validator: (value: any) => boolean, errorMessage: string) {
  return function (target: any, propertyKey: string) {
    let value: any;

    const getter = () => value;
    const setter = (newValue: any) => {
      if (!validator(newValue)) {
        throw new Error(`${propertyKey}: ${errorMessage}`);
      }
      value = newValue;
    };

    Object.defineProperty(target, propertyKey, {
      get: getter,
      set: setter,
      enumerable: true,
      configurable: true,
    });
  };
}

// 常用验证器
const validators = {
  email: (value: string) => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(value),
  minLength: (min: number) => (value: string) => value.length >= min,
  maxLength: (max: number) => (value: string) => value.length <= max,
  range: (min: number, max: number) => (value: number) => value >= min && value <= max,
  positive: (value: number) => value > 0,
  nonEmpty: (value: string) => value.trim().length > 0,
};

class UserProfile {
  @validate(validators.email, 'Invalid email format')
  email: string = '';

  @validate(validators.minLength(2), 'Name must be at least 2 characters')
  name: string = '';

  @validate(validators.range(18, 120), 'Age must be between 18 and 120')
  age: number = 18;

  @validate(validators.nonEmpty, 'Password cannot be empty')
  password: string = '';

  constructor(email: string, name: string, age: number, password: string) {
    this.email = email;
    this.name = name;
    this.age = age;
    this.password = password;
  }
}

// 使用示例
try {
  const profile = new UserProfile('invalid-email', 'A', 15, '');
} catch (error) {
  console.error(error.message); // 显示验证错误信息
}
```

### 序列化装饰器
**控制属性的序列化行为**

```typescript
function serializable(target: any, propertyKey: string) {
  // 标记属性为可序列化
  if (!target.constructor._serializable) {
    target.constructor._serializable = new Set<string>();
  }
  target.constructor._serializable.add(propertyKey);
}

function exclude(target: any, propertyKey: string) {
  // 标记属性为排除序列化
  if (!target.constructor._excluded) {
    target.constructor._excluded = new Set<string>();
  }
  target.constructor._excluded.add(propertyKey);
}

function transform(transformer: (value: any) => any) {
  return function (target: any, propertyKey: string) {
    if (!target.constructor._transformers) {
      target.constructor._transformers = new Map<string, (value: any) => any>();
    }
    target.constructor._transformers.set(propertyKey, transformer);
  };
}

class UserModel {
  @serializable
  id: number = 0;

  @serializable
  @transform((value: string) => value.toUpperCase())
  name: string = '';

  @serializable
  email: string = '';

  @exclude
  password: string = '';

  @serializable
  @transform((value: Date) => value.toISOString())
  createdAt: Date = new Date();

  toJSON() {
    const result: any = {};

    // 获取所有可序列化属性
    const serializable = (this.constructor as any)._serializable || new Set();
    const excluded = (this.constructor as any)._excluded || new Set();
    const transformers = (this.constructor as any)._transformers || new Map();

    Object.keys(this).forEach(key => {
      if (serializable.has(key) && !excluded.has(key)) {
        let value = (this as any)[key];

        // 应用转换器
        if (transformers.has(key)) {
          value = transformers.get(key)(value);
        }

        result[key] = value;
      }
    });

    return result;
  }
}

// 使用示例
const user = new UserModel();
user.id = 1;
user.name = 'John';
user.email = 'john@example.com';
user.password = 'secret123';
user.createdAt = new Date();

const json = JSON.stringify(user);
console.log(json);
// 输出: {"id":1,"name":"JOHN","email":"john@example.com","createdAt":"2025-01-01T00:00:00.000Z"}
```

## 🔄 参数装饰器

### 基础参数装饰器
**修改方法参数的行为**

```typescript
// 基础参数装饰器
function logParameter(target: any, methodName: string, parameterIndex: number) {
  const key = `${methodName}_parameters`;
  if (!target[key]) {
    target[key] = [];
  }
  target[key][parameterIndex] = true;
}

function validateParameters(target: any, methodName: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  const key = `${methodName}_parameters`;
  const loggedParams = target[key] || [];

  descriptor.value = function (...args: any[]) {
    loggedParams.forEach((shouldLog: boolean, index: number) => {
      if (shouldLog) {
        console.log(`Parameter ${index} of ${methodName}:`, args[index]);
      }
    });
    return originalMethod.apply(this, args);
  };

  return descriptor;
}

class ExampleService {
  @validateParameters
  greet(@logParameter name: string, @logParameter age: number): string {
    return `Hello ${name}, you are ${age} years old`;
  }
}

const service = new ExampleService();
service.greet('John', 25);
// 输出:
// Parameter 0 of greet: John
// Parameter 1 of greet: 25
```

### 类型转换装饰器
**自动转换参数类型**

```typescript
// 类型转换装饰器
function convert(converter: (value: any) => any) {
  return function (target: any, methodName: string, parameterIndex: number) {
    const key = `${methodName}_converters`;
    if (!target[key]) {
      target[key] = [];
    }
    target[key][parameterIndex] = converter;
  };
}

function applyConversions(target: any, methodName: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  const key = `${methodName}_converters`;
  const converters = target[key] || [];

  descriptor.value = function (...args: any[]) {
    const convertedArgs = args.map((arg, index) => {
      const converter = converters[index];
      return converter ? converter(arg) : arg;
    });
    return originalMethod.apply(this, convertedArgs);
  };

  return descriptor;
}

// 常用转换器
const converters = {
  toNumber: (value: any) => {
    const num = Number(value);
    if (isNaN(num)) {
      throw new Error(`Cannot convert ${value} to number`);
    }
    return num;
  },
  toInt: (value: any) => Math.floor(converters.toNumber(value)),
  toString: (value: any) => String(value),
  toDate: (value: any) => {
    const date = new Date(value);
    if (isNaN(date.getTime())) {
      throw new Error(`Cannot convert ${value} to Date`);
    }
    return date;
  },
  toBoolean: (value: any) => Boolean(value),
};

class DataProcessor {
  @applyConversions
  processData(
    @convert(converters.toInt) id: any,
    @convert(converters.toString) name: any,
    @convert(converters.toDate) createdAt: any
  ): void {
    console.log('Processed data:', { id, name, createdAt });
    console.log('Types:', {
      id: typeof id,
      name: typeof name,
      createdAt: createdAt instanceof Date
    });
  }
}

const processor = new DataProcessor();
processor.processData('123', 456, '2025-01-01');
// 输出:
// Processed data: { id: 123, name: '456', createdAt: 2025-01-01T00:00:00.000Z }
// Types: { id: 'number', name: 'string', createdAt: true }
```

## 🎨 实际应用场景

### API 控制器装饰器
**构建 REST API 控制器**

```typescript
// HTTP 方法装饰器
function Get(path: string) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    if (!target.constructor.routes) {
      target.constructor.routes = [];
    }
    target.constructor.routes.push({
      method: 'GET',
      path,
      handler: descriptor.value,
    });
  };
}

function Post(path: string) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    if (!target.constructor.routes) {
      target.constructor.routes = [];
    }
    target.constructor.routes.push({
      method: 'POST',
      path,
      handler: descriptor.value,
    });
  };
}

// 路由参数装饰器
function Param(paramName: string) {
  return function (target: any, methodName: string, parameterIndex: number) {
    const key = `${methodName}_params`;
    if (!target[key]) {
      target[key] = [];
    }
    target[key][parameterIndex] = paramName;
  };
}

function Body(target: any, methodName: string, parameterIndex: number) {
  const key = `${methodName}_body`;
  target[key] = parameterIndex;
}

// 控制器基类装饰器
function Controller(basePath: string) {
  return function <T extends { new (...args: any[]): {} }>(constructor: T) {
    return class extends constructor {
      static basePath = basePath;
      static routes = [];
    };
  };
}

// 使用示例
@Controller('/api/users')
class UserController {
  @Get('/')
  async getUsers(): Promise<User[]> {
    // 获取所有用户
    return [];
  }

  @Get('/:id')
  async getUser(@Param('id') id: string): Promise<User> {
    // 获取单个用户
    return {} as User;
  }

  @Post('/')
  async createUser(@Body userData: CreateUserRequest): Promise<User> {
    // 创建用户
    return {} as User;
  }
}

// 路由处理器
function registerControllers(controllers: any[]) {
  controllers.forEach(Controller => {
    const routes = Controller.routes || [];
    const basePath = Controller.basePath || '';

    routes.forEach((route: any) => {
      const fullPath = `${basePath}${route.path}`;
      console.log(`Registering ${route.method} ${fullPath}`);
      // 这里可以注册到 Express、Fastify 等框架
    });
  });
}

registerControllers([UserController]);
```

### 依赖注入装饰器
**实现依赖注入系统**

```typescript
// 依赖注入容器
class DIContainer {
  private services = new Map<string, any>();
  private factories = new Map<string, () => any>();

  register<T>(token: string, factory: () => T): void {
    this.factories.set(token, factory);
  }

  get<T>(token: string): T {
    if (this.services.has(token)) {
      return this.services.get(token);
    }

    const factory = this.factories.get(token);
    if (!factory) {
      throw new Error(`Service ${token} not found`);
    }

    const instance = factory();
    this.services.set(token, instance);
    return instance;
  }
}

const container = new DIContainer();

// 注入装饰器
function Injectable(token: string) {
  return function <T extends { new (...args: any[]): {} }>(constructor: T) {
    return class extends constructor {
      constructor(...args: any[]) {
        const dependencies = (constructor as any).dependencies || [];
        const resolvedDependencies = dependencies.map((dep: string) => container.get(dep));
        super(...resolvedDependencies, ...args);
      }
    };
  };
}

function Inject(token: string) {
  return function (target: any, propertyKey: string | symbol | undefined, parameterIndex: number) {
    if (!target.constructor.dependencies) {
      target.constructor.dependencies = [];
    }
    target.constructor.dependencies[parameterIndex] = token;
  };
}

// 服务定义
interface ILogger {
  log(message: string): void;
  error(error: Error): void;
}

interface IDatabase {
  query(sql: string): Promise<any[]>;
}

class ConsoleLogger implements ILogger {
  log(message: string) {
    console.log(`[LOG] ${message}`);
  }

  error(error: Error) {
    console.error(`[ERROR] ${error.message}`);
  }
}

class PostgreSQLDatabase implements IDatabase {
  async query(sql: string): Promise<any[]> {
    console.log(`Executing SQL: ${sql}`);
    return [];
  }
}

// 注册服务
container.register('ILogger', () => new ConsoleLogger());
container.register('IDatabase', () => new PostgreSQLDatabase());

// 使用依赖注入
@Injectable('UserService')
class UserService {
  constructor(
    @Inject('ILogger') private logger: ILogger,
    @Inject('IDatabase') private database: IDatabase
  ) {}

  async getUsers(): Promise<User[]> {
    this.logger.log('Fetching users from database');
    return this.database.query('SELECT * FROM users');
  }

  async createUser(userData: CreateUserRequest): Promise<User> {
    this.logger.log('Creating new user');
    // 实现创建用户逻辑
    return {} as User;
  }
}

// 使用服务
const userService = container.get<UserService>('UserService');
userService.getUsers();
```

### 权限控制装饰器
**实现方法级别的权限控制**

```typescript
// 权限装饰器
function hasRole(role: string) {
  return function (target: any, propertyKey: string, descriptor: PropertyDescriptor) {
    const originalMethod = descriptor.value;

    descriptor.value = function (...args: any[]) {
      const currentUser = (this as any).currentUser;

      if (!currentUser) {
        throw new Error('User not authenticated');
      }

      if (!currentUser.roles.includes(role)) {
        throw new Error(`Access denied. Required role: ${role}`);
      }

      return originalMethod.apply(this, args);
    };

    return descriptor;
  };
}

function requiresAuth(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = function (...args: any[]) {
    const currentUser = (this as any).currentUser;

    if (!currentUser) {
      throw new Error('Authentication required');
    }

    return originalMethod.apply(this, args);
  };

  return descriptor;
}

// 权限检查服务
interface User {
  id: string;
  name: string;
  roles: string[];
}

class AdminService {
  private currentUser: User | null = null;

  setCurrentUser(user: User | null) {
    this.currentUser = user;
  }

  @requiresAuth
  getUserProfile(): User | null {
    return this.currentUser;
  }

  @hasRole('admin')
  deleteAllUsers(): void {
    console.log('Deleting all users...');
  }

  @hasRole('moderator')
  moderateContent(): void {
    console.log('Moderating content...');
  }
}

// 使用示例
const adminService = new AdminService();

try {
  adminService.getUserProfile(); // 抛出错误: Authentication required

  const normalUser: User = { id: '1', name: 'John', roles: ['user'] };
  adminService.setCurrentUser(normalUser);

  adminService.getUserProfile(); // 正常执行
  adminService.moderateContent(); // 抛出错误: Access denied

  const adminUser: User = { id: '2', name: 'Admin', roles: ['admin', 'moderator'] };
  adminService.setCurrentUser(adminUser);

  adminService.deleteAllUsers(); // 正常执行
  adminService.moderateContent(); // 正常执行
} catch (error) {
  console.error(error.message);
}
```

## 📋 最佳实践

### 装饰器命名约定
```typescript
// 使用动词或动词短语
@validate
@cache
@retry
@log

// 使用描述性名称
@validateEmail
@cacheResult
@retryOnFailure
@logPerformance

// 避免使用单字母装饰器
@log  // ✅ 好
@l    // ❌ 不好
```

### 装饰器组合
```typescript
// 可以组合多个装饰器
class UserService {
  @retry(3, 1000)
  @cache
  @performance
  @log
  async fetchUser(id: string): Promise<User> {
    // 方法实现
  }
}

// 装饰器执行顺序：从下到上，从右到左
// @retry -> @cache -> @performance -> @log
```

### 错误处理
```typescript
// 在装饰器中提供有意义的错误信息
function validateEmail(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;

  descriptor.value = function (...args: any[]) {
    const email = args[0];

    if (!email || !email.includes('@')) {
      throw new Error(`Invalid email provided to ${propertyKey}: ${email}`);
    }

    return originalMethod.apply(this, args);
  };

  return descriptor;
}
```

## 📖 总结

TypeScript 装饰器提供了强大的元编程能力：

### 装饰器类型：
1. **类装饰器**: 修改类的行为和结构
2. **方法装饰器**: 增强方法功能
3. **属性装饰器**: 控制属性行为
4. **参数装饰器**: 修改参数处理

### 实际应用：
1. **API 控制器**: 构建 REST API 端点
2. **依赖注入**: 实现松耦合的架构
3. **权限控制**: 方法级别的访问控制
4. **性能监控**: 自动监控和缓存
5. **数据验证**: 自动验证输入数据

### 最佳实践：
1. **合理命名**: 使用描述性的装饰器名称
2. **组合使用**: 合理组合多个装饰器
3. **错误处理**: 提供清晰的错误信息
4. **性能考虑**: 避免过度使用装饰器

虽然装饰器仍然是 TypeScript 的实验性特性，但它们在许多现代框架（如 Angular、NestJS）中得到了广泛应用，是构建企业级应用的重要工具。