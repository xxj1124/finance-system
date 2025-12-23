#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试数据生成脚本
为每个模块生成测试记录
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime, timedelta
import random
from app.models import (db, User, Supplier, Customer, Account, PurchaseOrder, PurchaseOrderItem,
                     SalesOrder, SalesOrderItem, Expense, Voucher, VoucherEntry, Budget, Tax)
from run import app
from werkzeug.security import generate_password_hash

# 生成随机金额
def random_amount(min_amount=100.0, max_amount=100000.0):
    # 将参数转换为float类型以避免类型错误
    min_amount = float(min_amount)
    max_amount = float(max_amount)
    return round(random.uniform(min_amount, max_amount), 2)

# 生成随机税率
def random_tax_rate():
    tax_rates = [0.03, 0.06, 0.09, 0.13]
    return random.choice(tax_rates)

# 生成订单号
def generate_order_number(prefix):
    return f"{prefix}{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

# 生成凭证号
def generate_voucher_number():
    return f"VOU{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

# 生成报销单号
def generate_expense_number():
    return f"EXP{datetime.now().strftime('%Y%m%d')}{random.randint(1000, 9999)}"

# 生成随机日期时间
def random_datetime(start_date='-30d', end_date='now'):
    if start_date == '-30d':
        start = datetime.now() - timedelta(days=30)
    else:
        start = datetime.now()
    
    if end_date == 'now':
        end = datetime.now()
    else:
        end = datetime.now() + timedelta(days=int(end_date))
    
    delta = end - start
    return start + timedelta(seconds=random.randint(0, int(delta.total_seconds())))

# 生成随机日期
def random_date(start_date='-30d', end_date='now'):
    dt = random_datetime(start_date, end_date)
    return dt.date()

# 生成随机文本
def random_text(max_length=100):
    texts = [
        '日常办公费用',
        '客户招待费用',
        '员工出差费用',
        '购买办公用品',
        '设备维护费用',
        '广告宣传费用',
        '运输物流费用',
        '其他杂项费用'
    ]
    return random.choice(texts)

# 生成随机姓名
def random_name():
    first_names = ['张', '王', '李', '赵', '刘', '陈', '杨', '黄', '周', '吴']
    last_names = ['明', '华', '强', '芳', '秀英', '娜', '敏', '静', '丽', '强']
    return f"{random.choice(first_names)}{random.choice(last_names)}"

# 生成随机电话
def random_phone():
    return f"13{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}{random.randint(0, 9)}"

# 生成随机邮箱
def random_email():
    domains = ['example.com', 'test.com', 'company.com', 'mail.com']
    return f"user{random.randint(100, 999)}@{random.choice(domains)}"

# 生成随机地址
def random_address():
    provinces = ['北京市', '上海市', '广东省', '江苏省', '浙江省', '山东省', '河南省', '四川省', '湖北省', '湖南省']
    cities = ['市', '区', '县', '镇']
    streets = ['大街', '路', '巷', '胡同']
    return f"{random.choice(provinces)}{random.choice(cities)}{random.randint(1, 100)}{random.choice(streets)}{random.randint(1, 100)}号"

# 生成随机公司名
def random_company():
    prefixes = ['北京', '上海', '广州', '深圳', '杭州', '南京', '成都', '武汉', '西安', '重庆']
    suffixes = ['科技有限公司', '贸易有限公司', '实业有限公司', '发展有限公司', '有限公司']
    return f"{random.choice(prefixes)}{random.randint(100, 999)}{random.choice(suffixes)}"

# 生成用户数据
def generate_users(count=5):
    """生成用户数据"""
    users = []
    roles = ['admin', 'manager', 'user']
    
    # 检查是否已经有admin用户
    existing_admin = User.query.filter_by(username='admin').first()
    if not existing_admin:
        # 确保有一个admin用户
        admin_user = User(
            username='admin',
            password=generate_password_hash('123456'),  # 使用加密密码
            real_name='管理员',
            role='admin',
            email='admin@example.com',
            phone='13800138000'
        )
        users.append(admin_user)
    
    # 检查现有的userN用户数量
    existing_users = User.query.filter(User.username.like('user%')).all()
    existing_user_count = len(existing_users)
    
    # 生成其他用户，避免重复
    for i in range(existing_user_count, existing_user_count + count):
        user = User(
            username=f"user{i+1}",
            password=generate_password_hash('123456'),  # 使用加密密码
            real_name=random_name(),
            role=random.choice(roles),
            email=random_email(),
            phone=random_phone()
        )
        users.append(user)
    
    return users

# 生成供应商数据
def generate_suppliers(count=10):
    """生成供应商数据"""
    suppliers = []
    for i in range(count):
        supplier = Supplier(
            name=f"{random_company()}{i}",
            contact=random_name(),
            phone=random_phone(),
            email=random_email(),
            address=random_address(),
            tax_number=''.join(random.choices('0123456789', k=15)),
            bank_account=''.join(random.choices('0123456789', k=19))
        )
        suppliers.append(supplier)
    
    return suppliers

# 生成客户数据
def generate_customers(count=10):
    """生成客户数据"""
    customers = []
    for i in range(count):
        customer = Customer(
            name=f"{random_company()}{i}",
            contact=random_name(),
            phone=random_phone(),
            email=random_email(),
            address=random_address(),
            tax_number=''.join(random.choices('0123456789', k=15)),
            credit_limit=random_amount(100000, 500000)
        )
        customers.append(customer)
    
    return customers

# 生成会计科目数据
def generate_accounts():
    """生成会计科目数据"""
    accounts = []
    
    # 资产类科目
    asset_accounts = [
        ('1001', '库存现金', 'asset'),
        ('1002', '银行存款', 'asset'),
        ('1122', '应收账款', 'asset'),
        ('1221', '其他应收款', 'asset'),
        ('1403', '原材料', 'asset'),
        ('1405', '库存商品', 'asset'),
        ('1601', '固定资产', 'asset'),
        ('1602', '累计折旧', 'asset')
    ]
    
    # 负债类科目
    liability_accounts = [
        ('2001', '短期借款', 'liability'),
        ('2202', '应付账款', 'liability'),
        ('2211', '应付职工薪酬', 'liability'),
        ('2221', '应交税费', 'liability'),
        ('2241', '其他应付款', 'liability')
    ]
    
    # 权益类科目
    equity_accounts = [
        ('4001', '实收资本', 'equity'),
        ('4101', '盈余公积', 'equity'),
        ('4103', '本年利润', 'equity'),
        ('4104', '利润分配', 'equity')
    ]
    
    # 收入类科目
    income_accounts = [
        ('6001', '主营业务收入', 'income'),
        ('6051', '其他业务收入', 'income'),
        ('6301', '营业外收入', 'income')
    ]
    
    # 费用类科目
    expense_accounts = [
        ('6601', '销售费用', 'expense'),
        ('6602', '管理费用', 'expense'),
        ('6603', '财务费用', 'expense'),
        ('6711', '营业外支出', 'expense')
    ]
    
    # 成本类科目
    cost_accounts = [
        ('5001', '生产成本', 'cost'),
        ('5101', '制造费用', 'cost')
    ]
    
    # 合并所有科目
    all_accounts = asset_accounts + liability_accounts + equity_accounts + income_accounts + expense_accounts + cost_accounts
    
    for code, name, type in all_accounts:
        account = Account(
            code=code,
            name=name,
            type=type,
            balance=0.0 if type in ['asset', 'liability', 'equity'] else 0.0
        )
        accounts.append(account)
    
    return accounts

# 生成采购订单数据
def generate_purchase_orders(users, suppliers, count=10):
    """生成采购订单数据"""
    purchase_orders = []
    
    for i in range(count):
        total_amount = random_amount(1000, 50000)
        tax_rate = random_tax_rate()
        tax_amount = round(total_amount * tax_rate, 2)
        
        # 随机选择创建人和审批人
        creator = random.choice(users)
        approver = random.choice([user for user in users if user.id != creator.id])
        
        # 随机选择供应商
        supplier = random.choice(suppliers)
        
        # 随机选择状态
        status = random.choice(['pending', 'approved', 'paid', 'completed'])
        
        purchase_order = PurchaseOrder(
            order_number=generate_order_number('PO'),
            supplier_id=supplier.id,
            total_amount=total_amount,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            payment_method=random.choice(['现金', '银行转账', '支票', '承兑汇票']),
            status=status,
            user_id=creator.id,
            approval_id=approver.id if status in ['approved', 'paid', 'completed'] else None,
            approval_time=random_datetime('-30d', 'now') if status in ['approved', 'paid', 'completed'] else None,
            payment_time=random_datetime('-30d', 'now') if status in ['paid', 'completed'] else None
        )
        
        purchase_orders.append(purchase_order)
    
    return purchase_orders

# 生成采购订单项数据
def generate_purchase_order_items(purchase_orders):
    """生成采购订单项数据"""
    purchase_order_items = []
    item_names = ['办公用品', '设备配件', '原材料', '包装材料', '电子产品', '维修工具', '办公家具', '清洁用品']
    
    for order in purchase_orders:
        # 每个订单生成1-5个订单项
        item_count = random.randint(1, 5)
        # 将Decimal转换为float以避免类型错误
        remaining_amount = float(order.total_amount)
        
        for i in range(item_count):
            # 最后一个订单项使用剩余金额
            if i == item_count - 1:
                amount = remaining_amount
            else:
                amount = random_amount(100, remaining_amount / 2)
                remaining_amount -= amount
            
            quantity = round(random.uniform(1, 100), 2)
            unit_price = round(amount / quantity, 2)
            
            item = PurchaseOrderItem(
                order_id=order.id,
                item_name=random.choice(item_names),
                quantity=quantity,
                unit_price=unit_price,
                amount=amount
            )
            
            purchase_order_items.append(item)
    
    return purchase_order_items

# 生成销售订单数据
def generate_sales_orders(users, customers, count=10):
    """生成销售订单数据"""
    sales_orders = []
    
    for i in range(count):
        total_amount = random_amount(1000, 50000)
        tax_rate = random_tax_rate()
        tax_amount = round(total_amount * tax_rate, 2)
        
        # 随机选择创建人和审批人
        creator = random.choice(users)
        approver = random.choice([user for user in users if user.id != creator.id])
        
        # 随机选择客户
        customer = random.choice(customers)
        
        # 随机选择状态
        status = random.choice(['pending', 'approved', 'paid', 'completed'])
        
        sales_order = SalesOrder(
            order_number=generate_order_number('SO'),
            customer_id=customer.id,
            total_amount=total_amount,
            tax_rate=tax_rate,
            tax_amount=tax_amount,
            payment_method=random.choice(['现金', '银行转账', '支票', '承兑汇票']),
            status=status,
            user_id=creator.id,
            approval_id=approver.id if status in ['approved', 'paid', 'completed'] else None,
            approval_time=random_datetime('-30d', 'now') if status in ['approved', 'paid', 'completed'] else None,
            payment_time=random_datetime('-30d', 'now') if status in ['paid', 'completed'] else None
        )
        
        sales_orders.append(sales_order)
    
    return sales_orders

# 生成销售订单项数据
def generate_sales_order_items(sales_orders):
    """生成销售订单项数据"""
    sales_order_items = []
    item_names = ['产品A', '产品B', '产品C', '服务1', '服务2', '配件1', '配件2', '套装产品']
    
    for order in sales_orders:
        # 每个订单生成1-5个订单项
        item_count = random.randint(1, 5)
        # 将Decimal转换为float以避免类型错误
        remaining_amount = float(order.total_amount)
        
        for i in range(item_count):
            # 最后一个订单项使用剩余金额
            if i == item_count - 1:
                amount = remaining_amount
            else:
                amount = random_amount(100, remaining_amount / 2)
                remaining_amount -= amount
            
            quantity = round(random.uniform(1, 100), 2)
            unit_price = round(amount / quantity, 2)
            
            item = SalesOrderItem(
                order_id=order.id,
                item_name=random.choice(item_names),
                quantity=quantity,
                unit_price=unit_price,
                amount=amount
            )
            
            sales_order_items.append(item)
    
    return sales_order_items

# 生成费用报销数据
def generate_expenses(users, count=15):
    """生成费用报销数据"""
    expenses = []
    expense_types = ['差旅费', '办公费', '招待费', '交通费', '通讯费', '其他费用']
    
    for i in range(count):
        # 随机选择报销人和审批人
        submitter = random.choice(users)
        approver = random.choice([user for user in users if user.id != submitter.id])
        
        # 随机选择状态
        status = random.choice(['pending', 'approved', 'paid', 'rejected'])
        
        expense = Expense(
            expense_number=generate_expense_number(),
            user_id=submitter.id,
            amount=random_amount(100, 5000),
            expense_type=random.choice(expense_types),
            description=random_text(),
            status=status,
            approval_id=approver.id if status in ['approved', 'paid', 'rejected'] else None,
            approval_time=random_datetime('-30d', 'now') if status in ['approved', 'paid', 'rejected'] else None,
            payment_time=random_datetime('-30d', 'now') if status == 'paid' else None
        )
        
        expenses.append(expense)
    
    return expenses

# 生成凭证数据
def generate_vouchers(users, count=20):
    """生成凭证数据"""
    vouchers = []
    
    for i in range(count):
        # 随机选择制单人和审核人
        creator = random.choice(users)
        approver = random.choice([user for user in users if user.id != creator.id])
        
        # 随机选择状态
        status = random.choice(['draft', 'approved', 'posted'])
        
        voucher = Voucher(
            voucher_number=generate_voucher_number(),
            date=random_date('-30d', 'now'),
            summary=random_text(max_length=50),
            status=status,
            user_id=creator.id,
            approval_id=approver.id if status in ['approved', 'posted'] else None,
            approval_time=random_datetime('-30d', 'now') if status in ['approved', 'posted'] else None,
            post_time=random_datetime('-30d', 'now') if status == 'posted' else None
        )
        
        vouchers.append(voucher)
    
    return vouchers

# 生成凭证分录数据
def generate_voucher_entries(vouchers, accounts):
    """生成凭证分录数据"""
    voucher_entries = []
    
    # 获取不同类型的科目
    asset_accounts = [acc for acc in accounts if acc.type == 'asset']
    liability_accounts = [acc for acc in accounts if acc.type == 'liability']
    equity_accounts = [acc for acc in accounts if acc.type == 'equity']
    income_accounts = [acc for acc in accounts if acc.type == 'income']
    expense_accounts = [acc for acc in accounts if acc.type == 'expense']
    cost_accounts = [acc for acc in accounts if acc.type == 'cost']
    
    for voucher in vouchers:
        # 每个凭证生成2-6个分录
        entry_count = random.randint(2, 6)
        
        # 确保借贷平衡
        total_debit = 0.0
        total_credit = 0.0
        
        # 生成借方分录
        debit_amount = random_amount(1000, 50000)
        total_debit += debit_amount
        
        # 选择借方科目（通常是资产、费用、成本）
        debit_account = random.choice(asset_accounts + expense_accounts + cost_accounts)
        
        debit_entry = VoucherEntry(
            voucher_id=voucher.id,
            account_code=debit_account.code,
            debit=debit_amount,
            credit=0.0,
            description=voucher.summary
        )
        
        voucher_entries.append(debit_entry)
        
        # 生成贷方分录
        # 可以是一个或多个贷方分录
        remaining_credit = debit_amount
        for i in range(entry_count - 1):
            if i == entry_count - 2:
                credit_amount = remaining_credit
            else:
                credit_amount = random_amount(100, remaining_credit / 2)
                remaining_credit -= credit_amount
            
            total_credit += credit_amount
            
            # 选择贷方科目（通常是负债、权益、收入）
            credit_account = random.choice(liability_accounts + equity_accounts + income_accounts)
            
            credit_entry = VoucherEntry(
                voucher_id=voucher.id,
                account_code=credit_account.code,
                debit=0.0,
                credit=credit_amount,
                description=voucher.summary
            )
            
            voucher_entries.append(credit_entry)
    
    return voucher_entries

# 生成预算数据
def generate_budgets(count=10):
    """生成预算数据"""
    budgets = []
    departments = ['销售部', '市场部', '财务部', '人力资源部', '技术部', '生产部', '采购部']
    used_department_year = set()
    current_year = datetime.now().year
    
    while len(budgets) < count:
        department = random.choice(departments)
        year = current_year - random.randint(0, 2)  # 生成最近3年的预算
        
        # 确保部门和年份组合唯一
        if (department, year) not in used_department_year:
            used_department_year.add((department, year))
            budget_amount = random_amount(100000, 5000000)
            used_amount = random_amount(0, budget_amount * 0.8)
            
            budget = Budget(
                department=department,
                budget_amount=budget_amount,
                used_amount=used_amount,
                year=year,
                status=random.choice(['draft', 'approved', 'active'])
            )
            
            budgets.append(budget)
    
    return budgets

# 生成税务数据
def generate_taxes(count=10):
    """生成税务数据"""
    taxes = []
    tax_types = ['增值税', '企业所得税', '个人所得税', '城市维护建设税', '教育费附加', '地方教育附加']
    
    for i in range(count):
        # 随机选择状态
        status = random.choice(['pending', 'submitted', 'approved'])
        
        tax = Tax(
            tax_type=random.choice(tax_types),
            tax_period=random_date('-60d', 'now').strftime('%Y-%m'),
            amount=random_amount(1000, 100000),
            status=status,
            submit_time=random_datetime('-30d', 'now') if status in ['submitted', 'approved'] else None,
            approval_time=random_datetime('-30d', 'now') if status == 'approved' else None
        )
        
        taxes.append(tax)
    
    return taxes

# 主函数
def main():
    with app.app_context():
        # 删除现有测试数据（可选）
        print("正在清理现有测试数据...")
        
        # 注意：删除顺序很重要，要先删除有外键依赖的表
        db.session.query(PurchaseOrderItem).delete()
        db.session.query(SalesOrderItem).delete()
        db.session.query(VoucherEntry).delete()
        db.session.query(PurchaseOrder).delete()
        db.session.query(SalesOrder).delete()
        db.session.query(Voucher).delete()
        db.session.query(Expense).delete()
        db.session.query(Tax).delete()
        db.session.query(Budget).delete()
        db.session.query(Customer).delete()
        db.session.query(Supplier).delete()
        # db.session.query(User).delete()
        db.session.query(Account).delete()
        
        db.session.commit()
        print("清理完成！")
        
        # 生成测试数据
        print("正在生成测试数据...")
        
        # 1. 生成会计科目
        print("生成会计科目...")
        accounts = generate_accounts()
        db.session.add_all(accounts)
        db.session.commit()
        print(f"生成了 {len(accounts)} 个会计科目")
        
        # 2. 生成用户
        print("生成用户...")
        users = generate_users(count=10)
        db.session.add_all(users)
        db.session.commit()
        print(f"生成了 {len(users)} 个用户")
        
        # 3. 生成供应商
        print("生成供应商...")
        suppliers = generate_suppliers(count=15)
        db.session.add_all(suppliers)
        db.session.commit()
        print(f"生成了 {len(suppliers)} 个供应商")
        
        # 4. 生成客户
        print("生成客户...")
        customers = generate_customers(count=15)
        db.session.add_all(customers)
        db.session.commit()
        print(f"生成了 {len(customers)} 个客户")
        
        # 5. 生成采购订单
        print("生成采购订单...")
        purchase_orders = generate_purchase_orders(users, suppliers, count=15)
        db.session.add_all(purchase_orders)
        db.session.commit()
        print(f"生成了 {len(purchase_orders)} 个采购订单")
        
        # 6. 生成采购订单项
        print("生成采购订单项...")
        purchase_order_items = generate_purchase_order_items(purchase_orders)
        db.session.add_all(purchase_order_items)
        db.session.commit()
        print(f"生成了 {len(purchase_order_items)} 个采购订单项")
        
        # 7. 生成销售订单
        print("生成销售订单...")
        sales_orders = generate_sales_orders(users, customers, count=15)
        db.session.add_all(sales_orders)
        db.session.commit()
        print(f"生成了 {len(sales_orders)} 个销售订单")
        
        # 8. 生成销售订单项
        print("生成销售订单项...")
        sales_order_items = generate_sales_order_items(sales_orders)
        db.session.add_all(sales_order_items)
        db.session.commit()
        print(f"生成了 {len(sales_order_items)} 个销售订单项")
        
        # 9. 生成费用报销
        print("生成费用报销...")
        expenses = generate_expenses(users, count=20)
        db.session.add_all(expenses)
        db.session.commit()
        print(f"生成了 {len(expenses)} 个费用报销")
        
        # 10. 生成凭证
        print("生成凭证...")
        vouchers = generate_vouchers(users, count=25)
        db.session.add_all(vouchers)
        db.session.commit()
        print(f"生成了 {len(vouchers)} 个凭证")
        
        # 11. 生成凭证分录
        print("生成凭证分录...")
        voucher_entries = generate_voucher_entries(vouchers, accounts)
        db.session.add_all(voucher_entries)
        db.session.commit()
        print(f"生成了 {len(voucher_entries)} 个凭证分录")
        
        # 12. 生成预算
        print("生成预算...")
        budgets = generate_budgets(count=12)
        db.session.add_all(budgets)
        db.session.commit()
        print(f"生成了 {len(budgets)} 个预算")
        
        # 13. 生成税务
        print("生成税务...")
        taxes = generate_taxes(count=12)
        db.session.add_all(taxes)
        db.session.commit()
        print(f"生成了 {len(taxes)} 个税务记录")
        
        print("测试数据生成完成！")

if __name__ == "__main__":
    main()
