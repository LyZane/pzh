# 片仔癀健康·沛呼吸 30 秒 TVC 创意案展示站

本仓库是「片仔癀健康·沛呼吸 草本清润含片糖」30 秒 TVC 八版创意案的展示网站，通过 GitHub Pages 发布。

- 线上地址：<https://lyzane.github.io/pzh/>
- 内容来源：`source/` 下的创意方案 Markdown（产品分析、创作方法论、A–H 八版分镜脚本与即梦 Seedance 2.0 提示词）
- 构建产物：单文件静态页 `index.html`（内嵌 CSS/JS，请勿手工编辑）

## 目录结构

```
.
├── build_site.py   # 网站构建器：解析 source/*.md → 渲染 index.html（仅标准库，无第三方依赖）
├── index.html      # 构建产物，已提交
├── source/         # 创意方案 Markdown（网站的唯一内容来源）
└── assets/         # 页面引用的图片/视频素材（帧截图、包装与糖体参考图、样片 mp4）
```

## 构建

```bash
python3 build_site.py
```

成功时输出 `OK -> .../index.html (xx KB), versions: ['A', ..., 'H']`。构建后用浏览器直接打开 `index.html` 即可预览。

注意：`build_site.py` 对 Markdown 格式有强契约依赖（版本标题正则、各字段小节格式等），改内容前先阅读脚本开头的解析逻辑；版本的名称 / Slogan / 渠道等元数据硬编码在脚本的 `META` 字典中。

## 部署

推送到 `main` 分支即触发 GitHub Pages 部署（Source: Deploy from a branch，`main` / `(root)`）。仓库根目录的 `.nojekyll` 用于跳过 Jekyll 处理，直接按静态文件发布。

## 内容合规

产品为普通食品（压片糖果），方案与页面文案只允许「清凉、舒缓、甘润、清润」等体验性表达，不得出现化痰、止咳、治疗等功效宣称。
