# 小说仓库管理目录

> 本文件用于集中管理 NOTFROMCONCEN 账号下的小说与故事仓库。
> 当前阶段只建立索引，不改变任何仓库的所有者、Public/Private 状态、默认分支或 EdgeOne 部署配置。

## 1. 小说与故事仓库

| 作品 / 内容 | GitHub 仓库 | 可见性 | 默认分支 | 备注 |
|---|---|---:|---|---|
| 小说合集 | [novel-collection](https://github.com/NOTFROMCONCEN/novel-collection) | Public | master | 多作品合集与统一阅读入口；包含《夏夜》《2019血疫纪元》《小黑屋》《浮楼劫烬》《溟濛》 |
| 2019血疫纪元 | [Blood-Epoch](https://github.com/NOTFROMCONCEN/Blood-Epoch) | Public | main | 独立作品仓库；与合集内作品名称相同，迁移前需核对是否独立部署 |
| 夏夜 | [Summer-Night](https://github.com/NOTFROMCONCEN/Summer-Night) | Public | main | 独立作品仓库；与合集内作品名称相同，迁移前需核对是否独立部署 |
| 浮楼劫烬 | [Ashes-of-the-Floating-Tower](https://github.com/NOTFROMCONCEN/Ashes-of-the-Floating-Tower) | Public | main | 独立作品仓库；与合集内作品名称相同，迁移前需核对是否独立部署 |
| 溟濛 | [Haze](https://github.com/NOTFROMCONCEN/Haze) | Public | main | 独立作品仓库；与合集内作品名称相同，迁移前需核对是否独立部署 |
| 小黑屋 | [The-Dark-Room](https://github.com/NOTFROMCONCEN/The-Dark-Room) | Public | main | 独立作品仓库；与合集内作品名称相同，迁移前需核对是否独立部署 |
| AI 与爱情主题小说 | [novel_about_ai_and_love](https://github.com/NOTFROMCONCEN/novel_about_ai_and_love) | Public | master | 根目录包含《因果无岸》《她的眼睛》两个作品目录 |
| Stain 故事集 | [novel_Stain](https://github.com/NOTFROMCONCEN/novel_Stain) | Public | main | 根目录包含《周末》《床单》两个作品目录 |
| 短篇故事档案柜 | [stories](https://github.com/NOTFROMCONCEN/stories) | Private | main | 独立短篇故事集；暂时保持 Private，不擅自公开 |

## 2. 建议的组织结构

建议新建 GitHub Organization：`NOTFROMCONCEN-NOVELS`。

- 个人账号 `NOTFROMCONCEN`：继续存放网络工程、AI、自动化及其他个人技术项目。
- 小说组织 `NOTFROMCONCEN-NOVELS`：集中存放上表中的小说与故事仓库。
- 仓库可见性：目前为 Public 的仓库迁移后仍保持 Public；`stories` 暂时保持 Private，除非确认需要通过 EdgeOne 直接连接。
- 仓库名称和默认分支：迁移时保持不变，避免无必要地改变现有部署引用。

## 3. EdgeOne 迁移检查清单

每个仓库迁移前后逐项核对：

- [ ] 记录当前 EdgeOne Pages 项目与 GitHub 仓库的绑定关系。
- [ ] 确认 EdgeOne GitHub App 已获准访问新组织及对应仓库。
- [ ] 迁移仓库时保留原仓库名称、默认分支和可见性。
- [ ] 在 EdgeOne 中检查仓库授权、分支、构建命令、输出目录和环境变量。
- [ ] 触发一次部署，确认构建成功。
- [ ] 检查自定义域名、HTTPS、页面资源和路由。
- [ ] 验证完成后，再考虑清理旧绑定；不要提前删除 EdgeOne 项目或旧仓库。

> EdgeOne 项目名称、部署 URL、构建配置和环境变量尚未从 EdgeOne 侧核实，因此这里不填写猜测值。

## 4. 推荐 Topics

后续为小说仓库统一添加以下 GitHub Topics（按仓库内容选择）：

- `novel`
- `fiction`
- `creative-writing`
- `story`
- `edgeone-pages`

## 5. 当前边界与下一步

本目录已根据当前可访问的 GitHub 仓库清单建立。它不代表仓库已经迁移到 Organization。

下一步需要在 GitHub 网页端创建 `NOTFROMCONCEN-NOVELS`，并让 EdgeOne GitHub App 获得该组织的仓库访问权限。完成后按本目录逐个迁移和验证，优先迁移一个非关键站点作为试点。
