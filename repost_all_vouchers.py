#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Voucher, Account

app = create_app()

with app.app_context():
    try:
        print("=== 重新过账所有凭证 ===")
        
        # 1. 先重置所有科目余额为0
        all_accounts = Account.query.filter_by(is_deleted=False).all()
        for account in all_accounts:
            account.balance = 0.0
        db.session.commit()
        print(f"已重置 {len(all_accounts)} 个科目的余额为0")
        
        # 2. 重新过账所有已审核的凭证
        posted_vouchers = Voucher.query.filter_by(status='posted', is_deleted=False).all()
        print(f"\n找到 {len(posted_vouchers)} 张已过账凭证，开始重新过账...")
        
        for i, voucher in enumerate(posted_vouchers, 1):
            print(f"\n过账第 {i}/{len(posted_vouchers)} 张凭证：{voucher.voucher_number} ({voucher.date})")
            print(f"摘要：{voucher.summary}")
            
            for entry in voucher.entries:
                account = Account.query.filter_by(code=entry.account_code).first()
                if account:
                    # 根据科目类型更新余额
                    if account.type in ['asset', 'expense', 'cost']:
                        account.balance += entry.debit - entry.credit
                    else:  # liability, equity, income
                        account.balance += entry.credit - entry.debit
                    print(f"  {account.code} - {account.name}: 借{entry.debit} 贷{entry.credit} -> 余额: {account.balance}")
                else:
                    print(f"  ❌ 未找到科目：{entry.account_code}")
        
        # 3. 检查资产负债表平衡
        print("\n=== 重新过账完成！检查平衡 ===")
        
        # 获取所有科目
        accounts = Account.query.filter_by(is_deleted=False).all()
        
        # 按类型分组
        assets = [acc for acc in accounts if acc.type == 'asset']
        liabilities = [acc for acc in accounts if acc.type == 'liability']
        equity = [acc for acc in accounts if acc.type == 'equity']
        income = [acc for acc in accounts if acc.type == 'income']
        expense = [acc for acc in accounts if acc.type == 'expense']
        cost = [acc for acc in accounts if acc.type == 'cost']
        
        # 计算合计
        total_assets = sum(account.balance for account in assets)
        total_liabilities = sum(account.balance for account in liabilities)
        total_equity = sum(account.balance for account in equity)
        total_income = sum(account.balance for account in income)
        total_expense = sum(account.balance for account in expense)
        total_cost = sum(account.balance for account in cost)
        
        # 计算本年利润
        current_profit = total_income - total_expense - total_cost
        
        # 调整后的负债及所有者权益总计
        adjusted_total = total_liabilities + total_equity + current_profit
        
        print(f"资产总计: {total_assets}")
        print(f"负债合计: {total_liabilities}")
        print(f"所有者权益合计: {total_equity}")
        print(f"负债+所有者权益: {total_liabilities + total_equity}")
        print(f"\n收入总计: {total_income}")
        print(f"费用总计: {total_expense}")
        print(f"成本总计: {total_cost}")
        print(f"本年利润: {current_profit}")
        print(f"\n调整后负债及所有者权益总计: {adjusted_total}")
        
        # 检查平衡
        if abs(total_assets - adjusted_total) < 0.01:
            print("\n✅ 资产负债表平衡！")
        else:
            print(f"\n❌ 资产负债表不平衡，差额: {total_assets - adjusted_total}")
        
        # 保存更改
        db.session.commit()
        print("\n所有更改已保存！")
        
    except Exception as e:
        db.session.rollback()
        print(f"\n处理失败：{str(e)}")
        sys.exit(1)
