#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from app.models import db, Account, Voucher, VoucherEntry

app = create_app()

with app.app_context():
    print("=== 手动重新计算科目余额 ===")
    
    # 重置所有科目余额为0
    for account in Account.query.all():
        account.balance = 0.0
    db.session.commit()
    print("所有科目余额已重置为0")
    
    # 获取所有已过账的凭证
    posted_vouchers = Voucher.query.filter_by(status='posted', is_deleted=False).all()
    print(f"\n找到 {len(posted_vouchers)} 张已过账凭证")
    
    # 重新过账所有凭证
    for voucher in posted_vouchers:
        print(f"\n处理凭证 {voucher.voucher_number}:")
        for entry in voucher.entries:
            account = Account.query.filter_by(code=entry.account_code).first()
            if account:
                # 根据科目类型更新余额
                if account.type in ['asset', 'expense', 'cost']:
                    change = entry.debit - entry.credit
                    account.balance += change
                else:  # liability, equity, income
                    change = entry.credit - entry.debit
                    account.balance += change
                print(f"  {account.code} - {account.name}: {change} -> {account.balance}")
    
    db.session.commit()
    print("\n=== 重新计算完成 ===")
    
    # 显示结果
    account_types = ['asset', 'liability', 'equity', 'income', 'expense', 'cost']
    for acc_type in account_types:
        accounts = Account.query.filter_by(type=acc_type).all()
        print(f"\n{acc_type} 类型科目 ({len(accounts)}个):")
        for acc in accounts:
            print(f"  {acc.code} - {acc.name}: {acc.balance}")
