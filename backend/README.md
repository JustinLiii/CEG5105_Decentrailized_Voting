# 基于盲签名的匿名账户分配系统

该系统实现了一种基于RSA盲签名的匿名账户分配机制，可用于区块链投票等需要匿名但可验证的场景。

## 系统架构

系统分为两个主要组件：

1. **管理员端 (assign.py)**：
   - 对用户的盲签名请求进行签名
   - 验证用户的签名有效性
   - 分配匿名账户给已验证的用户
   - 确保每个签名只能使用一次（防止双重分配）

2. **用户端 (assign_user.py / assign_user_complete.py)**：
   - 计算用户身份信息的哈希值
   - 对哈希值进行盲化处理
   - 获取管理员的盲签名并解盲
   - 使用有效签名申请匿名账户

3. **服务器端 (server.py)**：
   - 提供HTTP API接口
   - 处理盲签名请求
   - 处理账户分配请求
   - 健康检查接口

4. **初始化工具 (setup.py)**：
   - 生成RSA密钥对
   - 初始化数据库表结构
   - 添加测试账户到账户池

## 工作原理

### 盲签名流程

1. **用户端**：
   - 将用户身份信息（身份证号、姓名等）计算SHA-256哈希
   - 使用随机盲因子和管理员公钥对哈希值进行盲化
   - 将盲化后的消息发送给管理员

2. **管理员端**：
   - 使用私钥对盲化消息进行签名
   - 返回盲签名给用户

3. **用户端**：
   - 对盲签名使用盲因子进行解盲
   - 得到对原始哈希的有效签名
   - 使用该签名申请匿名账户

该系统通过盲签名技术确保以下几点：

1. **隐私保护**：管理员永远不会看到用户的明文身份信息
2. **防止重复领取**：每个用户只能获得一个匿名账户
3. **匿名性**：无法将匿名账户与用户身份关联起来
4. **不可否认性**：用户无法伪造有效的签名

## 系统组件说明

### 核心模块

- **blind_signature/rsa.py**：提供RSA盲签名算法实现
  - `blind()` - 盲化消息
  - `sign()` - 对盲化消息签名
  - `unblind()` - 解盲签名
  - `verify()` - 验证签名

- **assign.py**：匿名账户分配器实现
  - `sign_blinded_identity()` - 对盲化消息签名
  - `verify_signature()` - 验证签名
  - `is_signature_used()` - 检查签名是否已使用
  - `assign_account()` - 分配匿名账户

- **server.py**：HTTP API服务器
  - `/blind_sign` - 处理盲签名请求
  - `/assign_account` - 处理账户分配请求
  - `/health` - 健康检查

### 辅助工具

- **dummy_db.py**：内存数据库模拟，用于测试
- **setup.py**：系统初始化工具

## 安装与配置

### 环境要求

- Python 3.6+
- MySQL数据库（或兼容服务）

### 安装依赖

```bash
pip install pycryptodome pymysql requests flask
```

### 初始化系统

1. 生成密钥和初始化数据库：

```bash
# 使用默认配置
python setup.py

# 自定义数据库连接
python setup.py --db-host localhost --db-user root --db-password yourpassword --db-name accounts
```

2. 启动服务器：

```bash
# 设置环境变量（可选）
export PRIVATE_KEY_PATH=private.pem
export PUBLIC_KEY_PATH=public.pem
export DB_HOST=localhost
export DB_USER=root
export DB_PASSWORD=114514
export DB_NAME=anonymous_accounts

# 启动服务器
python server.py
```

## 使用方法

### 用户申请匿名账户

使用完整的用户端工具：

```bash
python assign_user_complete.py --id 123456789012345678 --name "张三" --server http://localhost:5000
```

成功后将生成一个JSON文件（`张三_account.json`），包含分配到的匿名账户地址。

## 测试

系统提供了三种类型的测试：

1. **管理员端测试 (test_assign.py)**
   - 测试签名生成和验证功能
   - 测试账户分配逻辑
   - 测试防止重复使用签名的机制

2. **用户端测试 (test_assign_user.py)**
   - 测试用户身份哈希计算
   - 测试盲化消息过程
   - 测试签名验证逻辑

3. **集成测试 (test_integration.py)**
   - 端到端测试完整的盲签名与账户分配流程
   - 测试隐私保护机制
   - 测试防双重分配机制

4. **完整测试套件 (test_all.py)**
   - 包含所有测试用例
   - 使用内存数据库模拟

### 运行测试

```bash
# 安装测试依赖
pip install pycryptodome pymysql requests

# 运行单元测试
python -m unittest test_assign.py
python -m unittest test_assign_user.py

# 运行集成测试
python -m unittest test_integration.py

# 运行所有测试
python -m unittest test_all.py
```

## 安全注意事项

1. **通信安全**：实际部署时，服务器应该使用HTTPS加密通信
2. **密钥保护**：私钥应妥善保存，建议使用HSM（硬件安全模块）
3. **数据库安全**：数据库应进行适当的权限和加密设置
4. **隐私保护**：用户身份信息只在客户端使用，从不发送原始数据给服务器
5. **防重放攻击**：系统已实现签名的一次性使用检查，防止重复领取账户

## 扩展与改进

1. **多种身份验证**：支持不同类型的用户身份信息
2. **多级权限**：引入不同权限级别的账户分配
3. **更多加密算法**：支持ECC等其他加密算法的盲签名
4. **区块链集成**：直接与区块链网络集成，支持智能合约交互

## 协议与许可

该项目基于MIT许可证开源 