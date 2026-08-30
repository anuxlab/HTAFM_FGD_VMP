#!/usr/bin/env python3
"""
Parses simulation logs and extracts key metrics.
"""
import os
import re
import glob
import json
import argparse
import pandas as pd

def parse_alloc_line(line):
    """Extract metrics from [Alloc] line."""
    pattern = r"Used nodes: (\d+); Used GPUs: (\d+); Used GPU Milli: (\d+); Total GPUs: (\d+)"
    match = re.search(pattern, line)
    if match:
        return {
            "used_nodes": int(match.group(1)),
            "used_gpus": int(match.group(2)),
            "used_gpu_milli": int(match.group(3)),
            "total_gpus": int(match.group(4)),
            "gpu_utilization": int(match.group(3)) / (int(match.group(4)) * 1000)
        }
    return None

def parse_frag_line(line):
    """Extract fragmentation ratio from [Report] line."""
    pattern = r"Frag ratio: ([\d.]+)%"
    match = re.search(pattern, line)
    return float(match.group(1)) if match else None

def parse_unscheduled(line):
    """Extract unscheduled pod count."""
    pattern = r"there are (\d+) unscheduled pods"
    match = re.search(pattern, line)
    return int(match.group(1)) if match else None

def parse_summary_lines(lines):
    """Parse summary lines from the end of the log."""
    summary = {}
    for line in lines:
        if "Allocation Ratio" in line:
            if "MilliCpuLeft" in line:
                summary["cpu_utilization"] = parse_percentage(line)
            elif "Memory" in line:
                summary["memory_utilization"] = parse_percentage(line)
            elif "MilliGpu" in line:
                summary["gpu_utilization"] = parse_percentage(line)
        elif "Frag ratio" in line:
            summary["fragmentation"] = parse_frag_line(line)
        elif "unscheduled pods" in line:
            summary["unscheduled_pods"] = parse_unscheduled(line)
    return summary

def parse_percentage(line):
    """Extract percentage from summary line."""
    match = re.search(r"([\d.]+)%", line)
    return float(match.group(1)) if match else None

def process_log(log_path):
    """Process a single log file and return metrics."""
    with open(log_path, 'r') as f:
        content = f.read()
    
    lines = content.split('\n')
    
    # Extract policy name from path
    policy = os.path.basename(os.path.dirname(log_path))
    if 'fgd' in policy.lower():
        policy_name = 'FGD'
    elif 'bestfit' in policy.lower():
        policy_name = 'BestFit'
    elif 'random' in policy.lower():
        policy_name = 'Random'
    else:
        policy_name = policy
    
    # Find last allocation line
    alloc_lines = [l for l in lines if '[Alloc]' in l]
    final_alloc = parse_alloc_line(alloc_lines[-1]) if alloc_lines else None
    
    # Find fragmentation from last report
    frag_lines = [l for l in lines if 'Frag ratio' in l]
    fragmentation = parse_frag_line(frag_lines[-1]) if frag_lines else None
    
    # Find unscheduled pods
    unscheduled = parse_unscheduled(content)
    
    return {
        "policy": policy_name,
        "final_allocation": final_alloc,
        "fragmentation": fragmentation,
        "unscheduled_pods": unscheduled
    }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", default="experiments")
    parser.add_argument("--output-dir", default="../results")
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)

    log_files = glob.glob(f"{args.input_dir}/test_*/log-*.log")
    all_results = []

    for log_file in log_files:
        print(f"📊 Processing: {log_file}")
        results = process_log(log_file)
        all_results.append(results)

    # Save to CSV
    df = pd.DataFrame(all_results)
    df.to_csv(f"{args.output_dir}/experiment_results.csv", index=False)

    # Save to JSON for README update
    with open(f"{args.output_dir}/results.json", 'w') as f:
        json.dump(all_results, f, indent=2)

    print(f"✅ Results saved to {args.output_dir}/")

if __name__ == "__main__":
    main()