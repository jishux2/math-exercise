import subprocess
import sys

# 打印当前Python解释器路径，用来确认是否在虚拟环境中
print(f"当前Python解释器路径：{sys.executable}")

deps = [
    "ballyregan",
    "git+https://github.com/jishux2/poe-api-wrapper.git@v2",
    "numpy==1.26.4"
]

for dep in deps:
    print(f"正在安装：{dep}")
    subprocess.check_call([sys.executable, "-m", "pip", "install", dep])
