# GAN详细复习笔记

> 对照语雀《2 深度学习》§1.6「常见的深度学习家族」中的 GAN（生成对抗网络）。  
> 姊妹篇：神经网络与 MLP、CNN、反向传播与优化器、PyTorch 训练实战。  
> 公式：`$...$` / `$$...$$`。

---

## 〇、一句话抓住全篇

> **GAN：生成器造假数据，判别器分辨真假；两者对抗训练，生成器越来越能「以假乱真」。**

语雀口径举例：换脸等生成任务背后常见这一思想。

| 章 | 内容 |
| --- | --- |
| 一 | 两个玩家 |
| 二 | 目标与训练节奏 |
| 三 | 和自编码器等的对比 |
| 四 | 最小代码骨架 |
| 五 | 易错点与自测 |

---

## 一、生成器 vs 判别器

| 网络 | 输入 | 输出 | 目标 |
| --- | --- | --- | --- |
| 生成器 $G$ | 随机噪声 $z$ | 假样本 $G(z)$ | 骗过判别器 |
| 判别器 $D$ | 真样本或假样本 | 「有多真」的分数/概率 | 认出假货 |

人话：伪币工厂 vs 验钞机；验钞机变强，工厂也被迫变强。

图像 GAN 里 $G$、$D$ 常用 CNN 结构（DCGAN 等）。

---

## 二、训练在优化什么（直觉）

经典设定近似一个对抗博弈：

- $D$ 尽量：真样本打高分、假样本打低分  
- $G$ 尽量：让 $D(G(z))$ 变高（看起来像真的）  

交替步骤（实践常见）：

1. 固定 $G$，多更新几步 $D$  
2. 固定 $D$，更新 $G$  
3. 重复  

损失形式有 BCE、Wasserstein（WGAN）等变体；入门先建立「对抗」心智，不必死背全部公式。

---

## 三、能做什么 / 局限

| 能做 | 注意 |
| --- | --- |
| 图像生成、风格迁移、换脸思路、数据增强 | 训练不稳、模式崩塌（只生成少数几种样子） |
| 学数据分布 | 评估难（不像分类有准确率那么直观） |

现代大规模生成还常见扩散模型等；GAN 仍是「对抗生成」的入门必知。

---

## 四、综合代码（极简 1D，逐行注释）

用「学习一维高斯」演示对抗，不依赖真实图片，方便跑通思路。

```python
import torch  # PyTorch
import torch.nn as nn  # 模块

torch.manual_seed(42)  # 种子
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")  # 设备

# 真数据：N(4, 1.5^2)
def real_data(n):  # 采样真数据
    return torch.randn(n, 1, device=device) * 1.5 + 4.0  # (n,1)

G = nn.Sequential(  # 生成器：噪声 -> 假样本
    nn.Linear(1, 32), nn.ReLU(),  # 隐层
    nn.Linear(32, 1),  # 输出 1 维
).to(device)
D = nn.Sequential(  # 判别器：样本 -> logit（真假）
    nn.Linear(1, 32), nn.ReLU(),  # 隐层
    nn.Linear(32, 1),  # 1 个 logit
).to(device)

opt_G = torch.optim.Adam(G.parameters(), lr=1e-3)  # G 优化器
opt_D = torch.optim.Adam(D.parameters(), lr=1e-3)  # D 优化器
bce = nn.BCEWithLogitsLoss()  # 二分类损失

for step in range(1, 2001):  # 训练步
    # ----- 训 D -----
    z = torch.randn(64, 1, device=device)  # 噪声
    fake = G(z).detach()  # 假样本；detach 避免这步更新 G
    real = real_data(64)  # 真样本
    loss_D = bce(D(real), torch.ones(64, 1, device=device)) + bce(  # 真打 1
        D(fake), torch.zeros(64, 1, device=device)  # 假打 0
    )
    opt_D.zero_grad()  # 清梯度
    loss_D.backward()  # 反传
    opt_D.step()  # 更新 D

    # ----- 训 G -----
    z = torch.randn(64, 1, device=device)  # 新噪声
    fake = G(z)  # 假样本（需梯度）
    loss_G = bce(D(fake), torch.ones(64, 1, device=device))  # 希望 D 判成真
    opt_G.zero_grad()  # 清梯度
    loss_G.backward()  # 反传
    opt_G.step()  # 更新 G

    if step % 400 == 0:  # 日志
        with torch.no_grad():  # 抽样看均值
            samples = G(torch.randn(200, 1, device=device)).cpu().squeeze()  # 假样本
        print(f"step {step} | D {float(loss_D):.3f} G {float(loss_G):.3f} | fake mean {samples.mean():.2f}")  # 均值应靠近 4
```

---

## 五、易错点与自测

1. 更新 $D$ 时忘了对假样本 `detach`，梯度乱窜。  
2. $G$、$D$ 学习率/更新次数严重失衡导致一方碾压。  
3. 把 GAN 当成「有标签分类」来评估准确率。  
4. 一上来就上大图高分辨率，不先在小问题验证对抗闭环。  

自测：两个网络各自图什么？训练为何要交替？模式崩塌大概指什么？  
答案：造假 / 验真；对抗博弈需要轮流变强；生成多样性塌缩成少数模式。

---

## 六、一句话收束

> GAN 用「造假者 vs 鉴宝人」学数据分布；先搞清交替训练与损失方向，再谈 DCGAN、条件 GAN 与换脸应用。
