#!/usr/bin/env python3
"""
Generates a complete README.md from experiment results.
"""
import json
import argparse
from datetime import datetime

def generate_table(results):
    """Generate markdown table from results."""
    table = "| Policy | GPU Utilization | Fragmentation | Unscheduled Pods | Duration (s) |\n"
    table += "|--------|----------------|---------------|------------------|--------------|\n"
    
    for r in results:
        util = r.get('final_allocation', {}).get('gpu_utilization', 'N/A')
        if isinstance(util, float):
            util = f"{util*100:.1f}%"
        
        frag = r.get('fragmentation', 'N/A')
        if frag and isinstance(frag, float):
            frag = f"{frag:.1f}%"
        
        unsched = r.get('unscheduled_pods', 'N/A')
        dur = r.get('duration', 'N/A')
        
        table += f"| {r['policy']} | {util} | {frag} | {unsched} | {dur} |\n"
    
    return table

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results-dir", default="results")
    parser.add_argument("--readme", default="README.md")
    args = parser.parse_args()

    # Load results
    try:
        with open(f"{args.results_dir}/results.json", 'r') as f:
            results = json.load(f)
    except FileNotFoundError:
        print("⚠️ No results found. Generating README with placeholder.")
        results = []

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    table = generate_table(results)

    # Build complete README content (no partial updates)
    readme_content = f"""# VM Placement Experiments (Bin Packing)

    Automated benchmark for GPU VM placement policies using the Alibaba GPU trace.

    ## 📊 Latest Experiment Results

    *Last updated: {timestamp}*

    ### Summary Table

    {table}

    ### How to Reproduce

    Clone the repository and run the experiments:

    ```bash
    cd simulator
    # FGD
    python3 scripts/generate_config_and_run.py -d experiments/test_fgd -e -b -f data/openb_pod_list_gpushare40 -FGD 1000 -gpusel FGD -dimext share -norm max -tune 1.3 -tuneseed 50 --shuffle-pod=true -z experiments/test_fgd/snapshot/ds01

    # BestFit
    python3 scripts/generate_config_and_run.py -d experiments/test_bestfit -e -b -f data/openb_pod_list_gpushare40 -BestFit 1000 -tune 1.3 -tuneseed 50 --shuffle-pod=true -z experiments/test_bestfit/snapshot/ds01

    # Random
    python3 scripts/generate_config_and_run.py -d experiments/test_random -e -b -f data/openb_pod_list_gpushare40 -Random 1000 -gpusel random -tune 1.3 -tuneseed 50 --shuffle-pod=true -z experiments/test_random/snapshot/ds01
    """