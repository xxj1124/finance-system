#!/usr/bin/env python3
"""
删除旧的不平衡结转凭证
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models import Voucher

app = create_app()

with app.app_context():
    try:
        # 删除所有结转凭证
        closing_vouchers = Voucher.query.filter(Voucher.voucher_number.like('CLOS%')).all()
        
        if not closing_vouchers:
            print("没有找到结转凭证！")
            sys.exit(0)
            
        for voucher in closing_vouchers:
            print(f"删除凭证：ID={voucher.id}, 编号={voucher.voucher_number}, 状态={voucher.status}")
            # 先删除凭证分录
            for entry in voucher.entries:
                db.session.delete(entry)
            # 再删除凭证
            db.session.delete(voucher)
        
        db.session.commit()
        print(f"\n成功删除 {len(closing_vouchers)} 个结转凭证！")
        
    except Exception as e:
        db.session.rollback()
        print(f"删除失败：{str(e)}")
        sys.exit(1)