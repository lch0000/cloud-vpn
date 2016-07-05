#!/usr/bin/env python
# -*- coding: utf-8 -*-
# LCH @ 2016-06-17 11:14:18
'''
本脚本用于在国内的云服务器上运行云梯服务,并使用squid进行代理
1/自动连接可用VPN
2/调用脚本修改路由表,国内的流量走原有线路
3/断线重连,每过5小时换代理重连,防止因长时间链接被封
'''
import os
import time
from commands import getoutput, getstatusoutput

VPNS = ['hk1', 'hk2', 'tw1', 'us3', 'us6', 'jp1', 'sg1', 'uk1'] # vpn列表
BASEDIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
link_start_time = 0
link_vpn = 'jp1' # 初始设定一个不常用的vpn作为备选
username = '******' # vpn用户名
password = '******' # vpn密码

def linkstatus():
    '''检测本机当前是否存在ppp0的网卡'''
    return 'ppp0' in getoutput('ifconfig -s')

def up_routes():
    '''修改到vpn连接状态'''
    up_file = BASEDIR + '/ip-up'
    getoutput('bash %s' %up_file)

def down_routes():
    '''恢复原始路由表'''
    down_file = BASEDIR + '/ip-down'
    getoutput('bash %s' %down_file)

def connect_vpn(vpns):
    '''连接vpn'''
    global link_vpn
    for vpntag in vpns:
        if vpntag == link_vpn:
            continue
        print '尝试连接到%s 时间%s' % (vpntag, time.ctime())
        getoutput('killall pppd')
        result = getoutput('pptpsetup --create vpn --server p1.%s.faxgood.com --username %s --password %s --encrypt --start' %(vpntag, username, password)) # 需要跟据vpn提供商的服务器修改'p1.%s.faxgood.com'部分
        if 'local' in result and 'remote' in result:
            link_start_time = int(time.time())
            link_vpn = vpntag
            print 'vpn连接到%s 时间%s' % (link_vpn, time.ctime())
            break

def disconnect_vpn():
    '''断开vpn链接'''
    getoutput('killall pppd')

def restart_squid():
    '''重启squid'''
    getoutput('/etc/init.d/squid restart')


if __name__ == "__main__":
    while True:
        if not linkstatus():
            connect_vpn(VPNS)
            # up_routes()
        time.sleep(10) # vpn断线检测时间，10s

