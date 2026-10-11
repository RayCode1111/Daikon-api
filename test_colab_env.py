import subprocess
import sys

print("Python executable:", sys.executable)
print("GPU Info:")
print(subprocess.getoutput("nvidia-smi --query-gpu=gpu_name,memory.total,memory.free --format=csv"))
print("\nCheck if vllm or cloudflared is installed:")
print("vllm:", subprocess.getoutput("pip show vllm | head -n 3"))
print("cloudflared:", subprocess.getoutput("which cloudflared"))

