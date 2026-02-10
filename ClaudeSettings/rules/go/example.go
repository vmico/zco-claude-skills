package example

import (
	"errors"
	"fmt"
	"strings"
)

//; 示例代码：演示注释规范的使用

//;@NOTE: 这个文件展示了如何正确使用 //; 和 //;@注释

// ; User 表示系统用户
// ; 包含用户的基本信息和认证数据
type User struct {
	ID       int64
	Name     string
	Email    string
	Password string //;@FIXME: 应该存储哈希值而不是明文密码
}

// ; ValidateEmail 验证邮箱格式是否正确
// ; 返回 true 表示邮箱格式有效
func ValidateEmail(email string) bool {
	//; 检查邮箱是否包含 @ 符号
	if !strings.Contains(email, "@") {
		return false
	}

	//;@TODO: 添加更完整的邮箱格式验证
	//;@OPTIMIZE: 可以使用正则表达式提高验证准确性

	//; 检查 @ 符号前后是否有内容
	parts := strings.Split(email, "@")
	if len(parts) != 2 || parts[0] == "" || parts[1] == "" {
		return false
	}

	return true
}

// ; CreateUser 创建新用户
// ; 验证用户数据并返回创建的用户对象
func CreateUser(name, email, password string) (*User, error) {
	//;@NOTE: 这个函数需要重构，太长了

	//; 验证用户名
	if name == "" {
		return nil, errors.New("name cannot be empty")
	}

	//; 验证邮箱
	if !ValidateEmail(email) {
		return nil, errors.New("invalid email format")
	}

	//;@FIXME: 密码验证规则太简单，需要加强
	//; 验证密码长度
	if len(password) < 6 {
		return nil, errors.New("password too short")
	}

	//;@HACK: 临时方案 - 直接存储明文密码
	//;@等待安全团队提供密码哈希方案后修改
	user := &User{
		Name:     name,
		Email:    email,
		Password: password, //; 应该存储哈希值
	}

	//;@TODO: 添加到数据库
	//;@TODO: 发送欢迎邮件
	//;@TODO: 记录审计日志

	return user, nil
}

// ;@DEPRECATED: 使用 CreateUser 替代
// ;@此函数将在 v2.0 版本移除
// ; CreateUserLegacy 创建用户（旧版本）
func CreateUserLegacy(name, email string) *User {
	return &User{
		Name:  name,
		Email: email,
	}
}

// ; CalculateDiscount 根据用户等级和订单金额计算折扣
// ; 折扣规则：
// ; - VIP 用户：15% 折扣
// ; - 普通用户：10% 折扣
// ; - 订单金额 < 100 不享受折扣
func CalculateDiscount(userLevel string, amount float64) float64 {
	//;@OPTIMIZE: 这个函数可能会被频繁调用，考虑缓存折扣率

	//; 小额订单不参与折扣
	if amount < 100 {
		return 0
	}

	//; 根据用户等级确定折扣率
	var rate float64
	switch userLevel {
	case "VIP":
		rate = 0.15
	case "Premium":
		//;@NOTE: Premium 等级是新增的，需要在文档中说明
		rate = 0.12
	default:
		rate = 0.10
	}

	//;@DEBUG: 临时打印，用于调试折扣计算
	// fmt.Printf("Discount rate for %s: %.2f\n", userLevel, rate)

	return amount * rate
}

// ; processPayment 处理支付（私有函数）
func processPayment(amount float64) error {
	//;@FIXME: 需要添加支付网关集成
	//;@HACK: 临时返回 nil，假装支付成功

	//; 验证金额
	if amount <= 0 {
		return fmt.Errorf("invalid amount: %.2f", amount)
	}

	//;@TODO: 调用支付网关 API
	//;@TODO: 处理支付失败情况
	//;@TODO: 记录支付日志

	return nil
}

// ; NotifyUser 发送通知给用户
func NotifyUser(userID int64, message string) error {
	//;@NOTE: 这个函数暂时只支持邮件通知
	//;@TODO: 添加短信通知支持
	//;@TODO: 添加推送通知支持

	//; 获取用户信息
	//;@FIXME: 这里应该从数据库获取用户信息
	user := &User{ID: userID}

	//; 验证消息内容
	if message == "" {
		return errors.New("message cannot be empty")
	}

	//;@HACK: 直接打印到控制台，实际应该发送邮件
	fmt.Printf("Sending notification to user %d: %s\n", user.ID, message)

	//;@TODO: 实现真正的邮件发送
	return nil
}

// ;@XXX: 这个函数存在严重的性能问题
// ;@需要紧急优化，否则会影响系统稳定性
// ; SlowOperation 执行耗时操作（示例）
func SlowOperation(items []string) []string {
	var result []string

	//;@OPTIMIZE: 应该预分配 slice 容量
	//; result := make([]string, 0, len(items))

	for _, item := range items {
		//; 这里做一些复杂的处理
		processed := strings.ToUpper(item)
		result = append(result, processed)
	}

	return result
}

// ; Example 演示如何正确使用注释
func Example() {
	//; 这是普通的代码注释
	//; 用于解释代码的功能和逻辑

	user, err := CreateUser("John", "john@example.com", "password123")
	if err != nil {
		//;@NOTE: 这里的错误处理还不够完善
		fmt.Printf("Error: %v\n", err)
		return
	}

	//;@TODO: 添加用户创建成功的日志
	fmt.Printf("User created: %+v\n", user)

	//;@FIXME: 这里应该返回用户 ID 而不是打印
	discount := CalculateDiscount("VIP", 200)
	fmt.Printf("Discount: %.2f\n", discount)
}

/**
多行注释示例：

这是文档注释，用于描述包、类型、函数等的详细信息。
通常用于生成 API 文档。

对于元信息注释（TODO、FIXME 等），即使在多行注释中，
也应该使用 //;@前缀：

//;@TODO: 完成这个功能的实现
//;@NOTE: 这里需要特别注意线程安全问题
**/
