# 学生心理健康管理系统前端

Vue 3 + Vite 前端，服务于学生自助记录、心理测评、趋势观察，以及管理员风险预警、学生档案、班级管理和视频情绪会话分析。

## 运行方式

```bash
npm install
npm run dev
```

默认开发地址为 `http://localhost:5173`。Vite 会将 `/api` 代理到 `http://localhost:8000`，因此本地联调前需要先启动后端服务和数据库。

## 构建

```bash
npm run build
```

当前脚本只有 `dev`、`build`、`preview`，项目暂未配置 lint、typecheck 或单元测试脚本。

## 主要模块

- 公共入口：学校账号登录、学生注册。
- 学生端：心理工作台、个人档案、情绪识别、心理测评、识别记录、趋势观察。
- 管理员端：风险工作台、班级管理、学生档案、预警处置、识别记录、视频情绪会话分析。
- 共享结构：`components/AppShell.vue` 提供角色工作台布局，`components/PageHeader.vue` 统一页面标题，`domain/mentalHealth.js` 维护情绪、风险和格式化语义。
- API 分层：`src/api` 按 auth、classes、users、records、warnings、stats、video、questionnaire、emotion 拆分，页面不直接写 Axios 端点。

## 注意事项

- 情绪识别拍照需要浏览器摄像头权限；权限不可用时可改用图片上传。
- 视频会话分析读取后端配置的视频目录中的学生留存视频，不是实时摄像头流。
- 预警页当前后端只支持状态标记；跟进记录、责任分配和干预结案仍需要后续接口。
- 图表用于辅助观察风险和趋势，不替代专业心理评估。
