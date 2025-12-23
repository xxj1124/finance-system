#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查本月已过账凭证数据
"""

import sys
import os
from datetime import datetime, date, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用并创建上下文
from app import app
from app.models import db, Voucher, Account

# 创建应用上下文
app_context = app.app_context()
app_context.push()

# 获取当前月份的开始和结束日期
today = date.today()
start_date = date(today.year, today.month, 1)
end_date = date(today.year, today.month, 1) + timedelta(days=32)
end_date = end_date.replace(day=1) - timedelta(days=1)

print(f"检查期间: {start_date} 至 {end_date}")
print("=" * 50)

# 查询本月已过账凭证
try:
    vouchers = Voucher.query.filter(
        Voucher.date >= start_date,
        Voucher.date <= end_date,
        Voucher.status == 'posted',
        Voucher.is_deleted == False
    ).all()
    
    print(f"本月已过账凭证数量: {len(vouchers)}")
    print()
    
    for voucher in vouchers:
        print(f"凭证号: {voucher.voucher_number}")
        print(f"日期: {voucher.date}")
        
        # 获取所有条目
        entries = voucher.entries.all()
        print(f"条目数: {len(entries)}")
        print(f"状态: {voucher.status}")
        
        # 显示每个条目的详细信息
        print("凭证条目:")
        for entry in entries:
            account = entry.account
            account_name = account.name if account else "未知科目"
            account_code = account.code if account else "未知代码"
            account_type = account.type if account else "未知类型"
            print(f"  - {entry.id}: {account_code} {account_name} (类型: {account_type})")
            print(f"    借方: {entry.debit} | 贷方: {entry.credit}")
        print("=" * 50)
        
except Exception as e:
    print(f"查询出错: {e}")
    import traceback
    traceback.print_exc()
