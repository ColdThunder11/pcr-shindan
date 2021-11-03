import os
import traceback
from os import path
from hoshino import Service
from playwright.async_api import async_playwright


sv = Service('PCR女友')

cache_path = path.join(path.abspath(path.dirname(__file__)),"cache")

if not path.exists(cache_path):
    os.mkdir(cache_path)

@sv.on_fullmatch(('PCR女友','pcr女友'))
async def get_pcr_shindan(bot,ev):
    await bot.send(ev,f"正在生成中，请稍后")
    if "card" in ev.sender.keys() and ev.sender["card"] != '':
        user_name = ev.sender["card"] 
    else:
        user_name = ev.sender["nickname"] 
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context(viewport={"width":720, "height":1080})
            page = await context.new_page()
            await page.goto("https://shindan.priconne-redive.jp/")
            await page.click("input[type=\"text\"]")
            await page.fill("input[type=\"text\"]",user_name)
            await page.click("button")
            await page.wait_for_load_state("networkidle")
            div =  await page.wait_for_selector("#app > main > div > div > div")
            tweet = await page.wait_for_selector("#app > main > div > div > div > p > a > span.tweet-btn__on.s-sm-min > img")
            divbound = await div.bounding_box()
            tweetbound = await tweet.bounding_box()
            divbound["height"] = tweetbound["y"] - divbound["y"]
            div = await div.bounding_box()
            img = await page.screenshot(clip=divbound,path=path.join(cache_path,f"{user_name}.png"),full_page=True)
            await page.close()
            await context.close()
            await browser.close()
            img_path = path.join(cache_path,f"{user_name}.png")
    except:
        await bot.send(ev,f"图片生成失败了")
        traceback.print_exc()
        return
    await bot.send(ev,f"[CQ:image,file=file:///{img_path}]")
