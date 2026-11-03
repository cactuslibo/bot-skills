---
name: 网页设计
description: 维护和修改个人学术网站（静态 HTML + Bootstrap，托管在 GitHub Pages、自定义域名），包括内容更新、手机适配、访客地图、DNS/HTTPS 排查。
---

# 网页设计 SKILL

## 用途
帮用户维护一个静态学术个人网站（Home / Research / Publications / People / Teaching 五个页面）：改内容、改样式、做手机适配、加访客统计、排查域名与 HTTPS 问题，并把改动同步到 GitHub Pages。

## 触发场景
- “把我的头衔/简介/论文列表改一下”
- “手机上看排版不对 / 菜单不显示 / 字距太宽”
- “图片太大，跟另一页一样大小”
- “加个访客地图，看看谁访问过”
- “网站显示不安全 / 有时出现域名停放页”

## 硬性规则
1. 网站页面只允许英文，不能出现任何中文；和用户沟通用中文。
2. 直接改用户电脑上的原始文件（刷新就能看到），不做预览副本；改前在暂存目录留备份。
3. 推送到 GitHub（即上线）前先得到用户同意；用户已明确要求“本地和线上同步改”的改动可直接推送。
4. 文件以 UTF-8（无 BOM）写入。

## 步骤
1. **定位**：在用户电脑本地站点目录找到对应页面，读出相关片段。
2. **备份**：把原文件复制一份到暂存目录（文件名加 `.before-<改动>` 后缀）。
3. **修改**：
   - 内容改动：直接替换文本，保持现有 HTML 风格（如通讯作者标记 `<strong>Name</strong>,*`）。
   - 手机适配：每页加 viewport meta、引用 `bootstrap-responsive.css`，在 `@media (max-width:767px)` 中处理导航（仓库缺 collapse JS 时用纯 CSS 让菜单常显）、正文左对齐、标题缩小、图片 `max-width:100%`。
   - 固定尺寸图片：给图片列设固定宽度并让文字列用 margin 让位，手机端取消。
   - 访客地图：使用 MapMyVisitors 图片版嵌入（JS 版可能卡在 Loading）。
4. **本地验证**：让用户刷新确认，或自己检查文件内容。
5. **上线**：在已登录的浏览器中打开仓库 `upload/<branch>` 页面上传文件并直接提交；之后用 `curl raw.githubusercontent.com/...?x=随机数 | cmp` 与本地文件逐字节比对确认。
6. **汇报**：用中文简短告诉用户改了什么、是否已上线、需要他看什么。

## DNS / HTTPS 排查
- 检查域名 A 记录只指向 GitHub Pages 的 185.199.108–111.153，删除注册商的“Parked”记录；`www` CNAME 指向 `<user>.github.io`；关闭域名转发。
- DNS 生效后在仓库 Settings → Pages 勾选 Enforce HTTPS，必要时移除并重新添加自定义域名以触发证书签发。

## 用到的工具 / 数据源
- 用户电脑的 Shell（PowerShell）读写本地文件；共享电脑做中转和校验。
- 已登录的浏览器：GitHub（上传提交）、域名注册商（DNS）、MapMyVisitors（访客地图）。
- curl / Invoke-WebRequest 验证线上文件和资源可访问性。
