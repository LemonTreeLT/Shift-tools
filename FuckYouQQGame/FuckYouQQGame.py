import os
import psutil
import ctypes
import sys
from pathlib import Path

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False

def run_as_admin():
    if is_admin():
        return True
    else: 
        try:
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
            return True
        except Exception as e:
            print(f"Failed to elevate permissions: {e}")
        return False

def kill_process_using_file(file_path):
    for proc in psutil.process_iter(['pid', 'name', 'open_files']):
        try:
            if proc.info['open_files']:
                for file in proc.info['open_files']:
                    if file_path == file.path:
                        proc.kill()
                        print(f"Killed process {proc.info['name']} with PID {proc.info['pid']}")
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass

def delete_folder(folder_path):
    if os.path.exists(folder_path):
        for root, dirs, files in os.walk(folder_path, topdown=False):
            for name in files:
                file_path = os.path.join(root, name)
                try:
                    os.remove(file_path)
                except PermissionError:
                    print(f"File {file_path} is in use. Trying to kill the process...")
                    kill_process_using_file(file_path)
                    os.remove(file_path)
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(folder_path)
        print(f"Deleted folder: {folder_path}")
    else:
        print(f"The folder {folder_path} does not exist.")

if __name__ == "__main__":
    if not is_admin():
        if not run_as_admin():
            sys.exit("Administrator privileges are required to run this script.")
    
    # Get Roaming folder path
    roaming_path = Path(os.getenv('APPDATA'))

    # Paths to delete
    folders_to_delete = [
        roaming_path / "QQ" / "dynamic_package" / "gameCenterQQPlay",
        roaming_path / "QQ" / "qqgame",
        roaming_path / "qqgameshare"
    ]

    for folder in folders_to_delete:
        delete_folder(folder)
