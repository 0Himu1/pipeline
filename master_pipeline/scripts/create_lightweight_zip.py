import os
import zipfile
import time

root_dir = r"D:\Himu\Luna"
zip_name = "Luna_Project_Master.zip"
zip_path = os.path.join(root_dir, zip_name)

if os.path.exists(zip_path):
    os.remove(zip_path)

# Projects to include: ONLY The Locksmith's Spare Key as the reference example
allowed_project = "The Locksmith's Spare Key"

start_time = time.time()
file_count = 0
total_size = 0

with zipfile.ZipFile(zip_path, 'w', allowZip64=True) as z:
    for foldername, subfolders, filenames in os.walk(root_dir):
        # Exclude pycache and git
        if '__pycache__' in foldername or '.git' in foldername:
            continue
        
        rel_folder = os.path.relpath(foldername, root_dir)
        
        # Filter projects folder: only allow README.md and the single example project
        if rel_folder.startswith('projects'):
            parts = rel_folder.split(os.sep)
            if len(parts) > 1 and parts[1] != allowed_project:
                # Skip all other projects
                continue
            if 'sequenced_images' in rel_folder:
                # Skip heavy sequenced images folder
                continue

        for filename in filenames:
            if filename == zip_name or filename.endswith('.tmp') or filename.endswith('.pyc') or filename.startswith('Luna_'):
                continue
            
            # Exclude video files, heavy raw image zip archives, and intermediate wavs from the example project
            if filename.lower().endswith(('.mp4', '.zip', '.wav')):
                continue

            filepath = os.path.join(foldername, filename)
            relpath = os.path.relpath(filepath, root_dir)
            ext = os.path.splitext(filename)[1].lower()
            
            compress_type = zipfile.ZIP_DEFLATED if ext in ['.txt', '.py', '.js', '.json', '.md', '.html', '.css', '.srt'] else zipfile.ZIP_STORED
            z.write(filepath, relpath, compress_type=compress_type)
            file_count += 1
            total_size += os.path.getsize(filepath)

elapsed = time.time() - start_time
zip_size = os.path.getsize(zip_path)
print(f"Lightweight zip created in {elapsed:.2f}s!")
print(f"Total files: {file_count}")
print(f"Uncompressed size: {total_size / (1024*1024):.2f} MB")
print(f"Zip archive size: {zip_size / (1024*1024):.2f} MB")
print(f"Location: {zip_path}")
