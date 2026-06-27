
claude总结

---

## 0. 环境

```bash
# CPU 版(够入门用)
pip install torch torchvision

# 验证
python -c "import torch; print(torch.__version__)"
```

```python
import torch

# 设备:有 GPU 就用 GPU,代码后面统一用 device 这个变量
device = "cuda" if torch.cuda.is_available() else "cpu"
# Apple Silicon 可以用 "mps":
# device = "mps" if torch.backends.mps.is_available() else "cpu"
print(device)
```

---

## 1. 张量(Tensor)—— 只看 PyTorch 特有的部分

张量 = 带 GPU 支持和自动求导的 ndarray。和 numpy 几乎一一对应,这里只挑你以后会反复踩的点。

```python
import torch

# 创建
x = torch.tensor([[1., 2.], [3., 4.]])   # 从数据
z = torch.zeros(2, 3)                      # 全 0
r = torch.randn(2, 3)                      # 标准正态
a = torch.arange(0, 10, 2)                 # [0,2,4,6,8]

# 三个最常查的属性
print(x.shape)    # torch.Size([2, 2])
print(x.dtype)    # torch.float32  ← 默认浮点是 float32,不是 float64
print(x.device)   # cpu
```

### 1.1 形状操作(深度学习里 80% 的 bug 来自形状)

```python
x = torch.randn(4, 3)

x.reshape(2, 6)      # 改形状,元素总数不变
x.reshape(2, -1)     # -1 = 自动推断这一维 → (2, 6)
x.view(2, 6)         # 类似 reshape,但要求内存连续
x.T                  # 转置(2D)
x.unsqueeze(0)       # (4,3) → (1,4,3),增加一个维度
x.squeeze()          # 去掉所有大小为 1 的维度
```

> **广播(broadcasting)** 规则和 numpy 一致:`(4,3) + (3,)` 可以,`(4,3) + (4,1)` 可以。形状对不上时报的错,90% 是这里没对齐。

### 1.2 设备转移

```python
x = torch.randn(3, 3)
x = x.to(device)          # 搬到 GPU/CPU
# 注意:参与运算的张量必须在同一个 device 上,否则报错
```

### 1.3 和 numpy 互转

```python
import numpy as np
t = torch.from_numpy(np.array([1, 2, 3]))   # numpy → tensor(共享内存)
n = t.numpy()                                # tensor → numpy(需在 CPU 上)
```

---

## 2. Autograd —— PyTorch 的核心魔法

这是 PyTorch 和 numpy 的根本区别。你不用手写梯度,PyTorch 帮你算。

### 2.1 最小例子

```python
import torch

# requires_grad=True:告诉 PyTorch "追踪对这个张量的所有运算"
x = torch.tensor(2.0, requires_grad=True)

y = x ** 2 + 3 * x + 1     # y = x² + 3x + 1

y.backward()               # 反向传播:计算 dy/dx
print(x.grad)              # dy/dx = 2x + 3 = 7.0
```

发生了什么:前向算 `y` 时,PyTorch 在背后建了一张**计算图**;`backward()` 沿着图反向用链式法则把梯度算到每个 `requires_grad=True` 的叶子节点的 `.grad` 上。

### 2.2 几条必须记住的规则

```python
# (1) 梯度会累加!每次反向前要清零,否则越加越多
x.grad.zero_()

# (2) 只有标量能直接 backward。向量要先 reduce 成标量(通常是 .sum() 或 .mean())
y = (x ** 2).sum()
y.backward()

# (3) 不需要梯度时(比如推理、更新参数),用 no_grad 关掉追踪 → 更快更省内存
with torch.no_grad():
    prediction = model(x)

# (4) 把张量从图里摘出来(只要值不要梯度)
x_value = x.detach()
```

> **直觉**:`requires_grad` 是开关,`backward()` 是触发,`.grad` 是结果,`zero_()` 是重置。训练循环就是反复拨这四个动作。

---

## 3. 从零实现线性回归(把上面拼起来)

不用任何高层 API,纯手动,看清楚训练循环的骨架。

```python
import torch

# ---- 造数据:真实关系 y = 2x - 3 + 噪声 ----
torch.manual_seed(0)
X = torch.randn(100, 1)
y = 2 * X - 3 + 0.1 * torch.randn(100, 1)

# ---- 参数:要学的东西,开 requires_grad ----
w = torch.randn(1, 1, requires_grad=True)
b = torch.zeros(1, requires_grad=True)

lr = 0.1

for epoch in range(100):
    # 1. 前向:预测
    y_hat = X @ w + b

    # 2. 算 loss(均方误差)
    loss = ((y_hat - y) ** 2).mean()

    # 3. 反向:算梯度
    loss.backward()

    # 4. 更新参数(手动梯度下降)。更新时不要追踪梯度
    with torch.no_grad():
        w -= lr * w.grad
        b -= lr * b.grad

        # 5. 梯度清零!不清就会累加
        w.grad.zero_()
        b.grad.zero_()

    if epoch % 20 == 0:
        print(f"epoch {epoch:3d}  loss {loss.item():.4f}")

print(f"学到的 w={w.item():.3f}(真实 2),b={b.item():.3f}(真实 -3)")
```

**这五步就是所有深度学习训练的循环骨架**,后面只是把它们换成高层 API。

---

## 4. 用高层 API 改写(实际工作中的写法)

PyTorch 提供 `nn`(网络层 + loss)和 `optim`(优化器),把第 4、5 步自动化。

```python
import torch
import torch.nn as nn

# 同样的数据
torch.manual_seed(0)
X = torch.randn(100, 1)
y = 2 * X - 3 + 0.1 * torch.randn(100, 1)

# 模型:一个线性层 = w·x + b,参数 PyTorch 自动管理
model = nn.Linear(in_features=1, out_features=1)

loss_fn = nn.MSELoss()                                  # 均方误差
optimizer = torch.optim.SGD(model.parameters(), lr=0.1) # 随机梯度下降

for epoch in range(100):
    y_hat = model(X)              # 前向
    loss = loss_fn(y_hat, y)      # loss

    optimizer.zero_grad()         # 清零(替代手动 .grad.zero_())
    loss.backward()               # 反向
    optimizer.step()              # 更新(替代手动 w -= lr * w.grad)

    if epoch % 20 == 0:
        print(f"epoch {epoch:3d}  loss {loss.item():.4f}")

# 取出学到的参数
w, b = model.weight.item(), model.bias.item()
print(f"w={w:.3f}, b={b:.3f}")
```

> **对照第 3 节**:`optimizer.zero_grad()` / `loss.backward()` / `optimizer.step()` 这三行,就是手动版第 3、4、5 步的封装。**记住这三行的顺序**,所有训练循环都长这样。

---

## 5. 搭一个 MLP(多层感知机)

线性层叠 ReLU 就是 MLP。两种写法。

### 5.1 快速写法:Sequential

```python
import torch.nn as nn

model = nn.Sequential(
    nn.Linear(784, 256),   # 输入 784 维(比如 28×28 图片展平)
    nn.ReLU(),             # 非线性激活 —— 没有它,叠多少层都还是线性
    nn.Linear(256, 64),
    nn.ReLU(),
    nn.Linear(64, 10),     # 输出 10 类
)
```

### 5.2 标准写法:继承 nn.Module(灵活,以后都用这个)

```python
import torch.nn as nn
import torch.nn.functional as F

class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        # 在这里定义需要的层
        self.fc1 = nn.Linear(784, 256)
        self.fc2 = nn.Linear(256, 64)
        self.fc3 = nn.Linear(64, 10)

    def forward(self, x):
        # 在这里定义数据怎么流过这些层
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        x = self.fc3(x)          # 最后一层不加激活(交给 loss 处理)
        return x

model = MLP()
print(model)
```

> 你只写 `forward`(前向),`backward` PyTorch 用 autograd 自动生成。这就是为什么你只需要描述网络结构。

---

## 6. 数据加载:Dataset 和 DataLoader

真实训练是分**批(batch)**喂数据的。`DataLoader` 负责切批、打乱、并行加载。

```python
from torch.utils.data import TensorDataset, DataLoader

# 把特征和标签打包
dataset = TensorDataset(X, y)

# 切成 batch,每个 epoch 打乱
loader = DataLoader(dataset, batch_size=16, shuffle=True)

# 训练时这样遍历
for batch_X, batch_y in loader:
    # 每次拿到 16 个样本
    pass
```

---

## 7. 完整训练模板(背下来)

这是一个能直接套用的完整流程,以分类任务为例。**记住结构,以后改的只是模型和数据。**

```python
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader

device = "cuda" if torch.cuda.is_available() else "cpu"

# ---- 1. 数据(这里用假数据演示)----
X = torch.randn(1000, 20)
y = torch.randint(0, 3, (1000,))          # 3 分类,标签是 0/1/2
loader = DataLoader(TensorDataset(X, y), batch_size=32, shuffle=True)

# ---- 2. 模型 ----
model = nn.Sequential(
    nn.Linear(20, 64), nn.ReLU(),
    nn.Linear(64, 3),                     # 输出 3 个类别的 logits
).to(device)

# ---- 3. loss 和优化器 ----
loss_fn = nn.CrossEntropyLoss()           # 分类用交叉熵(内部已含 softmax)
optimizer = torch.optim.Adam(model.parameters(), lr=1e-3)

# ---- 4. 训练循环 ----
for epoch in range(10):
    model.train()                         # 切到训练模式
    total_loss = 0
    for batch_X, batch_y in loader:
        batch_X, batch_y = batch_X.to(device), batch_y.to(device)

        # —— 核心三步,永远是这个顺序 ——
        optimizer.zero_grad()
        pred = model(batch_X)
        loss = loss_fn(pred, batch_y)
        loss.backward()
        optimizer.step()

        total_loss += loss.item()

    print(f"epoch {epoch}  avg_loss {total_loss / len(loader):.4f}")

# ---- 5. 评估 ----
model.eval()                              # 切到评估模式
with torch.no_grad():                     # 评估不需要梯度
    pred = model(X.to(device))
    acc = (pred.argmax(dim=1) == y.to(device)).float().mean()
    print(f"训练集准确率 {acc.item():.3f}")
```

### 几个容易忽略但很重要的点

- **`model.train()` vs `model.eval()`**:影响 Dropout、BatchNorm 的行为。训练前调 `train()`,评估前调 `eval()`,养成习惯。
- **`CrossEntropyLoss` 内部已经做了 softmax**,所以模型最后一层**不要**自己加 softmax,直接输出 logits。
- **`with torch.no_grad()`**:评估/推理时一定加,省内存又加速。
- 数据和模型必须在**同一个 device** 上。

---

## 8. 保存和加载模型

```python
# 保存(只存参数,推荐)
torch.save(model.state_dict(), "model.pth")

# 加载(要先有同样结构的模型)
model.load_state_dict(torch.load("model.pth"))
model.eval()
```

---

## 9. 常见报错速查

|报错关键词|原因|解法|
|---|---|---|
|`Expected all tensors to be on the same device`|数据和模型不在同一设备|都 `.to(device)`|
|`shape mismatch` / `mat1 and mat2`|矩阵形状对不上|`print(x.shape)` 逐层查|
|`element 0 of tensors does not require grad`|对没开 `requires_grad` 的张量调 `backward`|检查参数 / 是否在 `no_grad` 里|
|loss 是 `nan`|学习率太大 / 数据没归一化|调小 lr,标准化输入|
|梯度爆炸/不下降|没 `zero_grad` 或 lr 不对|确认三步顺序,调 lr|

---

## 10. 下一步

你的计划里下一站是**手写反向传播**——建议:

1. 先用本笔记第 3 节的「从零线性回归」确认你能脱离 autograd 跑通循环;
2. 再去 Nielsen 第 2 章,把 MLP 的反向传播**手推 + 手写 numpy 实现**(不用 PyTorch);
3. 回来用 PyTorch 的 autograd 验证你手算的梯度对不对(`loss.backward()` 后对比 `.grad`)。

这样你既懂了 PyTorch 怎么用,也懂了它背后到底在算什么——面试时这层理解会很值钱。

---

**速记卡:训练循环永远是这五行**

```python
optimizer.zero_grad()   # 清梯度
pred = model(x)         # 前向
loss = loss_fn(pred, y) # 算损失
loss.backward()         # 反向
optimizer.step()        # 更新
```