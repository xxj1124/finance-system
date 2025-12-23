#!/usr/bin/env python3
"""
审核并过账最新创建的结转凭证
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Voucher

app = create_app()

with app.app_context():
    try:
        # 查找最新创建的结转凭证（编号以CLOS开头）
        closing_voucher = Voucher.query.filter(Voucher.voucher_number.like('CLOS%')).order_by(Voucher.create_time.desc()).first()
        
        if not closing_voucher:
            print("未找到结转凭证！")
            sys.exit(1)
            
        print(f"找到结转凭证：ID={closing_voucher.id}, 编号={closing_voucher.voucher_number}, 状态={closing_voucher.status}")
        
        # 审核凭证
        if closing_voucher.status == 'draft':
            closing_voucher.status = 'approved'
            closing_voucher.approval_id = 1  # 使用管理员ID
            closing_voucher.approval_time = db.func.now()
            db.session.commit()
            print("凭证审核成功！")
        
        # 过账凭证
        if closing_voucher.status == 'approved':
            # 更新科目余额
            for entry in closing_voucher.entries:
                account = entry.account
                if account:
                    # 根据科目类型更新余额
                    if account.type in ['asset', 'expense', 'cost']:
                        account.balance += entry.debit - entry.credit
                    else:  # liability, equity, income
                        account.balance += entry.credit - entry.debit
            
            closing_voucher.status = 'posted'
            closing_voucher.post_time = db.func.now()
            db.session.commit()
            print("凭证过账成功！")
        
        print("\n结转凭证处理完成！")
        print(f"当前状态：{closing_voucher.status}")
        
    except Exception as e:
        db.session.rollback()
        print(f"处理失败：{str(e)}")
        sys.exit(1)