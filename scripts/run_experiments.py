#!/usr/bin/env python3
"""
Orchestrates the full experiment workflow.
"""
import os
import sys
import subprocess
import time
import json
import argparse

def run_command(cmd, description, timeout=3600):
    """Run a shell command and return output, time, and success."""
    print(f"\n🚀 {description}...")
    start_time = time.time()
    try:
        result = subprocess.run(
            cmd, shell=True, check=True,
            capture_output=True, text=True
        )
        duration = time.time() - start_time
        print(f"✅ Done in {duration:.2f}s")
        return {
            "success": True,
            "duration": duration,
            "output": result.stdout,
            "error": result.stderr
        }
    except subprocess.CalledProcessError as e:
        duration = time.time() - start_time
        print(f"❌ Failed after {duration:.2f}s")
        return {
            "success": False,
            "duration": duration,
            "output": e.stdout,
            "error": e.stderr
        }

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow", choices=["baselines", "htafm", "all"],
                       default="baselines")
    parser.add_argument("--trace", default="openb_pod_list_gpushare40")
    args = parser.parse_args()

    os.chdir("simulator")
    results = {}

    experiments = [
        {
            "name": "FGD",
            "cmd": (
                "python3 scripts/generate_config_and_run.py "
                f"-d experiments/test_fgd -e -b -f data/{args.trace} "
                "-FGD 1000 -gpusel FGD -dimext share -norm max "
                "-tune 1.3 -tuneseed 50 --shuffle-pod=true "
                "-z experiments/test_fgd/snapshot/ds01"
            )
        },
        {
            "name": "BestFit",
            "cmd": (
                "python3 scripts/generate_config_and_run.py "
                f"-d experiments/test_bestfit -e -b -f data/{args.trace} "
                "-BestFit 1000 "
                "-tune 1.3 -tuneseed 50 --shuffle-pod=true "
                "-z experiments/test_bestfit/snapshot/ds01"
            )
        },
        {
            "name": "Random",
            "cmd": (
                "python3 scripts/generate_config_and_run.py "
                f"-d experiments/test_random -e -b -f data/{args.trace} "
                "-Random 1000 -gpusel random "
                "-tune 1.3 -tuneseed 50 --shuffle-pod=true "
                "-z experiments/test_random/snapshot/ds01"
            )
        }
    ]

    for exp in experiments:
        result = run_command(exp["cmd"], f"Running {exp['name']}")
        results[exp["name"]] = result

    # Save metadata
    with open("../results/experiment_metadata.json", "w") as f:
        json.dump(results, f, indent=2)

if __name__ == "__main__":
    main()