#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
删除历史交易记录脚本
"""

from app import app
from app.models import db, Expense, Voucher, VoucherEntry, Account

def clear_transactions():
    """删除所有交易记录"""
    with app.app_context():
        try:
            # 1. 删除所有凭证分录
            voucher_entry_count = VoucherEntry.query.count()
            VoucherEntry.query.delete()
            print(f"已删除 {voucher_entry_count} 条凭证分录")
            
            # 2. 删除所有凭证
            voucher_count = Voucher.query.count()
            Voucher.query.delete()
            print(f"已删除 {voucher_count} 张凭证")
            
            # 3. 删除所有费用报销
            expense_count = Expense.query.count()
            Expense.query.delete()
            print(f"已删除 {expense_count} 条费用报销记录")
            
            # 4. 重置会计科目余额
            accounts = Account.query.all()
            for account in accounts:
                account.balance = 0.0
            print(f"已重置 {len(accounts)} 个会计科目的余额")
            
            # 提交更改
            db.session.commit()
            print("所有交易记录已成功删除！")
            
        except Exception as e:
            db.session.rollback()
            print(f"删除交易记录失败: {str(e)}")

if __name__ == "__main__":
    clear_transactions()