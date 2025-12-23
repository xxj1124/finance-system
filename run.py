#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
应用启动文件
"""

from app import app

if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)