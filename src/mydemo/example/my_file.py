from pathlib import Path

IMAGE_EXTENSIONS = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
VIDEO_EXTENSIONS = {'.mp4', '.avi', '.mov', '.mkv', '.flv', '.wmv', '.webm', '.m4v'}

def scan_directory_pathlib(root_dir):
    root = Path(root_dir)
    if not root.exists():
        print(f"❌ 目录不存在: {root_dir}")
        return

    all_files = []
    image_files = []
    video_files = []

    # rglob('*') 递归遍历所有文件（不包括目录）
    for file_path in root.rglob('*'):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            filename = file_path.name
            full_path = str(file_path.resolve())  # 绝对路径

            all_files.append((filename, full_path))

            if ext in IMAGE_EXTENSIONS:
                image_files.append((filename, full_path))
            elif ext in VIDEO_EXTENSIONS:
                video_files.append((filename, full_path))

    # 打印结果
    print("=== 所有文件 ===")
    for name, path in all_files:
        print(f"文件名: {name} | 路径: {path}")

    print("\n=== 图片文件 ===")
    for name, path in image_files:
        print(f"图片: {name} | 路径: {path}")

    print("\n=== 视频文件 ===")
    for name, path in video_files:
        print(f"视频: {name} | 路径: {path}")


def walk_with_pathlib(root: Path, indent=0):
    """
    递归遍历目录，按层级打印文件夹和文件
    """
    if not root.exists():
        print(f"❌ 路径不存在: {root}")
        return [], [], []

    all_files = []
    image_files = []
    video_files = []

    # 打印当前文件夹（缩进表示层级）
    print("  " * indent + f"📁 {root.name}/")

    # 获取当前目录下的所有条目
    try:
        entries = sorted(root.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
    except PermissionError:
        print("  " * indent + "⚠️ 无权限访问")
        return [], [], []

    # 先处理文件，再处理文件夹（或反之，按需调整）
    files = [e for e in entries if e.is_file()]
    dirs = [e for e in entries if e.is_dir()]

    # 先处理文件
    for file_path in files:
        filename = file_path.name
        full_path = str(file_path.resolve())
        ext = file_path.suffix.lower()

        all_files.append((filename, full_path))

        # 分类
        if ext in IMAGE_EXTENSIONS:
            image_files.append((filename, full_path))
            print("  " * (indent + 1) + f"🖼️  {filename} (图片) - {file_path.stem}")
        elif ext in VIDEO_EXTENSIONS:
            video_files.append((filename, full_path))
            print("  " * (indent + 1) + f"🎥 {filename} (视频) - {file_path.stem}")
        else:
            print("  " * (indent + 1) + f"📄 {filename}")

    # 在递归处理子目录
    for dir_path in dirs:
        print(f"🔍 开始遍历子目录: {dir_path.name}\n")
        sub_all, sub_img, sub_vid = walk_with_pathlib(dir_path, indent + 1)
        all_files.extend(sub_all)
        image_files.extend(sub_img)
        video_files.extend(sub_vid)

    return all_files, image_files, video_files


def scan_by_folder_structure(root_dir: str):
    root = Path(root_dir).resolve()
    print(f"🔍 开始遍历目录: {root}\n")

    all_files, image_files, video_files = walk_with_pathlib(root)

    # 最后汇总统计（可选）
    print("="*60)
    print(f"📊 总计: {len(all_files)} 个文件")
    print(f"🖼️  图片: {len(image_files)} 个")
    print(f"🎥 视频: {len(video_files)} 个")

    return all_files, image_files, video_files


# 使用示例
if __name__ == "__main__":
    # scan_directory_pathlib("/Users/jiaxiaopeng/Downloads/我的壁纸")  # 替换为你的目录路径
    scan_by_folder_structure("/Users/jiaxiaopeng/Downloads/我的壁纸")