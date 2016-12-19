#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
import json
import sys
from httpRequest import httpRequest

class train:

    username = ''
    password = ''
    name12306 = ''
    password12306 = ''
    userToken = u''
    userid = 0
    expiretime = 0
    loginCapchat = ''
    fromstation = ''
    fromStationSign = ''
    tostation = ''
    toStationSign = ''
    date = ''
    codes = ''
    passengername = ''
    host = u'https://train.lvzhisha.com'
    cacheFilename = 'tokencache'
    email = ''

    def __init__(self):
        #初始化配置
        self.__initConfig()

    def register(self):
        #注册账号中
        print u'账号注册中.....\n'
        formData = {'username':self.username,'password':self.password,'nickname':self.username}
        url = self.host + u'/register'
        response = httpRequest().url(url).parameters(formData).post()
        response = self.__jsonDecode(response)
        if response[u'status_code'] == 1:
            print u'账号注册成功\n'
            return True
        else:
            print u'账号注册失败\n' + response[u'status_msg']
            return False

    def __queryOrderTicket(self,date,fromStation,toStation):
        queryData = {
            'date' : date,
            'from' : fromStation,
            'to'   : toStation
        }
        httpUrl = self.host + u'/train/leftTickets'
        response = httpRequest().url(httpUrl).header(self.__getHeaders()).parameters(queryData).get()
        response = self.__jsonDecode(response)
        return response[u'list'] if response != False and response[u'status_code'] == 1 else False

    #下单购票
    def __createOrder(self, date, fromStation, toStation, secret):
        formData = {
            'train_date'      : date,
            'from_station'    : fromStation,
            'back_train_date' : date,
            'to_station'      : toStation,
            'secret'          : secret
        }
        httpUrl = self.host + u'/train/order/ticket'
        response = httpRequest().url(httpUrl).header(self.__getHeaders()).parameters(formData).post()
        response = self.__jsonDecode(response)
        return response if response[u'status_code'] == 1 else False

    #检测订单
    def __checkOrder(self,code):
        formData = {
            'passengCodes' : code,
            'randCode'     : '144,24'
        }
        httpUrl = self.host + u'/train/order/check'
        response = httpRequest().url(httpUrl).header(self.__getHeaders()).parameters(formData).post()
        response = self.__jsonDecode(response)
        rdata = { 
            'status' : True if response[u'status_code'] == 1 else False,
            'msg'    : response[u'status_msg']
        }
        return rdata

    #确认下单
    def __submitOrder(self,code):
        formData = {
            'passengCodes' : code,
            'randCode'     : '144,24'
        }
        httpUrl = self.host + u'/train/order/confirmOrder'
        response = httpRequest().url(httpUrl).header(self.__getHeaders()).parameters(formData).post()
        response = self.__jsonDecode(response)
        return True if response[u'status_code'] == 1 else False

    #缓存过期删除
    def __deleteCacheToken(self):
        fp = open(self.cacheFilename,'w+')
        fp.write('')
        fp.close()

    #解析json
    def __jsonDecode(self,jsonStr):
        try:
            response = json.loads(jsonStr)
            if response[u'status_code'] != 1 and (response[u'status_code'] == 100 or response[u'status_code'] == u'100' or response[u'status_code'] == '100'):
                self.__deleteCacheToken()
                raise NameError('aa')
        except NameError,msg:
            sys.exit(u'登录token过期，请重新执行脚本')
        except:
            return {u'status_code':u'0'}
        else:
            return response
        
    #设置token
    def setUserToken(self, token, userid, expiretime): 
        self.userToken = token
        self.userid = userid
        self.expiretime = expiretime

    #获取token
    def __getUserToken(self):
        #print u'检测用户状态\n'
        if self.userToken != u'' or self.userToken != '':
            return self.userToken
        #获取缓存token
        token = self.__getCacheToken()
        if token != False:
            self.setUserToken(token[0], token[2], token[1])
            print u'用户已登录\n'
            return token[0]
        #无token去登录
        token = self.__login()
        if token['status'] == False:
            if token['code'] == -102:
                #自动注册
                regResult = self.register()
                if regResult == False:
                    sys.exit(u'请重新填写配置文件\n')
                #重新登录
                token = self.__login()
                if token['status'] == False:
                    sys.exit()
            else:
                sys.exit()
        self.setUserToken(token['token'], token['userid'], token['expire_time'])
        tokenList = [token['token'].encode("utf-8"),str(token['expire_time']),str(token['userid'])]
        self.__cacheToken(tokenList)
        return token['token']

    #写缓存
    def __cacheToken(self,tokenList):
        tokenStr = '\n'.join(tokenList)
        fp = open(self.cacheFilename,'w+')
        fp.write(tokenStr)
        fp.close()

    def __getCacheToken(self):
        try:
            fp = open(self.cacheFilename,'r')
            tokenStr = fp.read()
            fp.close()
            if '' == tokenStr:
                return False
            tokenList = tokenStr.split('\n')
            return tokenList
        except:
            return False
    
    #headers
    def __getHeaders(self):
        headers = [u'userToken: ' + self.__getUserToken()]
        return headers

    #检测登录验证码
    def __checkCapchat(self):
        print u'\n正在校验验登录验证码...\n'
        formData = {
            'randCode' : self.loginCapchat
        }
        httpUrl = self.host + u'/train/checkCapchat/login'
        response = httpRequest().url(httpUrl).header(self.__getHeaders()).parameters(formData).get()
        response = self.__jsonDecode(response)
        if response[u'status_code'] == 1:
            print u'登录验证码校验通过\n'
            return  True
        print u'登录验证码不正确\n'
        return False 
    
    #生成验证码图片链接
    def __capchatUrlFor12306(self):
        print u'↓↓↓↓↓↓↓↓↓↓↓请在浏览器打开以下链接生成验证码↓↓↓↓↓↓↓↓↓↓↓↓\n'
        print self.host + u'/train/%d/capchat/login\n' % (int(self.userid))
        print u'↑↑↑↑↑↑↑↑↑↑↑请在浏览中打开上面链接以获得验证码坐标↑↑↑↑↑↑\n'
    
    #获取输入的验证码坐标
    def getCapchatCoordinate(self):
        #ds = raw_input('请输入验证码坐标：').decode(sys.stdin.encoding)
        print u'↓↓↓↓↓↓↓↓↓↓↓请输入验证码坐标↓↓↓↓↓↓↓↓↓↓↓\n'
        ds = raw_input('capchat is : ')
        self.loginCapchat = ds

    #生成cookie
    def __createCookie(self):
        print u'正在生成cookie...\n'
        httpUrl = self.host + u'/train/cookie'
        response = httpRequest().url(httpUrl).header(self.__getHeaders()).post()
        response = self.__jsonDecode(response)
        if response[u'status_code'] == 1:
            print u'生成身份cookie完毕\n'
            return  True
        return False

    #检测用在12306是否登录
    def __checkLoginFor12306(self):
        print u'检测12306账户登录状态....\n'
        httpUrl = self.host + u'/train/loginStatus'
        response = httpRequest().url(httpUrl).header(self.__getHeaders()).get()
        response = self.__jsonDecode(response)
        if response[u'status_code'] == 1 and response[u'data'][u'status']:
            print u'12306账户已经登录\n'
            return  True
        print u'12306账户还未登录\n'
        return False 

    #12306登录
    def __loginFor12306(self):
        print '登录12306...\n'
        formData = {
            'username' : self.username12306,
            'password' : self.password12306,
            'randCode' : self.loginCapchat
        }
        httpUrl = self.host + u'/train/login'
        response = httpRequest().url(httpUrl).header(self.__getHeaders()).parameters(formData).post()
        response = self.__jsonDecode(response)
        if response[u'status_code'] == 1:
            print u'登录12306完毕\n'
            return  True
        print u'登录12306失败\n'
        return False 

    #登录
    def __login(self):
        print u'登录中...\n'
        formData = {
            'username' : self.username,
            'password' : self.password
        }
        httpUrl = self.host + u'/login'
        response = httpRequest().url(httpUrl).parameters(formData).post()
        response = self.__jsonDecode(response)
        rdata = {
                'status' : True if response[u'status_code'] == 1 else False,
                'code'   : response[u'status_code'],
                'token'  : response[u'data'][u'token'] if response[u'status_code'] == 1 else u'',
                'userid' : response[u'data'][u'userid'] if response[u'status_code'] == 1 else u'0',
                'expire_time' : response[u'data'][u'expire_time'] if response[u'status_code'] == 1 else u'0'
        }
        if response[u'status_code'] == 1:
            print u'登录完毕\n'
            return  rdata
        print u'登录失败，原因：' + response[u'status_msg'] + u'\n'
        return  rdata

    #抢票
    def go(self):
        #登录账号
        token = self.__getUserToken()
        if token == '':
            sys.exit()
        loginStatus = self.__checkLoginFor12306()
        if loginStatus == False:
            #生成cookie
            self.__createCookie()
            #生成验证码
            self.__capchatUrlFor12306()
            capchatStatus = False
            while(capchatStatus == False):
                #获取验证码坐标
                self.getCapchatCoordinate()
                #验证验证码
                capchatStatus = self.__checkCapchat()
            #12306登录
            self.__loginFor12306()
        #选择乘客
        self.__selectPassenger()
        date = self.date 
        planFrom = self.fromStationSign
        planTo = self.toStationSign
        num = 1
        while(num):
            print u'====================第' + str(num) + u'次尝试抢票=======================\n'
            print u'出发日期：' + unicode(date,'utf-8') + u' 乘车人：' + unicode(self.passengername,'utf-8') + u' 起始站：' + unicode(self.fromstation,'utf-8') + u' <--> 终点站：' + unicode(self.tostation,'utf-8') + u'\n'
            num += 1
            tickets = self.__queryOrderTicket(date,planFrom,planTo)
            if tickets == False:
                print u'未能查询到余票' + '\n'
                continue
            for item in tickets:
                t = item['queryLeftNewDTO']
                seatNum = {
                        'zy_num':[t[u'zy_num'],u'一等座'],
                        'ze_num':[t[u'ze_num'],u'二等座'],
                        'wz_num':[t[u'wz_num'],u'无座']
                        }
                for seat in seatNum:
                    if seatNum[seat][0] == u'有' or seatNum[seat][0].isdigit():
                        print u'查询到车票，车次为：' + t[u'station_train_code'] + u' ' + seatNum[seat][1] + u' 出发时间：' + t[u'start_time'] + u' 到站时间：' + t[u'arrive_time'] + u'\n'
                        print u'正在努力下单中...\n'
                        #有票下单
                        orderResult = self.__createOrder(date,planFrom,planTo,item[u'secretStr'])
                        if orderResult == False:
                            print u'很遗憾提交订单失败了0.0\n'
                            continue
                        print u'提交订单成功，进入订单验证....\n' 
                        #检测订单状态
                        checkResult = self.__checkOrder(self.codes)
                        #print checkResult
                        if checkResult['status'] == False:
                            print u'很遗憾订单验证失败了,原因：' + checkResult['msg'] + u'\n'
                            continue
                        print u'最后一步了，正在努力完成订单....\n'
                        #提交购票订单
                        submitResult = self.__submitOrder(self.codes)
                        #print submitResult
                        if submitResult:
                            #发送邮件
                            print u'恭喜你，抢到票了，快去付钱吧!!!!\n'
                            self.__sendEmail()
                            sys.exit()
                        else:
                            print u'很遗憾，未能完成订单\n'

    #初始化配置
    def __initConfig(self):
        filename = 'config'
        fp = open(filename,'r')
        configStr = fp.read()
        fp.close()
        configList = configStr.split('\n')
        print u'\n初始化配置中...\n'
        rulesObject = {
            'username'      : u'username不合法，请完善配置文件',
            'password'      : u'password不合法，请完善配置文件',
            'username12306' : u'username12306不能为空，请完善配置文件',
            'password12306' : u'password12306不能为空，请完善配置文件',
            'fromstation'   : u'fromstation不能为空，请完善配置文件',
            'tostation'     : u'tostation不能为空，请完善配置文件',
            'date'          : u'date格式不合格，请完善配置文件',
            'codes'         : u'',
            'passengername' : u'',
            'email'         : ''
        }
        for config in configList:
            itemList = config.split('=')
            if rulesObject.has_key(itemList[0]):
                setattr(self, itemList[0], itemList[1])

        #检测配置
        self.__checkConfig(rulesObject)
        print u'读取配置完毕\n'

    #检测配置项是否满足
    def __checkConfig(self,rules):
        notCheckList = ['codes','passengername','email']
        for attr in rules:
            attrValue = getattr(self,attr)
            if attrValue == '' and attr not in notCheckList:
                sys.exit(rules[attr])
            if (attr == 'username' and len(attrValue) < 6) or (attr == 'password' and len(attrValue) < 8):
                sys.exit(rules[attr])
            if attr == 'date':
                result = self.__isValidDate(attrValue)
                if result == False:
                    sys.exit(rules[attr])

        self.__decodeStation()

    #判断是否是一个有效的日期字符串
    def __isValidDate(self,dateStr):
        try:
            time.strptime(dateStr, "%Y-%m-%d")
            return True
        except:
            return False

    #解析站点
    def __decodeStation(self):
        print u'正在解析站点...\n'
        filename = 'stations'
        fp = open(filename,'r')
        stationsStr = fp.read()
        stationsList = stationsStr.split('@')
        fromStationList = []
        toStationList = []
        for item in stationsList:
            if self.fromstation in item:
                fromStationList.append(item)
            if self.tostation in item:
                toStationList.append(item)
        lenFrom = len(fromStationList)
        lenTo = len(toStationList)
        if  lenTo < 1 or lenFrom < 1:
            print u'站点解析出错，请重新配置站点\n'
        self.__stationSelect(fromStationList,0)
        self.__stationSelect(toStationList,1)
    
    #站点选择
    def __stationSelect(self, stationList, stationType):
        stationLen = len(stationList)
        stationTypeNames = [u'出发',u'到站']
        if stationLen == 1:
            item = stationList[0].split('|')
            if stationType == 1:
                self.toStationSign = item[2]
                self.tostation = item[1] 
            else:
                self.fromStationSign = item[2]
                self.fromstation = item[1]
            print stationTypeNames[stationType] + u'站点解析完成: ' + unicode(item[1],"utf-8") + u' 代号为：' + unicode(item[2],"utf-8") + '\n'
        else:
            print stationTypeNames[stationType] + u'站点匹配结果较多，请输入序号选择\n'
            key = 0
            for item in stationList:
                key += 1
                print u'%d 、%s' % (key,unicode(item.split('|')[1],'utf-8'))
            while(True):
                print u'\n↓↓↓↓↓↓↓↓↓↓↓请输入序号选择' + stationTypeNames[stationType] + u'站点↓↓↓↓↓↓↓↓↓↓↓\n'
                number = raw_input('serial number is : ')
                if number.isdigit() == False:
                    print u'\n请输入数字!!!\n'
                    continue
                number = int(number)
                if number >= 1 and number <= key:
                    break
                print u'\n请输入正确的序号!!!\n'
            selectItem = stationList[number-1].split('|')
            if stationType == 1:
                self.toStationSign = selectItem[2]
                self.tostation = selectItem[1] 
            else:
                self.fromStationSign = selectItem[2]
                self.fromstation = selectItem[1]
            print u'\n' + stationTypeNames[stationType] + u'站点解析完成: ' + unicode(selectItem[1],"utf-8") + u' 代号为：' + unicode(selectItem[2],"utf-8") + u'\n'

    #获取乘客列表
    def __getPassengers(self):
        print u'正在读取乘客列表.....\n'
        httpUrl = self.host + u'/train/passengers'
        response = httpRequest().url(httpUrl).header(self.__getHeaders()).get()
        response = self.__jsonDecode(response)
        if response[u'status_code'] == 1:
            print u'乘客列表读取完成\n'
            return  response[u'list']
        print u'乘客列表读取失败\n'
        return False

    #选择乘车人
    def __selectPassenger(self):
        if self.codes != '':
            return True
        passengers = self.__getPassengers()
        if passengers == False:
            sys.exit()
        key = 0
        for item in passengers:
            key += 1
            print u'%d  、%s' % (key,item[u'passenger_name']) 
        while(True):
            print (u'\n↓↓↓↓↓↓↓↓↓↓↓请输入序号选择乘车人↓↓↓↓↓↓↓↓↓↓↓\n')
            number = raw_input('serial number is : ')
            if number.isdigit() == False:
                print u'\n请输入数字!!!\n'
                continue
            number = int(number)
            if number >= 1 and number <= key:
                break
            print u'\n请输入正确的序号!!!\n'
        print u'\n乘客选择完毕，乘车人为：' + passengers[number-1][u'passenger_name'] + u'\n'
        
        #写入文件
        filename = 'config'
        fp = open(filename,'r')
        configStr = fp.read()
        fp.close()
        configList = configStr.split('\n')
        for config in configList[:]:
            #找到乘车人并覆盖
            if 'passengername=' in config or 'codes=' in config or config == '':
                configList.remove(config)
            
        #写入选择的乘车人
        codes = passengers[number-1][u'code'].encode("utf-8")
        passengername = passengers[number-1][u'passenger_name'].encode("utf-8")
        self.codes = codes
        self.passengername = passengername
        configList.append('codes=' + codes)
        configList.append('passengername=' + passengername) 
        configStr = '\n'.join(configList)
        fp = open(filename,'w+')
        fp.write(configStr)
        fp.close()

    #订票成功发送邮件
    def __sendEmail(self):
        if self.email == '':
            return False
        print (u'通知邮件发送中....\n')
        content = '已成功抢到 ' + self.date + ' 从 ' + self.fromstation + ' 开往 ' + self.tostation + '的车票,赶快去付款吧!' 
        formData = {
            'email'   : self.email,
            'content' : content
        }
        httpUrl = self.host + u'/train/email'
        response = httpRequest().url(httpUrl).header(self.__getHeaders()).parameters(formData).post()
        response = self.__jsonDecode(response)
        if response != False and response[u'status_code'] == 1:
            print u'通知邮件发送成功,注意查收\n'
            return True
        else:
            print u'通知邮件发送失败\n'
            return False


train = train()
train.go()

