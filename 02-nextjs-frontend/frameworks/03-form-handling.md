# 表单处理 - React Hook Form + Zod 验证

## 概述

表单是Web应用中最重要的交互元素之一。与PHP中直接处理`$_POST`或`$_GET`不同，React中的表单处理需要考虑状态管理、验证、提交等多个方面。本指南将介绍现代React表单处理的最佳实践，包括React Hook Form和Zod验证。

## 从PHP表单到React表单的对比

### PHP表单处理
```php
<!-- HTML表单 -->
<form method="POST" action="/submit.php">
    <input type="text" name="username" required>
    <input type="email" name="email" required>
    <input type="password" name="password" required>
    <button type="submit">提交</button>
</form>

<!-- PHP处理 -->
<?php
$username = $_POST['username'] ?? '';
$email = $_POST['email'] ?? '';
$password = $_POST['password'] ?? '';

// 验证
if (empty($username) || !filter_var($email, FILTER_VALIDATE_EMAIL)) {
    die('输入无效');
}

// 处理数据
// ...
?>
```

### React表单处理
```tsx
// React组件表单
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const schema = z.object({
  username: z.string().min(2, '用户名至少2个字符'),
  email: z.string().email('请输入有效的邮箱地址'),
  password: z.string().min(8, '密码至少8个字符'),
});

function LoginForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({
    resolver: zodResolver(schema),
  });

  const onSubmit = async (data) => {
    console.log(data);
    // 提交到API
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <input {...register('username')} placeholder="用户名" />
      {errors.username && <p>{errors.username.message}</p>}

      <input {...register('email')} type="email" placeholder="邮箱" />
      {errors.email && <p>{errors.email.message}</p>}

      <input {...register('password')} type="password" placeholder="密码" />
      {errors.password && <p>{errors.password.message}</p>}

      <button type="submit" disabled={isSubmitting}>
        {isSubmitting ? '提交中...' : '提交'}
      </button>
    </form>
  );
}
```

## React Hook Form 基础

### 1. 安装和配置

```bash
npm install react-hook-form
npm install @hookform/resolvers zod
```

### 2. 基本用法

```tsx
import { useForm } from 'react-hook-form';

interface FormData {
  name: string;
  email: string;
  age: number;
}

function BasicForm() {
  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<FormData>();

  const onSubmit = (data: FormData) => {
    console.log(data);
    // 提交逻辑
    reset(); // 重置表单
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)}>
      <div>
        <label>姓名</label>
        <input
          {...register('name', {
            required: '姓名是必填项',
            minLength: {
              value: 2,
              message: '姓名至少2个字符',
            },
          })}
        />
        {errors.name && <p className="error">{errors.name.message}</p>}
      </div>

      <div>
        <label>邮箱</label>
        <input
          type="email"
          {...register('email', {
            required: '邮箱是必填项',
            pattern: {
              value: /^[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}$/i,
              message: '请输入有效的邮箱地址',
            },
          })}
        />
        {errors.email && <p className="error">{errors.email.message}</p>}
      </div>

      <div>
        <label>年龄</label>
        <input
          type="number"
          {...register('age', {
            required: '年龄是必填项',
            min: {
              value: 18,
              message: '年龄必须大于18岁',
            },
            max: {
              value: 120,
              message: '年龄必须小于120岁',
            },
          })}
        />
        {errors.age && <p className="error">{errors.age.message}</p>}
      </div>

      <button type="submit">提交</button>
      <button type="button" onClick={() => reset()}>
        重置
      </button>
    </form>
  );
}
```

## Zod 验证模式

### 1. 基础验证

```tsx
import { z } from 'zod';

// 基础模式
const basicSchema = z.object({
  email: z.string().email('请输入有效的邮箱地址'),
  password: z.string().min(8, '密码至少8个字符'),
});

// 嵌套对象
const addressSchema = z.object({
  street: z.string().min(1, '街道地址不能为空'),
  city: z.string().min(1, '城市不能为空'),
  zipCode: z.string().regex(/^\d{6}$/, '邮政编码必须是6位数字'),
});

const userSchema = z.object({
  name: z.string().min(2, '姓名至少2个字符'),
  email: z.string().email('请输入有效的邮箱地址'),
  age: z.number().min(18, '年龄必须大于18岁'),
  address: addressSchema,
});

// 数组验证
const tagsSchema = z.array(z.string().min(1, '标签不能为空')).min(1, '至少需要一个标签');

// 联合类型
const phoneSchema = z.union([
  z.string().regex(/^1[3-9]\d{9}$/, '请输入有效的手机号'),
  z.string().email('请输入有效的邮箱地址'),
]);
```

### 2. 高级验证

```tsx
// 自定义验证
const passwordSchema = z.string()
  .min(8, '密码至少8个字符')
  .regex(/[A-Z]/, '密码必须包含大写字母')
  .regex(/[a-z]/, '密码必须包含小写字母')
  .regex(/[0-9]/, '密码必须包含数字')
  .regex(/[^A-Za-z0-9]/, '密码必须包含特殊字符');

// 条件验证
const conditionalSchema = z.object({
  accountType: z.enum(['personal', 'business']),
  companyName: z.string().optional(),
}).refine(
  (data) => data.accountType !== 'business' || data.companyName,
  {
    message: '企业账户必须提供公司名称',
    path: ['companyName'],
  }
);

// 异步验证
const emailUniqueSchema = z.string().email().refine(
  async (email) => {
    const response = await fetch(`/api/check-email?email=${email}`);
    const result = await response.json();
    return result.available;
  },
  {
    message: '邮箱已被使用',
  }
);

// 变换处理
const userSchema = z.object({
  name: z.string().transform((val) => val.trim()),
  email: z.string().transform((val) => val.toLowerCase()),
  age: z.string().transform((val) => parseInt(val, 10)),
});
```

## 综合表单示例

### 1. 用户注册表单

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const registerSchema = z.object({
  username: z
    .string()
    .min(3, '用户名至少3个字符')
    .max(20, '用户名最多20个字符')
    .regex(/^[a-zA-Z0-9_]+$/, '用户名只能包含字母、数字和下划线'),

  email: z
    .string()
    .email('请输入有效的邮箱地址'),

  password: z
    .string()
    .min(8, '密码至少8个字符')
    .regex(/[A-Z]/, '密码必须包含大写字母')
    .regex(/[a-z]/, '密码必须包含小写字母')
    .regex(/[0-9]/, '密码必须包含数字')
    .regex(/[^A-Za-z0-9]/, '密码必须包含特殊字符'),

  confirmPassword: z.string(),
  agreeTerms: z.boolean().refine((val) => val === true, '必须同意服务条款'),
}).refine((data) => data.password === data.confirmPassword, {
  message: '两次输入的密码不一致',
  path: ['confirmPassword'],
});

type RegisterFormData = z.infer<typeof registerSchema>;

function RegisterForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setError,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  const onSubmit = async (data: RegisterFormData) => {
    try {
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: data.username,
          email: data.email,
          password: data.password,
        }),
      });

      const result = await response.json();

      if (!response.ok) {
        throw new Error(result.message || '注册失败');
      }

      console.log('注册成功:', result);
    } catch (error) {
      setError('root', {
        message: error.message,
      });
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-md mx-auto space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          用户名
        </label>
        <input
          {...register('username')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="请输入用户名"
        />
        {errors.username && (
          <p className="mt-1 text-sm text-red-600">{errors.username.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          邮箱
        </label>
        <input
          {...register('email')}
          type="email"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="请输入邮箱"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          密码
        </label>
        <input
          {...register('password')}
          type="password"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="请输入密码"
        />
        {errors.password && (
          <p className="mt-1 text-sm text-red-600">{errors.password.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          确认密码
        </label>
        <input
          {...register('confirmPassword')}
          type="password"
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          placeholder="请再次输入密码"
        />
        {errors.confirmPassword && (
          <p className="mt-1 text-sm text-red-600">{errors.confirmPassword.message}</p>
        )}
      </div>

      <div className="flex items-center">
        <input
          {...register('agreeTerms')}
          type="checkbox"
          className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
        />
        <label className="ml-2 block text-sm text-gray-900">
          我同意<a href="/terms" className="text-blue-600 hover:text-blue-500">服务条款</a>
        </label>
      </div>
      {errors.agreeTerms && (
        <p className="text-sm text-red-600">{errors.agreeTerms.message}</p>
      )}

      {errors.root && (
        <p className="text-sm text-red-600">{errors.root.message}</p>
      )}

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
      >
        {isSubmitting ? '注册中...' : '注册'}
      </button>
    </form>
  );
}
```

### 2. 动态表单

```tsx
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const educationSchema = z.object({
  school: z.string().min(1, '学校名称不能为空'),
  degree: z.string().min(1, '学位不能为空'),
  year: z.string().regex(/^\d{4}$/, '年份必须是4位数字'),
});

const profileSchema = z.object({
  name: z.string().min(1, '姓名不能为空'),
  email: z.string().email('请输入有效的邮箱'),
  education: z.array(educationSchema).min(1, '至少需要一条教育经历'),
});

type ProfileFormData = z.infer<typeof profileSchema>;

function ProfileForm() {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
    defaultValues: {
      education: [{ school: '', degree: '', year: '' }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'education',
  });

  const onSubmit = (data: ProfileFormData) => {
    console.log(data);
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          姓名
        </label>
        <input
          {...register('name')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
        {errors.name && (
          <p className="mt-1 text-sm text-red-600">{errors.name.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          邮箱
        </label>
        <input
          {...register('email')}
          type="email"
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
        {errors.email && (
          <p className="mt-1 text-sm text-red-600">{errors.email.message}</p>
        )}
      </div>

      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">教育经历</h3>
          <button
            type="button"
            onClick={() => append({ school: '', degree: '', year: '' })}
            className="px-3 py-1 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
          >
            添加
          </button>
        </div>

        {fields.map((field, index) => (
          <div key={field.id} className="border border-gray-200 rounded-md p-4 mb-4">
            <div className="flex justify-between items-center mb-3">
              <h4 className="text-md font-medium">教育经历 {index + 1}</h4>
              {fields.length > 1 && (
                <button
                  type="button"
                  onClick={() => remove(index)}
                  className="text-red-600 hover:text-red-700"
                >
                  删除
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  学校
                </label>
                <input
                  {...register(`education.${index}.school`)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
                {errors.education?.[index]?.school && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.education[index]?.school?.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  学位
                </label>
                <input
                  {...register(`education.${index}.degree`)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                />
                {errors.education?.[index]?.degree && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.education[index]?.degree?.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  年份
                </label>
                <input
                  {...register(`education.${index}.year`)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="2024"
                />
                {errors.education?.[index]?.year && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.education[index]?.year?.message}
                  </p>
                )}
              </div>
            </div>
          </div>
        ))}

        {errors.education && (
          <p className="text-sm text-red-600">{errors.education.message}</p>
        )}
      </div>

      <button
        type="submit"
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        提交
      </button>
    </form>
  );
}
```

## 文件上传处理

### 1. 单文件上传

```tsx
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const uploadSchema = z.object({
  title: z.string().min(1, '标题不能为空'),
  file: z.instanceof(FileList).refine(
    (files) => files.length > 0,
    '请选择文件'
  ).refine(
    (files) => files[0]?.size <= 5 * 1024 * 1024, // 5MB
    '文件大小不能超过5MB'
  ).refine(
    (files) => ['image/jpeg', 'image/png', 'image/gif'].includes(files[0]?.type),
    '只支持JPEG、PNG和GIF格式'
  ),
});

type UploadFormData = z.infer<typeof uploadSchema>;

function FileUploadForm() {
  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
    setValue,
  } = useForm<UploadFormData>({
    resolver: zodResolver(uploadSchema),
  });

  const onSubmit = async (data: UploadFormData) => {
    const formData = new FormData();
    formData.append('title', data.title);
    formData.append('file', data.file[0]);

    try {
      const response = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      console.log('上传成功:', result);
    } catch (error) {
      console.error('上传失败:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          标题
        </label>
        <input
          {...register('title')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
        )}
      </div>

      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          文件上传
        </label>
        <input
          type="file"
          {...register('file', {
            onChange: (e) => {
              setValue('file', e.target.files, { shouldValidate: true });
            },
          })}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
          accept="image/jpeg,image/png,image/gif"
        />
        {errors.file && (
          <p className="mt-1 text-sm text-red-600">{errors.file.message}</p>
        )}
        <p className="mt-1 text-sm text-gray-500">
          支持JPEG、PNG、GIF格式，最大5MB
        </p>
      </div>

      <button
        type="submit"
        disabled={isSubmitting}
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
      >
        {isSubmitting ? '上传中...' : '上传'}
      </button>
    </form>
  );
}
```

### 2. 多文件上传

```tsx
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

const multiUploadSchema = z.object({
  title: z.string().min(1, '标题不能为空'),
  files: z.array(z.object({
    file: z.instanceof(File).refine(
      (file) => file.size <= 5 * 1024 * 1024,
      '文件大小不能超过5MB'
    ).refine(
      (file) => ['image/jpeg', 'image/png', 'image/gif'].includes(file.type),
      '只支持JPEG、PNG和GIF格式'
    ),
    description: z.string().optional(),
  })).min(1, '至少上传一个文件'),
});

type MultiUploadFormData = z.infer<typeof multiUploadSchema>;

function MultiFileUploadForm() {
  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
  } = useForm<MultiUploadFormData>({
    resolver: zodResolver(multiUploadSchema),
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'files',
  });

  const onSubmit = async (data: MultiUploadFormData) => {
    const formData = new FormData();
    formData.append('title', data.title);

    data.files.forEach((fileItem, index) => {
      formData.append(`files[${index}][file]`, fileItem.file);
      formData.append(`files[${index}][description]`, fileItem.description || '');
    });

    try {
      const response = await fetch('/api/upload-multiple', {
        method: 'POST',
        body: formData,
      });

      const result = await response.json();
      console.log('上传成功:', result);
    } catch (error) {
      console.error('上传失败:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1">
          标题
        </label>
        <input
          {...register('title')}
          className="w-full px-3 py-2 border border-gray-300 rounded-md"
        />
        {errors.title && (
          <p className="mt-1 text-sm text-red-600">{errors.title.message}</p>
        )}
      </div>

      <div>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-medium text-gray-900">文件列表</h3>
          <button
            type="button"
            onClick={() => append({ file: new File([], ''), description: '' })}
            className="px-3 py-1 bg-blue-600 text-white rounded-md text-sm hover:bg-blue-700"
          >
            添加文件
          </button>
        </div>

        {fields.map((field, index) => (
          <div key={field.id} className="border border-gray-200 rounded-md p-4 mb-4">
            <div className="flex justify-between items-center mb-3">
              <h4 className="text-md font-medium">文件 {index + 1}</h4>
              <button
                type="button"
                onClick={() => remove(index)}
                className="text-red-600 hover:text-red-700"
              >
                删除
              </button>
            </div>

            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  选择文件
                </label>
                <input
                  type="file"
                  {...register(`files.${index}.file`)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  accept="image/jpeg,image/png,image/gif"
                />
                {errors.files?.[index]?.file && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.files[index]?.file?.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  描述（可选）
                </label>
                <input
                  {...register(`files.${index}.description`)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  placeholder="文件描述"
                />
              </div>
            </div>
          </div>
        ))}

        {errors.files && (
          <p className="text-sm text-red-600">{errors.files.message}</p>
        )}
      </div>

      <button
        type="submit"
        className="w-full py-2 px-4 bg-blue-600 text-white rounded-md hover:bg-blue-700"
      >
        上传所有文件
      </button>
    </form>
  );
}
```

## 表单优化和最佳实践

### 1. 性能优化

```tsx
import { memo } from 'react';
import { useForm, Controller } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';

// 使用 memo 优化组件
const FormField = memo(({
  label,
  error,
  children
}: {
  label: string;
  error?: string;
  children: React.ReactNode;
}) => (
  <div className="mb-4">
    <label className="block text-sm font-medium text-gray-700 mb-1">
      {label}
    </label>
    {children}
    {error && (
      <p className="mt-1 text-sm text-red-600">{error}</p>
    )}
  </div>
));

// 使用 Controller 处理复杂组件
const SelectField = ({
  name,
  control,
  label,
  options,
  error
}: {
  name: string;
  control: any;
  label: string;
  options: Array<{ value: string; label: string }>;
  error?: string;
}) => (
  <FormField label={label} error={error}>
    <Controller
      name={name}
      control={control}
      render={({ field }) => (
        <select
          {...field}
          className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        >
          <option value="">请选择</option>
          {options.map(option => (
            <option key={option.value} value={option.value}>
              {option.label}
            </option>
          ))}
        </select>
      )}
    />
  </FormField>
);
```

### 2. 错误处理优化

```tsx
// 全局错误处理
interface FormErrors {
  [key: string]: {
    message: string;
  };
}

const ErrorMessage = ({ errors, field }: { errors: FormErrors; field: string }) => {
  if (!errors[field]) return null;

  return (
    <div className="mt-1 text-sm text-red-600">
      {errors[field].message}
    </div>
  );
};

// 表单状态管理
const useFormState = () => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const handleSubmit = async (submitFn: () => Promise<void>) => {
    setIsSubmitting(true);
    setSubmitError(null);

    try {
      await submitFn();
      setSubmitSuccess(true);
    } catch (error) {
      setSubmitError(error.message);
      setSubmitSuccess(false);
    } finally {
      setIsSubmitting(false);
    }
  };

  return {
    isSubmitting,
    submitError,
    submitSuccess,
    handleSubmit,
  };
};
```

### 3. 表单验证规则集合

```tsx
// lib/validations.ts
import { z } from 'zod';

// 通用验证规则
export const commonValidations = {
  required: (message = '此字段为必填项') => z.string().min(1, message),
  email: (message = '请输入有效的邮箱地址') => z.string().email(message),
  phone: (message = '请输入有效的手机号') =>
    z.string().regex(/^1[3-9]\d{9}$/, message),
  password: (message = '密码至少8个字符') =>
    z.string().min(8, message),
  url: (message = '请输入有效的URL') =>
    z.string().url(message),
};

// 中国特定验证
export const chinaValidations = {
  idCard: (message = '请输入有效的身份证号') =>
    z.string().regex(/^[1-9]\d{5}(18|19|20)\d{2}(0[1-9]|1[0-2])(0[1-9]|[12]\d|3[01])\d{3}[\dXx]$/, message),
  bankCard: (message = '请输入有效的银行卡号') =>
    z.string().regex(/^\d{16,19}$/, message),
};

// 业务验证
export const businessValidations = {
  username: (message = '用户名只能包含字母、数字和下划线') =>
    z.string().regex(/^[a-zA-Z0-9_]+$/, message),
  age: (min = 18, max = 120, message = '年龄必须在18-120之间') =>
    z.number().min(min, message).max(max, message),
  price: (message = '价格必须大于0') =>
    z.number().positive(message),
};
```

## 实战示例：完整的用户管理系统表单

```tsx
// forms/UserManagementForm.tsx
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { commonValidations, businessValidations } from '../lib/validations';

const userManagementSchema = z.object({
  users: z.array(z.object({
    id: z.string().optional(),
    name: commonValidations.required('姓名不能为空'),
    email: commonValidations.email(),
    role: z.enum(['admin', 'user', 'guest'], {
      errorMap: () => ({ message: '请选择有效的角色' }),
    }),
    status: z.enum(['active', 'inactive', 'pending'], {
      errorMap: () => ({ message: '请选择有效的状态' }),
    }),
    permissions: z.array(z.string()).optional(),
  })).min(1, '至少需要一个用户'),
});

type UserManagementFormData = z.infer<typeof userManagementSchema>;

interface UserManagementFormProps {
  initialData?: UserManagementFormData;
  onSubmit: (data: UserManagementFormData) => Promise<void>;
}

function UserManagementForm({ initialData, onSubmit }: UserManagementFormProps) {
  const {
    register,
    control,
    handleSubmit,
    formState: { errors, isSubmitting },
    reset,
  } = useForm<UserManagementFormData>({
    resolver: zodResolver(userManagementSchema),
    defaultValues: initialData || {
      users: [{
        name: '',
        email: '',
        role: 'user',
        status: 'active',
        permissions: [],
      }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'users',
  });

  const onFormSubmit = async (data: UserManagementFormData) => {
    try {
      await onSubmit(data);
      reset(data);
    } catch (error) {
      console.error('提交失败:', error);
    }
  };

  return (
    <form onSubmit={handleSubmit(onFormSubmit)} className="space-y-6">
      <div className="flex justify-between items-center">
        <h2 className="text-xl font-semibold text-gray-900">用户管理</h2>
        <button
          type="button"
          onClick={() => append({
            name: '',
            email: '',
            role: 'user',
            status: 'active',
            permissions: [],
          })}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
        >
          添加用户
        </button>
      </div>

      <div className="space-y-4">
        {fields.map((field, index) => (
          <div key={field.id} className="border border-gray-200 rounded-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">用户 {index + 1}</h3>
              {fields.length > 1 && (
                <button
                  type="button"
                  onClick={() => remove(index)}
                  className="text-red-600 hover:text-red-700"
                >
                  删除用户
                </button>
              )}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  姓名 *
                </label>
                <input
                  {...register(`users.${index}.name`)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {errors.users?.[index]?.name && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.users[index]?.name?.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  邮箱 *
                </label>
                <input
                  {...register(`users.${index}.email`)}
                  type="email"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                />
                {errors.users?.[index]?.email && (
                  <p className="mt-1 text-sm text-red-600">
                    {errors.users[index]?.email?.message}
                  </p>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  角色
                </label>
                <select
                  {...register(`users.${index}.role`)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="admin">管理员</option>
                  <option value="user">用户</option>
                  <option value="guest">访客</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  状态
                </label>
                <select
                  {...register(`users.${index}.status`)}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                >
                  <option value="active">活跃</option>
                  <option value="inactive">禁用</option>
                  <option value="pending">待审核</option>
                </select>
              </div>
            </div>

            <div className="mt-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                权限
              </label>
              <div className="space-y-2">
                {['read', 'write', 'delete', 'manage'].map((permission) => (
                  <label key={permission} className="flex items-center">
                    <input
                      type="checkbox"
                      value={permission}
                      {...register(`users.${index}.permissions`)}
                      className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700">
                      {permission === 'read' && '读取'}
                      {permission === 'write' && '写入'}
                      {permission === 'delete' && '删除'}
                      {permission === 'manage' && '管理'}
                    </span>
                  </label>
                ))}
              </div>
            </div>
          </div>
        ))}
      </div>

      {errors.users && (
        <p className="text-sm text-red-600">{errors.users.message}</p>
      )}

      <div className="flex justify-end space-x-4">
        <button
          type="button"
          onClick={() => reset()}
          className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
        >
          重置
        </button>
        <button
          type="submit"
          disabled={isSubmitting}
          className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
        >
          {isSubmitting ? '保存中...' : '保存'}
        </button>
      </div>
    </form>
  );
}

export default UserManagementForm;
```

## 测试表单组件

### 1. 单元测试

```tsx
// tests/UserForm.test.tsx
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { useForm } from 'react-hook-form';
import UserForm from '../components/UserForm';

describe('UserForm', () => {
  it('应该正确渲染表单字段', () => {
    render(<UserForm onSubmit={jest.fn()} />);

    expect(screen.getByLabelText(/姓名/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/邮箱/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/密码/i)).toBeInTheDocument();
  });

  it('应该显示验证错误信息', async () => {
    const onSubmit = jest.fn();
    render(<UserForm onSubmit={onSubmit} />);

    fireEvent.click(screen.getByText(/提交/i));

    await waitFor(() => {
      expect(screen.getByText(/姓名是必填项/i)).toBeInTheDocument();
      expect(screen.getByText(/请输入有效的邮箱地址/i)).toBeInTheDocument();
      expect(screen.getByText(/密码至少8个字符/i)).toBeInTheDocument();
    });

    expect(onSubmit).not.toHaveBeenCalled();
  });

  it('应该在验证通过时调用 onSubmit', async () => {
    const onSubmit = jest.fn();
    render(<UserForm onSubmit={onSubmit} />);

    fireEvent.change(screen.getByLabelText(/姓名/i), {
      target: { value: '张三' },
    });
    fireEvent.change(screen.getByLabelText(/邮箱/i), {
      target: { value: 'zhangsan@example.com' },
    });
    fireEvent.change(screen.getByLabelText(/密码/i), {
      target: { value: 'Password123!' },
    });

    fireEvent.click(screen.getByText(/提交/i));

    await waitFor(() => {
      expect(onSubmit).toHaveBeenCalledWith({
        name: '张三',
        email: 'zhangsan@example.com',
        password: 'Password123!',
      });
    });
  });
});
```

## 下一步

掌握表单处理后，你可以继续学习：

1. **数据获取** - 学习 TanStack Query 和 SWR
2. **UI 组件库** - 学习 Radix UI 和其他组件库
3. **项目实战** - 构建完整的表单应用
4. **测试策略** - 深入学习表单测试

---

*React Hook Form 和 Zod 的组合为现代 React 应用提供了强大而灵活的表单处理解决方案。*