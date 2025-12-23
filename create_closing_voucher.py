#!/usr/bin/env python3
import sys
import os
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from app import create_app
from app.models import db, Account, Voucher, VoucherEntry
from datetime import datetime, date

app = create_app('development')

with app.app_context():
    # 获取当前日期
    today = date.today()
    
    # 获取所有收入、费用和成本类账户
    income_accounts = Account.query.filter_by(type='income', is_deleted=False).all()
    expense_accounts = Account.query.filter_by(type='expense', is_deleted=False).all()
    cost_accounts = Account.query.filter_by(type='cost', is_deleted=False).all()
    
    # 计算收入合计
    total_income = 0.0
    print(f"收入类账户余额:")
    for acc in income_accounts:
        print(f"- {acc.name} ({acc.code}): {acc.balance}")
        total_income += float(acc.balance)
    
    # 计算费用合计
    total_expense = 0.0
    print(f"\\n费用类账户余额:")
    for acc in expense_accounts:
        print(f"- {acc.name} ({acc.code}): {acc.balance}")
        total_expense += float(acc.balance)
    
    # 计算成本合计
    total_cost = 0.0
    print(f"\\n成本类账户余额:")
    for acc in cost_accounts:
        print(f"- {acc.name} ({acc.code}): {acc.balance}")
        total_cost += float(acc.balance)
    
    # 计算净利润
    net_profit = total_income - total_expense - total_cost
    print(f"\\n收入总计: {total_income}")
    print(f"费用总计: {total_expense}")
    print(f"成本总计: {total_cost}")
    print(f"净利润: {net_profit}")
    
    # 检查是否需要结转
    if abs(total_income) < 0.01 and abs(total_expense) < 0.01 and abs(total_cost) < 0.01:
        print(f"\\n不需要结转，所有损益类账户余额都为零。")
        sys.exit(0)
    
    # 获取本年利润和利润分配账户
    profit_account = Account.query.filter_by(code='4103', is_deleted=False).first()  # 本年利润
    profit_distribution = Account.query.filter_by(code='4104', is_deleted=False).first()  # 利润分配
    
    if not profit_account:
        print(f"\n错误：没有找到本年利润账户（4103）！")
        sys.exit(1)
    
    if not profit_distribution:
        print(f"\n错误：没有找到利润分配账户（4104）！")
        sys.exit(1)
    
    print(f"\n使用账户 {profit_account.name} ({profit_account.code}) 和 {profit_distribution.name} ({profit_distribution.code}) 进行结转。")
    
    # 创建结转凭证
    voucher = Voucher()
    # 使用更可靠的方式生成唯一凭证编号
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    import random
    random_suffix = random.randint(1000, 9999)
    voucher.voucher_number = f"CLOS{timestamp}{random_suffix}"
    voucher.date = today
    voucher.summary = f"{today.strftime('%Y年%m月')}期末损益结转"
    voucher.status = 'draft'
    voucher.user_id = 1  # 假设用户ID为1
    
    db.session.add(voucher)
    db.session.flush()  # 获取voucher.id
    
    # 计算需要结转的总额
    total_income = sum(float(acc.balance) for acc in income_accounts if abs(float(acc.balance)) > 0.01)
    total_expense = sum(float(acc.balance) for acc in expense_accounts if abs(float(acc.balance)) > 0.01)
    total_cost = sum(float(acc.balance) for acc in cost_accounts if abs(float(acc.balance)) > 0.01)
    
    # 结转收入类账户（借：收入，贷：本年利润）
    for acc in income_accounts:
        if abs(float(acc.balance)) > 0.01:
            entry = VoucherEntry()
            entry.voucher_id = voucher.id
            entry.account_code = acc.code
            entry.debit = acc.balance
            entry.credit = 0.0
            entry.description = f"结转 {acc.name} 余额"
            db.session.add(entry)
    
    # 结转费用类账户（借：本年利润，贷：费用）
    for acc in expense_accounts:
        if abs(float(acc.balance)) > 0.01:
            entry = VoucherEntry()
            entry.voucher_id = voucher.id
            entry.account_code = acc.code
            entry.debit = 0.0
            entry.credit = acc.balance
            entry.description = f"结转 {acc.name} 余额"
            db.session.add(entry)
    
    # 结转成本类账户（借：本年利润，贷：成本）
    for acc in cost_accounts:
        if abs(float(acc.balance)) > 0.01:
            entry = VoucherEntry()
            entry.voucher_id = voucher.id
            entry.account_code = acc.code
            entry.debit = 0.0
            entry.credit = acc.balance
            entry.description = f"结转 {acc.name} 余额"
            db.session.add(entry)
    
    # 在本年利润账户中记录结转总额（使凭证借贷平衡）
    # 收入结转：本年利润 贷方
    if total_income > 0.01:
        entry = VoucherEntry()
        entry.voucher_id = voucher.id
        entry.account_code = profit_account.code
        entry.debit = 0.0
        entry.credit = total_income
        entry.description = "结转本月收入总额"
        db.session.add(entry)
    
    # 费用和成本结转：本年利润 借方
    total_expense_cost = total_expense + total_cost
    if total_expense_cost > 0.01:
        entry = VoucherEntry()
        entry.voucher_id = voucher.id
        entry.account_code = profit_account.code
        entry.debit = total_expense_cost
        entry.credit = 0.0
        entry.description = "结转本月费用和成本总额"
        db.session.add(entry)
    
    # 将本年利润结转到利润分配
    if abs(net_profit) > 0.01:
        entry = VoucherEntry()
        entry.voucher_id = voucher.id
        entry.account_code = profit_account.code
        if net_profit > 0:
            entry.debit = net_profit
            entry.credit = 0.0
        else:
            entry.debit = 0.0
            entry.credit = abs(net_profit)
        entry.description = "结转本年利润到利润分配"
        db.session.add(entry)
        
        # 利润分配科目对应分录
        entry = VoucherEntry()
        entry.voucher_id = voucher.id
        entry.account_code = profit_distribution.code
        if net_profit > 0:
            entry.debit = 0.0
            entry.credit = net_profit
        else:
            entry.debit = abs(net_profit)
            entry.credit = 0.0
        entry.description = "结转本年利润到利润分配"
        db.session.add(entry)
    
    try:
        db.session.commit()
        print(f"\\n成功创建结转凭证：{voucher.voucher_number}")
        print(f"现在需要审核并过账该凭证以完成结转。")
    except Exception as e:
        db.session.rollback()
        print(f"\\n创建结转凭证失败：{str(e)}")
        sys.exit(1)
