# testkit

test-ecosystem 底座 CLI。统一管理测试技能、知识、脚本、模板和项目的个人 AI 测试生态系统。

## 安装

```bash
pipx install git+https://github.com/Huanannan93/testkit.git
# 或
pip install git+https://github.com/Huanannan93/testkit.git
```

## 快速开始

```bash
testkit init              # 初始化生态系统
testkit project create    # 创建新测试项目
testkit skill list        # 查看可用技能
```

## 命令

| 命令 | 说明 |
|------|------|
| `init` | 初始化工作区，拉取所有仓库 |
| `update` | 更新所有仓库 |
| `status` | 查看生态状态 |
| `project create` | 交互式创建新项目 |
| `project list` | 列出所有项目 |
| `skill list` | 列出可用技能 |
| `skill load <name>` | 加载技能到 AI 上下文 |
| `skill install <name>` | 安装技能到项目 |
| `knowledge search <query>` | 搜索知识库 |
| `agent list` | 列出 Agent 模板 |
