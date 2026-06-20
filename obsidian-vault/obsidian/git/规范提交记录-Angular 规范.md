
#  Git Commit 规范书写笔记

## 1. 核心格式

```
git commit -m "<type>(<scope>): <subject>"
```

- **type（必填）**：本次提交的类型（如：是新功能、修 Bug 还是改文档）。
    
- **scope（可选）**：本次提交波及的范围（如：哪个模块、哪个组件或具体文件名）。
    
- **subject（必填）**：对变更的简短描述（一般不超过 50 个字符）。
    

## 2. 常用 Type（类型）分类详解

|**类型 (Type)**|**含义**|**适用场景**|
|---|---|---|
|**feat**|新功能 (feature)|引入了新需求、新功能、新接口|
|**fix**|修复 Bug|修复了现有的代码缺陷|
|**docs**|文档变更 (documentation)|修改了 README、API 文档、注释等|
|**style**|代码格式调整|不影响代码逻辑的变更（如去掉空格、格式化、补全分号等）|
|**refactor**|重构|既不是新功能也不是修 Bug 的代码变动（如优化结构、重命名变量）|
|**perf**|性能优化 (performance)|提升代码运行效率、降低内存占用等|
|**test**|测试用例|增加、修改或删除测试代码|
|**chore**|构建/工具链变动|修改配置文件、更新依赖、修改 CI/CD 流程等|
|**revert**|撤销/回滚|撤销之前的某次 Commit|

## 3. 书写细节与原则

1. **冒号后要有空格**：`<type>:` 后面必须紧跟一个**英文空格**，然后再写描述。
    
2. **用祈使句/现在时**：描述（subject）尽量用现在时态。例如用 `change` 而不是 `changed` 或 `changes`。
    
3. **简明扼要**：Subject 结尾**不要写句号**，保持在一句话内说清楚核心变动。
    
4. **语言一致性**：根据团队习惯统一使用中文或英文。
    

## 4. 常见书写示例

### 🚀 feat (新功能)

Bash

```
git commit -m "feat(auth): 增加微信第三方登录功能"
git commit -m "feat(user): add user profile upload API"
```

### 🐛 fix (修 Bug)

Bash

```
git commit -m "fix(cart): 修复商品数量减少时总价未刷新的问题"
git commit -m "fix: resolve memory leak in connection pool"
```

### 📝 docs (改文档)

Bash

```
git commit -m "docs(readme): 修改安装指南和部署步骤"
```

### 🎨 style (改格式)

Bash

```
git commit -m "style: 规范所有控制器的缩进并移除未使用的变量"
```

### ⚙️ chore (杂务/配置)

Bash

```
git commit -m "chore: 升级 lodash 依赖版本至 4.17.21"
```

## 💡 进阶：多行 Commit 的写法

如果变动比较复杂，`-m` 参数其实可以通过**多次输入 `-m`** 来实现包含 Body 和 Footer 的复杂提交：

Bash

```
git commit -m "feat(order): 引入支付超时自动取消订单功能" \
           -m "1. 增加定时任务检查未支付订单" \
           -m "2. 超过30分钟未支付则自动关闭订单并释放库存" \
           -m "Closes #123"
```

_(注：最后的 `Closes #123` 用于在 GitHub/GitLab 等平台上自动关闭对应的 Issue)_