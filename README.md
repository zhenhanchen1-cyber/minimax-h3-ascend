<div align="center">

# 🎬 MiniMax-H3 · 昇腾 NPU 本地部署（910B / 910C 真机实测）

**在华为昇腾 NPU 上用 ComfyUI 本地跑 MiniMax-H3 全模态视频生成**
文生视频 · 图生视频 · 参考图锁角色 · **原生音画同步** · 全程离线 · 免费无限量

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Platform: Ascend NPU](https://img.shields.io/badge/Platform-Ascend_NPU-c8102e)]()
[![Tested: 910B 2×64G](https://img.shields.io/badge/Tested-910B_2%C3%9764G-green)]()
[![Workflows: 10](https://img.shields.io/badge/Workflows-10-orange)]()
[![Download: 40MB/s](https://img.shields.io/badge/Download-40MB%2Fs-blue)]()

**中文** ｜ [English](#english)

</div>

> **🔥 一句话卖点**：官方和社区资料几乎**全是 N 卡路线**，这里是**唯一在昇腾 910B 双卡上真机跑通并给出完整实测数据**的部署方案 ——
> 一条命令装完 · 40MB/s 分片下载 · 17 条踩坑记录 · 3 档工作流 · 32GB 单卡低配档。
>
> **姊妹项目**：NVIDIA 显卡路线（8GB 显存起）→ [minimax-h3-nvidia-uncensored](https://gitcode.com/nxxwjbl/minimax-h3-nvidia-uncensored)
>
> **🟢 活跃维护中** · 最近更新：2026-10-12（新增社区增强件 + 昇腾兼容性判断）·
> 完整历史见 [CHANGELOG.md](CHANGELOG.md) —— 内容可以被复制，**持续的实测与更新不能**。

---

## 📑 目录

- [实测出片（60 秒连续剧情）](#-实测出片60-秒连续剧情本仓库流水线生成)
- [实测性能数据](#实测性能2x910b64gb2-hbm)
- [快速开始（换机复原只需三步）](#快速开始换机复原只需三步)
- [硬件怎么选（性价比）](#-硬件怎么选性价比)
- [模型清单（含硬件要求 / 测试状态）](#-模型清单含硬件要求--测试状态)
- [不同规格昇腾机器怎么配](#️-不同规格昇腾机器怎么配)
- [32GB 单卡低配档](#-32gb-单卡低配档完整可行方案)
- [三档工作流](#-三档工作流新手按场景直接选)
- [社区增强件（昇腾兼容性待验证）](#-社区增强件昇腾兼容性待验证欢迎实测)
- [关键注意事项](#-关键注意事项)
- [常见问题](#-常见问题)
- [⭐ 如果对你有帮助](#-如果对你有帮助)

## 🔥 三大看点

1. **昇腾真机实测（全社区稀缺）** —— 官方与社区资料几乎全是 NVIDIA 路线（CUDA/NVFP4/GGUF），
   本仓库提供**已在 910B 双卡跑通**的 INT8 完整方案 + 实测性能表 + 17 条踩坑修复，另有 1×64G / 1×32G / 4×64G 适配档
2. **开箱即用 + 一键复原** —— 换一台昇腾机器，clone（<5MB）→ 三条命令 → 浏览器开干；
   自研分片下载器实测聚合 **40MB/s**，90GB 约 35~40 分钟（官方单连接只有 ~2MB/s）
3. **完全本地运行** —— 视频生成与文本编码全程在本机，**没有云端审核掐提示词这一层**，免费无限量

## 🎬 实测出片（60 秒连续剧情，本仓库流水线生成）

| ![](assets/demo_1.jpg) | ![](assets/demo_2.jpg) | ![](assets/demo_3.jpg) |
|---|---|---|
| 镜头 1-2 · 建置 | 镜头 4-6 · 情绪推进 | 镜头 8-9 · 收尾空镜 |

> 1184×896 / 24fps / 原生 32kHz 立体声 / 由九宫格分镜图 + 2500 字分镜提示词生成，5 段 × 12 秒「尾帧接首帧」拼接为 61 秒成片。

## 实测性能（2×910B，64GB×2 HBM）

| 分辨率 | 帧数/时长 | 步数 | 采样耗时 | 端到端 | 场景 |
|---|---|---|---|---|---|
| 0.4MP (864×480) | 124 / 5s | **4** | **17.8s** | 71s（冷启）→ **20~25s（热机）** | 极速档，批量出片 |
| 0.4MP (864×480) | 124 / 5s | 8 | 36.4s | 89.7s | 8 步档 |
| 0.6MP (1024×576) | 192 / 8s | 4 | 约 40s | 约 60~90s | 中间档，画质/速度平衡 |
| 1.0MP (1152×864) | 294 / 12s | 8 | 71s/步 ≈ 570s | 约 11 分钟 | 高画质长片分段 |

> 提速杠杆：**分辨率 >> 帧数 > 步数**。0.4MP→1.0MP 每步耗时 4.4s→71s（16 倍）；步数 8→4 快 2 倍。

## 快速开始（换机复原只需三步）

```bash
git clone https://gitcode.com/nxxwjbl/minimax-h3-ascend-uncensored.git   # GitHub 镜像见文末
cd minimax-h3-ascend
bash setup.sh                      # ① 装好一切（拉ComfyUI+打昇腾补丁+依赖+工作流）
bash scripts/download_models.sh    # ② 下模型（约90GB，hf-mirror 分片并行，支持断点续传）
bash scripts/start_comfyui.sh      # ③ 启动，浏览器打开 http://127.0.0.1:8188
```

**下载速度参考**（实测）：聚合约 **40MB/s**（32 连接/文件），全量 90GB 约 **35~40 分钟**；
若环境带宽较差（10MB/s），约 2.5 小时，支持**断点续传**，断了重跑即可。

还想更快？把并发拉满（带宽够的前提下可到 60~80MB/s）：

```bash
MAX_CONN=48 FILES_PARALLEL=3 bash scripts/download_models.sh
```

**前提**：昇腾环境已装 CANN ≥ 9.0.0 与 torch/torch_npu（如 CANNLab 镜像自带）。
脚本会**自动识别 910B/910C 的卡数**（1/2/4/8）并同步到工作流配置。

> **用 N 卡（RTX 4090 / 5090）？** 请看**专门的 N 卡仓库**
> [minimax-h3-nvidia-uncensored](https://gitcode.com/nxxwjbl/minimax-h3-nvidia-uncensored)
> （8GB 显存起 · 一键脚本 · 9 套工作流 · 15+ 模型选型）。
> 本仓库也留了一份早期参考：[docs/NVIDIA显卡部署指南.md](docs/NVIDIA显卡部署指南.md)。

## 💰 硬件怎么选（性价比）

| 方案 | 成本 | 显存 | 体验 | 适合 |
|---|---|---|---|---|
| **昇腾 910B（CANNLab 等活动）** | **免费** | 2×64GB | 768P 无压力，480P 热机 20~25 秒/条 | **首选** |
| 昇腾 910B 32GB（低配档） | 免费 | 32GB | 480P/5s，约 2~5 分钟/条 | 约不到大显存时 |
| RTX 4090 云租用 | 2~4 元/小时 | 24GB | 480P 起步，需 fp8 / INT8 量化（GGUF 只可用于主模型） | 没昇腾资源时 |
| RTX 4090-48G（显存魔改，实测） | 约 2.2 元/小时 | 48GB | 0.4MP/5s **54 秒**、0.98MP/6 步 **243 秒**（无 SLA，保守值） | 想拿 N 卡数据对照 |
| RTX 5090 云租用 | 5~8 元/小时 | 32GB | 可摸 768P，NVFP4 加持 | 追求速度 |
| 昇腾 910C | 高 | 128GB/卡 | 最强，单卡跑完整模型 | 预算充足 |

一句话：**有免费昇腾就别租卡**；非要租，按显存下菜——24GB 只能 480P，32GB 能摸 768P。

## 📦 模型清单（含审查状态 / 硬件要求 / 测试状态）

> 全部公开可用；✅=本仓库实测通过，❓=未测试（理论可用，欢迎反馈），❌=昇腾不可用。
> 链接均为 HuggingFace 官方仓库地址（国内可在域名换成 `hf-mirror.com`）。

### 主模型 DiT（扩散"大脑"）

| 文件 | 大小 | 审查 | 昇腾要求 | 状态 | 说明 |
|---|---|---|---|---|---|
| `minimax_h3_fl2va_int8_convrot` | 34.0G | 中立 | ≥2×64G 推荐 | ✅ | **主力模型**：文生/图生/首尾帧 |
| `minimax_h3_ref2va_pruned_int8_convrot` | 21.0G | 中立 | 单卡 64G 可 | ⚠️ | Ref2VA 参考图锁角色，已就位未充分测 |
| `minimax_h3_fl2va_pruned_int8_convrot` | 20.9G | 中立 | 单卡 64G 可 | ❓ | 轻量版，省显存，**未测试** |
| `minimax_h3_fl2va_pruned_w6a8` | 16.0G | 中立 | 单卡 32G 理论可 | ❓ | 更激进量化，**未测试** |
| `minimax_h3_fl2va_bf16` | 66.3G | 中立 | ≥4×64G | ❓ | 全精度画质版，**未测试** |
| `minimax_h3_fl2va_pruned_bf16` | 40.2G | 中立 | ≥2×64G | ❓ | 半精度轻量版，**未测试** |
| `minimax_h3_fl2va_pruned_fp8_scaled` | 21.0G | 中立 | ❌ | ❌ | FP8 为 N 卡优化，昇腾不建议 |

### 文本编码器（体积与量化档才是选型依据）

| 文件 | 大小 | 来源 | 昇腾要求 | 状态 | 说明 |
|---|---|---|---|---|---|
| `qwen3vl_32b_h3_ultra_uncensored_heretic_int8_convrot` | 26.4G | 社区 | 单卡 64G | ✅ | **本仓库默认**，社区 heretic 版 |
| `qwen3vl_32b_minimax_h3_int8_convrot` | 27.1G | 官方 | 单卡 64G | ✅ | 官方版，追求稳妥可换 |
| `qwen3vl_32b_minimax_h3_nvfp4_awq` | 15.7G | 官方 | ❌ | ❌ | NVFP4：N 卡 Blackwell 专属 |
| `qwen3vl_32b_minimax_h3_bf16` | 51.5G | 官方 | ≥2×64G | ❓ | 全精度版，**未测试** |

> **⚠️ 关于「无审查文本编码器」的说明（社区最新结论）**
>
> 社区流传"换成 heretic/uncensored 文本编码器就能解锁内容"——**Heretic 作者本人已公开否认这一点**
> （PSA 帖在 r/StableDiffusion 拿到约 2450 赞）。原因很硬：文本编码器**不生成任何文字**，
> 它只把提示词编码成条件张量 `[token数, 5120]` 交给 DiT，**不存在"拒答"这个环节**；
> 社区 ClipProj 实测 abliterated 编码器与官方编码器的条件张量余弦差仅 **0.0023（≈0.23%）**，基本是噪声。
> 最坏情况还会因条件偏离训练分布而降低提示词遵循度。
>
> 越狱真正有意义的场景只有一个：把**生成尾层**（语言层 50-63 + LM 头）接成 LLM 做**提示词改写 / 增强**。
>
> 所以本仓库默认带 heretic 编码器只是"已装好、可直接对比"，**真正的自由度来自"全程本地 + 你自己的提示词"**，
> 而不是那个文件名——本方案在昇腾上跑通 60 秒长片，靠的是本地推理这一层，与编码器选哪个无关。

### VAE / 加速 LoRA

| 文件 | 大小 | 昇腾要求 | 状态 | 说明 |
|---|---|---|---|---|
| `minimax_h3_video_vae_fp16` | 5.2G | 单卡 | ✅ | 视频解码（默认） |
| `minimax_h3_video_vae_int8_convrot` | 2.8G | 单卡 | ✅ | 视频解码加速版 |
| `minimax_h3_audio_vae_fp32` | 0.6G | 单卡 | ✅ | **音频必须 fp32**，缺了会没声音 |
| `minimax_h3_fl2v_turbo_4step_v1.0` | 2.0G | 单卡 | ✅ | **4 步极速档**（提速一倍） |
| `minimax_h3_fl2v_turbo_8step_v1.0` | 2.0G | 单卡 | ✅ | 8 步画质档 |

> 原文/原始仓库：[Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) ·
> [uncensored 文本编码器](https://huggingface.co/ethanfel/Qwen3-VL-32B-Ultra-Heretic-H3-ComfyUI-INT8-ConvRot)

## 🖥️ 不同规格昇腾机器怎么配

| 机器 | 推荐配置 | 体验 |
|---|---|---|
| **2×64GB（本文实测）** | fl2va_int8 + npu_count=2 | 768P/12s 约 5~11 分钟；480P 热机 20~25 秒/条 |
| **1×64GB** | fl2va_int8 或 pruned_int8 + npu_count=1 | 480P 起步，速度约慢 1.5~2 倍；长片建议分段 |
| **1×32GB** | **精简版 pruned_int8（21GB）+ 480P + 5s + 4步** | 见下方「32GB 低配档」，显存占用约 27~30GB，贴上限 |
| **4×64GB（910C 等）** | fl2va_int8 + npu_count=4 | 接近官方满血：768P/15s 最快约 2 分钟级 |
| **8 卡以上** | 补丁当前支持到 4 卡并行 | 可多实例并行增加吞吐 |

## 🪫 32GB 单卡低配档（完整可行方案）

只有 32GB 显存的 910B？按这套走：

```bash
bash scripts/download_models.sh --lowvram   # 只下精简版主模型（21GB），跳过 34GB 完整版
bash scripts/start_comfyui.sh               # 启动（脚本会自动设 npu_count=1）
# 显存仍吃紧时：LOWVRAM=1 bash scripts/start_comfyui.sh
# 工作流选：fl2va_4step_480P低显存.json（864×480 / 5秒 / 4步 / 单卡）
```

**显存账本（单卡 32GB）**：

| 阶段 | 占用 |
|---|---|
| 文本编码器（26GB）加载 → 编码 → **卸载到内存** | 峰值 26GB，随后释放 |
| 精简版主模型 pruned_int8 | 21GB |
| 视频VAE(int8) + 音频VAE | 3.4GB |
| 激活值（480P/5s） | 约 2~5GB |
| **合计（稳态）** | **约 27~30GB** |

兜底三招（显存还是不够时，按序尝试）：
1. 分辨率降到 0.3MP（736×416）
2. 时长降到 5 秒以内
3. `LOWVRAM=1` 启动（逐层卸载到内存，速度下降但一定能跑）
4. 换 `w6a8` 主模型（16GB，**未测试**，欢迎反馈）

## 🎯 三档工作流（新手按场景直接选）

| 工作流 | 配置 | 用途 |
|---|---|---|
| `fl2va_4step_极速档.json` | 0.4MP/5s/4步 | 试提示词、批量：热机 **20~25 秒/条** |
| `fl2va_4step_0.6MP中间档.json` | 0.6MP/8s/4步 | **日常推荐**，约 1 分钟/条 |
| `fl2va_8steps_lora_int8_2npu.json` | 可自调到 1.0MP/12s | 高画质、长片分段 |
| `i2v_九宫格_昇腾适配.json` | 九宫格分镜图 → 连续剧情 | 下拉框已配好，即开即用 |
| `ref2va_8steps_lora.json` | 参考图锁角色 | 需切 ref2va 主模型 |
| `fl2va_4step_480P低显存.json` | 精简模型/864×480/5s/4步/单卡 | **32GB 卡专用** |

## 🔌 社区增强件（昇腾兼容性：待验证，欢迎实测）

H3 社区最火的两个单点工具都是**免训练、零依赖**的，理论上昇腾也能用 ——
但目前**全网没人测过昇腾**，这是本仓库的开放式 TODO：

| 增强件 | 做什么 | 收益 | 昇腾可行性判断 |
|---|---|---|---|
| [ComfyUI-Spectrum-MiniMax-H3](https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3)（682★） | 用岭回归拟合隐层特征，在"预测步"整个跳过 transformer | 省 30~35% 时间 | 🟡 依赖 `MiniMaxH3Model` 原生路径，操作是常规张量运算，**NPU 大概率可跑**，但作者只验证 CUDA/ROCm |
| [Comfyui_Minimax_h3_latent_Upscaler](https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler)（707★） | 在 24 通道 latent 上直接放大，跳过 VAE 往返 | 低分辨率出片 + 放大，**比直出高分辨率快得多** | 🟢 主体是 3D 卷积 + 三线性插值，作者已支持 ROCm 后端，**torch_npu 大概率可跑** |

```bash
# 手装（装完重启 ComfyUI）
cd $COMFY_HOME/custom_nodes
git clone https://github.com/xmarre/ComfyUI-Spectrum-MiniMax-H3.git
git clone https://github.com/LBH-123-AI/Comfyui_Minimax_h3_latent_Upscaler.git
# 放大模型（约 691MB）放到 models/latent_upscale_models/
```

> **这点很值钱**：昇腾路线的"低分辨率出片 + 潜空间放大"如果跑通，
> 等于把昇腾上 1.0MP 长片 11 分钟的耗时，换成"0.4MP 极速档 + 放大"，
> 可能把高分辨率成片从**分钟级压到秒级**。**谁先测出来，谁就是全网第一份数据** ——
> 测完欢迎开 Issue 提交（有专门的实测模板）。

## 📁 目录结构

```
├── setup.sh                    # 一键部署（自动适配卡数/CANN 路径）
├── scripts/
│   ├── dl_models.py            # 分片并行下载（40MB/s，断点续传）
│   ├── start_comfyui.sh        # 启动（自动识别卡数，内置 aarch64 修复）
│   ├── set_npu_count.py        # 按实际卡数同步所有工作流
│   ├── convert_wf.py           # ComfyUI 工作流 UI→API 转换
│   ├── driver_grid.py          # 长片流水线（尾帧接首帧 + 自动拼接）
│   ├── concat.py / 切九宫格.py  # 拼接 / 分镜切图
│   └── ...
├── workflows/                  # 10 个工作流 JSON
├── assets/                     # 昇腾适配补丁 + 验证版节点 + 演示图
├── docs/
│   ├── 出片操作手册.md
│   ├── 九宫格图生视频教程.md
│   ├── 部署踩坑记录.md          # 17 个坑与修复
│   ├── NVIDIA显卡部署指南.md     # 4090/5090 路线（参考，未实测）
│   └── ENVIRONMENT-910B.txt
├── scripts/
│   ├── setup_nvidia.sh          # N 卡一键部署
│   └── download_models_nvidia.sh # N 卡权重下载（fp8/nvfp4/w6a8）
└── windows/                    # Windows 隧道脚本（自愈重连）
```

## ⚠️ 关键注意事项

1. **音频 VAE 必须 fp32** —— 用 fp16 会没声音或音画不同步
2. **torchaudio 必须与 torch 同版本**（setup.sh 已自动处理）
3. **aarch64 需 `LD_PRELOAD=libgomp.so.1`**（启动脚本已内置）
4. **ComfyUI 必须锁 commit** `bd34f338`（补丁基于该版本）
5. 昇腾只选 `int8_convrot` 系列权重；**NVFP4 / FP8 / SLA 稀疏注意力是 N 卡专属**。
   顺带纠正一个**跨平台**结论（2026-10-13 N 卡真机验证）：**H3 的 GGUF 文本编码器在所有平台都不可用**
   —— 所有 H3 的 GGUF 编码器仓库都缺 mmproj 视觉塔，构建不出 tokenizer（`ClipLoaderGGUF` 必崩）。
   **GGUF 只适合 N 卡的"主模型"**；文本编码器一律 safetensors + 官方 `CLIPLoader`。
6. 单次最长 **15 秒**（362 帧）；更长用 `driver_grid.py` 分段接力
7. `npu_count` 必须等于实际卡数（`set_npu_count.py` 自动处理）
8. **出片立刻拉回本地** —— 租用机器随时可能回收，视频只存在服务器 `ComfyUI/output/video/`，丢了就没了

## ❓ 常见问题

**Q：下次换一台昇腾机器，能一键复原吗？**
能。`git clone`（<5MB）→ `setup.sh`（约 3 分钟）→ `download_models.sh`（90GB，40MB/s 约 40 分钟）→ `start_comfyui.sh` → 浏览器开干。前提是新机器有 CANN 环境（CANNLab 镜像自带）。

**Q：下载速度怎么样？**
实测聚合 40MB/s（16 路分片）。环境差时约 10MB/s，支持断点续传，中断重跑不丢进度。

**Q：没有昇腾、只有 N 卡能用吗？**
工作流 JSON 是通用的；模型请选对应平台的量化版本（N 卡用 nvfp4 / fp8 系列，即上文标 ❌ 的那些行，**未测试**）。

**Q：生成有内容限制吗？**
视频生成与文本编码**完全在本地运行**，不存在云端那一层审核拦截——**这才是"自由度"的真正来源**，
而不是文本编码器换成哪个版本（原因见上文[「关于无审查文本编码器的说明」](#文本编码器体积与量化档才是选型依据)）。
请自行遵守所处地区的法律法规。

## 🔗 相关项目 & 多平台镜像

| 项目 | 平台 | 说明 |
|---|---|---|
| **本项目**（昇腾） | [GitCode](https://gitcode.com/nxxwjbl/minimax-h3-ascend-uncensored) ｜ [GitHub](https://github.com/zhenhanchen1-cyber/minimax-h3-ascend) | 华为昇腾 910B/910C，真机实测 |
| **姊妹项目**（N 卡） | [GitCode](https://gitcode.com/nxxwjbl/minimax-h3-nvidia-uncensored) ｜ [GitHub](https://github.com/zhenhanchen1-cyber/minimax-h3-nvidia-uncensored) | NVIDIA 显卡，8GB 显存起，含 13 套工作流与全模型选型表；另附 [真机踩坑与前置要求](https://github.com/zhenhanchen1-cyber/minimax-h3-nvidia-uncensored/blob/main/docs/%E7%9C%9F%E6%9C%BA%E8%B8%A9%E5%9D%91%E4%B8%8E%E5%89%8D%E7%BD%AE%E8%A6%81%E6%B1%82.md) |

> 两个仓库是同一套模型的**两条硬件路线**，工作流 JSON 完全通用，可以互相参照。
> N 卡路线的加速件（SLA 稀疏注意力 / NVFP4）在昇腾上不可用，
> 且 **H3 的 GGUF 文本编码器在两条路线上都不可用**（缺 mmproj 视觉塔，只适合当主模型），
> 所以**同一条视频，N 卡所需算力约是昇腾的 1/5 ~ 1/8**——这不是昇腾不行，是生态成熟度差异。

---

## ⭐ 如果对你有帮助

**点个 Star** 是最实在的支持 —— 昇腾路线的文档本来就少，让更多在昇腾机器上折腾的人搜到它。
有实测数据、踩到新坑、或跑通了更多机型，欢迎开 [Issue](https://github.com/zhenhanchen1-cyber/minimax-h3-ascend/issues) / PR。

---

## English

**MiniMax-H3 local deployment on Huawei Ascend NPU (910B / 910C) — tested on real hardware.**

Run MiniMax-H3 (the omni-modal video model behind Hailuo 3.0) locally with ComfyUI on Ascend NPU:
text-to-video, image-to-video, reference-locked characters, native synchronized stereo audio, fully offline.

- **The scarce one**: virtually every public guide for MiniMax-H3 targets NVIDIA/CUDA. This repo is a complete,
  **actually-tested** INT8 deployment for Ascend 910B dual-card (2×64GB HBM), including measured performance
  and 17 documented pitfalls with fixes.
- **One-command setup**: `bash setup.sh` → `bash scripts/download_models.sh` → `bash scripts/start_comfyui.sh`.
  The custom sharded downloader reaches **40 MB/s** aggregate (upstream single-connection: ~2 MB/s), so ~90 GB
  of weights take ~35–40 min, with resume support.
- **Fits more than dual-card**: profiles for 1×64GB, **1×32GB (a dedicated low-VRAM workflow)**, 2×64GB and 4×64GB
  (910C); the setup script auto-detects the NPU count and syncs it into every workflow.
- **Measured**: 0.4MP / 124 frames / 4 steps → **17.8 s sampling, ~20–25 s end-to-end** per clip (warm);
  a 61-second continuous short film was produced with a keyframe-chaining pipeline included in `scripts/`.
- **Sister project**: NVIDIA GPU route (from 8GB VRAM) →
  [minimax-h3-nvidia-uncensored](https://gitcode.com/nxxwjbl/minimax-h3-nvidia-uncensored).

> Note: Ascend only supports `int8_convrot` weights. NVFP4 / FP8 / SLA sparse attention are CUDA-only.
> **GGUF text encoders do not work with H3 on any platform** (they ship no mmproj vision tower, so
> `ClipLoaderGGUF` crashes) — GGUF is only usable for the NVIDIA diffusion-model route.
> Audio VAE must be **fp32**. Max clip length is 15 s (362 frames).

**License**: MIT for scripts and docs — see [LICENSE](LICENSE) and [NOTICE.md](NOTICE.md).

---

## 致谢与许可

脚本与文档采用 **MIT 许可**。你可以自由使用、修改、二次分发 ——
**只要求一件事：保留原作者署名与本仓库链接**（这也是 MIT 的条款）。
如果你做了改进，欢迎开 PR 回流，比另起一个副本更有价值。

第三方组件归属见 [NOTICE.md](NOTICE.md)：
[Ascend-SACT 昇腾适配补丁](https://atomgit.com/Ascend-SACT/MiniMax-H3-Comfy-NPU)（Apache-2.0）、
[ComfyUI-MiniMax-H3-Turbo](https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo)（Apache-2.0）、
[ComfyUI](https://github.com/Comfy-Org/ComfyUI)（GPL-3.0）、
[Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) 模型权重。
