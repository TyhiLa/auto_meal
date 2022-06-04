#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time : 2021 Dec 24
# @Author : Hoshimaemi
import base64
import random
from datetime import datetime, date, timedelta
import json
from typing import Dict
import requests

# TODO: 捕捉无订餐时间的错误
# 登陆接口
LOGIN = 'https://syczapi.payc.net.cn/nlogin'
# 账号信息
USER_INFO = 'https://syczapi.payc.net.cn/user_balance'
# 可订餐时间
TAKE_DATE = 'https://syczapi.payc.net.cn/tk_available_date'
# 菜单 (侧边栏)
MEAL_TYPE = 'https://syczapi.payc.net.cn/set_meal_type'
# 具体餐品
MEAL_DATA = 'https://syczapi.payc.net.cn/set_meal_data'
# 查看订餐状态
OD_STATUS = 'https://syczapi.payc.net.cn/set_meal_times'
# 添加购物车
CART_ADD = 'https://syczapi.payc.net.cn/set_meal_change_num'
# 购物车列表 -> 获取id
CART_LIST = 'https://syczapi.payc.net.cn/set_meal_cart_data'
# 购物车提交 -> 使用id
CART_SUBMIT = 'https://syczapi.payc.net.cn/set_meal_submit'
# headers
HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Content-Type": "application/x-www-form-urlencoded;charset=UTF-8",
    "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Mobile Safari/537.36",
    "sec-ch-ua-platform": "Android",
    "Origin": "http://syczqt21.payc.net.cn",
    "Sec-Fetch-Site": "cross-site",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Dest": "empty",
    "Referer": "http://syczqt21.payc.net.cn/",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept-Language": "en-US,en;q=0.9"
}
# 测试帐号
ac1 = {"account": "13080832887", "password": "wb258369"}


# 密码处理
def pass2flag(passwd: str) -> str:
    stra = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    b64 = base64.b64encode(passwd.encode('utf-8'))
    letters = ''
    for _ in range(23):
        letters += random.choice(stra)
    flag = letters[:13] + bytes.decode(b64) + '8176' + letters[14:]
    return flag


# 登录提交
PARAMS = {
    "login_info": ac1["account"],
    "flag": pass2flag(ac1["password"])
}


class Main(object):
    def __init__(self, login: dict) -> None:
        # 每次登录都需读取，无需缓存
        self.token = login.get("token")
        self.balance = self.get_data(USER_INFO).get("balance")
        self.od_day = self.tk_date()
        self.meal_type = self.menu_type()
        # TODO: 判断餐品是否有剩余 排除餐品订购完成的错误
        self.meal_list = self.get_data(MEAL_DATA)
        # print(self.cart_add())
        # print(self.cart_sub())
        # print(self.menu_data())

    def get_data(self, api_url: str, **kwargs) -> Dict[str, str]:
        result = requests.post(url=api_url,
                                headers=HEADERS,
                                data=dict(**{"token": self.token}, **kwargs))
        try:
            print(result)
            return result.json()
        except requests.exceptions.JSONDecodeError:
            return {"error": "error"}

    def tk_date(self) -> list:
        year = datetime.now().year
        cn_time = self.get_data(TAKE_DATE)
        start_time = cn_time["start_time"]
        sdate = date(year, int(start_time[0:2]), int(start_time[3:5]))
        end_time = cn_time["end_time"]
        edate = date(year, int(end_time[0:2]), int(end_time[3:5]))
        delta = edate - sdate
        days = []
        for i in range(delta.days + 1):
            day = sdate + timedelta(days=i)
            days.append(str(day))
        return days

    def menu_type(self) -> Dict[str, str]:
        return self.get_data(MEAL_TYPE, preset_date=self.od_day[0], meal_times_id=1)

    def menu_data(self) -> Dict[str, str]:
        return self.get_data(MEAL_DATA, preset_date="2022-04-08", meal_times_id=2, meal_type_id=8)

    def if_checked(self) -> Dict[str, str]:
        return self.get_data(OD_STATUS, preset_date="2022-04-09")

    def cart_add(self, pdate, mti, mtyi, mid) -> Dict[str, str]:
        return self.get_data(CART_ADD, preset_date=pdate, meal_times_id=mti, meal_type_id=mtyi, meal_id=mid, num=1)

    def cart_sub(self):
        cart_list = self.get_data(CART_LIST)
        li = []
        for i in cart_list['data']:
            li.append(i['id'])
        return self.get_data(CART_SUBMIT, record_ids=li)

    def json2order(self) -> None:
        with open("default.json") as dm:
            ord_list = json.load(dm)
        with open("meal_id.json") as mid:
            meal_id = json.load(mid)
        # i: 订餐数据 "MM"
        # j: 订餐时间 "YYYY-MM-DD"
        # m: 订餐数据 "M"
        # n: 午餐和晚餐 1 / 2
        for i, j in zip(ord_list.values(), self.od_day):
            for m, n in zip(i, [1, 2]):
                result = self.cart_add(j, n, meal_id[m][0], meal_id[m][1])
                if result is None:
                    continue
                # TODO: 卡内余额不足情况
                while result.get('code') != 200:
                    alter = random.choice(list(meal_id.keys()))
                    if alter in ["Y", "Z"]:
                        continue
                    result = self.cart_add(j, n, meal_id[m][0], meal_id[m][1])
        self.cart_sub()


def main():
    response = requests.post(url=LOGIN, headers=HEADERS, data=PARAMS).json()
    op1 = Main(response)
    op1.json2order()


if __name__ == "__main__":
    main()
