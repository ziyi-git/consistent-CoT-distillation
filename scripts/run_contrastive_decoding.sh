#!/bin/bash

dataset="strategyQA"
prompt="explanation"

output_prefix="outputs/${dataset}/"
if [ -d "$output_prefix" ]; then
    rm -r $output_prefix
fi
mkdir -p $output_prefix

python -u \
    contrastive_decoding_rationalization.py \
    --output_prefix $output_prefix \
    --dataset $dataset \
    --prompt $prompt \
    >${output_prefix}/rationalization.log 2>&1 &
