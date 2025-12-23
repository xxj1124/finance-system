#!/usr/bin/env python3
"""
检查账户分类的一致性
验证所有账户的类型字段是否为有效的会计分类
"""
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath('.'))

from app import create_app
from app.models import Account, db

app = create_app()

def check_account_classifications():
    """检查账户分类的一致性"""
    print("=== 账户分类一致性检查 ===")
    
    with app.app_context():
        # 获取所有有效账户
        accounts = Account.query.filter(Account.is_deleted == False).all()
        
        # 有效会计分类
        valid_types = {'asset', 'liability', 'equity', 'income', 'expense', 'cost'}
        
        # 检查无效分类
        invalid_classifications = []
        for account in accounts:
            if account.type not in valid_types:
                invalid_classifications.append({
                    'code': account.code,
                    'name': account.name,
                    'type': account.type,
                    'message': f"无效的账户分类: {account.type}"
                })
        
        if invalid_classifications:
            print(f"❌ 发现 {len(invalid_classifications)} 个无效账户分类:")
            for item in invalid_classifications:
                print(f"   - 科目 {item['code']} ({item['name']}): {item['message']}")
            return False
        else:
            print("✅ 所有账户分类均有效")
            return True
        
        # 检查账户代码与分类的一致性（可选的额外检查）
        print("\n=== 账户代码与分类一致性检查 ===")
        
        # 根据会计编码规则检查分类一致性
        # 示例规则：
        # 1开头 - 资产类 (asset)
        # 2开头 - 负债类 (liability)
        # 3开头 - 所有者权益类 (equity)
        # 4开头 - 成本类 (cost)
        # 5开头 - 损益类 (income/expense)
        code_type_mismatches = []
        
        for account in accounts:
            first_char = account.code[0] if account.code else ''
            
            if first_char == '1' and account.type != 'asset':
                code_type_mismatches.append(account)
            elif first_char == '2' and account.type != 'liability':
                code_type_mismatches.append(account)
            elif first_char == '3' and account.type != 'equity':
                code_type_mismatches.append(account)
            elif first_char == '4' and account.type != 'cost':
                code_type_mismatches.append(account)
            elif first_char == '5' and account.type not in ['income', 'expense']:
                code_type_mismatches.append(account)
        
        if code_type_mismatches:
            print(f"❌ 发现 {len(code_type_mismatches)} 个账户代码与分类不匹配:")
            for account in code_type_mismatches:
                print(f"   - 科目 {account.code} ({account.name}): 代码以 {account.code[0]} 开头，但分类为 {account.type}")
            return False
        else:
            print("✅ 所有账户代码与分类匹配")
            return True

if __name__ == '__main__':
    check_account_classifications()
