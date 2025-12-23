# 阿里云OpenAnolis（龙蜥版）系统部署详细步骤

## 执行环境说明

### 简化版说明（适合直接在阿里云上操作）

如果您**直接在阿里云控制台**或**通过SSH连接**到服务器后操作，您已经在**服务器环境**中了。

### 两个环境的简单区别

1. **本地环境**：您自己的电脑（如家用笔记本、办公室电脑）
   - 用途：上传文件到服务器
   - 示例：您现在正在使用的电脑

2. **服务器环境**：阿里云服务器
   - 用途：安装软件、配置系统、运行服务
   - 示例：通过阿里云控制台远程连接的环境

### 文件上传的两种方式

您需要从**本地环境**上传文件到**服务器环境**。如果您觉得复杂，可以使用**阿里云控制台的文件上传功能**：

1. 登录阿里云ECS控制台
2. 找到您的实例，点击「远程连接」
3. 选择「Workbench远程连接」
4. 连接成功后，点击顶部的「文件」按钮
5. 选择「上传文件」，选择您本地的项目文件
6. 文件会上传到服务器的`/root`目录
7. 然后使用以下命令移动到项目目录：
   ```bash
   mv /root/finance.zip /var/www/finance/
   cd /var/www/finance
   unzip finance.zip
   ```

### 命令提示符参考
- 本地Windows：`C:\Users\yourname>`
- 本地Linux/macOS：`yourname@local:~$`
- 服务器环境：`[root@iZ7xv2oxvtpwp6y3cwmb49Z ~]#`

## 1. 初始准备

### 1.1 连接到服务器
**执行环境：本地环境**

- 使用SSH工具连接到服务器：
  ```bash
  # 在本地计算机的终端/PowerShell中执行
  ssh root@8.138.228.54
  ```
- 输入您设置的服务器密码

### 1.2 更新系统
**执行环境：服务器环境**

OpenAnolis使用yum/dnf包管理器，首先更新系统：
```bash
# 更新系统包
dnf update -y

# 安装基本工具
dnf install -y wget curl vim git
```

## 2. 安装Python 3和虚拟环境

### 2.1 安装Python 3
**执行环境：服务器环境**
```bash
# 检查Python版本
dnf list python3

# 安装Python 3
dnf install -y python3 python3-pip python3-venv

# 验证安装
python3 --version
pip3 --version
```

### 2.2 创建Python虚拟环境
**执行环境：服务器环境**
```bash
# 创建项目目录
mkdir -p /var/www/finance
cd /var/www/finance

# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate

# 更新pip
pip install --upgrade pip
```

## 3. 安装和配置数据库

### 3.1 安装MySQL
**执行环境：服务器环境**
OpenAnolis使用MariaDB（MySQL的分支）：
```bash
# 安装MariaDB
dnf install -y mariadb-server mariadb

# 启动MariaDB服务
systemctl start mariadb

# 设置开机自启
systemctl enable mariadb

# 查看服务状态
systemctl status mariadb
```

### 3.2 配置MariaDB
**执行环境：服务器环境**
```bash
# 运行安全配置脚本
mysql_secure_installation
```

按照提示进行配置：
- Enter current password for root (enter for none): 直接按回车
- Switch to unix_socket authentication [Y/n]: n
- Change the root password? [Y/n]: y
  - 设置root密码
- Remove anonymous users? [Y/n]: y
- Disallow root login remotely? [Y/n]: n（允许远程登录，后续会限制IP）
- Remove test database and access to it? [Y/n]: y
- Reload privilege tables now? [Y/n]: y

### 3.3 创建数据库和用户
**执行环境：服务器环境**
```bash
# 登录MySQL
mysql -u root -p

# 创建数据库
CREATE DATABASE finance DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

# 创建用户
CREATE USER 'finance_user'@'localhost' IDENTIFIED BY 'your_strong_password';

# 授权用户
GRANT ALL PRIVILEGES ON finance.* TO 'finance_user'@'localhost';

# 刷新权限
FLUSH PRIVILEGES;

# 退出MySQL
EXIT;
```

## 4. 部署项目代码

### 4.1 获取项目代码（适用于直接在服务器上操作）
**执行环境：服务器环境**

#### 4.1.1 方法一：从本地计算机复制文件到服务器（推荐）
1. 打开您的本地计算机（不是服务器）
2. 确保本地计算机安装了SSH客户端（Windows 10/11已内置OpenSSH）
3. 打开PowerShell或命令提示符
4. 运行以下命令：

```bash
# 从本地计算机上传代码到服务器
# 确保替换为您本地的实际路径
scp -r "E:\trae项目\finance\*" root@8.138.228.54:/var/www/finance/
```

#### 4.1.2 方法二：直接在服务器上克隆代码（如果代码在GitHub上）
```bash
# 克隆项目（替换为您的GitHub仓库地址）
git clone https://github.com/your_username/finance.git .
```

#### 4.1.3 方法三：在服务器上直接下载代码文件
如果您无法从本地上传文件，也可以使用以下方法：

1. 首先在本地计算机上将项目压缩为zip文件
2. 将zip文件上传到一个临时的网络存储空间（如阿里云OSS、百度网盘等）
3. 在服务器上使用wget命令下载：

```bash
# 下载项目压缩文件
wget -O finance.zip "https://your-file-storage.com/finance.zip"

# 解压文件
unzip finance.zip

# 将解压后的文件移动到当前目录
mv finance/* .
rm -rf finance
```

### 4.2 安装项目依赖
**执行环境：服务器环境**
```bash
# 激活虚拟环境（如果尚未激活）
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 4.3 配置项目

#### 4.3.1 更新配置文件
**执行环境：服务器环境**
```bash
# 编辑配置文件
vim app/config.py
```

修改数据库配置：
```python
# 数据库配置 - 使用MariaDB
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://finance_user:your_strong_password@localhost/finance'
```

设置生产环境配置：
```python
# 安全配置
SECRET_KEY = 'your_very_secure_secret_key_here'

# 系统配置
DEBUG = False
```

#### 4.3.2 初始化数据库
**执行环境：服务器环境**
```bash
# 初始化数据库
export FLASK_APP=app
flask db init
flask db migrate
flask db upgrade

# 或者使用Python命令
python -c "from app import app, db; with app.app_context(): db.create_all()"
```

## 5. 配置Web服务器

### 5.1 安装Nginx
**执行环境：服务器环境**
```bash
# 安装Nginx
dnf install -y nginx

# 启动Nginx服务
systemctl start nginx

# 设置开机自启
systemctl enable nginx

# 查看服务状态
systemctl status nginx
```

### 5.2 配置Nginx
**执行环境：服务器环境**
```bash
# 创建Nginx配置文件
vim /etc/nginx/conf.d/finance.conf
```

添加以下配置：
```nginx
server {
    listen 80;
    server_name 8.138.228.54;  # 或您的域名

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/finance/app/static;
        expires 30d;
    }

    location /uploads {
        alias /var/www/finance/app/uploads;
        expires 30d;
    }
}
```

### 5.3 测试Nginx配置
**执行环境：服务器环境**
```bash
# 检查Nginx配置
nginx -t

# 重新加载Nginx
systemctl reload nginx
```

## 6. 安装和配置Gunicorn

### 6.1 安装Gunicorn
**执行环境：服务器环境**
```bash
# 激活虚拟环境
cd /var/www/finance
source venv/bin/activate

# 安装Gunicorn
pip install gunicorn
```

### 6.2 创建Gunicorn配置文件
**执行环境：服务器环境**
```bash
vim /var/www/finance/gunicorn_config.py
```

添加以下配置：
```python
bind = '127.0.0.1:8000'
workers = 3
worker_class = 'sync'
timeout = 30
accesslog = '/var/log/gunicorn/finance_access.log'
errorlog = '/var/log/gunicorn/finance_error.log'
pidfile = '/var/run/gunicorn/finance.pid'
```

### 6.3 创建日志和PID目录
**执行环境：服务器环境**
```bash
mkdir -p /var/log/gunicorn
mkdir -p /var/run/gunicorn
chown -R nginx:nginx /var/log/gunicorn
chown -R nginx:nginx /var/run/gunicorn
```

## 7. 使用Systemd管理Gunicorn

### 7.1 创建Systemd服务文件
**执行环境：服务器环境**
```bash
vim /etc/systemd/system/finance.service
```

添加以下内容：
```ini
[Unit]
Description=Gunicorn service for finance application
After=network.target

[Service]
User=nginx
Group=nginx
WorkingDirectory=/var/www/finance
Environment="PATH=/var/www/finance/venv/bin"
ExecStart=/var/www/finance/venv/bin/gunicorn --config /var/www/finance/gunicorn_config.py app:app
Restart=on-failure

[Install]
WantedBy=multi-user.target
```

### 7.2 设置文件权限
**执行环境：服务器环境**
```bash
# 设置项目目录权限
chown -R nginx:nginx /var/www/finance
chmod -R 755 /var/www/finance
```

### 7.3 启动并启用服务
**执行环境：服务器环境**
```bash
# 重新加载systemd配置
systemctl daemon-reload

# 启动服务
systemctl start finance

# 设置开机自启
systemctl enable finance

# 查看服务状态
systemctl status finance
```

## 8. 配置防火墙

### 8.1 检查防火墙状态
**执行环境：服务器环境**
```bash
# 检查firewalld状态
systemctl status firewalld

# 如果未运行，启动并设置开机自启
if [ $? -ne 0 ]; then
    systemctl start firewalld
    systemctl enable firewalld
fi
```

### 8.2 开放必要端口
**执行环境：服务器环境**
```bash
# 开放SSH端口
firewall-cmd --permanent --add-port=22/tcp

# 开放HTTP端口
firewall-cmd --permanent --add-port=80/tcp

# 开放HTTPS端口（如果需要）
# firewall-cmd --permanent --add-port=443/tcp

# 重新加载防火墙规则
firewall-cmd --reload

# 查看已开放的端口
firewall-cmd --list-all
```

## 9. 测试部署

### 9.1 访问网站
**执行环境：本地环境**
在浏览器中访问：
```
http://8.138.228.54
```

### 9.2 检查服务状态
**执行环境：服务器环境**
```bash
# 查看Gunicorn日志
tail -f /var/log/gunicorn/finance_error.log

# 查看Nginx日志
tail -f /var/log/nginx/error.log

# 检查服务状态
systemctl status nginx finance
```

## 10. 配置HTTPS（可选）

### 10.1 安装Certbot
**执行环境：服务器环境**
```bash
# 安装Certbot
dnf install -y epel-release
dnf install -y certbot python3-certbot-nginx
```

### 10.2 获取SSL证书
**执行环境：服务器环境**
```bash
# 替换为您的域名
certbot --nginx -d yourdomain.com -d www.yourdomain.com
```

按照提示完成证书申请过程。

### 10.3 自动续期配置
**执行环境：服务器环境**
```bash
# 测试自动续期
sudo certbot renew --dry-run

# 设置自动续期服务
echo "0 0,12 * * * root python3 -c 'import random; import time; time.sleep(random.random() * 3600)' && certbot renew --quiet" | sudo tee -a /etc/crontab > /dev/null
```

## 11. 部署完成后的维护

### 11.1 定期备份数据库
**执行环境：服务器环境**
```bash
# 创建备份脚本
vim /root/backup_db.sh
```

添加以下内容：
```bash
#!/bin/bash

# 数据库备份
BACKUP_DIR="/var/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

mysqldump -u finance_user -p'your_strong_password' finance > $BACKUP_DIR/finance_$DATE.sql

# 压缩备份文件
gzip $BACKUP_DIR/finance_$DATE.sql

# 删除7天前的备份文件
find $BACKUP_DIR -name "finance_*.sql.gz" -mtime +7 -delete
```

设置执行权限并测试：
```bash
chmod +x /root/backup_db.sh
/root/backup_db.sh
```

### 11.2 设置定时备份
**执行环境：服务器环境**
```bash
# 添加到crontab
crontab -e
```

添加以下内容（每天凌晨2点执行备份）：
```
0 2 * * * /root/backup_db.sh
```

## 12. 常见问题排查
**执行环境：服务器环境（除特别说明外）**

### 12.1 网站无法访问
- 检查Nginx服务状态：`systemctl status nginx`
- 检查Gunicorn服务状态：`systemctl status finance`
- 检查防火墙规则：`firewall-cmd --list-all`
- 检查阿里云安全组是否开放了80/443端口

### 12.2 数据库连接错误
- 检查MariaDB服务状态：`systemctl status mariadb`
- 验证数据库连接：`mysql -u finance_user -p finance`
- 检查配置文件中的数据库连接信息

### 12.3 502 Bad Gateway错误
- 检查Gunicorn服务是否运行：`systemctl status finance`
- 查看Gunicorn日志：`tail -f /var/log/gunicorn/finance_error.log`
- 检查Nginx配置中的proxy_pass地址是否正确

## 13. 服务器信息

- **IP地址**：8.138.228.54
- **实例ID**：9b0244f6f569415c85e22234e6a65076f
- **配置**：2 vCPU / 2 GiB / ESSD云盘 40 GiB
- **系统**：OpenAnolis（龙蜥版）

---

部署完成后，您的财务系统就可以在阿里云OpenAnolis服务器上稳定运行了。如果遇到任何问题，请参考常见问题排查部分或查看相关日志文件。