# Copyright (C) 2021-2022, Mindee.

# This program is licensed under the Apache License version 2.
# See LICENSE or go to <https://www.apache.org/licenses/LICENSE-2.0.txt> for full license details.

"""
Image classification latency benchmark
"""

import argparse
import os
import time

import numpy as np
import torch

os.environ['USE_TORCH'] = '1'

from doctr.models import classification


@torch.no_grad()
def main(args):

    device = torch.device("cuda:0" if args.gpu else "cpu")

    # Pretrained imagenet model
    model = classification.__dict__[args.arch](
        pretrained=args.pretrained,
    ).eval().to(device=device)

    # Input
    img_tensor = torch.rand((args.batch_size, 3, args.size, args.size)).to(device=device)

    # Warmup
    for _ in range(10):
        _ = model(img_tensor)

    timings = []

    # Evaluation runs
    for _ in range(args.it):
        start_ts = time.perf_counter()
        _ = model(img_tensor)
        timings.append(time.perf_counter() - start_ts)

    _timings = np.array(timings)
    print(f"{args.arch} ({args.it} runs on ({args.size}, {args.size}) inputs in batches of {args.batch_size})")
    print(f"mean {1000 * _timings.mean():.2f}ms, std {1000 * _timings.std():.2f}ms")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='docTR latency benchmark for image classification (PyTorch)',
                                     formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument("arch", type=str, help="Architecture to use")
    parser.add_argument("--size", type=int, default=32, help="The image input size")
    parser.add_argument("--batch-size", "-b", type=int, default=64, help="The batch_size")
    parser.add_argument("--gpu", dest="gpu", help='Should the benchmark be performed on GPU', action="store_true")
    parser.add_argument("--it", type=int, default=100, help="Number of iterations to run")
    parser.add_argument("--pretrained", dest="pretrained", help="Use pre-trained models from the modelzoo",
                        action="store_true")
    args = parser.parse_args()

    main(args)
