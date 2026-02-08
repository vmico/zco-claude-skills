#!/usr/bin/env python3
"""
Python 注释规范示例代码。

演示如何正确使用 ##; 和 ##;@ 注释。
"""

from dataclasses import dataclass
from typing import Optional


##; 示例代码：演示注释规范的使用

##;@NOTE: 这个文件展示了如何正确使用 ##; 和 ##;@ 注释


##; User 表示系统用户
##; 包含用户的基本信息和认证数据
@dataclass
class User:
    id: Optional[int] = None
    name: str = ""
    email: str = ""
    password: str = ""  ##;@FIXME: 应该存储哈希值而不是明文密码


##; validate_email 验证邮箱格式是否正确
##; 返回 True 表示邮箱格式有效
def validate_email(email: str) -> bool:
    ##; 检查邮箱是否包含 @ 符号
    if "@" not in email:
        return False

    ##;@TODO: 添加更完整的邮箱格式验证
    ##;@OPTIMIZE: 可以使用正则表达式提高验证准确性

    ##; 检查 @ 符号前后是否有内容
    parts = email.split("@")
    if len(parts) != 2 or not parts[0] or not parts[1]:
        return False

    return True


##; create_user 创建新用户
##; 验证用户数据并返回创建的用户对象
def create_user(name: str, email: str, password: str) -> User:
    ##;@NOTE: 这个函数需要重构，参数太多

    ##; 验证用户名
    if not name:
        raise ValueError("Name cannot be empty")

    ##; 验证邮箱
    if not validate_email(email):
        raise ValueError("Invalid email format")

    ##;@FIXME: 密码验证规则太简单，需要加强
    ##; 验证密码长度
    if len(password) < 6:
        raise ValueError("Password too short")

    ##;@HACK: 临时方案 - 直接存储明文密码
    ##;@等待安全团队提供密码哈希方案后修改
    user = User(
        name=name,
        email=email,
        password=password,  ##; 应该存储哈希值
    )

    ##;@TODO: 添加到数据库
    ##;@TODO: 发送欢迎邮件
    ##;@TODO: 记录审计日志

    return user


##;@DEPRECATED: 使用 create_user 替代
##;@此函数将在 v2.0 版本移除
##; create_user_legacy 创建用户（旧版本）
def create_user_legacy(name: str, email: str) -> User:
    return User(name=name, email=email)


##; calculate_discount 根据用户等级和订单金额计算折扣
##; 折扣规则：
##; - VIP 用户：15% 折扣
##; - 普通用户：10% 折扣
##; - 订单金额 < 100 不享受折扣
def calculate_discount(user_level: str, amount: float) -> float:
    ##;@OPTIMIZE: 这个函数可能会被频繁调用，考虑缓存折扣率

    ##; 小额订单不参与折扣
    if amount < 100:
        return 0.0

    ##; 根据用户等级确定折扣率
    rate = 0.10  ##; 默认普通用户折扣
    if user_level == "VIP":
        rate = 0.15
    elif user_level == "Premium":
        ##;@NOTE: Premium 等级是新增的，需要在文档中说明
        rate = 0.12

    ##;@DEBUG: 临时打印，用于调试折扣计算
    ## print(f"Discount rate for {user_level}: {rate}")

    return amount * rate


##; _process_payment 处理支付（私有函数）
def _process_payment(amount: float) -> bool:
    ##;@FIXME: 需要添加支付网关集成
    ##;@HACK: 临时返回 True，假装支付成功

    ##; 验证金额
    if amount <= 0:
        raise ValueError(f"Invalid amount: {amount}")

    ##;@TODO: 调用支付网关 API
    ##;@TODO: 处理支付失败情况
    ##;@TODO: 记录支付日志

    return True


##; notify_user 发送通知给用户
def notify_user(user_id: int, message: str) -> bool:
    ##;@NOTE: 这个函数暂时只支持邮件通知
    ##;@TODO: 添加短信通知支持
    ##;@TODO: 添加推送通知支持

    ##; 获取用户信息
    ##;@FIXME: 这里应该从数据库获取用户信息
    user = User(id=user_id)

    ##; 验证消息内容
    if not message:
        raise ValueError("Message cannot be empty")

    ##;@HACK: 直接打印到控制台，实际应该发送邮件
    print(f"Sending notification to user {user.id}: {message}")

    ##;@TODO: 实现真正的邮件发送
    return True


##;@XXX: 这个函数存在严重的性能问题
##;@需要紧急优化，否则会影响系统稳定性
##; slow_operation 执行耗时操作（示例）
def slow_operation(items: list[str]) -> list[str]:
    result = []

    ##;@OPTIMIZE: 应该预分配列表容量
    ##; result = []
    ##; result.reserve(len(items))  ## Python 没有 reserve，但可以预分配

    for item in items:
        ##; 这里做一些复杂的处理
        processed = item.upper()
        result.append(processed)

    return result


##; example 演示如何正确使用注释
def example() -> None:
    ##; 这是普通的代码注释
    ##; 用于解释代码的功能和逻辑

    try:
        user = create_user("John", "john@example.com", "password123")
    except ValueError as e:
        ##;@NOTE: 这里的错误处理还不够完善
        print(f"Error: {e}")
        return

    ##;@TODO: 添加用户创建成功的日志
    print(f"User created: {user}")

    ##;@FIXME: 这里应该返回用户 ID 而不是打印
    discount = calculate_discount("VIP", 200.0)
    print(f"Discount: {discount:.2f}")


if __name__ == "__main__":
    ##; 运行示例
    example()
