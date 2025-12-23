#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用初始化文件
"""

from flask import Flask
from app.config import Config
from app.models import db
import math

# 创建应用实例
def create_app(config_name='default'):
    """
    创建应用实例
    :param config_name: 配置名称
    :return: Flask应用实例
    """
    app = Flask(__name__)
    
    # 加载配置
    app.config.from_object(Config)
    
    # 初始化数据库
    db.init_app(app)
    
    # 注册蓝图
    from app.views import main_bp
    app.register_blueprint(main_bp)
    
    # 注册模板全局函数
    app.jinja_env.globals.update(abs=abs)
    
    # 创建数据库表
    with app.app_context():
        db.create_all()
    
    return app

# 创建默认应用实例
app = create_app()