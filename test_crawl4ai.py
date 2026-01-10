#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import asyncio
from datetime import datetime


async def test_crawl4ai():
    print(f"=== Crawl4AI 測試 ===")
    print(f"開始時間: {datetime.now().strftime('%H:%M:%S')}")

    urls = [
        "https://www.cnbc.com/2026/01/09/heres-whats-happening-now-with-mortgage-rates-.html",
        "https://www.cnbc.com/2026/01/09/trump-greenland-military-denmark-nato.html",
    ]

    for i, url in enumerate(urls, 1):
        print(f"\n[測試 {i}/2] URL: {url}")
        try:
            from crawl4ai import AsyncWebCrawler

            async with AsyncWebCrawler(verbose=True) as crawler:
                result = await crawler.arun(url=url)
                print(
                    f"  成功: {result.success if hasattr(result, 'success') else 'N/A'}"
                )

                if result and result.markdown:
                    print(f"  Markdown 長度: {len(result.markdown)} 字符")
                    if len(result.markdown) >= 250:
                        print(f"  ✅ 內容長度足夠 (>= 250 字符)")
                        preview = result.markdown[:100].replace("\n", " ")
                        print(f"  內容預覽: {preview}...")
                    else:
                        print(f"  ⚠️ 內容較短 (僅 {len(result.markdown)} 字符)")
                else:
                    print(f"  ❌ Markdown 為空")
        except Exception as e:
            print(f" ❌ 錯誤: {e}")

    print(f"\n結束時間: {datetime.now().strftime('%H:%M:%S')}")


if __name__ == "__main__":
    asyncio.run(test_crawl4ai())
