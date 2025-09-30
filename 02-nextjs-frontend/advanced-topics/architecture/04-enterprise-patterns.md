# 企业级模式 - Next.js 15 现代架构实践

## 📋 概述

企业级应用需要考虑可扩展性、安全性、可维护性和团队协作等多个方面。Next.js 15 提供了强大的功能来支持企业级应用的开发，本文将深入探讨企业级应用的设计模式和最佳实践。

## 🎯 企业级架构设计

### 1. 分层架构

```
enterprise-app/
├── presentation/           # 表现层
│   ├── components/        # UI组件
│   ├── pages/           # 页面
│   └── layouts/         # 布局
├── application/           # 应用层
│   ├── services/        # 应用服务
│   ├── dtos/            # 数据传输对象
│   └── use-cases/       # 用例
├── domain/              # 领域层
│   ├── entities/        # 领域实体
│   ├── value-objects/   # 值对象
│   └── repositories/     # 仓储接口
├── infrastructure/       # 基础设施层
│   ├── databases/       # 数据库实现
│   ├── external-apis/   # 外部API
│   └── messaging/       # 消息队列
└── shared/              # 共享模块
    ├── utils/           # 工具函数
    ├── constants/       # 常量
    └── types/           # 类型定义
```

### 2. CQRS 模式实现

```typescript
// domain/commands/CreateUserCommand.ts
export interface CreateUserCommand {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
  role: UserRole;
}

// domain/queries/GetUserQuery.ts
export interface GetUserQuery {
  userId: string;
}

// application/handlers/CreateUserHandler.ts
export class CreateUserHandler {
  constructor(
    private readonly userRepository: IUserRepository,
    private readonly eventBus: IEventBus,
    private readonly passwordHasher: IPasswordHasher
  ) {}

  async handle(command: CreateUserCommand): Promise<User> {
    // 验证命令
    await this.validateCommand(command);

    // 检查用户是否已存在
    const existingUser = await this.userRepository.findByEmail(command.email);
    if (existingUser) {
      throw new UserAlreadyExistsError(command.email);
    }

    // 创建用户
    const user = User.create({
      email: command.email,
      password: await this.passwordHasher.hash(command.password),
      firstName: command.firstName,
      lastName: command.lastName,
      role: command.role,
    });

    // 保存用户
    await this.userRepository.save(user);

    // 发布事件
    await this.eventBus.publish(new UserCreatedEvent(user.id, user.email));

    return user;
  }

  private async validateCommand(command: CreateUserCommand): Promise<void> {
    const errors: string[] = [];

    if (!command.email || !isValidEmail(command.email)) {
      errors.push('Invalid email address');
    }

    if (!command.password || command.password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }

    if (!command.firstName || command.firstName.trim().length < 2) {
      errors.push('First name must be at least 2 characters long');
    }

    if (!command.lastName || command.lastName.trim().length < 2) {
      errors.push('Last name must be at least 2 characters long');
    }

    if (errors.length > 0) {
      throw new ValidationError(errors);
    }
  }
}

// application/handlers/GetUserHandler.ts
export class GetUserHandler {
  constructor(
    private readonly userRepository: IUserRepository,
    private readonly cacheService: ICacheService
  ) {}

  async handle(query: GetUserQuery): Promise<UserDto | null> {
    // 尝试从缓存获取
    const cacheKey = `user:${query.userId}`;
    const cachedUser = await this.cacheService.get<UserDto>(cacheKey);

    if (cachedUser) {
      return cachedUser;
    }

    // 从数据库获取
    const user = await this.userRepository.findById(query.userId);
    if (!user) {
      return null;
    }

    // 转换为DTO
    const userDto: UserDto = {
      id: user.id,
      email: user.email,
      firstName: user.firstName,
      lastName: user.lastName,
      role: user.role,
      createdAt: user.createdAt,
      updatedAt: user.updatedAt,
    };

    // 缓存结果
    await this.cacheService.set(cacheKey, userDto, { ttl: 3600 });

    return userDto;
  }
}
```

## 🚀 领域驱动设计（DDD）

### 1. 领域实体

```typescript
// domain/entities/User.ts
export class User {
  private readonly _id: string;
  private _email: string;
  private _password: string;
  private _firstName: string;
  private _lastName: string;
  private _role: UserRole;
  private _isActive: boolean;
  private _createdAt: Date;
  private _updatedAt: Date;

  private constructor(data: UserData) {
    this._id = data.id;
    this._email = data.email;
    this._password = data.password;
    this._firstName = data.firstName;
    this._lastName = data.lastName;
    this._role = data.role;
    this._isActive = data.isActive;
    this._createdAt = data.createdAt;
    this._updatedAt = data.updatedAt;
  }

  static create(data: Omit<UserData, 'id' | 'createdAt' | 'updatedAt'>): User {
    const user = new User({
      ...data,
      id: uuidv4(),
      createdAt: new Date(),
      updatedAt: new Date(),
    });

    user.validate();

    return user;
  }

  static fromPersistence(data: UserData): User {
    return new User(data);
  }

  private validate(): void {
    const errors: string[] = [];

    if (!this._email || !isValidEmail(this._email)) {
      errors.push('Invalid email address');
    }

    if (!this._password || this._password.length < 8) {
      errors.push('Password must be at least 8 characters long');
    }

    if (!this._firstName || this._firstName.trim().length < 2) {
      errors.push('First name must be at least 2 characters long');
    }

    if (!this._lastName || this._lastName.trim().length < 2) {
      errors.push('Last name must be at least 2 characters long');
    }

    if (errors.length > 0) {
      throw new DomainValidationError('User', errors);
    }
  }

  // 领域方法
  updateProfile(data: { firstName: string; lastName: string }): void {
    this._firstName = data.firstName;
    this._lastName = data.lastName;
    this._updatedAt = new Date();

    this.validate();
  }

  changePassword(newPassword: string): void {
    if (newPassword.length < 8) {
      throw new DomainValidationError('User', ['Password must be at least 8 characters long']);
    }

    this._password = newPassword;
    this._updatedAt = new Date();
  }

  deactivate(): void {
    this._isActive = false;
    this._updatedAt = new Date();
  }

  activate(): void {
    this._isActive = true;
    this._updatedAt = new Date();
  }

  // 获取器
  get id(): string { return this._id; }
  get email(): string { return this._email; }
  get firstName(): string { return this._firstName; }
  get lastName(): string { return this._lastName; }
  get fullName(): string { return `${this._firstName} ${this._lastName}`; }
  get role(): UserRole { return this._role; }
  get isActive(): boolean { return this._isActive; }
  get createdAt(): Date { return this._createdAt; }
  get updatedAt(): Date { return this._updatedAt; }

  // 领域事件
  get domainEvents(): DomainEvent[] {
    return [];
  }
}

// domain/value-objects/Email.ts
export class Email {
  private readonly _value: string;

  constructor(value: string) {
    if (!isValidEmail(value)) {
      throw new InvalidEmailError(value);
    }
    this._value = value.toLowerCase();
  }

  get value(): string {
    return this._value;
  }

  equals(other: Email): boolean {
    return this._value === other._value;
  }

  toString(): string {
    return this._value;
  }
}

// domain/value-objects/Money.ts
export class Money {
  private readonly _amount: number;
  private readonly _currency: string;

  constructor(amount: number, currency: string) {
    if (amount < 0) {
      throw new InvalidMoneyError('Amount cannot be negative');
    }

    if (!isValidCurrency(currency)) {
      throw new InvalidMoneyError('Invalid currency code');
    }

    this._amount = Math.round(amount * 100) / 100; // 保留两位小数
    this._currency = currency.toUpperCase();
  }

  static fromString(value: string): Money {
    const match = value.match(/^([0-9]+(?:\.[0-9]{1,2})?)\s*([A-Z]{3})$/i);
    if (!match) {
      throw new InvalidMoneyError('Invalid money format');
    }

    const amount = parseFloat(match[1]);
    const currency = match[2];

    return new Money(amount, currency);
  }

  add(other: Money): Money {
    if (this._currency !== other._currency) {
      throw new CurrencyMismatchError(this._currency, other._currency);
    }

    return new Money(this._amount + other._amount, this._currency);
  }

  subtract(other: Money): Money {
    if (this._currency !== other._currency) {
      throw new CurrencyMismatchError(this._currency, other._currency);
    }

    return new Money(this._amount - other._amount, this._currency);
  }

  multiply(factor: number): Money {
    return new Money(this._amount * factor, this._currency);
  }

  get amount(): number { return this._amount; }
  get currency(): string { return this._currency; }

  toString(): string {
    return `${this._amount.toFixed(2)} ${this._currency}`;
  }
}
```

### 2. 仓储模式

```typescript
// domain/repositories/IUserRepository.ts
export interface IUserRepository {
  findById(id: string): Promise<User | null>;
  findByEmail(email: string): Promise<User | null>;
  save(user: User): Promise<void>;
  update(user: User): Promise<void>;
  delete(id: string): Promise<void>;
  findAll(options: PaginationOptions): Promise<PaginatedResult<User>>;
  findByRole(role: UserRole): Promise<User[]>;
}

// infrastructure/repositories/UserRepository.ts
export class UserRepository implements IUserRepository {
  constructor(
    private readonly prisma: PrismaClient,
    private readonly eventBus: IEventBus
  ) {}

  async findById(id: string): Promise<User | null> {
    const userRecord = await this.prisma.user.findUnique({
      where: { id },
      include: {
        roles: true,
        permissions: true,
      },
    });

    if (!userRecord) {
      return null;
    }

    return User.fromPersistence({
      id: userRecord.id,
      email: userRecord.email,
      password: userRecord.password,
      firstName: userRecord.firstName,
      lastName: userRecord.lastName,
      role: userRecord.roles[0]?.name as UserRole,
      isActive: userRecord.isActive,
      createdAt: userRecord.createdAt,
      updatedAt: userRecord.updatedAt,
    });
  }

  async findByEmail(email: string): Promise<User | null> {
    const userRecord = await this.prisma.user.findUnique({
      where: { email },
      include: {
        roles: true,
        permissions: true,
      },
    });

    if (!userRecord) {
      return null;
    }

    return User.fromPersistence({
      id: userRecord.id,
      email: userRecord.email,
      password: userRecord.password,
      firstName: userRecord.firstName,
      lastName: userRecord.lastName,
      role: userRecord.roles[0]?.name as UserRole,
      isActive: userRecord.isActive,
      createdAt: userRecord.createdAt,
      updatedAt: userRecord.updatedAt,
    });
  }

  async save(user: User): Promise<void> {
    const userData = {
      id: user.id,
      email: user.email,
      password: user._password,
      firstName: user.firstName,
      lastName: user.lastName,
      isActive: user.isActive,
      createdAt: user.createdAt,
      updatedAt: user.updatedAt,
    };

    await this.prisma.user.upsert({
      where: { id: user.id },
      create: userData,
      update: userData,
    });

    // 处理角色
    await this.prisma.userRole.deleteMany({
      where: { userId: user.id },
    });

    await this.prisma.userRole.create({
      data: {
        userId: user.id,
        roleId: await this.getRoleIdByName(user.role),
      },
    });

    // 发布领域事件
    for (const event of user.domainEvents) {
      await this.eventBus.publish(event);
    }
  }

  async findAll(options: PaginationOptions): Promise<PaginatedResult<User>> {
    const { page = 1, limit = 10, sortBy = 'createdAt', sortOrder = 'desc' } = options;
    const skip = (page - 1) * limit;

    const [users, total] = await Promise.all([
      this.prisma.user.findMany({
        skip,
        take: limit,
        orderBy: { [sortBy]: sortOrder },
        include: {
          roles: true,
          permissions: true,
        },
      }),
      this.prisma.user.count(),
    ]);

    const userEntities = users.map(userRecord =>
      User.fromPersistence({
        id: userRecord.id,
        email: userRecord.email,
        password: userRecord.password,
        firstName: userRecord.firstName,
        lastName: userRecord.lastName,
        role: userRecord.roles[0]?.name as UserRole,
        isActive: userRecord.isActive,
        createdAt: userRecord.createdAt,
        updatedAt: userRecord.updatedAt,
      })
    );

    return {
      data: userEntities,
      pagination: {
        page,
        limit,
        total,
        totalPages: Math.ceil(total / limit),
      },
    };
  }

  private async getRoleIdByName(roleName: UserRole): Promise<string> {
    const role = await this.prisma.role.findUnique({
      where: { name: roleName },
    });

    if (!role) {
      throw new Error(`Role ${roleName} not found`);
    }

    return role.id;
  }
}
```

## 🎨 企业级安全模式

### 1. 多因素认证

```typescript
// infrastructure/auth/MFAService.ts
export class MFAService {
  constructor(
    private readonly totpService: ITOTPService,
    private readonly smsService: ISMSService,
    private readonly emailService: IEmailService,
    private readonly userRepository: IUserRepository
  ) {}

  async setupMFA(userId: string, method: MFAMethod): Promise<MFASetupResult> {
    const user = await this.userRepository.findById(userId);
    if (!user) {
      throw new UserNotFoundError(userId);
    }

    switch (method) {
      case MFAMethod.TOTP:
        return this.setupTOTP(user);
      case MFAMethod.SMS:
        return this.setupSMS(user);
      case MFAMethod.EMAIL:
        return this.setupEmail(user);
      default:
        throw new UnsupportedMFAMethodError(method);
    }
  }

  private async setupTOTP(user: User): Promise<MFASetupResult> {
    const secret = this.totpService.generateSecret();
    const qrCodeUrl = this.totpService.generateQRCodeUrl(
      secret,
      user.email,
      'Enterprise App'
    );

    // 临时存储secret，用户验证后才启用
    await this.totpService.storeTemporarySecret(user.id, secret);

    return {
      method: MFAMethod.TOTP,
      secret,
      qrCodeUrl,
      backupCodes: await this.generateBackupCodes(user.id),
    };
  }

  private async setupSMS(user: User): Promise<MFASetupResult> {
    const code = Math.floor(100000 + Math.random() * 900000).toString();

    await this.smsService.sendSMS(
      user.phoneNumber,
      `Your verification code is: ${code}`
    );

    // 临时存储code
    await this.totpService.storeTemporaryCode(user.id, code);

    return {
      method: MFAMethod.SMS,
      phoneNumber: user.phoneNumber,
      backupCodes: await this.generateBackupCodes(user.id),
    };
  }

  private async setupEmail(user: User): Promise<MFASetupResult> {
    const code = Math.floor(100000 + Math.random() * 900000).toString();

    await this.emailService.sendEmail(
      user.email,
      'Your MFA Verification Code',
      `Your verification code is: ${code}`
    );

    // 临时存储code
    await this.totpService.storeTemporaryCode(user.id, code);

    return {
      method: MFAMethod.EMAIL,
      email: user.email,
      backupCodes: await this.generateBackupCodes(user.id),
    };
  }

  async verifyMFA(userId: string, code: string): Promise<boolean> {
    const user = await this.userRepository.findById(userId);
    if (!user) {
      throw new UserNotFoundError(userId);
    }

    // 检查TOTP
    const isValidTOTP = await this.totpService.verifyCode(userId, code);
    if (isValidTOTP) {
      await this.enableMFA(userId, MFAMethod.TOTP);
      return true;
    }

    // 检查临时code
    const isValidTemporary = await this.totpService.verifyTemporaryCode(userId, code);
    if (isValidTemporary) {
      await this.enableMFA(userId, MFAMethod.SMS);
      return true;
    }

    // 检查备用码
    const isValidBackup = await this.totpService.verifyBackupCode(userId, code);
    if (isValidBackup) {
      return true;
    }

    return false;
  }

  private async enableMFA(userId: string, method: MFAMethod): Promise<void> {
    await this.userRepository.updateMFAStatus(userId, {
      enabled: true,
      method,
    });
  }

  private async generateBackupCodes(userId: string): Promise<string[]> {
    const codes = Array.from({ length: 10 }, () =>
      Math.random().toString(36).substring(2, 8).toUpperCase()
    );

    await this.totpService.storeBackupCodes(userId, codes);

    return codes;
  }
}
```

### 2. 权限和角色管理

```typescript
// domain/entities/Permission.ts
export class Permission {
  private readonly _id: string;
  private readonly _name: string;
  private readonly _resource: string;
  private readonly _action: string;
  private readonly _description: string;

  constructor(data: PermissionData) {
    this._id = data.id;
    this._name = data.name;
    this._resource = data.resource;
    this._action = data.action;
    this._description = data.description;
  }

  get id(): string { return this._id; }
  get name(): string { return this._name; }
  get resource(): string { return this._resource; }
  get action(): string { return this._action; }
  get description(): string { return this._description; }

  matches(resource: string, action: string): boolean {
    return this._resource === resource && this._action === action;
  }
}

// domain/entities/Role.ts
export class Role {
  private readonly _id: string;
  private readonly _name: string;
  private readonly _description: string;
  private readonly _permissions: Set<Permission>;

  constructor(data: RoleData) {
    this._id = data.id;
    this._name = data.name;
    this._description = data.description;
    this._permissions = new Set(data.permissions || []);
  }

  get id(): string { return this._id; }
  get name(): string { return this._name; }
  get description(): string { return this._description; }
  get permissions(): Permission[] { return Array.from(this._permissions); }

  hasPermission(resource: string, action: string): boolean {
    return Array.from(this._permissions).some(permission =>
      permission.matches(resource, action)
    );
  }

  addPermission(permission: Permission): void {
    this._permissions.add(permission);
  }

  removePermission(permissionId: string): void {
    this._permissions.forEach(permission => {
      if (permission.id === permissionId) {
        this._permissions.delete(permission);
      }
    });
  }
}

// application/services/AuthorizationService.ts
export class AuthorizationService {
  constructor(
    private readonly roleRepository: IRoleRepository,
    private readonly permissionRepository: IPermissionRepository
  ) {}

  async canUserPerformAction(
    userId: string,
    resource: string,
    action: string
  ): Promise<boolean> {
    // 获取用户角色
    const userRoles = await this.roleRepository.findByUserId(userId);

    // 检查每个角色是否有对应权限
    for (const role of userRoles) {
      if (role.hasPermission(resource, action)) {
        return true;
      }
    }

    return false;
  }

  async getUserPermissions(userId: string): Promise<Permission[]> {
    const userRoles = await this.roleRepository.findByUserId(userId);
    const allPermissions = new Set<Permission>();

    for (const role of userRoles) {
      role.permissions.forEach(permission => {
        allPermissions.add(permission);
      });
    }

    return Array.from(allPermissions);
  }

  async checkAccess(
    userId: string,
    resource: string,
    action: string,
    context?: any
  ): Promise<AccessResult> {
    const hasPermission = await this.canUserPerformAction(userId, resource, action);

    if (!hasPermission) {
      return {
        granted: false,
        reason: 'Insufficient permissions',
      };
    }

    // 检查业务规则
    const businessRuleResult = await this.checkBusinessRules(userId, resource, action, context);
    if (!businessRuleResult.granted) {
      return businessRuleResult;
    }

    return {
      granted: true,
    };
  }

  private async checkBusinessRules(
    userId: string,
    resource: string,
    action: string,
    context?: any
  ): Promise<AccessResult> {
    // 根据资源类型执行特定的业务规则检查
    switch (resource) {
      case 'order':
        return this.checkOrderAccess(userId, action, context);
      case 'user':
        return this.checkUserAccess(userId, action, context);
      case 'financial':
        return this.checkFinancialAccess(userId, action, context);
      default:
        return { granted: true };
    }
  }

  private async checkOrderAccess(
    userId: string,
    action: string,
    context?: { orderId?: string }
  ): Promise<AccessResult> {
    if (action === 'delete' && context?.orderId) {
      // 检查是否是订单的所有者
      const isOwner = await this.isOrderOwner(userId, context.orderId);
      if (!isOwner) {
        return {
          granted: false,
          reason: 'Can only delete your own orders',
        };
      }
    }

    return { granted: true };
  }

  private async checkUserAccess(
    userId: string,
    action: string,
    context?: { targetUserId?: string }
  ): Promise<AccessResult> {
    if (context?.targetUserId && context.targetUserId !== userId) {
      // 只有管理员可以操作其他用户
      const isAdmin = await this.canUserPerformAction(userId, 'admin', 'manage_users');
      if (!isAdmin) {
        return {
          granted: false,
          reason: 'Can only manage your own account',
        };
      }
    }

    return { granted: true };
  }

  private async checkFinancialAccess(
    userId: string,
    action: string,
    context?: any
  ): Promise<AccessResult> {
    // 财务操作需要特殊的审计检查
    if (['create', 'update', 'delete'].includes(action)) {
      const hasAuditPermission = await this.canUserPerformAction(userId, 'financial', 'audit');
      if (!hasAuditPermission) {
        return {
          granted: false,
          reason: 'Financial operations require audit permissions',
        };
      }
    }

    return { granted: true };
  }

  private async isOrderOwner(userId: string, orderId: string): Promise<boolean> {
    // 实现检查用户是否是订单所有者的逻辑
    return true;
  }
}
```

## 🔄 企业级监控和日志

### 1. 结构化日志

```typescript
// infrastructure/logging/StructuredLogger.ts
export class StructuredLogger {
  constructor(
    private readonly serviceName: string,
    private readonly logLevel: LogLevel = LogLevel.INFO
  ) {}

  info(message: string, meta?: Record<string, any>): void {
    this.log(LogLevel.INFO, message, meta);
  }

  warn(message: string, meta?: Record<string, any>): void {
    this.log(LogLevel.WARN, message, meta);
  }

  error(message: string, error?: Error, meta?: Record<string, any>): void {
    this.log(LogLevel.ERROR, message, {
      ...meta,
      error: error ? {
        message: error.message,
        stack: error.stack,
        name: error.name,
      } : undefined,
    });
  }

  debug(message: string, meta?: Record<string, any>): void {
    this.log(LogLevel.DEBUG, message, meta);
  }

  private log(level: LogLevel, message: string, meta?: Record<string, any>): void {
    if (level < this.logLevel) {
      return;
    }

    const logEntry: LogEntry = {
      timestamp: new Date().toISOString(),
      level: LogLevel[level],
      service: this.serviceName,
      message,
      ...meta,
      traceId: this.getTraceId(),
      spanId: this.getSpanId(),
    };

    // 根据环境选择输出方式
    if (process.env.NODE_ENV === 'production') {
      // 发送到日志服务
      this.sendToLogService(logEntry);
    } else {
      // 开发环境输出到控制台
      console.log(JSON.stringify(logEntry, null, 2));
    }
  }

  private getTraceId(): string {
    // 从上下文或请求头中获取trace ID
    return 'trace-id';
  }

  private getSpanId(): string {
    // 从上下文或请求头中获取span ID
    return 'span-id';
  }

  private async sendToLogEntry(logEntry: LogEntry): Promise<void> {
    try {
      await fetch(process.env.LOG_SERVICE_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(logEntry),
      });
    } catch (error) {
      console.error('Failed to send log entry:', error);
    }
  }
}

// 使用示例
const logger = new StructuredLogger('user-service');

export class UserService {
  async createUser(userData: CreateUserDto): Promise<User> {
    try {
      logger.info('Creating new user', {
        email: userData.email,
        firstName: userData.firstName,
        lastName: userData.lastName,
      });

      const user = await this.userRepository.create(userData);

      logger.info('User created successfully', {
        userId: user.id,
        email: user.email,
      });

      return user;
    } catch (error) {
      logger.error('Failed to create user', error as Error, {
        email: userData.email,
      });
      throw error;
    }
  }
}
```

### 2. 性能监控

```typescript
// infrastructure/monitoring/PerformanceMonitor.ts
export class PerformanceMonitor {
  private metrics: Map<string, Metric[]> = new Map();

  recordMetric(name: string, value: number, tags: Record<string, string> = {}): void {
    const metric: Metric = {
      name,
      value,
      timestamp: Date.now(),
      tags,
    };

    if (!this.metrics.has(name)) {
      this.metrics.set(name, []);
    }

    this.metrics.get(name)!.push(metric);

    // 限制内存中的指标数量
    const metrics = this.metrics.get(name)!;
    if (metrics.length > 1000) {
      metrics.shift();
    }
  }

  recordDuration(name: string, duration: number, tags: Record<string, string> = {}): void {
    this.recordMetric(`${name}.duration`, duration, tags);
  }

  recordCounter(name: string, increment: number = 1, tags: Record<string, string> = {}): void {
    this.recordMetric(`${name}.count`, increment, tags);
  }

  getMetrics(name?: string): Metric[] {
    if (name) {
      return this.metrics.get(name) || [];
    }
    return Array.from(this.metrics.values()).flat();
  }

  getAggregatedMetrics(name: string, timeRange: number = 3600000): AggregatedMetrics {
    const metrics = this.metrics.get(name) || [];
    const cutoff = Date.now() - timeRange;
    const recentMetrics = metrics.filter(m => m.timestamp > cutoff);

    if (recentMetrics.length === 0) {
      return {
        count: 0,
        sum: 0,
        avg: 0,
        min: 0,
        max: 0,
        p95: 0,
        p99: 0,
      };
    }

    const values = recentMetrics.map(m => m.value).sort((a, b) => a - b);
    const sum = values.reduce((a, b) => a + b, 0);

    return {
      count: values.length,
      sum,
      avg: sum / values.length,
      min: values[0],
      max: values[values.length - 1],
      p95: this.percentile(values, 95),
      p99: this.percentile(values, 99),
    };
  }

  private percentile(values: number[], p: number): number {
    const index = Math.ceil((p / 100) * values.length) - 1;
    return values[index];
  }
}

// 装饰器使用
export function measurePerformance(target: any, propertyKey: string, descriptor: PropertyDescriptor) {
  const originalMethod = descriptor.value;
  const monitor = new PerformanceMonitor();

  descriptor.value = async function (...args: any[]) {
    const startTime = performance.now();
    const methodName = `${target.constructor.name}.${propertyKey}`;

    try {
      const result = await originalMethod.apply(this, args);
      const duration = performance.now() - startTime;

      monitor.recordDuration(methodName, duration, {
        success: 'true',
      });

      return result;
    } catch (error) {
      const duration = performance.now() - startTime;

      monitor.recordDuration(methodName, duration, {
        success: 'false',
        error: error instanceof Error ? error.name : 'unknown',
      });

      throw error;
    }
  };

  return descriptor;
}

// 使用示例
export class UserService {
  @measurePerformance
  async createUser(userData: CreateUserDto): Promise<User> {
    // 创建用户逻辑
  }
}
```

## 🎯 企业级测试策略

### 1. 集成测试

```typescript
// tests/integration/UserIntegration.test.ts
import { TestContainer } from '@testcontainers/postgresql';
import { PrismaClient } from '@prisma/client';
import { UserService } from '@/application/services/UserService';
import { UserRepository } from '@/infrastructure/repositories/UserRepository';
import { MFAService } from '@/infrastructure/auth/MFAService';

describe('User Integration Tests', () => {
  let container: TestContainer;
  let prisma: PrismaClient;
  let userService: UserService;
  let userRepository: UserRepository;
  let mfaService: MFAService;

  beforeAll(async () => {
    // 启动测试数据库
    container = await new TestContainer('postgres:15-alpine')
      .withExposedPorts(5432)
      .start();

    const connectionString = `postgresql://test:test@localhost:${container.getMappedPort(5432)}/test`;

    prisma = new PrismaClient({
      datasources: {
        db: {
          url: connectionString,
        },
      },
    });

    await prisma.$connect();
    await prisma.$executeRaw`CREATE SCHEMA IF NOT EXISTS test`;

    // 运行迁移
    await prisma.$executeRaw`
      CREATE TABLE users (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        email VARCHAR(255) UNIQUE NOT NULL,
        password VARCHAR(255) NOT NULL,
        first_name VARCHAR(100) NOT NULL,
        last_name VARCHAR(100) NOT NULL,
        is_active BOOLEAN DEFAULT true,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
      )
    `;

    // 初始化服务
    userRepository = new UserRepository(prisma, mockEventBus);
    mfaService = new MFAService(mockTOTPService, mockSMSService, mockEmailService, userRepository);
    userService = new UserService(userRepository, mfaService, mockPasswordHasher);
  });

  afterAll(async () => {
    await prisma.$disconnect();
    await container.stop();
  });

  beforeEach(async () => {
    // 清理测试数据
    await prisma.user.deleteMany();
  });

  describe('User Creation', () => {
    it('should create user with valid data', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe',
      };

      const user = await userService.createUser(userData);

      expect(user).toBeDefined();
      expect(user.email).toBe(userData.email);
      expect(user.firstName).toBe(userData.firstName);
      expect(user.lastName).toBe(userData.lastName);

      // 验证数据库中的数据
      const dbUser = await prisma.user.findUnique({
        where: { id: user.id },
      });

      expect(dbUser).toBeTruthy();
      expect(dbUser.email).toBe(userData.email);
    });

    it('should throw error for duplicate email', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe',
      };

      // 创建第一个用户
      await userService.createUser(userData);

      // 尝试创建重复用户
      await expect(userService.createUser(userData)).rejects.toThrow(
        UserAlreadyExistsError
      );
    });

    it('should hash password on creation', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe',
      };

      const user = await userService.createUser(userData);

      const dbUser = await prisma.user.findUnique({
        where: { id: user.id },
      });

      expect(dbUser.password).not.toBe(userData.password);
      expect(dbUser.password).toMatch(/^\$2[ayb]\$.{56}$/);
    });
  });

  describe('MFA Setup', () => {
    it('should setup TOTP for user', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe',
      };

      const user = await userService.createUser(userData);
      const mfaSetup = await mfaService.setupMFA(user.id, MFAMethod.TOTP);

      expect(mfaSetup.method).toBe(MFAMethod.TOTP);
      expect(mfaSetup.secret).toBeDefined();
      expect(mfaSetup.qrCodeUrl).toBeDefined();
      expect(mfaSetup.backupCodes).toHaveLength(10);
    });

    it('should verify MFA code', async () => {
      const userData = {
        email: 'test@example.com',
        password: 'password123',
        firstName: 'John',
        lastName: 'Doe',
      };

      const user = await userService.createUser(userData);
      const mfaSetup = await mfaService.setupMFA(user.id, MFAMethod.TOTP);

      // 模拟TOTP验证
      const isValid = await mfaService.verifyMFA(user.id, '123456');

      expect(isValid).toBe(true);
    });
  });
});
```

### 2. E2E 测试

```typescript
// tests/e2e/auth-flow.test.ts
import { test, expect } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/login');
  });

  test('should login with valid credentials', async ({ page }) => {
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');

    await expect(page).toHaveURL('/dashboard');
    await expect(page.locator('[data-testid="welcome-message"]')).toBeVisible();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.fill('[data-testid="email"]', 'invalid@example.com');
    await page.fill('[data-testid="password"] = 'wrongpassword');
    await page.click('[data-testid="login-button"]');

    await expect(page.locator('[data-testid="error-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="error-message"]')).toHaveText(
      'Invalid email or password'
    );
  });

  test('should setup MFA after first login', async ({ page }) => {
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.fill('[data-testid="password"]', 'password123');
    await page.click('[data-testid="login-button"]');

    // 重定向到MFA设置页面
    await expect(page).toHaveURL('/setup-mfa');
    await expect(page.locator('[data-testid="mfa-setup-title"]')).toBeVisible();

    // 选择TOTP
    await page.click('[data-testid="totp-option"]');

    // 验证QR码显示
    await expect(page.locator('[data-testid="qr-code"]')).toBeVisible();

    // 模拟验证
    await page.fill('[data-testid="verification-code"]', '123456');
    await page.click('[data-testid="verify-button"]');

    await expect(page).toHaveURL('/dashboard');
  });

  test('should handle password reset flow', async ({ page }) => {
    // 点击忘记密码链接
    await page.click('[data-testid="forgot-password"]');

    await expect(page).toHaveURL('/forgot-password');

    // 输入邮箱
    await page.fill('[data-testid="email"]', 'test@example.com');
    await page.click('[data-testid="reset-button"]');

    // 等待成功消息
    await expect(page.locator('[data-testid="success-message"]')).toBeVisible();
    await expect(page.locator('[data-testid="success-message"]')).toHaveText(
      'Password reset email sent'
    );
  });
});
```

## 🎯 总结

Next.js 15 的企业级模式为构建大型、复杂的应用提供了强大的架构支持。通过合理使用分层架构、领域驱动设计、安全模式和监控体系，可以构建出高质量、可维护的企业级应用。

### 关键要点：

1. **架构设计**：分层架构、CQRS模式、领域驱动设计
2. **领域建模**：实体、值对象、仓储模式
3. **安全体系**：多因素认证、权限管理、审计日志
4. **监控体系**：结构化日志、性能监控、错误追踪
5. **测试策略**：单元测试、集成测试、E2E测试

### 实施建议：

- **渐进式实施**：从简单模式开始，逐步引入复杂模式
- **团队培训**：确保团队理解企业级架构的概念和原则
- **工具选择**：选择合适的工具链和框架
- **文档完善**：建立完整的架构文档和最佳实践指南
- **持续改进**：根据实际使用情况不断优化架构

通过掌握这些企业级模式，可以构建出满足企业级需求的高质量应用。