#!/bin/bash
source /home/developer/Ascend/ascend-toolkit/set_env.sh 2>/dev/null
export HF_ENDPOINT=https://hf-mirror.com
export HF_HUB_ENABLE_HF_TRANSFER=1
export HF_XET_HIGH_PERFORMANCE=1
cd /mnt/workspace
setsid nohup python3 /mnt/workspace/dl_models.py > /mnt/workspace/dl_models.log 2>&1 &
echo "LAUNCHED $!"
