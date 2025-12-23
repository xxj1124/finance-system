#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import create_app
from app.models import db, Account

app = create_app()

with app.app_context():
    print("=== 资产负债表平衡检查 ===")
    
    # 获取所有会计科目
    accounts = Account.query.filter_by(is_deleted=False).all()
    
    # 按科目类型分组
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
        print(f"\n❌ 资产负债表不平衡！差额: {total_assets - adjusted_total}")
    
    # 打印详细的科目余额
    print("\n=== 详细科目余额 ===")
    print("资产类:")
    for acc in assets:
        print(f"  {acc.code} - {acc.name}: {acc.balance}")
    
    print("\n负债类:")
    for acc in liabilities:
        print(f"  {acc.code} - {acc.name}: {acc.balance}")
    
    print("\n所有者权益类:")
    for acc in equity:
        print(f"  {acc.code} - {acc.name}: {acc.balance}")
    
    print("\n收入类:")
    for acc in income:
        print(f"  {acc.code} - {acc.name}: {acc.balance}")
    
    print("\n费用类:")
    for acc in expense:
        print(f"  {acc.code} - {acc.name}: {acc.balance}")
    
    print("\n成本类:")
    for acc in cost:
        print(f"  {acc.code} - {acc.name}: {acc.balance}")
