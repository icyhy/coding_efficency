# 项目架构设计文档

## 系统架构概览

本项目采用前后端分离的架构设计，前端使用Vue.js构建SPA应用，后端使用FastAPI提供RESTful API服务。

```
┌─────────────────┐    HTTP/HTTPS    ┌─────────────────┐
│                 │ ◄──────────────► │                 │
│   Vue.js 前端   │                  │  FastAPI 后端   │
│                 │                  │                 │
└─────────────────┘                  └─────────────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │                 │
                                     │  SQLite 数据库  │
                                     │                 │
                                     └─────────────────┘
                                              │
                                              ▼
                                     ┌─────────────────┐
                                     │                 │
                                     │  阿里云效 API   │
                                     │                 │
                                     └─────────────────┘
```

## 技术架构

### 前端架构

#### 技术栈
- **Vue.js 3**: 渐进式JavaScript框架
- **Element Plus**: 基于Vue 3的组件库
- **ECharts**: 数据可视化图表库
- **Pinia**: Vue 3状态管理库
- **Vue Router**: 前端路由管理
- **Axios**: HTTP客户端
- **Vite**: 构建工具

#### 目录结构
```
frontend/
├── src/
│   ├── components/          # 可复用组件
│   │   ├── common/         # 通用组件
│   │   ├── charts/         # 图表组件
│   │   └── forms/          # 表单组件
│   ├── views/              # 页面视图
│   │   ├── auth/           # 认证相关页面
│   │   ├── dashboard/      # 仪表板
│   │   ├── repository/     # 仓库管理
│   │   └── analytics/      # 数据分析
│   ├── store/              # Pinia状态管理
│   │   ├── modules/        # 状态模块
│   │   └── index.js        # 状态入口
│   ├── api/                # API调用封装
│   ├── utils/              # 工具函数
│   ├── router/             # 路由配置
│   └── assets/             # 静态资源
├── public/                 # 公共资源
└── package.json           # 依赖配置
```

### 后端架构

#### 技术栈
- **FastAPI**: 现代高性能Web框架
- **SQLAlchemy**: ORM数据库操作
- **python-jose**: JWT身份验证
- **FastAPI CORS**: 跨域资源共享
- **Requests**: HTTP请求库
- **APScheduler**: 定时任务调度
- **SQLite**: 轻量级数据库

#### 目录结构
```
backend/
├── app/
│   ├── main.py            # FastAPI应用入口
│   ├── models/             # 数据模型
│   │   ├── __init__.py
│   │   ├── user.py         # 用户模型
│   │   ├── repository.py   # 仓库模型
│   │   └── analytics.py    # 分析数据模型
│   ├── api/                # API路由
│   │   ├── __init__.py
│   │   ├── auth.py         # 认证API
│   │   ├── repository.py   # 仓库API
│   │   └── analytics.py    # 分析API
│   ├── services/           # 业务逻辑服务
│   │   ├── __init__.py
│   │   ├── auth_service.py # 认证服务
│   │   ├── git_service.py  # Git服务
│   │   └── analytics_service.py # 分析服务
│   └── utils/              # 工具函数
│       ├── __init__.py
│       ├── decorators.py   # 装饰器
│       └── helpers.py      # 辅助函数
├── config.py               # 配置文件
├── requirements.txt        # Python依赖
└── run.py                 # 应用启动文件
```

## 数据库设计

### 核心表结构

#### 用户表 (users)
- id: 主键
- username: 用户名
- email: 邮箱
- password_hash: 密码哈希
- created_at: 创建时间
- updated_at: 更新时间

#### 仓库表 (repositories)
- id: 主键
- user_id: 用户ID (外键)
- name: 仓库名称
- url: 仓库URL
- api_key: API密钥 (加密存储)
- platform: 平台类型 (yunxiao)
- is_active: 是否激活
- created_at: 创建时间
- updated_at: 更新时间

#### 提交记录表 (commits)
- id: 主键
- repository_id: 仓库ID (外键)
- commit_hash: 提交哈希
- author: 提交作者
- message: 提交信息
- additions: 新增行数
- deletions: 删除行数
- commit_date: 提交时间
- created_at: 记录创建时间

#### 合并请求表 (merge_requests)
- id: 主键
- repository_id: 仓库ID (外键)
- mr_id: 合并请求ID
- title: 标题
- author: 作者
- state: 状态
- additions: 新增行数
- deletions: 删除行数
- created_at: 创建时间
- merged_at: 合并时间

## API设计

### 认证相关
- POST /api/auth/register - 用户注册
- POST /api/auth/login - 用户登录
- POST /api/auth/refresh - 刷新Token
- GET /api/auth/profile - 获取用户信息
- PUT /api/auth/profile - 更新用户信息

### 仓库管理
- GET /api/repositories - 获取仓库列表
- POST /api/repositories - 添加仓库
- PUT /api/repositories/{id} - 更新仓库
- DELETE /api/repositories/{id} - 删除仓库
- POST /api/repositories/{id}/sync - 同步仓库数据

### 数据分析
- GET /api/analytics/commits - 获取提交统计
- GET /api/analytics/timeline - 获取时间线分析
- GET /api/analytics/contributors - 获取贡献者分析
- GET /api/analytics/efficiency - 获取效率分析

## 安全设计

### 身份验证
- 使用JWT Token进行身份验证
- Token包含用户ID和权限信息
- 设置合理的Token过期时间
- 支持Token刷新机制

### 数据安全
- API密钥使用AES加密存储
- 密码使用bcrypt哈希存储
- 所有API接口进行权限验证
- 防止SQL注入和XSS攻击

### 接口安全
- 实现请求频率限制
- 添加CORS跨域保护
- 使用HTTPS加密传输
- 输入数据验证和清理

## 性能优化

### 前端优化
- 组件懒加载
- 图片资源优化
- 代码分割和压缩
- 缓存策略

### 后端优化
- 数据库查询优化
- Redis缓存热点数据
- 异步任务处理
- 分页查询

### 数据库优化
- 合理的索引设计
- 查询语句优化
- 连接池管理
- 定期数据清理

## 部署架构

### Docker容器化
- 前端Nginx容器
- 后端FastAPI容器
- 数据库SQLite文件挂载
- Docker Compose编排

### 监控和日志
- 应用性能监控
- 错误日志收集
- 访问日志分析
- 健康检查机制

## 扩展性设计

### 模块化设计
- 插件化的Git平台支持
- 可配置的评分规则
- 灵活的报表模板
- 多租户支持预留

### 微服务演进
- 服务拆分预留接口
- 消息队列集成准备
- 分布式缓存支持
- 负载均衡配置