import sys, subprocess
print("Python:", sys.version)
print("Pip cache info:")
res = subprocess.run(["pip", "install", "-q", "vllm"], capture_output=True, text=True)
print("Returncode:", res.returncode)
if res.returncode != 0:
    print("Stderr:", res.stderr)
else:
    print("vLLM installed successfully!")

