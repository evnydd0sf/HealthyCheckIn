import asyncio
from logging import exception
from os import access
import time
import telegram
from base64 import decode
import requests
import json
from bs4 import BeautifulSoup
import random
import traceback

def check_logic(stuID, stuPass):
    msg = ''

    # 登录
    try:
        cookieUrl = 'https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/login'
        s = requests.Session()
        s.cookies.clear()
        s.get(cookieUrl, headers={'userId': stuID, 'password': stuPass}, timeout=5)

        if s.cookies is None:
            msg = '登录❌'
            return msg
        else: msg = '登录✅'
    except Exception as e:
        msg = '登录❌\n出现错误，请查看错误日志：' + '\n' + str(traceback.format_exc())
        return msg

    # 读取
    try:
        pushUrl = 'https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/webs/yqsb/sjhmcj/index.html'

        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate, br',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,zh-TW;q=0.7',
            'Connection': 'keep-alive',
            'Content-Length': '32',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Cookie': "idSession=" + s.cookies.get("idSession") + ";openId=" + s.cookies.get("openId") + ";route=" + s.cookies.get("route"),
            'Host': 'yqtb.◼︎◼︎◼︎.edu.cn',
            'Origin': 'https://yqtb.◼︎◼︎◼︎.edu.cn',
            'Referer': pushUrl,
            'sec-ch-ua': '"Chromium";v="106", "Google Chrome";v="106", "Not;A=Brand";v="99"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"iOS"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/106.0.0.0 Safari/537.36',
            'X-Requested-With': 'XMLHttpRequest',
        }

        sourceJson = requests.post('https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/dkjl', headers=headers, timeout=5, data={
            'userId': stuID, 'password': stuPass})

        htmlJson = BeautifulSoup(sourceJson.text, "html.parser")
        json_seletc = json.loads(htmlJson.text)

        if json_seletc['json']['data']['xhOrgh'] == '':
            msg = '🪪未知 登录✅ 读取❌'
            return msg
        else: 
            msg = '🪪' + json_seletc['json']['data']['xhOrgh'] + '\n登录✅ 读取✅'
    except Exception as e:
        msg = '🪪未知\n登录✅ 读取❌\n出现错误，请查看错误日志：' + '\n' + str(traceback.format_exc())
        return msg
    
    # 打卡
    try:
        saveData = {
            'xhOrgh': json_seletc['json']['data']['xhOrgh'],
            'tbrq': '',
            'sffyhz': '0',
            'twqk': '1',
            'sfjc': '0',
            'sfdf': '0',
            'szdf': json_seletc['json']['data']['szdf'],
            'sfcqglcs': '0',
            'gldd': '',
            'sfhsjc': '2',
            'hsjcjg': '0',
            'jkmqk': '0',
            'xcmqk': '0',
            'lxdh': json_seletc['json']['data']['lxdh'],
            'qtqk': '',
            'role': '1',
            'jrsfwc': '2',
            'ymjzqk': '3',
            'sffx': '0',
            'sfzgfx': '0',
            'jjrStqk': '0',
        }

        saveData = requests.post(
            'https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/save', headers=headers, timeout=5, data=saveData)
        saveJson = BeautifulSoup(saveData.text, "html.parser")
        save_json_seletc = json.loads(saveJson.text)

        if save_json_seletc['json']['data'] == 'true' and save_json_seletc['json']['status'] == 1 and save_json_seletc['json']['msg'] == '获取数据成功'  and save_json_seletc['json']['code'] == 200:
            msg = '🪪' + json_seletc['json']['data']['xhOrgh'] + '\n登录✅ 读取✅ 打卡✅'
        else: 
            msg = '🪪未知\n登录✅ 读取✅ 打卡❌'
            return msg
    except Exception as e:
        msg = '🪪' + json_seletc['json']['data']['xhOrgh'] + '\n登录✅ 读取✅ 打卡❌\n出现错误，请查看错误日志：' + '\n' + str(traceback.format_exc())
        return msg
    return msg


async def telegramMsg(botToken, message):
    bot = telegram.Bot(botToken)
    try: 
        bot.send_message(text=message, chat_id=395107166)
    except Exception as e:
        print(e)
        bot.send_message(text='出现未知错误，请查看错误日志：\n' + str(traceback.format_exc(), chat_id=395107166))

def check_up(idData):
    finalMessage = ''
    successMessage = 0
    failIndex = []
    failMessage = ''

    for i in idData:
        stuID = i[2]
        stuPass = i[3]

        checkMessage = check_logic(stuID, stuPass, 0)
        
        message = '🎓' + i[1] + ' ' + checkMessage
        if checkMessage == '🪪' + i[2] + '\n登录✅ 读取✅ 打卡✅':
            successMessage += 1
        else:
            failIndex.append(i[0])
            failMessage += i[1] + ' '
        finalMessage += message + '\n\n'
        print(message + '\n')
        time.sleep(random.randint(2,5))

    timeMessage = '打卡结束，时间：' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    if successMessage == len(idData):
        poepleMessage = '共' + str(len(idData)) + '人，成功打卡' + str(successMessage) + '人'
    else:
        poepleMessage = '共' + str(len(idData)) + '人，成功打卡' + str(successMessage) + '人，失败' + str(len(idData) - successMessage) + '人，失败名单：' + failMessage + '，将在5秒内重新打卡。'

    telegramBotMsg = timeMessage + '\n\n' + poepleMessage +'\n\n' + finalMessage
    print(telegramBotMsg)
    asyncio.run(telegramMsg(botToken, telegramBotMsg))
    return failIndex

if __name__ == '__main__':
    botToken = TOKEN
    idData = [
            [1, '用户1', 'M2205◼︎◼︎◼︎', '◼︎◼︎◼︎◼︎◼︎◼︎'],
            [2, '用户2', 'M2205◼︎◼︎◼︎', '◼︎◼︎◼︎◼︎◼︎◼︎'],
            [3, '用户3', 'M2205◼︎◼︎◼︎', '◼︎◼︎◼︎◼︎◼︎◼︎'],
                    ...
            ]

    failIndex = check_up(idData)
    print(failIndex)
    init = 0
    while len(failIndex) != 0:
        init += 1
        time.sleep(5)
        print('第' + str(init) + '次重新打卡，失败名单：' + str(failIndex))
        asyncio.run(telegramMsg(botToken, '第' + str(init) + '次重新打卡'))
        newIdDate = []
        for i in failIndex:
            newIdDate.append(idData[i-1])
        failIndex = (check_up(newIdDate))
        print(failIndex)
        if failIndex != []:
            continue
        if init == 10:
            failMessage = ''
            for i in failIndex:
                failMessage += [idData[i]][1] + ' '
            asyncio.run(telegramMsg(botToken, '🤖️哥们实在顶不住了，已经十次尝试了，这次就不再尝试了，快看看这' + str(len(failIndex)) + '个倒霉哥们到底啥情况吧：' + failMessage))
            break
        elif failIndex == []:
            asyncio.run(telegramMsg(botToken, '🤖️噩梦终于结束了'))
            break