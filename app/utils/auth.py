#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
认证工具模块
"""

from functools import wraps
from flask import session, redirect, url_for, flash


def login_required(f):
    """
    登录保护装饰器
    用于保护需要登录才能访问的路由
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查session中是否存在user_id
        if 'user_id' not in session:
            # 如果未登录，重定向到登录页面
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    """
    角色保护装饰器
    用于限制特定角色的用户才能访问的路由
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 检查是否已登录
            if 'user_id' not in session:
                return redirect(url_for('main.login'))
            # 检查角色是否匹配
            if 'role' not in session or session['role'] != role:
                flash('您没有权限执行此操作！', 'danger')
                return redirect(url_for('main.dashboard'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


def admin_required(f):
    """
    管理员权限装饰器
    限制只有管理员才能访问的路由
    """
    return role_required('admin')(f)


def manager_required(f):
    """
    经理权限装饰器
    限制只有经理才能访问的路由
    """
    return role_required('manager')(f)
