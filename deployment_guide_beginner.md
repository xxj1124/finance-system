# 阿里云OpenAnolis（龙蜥版）系统部署指南 - 初学者版

## 目录

1. [准备工作](#准备工作)
2. [连接到阿里云服务器](#连接到阿里云服务器)
3. [在服务器上安装必要的软件](#在服务器上安装必要的软件)
4. [上传项目文件到服务器](#上传项目文件到服务器)
5. [配置项目](#配置项目)
6. [启动应用](#启动应用)
7. [配置防火墙](#配置防火墙)
8. [测试访问网站](#测试访问网站)
9. [常见问题解答](#常见问题解答)

---

## 准备工作

### 1.1 本地计算机准备
- 确保您的Windows电脑可以正常上网
- 您需要知道：
  - 阿里云服务器的公网IP地址：**8.138.228.54**
  - 服务器的登录密码

### 1.2 服务器准备
- 登录阿里云控制台，确认服务器状态为「运行中」
- 确保安全组已开放以下端口：
  - 22（SSH连接）
  - 80（HTTP访问）
  - 5000（应用访问）

---

## 连接到阿里云服务器

### 2.1 方法一：使用阿里云控制台远程连接（推荐初学者）

1. 打开阿里云ECS控制台：https://ecs.console.aliyun.com/
2. 找到您的服务器实例（IP：8.138.228.54）
3. 点击「远程连接」按钮
4. 选择「Workbench远程连接」
5. 输入您的服务器登录密码
6. 点击「确定」连接

连接成功后，您会看到一个黑色的命令行界面，这就是服务器的操作系统界面。

### 2.2 方法二：使用本地SSH客户端连接

如果您想使用本地工具连接：

1. 下载并安装PuTTY：https://www.putty.org/
2. 打开PuTTY
3. 在「Host Name」中输入：`8.138.228.54`
4. 点击「Open」
5. 输入用户名：`root`
6. 输入您的服务器密码

---

## 在服务器上安装必要的软件

### 3.1 更新系统

在服务器的命令行中，执行以下命令更新系统：

```bash
dnf update -y
dnf install -y wget curl vim git unzip
```

### 3.2 安装Python 3

执行以下命令安装Python 3：

```bash
dnf install -y python3 python3-pip python3-venv
echo "Python版本："
python3 --version
echo "pip版本："
pip3 --version
```

### 3.3 安装SQLite

项目使用SQLite数据库，执行以下命令安装：

```bash
dnf install -y sqlite sqlite-devel
echo "SQLite版本："
sqlite3 --version
```

---

## 上传项目文件到服务器

### 4.1 方法一：使用阿里云控制台文件上传（推荐初学者）

1. 在Workbench远程连接界面顶部，点击「文件」按钮
2. 选择「上传文件」
3. 在弹出的窗口中，点击「选择文件」
4. 找到您本地的项目文件：`E:\trae项目\finance\`
5. 选择所有文件和文件夹，点击「上传」

文件会自动上传到服务器的`/root`目录下。

### 4.2 方法二：使用压缩包上传（备选）

1. 在本地计算机上，将`E:\trae项目\finance\`文件夹压缩为zip文件
2. 使用控制台的文件上传功能上传这个zip文件
3. 在服务器命令行中执行：

```bash
# 创建项目目录
mkdir -p /var/www/finance

# 解压文件
cd /var/www
unzip /root/finance.zip

# 如果解压后有嵌套目录，移动到正确位置
mv /var/www/finance/* /var/www/finance
```

---

## 配置项目

### 5.1 进入项目目录

```bash
cd /var/www/finance
```

### 5.2 创建Python虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 5.3 安装项目依赖

```bash
# 升级pip
pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 5.4 修改配置文件

执行以下命令修改配置文件：

```bash
vim app/config.py
```

在打开的编辑器中：
1. 按`i`键进入编辑模式
2. 将第8行的SQLite路径修改为：
   ```python
   SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "finance.db")}'
   ```
3. 将第19行的DEBUG模式修改为：
   ```python
   DEBUG = False
   ```
4. 按`Esc`键退出编辑模式
5. 输入`:wq`并按回车保存退出

---

## 启动应用

### 6.1 使用Flask内置服务器启动（仅用于测试）

```bash
# 确保虚拟环境已激活
if [ -z "$VIRTUAL_ENV" ]; then
    source venv/bin/activate
fi

# 启动应用
export FLASK_APP=run.py
export FLASK_ENV=production
flask run --host=0.0.0.0 --port=5000
```

### 6.2 使用Gunicorn启动（推荐生产环境）

```bash
# 安装Gunicorn
pip install gunicorn

# 启动应用
gunicorn --bind 0.0.0.0:5000 app:app
```

### 6.3 让应用在后台运行

```bash
# 使用nohup命令让应用在后台运行
nohup gunicorn --bind 0.0.0.0:5000 app:app > finance.log 2>&1 &
```

---

## 配置防火墙

### 7.1 检查防火墙状态

```bash
systemctl status firewalld
```

### 7.2 开放必要的端口

```bash
# 开放SSH端口（22）
firewall-cmd --permanent --add-port=22/tcp

# 开放HTTP端口（80）
firewall-cmd --permanent --add-port=80/tcp

# 开放应用端口（5000）
firewall-cmd --permanent --add-port=5000/tcp

# 重新加载防火墙规则
firewall-cmd --reload

# 查看已开放的端口
firewall-cmd --list-all
```

---

## 测试访问网站

### 8.1 使用浏览器访问

在您的本地计算机上，打开浏览器并访问：

```
http://8.138.228.54:5000
```

如果一切正常，您应该能看到应用的登录页面。

### 8.2 检查应用日志

```bash
# 查看应用日志
tail -f finance.log
```

---

## 常见问题解答

### 9.1 无法连接到服务器

**问题**：使用Workbench连接时提示密码错误

**解决方法**：
1. 确认您输入的是服务器的登录密码
2. 登录阿里云控制台，点击「实例ID」→「重置实例密码」
3. 重置密码后，等待1-2分钟再尝试连接

### 9.2 无法上传文件

**问题**：使用控制台上传文件失败

**解决方法**：
1. 确保文件大小不超过限制（一般不超过1GB）
2. 尝试将文件压缩为zip格式后再上传
3. 尝试使用其他浏览器上传

### 9.3 应用启动失败

**问题**：执行启动命令后出现错误

**解决方法**：
1. 检查是否激活了虚拟环境
2. 检查依赖是否安装完整：`pip list`
3. 查看应用日志：`tail -f finance.log`

### 9.4 无法访问网站

**问题**：浏览器无法连接到网站

**解决方法**：
1. 检查服务器防火墙是否开放了5000端口
2. 检查安全组是否开放了5000端口
3. 检查应用是否正在运行：`ps aux | grep gunicorn`

---

## 后续维护

### 10.1 重启应用

```bash
# 查找应用进程ID
ps aux | grep gunicorn

# 终止进程
kill <进程ID>

# 重新启动
nohup gunicorn --bind 0.0.0.0:5000 app:app > finance.log 2>&1 &
```

### 10.2 备份数据库

```bash
# 复制数据库文件到备份目录
mkdir -p /var/www/backup
cp /var/www/finance/finance.db /var/www/backup/finance_$(date +%Y%m%d_%H%M%S).db
```

---

## 联系支持

如果您在部署过程中遇到任何问题，可以：
1. 查看阿里云官方文档：https://help.aliyun.com/product/25365.html
2. 在阿里云控制台提交工单
3. 寻求技术人员帮助

祝您部署成功！🎉