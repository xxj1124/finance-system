#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from app.models import db, Account, Voucher

app = create_app()

with app.app_context():
    print("=== 会计科目检查 ===")
    
    # 检查所有科目
    all_accounts = Account.query.all()
    print(f"总科目数量: {len(all_accounts)}")
    
    # 按类型分类打印
    account_types = ['asset', 'liability', 'equity', 'income', 'expense', 'cost']
    for acc_type in account_types:
        accounts = Account.query.filter_by(type=acc_type).all()
        print(f"\n{acc_type} 类型科目 ({len(accounts)}个):")
        for acc in accounts:
            print(f"  {acc.code} - {acc.name}: {acc.balance}")
    
    # 检查已过账的凭证
    posted_vouchers = Voucher.query.filter_by(status='posted').all()
    print(f"\n=== 已过账凭证 ({len(posted_vouchers)}张) ===")
    for voucher in posted_vouchers:
        print(f"\n凭证 {voucher.voucher_number} ({voucher.date}):")
        for entry in voucher.entries:
            account = Account.query.filter_by(code=entry.account_code).first()
            acc_name = account.name if account else '未知科目'
            print(f"  {entry.account_code} - {acc_name}: 借 {entry.debit}, 贷 {entry.credit}")
