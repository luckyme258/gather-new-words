import subprocess
import sys

def package_application():
    """执行修正后的PyInstaller命令打包应用程序"""
    # 修正：移除了--exclude-module=tkinter.constants，因为它是Tkinter必需模块
    command = [
        "pyinstaller",
        "--onefile",
        "--noconsole",
        "--strip",
        "--clean",
        "--exclude-module=tkinter.test",  # 保留排除非必需的测试模块
        "--exclude-module=tkinter.tix",   # 保留排除不常用的tix模块
        "gather-improve.py"
    ]
    
    try:
        print("开始打包应用程序...")
        result = subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        print("打包完成！生成的exe文件在dist目录下")
        print("标准输出:")
        print(result.stdout)
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"打包失败，错误代码: {e.returncode}")
        print("错误输出:")
        print(e.stderr)
        return False
    except FileNotFoundError:
        print("错误: 未找到pyinstaller命令，请确保已安装PyInstaller")
        return False
    except Exception as e:
        print(f"发生未知错误: {str(e)}")
        return False

if __name__ == "__main__":
    success = package_application()
    sys.exit(0 if success else 1)
