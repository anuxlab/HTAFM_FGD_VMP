#!/usr/bin/env python3
"""
Updates README.md with experiment results.
"""
import json
import argparse
from datetime import datetime

def generate_markdown_table(results):
    """Generate markdown table from results."""
    table = "| Policy | GPU Utilization | Fragmentation | Unscheduled Pods | Duration |\n"
    table += "|--------|----------------|---------------|------------------|----------|\n"
    
    for r in results:
        util = r.get('final_allocation', {}).get('gpu_utilization', 'N/A')
        if isinstance(util, float):
            util = f"{util*100:.1f}%"
        
        frag = r.get('fragmentation', 'N/A')
        if frag and isinstance(frag, float):
            frag = f"{frag:.1f}%"
        
        unsched = r.get('unscheduled_pods', 'N/A')
        
        table += f"| {r['policy']} | {util} | {frag} | {unsched} | {r.get('duration', 'N/A')}s |\n"
    
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
        print("No results found. Skipping README update.")
        return

    # Read existing README
    try:
        with open(args.readme, 'r') as f:
            readme_content = f.read()
    except FileNotFoundError:
        readme_content = ""

    # Generate new content
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
    table = generate_markdown_table(results)

    new_section = f"""
## 📊 Latest Experiment Results

*Last updated: {timestamp}*

### Summary Table

{table}

### How to Reproduce

1. Clone the repository
2. Run experiments:
```bash
cd simulator
python3 scripts/generate_config_and_run.py -d experiments/test_fgd -e -b -f data/openb_pod_list_gpushare40 -FGD 1000 -gpusel FGD -dimext share -norm max -tune 1.3 -tuneseed 50 --shuffle-pod=true -z experiments/test_fgd/snapshot/ds01