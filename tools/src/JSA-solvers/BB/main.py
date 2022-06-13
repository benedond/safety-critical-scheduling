#! /usr/bin/python3
import argparse
import logging
import os 


parser = argparse.ArgumentParser()
parser.add_argument("--input", "-i", type=str, required=True, help="Path to the input file.")
parser.add_argument("--output", "-o", type=str, required=True, help="Path to the output file.")
parser.add_argument("--timelimit", "-t", type=float, default=60, help="Timelimit.")
parser.add_argument("--path_lr", "-c", type=str, required=True, help="Path to the LR coefficients.")
parser.add_argument("--platform", "-p", type=str, required=True, help="Platform [imx8a, imb8b, tx2].", choices=["imx8a", "imx8b", "tx2"])
parser.add_argument("--model", "-m", type=str, required=True, help="Power model to be used for fitness evaluation [sm, lr].", choices=["sm", "lr"])

if __name__ == "__main__":
    args = parser.parse_args()
    input_filename = args.input

    logging.info("Running julia.")
    os.system(f"julia -t 1 main.jl -i {args.input} -o {args.output} -t {args.timelimit} -c {args.path_lr} -p {args.platform} -m {args.model}")