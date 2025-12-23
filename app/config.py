import os

class Config:
    # 项目基础目录
    BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    
    # 数据库配置 - 使用SQLite
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{os.path.join(BASE_DIR, "finance.db")}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 安全配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hard to guess string'
    
    # 系统配置
    PER_PAGE = 10  # 分页大小
    
    # 模板配置
    TEMPLATES_AUTO_RELOAD = True
    DEBUG = True
    
    # 会计科目默认模板
    DEFAULT_ACCOUNT_TEMPLATE = [
        {'code': '1001', 'name': '库存现金', 'type': 'asset', 'parent_code': ''},
        {'code': '1002', 'name': '银行存款', 'type': 'asset', 'parent_code': ''},
        {'code': '1122', 'name': '应收账款', 'type': 'asset', 'parent_code': ''},
        {'code': '1123', 'name': '预付账款', 'type': 'asset', 'parent_code': ''},
        {'code': '1403', 'name': '原材料', 'type': 'asset', 'parent_code': ''},
        {'code': '1405', 'name': '库存商品', 'type': 'asset', 'parent_code': ''},
        {'code': '1601', 'name': '固定资产', 'type': 'asset', 'parent_code': ''},
        {'code': '2202', 'name': '应付账款', 'type': 'liability', 'parent_code': ''},
        {'code': '2203', 'name': '预收账款', 'type': 'liability', 'parent_code': ''},
        {'code': '2211', 'name': '应付职工薪酬', 'type': 'liability', 'parent_code': ''},
        {'code': '2221', 'name': '应交税费', 'type': 'liability', 'parent_code': ''},
        {'code': '4001', 'name': '实收资本', 'type': 'equity', 'parent_code': ''},
        {'code': '5001', 'name': '生产成本', 'type': 'cost', 'parent_code': ''},
        {'code': '5101', 'name': '制造费用', 'type': 'cost', 'parent_code': ''},
        {'code': '6001', 'name': '主营业务收入', 'type': 'income', 'parent_code': ''},
        {'code': '6051', 'name': '其他业务收入', 'type': 'income', 'parent_code': ''},
        {'code': '6401', 'name': '主营业务成本', 'type': 'expense', 'parent_code': ''},
        {'code': '6402', 'name': '其他业务成本', 'type': 'expense', 'parent_code': ''},
        {'code': '6601', 'name': '销售费用', 'type': 'expense', 'parent_code': ''},
        {'code': '6602', 'name': '管理费用', 'type': 'expense', 'parent_code': ''},
        {'code': '6603', 'name': '财务费用', 'type': 'expense', 'parent_code': ''},
    ]
