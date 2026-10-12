# MiniMax-H3 (Uncensored 去审核版) · 昇腾 910B/910C 本地部署全栈方案

> 在华为昇腾 NPU（910B / 910C）上用 ComfyUI 本地运行 **MiniMax-H3** 全模态视频生成：
> 文生视频 / 图生视频 / 参考图锁角色，**原生音画同步**，文本编码器可选**无审查（Uncensored）版本**，
> 完全本地运行、无云端内容限制，免费无限量。

## 🔥 三大看点

1. **无审查运行** —— 文本编码器提供社区 **uncensored（heretic）** 版本，视频生成全程本地，没有云端审核掐提示词的问题
2. **昇腾真机部署** —— 官方和社区资料几乎全是 NVIDIA 路线（CUDA/NVFP4/GGUF），本仓库提供**已在 910B 双卡实测跑通**的 INT8 完整方案，单机 128GB HBM
3. **开箱即用 + 一键复原** —— 换一台昇腾机器，clone → 三条命令 → 浏览器开干；附实测性能数据与 17 条踩坑修复

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

### 文本编码器（决定"审查"）

| 文件 | 大小 | 审查 | 昇腾要求 | 状态 | 说明 |
|---|---|---|---|---|---|
| `qwen3vl_32b_h3_ultra_uncensored_heretic_int8_convrot` | 26.4G | **无审查** 🔥 | 单卡 64G | ✅ | **本仓库默认**，社区 uncensored 版 |
| `qwen3vl_32b_minimax_h3_int8_convrot` | 27.1G | 官方有审查 | 单卡 64G | ✅ | 官方版，追求稳妥可换 |
| `qwen3vl_32b_minimax_h3_nvfp4_awq` | 15.7G | 官方有审查 | ❌ | ❌ | NVFP4：N 卡 Blackwell 专属 |
| `qwen3vl_32b_minimax_h3_bf16` | 51.5G | 官方有审查 | ≥2×64G | ❓ | 全精度版，**未测试** |

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
│   └── ENVIRONMENT-910B.txt
└── windows/                    # Windows 隧道脚本（自愈重连）
```

## ⚠️ 关键注意事项

1. **音频 VAE 必须 fp32** —— 用 fp16 会没声音或音画不同步
2. **torchaudio 必须与 torch 同版本**（setup.sh 已自动处理）
3. **aarch64 需 `LD_PRELOAD=libgomp.so.1`**（启动脚本已内置）
4. **ComfyUI 必须锁 commit** `bd34f338`（补丁基于该版本）
5. 昇腾只选 `int8_convrot` 系列权重；**NVFP4 / GGUF / FP8 是 N 卡专属**
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
视频生成完全在本地运行，本仓库默认文本编码器为社区 uncensored 版本，不存在云端审核拦截；请自行遵守所处地区的法律法规。

## 📦 多平台镜像

| 平台 | 地址 |
|---|---|
| GitCode | https://gitcode.com/nxxwjbl/minimax-h3-ascend-uncensored |
| GitHub | https://github.com/zhenhanchen1-cyber/minimax-h3-ascend-uncensored |

## 致谢与许可

脚本与文档采用 **MIT 许可**。第三方组件归属见 [NOTICE.md](NOTICE.md)：
[Ascend-SACT 昇腾适配补丁](https://atomgit.com/Ascend-SACT/MiniMax-H3-Comfy-NPU)（Apache-2.0）、
[ComfyUI-MiniMax-H3-Turbo](https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo)（Apache-2.0）、
[ComfyUI](https://github.com/Comfy-Org/ComfyUI)（GPL-3.0）、
[Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) 模型权重。
