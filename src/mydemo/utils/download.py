

def save_bytes(save_path: str, body: bytes):
    if body is None:
        print(f"⚠️ body不存在，跳过保存。")
        return
    if save_path is None:
        print(f"⚠️ save_path不存在，跳过保存。")
        return
    with open(save_path, "wb") as f:
        f.write(body)
        print(f"✅ 文件已保存: {save_path}")



