#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
用户认证模块
"""

from flask import render_template, request, redirect, url_for, flash, session
from app.models import db, User
from app.views import main_bp
from werkzeug.security import generate_password_hash, check_password_hash

# 登录路由
@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    """用户登录"""
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # 查找用户
        user = User.query.filter_by(username=username, is_deleted=False).first()
        
        if user and check_password_hash(user.password, password):
            # 登录成功，保存用户信息到session
            session['user_id'] = user.id
            session['username'] = user.username
            session['role'] = user.role
            flash('登录成功！', 'success')
            return redirect(url_for('main.dashboard'))
        else:
            flash('用户名或密码错误！', 'danger')
    return render_template('auth/login.html')

# 注册路由
@main_bp.route('/register', methods=['GET', 'POST'])
def register():
    """用户注册"""
    if request.method == 'POST':
        try:
            username = request.form['username']
            password = request.form['password']
            real_name = request.form['real_name']
            email = request.form.get('email')
            phone = request.form.get('phone')
            
            # 检查用户名是否已存在
            existing_user = User.query.filter_by(username=username, is_deleted=False).first()
            if existing_user:
                flash('用户名已存在！', 'danger')
                return redirect(url_for('main.register'))
            
            # 创建新用户
            new_user = User(
                username=username,
                password=generate_password_hash(password),
                real_name=real_name,
                email=email,
                phone=phone
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash('注册成功！', 'success')
            return redirect(url_for('main.login'))
        except Exception as e:
            db.session.rollback()
            flash(f'注册失败: {str(e)}', 'danger')
    return render_template('auth/register.html')

# 登出路由
@main_bp.route('/logout')
def logout():
    """用户登出"""
    session.clear()
    flash('已成功登出！', 'success')
    return redirect(url_for('main.login'))

# 密码修改路由
@main_bp.route('/change_password', methods=['GET', 'POST'])
def change_password():
    """修改密码"""
    if 'user_id' not in session:
        return redirect(url_for('main.login'))
    
    if request.method == 'POST':
        try:
            old_password = request.form['old_password']
            new_password = request.form['new_password']
            confirm_password = request.form['confirm_password']
            
            user = User.query.get(session['user_id'])
            
            # 验证旧密码
            if not check_password_hash(user.password, old_password):
                flash('旧密码错误！', 'danger')
                return redirect(url_for('main.change_password'))
            
            # 验证新密码
            if new_password != confirm_password:
                flash('新密码与确认密码不匹配！', 'danger')
                return redirect(url_for('main.change_password'))
            
            # 更新密码
            user.password = generate_password_hash(new_password)
            db.session.commit()
            
            flash('密码修改成功！', 'success')
            return redirect(url_for('main.dashboard'))
        except Exception as e:
            db.session.rollback()
            flash(f'密码修改失败: {str(e)}', 'danger')
    return render_template('auth/change_password.html')
