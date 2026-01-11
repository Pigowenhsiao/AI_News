#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime


async def test_crawl4ai():
    print(f"=== Crawl4AI 測試 ===")
    print(f"開始時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()

    urls = [
        "https://www.cnbc.com/2026/01/09/heres-whats-happening-now-with-mortgage-rates-.html",
        "https://www.cnbc.com/2026/01/09/trump-greenland-military-denmark-nato.html",
    ]

    success_count = 0
    fail_count = 0

    for i, url in enumerate(urls, 1):
        print(f"[測試 {i}/{len(urls)}] URL: {url}")
        try:
            from crawl4ai import AsyncWebCrawler

            async with AsyncWebCrawler(verbose=False) as crawler:
                result = await crawler.arun(url=url)
                print(
                    f"  狀態: {'✅ 成功' if hasattr(result, 'success') and result.success else '❌ 失敗'}"
                )

                if result and result.markdown:
                    print(f"  Markdown 長度: {len(result.markdown)} 字符")
                    if len(result.markdown) >= 250:
                        print(f"  ✅ 內容長度足夠 (>= 250 字符)")
                        preview = result.markdown[:100].replace("\n", " ")
                        print(f"  內容預覽: {preview}...")
                        success_count += 1
                    else:
                        print(f"  ⚠️ 內容較短 (僅 {len(result.markdown)} 字符)")
                        fail_count += 1
                else:
                    print(f"  ❌ Markdown 為空")
                    fail_count += 1
        except ImportError as e:
            print(f"  ❌ 模組未安裝: {e}")
            print(f"  提示: 請執行 'pip install crawl4ai'")
            fail_count += 1
        except Exception as e:
            print(f"  ❌ 錯誤: {e}")
            fail_count += 1
        print()

    print(f"=== 測試結果 ===")
    print(f"成功: {success_count}")
    print(f"失敗: {fail_count}")
    if len(urls) > 0:
        print(f"成功率: {success_count / len(urls) * 100:.1f}%")
    print(f"結束時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(test_crawl4ai())
