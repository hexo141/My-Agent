#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
IndexTTS2 自动安装脚本
支持 Windows、Linux、macOS
自动完成环境配置、仓库克隆、依赖安装和模型下载。
"""
import os
import sys
import platform
import subprocess
import shutil
from pathlib import Path

class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'

def print_step(msg):
    print(f"\n{Colors.HEADER}===> {msg}{Colors.ENDC}")

def print_ok(msg):
    print(f"{Colors.OKGREEN}[SUCCESS] {msg}{Colors.ENDC}")

def print_warn(msg):
    print(f"{Colors.WARNING}[WARNING] {msg}{Colors.ENDC}")

def print_error(msg):
    print(f"{Colors.FAIL}[ERROR] {msg}{Colors.ENDC}")

def run(cmd, check=True, verbose=True):
    """执行shell命令"""
    if verbose:
        print(f"运行: {cmd}")
    result = subprocess.run(cmd, shell=True)
    if check and result.returncode != 0:
        print_error(f"命令失败: {cmd}")
        sys.exit(1)
    return result.returncode == 0

def check_python_version():
    """检查Python版本"""
    print_step("检查 Python 版本")
    if sys.version_info < (3, 8):
        print_error("需要 Python 3.8 或更高版本")
        sys.exit(1)
    print_ok(f"Python 版本: {sys.version.split()[0]}")

def check_cuda():
    """检查CUDA环境"""
    print_step("检查 CUDA 环境")
    try:
        import torch
        if torch.cuda.is_available():
            print_ok(f"CUDA 可用: {torch.cuda.get_device_name(0)}")
            print_ok(f"CUDA 版本: {torch.version.cuda}")
        else:
            print_warn("CUDA 不可用，将使用 CPU 模式（速度较慢）")
    except ImportError:
        print_warn("未检测到 PyTorch，将在安装依赖时自动安装")

def install_git_lfs():
    """安装git和git-lfs"""
    print_step("安装 Git 和 Git LFS")
    system = platform.system()

    # 检查git是否已安装
    if not shutil.which("git"):
        if system == "Linux":
            run("sudo apt update")
            run("sudo apt install -y git")
        elif system == "Darwin":
            run("brew install git")
        elif system == "Windows":
            print_error("请先安装 Git: https://git-scm.com/download/win")
            sys.exit(1)

    # 检查git-lfs是否已安装
    if not shutil.which("git-lfs"):
        if system == "Linux":
            run("sudo apt install -y git-lfs")
        elif system == "Darwin":
            run("brew install git-lfs")
        elif system == "Windows":
            print_error("请先安装 Git LFS: https://git-lfs.com/")
            sys.exit(1)

    run("git lfs install")
    print_ok("Git 和 Git LFS 已就绪")

def setup_mirrors():
    """设置镜像源"""
    print_step("配置镜像源")
    
    # 检测是否为中国用户（通过ping检测延迟）
    def is_china_user():
        try:
            # 测试访问百度的延迟
            result = subprocess.run(["ping", "-c", "1", "baidu.com"], 
                                  stdout=subprocess.PIPE, 
                                  stderr=subprocess.PIPE,
                                  timeout=2)
            return result.returncode == 0
        except:
            return False
    
    if is_china_user():
        print_ok("检测到中国用户，使用国内镜像源")
        # 设置环境变量
        os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
        # 返回国内镜像URL列表
        return {
            "is_china": True,
            "pip_mirrors": [
                "https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple",
                "https://mirrors.aliyun.com/pypi/simple"
            ]
        }
    else:
        print_ok("使用默认源")
        return {
            "is_china": False,
            "pip_mirrors": ["https://pypi.org/simple"]
        }

def install_uv():
    """安装uv包管理器"""
    print_step("安装 UV 包管理器")
    success = False
    for pip_mirror in setup_mirrors():
        try:
            cmd = f"{sys.executable} -m pip install -i {pip_mirror} -U uv"
            if run(cmd, check=False):
                success = True
                break
        except Exception as e:
            print_warn(f"从 {pip_mirror} 安装失败: {e}")

    if not success:
        print_error("UV 安装失败")
        sys.exit(1)
    print_ok("UV 包管理器已安装")

def clone_repository():
    """克隆代码仓库"""
    print_step("克隆 IndexTTS2 代码仓库")
    if not os.path.exists("index-tts"):
        run("git clone https://github.com/index-tts/index-tts.git")
    os.chdir("index-tts")
    run("git lfs pull")
    print_ok("代码仓库克隆完成")

def install_dependencies():
    """安装项目依赖"""
    print_step("安装项目依赖")
    mirrors_config = setup_mirrors()
    success = False

    for mirror in mirrors_config["pip_mirrors"]:
        try:
            cmd = f"uv sync --all-extras --default-index {mirror}"
            if run(cmd, check=False):
                success = True
                break
        except Exception as e:
            print_warn(f"从 {mirror} 安装依赖失败: {e}")

    if not success:
        print_error("依赖安装失败")
        sys.exit(1)
    print_ok("项目依赖安装完成")

def download_models():
    """下载模型"""
    print_step("下载 IndexTTS2 模型")
    
    # 创建checkpoints目录
    os.makedirs("checkpoints", exist_ok=True)
    
    # 获取区域配置
    mirrors_config = setup_mirrors()
    success = False
    
    if mirrors_config["is_china"]:
        # 中国用户优先使用ModelScope
        try:
            print("从 ModelScope 下载...")
            run("uv tool install 'modelscope'")
            if run("modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints", check=False):
                success = True
        except Exception as e:
            print_warn(f"从 ModelScope 下载失败: {e}")
            
        # ModelScope失败后尝试HuggingFace镜像
        if not success:
            try:
                print("\n从 HuggingFace 镜像下载...")
                run("uv tool install 'huggingface-hub[cli,hf_xet]'")
                if run("hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints", check=False):
                    success = True
            except Exception as e:
                print_warn(f"从 HuggingFace 镜像下载失败: {e}")
    else:
        # 海外用户优先使用HuggingFace
        try:
            print("从 HuggingFace 下载...")
            run("uv tool install 'huggingface-hub[cli,hf_xet]'")
            if run("hf download IndexTeam/IndexTTS-2 --local-dir=checkpoints", check=False):
                success = True
        except Exception as e:
            print_warn(f"从 HuggingFace 下载失败: {e}")

        # HuggingFace失败后尝试ModelScope
        if not success:
            try:
                print("\n从 ModelScope 下载...")
                run("uv tool install 'modelscope'")
                if run("modelscope download --model IndexTeam/IndexTTS-2 --local_dir checkpoints", check=False):
                    success = True
            except Exception as e:
                print_warn(f"从 ModelScope 下载失败: {e}")

    if not success:
        print_error("模型下载失败，请检查网络连接后重试")
        sys.exit(1)
    print_ok("模型下载完成")

def check_gpu_support():
    """检查GPU支持"""
    print_step("检查 GPU 支持")
    try:
        result = subprocess.run(
            [sys.executable, "tools/gpu_check.py"],
            capture_output=True,
            text=True
        )
        print(result.stdout)
        if result.returncode != 0:
            print_warn("GPU 检查失败，可能影响性能")
    except Exception as e:
        print_warn(f"GPU 检查出错: {e}")

def main():
    """主函数"""
    # 显示欢迎信息
    print(f"{Colors.HEADER}开始安装 IndexTTS2...{Colors.ENDC}")

    # 1. 检查Python版本
    check_python_version()

    # 2. 检查CUDA环境
    check_cuda()

    # 3. 安装git和git-lfs
    install_git_lfs()

    # 4. 安装uv包管理器
    install_uv()

    # 5. 克隆代码仓库
    clone_repository()

    # 6. 安装依赖
    install_dependencies()

    # 7. 下载模型
    download_models()

    # 8. 检查GPU支持
    check_gpu_support()

    print(f"\n{Colors.OKGREEN}IndexTTS2 安装完成！{Colors.ENDC}")
    print(f"{Colors.OKBLUE}可以进入 index-tts 目录使用了！{Colors.ENDC}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n安装被用户中断")
        sys.exit(1)
    except Exception as e:
        print_error(f"安装过程出错: {e}")
        sys.exit(1)
