#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import db, Account, Voucher
from datetime import datetime

app = create_app('development')

with app.app_context():
    try:
        # 获取最后创建的结转凭证（CLOS开头）
        closing_voucher = Voucher.query.filter(
            Voucher.voucher_number.like('CLOS%'),
            Voucher.status == 'draft',
            Voucher.is_deleted == False
        ).order_by(Voucher.create_time.desc()).first()
        
        if not closing_voucher:
            print("没有找到需要过账的结转凭证。")
            sys.exit(1)
        
        print(f"找到结转凭证：{closing_voucher.voucher_number}")
        print(f"当前状态：{closing_voucher.status}")
        
        # 1. 审核凭证
        closing_voucher.status = 'approved'
        closing_voucher.approval_id = 1  # 假设用户ID为1
        closing_voucher.approval_time = datetime.now()
        db.session.commit()
        print(f"凭证已审核，状态：{closing_voucher.status}")
        
        # 2. 过账凭证
        closing_voucher.status = 'posted'
        closing_voucher.post_time = datetime.now()
        
        # 更新账户余额
        for entry in closing_voucher.entries:
            account = Account.query.filter_by(code=entry.account_code).first()
            if account:
                # 根据科目类型更新余额
                if account.type in ['asset', 'expense', 'cost']:
                    account.balance += entry.debit - entry.credit
                else:  # liability, equity, income
                    account.balance += entry.credit - entry.debit
        
        db.session.commit()
        print(f"凭证已过账，状态：{closing_voucher.status}")
        print("结转完成！")
        
    except Exception as e:
        db.session.rollback()
        print(f"操作失败：{str(e)}")
        sys.exit(1)
