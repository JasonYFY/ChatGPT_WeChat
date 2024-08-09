#!/bin/bash
# 查找进程ID
pid=$(pgrep -f "flask")
# 检查进程是否存在
if [ -n "$pid" ]; then
    echo "进程信息："
    ps -fp $pid
else
    echo "进程不存在"
fi
