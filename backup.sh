#!/bin/bash

# workspace目录, 末尾不用带/
workspace=/myapps/siyuan/workspace

# desktop目录
desktop=/myapps/siyuan/desktop

# 备份文件名
fileName=$(date "+%Y-%m-%d_%H.%M.%S")_full.tar.gz

# 填写你的RefreshToken
RefreshToken=********

# 上传到云盘的哪个位置
cloudPath=/我的思源备份/全量备份数据/




# 打包 排除了widgets组件目录
cd $workspace/data/ && tar  --exclude="widgets" -Pzcf $fileName *

# 上传
aliyunpan login -RefreshToken=$RefreshToken
aliyunpan upload --norapid $fileName $cloudPath

# 删除本地压缩包
rm -f $fileName
