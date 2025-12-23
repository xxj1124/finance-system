#!/usr/bin/env python3
"""
验证期间损益结转凭证的正确性
"""
import sys
import os
sys.path.append(os.path.abspath('.'))

from app import app, db
from app.models import Voucher, VoucherEntry, Account
from decimal import Decimal

def check_closing_vouchers():
    """检查期间损益结转凭证"""
    print("=== 期间损益结转凭证检查 ===")
    
    with app.app_context():
        # 查询所有结转凭证
        closing_vouchers = Voucher.query.filter(
            Voucher.voucher_number.like('CLOS%'),
            Voucher.is_deleted == False
        ).order_by(Voucher.date.desc()).all()
        
        if not closing_vouchers:
            print("❌ 没有找到期间损益结转凭证")
            return False
        
        print(f"✅ 找到 {len(closing_vouchers)} 张结转凭证")
        
        # 检查每张结转凭证
        for voucher in closing_vouchers:
            print(f"\n=== 检查结转凭证: {voucher.voucher_number} (日期: {voucher.date}) ===")
            print(f"摘要: {voucher.summary}")
            print(f"状态: {voucher.status}")
            
            # 检查凭证的借贷平衡
            debit_total = sum(entry.debit for entry in voucher.entries)
            credit_total = sum(entry.credit for entry in voucher.entries)
            
            if abs(debit_total - credit_total) < Decimal('0.01'):
                print(f"✅ 凭证借贷平衡: 借方 {debit_total:.2f}, 贷方 {credit_total:.2f}")
            else:
                print(f"❌ 凭证借贷不平衡: 借方 {debit_total:.2f}, 贷方 {credit_total:.2f}")
            
            # 分析凭证分录
            profit_entries = []  # 本年利润相关分录
            income_entries = []  # 收入结转分录
            expense_entries = [] # 费用结转分录
            cost_entries = []    # 成本结转分录
            
            for entry in voucher.entries:
                account = entry.account
                if not account:
                    continue
                    
                if account.code == '4103':  # 本年利润
                    profit_entries.append(entry)
                elif account.type == 'income':
                    income_entries.append(entry)
                elif account.type == 'expense':
                    expense_entries.append(entry)
                elif account.type == 'cost':
                    cost_entries.append(entry)
            
            # 检查结转逻辑
            print(f"\n凭证分录分析:")
            print(f"- 收入类分录: {len(income_entries)} 条")
            print(f"- 成本类分录: {len(cost_entries)} 条")
            print(f"- 费用类分录: {len(expense_entries)} 条")
            print(f"- 本年利润分录: {len(profit_entries)} 条")
            
            # 验证收入结转逻辑（借：收入，贷：本年利润）
            valid_income = True
            for entry in income_entries:
                if entry.debit == 0 or entry.credit > 0:
                    print(f"⚠️  收入账户 {entry.account.name} ({entry.account.code}) 结转分录方向错误: 借 {entry.debit:.2f}, 贷 {entry.credit:.2f}")
                    valid_income = False
            
            if valid_income and income_entries:
                print("✅ 收入类账户结转方向正确（借记收入账户）")
            
            # 验证费用和成本结转逻辑（借：本年利润，贷：费用/成本）
            valid_expense_cost = True
            for entry in expense_entries + cost_entries:
                if entry.debit > 0 or entry.credit == 0:
                    print(f"⚠️  {entry.account.type}账户 {entry.account.name} ({entry.account.code}) 结转分录方向错误: 借 {entry.debit:.2f}, 贷 {entry.credit:.2f}")
                    valid_expense_cost = False
            
            if valid_expense_cost and (expense_entries or cost_entries):
                print("✅ 费用/成本类账户结转方向正确（贷记费用/成本账户）")
            
            # 检查本年利润账户的分录是否与结转总额一致
            if profit_entries:
                profit_debit = sum(entry.debit for entry in profit_entries)
                profit_credit = sum(entry.credit for entry in profit_entries)
                print(f"本年利润账户: 借方 {profit_debit:.2f}, 贷方 {profit_credit:.2f}")
            
        return True

if __name__ == '__main__':
    check_closing_vouchers()