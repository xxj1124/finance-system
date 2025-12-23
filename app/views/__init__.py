#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视图模块
"""

from flask import Blueprint

# 创建主蓝图
main_bp = Blueprint('main', __name__)

# 导入所有视图
from app.views import company
from app.views import purchase
from app.views import sales
from app.views import expense
from app.views import account
from app.views import report
from app.views import auth
from app.views import budget
from app.views import tax