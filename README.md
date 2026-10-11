# MiniMax-H3 on Ascend 910B/910C · 昇腾本地部署全栈方案

> 在华为昇腾 NPU（910B / 910C）上用 ComfyUI 本地运行 **MiniMax-H3** 全模态视频生成模型：文生视频 / 图生视频 / 参考图锁角色，**原生音画同步**，单机双卡 128GB 显存，最高实测 1.0MP / 12 秒 / 8 步。
>
> 本仓库由一次真实部署（CANNLab 2×910B）完整沉淀而成：**一键复原脚本 + 实测性能数据 + 全流程踩坑修复 + 可直接导入的工作流**。

[![Platform](https://img.shields.io/badge/platform-Ascend%20910B%2F910C-green)]() [![CANN](https://img.shields.io/badge/CANN-9.0.0-blue)]() [![ComfyUI](https://img.shields.io/badge/ComfyUI-v0.32.0-purple)]()

---

## 为什么值得看

- **昇腾跑通 MiniMax-H3**：官方和社区资源大多面向 NVIDIA（CUDA/NVFP4/GGUF），本仓库给出一条**已在 910B 真机验证**的 INT8 路线（`int8_convrot` + `npu_quant_matmul`）
- **双卡序列并行**：2×64GB HBM 协同推理，768P 档单条 12 秒视频约 5~11 分钟
- **4 步极速档**：切到 4-step Turbo LoRA 后，5 秒视频采样仅 **17.8 秒**（热机连续出片约 20~25 秒/条）
- **60 秒长片流水线**：内置「尾帧接首帧」自动分段拼接脚本，突破单次 15 秒上限
- **原生音频**：视频与 32kHz 立体声同步生成，不需要后期配音（注意音频 VAE 必须 fp32）
- **踩坑全修复**：torchaudio 版本、aarch64 libgomp TLS、sqlite 兼容、HF 镜像 40MB/s 分片下载……都在 `docs/部署踩坑记录.md`

## 实测性能（2×910B，64GB×2 HBM）

| 分辨率 | 帧数/时长 | 步数 | 采样耗时 | 端到端 | 场景 |
|---|---|---|---|---|---|
| 0.4MP (864×480) | 124 / 5s | **4** | **17.8s** | 71s（冷启）→ **20~25s（热机）** | 极速档，批量出片 |
| 0.4MP (864×480) | 124 / 5s | 8 | 36.4s | 89.7s | 8 步档 |
| 0.6MP (1024×576) | 192 / 8s | 4 | 约 40s | 约 60~90s | 中间档，画质/速度平衡 |
| 1.0MP (1152×864) | 294 / 12s | 8 | 71s/步 ≈ 570s | 约 11 分钟 | 高画质长片分段 |

> 提速杠杆：**分辨率 >> 帧数 > 步数**。0.4MP→1.0MP 每步耗时 4.4s→71s（16 倍）；步数 8→4 快 2 倍。

## 快速开始

### 0. 前提

- 昇腾 NPU 环境（910B/910C，建议 ≥64GB HBM/卡），已装 **CANN ≥ 9.0.0** 与驱动
- Python 3.10~3.12，`torch` + `torch_npu`（版本需与 CANN 配套；本项目在 torch 2.7.1 + torch_npu 2.7.1.post4 验证）
- 磁盘 ≥ 150GB（模型全量约 90GB）

### 1. 一键部署

```bash
git clone https://gitcode.com/czhljj/minimax-h3-ascend.git
cd minimax-h3-ascend
bash setup.sh              # 会自动：拉取ComfyUI→打昇腾补丁→装依赖→装工作流
bash scripts/download_models.sh   # 下载全部模型（约 90GB，走 hf-mirror，支持断点续传）
bash scripts/start_comfyui.sh     # 启动服务（自动识别 NPU 数量）
```

浏览器打开 `http://127.0.0.1:8188`，从 **Workflows → minimax-h3** 选择工作流即可出片。

### 2. 三档工作流怎么选

| 工作流 | 用途 |
|---|---|
| `fl2va_4step_极速档.json` | 0.4MP/5s/4步，20~25 秒一条，试提示词、批量 |
| `fl2va_4step_0.6MP中间档.json` | 0.6MP/8s/4步，约 1 分钟一条，**日常推荐** |
| `fl2va_8steps_lora_int8_2npu.json` | 可自调到 1.0MP/12s，高画质/长片分段 |
| `i2v_九宫格_昇腾适配.json` | 九宫格分镜图 → 一段连续剧情（用户下拉框已配好） |
| `ref2va_8steps_lora.json` | Ref2VA 参考图锁角色一致性（需切 ref2va 主模型） |

### 3. 60 秒长片

```bash
python3 scripts/driver_grid.py    # 5 段 × 12 秒，尾帧接首帧，自动拼接
python3 scripts/concat.py         # ffmpeg 流拷贝，零重编码拼接
```

## 目录结构

```
├── setup.sh                    # 一键部署
├── scripts/
│   ├── download_models.sh      # 模型清单下载（hf-mirror 分片并行，40MB/s）
│   ├── dl_fast.py              # 通用分片并行下载器（33 路并发）
│   ├── start_comfyui.sh        # 启动脚本（自动识别 NPU 数/CANN 路径）
│   ├── convert_wf.py           # ComfyUI 工作流 UI→API 格式转换
│   ├── driver_grid.py          # 分镜提示词自动拆分 + 长片流水线
│   ├── concat.py               # 视频拼接（imageio-ffmpeg）
│   └── 切九宫格.py              # 九宫格分镜图切图工具
├── workflows/                  # 全部工作流 JSON
├── assets/
│   ├── comfy-ui-changes.patch  # 昇腾适配补丁（来自 Ascend-SACT 开源项目）
│   └── ComfyUI-MiniMax-H3-Turbo-verified.tgz  # 验证版 Turbo 节点
├── docs/
│   ├── 出片操作手册.md
│   ├── 九宫格图生视频教程.md
│   ├── 部署踩坑记录.md
│   └── ENVIRONMENT-910B.txt
└── windows/打开ComfyUI界面.bat  # Windows 客户端一键隧道+开浏览器
```

## 模型清单（全部来自公开仓库）

| 文件 | 大小 | 来源 | 位置 |
|---|---|---|---|
| `minimax_h3_fl2va_int8_convrot.safetensors` | 34.0 GB | Comfy-Org/MiniMax-H3 | `models/diffusion_models/` |
| `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | 21.0 GB | Comfy-Org/MiniMax-H3 | `models/diffusion_models/` |
| `qwen3vl_32b_..._int8_convrot.safetensors`（文本编码器二选一） | 27.1 GB | Comfy-Org/MiniMax-H3 | `models/text_encoders/` |
| `qwen3vl_32b_h3_ultra_uncensored_heretic_int8_convrot`（可选替代） | 26.4 GB | ethanfel（公开仓库） | `models/text_encoders/` |
| `minimax_h3_video_vae_fp16.safetensors` | 5.2 GB | Comfy-Org/MiniMax-H3 | `models/vae/` |
| `minimax_h3_audio_vae_fp32.safetensors` ⚠️ 必须 fp32 | 0.6 GB | Comfy-Org/MiniMax-H3 | `models/vae/` |
| `minimax_h3_video_vae_int8_convrot.safetensors`（可选，解码更快） | 2.8 GB | Comfy-Org/MiniMax-H3 | `models/vae/` |
| `minimax_h3_fl2v_turbo_4step_v1.0_768p_...safetensors` | 2.0 GB | Comfy-Org/MiniMax-H3 | `models/loras/` |
| `minimax_h3_fl2v_turbo_8step_v1.0_...safetensors` | 2.0 GB | Comfy-Org/MiniMax-H3 | `models/loras/` |

## 关键注意事项（血泪总结）

1. **音频 VAE 必须用 fp32**——用 fp16 会没声音或音画不同步
2. **torchaudio 必须与 torch 同版本**（如 torch 2.7.1 → torchaudio 2.7.1），否则 `undefined symbol`
3. **aarch64 下启动前加 `LD_PRELOAD=/lib/aarch64-linux-gnu/libgomp.so.1`**，否则 torchaudio 加载报 TLS 错误
4. **ComfyUI 版本必须锁 commit**（本仓库验证版本 `bd34f338`），补丁基于该版本
5. 昇腾上**不要**使用 NVFP4/GGUF 权重（NVIDIA 专属），只选 `int8_convrot`
6. 单次生成 **最长 15 秒**（362 帧）；更长请用 `driver_grid.py` 分段接力
7. `MultiNPUParallelConfig` 的 `npu_count` 必须等于实际可用卡数（1/2/4）

## 已知限制

- 昇腾缺乏 CUDA 生态的稀疏注意力优化（如 SLA），同模型同参数下速度约为高端 N 卡的 1/3~1/2
- ComfyUI 的 prompt history sqlite 落库在旧版 sqlite 系统上会报错（不影响出片）
- 本方案基于社区适配补丁（Ascend-SACT），非华为官方支持路径

## 致谢与许可

本项目脚本代码采用 **MIT 许可**。依赖组件的许可与归属见 [NOTICE.md](NOTICE.md)：
- [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3)（模型权重，遵循其仓库声明）
- [Ascend-SACT/MiniMax-H3-Comfy-NPU](https://atomgit.com/Ascend-SACT/MiniMax-H3-Comfy-NPU)（昇腾适配补丁，Apache-2.0）
- [Larryvrh/ComfyUI-MiniMax-H3-Turbo](https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo)（Turbo 采样节点，Apache-2.0）
- [ComfyUI](https://github.com/Comfy-Org/ComfyUI)（GPL-3.0）
