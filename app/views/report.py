#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
财务报表模块视图
"""

from flask import render_template, request, redirect, url_for, flash
from app.models import db, Account, Voucher, Expense, SalesOrder, PurchaseOrder
from app.views import main_bp
from app.utils.auth import login_required
from datetime import datetime, timedelta, date
from decimal import Decimal

# 资产负债表
@main_bp.route('/report/balance_sheet', methods=['GET', 'POST'])
@login_required
def balance_sheet():
    """资产负债表"""
    print(f"[DEBUG] Request method: {request.method}")
    print(f"[DEBUG] Form data: {request.form}")
    if request.method == 'POST':
        report_date = datetime.strptime(request.form['report_date'], '%Y-%m-%d').date()
        print(f"[DEBUG] Report date from POST: {report_date}")
        flash(f'报表已生成，日期: {report_date}', 'success')
    else:
        # 默认显示当前月份的最后一天
        today = date.today()
        report_date = date(today.year, today.month, 1) + timedelta(days=32)
        report_date = report_date.replace(day=1) - timedelta(days=1)
        print(f"[DEBUG] Report date from GET: {report_date}")
    
    # 获取所有会计科目
    accounts = Account.query.filter_by(is_deleted=False).all()
    
    # 查询报告日期之前的所有已过账凭证
    vouchers = Voucher.query.filter(
        Voucher.date <= report_date,
        Voucher.status == 'posted',
        Voucher.is_deleted == False
    ).all()
    
    # 计算每个科目的历史余额
    account_balances = {}
    
    # 初始化所有科目的余额为0
    for account in accounts:
        account_balances[account.code] = Decimal('0.0')
    
    # 根据凭证计算每个科目的历史余额
    for voucher in vouchers:
        for entry in voucher.entries:
            if entry.account_code in account_balances:
                # 资产、费用、成本类科目：借方增加，贷方减少
                # 负债、所有者权益、收入类科目：贷方增加，借方减少
                account = next(a for a in accounts if a.code == entry.account_code)
                if account.type in ['asset', 'expense', 'cost']:
                    account_balances[entry.account_code] += entry.debit - entry.credit
                else:
                    account_balances[entry.account_code] += entry.credit - entry.debit
    
    # 按科目类型分组，并使用计算出的历史余额
    assets = []
    liabilities = []
    equity = []
    income_accounts = []
    expense_accounts = []
    cost_accounts = []
    
    for account in accounts:
        # 更新账户的余额为历史余额
        account.calculated_balance = account_balances[account.code]
        
        if account.type == 'asset':
            assets.append(account)
        elif account.type == 'liability':
            liabilities.append(account)
        elif account.type == 'equity':
            equity.append(account)
        elif account.type == 'income':
            income_accounts.append(account)
        elif account.type == 'expense':
            expense_accounts.append(account)
        elif account.type == 'cost':
            cost_accounts.append(account)
    
    # 计算合计
    total_assets = sum(account.calculated_balance for account in assets)
    total_liabilities = sum(account.calculated_balance for account in liabilities)
    total_equity = sum(account.calculated_balance for account in equity)
    
    # 计算收入、费用和成本的总计（使用历史余额）
    total_income = sum(account.calculated_balance for account in income_accounts)
    total_expense = sum(account.calculated_balance for account in expense_accounts)
    total_cost = sum(account.calculated_balance for account in cost_accounts)
    
    # 计算本年利润的影响
    current_profit = total_income - total_expense - total_cost
    
    # 计算调整后所有者权益总额（包含本年利润）
    adjusted_equity = total_equity + current_profit
    
    # 调整资产负债表平衡检查：资产 = 负债 + 所有者权益（含本年利润）
    adjusted_total = total_liabilities + adjusted_equity
    
    return render_template('report/balance_sheet.html', 
                         report_date=report_date, 
                         assets=assets, 
                         liabilities=liabilities, 
                         equity=equity,
                         total_assets=total_assets,
                         total_liabilities=total_liabilities,
                         total_equity=total_equity,
                         adjusted_equity=adjusted_equity,
                         current_profit=current_profit,
                         adjusted_total=adjusted_total,
                         total_income=total_income,
                         total_expense=total_expense,
                         total_cost=total_cost)

# 利润表
@main_bp.route('/report/profit_statement', methods=['GET', 'POST'])
@login_required
def profit_statement():
    """利润表"""
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
    else:
        # 默认显示当前月份
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, 1) + timedelta(days=32)
        end_date = end_date.replace(day=1) - timedelta(days=1)
    
    # 获取所有收入、费用和成本类账户
    income_accounts = Account.query.filter_by(type='income', is_deleted=False).all()
    expense_accounts = Account.query.filter_by(type='expense', is_deleted=False).all()
    cost_accounts = Account.query.filter_by(type='cost', is_deleted=False).all()
    
    # 获取期间内的所有已过账凭证（排除期末结转凭证）
    vouchers = Voucher.query.filter(
        Voucher.date >= start_date,
        Voucher.date <= end_date,
        Voucher.status == 'posted',
        Voucher.is_deleted == False,
        ~Voucher.voucher_number.like('CLOS%')  # 排除结转凭证
    ).all()
    
    # 基于凭证数据计算期间收入和费用
    total_income = Decimal('0.0')  # 收入（损益类账户的贷方发生额）
    total_cost = Decimal('0.0')    # 成本（损益类账户的借方发生额）
    total_expense = Decimal('0.0') # 费用（损益类账户的借方发生额）
    
    # 为每个损益类账户创建期间发生额字典
    account_movements = {}
    
    # 初始化所有账户的发生额为0
    for acc in income_accounts + cost_accounts + expense_accounts:
        account_movements[acc.code] = Decimal('0.0')
    
    # 收集损益类账户的代码
    income_codes = [acc.code for acc in income_accounts]
    cost_codes = [acc.code for acc in cost_accounts]
    expense_codes = [acc.code for acc in expense_accounts]
    
    # 遍历所有凭证条目，汇总期间损益数据
    for voucher in vouchers:
        for entry in voucher.entries:
            if entry.account_code in income_codes:
                # 收入类账户的贷方发生额计入收入
                total_income += entry.credit
                account_movements[entry.account_code] += entry.credit
            elif entry.account_code in cost_codes:
                # 成本类账户的借方发生额计入成本
                total_cost += entry.debit
                account_movements[entry.account_code] += entry.debit
            elif entry.account_code in expense_codes:
                # 费用类账户的借方发生额计入费用
                total_expense += entry.debit
                account_movements[entry.account_code] += entry.debit
    
    # 计算利润
    gross_profit = total_income - total_cost
    net_profit = gross_profit - total_expense
    
    return render_template('report/profit_statement.html', 
                         start_date=start_date, 
                         end_date=end_date, 
                         income_accounts=income_accounts, 
                         expense_accounts=expense_accounts,
                         cost_accounts=cost_accounts,
                         account_movements=account_movements,
                         total_income=total_income,
                         total_cost=total_cost,
                         total_expense=total_expense,
                         gross_profit=gross_profit,
                         net_profit=net_profit)

# 现金流量表
@main_bp.route('/report/cash_flow', methods=['GET', 'POST'])
@login_required
def cash_flow():
    """现金流量表"""
    if request.method == 'POST':
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d').date()
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d').date()
    else:
        # 默认显示当前月份
        today = date.today()
        start_date = date(today.year, today.month, 1)
        end_date = date(today.year, today.month, 1) + timedelta(days=32)
        end_date = end_date.replace(day=1) - timedelta(days=1)
    
    # 这里简化处理，实际应该基于现金科目计算
    # 假设现金和银行存款科目
    cash_accounts = Account.query.filter(
        Account.code.like('1001%') | Account.code.like('1002%'),
        Account.is_deleted == False
    ).all()
    
    # 获取期间内的凭证
    vouchers = Voucher.query.filter(
        Voucher.date >= start_date,
        Voucher.date <= end_date,
        Voucher.status == 'posted',
        Voucher.is_deleted == False
    ).all()
    
    # 计算经营活动、投资活动、筹资活动的现金流量
    # 正确的方法：基于现金类科目（1001、1002）的实际变动计算
    cash_sales = Decimal('0.0')  # 销售商品收到的现金
    cash_expenses = Decimal('0.0')  # 支付的经营费用
    investing_cash = Decimal('0.0')  # 投资活动现金流量
    financing_cash = Decimal('0.0')  # 筹资活动现金流量
    
    for voucher in vouchers:
        for entry in voucher.entries:
            account = entry.account
            if not account:
                continue
                
            # 现金流入：现金/银行存款科目的借方
            if account.code in ['1001', '1002'] and entry.debit > 0:
                # 查找对应的贷方科目，判断现金流入的性质
                credit_entry = None
                for e in voucher.entries:
                    if e.credit > 0 and e != entry:
                        credit_entry = e
                        break
                
                if credit_entry:
                    credit_account = credit_entry.account
                    if credit_account:
                        if credit_account.type == 'income':
                            # 销售商品收到的现金（经营活动流入）
                            cash_sales += entry.debit
                        elif credit_account.type == 'equity':
                            # 筹资活动流入
                            financing_cash += entry.debit
                        elif credit_account.type == 'liability':
                            # 筹资活动流入（借款）
                            financing_cash += entry.debit
            
            # 现金流出：现金/银行存款科目的贷方
            elif account.code in ['1001', '1002'] and entry.credit > 0:
                # 查找对应的借方科目，判断现金流出的性质
                debit_entry = None
                for e in voucher.entries:
                    if e.debit > 0 and e != entry:
                        debit_entry = e
                        break
                
                if debit_entry:
                    debit_account = debit_entry.account
                    if debit_account:
                        if debit_account.type in ['expense', 'cost']:
                            # 支付经营费用（经营活动流出）
                            cash_expenses += entry.credit
                        elif debit_account.type == 'asset' and (debit_account.code.startswith('15') or debit_account.code.startswith('16')):
                            # 投资活动流出（购买长期资产）
                            investing_cash -= entry.credit
    
    # 计算各活动现金流量净额
    operating_cash_flow = cash_sales - cash_expenses
    investing_cash_flow = investing_cash
    financing_cash_flow = financing_cash
    
    net_cash_flow = operating_cash_flow + investing_cash_flow + financing_cash_flow
    
    # 计算期初和期末现金余额
    if cash_accounts:
        beginning_cash = sum(account.balance for account in cash_accounts) - net_cash_flow
        ending_cash = sum(account.balance for account in cash_accounts)
    else:
        beginning_cash = Decimal('0.0')
        ending_cash = net_cash_flow
    
    return render_template('report/cash_flow.html', 
                         start_date=start_date, 
                         end_date=end_date, 
                         cash_sales=cash_sales,
                         cash_expenses=cash_expenses,
                         operating_cash_flow=operating_cash_flow,
                         investing_cash_flow=investing_cash_flow,
                         financing_cash_flow=financing_cash_flow,
                         net_cash_flow=net_cash_flow,
                         beginning_cash=beginning_cash,
                         ending_cash=ending_cash)

# 科目余额表
@main_bp.route('/report/account_balance', methods=['GET', 'POST'])
@login_required
def account_balance():
    """科目余额表"""
    if request.method == 'POST':
        report_date = datetime.strptime(request.form['report_date'], '%Y-%m-%d').date()
        flash(f'报表已生成，日期: {report_date}', 'success')
    else:
        report_date = date.today()
    
    # 获取所有会计科目
    accounts = Account.query.filter_by(is_deleted=False).order_by(Account.code).all()
    
    # 查询报告日期之前的所有已过账凭证
    vouchers = Voucher.query.filter(
        Voucher.date <= report_date,
        Voucher.status == 'posted',
        Voucher.is_deleted == False
    ).all()
    
    # 计算每个科目的历史余额
    account_balances = {}
    
    # 初始化所有科目的余额为0
    for account in accounts:
        account_balances[account.code] = Decimal('0.0')
    
    # 根据凭证计算每个科目的历史余额
    for voucher in vouchers:
        for entry in voucher.entries:
            if entry.account_code in account_balances:
                # 资产、费用、成本类科目：借方增加，贷方减少
                # 负债、所有者权益、收入类科目：贷方增加，借方减少
                account = next(a for a in accounts if a.code == entry.account_code)
                if account.type in ['asset', 'expense', 'cost']:
                    account_balances[entry.account_code] += entry.debit - entry.credit
                else:
                    account_balances[entry.account_code] += entry.credit - entry.debit
    
    # 将计算出的历史余额添加到账户对象中
    for account in accounts:
        account.calculated_balance = account_balances[account.code]
    
    return render_template('report/account_balance.html', 
                         report_date=report_date, 
                         accounts=accounts)

# 报表列表
@main_bp.route('/report/list')
@login_required
def report_list():
    """报表列表"""
    return render_template('report/list.html')
