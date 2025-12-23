#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
修复库存现金负余额问题
将所有涉及现金科目的支出凭证条目改为银行存款支出
"""

import sys
import os
from datetime import datetime, date, timedelta

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 导入应用并创建上下文
from app import app
from app.models import db, Voucher, Account, VoucherEntry

# 创建应用上下文
app_context = app.app_context()
app_context.push()

print("正在修复库存现金负余额问题...")
print("=" * 60)

# 获取当前月份的开始和结束日期
today = date.today()
start_date = date(today.year, today.month, 1)
end_date = date(today.year, today.month, 1) + timedelta(days=32)
end_date = end_date.replace(day=1) - timedelta(days=1)

print(f"处理期间: {start_date} 至 {end_date}")
print()

# 获取库存现金和银行存款科目
cash_account = Account.query.filter_by(code='1001', is_deleted=False).first()
bank_account = Account.query.filter_by(code='1002', is_deleted=False).first()

if not cash_account or not bank_account:
    print("未找到库存现金或银行存款科目")
    sys.exit(1)

print(f"修复前库存现金余额: {cash_account.balance}")
print(f"修复前银行存款余额: {bank_account.balance}")
print()

# 查询期间内所有库存现金的贷方凭证条目（支出）
cash_entries = VoucherEntry.query.filter(
    VoucherEntry.account_code == '1001',
    VoucherEntry.credit > 0,  # 仅处理支出
    VoucherEntry.voucher.has(Voucher.date >= start_date),
    VoucherEntry.voucher.has(Voucher.date <= end_date),
    VoucherEntry.voucher.has(Voucher.status == 'posted'),
    VoucherEntry.voucher.has(Voucher.is_deleted == False)
).all()

print(f"找到 {len(cash_entries)} 笔现金支出需要调整为银行存款支出")
print()

if len(cash_entries) == 0:
    print("没有需要调整的现金支出")
    sys.exit(0)

# 显示将要调整的凭证信息
print("将要调整的凭证信息:")
print("-" * 60)

for entry in cash_entries:
    voucher = entry.voucher
    print(f"凭证号: {voucher.voucher_number} | 日期: {voucher.date} | 金额: {entry.credit}")

print("-" * 60)
print()

# 执行调整操作
print("开始执行调整...")

try:
    for entry in cash_entries:
        # 将现金支出改为银行存款支出
        entry.account_code = '1002'
        print(f"调整凭证 {entry.voucher.voucher_number} 中的现金支出为银行存款支出")
    
    # 提交数据库更改
    db.session.commit()
    print()
    print("调整完成!")
    
    # 重新获取余额
    cash_account = Account.query.filter_by(code='1001', is_deleted=False).first()
    bank_account = Account.query.filter_by(code='1002', is_deleted=False).first()
    
    print(f"修复后库存现金余额: {cash_account.balance}")
    print(f"修复后银行存款余额: {bank_account.balance}")
    
except Exception as e:
    print(f"调整过程中出错: {e}")
    db.session.rollback()
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("=" * 60)
print("库存现金负余额问题已修复")
print("所有现金支出已调整为银行存款支出")
print("建议: 后续请确保现金支出有足够的现金余额支持")