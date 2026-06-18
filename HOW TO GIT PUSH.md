# Git 推送指南

> 本文档说明如何将小说项目的更新推送到GitHub，并更新在线阅读网站。

---

## 📋 前置条件

### 1. 安装 Git

**Windows**：
```bash
# 下载并安装 Git for Windows
# https://git-scm.com/download/win
```

**macOS**：
```bash
# 使用 Homebrew 安装
brew install git
```

**Linux**：
```bash
# Ubuntu/Debian
sudo apt-get install git

# CentOS/RHEL
sudo yum install git
```

### 2. 安装 GitHub CLI

**Windows**：
```bash
# 使用 winget 安装
winget install GitHub.cli

# 或者使用 Scoop 安装
scoop install gh
```

**macOS**：
```bash
# 使用 Homebrew 安装
brew install gh
```

**Linux**：
```bash
# Ubuntu/Debian
sudo apt-get install gh

# CentOS/RHEL
sudo yum install gh
```

### 3. 登录 GitHub

```bash
# 登录 GitHub 账号
gh auth login

# 按照提示选择：
# - GitHub.com
# - HTTPS
# - 浏览器登录
```

---

## 🚀 基本推送流程

### 步骤 1：进入项目目录

```bash
cd "F:\缓存\obsidian_datasql\obsidian_datasql\或许我将再逝朝花"
```

### 步骤 2：查看当前状态

```bash
# 查看文件修改状态
git status

# 查看修改内容
git diff
```

### 步骤 3：添加修改的文件

```bash
# 添加所有修改的文件
git add .

# 或者添加特定文件
git add 夏夜/夏夜/夏夜/新章节.md
```

### 步骤 4：提交修改

```bash
# 提交修改，附带描述性信息
git commit -m "添加《夏夜》新章节：第六章"

# 更详细的提交信息
git commit -m "feat: 添加《夏夜》第六章

- 新增第六章内容
- 更新网站 content.js
- 更新目录结构"
```

### 步骤 5：推送到 GitHub

```bash
# 推送到远程仓库
git push origin master

# 或者使用简写
git push
```

---

## 📝 常用 Git 命令

### 查看状态

```bash
# 查看工作区状态
git status

# 查看提交历史
git log

# 查看简洁的提交历史
git log --oneline

# 查看某个文件的修改历史
git log --follow -- 文件路径
```

### 分支管理

```bash
# 查看所有分支
git branch

# 创建新分支
git branch 新分支名

# 切换到新分支
git checkout 新分支名

# 创建并切换到新分支
git checkout -b 新分支名

# 合并分支到当前分支
git merge 分支名

# 删除分支
git branch -d 分支名
```

### 撤销操作

```bash
# 撤销工作区的修改
git checkout -- 文件路径

# 撤销暂存区的修改
git reset HEAD 文件路径

# 撤销最后一次提交（保留修改）
git reset --soft HEAD~1

# 撤销最后一次提交（丢弃修改）
git reset --hard HEAD~1
```

---

## 🔄 更新网站

### 方法 1：使用 Python 脚本

```bash
# 进入项目目录
cd "F:\缓存\obsidian_datasql\obsidian_datasql\或许我将再逝朝花"

# 运行网站生成脚本
python generate_website.py 夏夜

# 提交并推送
git add .
git commit -m "更新夏夜网站"
git push
```

### 方法 2：手动更新

如果需要手动更新网站，需要修改以下文件：

1. **content.js**：添加新章节的内容数据
2. **index.html**：更新章节统计信息

---

## 🌐 GitHub Pages 部署

### 检查 GitHub Pages 状态

```bash
# 查看 GitHub Pages 状态
gh api repos/NOTFROMCONCEN/novel-collection/pages
```

### 手动启用 GitHub Pages

```bash
# 启用 GitHub Pages
gh api repos/NOTFROMCONCEN/novel-collection/pages --method POST --input - << 'EOF'
{
  "source": {
    "branch": "master",
    "path": "/"
  }
}
EOF
```

### 访问链接

- **主页面**：https://notfromconcen.github.io/novel-collection/
- **夏夜**：https://notfromconcen.github.io/novel-collection/夏夜/website/index.html
- **2019血疫纪元**：https://notfromconcen.github.io/novel-collection/2019血疫纪元/2019血疫纪元/website/index.html
- **小黑屋**：https://notfromconcen.github.io/novel-collection/小黑屋/website/index.html
- **浮楼劫烬**：https://notfromconcen.github.io/novel-collection/浮楼劫烬/website/index.html
- **溟濛**：https://notfromconcen.github.io/novel-collection/溟濛/website/index.html

---

## 📁 目录结构说明

```
或许我将再逝朝花/
├── .git/                        # Git 仓库数据
├── README.md                    # 项目说明文档
├── HOW TO GIT PUSH.md           # 本文档
├── generate_website.py          # 网站生成脚本
├── 小说项目总览.md               # 项目总览文档
│
├── 夏夜/                        # 夏夜项目
│   ├── website/                 # 网站文件
│   │   ├── index.html           # 网站主页
│   │   ├── content.js           # 章节内容数据
│   │   ├── common.css           # 公共样式
│   │   └── utils.js             # 工具函数
│   └── 夏夜/                    # 小说内容
│       ├── 夏夜/                # 《夏夜》子故事
│       ├── 霸凌/                # 《囚鸟与画师》
│       └── 最难忘的夏天/         # 《最难忘的夏天》
│
├── 2019血疫纪元/                 # 2019血疫纪元项目
├── 小黑屋/                      # 小黑屋项目
├── 浮楼劫烬/                    # 浮楼劫烬项目
└── 溟濛/                        # 溟濛项目
```

---

## ⚠️ 注意事项

### 1. 文件编码

- 所有 Markdown 文件使用 **UTF-8** 编码
- 确保文件末尾有换行符

### 2. 文件命名

- 避免使用特殊字符（如 `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`）
- 使用中文或英文命名，避免空格（可用下划线 `_` 替代）

### 3. 提交信息规范

使用语义化的提交信息：

```bash
# 新增功能
git commit -m "feat: 添加《夏夜》新章节"

# 修复问题
git commit -m "fix: 修复网站显示问题"

# 更新文档
git commit -m "docs: 更新 README 文档"

# 重构代码
git commit -m "refactor: 重构网站生成脚本"

# 样式修改
git commit -m "style: 修改网站样式"
```

### 4. 大文件处理

- 避免提交大文件（如图片、视频）
- 如果需要提交大文件，使用 Git LFS：
```bash
# 安装 Git LFS
git lfs install

# 跟踪大文件
git lfs track "*.psd"
git lfs track "*.zip"
```

---

## 🔧 常见问题

### Q1: 推送时提示 "permission denied"

**解决方案**：
```bash
# 检查 GitHub 登录状态
gh auth status

# 重新登录
gh auth login
```

### Q2: 推送时提示 "rejected"

**解决方案**：
```bash
# 先拉取远程更新
git pull origin master

# 解决冲突后再次推送
git push origin master
```

### Q3: 如何查看远程仓库地址

```bash
# 查看远程仓库配置
git remote -v
```

### Q4: 如何修改远程仓库地址

```bash
# 修改远程仓库地址
git remote set-url origin 新地址
```

### Q5: 如何删除 Git 仓库

```bash
# 删除本地 Git 仓库
rm -rf .git

# 或者在 Windows 上
rmdir /s /q .git
```

---

## 📞 获取帮助

```bash
# Git 帮助
git --help
git commit --help
git push --help

# GitHub CLI 帮助
gh --help
gh repo --help
gh auth --help
```

---

## 📚 参考资源

- [Git 官方文档](https://git-scm.com/doc)
- [GitHub CLI 文档](https://cli.github.com/manual/)
- [GitHub Pages 文档](https://docs.github.com/en/pages)
- [Markdown 语法指南](https://www.markdownguide.org/basic-syntax/)

---

> 💡 **提示**：每次修改小说内容后，记得运行 `generate_website.py` 脚本更新网站，然后提交并推送到 GitHub。
