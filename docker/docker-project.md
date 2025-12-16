## 收集的docker项目

# 一款实用的个人IT工具箱——it-tools
https://hub.docker.com/r/corentinth/it-tools
开源项目：https://github.com/CorentinTh/it-tools
docker run -d --name it-tools --restart unless-stopped -p 8800:80 corentinth/it-tools:latest

# 阅读3网页版
Reading：免费小说阅读 app，支持多种源与 TTS，提供多样阅读体验。
https://hub.docker.com/r/hectorqin/reader
开源项目：https://github.com/celetor/web-yuedu3
docker run -d --restart=always \
--name=reader -e "SPRING_PROFILES_ACTIVE=prod" \
-v /docker/reader/logs:/logs -v /docker/reader/storage:/storage \
-p 9800:8080 hectorqin/reader:3.2.11

# Teemii
Teemii：实现在线漫画下载与管理，满足漫画爱好者需求。
git clone https://github.com/dokkaner/teemii.git
cd ../server
docker build -t teemii-backend .
docker run -d --name teemii-backend --network teemii-network -v teemii-data:/app/data teemii-backend
cd ../app
docker build -t teemii-frontend .
docker run -d -p 8080:80 --name teemii-frontend --network teemii-network teemii-frontend

# 1panel
https://1panel.cn/docs/installation/online_installation/
docker run -d \
--name 1panel \
-p 10086:10086 \
--restart always \
--network host \
-v /var/run/docker.sock:/var/run/docker.sock \
-v /Users/jxp/docker/debian/volumes:/var/lib/docker/volumes \
-v /Users/jxp/docker/debian/opt:/opt \
-v /Users/jxp/docker/debian/root:/root \
-v /Users/jxp/docker/debian/home:/home \
-v /Users/jxp/docker/debian/var:/var \
-e TZ=Asia/Shanghai \
moelin/1panel:latest

http://jxp:10086/entrance

# nascab
https://hub.docker.com/r/ypptec/nascab
docker run -v /Users/jiaxiaopeng/docker/nascabData:/root/.local/share/nascab \
-p 8888:80 -p 5555:90 \
--name nascab \
--network host \
-v /mnt:/mnt \
-v /media:/media \
-v /Volumes:/Volumes \
-d --log-opt max-size=10m --log-opt max-file=3 ypptec/nascab:3.5.3-arm64

# emby 开心特别版
https://hub.docker.com/r/lovechen/embyserver
docker run -d \
--name emby \
--restart unless-stopped \
-p 8096:8096 \
-p 8920:8920 \
-v /docker/emby4714/config:/config \
-v /docker/emby4714/media:/mnt/media \
-v /:/all \
lovechen/embyserver:4.7.14.0

# redis
docker run --name redis -d \
-e REDIS_PASSWORD=admin1234 \
-p 6379:6379 \
redis:7.2.6 --requirepass admin1234
docker exec -it redis redis-cli -a admin1234

# mysql
docker run --name mysql8 -v /Users/jxp/docker/mysql8/conf:/etc/mysql/conf.d \
-v /Users/jxp/docker/mysql8/data:/var/lib/mysql -e MYSQL_ROOT_PASSWORD=admin123456 -p 3306:3306 -d 
mysql:8

docker run -d \
--name mysql8 \
-p 3306:3306 \
-e MYSQL_ROOT_PASSWORD=admin123456 \
-e MYSQL_DATABASE=test \
-e MYSQL_CHARSET=utf8mb4 \
-e MYSQL_COLLATION=utf8mb4_unicode_ci \
--restart unless-stopped \
mysql:8.0 \
--character-set-server=utf8mb4 \
--collation-server=utf8mb4_unicode_ci \
--bind-address=0.0.0.0



CREATE USER 'root'@'%' IDENTIFIED BY 'admin123456'; 创建一个新的 root 用户
ALTER USER 'root'@'%' IDENTIFIED BY 'admin123456';           -- 修改任何 IP 用户的密码
GRANT ALL PRIVILEGES ON *.* TO 'root'@'%' WITH GRANT OPTION;           -- 任何 IP
FLUSH PRIVILEGES;  -- 刷新权限

CREATE DATABASE erupt CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;



# CloudBeaver 是一个基于Web的数据库管理工具
docker run -d \
--name cloudbeaver \
-p 8978:8978 \
dbeaver/cloudbeaver:latest


# elasticsearch
docker run -d \
--name es7 \
-e "ES_JAVA_OPTS=-Xms512m -Xmx1g" \
-e "discovery.type=single-node" \
-v /Users/jiaxiaopeng/docker/es7/data:/usr/share/elasticsearch/data \
-v /Users/jiaxiaopeng/docker/es7/plugins:/usr/share/elasticsearch/plugins \
-v /Users/jiaxiaopeng/docker/es7/config:/usr/share/elasticsearch/config \
-v /Users/jiaxiaopeng/docker/es7/logs:/usr/share/elasticsearch/logs \
--privileged \
--network mynet \
-p 9200:9200 \
-p 9300:9300 \
elasticsearch:7.12.1
docker cp es:/usr/share/elasticsearch/config /Users/jiaxiaopeng/docker/es7
安装分词器
docker exec -it es7 bash
cd /usr/share/elasticsearch/bin
./elasticsearch-plugin  install https://release.infinilabs.com/analysis-ik/stable/elasticsearch-analysis-ik-7.12.1.zip

docker pull docker.1ms.run/elastic/elasticsearch:8.18.1
docker run -d --name es8 \
--net mynet \
-p 9200:9200 -p 9300:9300 \
-e "ES_JAVA_OPTS=-Xms512m -Xmx1g" \
-e "discovery.type=single-node" \
-e "xpack.security.enabled=false" \
-v /Users/jiaxiaopeng/docker/es8/data:/usr/share/elasticsearch/data \
-v /Users/jiaxiaopeng/docker/es8/plugins:/usr/share/elasticsearch/plugins \
-v /Users/jiaxiaopeng/docker/es8/config:/usr/share/elasticsearch/config \
-v /Users/jiaxiaopeng/docker/es8/logs:/usr/share/elasticsearch/logs \
docker.elastic.co/elasticsearch/elasticsearch:8.18.1

# 下载分词器并赋值到plugins目录执行
https://release.infinilabs.com/analysis-ik/stable/
docker exec -it es8 bash

./bin/elasticsearch-plugin install https://release.infinilabs.com/analysis-ik/stable/elasticsearch-analysis-ik-8.18.1.zip
docker restart es8 

docker pull docker.elastic.co/kibana/kibana:8.18.1

docker run -d \
--name kibana8 \
--network mynet \
-p 5601:5601  \
-e ELASTICSEARCH_HOSTS=http://es8:9200 \
docker.elastic.co/kibana/kibana:8.18.1

# meilisearch

docker run -it -d \
-p 7700:7700 \
-v /Users/jiaxiaopeng/docker/meili/data:/meili_data \
-e MEILI_MASTER_KEY=R5T5WDon_QrPqhFK97NgGlTVa81iuVlN44TMLiClTTg \
--name meili \
getmeili/meilisearch:v1.15

# kibana
docker run -d \
--name kibana \
-e ELASTICSEARCH_HOSTS=http://es7:9200 \
--network=mynet \
-p 5601:5601  \
kibana:7.12.1

容器在同一个网络，因此可以用容器名直接访问

# javaSP java刮削
https://github.com/Yuukiy/JavSP.git
docker run -it -d \
--network="host" \
-v /docker/javsp/media:/media \
-v  /docker/javsp/data:/app/config.yml \
ghcr.io/yuukiy/javsp:master

# ikaros绅士刮削器
https://hub.docker.com/r/suwmlee/ikaros
https://github.com/Suwmlee/ikaros
docker run -d \
--name=ikaros \
-e PUID=0 \
-e PGID=0 \
-e TZ=Asia/Shanghai \
-p 12346:12346 \
-v /path/to/media:/media \
-v /path/to/data:/app/data \
--restart unless-stopped \
suwmlee/ikaros:lates

# 代替MovieDataCapture的电影数据抓取器
xxxsen/yamdc:latest
https://github.com/xxxsen/yamdc

# Stash
可以刮削视频，图片
https://github.com/stashapp/stash

docker run -d \
--name stash \
--restart unless-stopped \
--network bridge \
-p 9909:9999 \
--log-driver "json-file" \
--log-opt max-file=10 \
--log-opt max-size=2m \
-e STASH_STASH=/data/ \
-e STASH_GENERATED=/generated/ \
-e STASH_METADATA=/metadata/ \
-e STASH_CACHE=/cache/ \
-e STASH_PORT=9999 \
-v /etc/localtime:/etc/localtime:ro \
-v /Users/jiaxiaopeng/docker/crash/config:/root/.stash \
-v /Users/jiaxiaopeng/docker/crash/data:/data \
-v /Users/jiaxiaopeng/docker/crash/metadata:/metadata \
-v /Users/jiaxiaopeng/docker/crash/cache:/cache \
-v /Users/jiaxiaopeng/docker/crash/blobs:/blobs \
-v /Users/jiaxiaopeng/docker/crash/generated:/generated \
stashapp/stash:latest

配置文件位置：
/root/.stash/config.yml
Stash 库目录
数据库文件路径
/root/.stash/stash-go.sqlite
二进制数据目录
/root/.stash/blobs

# 削刮海报的神器--metatube

docker pull ghcr.io/metatube-community/metatube-server:latest
数据库模式(推荐)：
docker run -d -p 8080:8080 -v $PWD/config:/config --name metatube ghcr.io/metatube-community/metatube-server:latest -dsn /config/metatube.db

# exatorrent
exatorrent 是用Go编写的优雅的BitTorrent客户端。
https://github.com/varbhat/exatorrent?tab=readme-ov-file
Adding Admin user with username "adminuser" and password "adminpassword"
docker run -d --name exatorrent -p 9500:5000 -p 42069:42069 \
-v /Users/jiaxiaopeng/docker/exatorrent:/exa/exadir \
-e EXATORRENT_ADMIN_USER=adminuser \
-e EXATORRENT_ADMIN_PASSWORD=adminpassword \
ghcr.io/varbhat/exatorrent:latest

# Erupt
https://www.erupt.xyz/#!/doc

# kkFileView是一个万能的在线预览开源项目

# MinIO
mkdir -p /minio/{data,config} && chmod -R 755 /minio
docker pull minio/minio:RELEASE.2025-04-22T22-12-26Z
// 最后一个完整功能版本‌
docker run -d \
--name minio \
--restart=always \
-p 9000:9000 \
-p 9001:9001 \
-v /Users/jiaxiaopeng/docker/minio/data:/data \
-v /Users/jiaxiaopeng:/d \
-v /Users/jiaxiaopeng/docker/minio/config:/root/.minio \
-e "MINIO_ROOT_USER=admin" \
-e "MINIO_ROOT_PASSWORD=Jiaxiaopeng@StrongPassword123" \
-e "TZ=Asia/Shanghai" \
-e "MINIO_BROWSER=on" \
minio/minio:RELEASE.2025-04-22T22-12-26Z \
server /data \
--console-address ":9001"

// 最后一个文件系统存储的版本,可通过域名+localhost:9000/pictures/11.jpg直接访问
docker run -d \
--name minio \
-p 9000:9000 \
-p 9001:9001 \
--restart=always \
-v /Users/jiaxiaopeng/docker/minio/data:/data \
-v /Users:/home \
-e "MINIO_ACCESS_KEY=myminioadmin" \
-e "MINIO_SECRET_KEY=myminioadmin" \
minio/minio:RELEASE.2022-05-26T05-48-41Z \
server /data \
--console-address ":9001"



# rustfs
https://github.com/rustfs
run -d -p 9000:9000 -p 9001:9001 -v /Users/jiaxiaopeng/docker/rustfs/data:/data quay.io/rustfs/rustfs

# r-nacos是一款使用rust实现的nacos服务
https://github.com/nacos-group/r-nacos

docker run --name mynacos -e RNACOS_CONSOLE_ENABLE_CAPTCHA=false \
-e RNACOS_ENABLE_NO_AUTH_CONSOLE=true \
-v /Users/jxp/docker/rnacos/config:/io:rw \
-p 8848:8848 -p 9848:9848 -p 10848:10848 -d qingpan/rnacos:stable

# nginx
docker cp nginx:/etc/nginx/nginx.conf /Users/jxp/docker/nginx/nginx.conf
docker cp nginx:/etc/nginx/conf.d /Users/jxp/docker/nginx/conf.d
docker cp nginx:/usr/share/nginx/html /Users/jxp/docker/nginx/html
docker rm -f nginx

docker run --name nginx -m 200m -p 80:80 \
-v /Users/jxp/docker/nginx/nginx.conf:/etc/nginx/nginx.conf \
-v /Users/jxp/docker/nginx/conf.d:/etc/nginx/conf.d \
-v /Users/jxp/docker/nginx/html:/usr/share/nginx/html \
-v /Users/jxp/docker/nginx/log:/var/log/nginx \
-e TZ=Asia/Shanghai \
--restart=always \
--privileged=true -d nginx


# liteflow
LiteFlow是一个轻量且强大的国产规则引擎框架
# AviatorScript
AviatorScript 是一门高性能、轻量级寄宿于 JVM （包括 Android 平台）之上的脚本语言。
# radar开源的风控项目
https://gitee.com/freshday/radar


# 1panel
docker run -d \
--name 1panel \
-p 10086:10086 \
--restart always \
--network host \
-v /var/run/docker.sock:/var/run/docker.sock \
-v /Users/jxp/docker/1panel/volumes:/var/lib/docker/volumes \
-v /Users/jxp/docker/1panel/opt:/opt \
-v /Users/jxp/docker/1panel/root:/root \
-v /Users/jxp/docker/1panel/home:/home \
-e TZ=Asia/Shanghai \
moelin/1panel:latest

http://jxp:10086/entrance

# LocalSend
LocalSend 是一个自由、开源的应用程序，允许你在本地网络上安全地与附近设备分享文件和消息，无需互联网连接。
https://github.com/localsend/localsend

# input-leap
Input Leap 是一款模拟 KVM 切换器功能的软件，从历史上看，KVM 切换器允许您使用单个键盘和鼠标来控制多台计算机。
所有共享键盘和鼠标的机器上都需要安装 Input Leap。
https://github.com/input-leap/input-leap

# memos
一款清爽的轻量级备忘录中心。
https://github.com/usememos/memos
docker run -d --name memos -p 5230:5230 -v /Users/jiaxiaopeng/docker/memos/:/var/opt/memos neosmemo/memos:stable

# Melody
网易云-音乐精灵，旨在帮助你更好地管理音乐。目前的主要能力是帮助你将喜欢的歌曲或者音频上传到音乐平台的云盘。
docker run -d -p 5566:5566 --name melody -v /Users/jiaxiaopeng/Music:/Users/jiaxiaopeng/Music -v \
/Users/jiaxiaopeng/docker/melody/melody-profile:/app/backend/.profile foamzou/melody:latest

#  flomo浮墨笔记（Web、Android、iOS等）


# music-tag-web
https://github.com/xhongc/music-tag-web
docker run -d -p 8002:8002 -v /path/to/your/music:/app/media -v /path/to/your/config:/app/data --restart=always xhongc/music_tag_web:latest

# Musicn：用于下载 mp3 音乐，方便用户获取所需音频文件
https://github.com/zonemeen/musicn

# Termux
Termux 是一款Android 终端模拟器和 Linux 环境应用，无需 root 权限或设置即可直接使用
https://termux.dev/en/

# UserLAnd
在 Android 上运行 Linux 发行版或应用程序的最简单方法。
https://github.com/CypherpunkArmory/UserLAnd


docker run -d --name gopeed --restart always -p 6600:9999 -v /Users/jiaxiaopeng/docker/gopeed/download:/download liwei2633/gopeed:v1.6.7

# Pingora正式开源：超强的Nginx替代品，每秒可处理4000万请求
https://github.com/cloudflare/pingora


# Apache Pulsar  下一代消息队列
docker pull apachepulsar/pulsar:3.3.5


docker run -d \
--name pulsar \
-p 6650:6650 \    # Broker 通信端口
-p 8650:8080 \    # Admin 控制台端口
--mount source=pulsardata,target=/Users/jiaxiaopeng/docker/pulsar/data \  # 数据持久化‌:ml-citation{ref="1,6" data="citationList"}
--mount source=pulsarconf,target=/Users/jiaxiaopeng/docker/pulsar/conf \  # 配置持久化‌:ml-citation{ref="1,6" data="citationList"}
apachepulsar/pulsar \
bin/pulsar standalone  # 启动单机模式‌:ml-citation{ref="1,8" data="citationList"}

docker ps -a | grep pulsar  # 检查容器运行状态‌:ml-citation{ref="1,8" data="citationList"}


docker run -d \
--name pulsar \
-p 6650:6650 \
-p 8080:8080 \
-v /Users/jiaxiaopeng/docker/pulsar/data:/pulsar/data \
-v /Users/jiaxiaopeng/docker/pulsar/conf:/pulsar/conf \
apachepulsar/pulsar:3.3.5 \
bin/pulsar standalone

docker cp pulsar:/pulsar/conf /Users/jiaxiaopeng/docker/pulsar/conf


# easyvoice
docker run -d -p 3000:3000 -v /Users/jiaxiaopeng/docker/easyvoice/audio:/app/audio cosincox/easyvoice:latest
https://github.com/cosin2077/easyVoice

# Blade：一款追求简约、高效的 Web 框架，基于 Java8 + Netty4。
https://github.com/lets-blade/blade

# Javalin：一个轻量级的 Web 框架，同时支持 Java 和 Kotlin，被微软、红帽、Uber 等公司使用。
https://github.com/javalin/javalin

# 数字人Heygem

# 文本语音互转chattts

# any-listen web听歌服务
https://github.com/any-listen/any-listen
docker run -d --name listen -p 9500:9500 lyswhut/any-listen-web-server:latest

docker run -d --name listen --volume=/Users/jiaxiaopeng/docker/listen/music:/music \ 
--volume=/Users/jiaxiaopeng/docker/listen/data:/server/data -p 9500:9500 lyswhut/any-listen-web-server:latest



# localai
docker run -ti -d --name local-ai -p 8080:8080 localai/localai:latest-cpu

docker run -ti -d --name local-ai -p 8080:8080 localai/localai:master-aio-cpu


# easy-gate Easy Gate 是一款简易的 Web 应用程序，旨在作为您自托管基础设施的中心枢纽。
https://github.com/wiredlush/easy-gate
docker run -d --name=easy-gate \
-p 8080:8080 \
--network mynet \
-v /Users/jiaxiaopeng/docker/gate/easy-gate.json:/etc/easy-gate/easy-gate.json \
--restart unless-stopped \
wiredlush/easy-gate:2.0.3

# Homer 是一个简单而强大的个人主页生成器，适合用来展示你的各种服务和链接。
docker run -d \
--name homer \
-p 8080:8080 \
-v ${PWD}/assets:/www/assets \
b4bz/homer:latest

# Filebrowser：在线文件管理器
docker run -d \
--name filebrowser \
-v $PWD/filebrowser:/srv \
-p 80:80 \
filebrowser/filebrowser


# streamdock电视网页直播
docker run -d --name streamdock --network host --restart unless-stopped ghcr.io/limmer55/streamdock:latest

# torrserver 免下载秒播
https://github.com/yourok/TorrServer
docker run --rm -d --name torrserver -v ~/ts:/opt/ts -p 8090:8090 ghcr.io/yourok/torrserver:latest


# Lucky 动态域名+自动证书+反代，傻瓜式设置，非常不错
https://lucky666.cn/
https://github.com/gdy666/lucky?tab=readme-ov-file#docker%E4%B8%AD%E4%BD%BF%E7%94%A8
docker run -d --name lucky --restart=always -p 16601:16601 gdy666/lucky

docker run -d --name lucky --restart=always --net=host -p 16601:16601 -v /Users/jiaxiaopeng/docker/lucky/config:/goodluck gdy666/lucky


# 开源的无损音乐库playlistdl
sudo docker run -d \
--restart unless-stopped \
--name playlistdl \
-p 5045:5000 \
-v /Users/jiaxiaopeng/docker/playlistdl/data:/data \
-e ADMIN_USERNAME=admin \
-e ADMIN_PASSWORD=admin234 \
-e AUDIO_DOWNLOAD_PATH=/data \
-e CLEANUP_INTERVAL=300 \
tanner23456/playlistdl:v2




