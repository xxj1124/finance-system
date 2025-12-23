#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
详细检查资产负债表不平衡问题
"""

import sys
import os
from datetime import date, datetime

# 添加项目根目录到系统路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.models import db, Account, Voucher

def main():
    app = create_app()
    with app.app_context():
        print("=== 详细资产负债表平衡检查 ===")
        print(f"检查日期: {date.today()}")
        print()
        
        # 1. 获取所有科目
        accounts = Account.query.filter_by(is_deleted=False).all()
        
        # 2. 按类型分组
        assets = []
        liabilities = []
        equity = []
        income = []
        expense = []
        cost = []
        
        for account in accounts:
            if account.type == 'asset':
                assets.append(account)
            elif account.type == 'liability':
                liabilities.append(account)
            elif account.type == 'equity':
                equity.append(account)
            elif account.type == 'income':
                income.append(account)
            elif account.type == 'expense':
                expense.append(account)
            elif account.type == 'cost':
                cost.append(account)
        
        # 3. 打印各类科目余额
        print("--- 资产类科目 --- ")
        total_assets = 0
        for acc in assets:
            total_assets += acc.balance
            print(f"{acc.code} {acc.name}: {acc.balance}")
        print(f"资产总计: {total_assets}")
        print()
        
        print("--- 负债类科目 --- ")
        total_liabilities = 0
        for acc in liabilities:
            total_liabilities += acc.balance
            print(f"{acc.code} {acc.name}: {acc.balance}")
        print(f"负债总计: {total_liabilities}")
        print()
        
        print("--- 所有者权益类科目 --- ")
        total_equity = 0
        for acc in equity:
            total_equity += acc.balance
            print(f"{acc.code} {acc.name}: {acc.balance}")
        print(f"所有者权益总计: {total_equity}")
        print()
        
        print("--- 收入类科目 --- ")
        total_income = 0
        for acc in income:
            total_income += acc.balance
            print(f"{acc.code} {acc.name}: {acc.balance}")
        print(f"收入总计: {total_income}")
        print()
        
        print("--- 费用类科目 --- ")
        total_expense = 0
        for acc in expense:
            total_expense += acc.balance
            print(f"{acc.code} {acc.name}: {acc.balance}")
        print(f"费用总计: {total_expense}")
        print()
        
        print("--- 成本类科目 --- ")
        total_cost = 0
        for acc in cost:
            total_cost += acc.balance
            print(f"{acc.code} {acc.name}: {acc.balance}")
        print(f"成本总计: {total_cost}")
        print()
        
        # 4. 计算平衡情况
        total_liability_equity = total_liabilities + total_equity
        print("=== 平衡检查结果 ===")
        print(f"资产总计: {total_assets}")
        print(f"负债+所有者权益总计: {total_liability_equity}")
        print(f"差额: {total_assets - total_liability_equity}")
        print()
        
        # 5. 检查未结账的凭证
        unposted_vouchers = Voucher.query.filter(
            Voucher.status != 'posted',
            Voucher.is_deleted == False
        ).all()
        
        if unposted_vouchers:
            print("=== 未过账凭证 ===")
            for voucher in unposted_vouchers:
                print(f"凭证号: {voucher.voucher_number}, 日期: {voucher.date}, 摘要: {voucher.summary}, 状态: {voucher.status}")
            print()
        
        # 6. 检查所有凭证的借贷平衡
        print("=== 凭证借贷平衡检查 ===")
        all_vouchers = Voucher.query.filter_by(is_deleted=False).all()
        unbalanced_vouchers = []
        
        for voucher in all_vouchers:
            total_debit = sum(entry.debit for entry in voucher.entries)
            total_credit = sum(entry.credit for entry in voucher.entries)
            
            if abs(total_debit - total_credit) > 0.01:
                unbalanced_vouchers.append({
                    'voucher_number': voucher.voucher_number,
                    'date': voucher.date,
                    'summary': voucher.summary,
                    'total_debit': total_debit,
                    'total_credit': total_credit,
                    'difference': abs(total_debit - total_credit)
                })
        
        if unbalanced_vouchers:
            print("发现不平衡的凭证:")
            for v in unbalanced_vouchers:
                print(f"凭证号: {v['voucher_number']}, 日期: {v['date']}, 摘要: {v['summary']}")
                print(f"  借方合计: {v['total_debit']}, 贷方合计: {v['total_credit']}, 差额: {v['difference']}")
        else:
            print("所有凭证借贷平衡")
        
        print()
        print("=== 检查完成 ===")

if __name__ == '__main__':
    main()
