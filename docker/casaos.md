# arm小主机安装完armbian之后
sudo apt update
apt install -y curl vim sudo wget
# 一键换源
bash <(curl -sSL https://linuxmirrors.cn/main.sh)
# 一键安装CasaOS
curl -fsSL https://get.casaos.io | sudo bash
# 添加一个普通用户
useradd admin
usermod -aG sudo admin  #将用户加入 sudo 组
su - admin #切换用户
# 为用户（admin需和上边的用户名保持一致）添加smb密码
smbpasswd -a admin1234
将smb.casa.conf文件中的guest ok = Yes改为[guest ok = No]，可以禁用访客账户
# 停用Docker自动唤醒服务，关闭对 /var/run/docker.sock 的监听
systemctl stop docker.socket
# 停止Docker服务
sudo systemctl stop casaos
systemctl stop docker
# 转移Docker文件（后边的路径“/mnt/Storage1/docker”改为你在SATA硬盘创建的docker文件夹路径）
mv /var/lib/docker /mnt/Storage1/docker
# 创建软链接（中间的路径“/mnt/Storage1/docker”改为你在SATA硬盘创建的docker文件夹路径）
/var/lib/docker存储 Docker 运行所需的所有持久化数据。 /etc/docker/daemon.json存放data-root
ln -s /mnt/Storage1/docker /var/lib/docker
# 启用Docker自动唤醒服务
systemctl start docker.socket
# 启动服务
systemctl start docker
systemctl start casaos
# CasaOS第三方应用商店源
https://play.cuse.eu.org/Cp0204-AppStore-Play.zip
