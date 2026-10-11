# NOTICE · 第三方组件与许可

本仓库（MiniMax-H3 on Ascend 部署方案）的脚本与文档采用 MIT 许可。
以下第三方组件的版权与许可归其各自作者所有：

## 模型权重（不在本仓库中，由脚本从公开仓库下载）

| 组件 | 来源 | 说明 |
|---|---|---|
| MiniMax-H3（DiT / 文本编码器 / VAE / Turbo LoRA） | [Comfy-Org/MiniMax-H3](https://huggingface.co/Comfy-Org/MiniMax-H3) | 请遵循其仓库声明的许可条款 |
| Qwen3-VL 文本编码器（可选替代版本） | [ethanfel/Qwen3-VL-32B-Ultra-Heretic-H3-ComfyUI-INT8-ConvRot](https://huggingface.co/ethanfel/Qwen3-VL-32B-Ultra-Heretic-H3-ComfyUI-INT8-ConvRot) | 社区公开权重，按原仓库声明使用 |

## 代码与补丁

| 组件 | 来源 | 许可 |
|---|---|---|
| `assets/comfy-ui-changes.patch`（昇腾 NPU 多卡适配补丁） | [Ascend-SACT/MiniMax-H3-Comfy-NPU](https://atomgit.com/Ascend-SACT/MiniMax-H3-Comfy-NPU) | Apache-2.0 |
| `assets/ComfyUI-MiniMax-H3-Turbo-verified.tgz`（Turbo 采样节点归档，含本地 NPU 兼容修改） | 基于 [Larryvrh/ComfyUI-MiniMax-H3-Turbo](https://github.com/Larryvrh/ComfyUI-MiniMax-H3-Turbo) | Apache-2.0 |
| ComfyUI 本体（由 setup.sh 从上游克隆，不包含在本仓库） | [Comfy-Org/ComfyUI](https://github.com/Comfy-Org/ComfyUI) | GPL-3.0 |

> 说明：本仓库以"补丁 + 归档 + 一键脚本"的形式分发昇腾适配层，便于在昇腾硬件上复现；
> 所有上游代码的修改均在 patch 文件中明示，且保留原始 LICENSE 文件。

## 引用

如果本项目对你的工作有帮助，欢迎在文档中引用：

```
MiniMax-H3 on Ascend 910B/910C 部署方案
基于 ComfyUI + CANN + Ascend-SACT 适配补丁
```
