#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
检查现金科目(1001)的流水记录，分析负数原因
"""

import sys
import os
from datetime import datetime, date, timedelta
from decimal import Decimal

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用并创建上下文
from app import app
from app.models import db, Voucher, Account, VoucherEntry

# 创建应用上下文
app_context = app.app_context()
app_context.push()

# 获取当前月份的开始和结束日期
today = date.today()
start_date = date(today.year, today.month, 1)
end_date = date(today.year, today.month, 1) + timedelta(days=32)
end_date = end_date.replace(day=1) - timedelta(days=1)

print(f"检查期间: {start_date} 至 {end_date}")
print("=" * 60)

# 获取现金科目
cash_account = Account.query.filter_by(code='1001', is_deleted=False).first()
if not cash_account:
    print("未找到库存现金科目")
    sys.exit(1)

print(f"库存现金当前余额: {cash_account.balance}")
print()

# 查询期间内所有与现金科目相关的凭证条目
# 获取所有涉及现金科目的凭证条目
entries = VoucherEntry.query.filter(
    VoucherEntry.account_code == '1001',
    VoucherEntry.voucher.has(Voucher.date >= start_date),
    VoucherEntry.voucher.has(Voucher.date <= end_date),
    VoucherEntry.voucher.has(Voucher.status == 'posted'),
    VoucherEntry.voucher.has(Voucher.is_deleted == False)
).order_by(VoucherEntry.voucher_id).all()

print(f"期间内现金科目交易数量: {len(entries)}")
print()

# 计算期初余额和交易明细
# 首先获取期初余额（月初的余额）
prev_month_end = start_date - timedelta(days=1)

# 获取月初余额的方法：计算所有截止到上月末的现金交易
prev_entries = VoucherEntry.query.filter(
    VoucherEntry.account_code == '1001',
    VoucherEntry.voucher.has(Voucher.date <= prev_month_end),
    VoucherEntry.voucher.has(Voucher.status == 'posted'),
    VoucherEntry.voucher.has(Voucher.is_deleted == False)
).all()

# 计算期初余额（现金科目是资产类，借方为正，贷方为负）
beginning_balance = Decimal('0.0')
for entry in prev_entries:
    beginning_balance += entry.debit - entry.credit

print(f"期初余额: {beginning_balance}")
print()
print("交易明细（按凭证顺序）:")
print("-" * 80)
print(f"{'凭证号':<10} {'日期':<15} {'借方':<12} {'贷方':<12} {'余额':<12}")
print("-" * 80)

current_balance = beginning_balance

for entry in entries:
    voucher = entry.voucher
    # 计算本次交易后的余额
    current_balance += entry.debit - entry.credit
    
    print(f"{voucher.voucher_number:<10} {str(voucher.date):<15} {entry.debit:<12.2f} {entry.credit:<12.2f} {current_balance:<12.2f}")

print("-" * 80)
print(f"期末余额: {current_balance}")
print()

# 检查是否有异常交易
print("异常交易检查（贷方金额大于当前可用余额）:")
print("-" * 80)
print(f"{'凭证号':<10} {'日期':<15} {'交易前余额':<15} {'贷方金额':<12} {'交易后余额':<12}")
print("-" * 80)

current_balance_check = beginning_balance

for entry in entries:
    voucher = entry.voucher
    
    # 如果是现金支出（贷方）且金额大于当前可用余额，可能导致负数
    if entry.credit > 0 and entry.credit > current_balance_check:
        print(f"{voucher.voucher_number:<10} {str(voucher.date):<15} {current_balance_check:<15.2f} {entry.credit:<12.2f} {current_balance_check - entry.credit:<12.2f}")
    
    # 更新余额
    current_balance_check += entry.debit - entry.credit