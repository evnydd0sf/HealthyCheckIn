鉴于当前不再需要“每日打卡”，因此我打算将我的思路和方法进行披露，当作一个笔记，以防下一次还有这样类似的需求需要被满足。

> 注意，与之相关的姓名、账号、密码和机构都进行了脱敏处理。
> 

---

# 为什么

在2022年9月末，被要求进行“每日打卡”，来确保一些众所周知的事情不会发生。但是这个“每日打卡”很有意思，它需要在每天十点前完成打卡，但打卡内容只有两类内容，一类是长期不需要被修改的内容，例如姓名、电话、宿舍所在地等等；另一方面又是每天十点前无法预估今天所有行程规划或是未来发生的内容，例如今天的是否需要到达本部、温度、是否流感等等；甚至会有一些匪夷所思的内容，例如是否密接等等。

一方面，固定内容不需要进行每天的更新（虽然这类表单的内容无需每天填入，但每天滑动这类信息才能定位到每天需要手动填写的内容属实恶心，并严重影响效率），另一方面，每天十点并不能把当天的所有信息都完整预估。从另一个角度思考，这样的形式更是无法避免众所周知的事情发生，反倒成为了一种责任分散的挡箭牌。故此，这样的行为无疑是每天都在恶心着我。

目标既然确定，那么便开始分析一下如何让代码替我打卡。

# 确定流程

每天十点未打卡，会有一封短信发来，并附有一串链接：

```python
https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/webs/yqsb/yqsb/xsyqtb-xq.html
```

通过浏览器访问，发现会被跳转至登录界面：

```python
https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/webs/yqsb/sjhmcj/index.html
```

在手动填入账号信息后，进入填报表单界面，在手动填报后完成提交。

那么现在的流程就很明确了：

```python
通过模拟登录获取 Cookie -> 携带 Cookie 尝试进入表单界面 -> 将预设信息填入表单
```

将整个流程进行优化便得到：

```python
每天定时开始 -> 循环账号列表 -> 通过模拟登录获取 Cookie -> 携带 Cookie 尝试进入表单界面 -> 正确获取到账号并匹配成功 -> 将预设信息填入报表 -> 反馈状态为 200 时通过 Telegram Bot 推送打卡成功
```

即相当于创建一种方法，填入账号和密码，内部进行打卡，反馈数据为成果或失败。然后将这个方法循环在一组账号列表中，并累积哪些账号成功，哪些账号失败，然后通过 Telegram Bot 机器人推送，同时代码等待十秒后，将先前未成功的账号再次尝试打卡，直到所有账号打卡成功，或者重复十次后放弃。

首先就是检测登录逻辑中实际的网址是什么，在浏览网页时，往往当前的网址和信息发送与接收不一样，并同时伴随着复杂的 Cookie 和 Header，在这时就需要 Chrome 浏览器去检测整个网络活动，检测实际发送的网址、数据和反馈的内容：

```yaml
Request URL: https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/login
Request Method: POST
Status Code: 200 OK
Remote Address: 127.0.0.1:7890
Referrer Policy: strict-origin-when-cross-origin
```

我们发现：

```python
# 虽然登录网址是：
https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/webs/yqsb/sjhmcj/index.html
# 但实际接收数据的网址是：
https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/login
```

并且使用 Post 方法发送了 Header：

```yaml
Accept: */*
Accept-Encoding: gzip, deflate, br
Accept-Language: zh-CN,zh;q=0.9
Connection: keep-alive
Content-Length: 33
Content-Type: application/x-www-form-urlencoded; charset=UTF-8
Host: yqtb.◼︎◼︎◼︎.edu.cn
Origin: https://yqtb.◼︎◼︎◼︎.edu.cn
Referer: https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/webs/yqsb/sjhmcj/index.html
sec-ch-ua: "Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"
sec-ch-ua-mobile: ?0
sec-ch-ua-platform: "macOS"
Sec-Fetch-Dest: empty
Sec-Fetch-Mode: cors
Sec-Fetch-Site: same-origin
User-Agent: Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Safari/537.36
X-Requested-With: XMLHttpRequest
```

以及两个信息：

```yaml
userId: 
M2205◼︎◼︎◼︎
password: 
◼︎◼︎◼︎◼︎◼︎◼︎◼︎◼︎
```

# 那就登录看看

将其汇总，便确定采用的方法是 Python 中常见的 Request 方法，同时将 stuID 定义为账号，stuPass 定义为密码：

```python
# 登录
    try:
        cookieUrl = 'https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/login' # 定义登录网址
        s = requests.Session() # 定义方法
        s.cookies.clear() # 清理 Cookie 缓存
        s.get(cookieUrl, headers={'userId': stuID, 'password': stuPass}, timeout=5) # 通过登录网址，填入账号和密码，获取五秒内反馈的 Cookie 数据

        if s.cookies is None: # 如果获取的 Cookie 是空的
            msg = '登录❌' # 那么信息为“登录❌”
            return msg # 打断代码并返回信息
        else: msg = '登录✅' # 否则信息为“登录✅”
    except Exception as e: # 如果遇到了意外事件
        msg = '登录❌\n出现错误，请查看错误日志：' + '\n' + str(traceback.format_exc()) # 信息为“登录❌ 出现错误，请查看错误日志：%错误日志%”
        return msg # 打断代码并返回信息
```

# 确定对吗

在这个方法后， s.cookies 就成为了验证表单和填写表单的一把钥匙，接下来，进行表单验证：

```python
# 读取
    try:
        pushUrl = 'https://yqtb.◼︎◼︎◼︎.edu.cn/mp-czzx/webs/yqsb/sjhmcj/index.html' # 定义表单网址

        headers = { # 定义申请标头，同时将上一步中的 s.cookies 嵌入到这一步中
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
            'userId': stuID, 'password': stuPass}) # 登录表单界面

        htmlJson = BeautifulSoup(sourceJson.text, "html.parser") # 解码网页数据
        json_seletc = json.loads(htmlJson.text) # json 化网页数据

        if json_seletc['json']['data']['xhOrgh'] == '': # 如果获取到的表单内容账号为空
            msg = '🪪未知 登录✅ 读取❌' # 返回信息为“🪪未知 登录✅ 读取❌”
            return msg # 打断代码并返回信息
        else: 
            msg = '🪪' + json_seletc['json']['data']['xhOrgh'] + '\n登录✅ 读取✅' # 否则信息为“🪪%账号% 登录✅ 读取✅”
    except Exception as e: # 如果遇到了意外事件
        msg = '🪪未知\n登录✅ 读取❌\n出现错误，请查看错误日志：' + '\n' + str(traceback.format_exc()) # 信息为“🪪未知\n登录✅ 读取❌ 出现错误，请查看错误日志：%错误日志%”
        return msg # 打断代码并返回信息
```

# 不要浪费时间

最终如果最初的账号与网页表单中获取的账号一致，那么就说明当前的表单可以进行推送数据，也就是打卡：

```python
# 打卡
    try:
        saveData = { # 预设打卡内容，其中 xhOrgh 为账号，szdf 为所在地方，lxdh 为 联系电话，这三个数据将上一次的数据进行动态填入
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
            'https://yqtb.nua.edu.cn/mp-czzx/save', headers=headers, timeout=5, data=saveData) # 将以上数据填入到网址中，并在五秒钟内得到反馈状态
        saveJson = BeautifulSoup(saveData.text, "html.parser") # 解码网页数据
        save_json_seletc = json.loads(saveJson.text) # json 化网页数据

        if save_json_seletc['json']['data'] == 'true' and save_json_seletc['json']['status'] == 1 and save_json_seletc['json']['msg'] == '获取数据成功'  and save_json_seletc['json']['code'] == 200:  # 如果反馈的数据中包含“获取数据成功”和“200”
            msg = '🪪' + json_seletc['json']['data']['xhOrgh'] + '\n登录✅ 读取✅ 打卡✅' # 返回信息为“🪪%账号% 登录✅ 读取✅ 打卡✅”
        else: 
            msg = '🪪未知\n登录✅ 读取✅ 打卡❌' # 否则返回数据为“🪪未知 登录✅ 读取✅ 打卡❌”
            return msg # 打断代码并返回信息
    except Exception as e: # 如果遇到了意外事件
        msg = '🪪' + json_seletc['json']['data']['xhOrgh'] + '\n登录✅ 读取✅ 打卡❌\n出现错误，请查看错误日志：' + '\n' + str(traceback.format_exc()) # 信息为“🪪未知\n登录✅ 读取✅ 打卡❌ 出现错误，请查看错误日志：%错误日志%”
        return msg # 打断代码并返回信息
    return msg # 打断代码并返回信息
```

# 终于完成

至此，这个方法便完成，只需要填入账号和密码，便会自动填入预设好的所有信息，同时反馈一个打卡是否成功的信息。

下一步，将这个方法进行包装，循环一个账号列表，并将所有打卡结果汇总到 Telegram Bot 中，来提醒我：

首先将这个方法定义成：

```python
def check_logic(stuID, stuPass):
# 中间的代码 
return msg
```

无论何时，引用这个方法并将 stuID, stuPass 修改为账号和密码都会进行打卡，然后，定义一个账号列表，并将一个账号列表循环在其中：

```python
idData = [
        [1, '用户1', 'M2205◼︎◼︎◼︎', '◼︎◼︎◼︎◼︎◼︎◼︎'],
        [2, '用户2', 'M2205◼︎◼︎◼︎', '◼︎◼︎◼︎◼︎◼︎◼︎'],
        [3, '用户3', 'M2205◼︎◼︎◼︎', '◼︎◼︎◼︎◼︎◼︎◼︎'],
				...
        ]
```

```python
def check_up(idData): # 定义一个方法，将账号列表引入
    finalMessage = '' # 定义一个最终的信息，初始为空
    successMessage = 0 # 定义一个成功打卡的计数，初始为 0
    failIndex = [] # 定义一个错误账号的唯一指示序列
    failMessage = '' # 定义一个最终错误的信息，初始为空

    for i in idData: # 循环 idData 中的数据
        stuID = i[2] # 获取每条数据的第三个数据，即为账号
        stuPass = i[3] # 获取每条数据的第四个数据，即为账号密码

        checkMessage = check_logic(stuID, stuPass) # 将账号和密码引入到刚刚说到的打卡方法中
        
        message = '🎓' + i[1] + ' ' + checkMessage # 定义一个信息为“🎓%姓名% 打卡结果”
        if checkMessage == '🪪' + i[2] + '\n登录✅ 读取✅ 打卡✅': # 如果打卡结果为成功
            successMessage += 1 # 将成功打卡的计数加 1
        else: # 否则
            failIndex.append(i[0]) # 将失败的账号唯一指示序列加入到错误列表中
            failMessage += i[1] + ' ' # 将失败账号的姓名添加到错误信息中
        finalMessage += message + '\n\n' # 最终的信息等于每条信息的累积
        print(message + '\n') # 将信息输出到结果中
        time.sleep(random.randint(2,5)) # 每次完成一个账号后，暂停 2～5 秒

    timeMessage = '打卡结束，时间：' + time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) # 记录每一次打卡的东八区时间
    if successMessage == len(idData): # 如果所有人都打卡成功
        poepleMessage = '共' + str(len(idData)) + '人，成功打卡' + str(successMessage) + '人' # 返回所有人都打卡成功的列表
    else:
        poepleMessage = '共' + str(len(idData)) + '人，成功打卡' + str(successMessage) + '人，失败' + str(len(idData) - successMessage) + '人，失败名单：' + failMessage + '，将在5秒内重新打卡。' # 返回打卡成功和打卡失败的列表

    telegramBotMsg = timeMessage + '\n\n' + poepleMessage +'\n\n' + finalMessage # 汇总 Telegram Bot 中所有需要反馈的信息
    print(telegramBotMsg) # 输出 Telegram Bot 输出的信息
    asyncio.run(telegramMsg(botToken, telegramBotMsg)) # 
    return failIndex # 返回打卡失败
```

于是，这个功能便基本完成，他将按照我预设的账号列表，将每一个账号进行打卡，并在其间隔 2～5 秒后再进行下一个，并在循环结束后通过 Telegram Bot 通知我。

# 最后一颗螺丝

不过在中期账号列表增多后，偶尔会发生某一个账号打卡失败的情况，这里，就需要将代码升级一下，通过自动检测，来循环错误的账号，直到打卡成功。

```python
failIndex = check_up(idData) # 引入错误列表
    print(failIndex) # 输出错误列表
    init = 0 # 定义一个初始值 0
    while len(failIndex) != 0: # 当错误列表的计数不为0，也就是还有打卡错误的账号时
        init += 1 # 初始值累积加 1
        time.sleep(5) # 等待 5 秒
        print('第' + str(init) + '次重新打卡，失败名单：' + str(failIndex)) # 输出信息，记录这是第几次进行重复打卡
        asyncio.run(telegramMsg(botToken, '第' + str(init) + '次重新打卡')) # 通过 Telegram Bot 输出这是第几次进行打卡
        newIdDate = [] # 创建下一次错误打卡的账号列表
        for i in failIndex: # 循环上一次的错误列表
            newIdDate.append(idData[i-1]) # 将上一次错误的账号列表添加这个列表中
        failIndex = (check_up(newIdDate)) # 获取这一次打卡失败的账号
        print(failIndex) # 输出信息
        if failIndex != []: # 如果错误列表不等于空
            continue # 那就继续循环
        if init == 10: # 如果重复计数累积到 10 次
            failMessage = '' # 定义错误信息
            for i in failIndex: # 循环错误账号的列表
                failMessage += [idData[i]][1] + ' ' # 定义错误账号的姓名
            asyncio.run(telegramMsg(botToken, '🤖️哥们实在顶不住了，已经十次尝试了，这次就不再尝试了，快看看这' + str(len(failIndex)) + '个倒霉哥们到底啥情况吧：' + failMessage)) # 返回错误信息
            break # 停止代码
        elif failIndex == []: # 如果错误代码为空
            asyncio.run(telegramMsg(botToken, '🤖️噩梦终于结束了')) # 返回数据
            break # 停止代码
```

那么到这一步，整个代码也就完整了，最终我上传至远端服务器中，并设置了每天早晨 07:05 分自动执行代码，于是我便高枕无忧了。

这算是我最近一次可以披露的代码实例，并可以实际感受到这个代码带来的效益。不过有关这个这个代码的道德问题，我认为对于我来说则完全不是问题，毕竟提升低效率形式最好的武器就是让机器替我干活。

# 最后

代码目前已在 GitHub 上开源：https://github.com/evnydd0sf/HealthyCheckIn，并且与之相关的姓名、账号、密码和机构都进行了脱敏处理。

有任何交流或疑问可以在 Telegram 联系我：https://t.me/evnydd0sf

Peace！