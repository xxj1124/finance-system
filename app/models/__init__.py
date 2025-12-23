from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import json

# 创建数据库实例
db = SQLAlchemy()

# 基础模型类
class BaseModel(db.Model):
    __abstract__ = True
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    create_time = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    is_deleted = db.Column(db.Boolean, default=False, comment='是否删除')

# 企业信息模型
class Company(BaseModel):
    __tablename__ = 'company'
    name = db.Column(db.String(100), nullable=False, unique=True, comment='企业名称')
    registered_capital = db.Column(db.DECIMAL(15, 2), nullable=False, comment='注册资金')
    industry = db.Column(db.String(50), nullable=False, comment='行业类型')
    accounting_period = db.Column(db.String(20), nullable=False, comment='会计期间')
    currency = db.Column(db.String(10), nullable=False, default='CNY', comment='币种')
    enabled_modules = db.Column(db.Text, nullable=True, comment='启用模块')
    
    @property
    def modules(self):
        if self.enabled_modules:
            return json.loads(self.enabled_modules)
        return []
    
    @modules.setter
    def modules(self, value):
        self.enabled_modules = json.dumps(value)

# 用户模型
class User(BaseModel):
    __tablename__ = 'user'
    username = db.Column(db.String(50), nullable=False, unique=True, comment='用户名')
    password = db.Column(db.String(100), nullable=False, comment='密码')
    real_name = db.Column(db.String(50), nullable=False, comment='真实姓名')
    role = db.Column(db.String(20), nullable=False, default='user', comment='角色')  # admin, manager, user
    email = db.Column(db.String(100), nullable=True, comment='邮箱')
    phone = db.Column(db.String(20), nullable=True, comment='电话')

# 会计科目模型
class Account(BaseModel):
    __tablename__ = 'account'
    code = db.Column(db.String(20), nullable=False, unique=True, comment='科目编码')
    name = db.Column(db.String(100), nullable=False, comment='科目名称')
    type = db.Column(db.String(20), nullable=False, comment='科目类型: asset, liability, equity, income, expense, cost')
    parent_code = db.Column(db.String(20), nullable=True, comment='父科目编码')
    description = db.Column(db.Text, nullable=True, comment='科目描述')
    balance = db.Column(db.DECIMAL(15, 2), nullable=False, default=0.0, comment='当前余额')

# 供应商模型
class Supplier(BaseModel):
    __tablename__ = 'supplier'
    name = db.Column(db.String(100), nullable=False, unique=True, comment='供应商名称')
    contact = db.Column(db.String(50), nullable=False, comment='联系人')
    phone = db.Column(db.String(20), nullable=False, comment='联系电话')
    email = db.Column(db.String(100), nullable=True, comment='邮箱')
    address = db.Column(db.String(200), nullable=True, comment='地址')
    tax_number = db.Column(db.String(50), nullable=True, comment='纳税人识别号')
    bank_account = db.Column(db.String(50), nullable=True, comment='银行账号')

# 客户模型
class Customer(BaseModel):
    __tablename__ = 'customer'
    name = db.Column(db.String(100), nullable=False, unique=True, comment='客户名称')
    contact = db.Column(db.String(50), nullable=False, comment='联系人')
    phone = db.Column(db.String(20), nullable=False, comment='联系电话')
    email = db.Column(db.String(100), nullable=True, comment='邮箱')
    address = db.Column(db.String(200), nullable=True, comment='地址')
    tax_number = db.Column(db.String(50), nullable=True, comment='纳税人识别号')
    credit_limit = db.Column(db.DECIMAL(15, 2), nullable=False, default=0.0, comment='信用额度')

# 采购订单模型
class PurchaseOrder(BaseModel):
    __tablename__ = 'purchase_order'
    order_number = db.Column(db.String(50), nullable=False, unique=True, comment='订单编号')
    supplier_id = db.Column(db.Integer, db.ForeignKey('supplier.id'), nullable=False, comment='供应商ID')
    total_amount = db.Column(db.DECIMAL(15, 2), nullable=False, comment='总金额')
    tax_rate = db.Column(db.DECIMAL(5, 2), nullable=False, comment='税率')
    tax_amount = db.Column(db.DECIMAL(15, 2), nullable=False, comment='税额')
    payment_method = db.Column(db.String(20), nullable=False, comment='支付方式')
    status = db.Column(db.String(20), nullable=False, comment='状态: pending, approved, paid, completed, cancelled')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='创建人ID')
    approval_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, comment='审批人ID')
    approval_time = db.Column(db.DateTime, nullable=True, comment='审批时间')
    payment_time = db.Column(db.DateTime, nullable=True, comment='支付时间')
    
    # 关系
    supplier = db.relationship('Supplier', backref=db.backref('purchase_orders', lazy='dynamic'))
    items = db.relationship('PurchaseOrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

# 采购订单项模型
class PurchaseOrderItem(BaseModel):
    __tablename__ = 'purchase_order_item'
    order_id = db.Column(db.Integer, db.ForeignKey('purchase_order.id'), nullable=False, comment='订单ID')
    item_name = db.Column(db.String(100), nullable=False, comment='项目名称')
    quantity = db.Column(db.DECIMAL(10, 2), nullable=False, comment='数量')
    unit_price = db.Column(db.DECIMAL(10, 2), nullable=False, comment='单价')
    amount = db.Column(db.DECIMAL(15, 2), nullable=False, comment='金额')

# 销售订单模型
class SalesOrder(BaseModel):
    __tablename__ = 'sales_order'
    order_number = db.Column(db.String(50), nullable=False, unique=True, comment='订单编号')
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False, comment='客户ID')
    total_amount = db.Column(db.DECIMAL(15, 2), nullable=False, comment='总金额')
    tax_rate = db.Column(db.DECIMAL(5, 2), nullable=False, comment='税率')
    tax_amount = db.Column(db.DECIMAL(15, 2), nullable=False, comment='税额')
    payment_method = db.Column(db.String(20), nullable=False, comment='支付方式')
    status = db.Column(db.String(20), nullable=False, comment='状态: pending, approved, paid, completed, cancelled')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='创建人ID')
    approval_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, comment='审批人ID')
    approval_time = db.Column(db.DateTime, nullable=True, comment='审批时间')
    payment_time = db.Column(db.DateTime, nullable=True, comment='支付时间')
    
    # 关系
    customer = db.relationship('Customer', backref=db.backref('sales_orders', lazy='dynamic'))
    items = db.relationship('SalesOrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')

# 销售订单项模型
class SalesOrderItem(BaseModel):
    __tablename__ = 'sales_order_item'
    order_id = db.Column(db.Integer, db.ForeignKey('sales_order.id'), nullable=False, comment='订单ID')
    item_name = db.Column(db.String(100), nullable=False, comment='项目名称')
    quantity = db.Column(db.DECIMAL(10, 2), nullable=False, comment='数量')
    unit_price = db.Column(db.DECIMAL(10, 2), nullable=False, comment='单价')
    amount = db.Column(db.DECIMAL(15, 2), nullable=False, comment='金额')

# 费用报销模型
class Expense(BaseModel):
    __tablename__ = 'expense'
    expense_number = db.Column(db.String(50), nullable=False, unique=True, comment='报销单号')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='报销人ID')
    amount = db.Column(db.DECIMAL(15, 2), nullable=False, comment='报销金额')
    expense_type = db.Column(db.String(50), nullable=False, comment='费用类型')
    description = db.Column(db.Text, nullable=True, comment='费用说明')
    status = db.Column(db.String(20), nullable=False, comment='状态: pending, approved, paid, rejected')
    approval_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, comment='审批人ID')
    approval_time = db.Column(db.DateTime, nullable=True, comment='审批时间')
    payment_time = db.Column(db.DateTime, nullable=True, comment='支付时间')
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('expenses', lazy='dynamic'))
    approver = db.relationship('User', foreign_keys=[approval_id])

# 凭证模型
class Voucher(BaseModel):
    __tablename__ = 'voucher'
    voucher_number = db.Column(db.String(50), nullable=False, unique=True, comment='凭证编号')
    date = db.Column(db.Date, nullable=False, default=datetime.now, comment='凭证日期')
    summary = db.Column(db.String(200), nullable=False, comment='摘要')
    status = db.Column(db.String(20), nullable=False, default='draft', comment='状态: draft, approved, posted')
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False, comment='制单人ID')
    approval_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True, comment='审核人ID')
    approval_time = db.Column(db.DateTime, nullable=True, comment='审核时间')
    post_time = db.Column(db.DateTime, nullable=True, comment='过账时间')
    
    # 关系
    user = db.relationship('User', foreign_keys=[user_id], backref=db.backref('vouchers', lazy='dynamic'))
    approver = db.relationship('User', foreign_keys=[approval_id])
    entries = db.relationship('VoucherEntry', backref='voucher', lazy='select', cascade='all, delete-orphan')

# 凭证分录模型
class VoucherEntry(BaseModel):
    __tablename__ = 'voucher_entry'
    voucher_id = db.Column(db.Integer, db.ForeignKey('voucher.id'), nullable=False, comment='凭证ID')
    account_code = db.Column(db.String(20), db.ForeignKey('account.code'), nullable=False, comment='科目编码')
    debit = db.Column(db.DECIMAL(15, 2), nullable=False, default=0.0, comment='借方金额')
    credit = db.Column(db.DECIMAL(15, 2), nullable=False, default=0.0, comment='贷方金额')
    description = db.Column(db.String(200), nullable=True, comment='摘要')
    
    # 关系
    account = db.relationship('Account')

# 预算模型
class Budget(BaseModel):
    __tablename__ = 'budget'
    department = db.Column(db.String(50), nullable=False, comment='部门')
    budget_amount = db.Column(db.DECIMAL(15, 2), nullable=False, comment='预算金额')
    used_amount = db.Column(db.DECIMAL(15, 2), nullable=False, default=0.0, comment='已使用金额')
    year = db.Column(db.Integer, nullable=False, comment='预算年度')
    status = db.Column(db.String(20), nullable=False, default='draft', comment='状态: draft, approved, active')
    
    # 联合唯一约束
    __table_args__ = (db.UniqueConstraint('department', 'year', name='_department_year_uc'),)

# 税务模型
class Tax(BaseModel):
    __tablename__ = 'tax'
    tax_type = db.Column(db.String(50), nullable=False, comment='税种')
    tax_period = db.Column(db.String(20), nullable=False, comment='申报期')
    amount = db.Column(db.DECIMAL(15, 2), nullable=False, comment='申报金额')
    status = db.Column(db.String(20), nullable=False, default='pending', comment='状态: pending, submitted, approved')
    submit_time = db.Column(db.DateTime, nullable=True, comment='申报时间')
    approval_time = db.Column(db.DateTime, nullable=True, comment='审批时间')


