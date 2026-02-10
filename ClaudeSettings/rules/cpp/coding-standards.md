# C++ 项目编程标准

## 注释规范

### 注释类型区分（核心约定）

本项目使用不同的注释标记来区分注释的用途：

#### 1. 标准代码注释 `//`
**用途**：API 文档、函数说明、公共接口注释

**使用场景**：
- 类、函数、方法的文档注释
- 公共 API 的使用说明
- 复杂算法的整体说明
- 文件头部的版权和描述信息

#### 2. 代码逻辑解释 `//;`
**用途**：解释代码的功能、逻辑、算法，与纯代码注释 `//` 区分

**使用场景**：
- 解释复杂的业务逻辑
- 说明算法实现思路
- 阐述为什么这样写（设计决策）
- 解释不明显的代码行为


**示例**：
```cpp
// Calculate the discount based on order amount and user level
//
// Discount rules:
// - VIP users: 15% of order amount
// - Regular users: 10% of order amount
// - Orders < $100 don't qualify for discounts
//
// @param amount Order amount in dollars
// @param userLevel User membership level ("VIP" or "Regular")
// @return Discount amount in dollars
double calculateDiscount(double amount, const std::string& userLevel) {
    //; Small orders don't qualify for discount program
    if (amount < 100.0) {
        return 0.0;
    }

    //; Calculate discount rate based on user level
    double rate = 0.0;
    if (userLevel == "VIP") {
        rate = 0.15;
    } else {
        rate = 0.10;
    }

    return amount * rate;
}
```
