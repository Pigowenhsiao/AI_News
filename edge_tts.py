#!/usr/bin/env python3
"""
GUI 版：選擇 .txt 檔後，自動轉成台灣中文 MP3
執行: python txt2twtts_gui.py
"""
import asyncio, pathlib, tkinter as tk
from tkinter import filedialog as fd
import edge_tts                             # pip install edge-tts

DEFAULT_VOICE = "zh-TW-YunJheNeural"        # 雲哲（男），可改 HsiaoChen/HsiaoYu

async def run_tts(txt_path: pathlib.Path,
                  out_path: pathlib.Path,
                  voice: str = DEFAULT_VOICE) -> None:
    """讀取文字並呼叫 edge-tts 產生 MP3"""
    text = txt_path.read_text(encoding="utf-8")
    communicate = edge_tts.Communicate(text, voice)   # 官方 API :contentReference[oaicite:2]{index=2}
    await communicate.save(out_path)                  # 一步輸出 mp3

def main() -> None:
    # 建立隱藏的 Tk 介面，僅用於呼叫檔案選擇器
    root = tk.Tk()
    root.withdraw()                                  # 隱藏主視窗 :contentReference[oaicite:3]{index=3}

    # 只允許選 *.txt
    file_path = fd.askopenfilename(
        title="選擇文字檔",
        filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
    )                                                # 檔案對話框 :contentReference[oaicite:4]{index=4}

    if not file_path:                                # 使用者取消
        print("⚠️  未選取檔案，已中止。")
        return

    in_file = pathlib.Path(file_path)
    out_file = in_file.with_suffix(".mp3")           # 同名 .mp3

    # 非同步執行 TTS
    asyncio.run(run_tts(in_file, out_file))
    print(f"✅  已輸出 {out_file}")

if __name__ == "__main__":
    main()
