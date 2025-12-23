#!/usr/bin/env python3
"""
验证所有凭证的借贷平衡（借方总额=贷方总额）
"""
import sys
import os
sys.path.append(os.path.abspath('.'))

from app import app, db
from app.models import Voucher, VoucherEntry
from decimal import Decimal

def check_voucher_balances():
    """检查所有凭证的借贷平衡"""
    print("=== 凭证借贷平衡检查 ===")
    
    with app.app_context():
        # 查询所有有效凭证
        vouchers = Voucher.query.filter(
            Voucher.is_deleted == False
        ).order_by(Voucher.date, Voucher.voucher_number).all()
        
        unbalanced_vouchers = []
        
        for voucher in vouchers:
            # 计算该凭证的借方总额和贷方总额
            debit_total = Decimal('0')
            credit_total = Decimal('0')
            
            for entry in voucher.entries:
                debit_total += entry.debit
                credit_total += entry.credit
            
            # 检查是否平衡（考虑浮点精度问题）
            is_balanced = abs(debit_total - credit_total) < Decimal('0.01')
            
            status = "✅" if is_balanced else "❌"
            print(f"{status} 凭证: {voucher.date} ({voucher.voucher_number or '无编号'}) - 借方: {debit_total:.2f}, 贷方: {credit_total:.2f}")
            
            if not is_balanced:
                unbalanced_vouchers.append((voucher, debit_total, credit_total))
        
        print()
        if unbalanced_vouchers:
            print(f"⚠️  发现 {len(unbalanced_vouchers)} 张凭证借贷不平衡：")
            for voucher, debit, credit in unbalanced_vouchers:
                print(f"  - {voucher.date} ({voucher.voucher_number or '无编号'}) - 借方: {debit:.2f}, 贷方: {credit:.2f}, 差异: {debit - credit:.2f}")
        else:
            print(f"✅ 所有 {len(vouchers)} 张凭证借贷均平衡")
    
    return len(unbalanced_vouchers) == 0

if __name__ == '__main__':
    check_voucher_balances()