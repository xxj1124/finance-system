#!/usr/bin/env python3
"""
检查所有资产账户是否存在负数余额
"""
import sys
import os
sys.path.append(os.path.abspath('.'))

from app import app, db
from app.models import Account

def check_asset_accounts():
    """检查所有资产账户的余额"""
    print("=== 资产账户余额检查 ===")
    
    with app.app_context():
        # 查询所有资产类账户
        asset_accounts = Account.query.filter(
            Account.type == 'asset',
            Account.is_deleted == False
        ).all()
        
        negative_assets = []
        
        for account in asset_accounts:
            print(f"账户: {account.name} ({account.code}) - 余额: {account.balance:.2f}")
            if account.balance < 0:
                negative_assets.append(account)
        
        print()
        if negative_assets:
            print("⚠️  发现以下资产账户存在负数余额：")
            for account in negative_assets:
                print(f"  - {account.name} ({account.code}): {account.balance:.2f}")
        else:
            print("✅ 所有资产账户余额均为非负")
        
        return len(negative_assets) == 0

if __name__ == '__main__':
    check_asset_accounts()