# guanwang — 开发日志

项目路径：`E:\linlang\LinlangAgent\guanwang\linknlatch`  
记录规范：每次会话一条，包含日期、内容摘要、对话历史文件地址。

---

## 2026-07-01 | 官网从零搭建

**对话历史**：`C:\Users\崔博能\.claude\projects\e--linlang-LinlangAgent\48ff9d20-2cef-4fae-a545-7507b5ed8139.jsonl`

### 背景
阅读三份设计文档后，从零创建 LinknLatch 官方网站，目标是 Awwwards 级别的沉浸式体验。

| 设计文档 | 路径 |
|---------|------|
| 产品与技术栈提示词 | `guanwang/promt.md` |
| 视觉语言参考 | `guanwang/Visual Language Reference Prompt（Creative Direction).md` |
| 反模板指令 | `guanwang/Anti-AI Prompt.md` |

### 技术栈
Next.js 14 · React 18 · TypeScript · Tailwind CSS v3 · React Three Fiber · Three.js · Framer Motion · Lenis

### 完成内容

| # | 组件 | 说明 |
|---|------|------|
| 1 | 项目脚手架 | Next.js 14 初始化，安装全部 3D/动效依赖 |
| 2 | `app/globals.css` | Tailwind v3、CSS 变量色系（`#070B14` / `#4F9EFF` / `#7AE7FF`）、glass 工具类、noise 叠加层 |
| 3 | `app/layout.tsx` | Inter + Space Grotesk 字体、SEO meta、全局 Provider 挂载 |
| 4 | `LenisProvider` | 全局 smooth scroll 封装 |
| 5 | `CustomCursor` | 双层光标（点 + 环），lag-trail 物理感，`mix-blend-mode: difference` |
| 6 | `LoadingScreen` | 进度条动画，完成后渐出 |
| 7 | `ScrollProgress` | 顶部蓝色 glow 进度线 |
| 8 | `Navigation` | 滚动后 glassmorphism 效果，移动端汉堡菜单 |
| 9 | `ParticleField` | 6000 粒子 + 自定义 GLSL shader + 神经网络连线，鼠标斥力交互 |
| 10 | `HeroSection` | 全屏 R3F Canvas、渐变大标题、双按钮 CTA、滚动提示动画 |
| 11 | `EarthScene` | 经纬网格 + 8 条贸易航线弧线（上海→纽约/伦敦/东京/巴黎/孟买/悉尼/旧金山/新加坡），城市节点 |
| 12 | `GlobalNetwork` | 旋转地球 + 四格统计数字（80+ 国家、3000+ 品牌、$2B+ GMV、15 个办公室）|
| 13 | `ServicesSection` | 4 张玻璃 bento 卡片，3D 磁力悬停，spotlight 光效 |
| 14 | `AICore` | 呼吸 shader 球 + 3 轨道环 + 流入粒子流 |
| 15 | `AIPlatform` | AI 核心 + 4 项能力指标（98.2% 预测准确率等）|
| 16 | `CompanyStory` | 2019→2025 双语时间线，交错布局大字排版 |
| 17 | `CallToAction` | "The world's your market" 大标题 + 联系按钮 |
| 18 | `Footer` | 四栏导航 + Systems operational 脉冲指示灯 |
| 19 | `app/page.tsx` | 顺序组合全部区块 |

### 兼容性修复
- Node.js 18 → 降级 Next.js `14.2.29`（Next.js 15/16 要求 Node ≥ 20）
- Tailwind v4 → 降级至 `v3.4`（v4 oxide 原生绑定在 Node 18 下无法加载）
- `next.config.ts` → 重命名为 `next.config.mjs`（Next.js 14 不支持 `.ts` 配置）
- `THREE.Line` JSX 类型冲突 → 改用 `<primitive object={lineObj} />`
- Framer Motion `ease` 类型错误 → 数组加 `as const`

### 本地运行
```bash
cd guanwang/linknlatch
npm run dev    # http://localhost:3000
npm run build  # 生产构建验证通过 ✓
```

### 待下次会话继续
- [x] GSAP ScrollTrigger 文字遮罩揭示动画 ✓
- [x] Company Story 区块视差滚动 ✓
- [x] Services 卡片 Framer Motion stagger 入场 ✓
- [ ] 部署配置（Vercel / Nginx）
- [ ] 填入真实联系邮箱、案例数据、合作方 Logo

---

## 2026-07-01 | 动效升级 + 公司名修正

**对话历史**：`C:\Users\崔博能\.claude\projects\e--linlang-LinlangAgent\b137627a-ff42-4d44-983f-f26b0026521f.jsonl`（同一会话续写）

### 本次完成内容

| # | 改动 | 文件 |
|---|------|------|
| 1 | 公司名 `凌浪` → `淋浪`（杭州淋浪信息技术有限公司） | `HeroSection.tsx`、`layout.tsx` |
| 2 | GSAP ScrollTrigger 逐行遮罩揭示 | `CompanyStory.tsx` |
| 3 | Framer Motion useScroll + useTransform 视差 | `CompanyStory.tsx` |
| 4 | Framer Motion stagger 入场（containerVariants + cardVariants） | `ServicesSection.tsx` |

### 实现细节

**CompanyStory GSAP 揭示**
- 4 行标题各包在 `overflow:hidden` 的 `<span>` 内，内部 `<span className="line-inner">` 被 GSAP 从 `yPercent:115` 动画到 `0`
- `stagger: 0.1`，`ease: 'power3.out'`，ScrollTrigger `start: 'top 82%'`
- 在 `gsap.context()` 内注册，组件卸载时 `ctx.revert()` 清理

**CompanyStory 视差**
- `useScroll({ target: ref, offset: ['start end', 'end start'] })` 获取 section 滚动进度
- 4 个里程碑各自使用 `useTransform` 映射到不同 Y 偏移（[30,-20] / [10,-45] / [-15,35] / [45,-25] px）
- 每个里程碑提取为 `<MilestoneItem>` 子组件，在其内部调用 `useTransform`（避免 hooks-in-loop 规则违反）

**ServicesSection stagger**
- 移除 `useInView` + 手动 `inView` prop
- 父容器 `motion.div` 挂 `variants={containerVariants}` + `whileInView="visible"` + `viewport={{ once: true, margin: '-15%' }}`
- `containerVariants.visible.transition.staggerChildren: 0.12`
- 每张卡片 `motion.div` 只挂 `variants={cardVariants}`（hidden: y:60 opacity:0 → visible: y:0 opacity:1）

### 本地运行
```bash
cd guanwang/linknlatch
npm run dev    # http://localhost:3000
```

### 下次会话交接提示词

```
读 E:\linlang\LinlangAgent\guanwang\dev-log.md 恢复上下文。

项目是 LinknLatch 官方网站，路径：E:\linlang\LinlangAgent\guanwang\linknlatch
公司中文名：杭州淋浪信息技术有限公司
本地开发服务器：cd guanwang/linknlatch && npm run dev（http://localhost:3000）

动效三项已完成（GSAP逐行揭示、视差、stagger），下次优先处理：

1. 部署配置
   方案A Vercel：根目录设为 guanwang/linknlatch，自动检测 Next.js
   方案B Nginx：npm run build → .next 静态输出 → Nginx 反代 3000

2. 真实内容填充
   - 联系邮箱：填入 contact@linknlatch.com 或实际邮箱
   - 合作品牌 Logo：ServicesSection / GlobalNetwork 区块
   - Footer 社交链接

3. 可选动效补充
   - GSAP ScrollTrigger 用于 HeroSection 主标题字符逐个揭示（当前用 Framer Motion，可升级）
   - CallToAction 区块大标题遮罩揭示

完成后截图验证，更新 dev-log.md。
```

---
