#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试利润表计算逻辑
"""

import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal

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

print(f"测试期间: {start_date} 至 {end_date}")
print("=" * 60)

# 获取所有收入、费用和成本类账户
income_accounts = Account.query.filter_by(type='income', is_deleted=False).all()
expense_accounts = Account.query.filter_by(type='expense', is_deleted=False).all()
cost_accounts = Account.query.filter_by(type='cost', is_deleted=False).all()

print("收入类账户:")
for account in income_accounts:
    print(f"  {account.code} {account.name} - 余额: {account.balance}")

print("\n成本类账户:")
for account in cost_accounts:
    print(f"  {account.code} {account.name} - 余额: {account.balance}")

print("\n费用类账户:")
for account in expense_accounts:
    print(f"  {account.code} {account.name} - 余额: {account.balance}")

# 获取期间内的所有已过账凭证（排除期末结转凭证）
print(f"\n{'-'*40}")
print("查询期间内已过账凭证...")
vouchers = Voucher.query.filter(
    Voucher.date >= start_date,
    Voucher.date <= end_date,
    Voucher.status == 'posted',
    Voucher.is_deleted == False,
    ~Voucher.voucher_number.like('CLOS%')  # 排除结转凭证
).all()

print(f"找到 {len(vouchers)} 张已过账凭证")

# 收集损益类账户的代码
income_codes = [acc.code for acc in income_accounts]
cost_codes = [acc.code for acc in cost_accounts]
expense_codes = [acc.code for acc in expense_accounts]

# 计算每个科目的发生额
account_movements = {}

# 遍历所有凭证条目，汇总期间损益数据
for voucher in vouchers:
    entries = voucher.entries.all()
    for entry in entries:
        account_code = entry.account_code
        
        if account_code not in account_movements:
            account_movements[account_code] = {'debit': Decimal('0.0'), 'credit': Decimal('0.0')}
        
        account_movements[account_code]['debit'] += entry.debit
        account_movements[account_code]['credit'] += entry.credit

print(f"\n{'-'*40}")
print("期间内各账户发生额:")
for account in income_accounts + cost_accounts + expense_accounts:
    movements = account_movements.get(account.code, {'debit': Decimal('0.0'), 'credit': Decimal('0.0')})
    
    if account.type == 'income':
        # 收入类：期间发生额 = 贷方发生额 - 借方发生额
        amount = movements['credit'] - movements['debit']
    elif account.type in ['cost', 'expense']:
        # 成本费用类：期间发生额 = 借方发生额 - 贷方发生额
        amount = movements['debit'] - movements['credit']
    else:
        amount = Decimal('0.0')
    
    print(f"  {account.code} {account.name} ({account.type})")
    print(f"    借方发生额: {movements['debit']} | 贷方发生额: {movements['credit']}")
    print(f"    期间发生额: {amount}")

# 计算收入、成本、费用合计
total_income = Decimal('0.0')
total_cost = Decimal('0.0')
total_expense = Decimal('0.0')

for account in income_accounts:
    movements = account_movements.get(account.code, {'debit': Decimal('0.0'), 'credit': Decimal('0.0')})
    total_income += (movements['credit'] - movements['debit'])

for account in cost_accounts:
    movements = account_movements.get(account.code, {'debit': Decimal('0.0'), 'credit': Decimal('0.0')})
    total_cost += (movements['debit'] - movements['credit'])

for account in expense_accounts:
    movements = account_movements.get(account.code, {'debit': Decimal('0.0'), 'credit': Decimal('0.0')})
    total_expense += (movements['debit'] - movements['credit'])

# 计算利润
gross_profit = total_income - total_cost
net_profit = gross_profit - total_expense

print(f"\n{'-'*40}")
print("利润表计算结果:")
print(f"  营业收入合计: {total_income}")
print(f"  营业成本合计: {total_cost}")
print(f"  营业毛利: {gross_profit}")
print(f"  营业费用合计: {total_expense}")
print(f"  净利润: {net_profit}")
