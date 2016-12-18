#!/usr/bin/env python
# -*- coding: utf-8 -*-

import pycurl
from urllib import urlencode
import StringIO
import json

class httpRequest:
    
    timeout = 300
    connecttimeout = 60
    curl = None
    cache = None
    paramsStr = ''
    url = ''

    def __init__(self):
        self.curl = pycurl.Curl()
        self.cache = StringIO.StringIO()
        # c.setopt(pycurl.FOLLOWLOCATION, 1) #参数有1、2
        # c.setopt(pycurl.MAXREDIRS, 5)
        self.curl.setopt(pycurl.WRITEFUNCTION, self.cache.write)
        self.curl.setopt(pycurl.CONNECTTIMEOUT, self.connecttimeout)
        self.curl.setopt(pycurl.TIMEOUT, self.timeout)
        self.curl.setopt(pycurl.HEADER, False)

    #post
    def post(self):
        if self.paramsStr != '':
            self.curl.setopt(self.curl.POSTFIELDS, self.paramsStr)
        response = self.__request('POST')
        return response
    
    #get
    def get(self):
        if self.paramsStr != '':
            self.url = self.url + self.paramsStr if '?' in self.url else self.url + '?' + self.paramsStr
        response = self.__request('GET')
        return response

    #header
    def header(self,headers):
        self.curl.setopt(self.curl.HTTPHEADER, headers)
        return self
    
    #url
    def url(self,url):
        self.url = url
        return self

    #formData
    def parameters(self,data):
        self.paramsStr = urlencode(data)  
        return self

    # userAgent
    def userAgent(self, userAgentStr):
        self.curl.setopt(pycurl.USERAGENT, userAgentStr)
        return self

    #request
    def __request(self, method):
        #执行上述访问网址的操作
        self.curl.setopt(self.curl.CUSTOMREQUEST, method)
        self.curl.setopt(pycurl.URL, self.url) 
        self.curl.perform() 
        response = self.cache.getvalue()
        return response
