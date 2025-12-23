# 测试报表日期筛选功能

# 登录参数
$loginParams = @{username='admin'; password='123456'}

# 创建会话
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

# 登录系统
Write-Host "正在登录系统..."
$loginResponse = Invoke-WebRequest -Uri http://127.0.0.1:5000/login -Method POST -Body $loginParams -WebSession $session -ContentType "application/x-www-form-urlencoded"
if ($loginResponse.StatusCode -ne 200) {
    Write-Host "登录失败: $($loginResponse.StatusCode)" -ForegroundColor Red
    exit 1
}
Write-Host "登录成功！" -ForegroundColor Green

# 测试日期
$today = Get-Date
$lastMonth = $today.AddMonths(-1)
$lastYear = $today.AddYears(-1)

# 测试资产负债表
Write-Host "\n=== 测试资产负债表 ==="
foreach ($date in @($lastYear, $lastMonth, $today)) {
    $dateStr = $date.ToString('yyyy-MM-dd')
    Write-Host "测试日期: $dateStr"
    
    $reportParams = @{report_date=$dateStr}
    $reportResponse = Invoke-WebRequest -Uri http://127.0.0.1:5000/report/balance_sheet -Method POST -Body $reportParams -WebSession $session -ContentType "application/x-www-form-urlencoded"
    
    if ($reportResponse.StatusCode -eq 200) {
        Write-Host "  ✅ 请求成功"
        # 检查响应中是否包含报告日期
        if ($reportResponse.Content -match $date.ToString('yyyy年MM月dd日')) {
            Write-Host "  ✅ 报告日期正确显示"
        } else {
            Write-Host "  ❌ 报告日期未正确显示" -ForegroundColor Red
        }
    } else {
        Write-Host "  ❌ 请求失败: $($reportResponse.StatusCode)" -ForegroundColor Red
    }
}

# 测试利润表
Write-Host "\n=== 测试利润表 ==="
foreach ($date in @($lastMonth, $today)) {
    $startDate = $date.AddMonths(-1).ToString('yyyy-MM-dd')
    $endDate = $date.ToString('yyyy-MM-dd')
    Write-Host "测试期间: $startDate 至 $endDate"
    
    $reportParams = @{start_date=$startDate; end_date=$endDate}
    $reportResponse = Invoke-WebRequest -Uri http://127.0.0.1:5000/report/profit_statement -Method POST -Body $reportParams -WebSession $session -ContentType "application/x-www-form-urlencoded"
    
    if ($reportResponse.StatusCode -eq 200) {
        Write-Host "  ✅ 请求成功"
        # 检查响应中是否包含报告期间
        if ($reportResponse.Content -match "编制期间") {
            Write-Host "  ✅ 报告期间正确显示"
        } else {
            Write-Host "  ❌ 报告期间未正确显示" -ForegroundColor Red
        }
    } else {
        Write-Host "  ❌ 请求失败: $($reportResponse.StatusCode)" -ForegroundColor Red
    }
}

# 测试现金流量表
Write-Host "\n=== 测试现金流量表 ==="
foreach ($date in @($lastMonth, $today)) {
    $startDate = $date.AddMonths(-1).ToString('yyyy-MM-dd')
    $endDate = $date.ToString('yyyy-MM-dd')
    Write-Host "测试期间: $startDate 至 $endDate"
    
    $reportParams = @{start_date=$startDate; end_date=$endDate}
    $reportResponse = Invoke-WebRequest -Uri http://127.0.0.1:5000/report/cash_flow -Method POST -Body $reportParams -WebSession $session -ContentType "application/x-www-form-urlencoded"
    
    if ($reportResponse.StatusCode -eq 200) {
        Write-Host "  ✅ 请求成功"
        # 检查响应中是否包含报告期间
        if ($reportResponse.Content -match "编制期间") {
            Write-Host "  ✅ 报告期间正确显示"
        } else {
            Write-Host "  ❌ 报告期间未正确显示" -ForegroundColor Red
        }
    } else {
        Write-Host "  ❌ 请求失败: $($reportResponse.StatusCode)" -ForegroundColor Red
    }
}

# 测试科目余额表
Write-Host "\n=== 测试科目余额表 ==="
foreach ($date in @($lastYear, $lastMonth, $today)) {
    $dateStr = $date.ToString('yyyy-MM-dd')
    Write-Host "测试日期: $dateStr"
    
    $reportParams = @{report_date=$dateStr}
    $reportResponse = Invoke-WebRequest -Uri http://127.0.0.1:5000/report/account_balance -Method POST -Body $reportParams -WebSession $session -ContentType "application/x-www-form-urlencoded"
    
    if ($reportResponse.StatusCode -eq 200) {
        Write-Host "  ✅ 请求成功"
        # 检查响应中是否包含报告日期
        if ($reportResponse.Content -match $date.ToString('yyyy年MM月dd日')) {
            Write-Host "  ✅ 报告日期正确显示"
        } else {
            Write-Host "  ❌ 报告日期未正确显示" -ForegroundColor Red
        }
    } else {
        Write-Host "  ❌ 请求失败: $($reportResponse.StatusCode)" -ForegroundColor Red
    }
}

Write-Host "\n=== 所有测试完成 ==="
