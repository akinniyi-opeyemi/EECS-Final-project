# scripts/config.py
# Auto-detects environment and returns correct paths and ports.
# Import this in infer.py and infer_rq2.py instead of hardcoding.

import os, socket

def get_env_config():
    hostname = socket.gethostname()

    if "bridges2" in hostname or "psc.edu" in hostname or hostname.startswith("v0"):
        return {
            "env":            "bridges2",
            "model_base":     "/ocean/projects/tra260004p/akinniyi/models",
            "course_reg_port": 9001,
            "agent_ports": {
                "uitars":   9002,
                "qwen25":   9003,
                "internvl": 9004,
            }
        }
    elif "gl" in hostname or "greatlakes" in hostname or "arc-ts" in hostname:
        return {
            "env":            "greatlakes",
            "model_base":     "/scratch/eecs545w26_class_root/eecs545w26_class/akinniyi/models",
            "course_reg_port": 8001,
            "agent_ports": {
                "uitars":   8001,
                "qwen25":   8002,
                "internvl": 8003,
            }
        }
    else:
        return {
            "env":            "mac",
            "model_base":     "",
            "course_reg_port": 8001,
            "agent_ports": {
                "uitars":   8001,
                "qwen25":   8002,
                "internvl": 8003,
            }
        }

CONFIG = get_env_config()

def model_path(model_name):
    """Return full model path for local models."""
    base = CONFIG["model_base"]
    models = {
        "uitars":   "UI-TARS-7B-DPO",
        "qwen25":   "Qwen2.5-VL-7B-Instruct",
        "internvl": "InternVL2-8B",
    }
    if model_name not in models:
        return model_name
    return os.path.join(base, models[model_name]) if base else models[model_name]

def agent_url(agent_name):
    """Return default vLLM base URL for local agents."""
    port = CONFIG["agent_ports"].get(agent_name, 8001)
    return f"http://localhost:{port}/v1"

def is_course_reg_url(url):
    """Check if URL is a course registration page needing extra wait."""
    port = str(CONFIG["course_reg_port"])
    return port in url

if __name__ == "__main__":
    print(f"Environment: {CONFIG['env']}")
    print(f"Model base:  {CONFIG['model_base']}")
    print(f"Course reg port: {CONFIG['course_reg_port']}")
    for agent, port in CONFIG['agent_ports'].items():
        print(f"  {agent}: localhost:{port}")
    print(f"  uitars path: {model_path('uitars')}")