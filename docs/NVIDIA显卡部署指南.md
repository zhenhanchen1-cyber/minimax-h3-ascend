# NVIDIA 显卡部署指南（4090 / 5090 等）

> ⚠️ **本指南为参考路线，未经本仓库在 N 卡上实测**（本仓库实测环境是昇腾 910B）。
> 信息来源：Comfy-Org 官方模型仓库的权重说明、社区工作流（如 MATLOWAI 的 4 步 SLA 工作流）。
> 欢迎 N 卡用户实践后回来提 PR 补充实测数据。

## 为什么 N 卡路线不一样

昇腾走的是 `int8_convrot`（旋转量化 + `npu_quant_matmul`），而 N 卡有自己的一套：

| 硬件 | 推荐权重格式 |
|---|---|
| 昇腾 910B/910C | `*_int8_convrot` |
| RTX 40 系（4090） | `*_fp8_scaled` / 社区 GGUF |
| RTX 50 系（5090，Blackwell） | `*_nvfp4_awq` / `*_fp8_scaled` |

## 显存账本（RTX 4090 24GB）

| 配置 | 占用 | 可行性 |
|---|---|---|
| 完整版 fp8 (21GB) + 文本编码器 nvfp4 (15.7GB) | 约 37GB | ❌ 装不下，需靠卸载/分步 |
| **精简版 fp8 (21GB) + 文本编码器卸载到内存** | 峰值 21GB + 激活 | ✅ 480P 可跑 |
| 精简版 w6a8 (16GB) | 更宽松 | ✅ 推荐先试 |
| 社区 GGUF Q4/Q5 | 约 10~14GB | ✅ 最省（画质有损） |

**结论**：4090 24GB 建议 **精简版 fp8 或 GGUF + 480P + 5 秒 + 4 步**，与昇腾 32GB 档的策略一致。

## 快速开始（N 卡）

```bash
git clone https://gitcode.com/nxxwjbl/minimax-h3-ascend-uncensored.git
cd minimax-h3-ascend-uncensored
bash scripts/setup_nvidia.sh          # 装 ComfyUI 原生版（不打昇腾补丁）
bash scripts/download_models_nvidia.sh # 下载 N 卡专用权重（fp8 / nvfp4 / 可选 GGUF）
python main.py --listen --lowvram      # 24GB 卡建议带 --lowvram
```

工作流直接用 **Comfy-Org 官方模板**（本仓库 `workflows/` 里的 `i2v_九宫格_昇腾适配.json` 是昇腾改版，
N 卡请用官方原版或社区 4 步 SLA 工作流）。

## N 卡专属加速技巧（昇腾暂时用不上）

| 手段 | 效果 |
|---|---|
| **4 步 Turbo LoRA** | 采样步数 8→4，速度翻倍（本仓库已收录该 LoRA） |
| **SageAttention** | 注意力加速，社区反馈显著 |
| **SLA 稀疏注意力**（`H3SLAAttention` 节点，稀疏度 0.9） | 跳过 90% 注意力计算，2~3 倍加速（CUDA 专属算子） |
| `torch.compile` | 视环境而定，首次编译有开销 |
| NVFP4（仅 Blackwell / 50 系） | 权重体积减半、速度提升 |

> 参考：社区实测 4 步 + SLA 稀疏注意力在高端 N 卡上，10 秒视频可做到约 20 秒级生成。

## 权重下载对照表（N 卡）

| 文件 | 大小 | 适用 |
|---|---|---|
| `diffusion_models/minimax_h3_fl2va_pruned_fp8_scaled.safetensors` | 21.0G | 4090 首选 |
| `diffusion_models/minimax_h3_fl2va_pruned_w6a8.safetensors` | 16.0G | 更省显存 |
| `text_encoders/qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | 15.7G | **仅 Blackwell（50 系）** |
| `text_encoders/qwen3vl_32b_minimax_h3_int8_convrot.safetensors` | 27.1G | 通用 INT8 |
| 社区 GGUF（Q4/Q5/Q8） | 10~20G | 24GB 卡兜底，画质有损 |

> 官方仓库：https://huggingface.co/Comfy-Org/MiniMax-H3

## 硬件选型建议（性价比）

| 方案 | 成本 | 体验 | 适合 |
|---|---|---|---|
| **昇腾 910B（CANNLab 等活动）** | 免费 | 2 卡 128GB 显存，768P 无压力 | 首选 |
| 4090 云租用 | 约 2~4 元/小时 | 24GB 吃紧，480P 起步 | 没昇腾资源时 |
| 5090 云租用 | 约 5~8 元/小时 | 32GB 更宽松，NVFP4 加持 | 追求速度 |
| 910C | 高 | 单卡 128GB，最强 | 预算充足 |

**一句话**：有免费昇腾就别租卡；非要租，看显存下菜——**24GB 只能 480P，32GB 能摸 768P**。
