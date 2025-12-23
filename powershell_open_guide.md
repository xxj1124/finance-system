# 如何在Windows系统中打开PowerShell窗口

本指南将帮助您在Windows系统中打开PowerShell窗口，以便执行GitHub代码上传指南中的命令。

## 方法一：通过开始菜单搜索（最常用）

1. 点击Windows开始按钮（通常在屏幕左下角，带有Windows徽标）
2. 在搜索框中输入 `PowerShell`
3. 从搜索结果中选择 `Windows PowerShell`

   **提示**：如果您看到 `Windows PowerShell (管理员)` 选项，对于大多数Git操作，您不需要以管理员身份运行，选择普通的 `Windows PowerShell` 即可。

## 方法二：通过运行对话框

1. 按下键盘上的 `Win + R` 组合键（Win键是带有Windows徽标的键）
2. 在打开的"运行"对话框中输入 `powershell`
3. 点击 `确定` 按钮或按下 `Enter` 键

## 方法三：通过命令提示符(CMD)转换

1. 打开命令提示符（CMD）：
   - 按下 `Win + R`，输入 `cmd`，然后按 `Enter`
   或
   - 通过开始菜单搜索 "命令提示符"

2. 在命令提示符窗口中，输入 `powershell` 并按下 `Enter` 键
3. 您将看到窗口从命令提示符切换到PowerShell

## 方法四：在特定目录中打开PowerShell（推荐）

这种方法可以直接在您的项目目录中打开PowerShell，省去了手动切换目录的步骤：

1. 打开文件资源管理器：
   - 按下 `Win + E` 组合键
   或
   - 点击任务栏上的文件资源管理器图标

2. 导航到您的项目目录：`e:\trae项目\finance`
   - 在左侧导航栏中点击 `此电脑`
   - 双击 `本地磁盘(E:)`
   - 双击 `trae项目` 文件夹
   - 双击 `finance` 文件夹

3. 在地址栏中输入 `powershell`
   - 点击文件资源管理器顶部的地址栏（显示当前路径的位置）
   - 输入 `powershell` 并按下 `Enter` 键

4. PowerShell窗口将在 `e:\trae项目\finance` 目录下打开

## 如何确认PowerShell已正确打开

当PowerShell窗口打开时，您应该能看到：
- 蓝色背景（默认主题）
- 命令提示符以 `PS` 开头，后面跟着当前工作目录
  例如：`PS E:\trae项目\finance>`

## 验证当前工作目录

如果您需要确认当前工作目录是否正确，可以执行以下命令：

```powershell
pwd
```

该命令将显示当前PowerShell窗口的工作目录。如果输出显示 `E:\trae项目\finance`，则表示您已在正确的目录中。

如果当前目录不正确，可以使用以下命令切换到目标目录：

```powershell
cd e:\trae项目\finance
```

## 下一步

成功打开PowerShell窗口后，您可以继续执行GitHub代码上传指南中的下一步命令，例如：

```powershell
git init
```

如果您在操作过程中遇到任何问题，请随时联系我们获取帮助。