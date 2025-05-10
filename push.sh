#!/bin/bash
# 保存为 push.sh，添加执行权限后使用：chmod +x push.sh && ./push.sh

# 配置区域 (按需修改)
REMOTE1="github"    # 第一个远程仓库名称 (如 GitHub)
REMOTE2="origin"    # 第二个远程仓库名称 (如 Gitee)
BRANCH="master"     # 要推送的分支名称

# 红色警告提示
echo -e "\033[31m⚠️  警告：强制推送会覆盖远程仓库历史记录！\033[0m"
read -p "确定要强制推送吗？(y/N) " -n 1 -r

echo    # 换行
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    exit 1
fi
git add .
git commit -m "$(date +%Y-%m-%d) 更新"
# 强制推送到第一个仓库
git push --force $REMOTE1 $BRANCH

# 推送到第二个仓库并设置上游
git push -u $REMOTE2 $BRANCH

echo "推送完成！"