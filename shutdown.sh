#!/bin/bash
echo '停止当前项目'
sudo kill -9 `ps -ef|grep 'flask'|grep -v grep|awk '{print $2}'`
