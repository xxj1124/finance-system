#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import db, Voucher, Account
from datetime import datetime, date

app = create_app('development')
with app.app_context():
    # 获取当前月份
    today = date.today()
    current_month_start = date(today.year, today.month, 1)
    current_month_end = date(today.year, today.month, 28)
    if today.month in [1, 3, 5, 7, 8, 10, 12]:
        current_month_end = date(today.year, today.month, 31)
    elif today.month in [4, 6, 9, 11]:
        current_month_end = date(today.year, today.month, 30)
    elif today.month == 2 and today.year % 4 == 0 and (today.year % 100 != 0 or today.year % 400 == 0):
        current_month_end = date(today.year, today.month, 29)
    
    print(f"当前月份范围: {current_month_start} 到 {current_month_end}")
    
    # 查询所有已过账的凭证
    vouchers = Voucher.query.filter(
        Voucher.date >= current_month_start,
        Voucher.date <= current_month_end,
        Voucher.status == 'posted',
        Voucher.is_deleted == False
    ).all()
    
    print(f"当前月份已过账凭证数量: {len(vouchers)}")
    
    # 打印凭证详情和收入类账户记录
    total_income = 0.0
    income_accounts = Account.query.filter_by(type='income', is_deleted=False).all()
    print(f"\\n收入类账户列表:")
    for acc in income_accounts:
        print(f"- {acc.name} ({acc.code})")
    
    print(f"\\n详细凭证记录:")
    for voucher in vouchers:
        print(f"\\n凭证 {voucher.voucher_number} ({voucher.date}) - 状态: {voucher.status}")
        print(f"凭证摘要: {voucher.summary}")
        
        voucher_income = 0.0
        for entry in voucher.entries:
            if entry.account:
                is_income = entry.account.type == 'income'
                if is_income:
                    voucher_income += float(entry.credit)
                print(f"  - {entry.account.name} ({entry.account.code}) - 借: {entry.debit}, 贷: {entry.credit} {'[收入]' if is_income else ''}")
        
        if voucher_income > 0:
            total_income += voucher_income
            print(f"  该凭证收入合计: {voucher_income}")
    
    print(f"\\n仪表盘计算的总收入: {total_income}")
    
    # 检查是否有50000元的收入记录
    print(f"\\n搜索50000元收入记录:")
    for voucher in Voucher.query.filter_by(is_deleted=False).all():
        for entry in voucher.entries:
            if entry.account and entry.account.type == 'income' and abs(float(entry.credit) - 50000.0) < 0.01:
                print(f"找到50000元收入记录:")
                print(f"  凭证: {voucher.voucher_number}")
                print(f"  日期: {voucher.date}")
                print(f"  状态: {voucher.status}")
                print(f"  摘要: {voucher.description}")
                print(f"  账户: {entry.account.name}")
                print(f"  金额: {entry.credit}")
