#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from app.models import db, Account, Voucher

app = create_app()

with app.app_context():
    print("=== 特定凭证状态检查 ===")
    
    # 检查包含所有者权益操作的凭证
    target_voucher_numbers = ['VOU202512203856', 'VOU202512206295']
    
    for voucher_number in target_voucher_numbers:
        voucher = Voucher.query.filter_by(voucher_number=voucher_number).first()
        if voucher:
            print(f"\n凭证 {voucher.voucher_number}:")
            print(f"  日期: {voucher.date}")
            print(f"  状态: {voucher.status}")
            print(f"  制单人: {voucher.user_id}")
            print(f"  审核人: {voucher.approval_id}")
            print(f"  过账时间: {voucher.post_time}")
            
            # 重新计算这些凭证应该产生的余额变化
            print("\n  凭证分录:")
            for entry in voucher.entries:
                account = Account.query.filter_by(code=entry.account_code).first()
                acc_name = account.name if account else '未知科目'
                print(f"    {entry.account_code} - {acc_name}: 借 {entry.debit}, 贷 {entry.credit}")
        else:
            print(f"\n未找到凭证: {voucher_number}")
    
    # 检查所有所有者权益科目的当前状态
    print("\n=== 所有者权益科目当前状态 ===")
    equity_accounts = Account.query.filter_by(type='equity').all()
    for acc in equity_accounts:
        print(f"{acc.code} - {acc.name}: {acc.balance}")
