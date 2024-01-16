# Bilibili Collection Update

## 项目介绍
Bilibili Collection Update 是一个自动化脚本，用于从Bilibili收藏夹中识别新增视频，并将视频信息保存到Markdown文件中。这个项目利用 GitHub Actions 实现每日定时执行。

## 功能特点
- 每天自动检查指定的Bilibili收藏夹。
- 识别自上次检查以来新增的视频。
- 提取视频的标题、作者、封面图、视频创建时间和播放时长等信息。
- 将提取的信息以Markdown格式保存在年月层级的文件夹中。

## 如何使用
1. 将本项目克隆到您的GitHub仓库中。
2. 在 `.github/workflows` 目录下配置您的 GitHub Actions 工作流。
3. 根据需要调整脚本 `.github/scripts/get_video_info.py`。
    - COLLECTION_ID：指定收藏夹ID。
    - USER_AGENT：指定header中User-Agent字段的值。
4. 设置必要的环境变量或GitHub Secrets（如API密钥等）。
    - 在项目settings-Secrets and Variables中设置SESSDATA和PUSHTOKEN   
5. 监控 GitHub Actions 的运行情况，查看日志和结果。

## 工作流配置
本项目使用 GitHub Actions 定时执行脚本。以下是一个工作流配置示例：

```yaml
name: Bilibili Collection Update

on:
  schedule:
    - cron: '0 0 * * *'  # 每天UTC时间0点（北京时间上午8点）运行
jobs:
  update-collection:
    runs-on: ubuntu-latest
    env:
      SESSDATA: ${{ secrets.SESSDATA }}  # bilibili sessdata
    steps:
      - name: Checkout Repository
        uses: actions/checkout@v2
        with:
          token: ${{ secrets.PUSHTOKEN }}  # token，为执行py后的git push提供权限

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'

      - name: Install Python Dependencies
        run: |
          pip install requests

      - name: Run Bilibili Collection Update Script
        run: python get_video_info.py

      - name: Commit and Push Changes
        run: |
          git config --global user.name 'Raccoon'
          git config --global user.email '1665651288@qq.com'
          git add .
          git commit -m "Updated Bilibili Collections"
          git push
```

## TODO
1. 维护失效资源库，周级别更新
2. 提取视频cc字幕
3. 请求LLM获取视频summary
4. 基于面向对象思想重构项目
