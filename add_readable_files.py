import os
import subprocess

def add_readable_files():
    for root, dirs, files in os.walk('.'):
        if '.git' in root or 'node_modules' in root or 'venv' in root or '__pycache__' in root:
            continue
        for file in files:
            path = os.path.join(root, file)
            try:
                with open(path, 'rb') as f:
                    f.read(1)
                # If readable, add to git
                subprocess.run(['git', 'add', path], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                print(f"Added {path}")
            except Exception as e:
                print(f"Skipping {path}: {e}")

if __name__ == '__main__':
    add_readable_files()
