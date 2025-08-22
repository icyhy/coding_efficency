# 软件开发团队效率统计分析工具

## 项目概述

这是一个面向软件开发团队的效率分析平台，通过集成Git仓库API来收集和分析团队的开发数据，为团队管理者提供数据驱动的效率洞察。

## 技术栈

### 前端
- Vue.js 3
- Element Plus UI组件库
- ECharts数据可视化
- Pinia状态管理
- Vite构建工具

### 后端
- Python Flask
- SQLite数据库
- JWT身份验证
- 阿里云效API集成

## 项目结构

```
coding_efficency/
├── backend/                 # 后端Flask应用
│   ├── app/                # 应用核心代码
│   │   ├── __init__.py
│   │   ├── models/         # 数据模型
│   │   ├── api/           # API路由
│   │   ├── services/      # 业务逻辑服务
│   │   └── utils/         # 工具函数
│   ├── config.py          # 配置文件
│   ├── requirements.txt   # Python依赖
│   └── run.py            # 应用启动文件
├── frontend/               # 前端Vue应用
│   ├── src/
│   │   ├── components/    # Vue组件
│   │   ├── views/         # 页面视图
│   │   ├── store/         # Pinia状态管理
│   │   ├── api/           # API调用
│   │   └── utils/         # 工具函数
│   ├── package.json
│   └── vite.config.js
├── docs/                   # 项目文档
├── docker/                 # Docker配置
└── README.md
```

## 核心功能

1. **用户管理系统**
   - 用户注册和登录
   - 个人资料管理
   - JWT身份验证

2. **Git仓库集成**
   - 阿里云效API集成
   - 仓库列表获取
   - 监控仓库管理

3. **数据统计分析**
   - 提交统计
   - 时间分布分析
   - 代码量分析
   - 人员效率评分

4. **数据可视化**
   - 多种图表类型
   - 响应式设计
   - 交互式报表

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
python run.py
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

## 开发文档

详细的开发文档请参考 `docs/` 目录。

## 许可证

MIT License