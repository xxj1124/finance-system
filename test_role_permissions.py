#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
角色权限测试脚本
测试普通用户和管理员用户的权限控制
"""

import requests
import json

# 测试配置
BASE_URL = 'http://127.0.0.1:5000'

# 测试用户信息
TEST_USERS = {
    'admin': {'username': 'admin', 'password': 'admin123'},  # 管理员
    'user': {'username': 'user5', 'password': 'user5123'}     # 普通用户
}

# 测试路由列表
TEST_ROUTES = {
    'voucher_list': '/voucher/list',
    'voucher_add': '/voucher/add',
    'voucher_approve': '/voucher/approve/1',  # 假设存在ID为1的凭证
    'voucher_post': '/voucher/post/1',         # 假设存在ID为1的凭证
    'voucher_delete': '/voucher/delete/1'      # 假设存在ID为1的凭证
}


def login(username, password):
    """
    登录测试用户，返回session对象
    """
    session = requests.Session()
    login_url = f'{BASE_URL}/login'
    
    # 先GET获取CSRF令牌（如果有）
    session.get(login_url)
    
    # POST登录请求
    login_data = {
        'username': username,
        'password': password,
        'submit': '登录'
    }
    
    response = session.post(login_url, data=login_data, allow_redirects=True)
    
    # 检查是否登录成功
    if 'dashboard' in response.url:
        print(f"✓ 用户 {username} 登录成功")
        return session
    else:
        print(f"✗ 用户 {username} 登录失败")
        print(f"  响应URL: {response.url}")
        return None


def test_route_access(session, route_name, route_url, method='GET'):
    """
    测试用户对特定路由的访问权限
    """
    url = f'{BASE_URL}{route_url}'
    
    if method == 'GET':
        response = session.get(url, allow_redirects=True)
    else:
        response = session.post(url, allow_redirects=True)
    
    # 检查响应
    if response.status_code == 200:
        if '您没有权限执行此操作' in response.text:
            print(f"✓ {route_name}: 访问被拒绝（权限不足）")
            return 'forbidden'
        else:
            print(f"✓ {route_name}: 访问成功")
            return 'allowed'
    else:
        print(f"✗ {route_name}: 访问失败（状态码: {response.status_code}）")
        return 'error'


def test_user_permissions():
    """
    测试不同用户角色的权限
    """
    print("\n=== 开始角色权限测试 ===")
    
    for user_type, user_info in TEST_USERS.items():
        print(f"\n--- 测试 {user_type} 用户 ({user_info['username']}) ---")
        
        # 登录用户
        session = login(user_info['username'], user_info['password'])
        if not session:
            continue
        
        # 测试各个路由
        print("\n路由访问测试：")
        for route_name, route_url in TEST_ROUTES.items():
            test_route_access(session, route_name, route_url)


if __name__ == '__main__':
    test_user_permissions()
