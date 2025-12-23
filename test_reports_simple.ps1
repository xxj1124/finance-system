# 简化版报表测试脚本

# 登录系统
$loginParams = @{username='admin'; password='123456'}
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession

Write-Host "登录系统..."
$loginResponse = Invoke-WebRequest -Uri http://127.0.0.1:5000/login -Method POST -Body $loginParams -WebSession $session -ContentType "application/x-www-form-urlencoded"

if ($loginResponse.StatusCode -eq 200) {
    Write-Host "登录成功！"
} else {
    Write-Host "登录失败"
    exit 1
}

# 测试日期
$today = Get-Date
$lastMonth = $today.AddMonths(-1)
$todayStr = $today.ToString('yyyy-MM-dd')
$lastMonthStr = $lastMonth.ToString('yyyy-MM-dd')

# 测试资产负债表
Write-Host "\n测试资产负债表..."
$params = @{report_date=$lastMonthStr}
$response = Invoke-WebRequest -Uri http://127.0.0.1:5000/report/balance_sheet -Method POST -Body $params -WebSession $session -ContentType "application/x-www-form-urlencoded"
Write-Host "资产负债表(上月): $($response.StatusCode)"

$params = @{report_date=$todayStr}
$response = Invoke-WebRequest -Uri http://127.0.0.1:5000/report/balance_sheet -Method POST -Body $params -WebSession $session -ContentType "application/x-www-form-urlencoded"
Write-Host "资产负债表(今日): $($response.StatusCode)"

# 测试科目余额表
Write-Host "\n测试科目余额表..."
$params = @{report_date=$lastMonthStr}
$response = Invoke-WebRequest -Uri http://127.0.0.1:5000/report/account_balance -Method POST -Body $params -WebSession $session -ContentType "application/x-www-form-urlencoded"
Write-Host "科目余额表(上月): $($response.StatusCode)"

$params = @{report_date=$todayStr}
$response = Invoke-WebRequest -Uri http://127.0.0.1:5000/report/account_balance -Method POST -Body $params -WebSession $session -ContentType "application/x-www-form-urlencoded"
Write-Host "科目余额表(今日): $($response.StatusCode)"

# 测试利润表
Write-Host "\n测试利润表..."
$params = @{start_date=$lastMonthStr; end_date=$todayStr}
$response = Invoke-WebRequest -Uri http://127.0.0.1:5000/report/profit_statement -Method POST -Body $params -WebSession $session -ContentType "application/x-www-form-urlencoded"
Write-Host "利润表: $($response.StatusCode)"

# 测试现金流量表
Write-Host "\n测试现金流量表..."
$params = @{start_date=$lastMonthStr; end_date=$todayStr}
$response = Invoke-WebRequest -Uri http://127.0.0.1:5000/report/cash_flow -Method POST -Body $params -WebSession $session -ContentType "application/x-www-form-urlencoded"
Write-Host "现金流量表: $($response.StatusCode)"

Write-Host "\n测试完成！"
