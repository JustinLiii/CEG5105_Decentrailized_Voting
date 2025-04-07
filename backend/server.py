#!/usr/bin/env python3
"""
匿名账户分配系统 - 服务器端
"""

from flask import Flask, request, jsonify
import os
import pymysql
from assign import AnonymousAccountAllocatorDB

app = Flask(__name__)

# 数据库配置
DB_CONFIG = {
    'host': os.environ.get('DB_HOST', 'localhost'),
    'user': os.environ.get('DB_USER', 'root'),
    'password': os.environ.get('DB_PASSWORD', '114514'),
    'db': os.environ.get('DB_NAME', 'anonymous_accounts'),
}

# 密钥文件路径
PRIVATE_KEY_PATH = os.environ.get('PRIVATE_KEY_PATH', 'private.pem')
PUBLIC_KEY_PATH = os.environ.get('PUBLIC_KEY_PATH', 'public.pem')

# 全局账户分配器实例
allocator = None

@app.before_first_request
def initialize_allocator():
    """初始化账户分配器"""
    global allocator
    try:
        allocator = AnonymousAccountAllocatorDB(
            DB_CONFIG,
            PRIVATE_KEY_PATH,
            PUBLIC_KEY_PATH
        )
    except Exception as e:
        app.logger.error(f"初始化账户分配器失败: {e}")


@app.route('/blind_sign', methods=['POST'])
def blind_sign():
    """处理盲签名请求"""
    if not allocator:
        return jsonify({'error': '服务器未正确初始化'}), 500

    data = request.json
    if not data or 'blinded_message' not in data:
        return jsonify({'error': '缺少必要参数'}), 400

    try:
        blinded_message = int(data['blinded_message'])
        blind_signature = allocator.sign_blinded_identity(blinded_message)
        return jsonify({'blind_signature': str(blind_signature)})
    except Exception as e:
        app.logger.error(f"盲签名失败: {e}")
        return jsonify({'error': f'处理请求失败: {str(e)}'}), 500


@app.route('/assign_account', methods=['POST'])
def assign_account():
    """处理账户分配请求"""
    if not allocator:
        return jsonify({'error': '服务器未正确初始化'}), 500

    data = request.json
    if not data or 'user_info' not in data or 'signature' not in data:
        return jsonify({'error': '缺少必要参数'}), 400

    try:
        user_info = data['user_info']
        signature = int(data['signature'])

        # 分配账户
        account_address = allocator.assign_account(user_info, signature)
        return jsonify({'account_address': account_address})
    except Exception as e:
        app.logger.error(f"分配账户失败: {e}")
        return jsonify({'error': f'处理请求失败: {str(e)}'}), 500


@app.route('/health', methods=['GET'])
def health_check():
    """健康检查接口"""
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    # 设置环境变量以进行初始化
    # 例如: os.environ['PRIVATE_KEY_PATH'] = 'path/to/private.pem'
    
    # 启动服务器
    app.run(host='0.0.0.0', port=5000, debug=True) 