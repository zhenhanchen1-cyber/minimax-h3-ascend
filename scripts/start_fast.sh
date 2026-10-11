#!/bin/bash
cd /mnt/workspace
setsid nohup python3 /mnt/workspace/dl_fast.py > /mnt/workspace/dl_fast.log 2>&1 &
echo "LAUNCHED $!"
