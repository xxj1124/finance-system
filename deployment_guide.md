# 阿里云平台部署详细步骤

## 1. 阿里云ECS实例创建步骤

### 1.1 登录阿里云控制台
- 访问阿里云官网：https://www.aliyun.com/
- 点击右上角"登录"按钮，使用阿里云账号登录

### 1.2 进入ECS实例创建页面
- 登录成功后，点击控制台顶部的"产品与服务"菜单
- 在搜索框中输入"ECS"，点击"云服务器ECS"进入ECS管理控制台
- 点击左侧导航栏的"实例"，然后点击"创建实例"

### 1.3 选择计费方式
- 选择"包年包月"（适合长期稳定运行的生产环境）
- 或者选择"按量付费"（适合短期测试）

### 1.4 选择区域和可用区
- 区域：选择离目标用户最近的区域，如"华东2（上海）"、"华北3（张家口）"等
- 可用区：默认选择"系统默认分配"即可

### 1.5 选择实例规格
- 点击"选择实例规格"
- 推荐选择2核4GB或4核8GB的通用型实例，如：
  - 入门级：ecs.g6.large（2核4GB）
  - 标准级：ecs.g6.xlarge（4核8GB）
- 点击"确认"选择实例规格

### 1.6 选择镜像
- 操作系统：选择"公共镜像"
- 镜像类型：选择"Ubuntu"，版本推荐"Ubuntu 22.04 LTS 64位"

### 1.7 配置网络
- 网络类型：选择"专有网络"
- 专有网络：默认创建或选择现有专有网络
- 交换机：默认创建或选择现有交换机
- 公网IP：选择"分配公网IPv4地址"
- 带宽计费方式：选择"按固定带宽"
- 带宽值：建议选择2-5Mbps（根据预计访问量调整）

### 1.8 配置存储
- 系统盘：选择"高效云盘"，大小建议40GB
- 数据盘：可根据需要添加，用于存储数据库等数据

### 1.9 配置安全组
- 选择"新建安全组"或"选择已有安全组"
- 安全组规则：
  - 开放SSH（22端口）：允许所有IP访问
  - 开放HTTP（80端口）：允许所有IP访问
  - 开放HTTPS（443端口）：允许所有IP访问

### 1.10 设置登录凭证
- 登录凭证：选择"自定义密码"
- 密码：设置一个强密码（包含大小写字母、数字和特殊字符）
- 确认密码：再次输入密码

### 1.11 实例名称和数量
- 实例名称：输入一个易于识别的名称，如"finance-server"
- 实例数量：选择"1"

### 1.12 确认订单
- 点击"下一步：确认订单"
- 勾选"我已阅读并同意《云服务器ECS服务条款》"
- 点击"创建实例"

### 1.13 获取实例信息
- 创建成功后，点击"管理控制台"查看实例
- 记录实例的公网IP地址（后续连接服务器需要使用）

## 2. 环境配置步骤

### 2.1 连接到ECS实例
- 使用SSH工具（如PuTTY、Xshell或终端）连接到ECS实例
- 命令：`ssh root@[ECS公网IP]`
- 输入设置的密码进行登录

### 2.2 更新系统
```bash
apt update && apt upgrade -y
```

### 2.3 安装Python 3和pip
```bash
apt install python3 python3-pip python3-venv -y
```

### 2.4 安装Git
```bash
apt install git -y
```

### 2.5 安装MySQL数据库
```bash
apt install mysql-server mysql-client -y

# 启动MySQL服务
systemctl start mysql
systemctl enable mysql

# 运行安全配置脚本
mysql_secure_installation
```

### 2.6 安装Nginx
```bash
apt install nginx -y

systemctl start nginx
systemctl enable nginx
```

## 3. 数据库配置（从SQLite切换到MySQL）

### 3.1 创建MySQL数据库和用户
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

### 3.2 修改项目配置文件
- 编辑`app/config.py`文件
- 修改数据库配置部分：

```python
# 数据库配置 - 使用MySQL
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://finance_user:your_strong_password@localhost/finance'
```

### 3.3 更新依赖
- 在项目根目录创建`requirements.txt`文件（如果不存在）
- 添加MySQL驱动依赖：

```
Flask==2.0.3
Flask-SQLAlchemy==2.5.1
python-docx==0.8.11
Werkzeug==2.0.3
Jinja2==3.0.3
Flask-WTF==1.0.1
WTForms==3.0.1
SQLAlchemy==1.4.49
pymysql==1.0.2
```

## 4. 项目部署步骤

### 4.1 克隆项目代码
```bash
# 创建项目目录
mkdir -p /var/www/finance
cd /var/www/finance

# 克隆项目代码（假设代码托管在GitHub上）
git clone https://github.com/your_username/finance.git .
```

### 4.2 创建虚拟环境
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 4.3 安装依赖
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4.4 配置环境变量
```bash
# 创建环境变量文件
touch .env

# 编辑环境变量文件
nano .env
```

在.env文件中添加以下内容：
```
SECRET_KEY=your_strong_secret_key
DEBUG=False
```

### 4.5 初始化数据库
```bash
# 运行数据库迁移
python -c "from app import app, db; with app.app_context(): db.create_all()"
```

## 5. 配置Web服务器（Nginx和Gunicorn）

### 5.1 安装Gunicorn
```bash
pip install gunicorn
```

### 5.2 配置Nginx
```bash
# 创建Nginx配置文件
nano /etc/nginx/sites-available/finance
```

在配置文件中添加以下内容：

```nginx
server {
    listen 80;
    server_name your_domain.com;

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

### 5.3 启用Nginx配置
```bash
# 创建符号链接
ln -s /etc/nginx/sites-available/finance /etc/nginx/sites-enabled/

# 检查Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx
```

## 6. 使用systemd管理Gunicorn进程

### 6.1 创建systemd服务文件
```bash
nano /etc/systemd/system/finance.service
```

在服务文件中添加以下内容：

```ini
[Unit]
Description=Gunicorn instance to serve finance application
After=network.target

[Service]
User=www-data
Group=www-data
WorkingDirectory=/var/www/finance
Environment="PATH=/var/www/finance/venv/bin"
ExecStart=/var/www/finance/venv/bin/gunicorn --workers 3 --bind 127.0.0.1:8000 app:app

[Install]
WantedBy=multi-user.target
```

### 6.2 启用并启动服务
```bash
# 重新加载systemd配置
systemctl daemon-reload

# 启用服务
systemctl enable finance

# 启动服务
systemctl start finance

# 检查服务状态
systemctl status finance
```

## 7. 配置域名和SSL证书

### 7.1 域名解析配置
- 登录阿里云控制台，进入"域名"管理页面
- 点击需要解析的域名，进入域名解析设置
- 添加A记录：
  - 主机记录：@（或www，根据需要）
  - 记录类型：A
  - 记录值：ECS实例的公网IP
  - TTL：默认即可

### 7.2 申请和配置SSL证书
- 进入阿里云控制台，搜索"SSL证书"
- 点击"SSL证书"服务，进入证书管理页面
- 点击"购买证书"，选择"免费证书"
- 填写证书申请信息，域名使用已解析的域名
- 提交申请，等待审核通过
- 审核通过后，下载证书文件
- 上传证书文件到服务器（如：/etc/nginx/ssl/目录）

### 7.3 配置Nginx支持HTTPS
```bash
# 编辑Nginx配置文件
nano /etc/nginx/sites-available/finance
```

修改配置文件，添加HTTPS支持：

```nginx
server {
    listen 80;
    server_name your_domain.com;
    # 重定向HTTP到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name your_domain.com;

    # SSL证书配置
    ssl_certificate /etc/nginx/ssl/your_domain.com.pem;
    ssl_certificate_key /etc/nginx/ssl/your_domain.com.key;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers 'ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384:ECDHE-ECDSA-CHACHA20-POLY1305:ECDHE-RSA-CHACHA20-POLY1305:DHE-RSA-AES128-GCM-SHA256:DHE-RSA-AES256-GCM-SHA384';

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

### 7.4 重启Nginx服务
```bash
systemctl restart nginx
```

## 8. 测试部署并验证功能

### 8.1 访问网站
- 打开浏览器，访问配置的域名（如：https://your_domain.com）
- 检查网站是否正常加载

### 8.2 测试核心功能
- 测试用户登录功能
- 测试报表生成功能
- 测试数据查询功能
- 测试系统其他功能

### 8.3 检查日志
```bash
# 查看Nginx日志
cat /var/log/nginx/access.log
cat /var/log/nginx/error.log

# 查看Gunicorn日志
journalctl -u finance
```

## 9. 部署完成后的维护

### 9.1 定期备份数据库
```bash
# 备份数据库
mysqldump -u finance_user -p finance > /var/backups/finance_$(date +%Y%m%d).sql
```

### 9.2 定期更新系统和依赖
```bash
# 更新系统
apt update && apt upgrade -y

# 更新Python依赖
cd /var/www/finance
source venv/bin/activate
pip install --upgrade pip
pip install --upgrade -r requirements.txt
```

### 9.3 监控系统性能
- 使用阿里云云监控服务监控ECS实例性能
- 设置告警规则，及时发现问题

## 10. 常见问题排查

### 10.1 网站无法访问
- 检查ECS实例是否正常运行
- 检查Nginx服务是否正常运行
- 检查Gunicorn服务是否正常运行
- 检查安全组是否开放80/443端口

### 10.2 数据库连接失败
- 检查MySQL服务是否正常运行
- 检查数据库配置是否正确
- 检查数据库用户权限是否正确

### 10.3 页面显示错误
- 检查Gunicorn日志，查看详细错误信息
- 检查Nginx日志，查看访问情况
- 确保DEBUG模式已关闭（生产环境）

---

部署完成后，您的财务系统就可以在阿里云平台上稳定运行，其他用户可以通过域名访问使用。