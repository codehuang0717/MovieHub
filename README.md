# MyMovie - 电影管理系统

一个基于 Vue 3 + Django REST Framework 的现代化电影信息管理与推荐系统，集成了 TMDB（The Movie Database）数据源，支持用户收藏、评分、评论、想看列表等完整功能。

## 🌟 功能特性

- 🎬 **电影浏览**：热门、高分、即将上映电影展示
- 🎪 **轮播首页**：大屏英雄区轮播展示精选电影
- 🔍 **智能搜索**：支持标题、演员、导演等多维度搜索
- 📁 **收藏系统**：创建多个收藏夹，管理私人/公开收藏
- ⭐ **评分评论**：1-5星评分，支持长评/短评与点赞
- 📝 **想看清单**：标记想看、在看、已看状态
- 👤 **用户系统**：注册/登录、头像上传、个人主页
- 🎭 **分类浏览**：按电影类型筛选
- 🎨 **响应式 UI**：基于 Element Plus，暗色主题
- 📱 **移动适配**：完美支持手机/平板端

## 🛠 技术栈

### 前端
- **Vue 3** + **TypeScript**
- **Vite** - 构建工具
- **Pinia** - 状态管理
- **Vue Router** - 路由管理
- **Element Plus** - UI 组件库
- **Axios** - HTTP 客户端

### 后端
- **Django 5.x** + **Django REST Framework**
- **SQLite** / **PostgreSQL**（可配置）
- **JWT** 认证
- **TMDB API** 集成
- **Django CORS Headers** 跨域支持

## 📦 快速开始

### 环境要求
- Node.js 18+
- Python 3.9+
- Git

### 1. 克隆项目
```bash
git clone https://github.com/codehuang0717/MovieHub.git
cd MyMovie
```

### 2. 后端配置

```bash
# 进入后端目录
cd backend

# 创建虚拟环境
python -m venv venv

# 激活venv虚拟环境
# Windows
venv\Scripts\activate
#当然你也可以用conda环境，这里就不说怎么配置了

# macOS / Linux
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
python manage.py migrate

# 启动后端服务
python manage.py runserver
```

### 3. 前端配置

```bash
# 1 新开一个终端，进入前端目录
cd frontend/movie-app

# 2 安装依赖
npm install
```

启动开发服务器：

```bash
npm run dev
```

## 🔧 开发配置

### VS Code 推荐插件（可选）
- Vue Language Features (Volar)
- TypeScript Vue Plugin (Volar)
- Python
- Django
- GitLens

### 端口配置
- 前端：`http://localhost:5173`
- 后端 API：`http://localhost:8000`
- Django 管理：`http://localhost:8000/admin`

### 环境变量说明

#### 前端 (.env)
```env
VITE_TMDB_API_KEY=your_tmdb_api_key
VITE_API_BASE_URL=http://localhost:8000
```

#### 后端环境变量（可选）
```bash
export DEBUG=True
export SECRET_KEY=your_secret_key_here
export TMDB_API_KEY=your_tmdb_api_key
```

## 📁 项目结构

```
MyMovie/
├── backend/                # Django 后端
│   ├── movies/            # 电影模块
│   ├── reviews/           # 评分评论模块
│   ├── users/             # 用户模块
│   ├── recommendations/    # 推荐模块
│   └── movie_recommendation/ # 项目配置
├── frontend/              # Vue 前端
│   └── movie-app/
│       ├── src/
│       │   ├── components/  # 通用组件
│       │   ├── layouts/     # 布局组件
│       │   ├── router/      # 路由配置
│       │   ├── stores/      # Pinia 状态管理
│       │   ├── views/       # 页面组件
│       │   └── main.ts      # 入口文件
│       ├── public/          # 静态资源
│       └── index.html       # HTML 模板
├── README.md              # 项目文档
└── .env.example           # 环境变量模板
```

## 🚀 部署指南

### 生产环境部署（只想本地运行的不用管）

#### 后端部署
```bash
# 1. 安装生产依赖
pip install gunicorn

# 2. 收集静态文件
python manage.py collectstatic --noinput

# 3. 使用 Gunicorn 启动
gunicorn movie_recommendation.wsgi:application \
  --bind 0.0.0.0:8000 \
  --workers 4 \
  --access-logfile -
  --error-logfile -
```

#### 前端部署
```bash
# 1. 构建生产版本
npm run build

# 2. 部署 dist/ 目录到 Web 服务器（Nginx/Apache）
npm install -g serve
serve -s dist -l 3000
```

### Nginx 配置示例
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /path/to/frontend/movie-app/dist;
        try_files $uri $uri/ /index.html;
    }
}
```

## 🔐 认证说明

- 使用 JWT Token 认证
- Token 存储在 `localStorage`
- 自动 Token 刷新机制
- 受保护路由需要登录

## 📊 数据库说明

### 核心模型
- **Movie**：电影信息（含 TMDB ID 映射）
- **User**：用户信息
- **UserProfile**：用户扩展（头像、简介）
- **Rating**：评分（1-5 星）
- **Comment**：评论（支持长评标记）
- **Collection**：收藏夹
- **Watchlist**：想看列表

### API 接口
- `GET /api/movies/` - 电影列表
- `GET /api/movies/{id}/` - 电影详情
- `POST /api/auth/login/` - 用户登录
- `POST /api/auth/register/` - 用户注册
- `GET /api/reviews/collections/` - 收藏夹列表
- `POST /api/reviews/ratings/` - 提交评分
- `POST /api/reviews/comments/` - 提交评论

## 🎨 UI/UX 特色

- 🌙 **暗色主题**：现代化深色界面
- ✨ **平滑动画**：页面切换与交互动画
- 📱 **响应式**：适配各种屏幕尺寸
- 🎬 **电影海报**：优雅的网格布局
- 🔍 **智能搜索**：实时搜索建议
- ⭐ **交互评分**：可视化评分分布

## 🤝 贡献指南

1. Fork 本项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request

## 📝 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 🙋 FAQ

### Q: 如何获取 TMDB API 密钥？
A: 访问 [TMDB Developer Portal](https://www.themoviedb.org/settings/api)，注册并获取 API Key。

### Q: 如何修改数据库？
A: 编辑 `backend/movie_recommendation/settings.py` 中的 `DATABASES` 配置。

### Q: 如何添加新电影？
A: 系统自动从 TMDB 同步数据，无需手动添加。

### Q: 为什么有些功能无法使用？
A: 确保已登录，相关功能需要用户认证。

### Q: 如何配置跨域？
A: 开发环境已配置 CORS，生产环境请在 `settings.py` 中配置 `CORS_ALLOWED_ORIGINS`。
