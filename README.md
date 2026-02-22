# Yonsei Course Finder (OCR Demo)

把延世大学选课系统里“课程计划/考核方式”截图做 OCR → 提取考核占比（期中/期末/作业/出勤/团队项目…）→ 用一个网页快速筛选出符合你偏好的课程。

## Demo（线上可直接打开）
- GitHub Pages: https://111tang-no1.github.io/yonsei-course-finder/

## 你能看到什么
- 列表展示每门课的：course_id / 考核占比（解析结果）/ 原始文件 + OCR 原文片段
- 支持按「考核项」筛选（例如：只看有期末考试、作业占比 >= 20% 等）
- 支持阈值过滤（>= X%）
- 点击某一行，展开该课程 OCR 全文（用于人工快速校验）

## 本项目的输入/输出
### 输入
- OCR 文本：`data/merged/course_*.txt`（每门课合并后的 OCR 文本）
- 结构化结果：`data/course_grading.csv`
- 人工兜底：`data/override.csv`（当 OCR 解析不到或不稳定时手工补）

### 输出
- 网页展示：`web.html`
- （用于 GitHub Pages 的静态站点内容）`docs/`

## 一键本地运行（开发/调试）
1) 进入项目目录
```bash
cd ~/Projects/yonsei-course-finder
