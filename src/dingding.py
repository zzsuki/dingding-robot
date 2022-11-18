# -*- coding: utf-8 -*-
import sys
import json
import time
import hmac
import hashlib
import base64
from .settings import ROBOT_TOKEN, ROBOT_SECRET


if sys.version_info > (3, 0):
    from urllib.request import urlopen, Request
    from urllib.parse import quote_plus
else:
    from urllib2 import urlopen, Request
    from urllib import quote_plus

SHOW_AVATAR = "0"  # 不隐藏头像
HIDE_AVATAR = "1"  # 隐藏头像

BTN_CROSSWISE = "0"  # 横向
BTN_LENGTHWAYS = "1"  # 纵向


class DingDing:
    """钉钉机器人简单封装"""
    def __init__(self, token: str, secret: str):
        """构造方法，注意区分token和secret"""
        self.url = self.parse_token(token)
        self.headers = {"Content-Type": "application/json"}
        self.secret = secret

    def _generate_url(self, token):
        """生成url，传入token则自动追加前边的url；如果传入url则返回url"""
        token = token.strip()
        if len(token) == 64:
            return f"https://oapi.dingtalk.com/robot/send?access_token={token}"
        elif len(token) == 114:
            return token
        else:
            raise ValueError("token异常，请检查token格式")

    def send_text(self, text, at_mobiles=[], at_all=False):
        """以文本格式发送消息
        :param text: 要传输的内容
        :param at_mobiles: 被@人的手机号，以列表格式传入，eg: ['13333333333', ]。默认为[]，即不@任何人
        :param at_all: @所有人时:true,否则为:false。默认为false
        :return: 响应json
        """
        data = {
            "msgtype": "text",
            "text": {"content": text},
            "at": {"atMobiles": at_mobiles, "isAtAll": at_all},
        }
        return self._send(data)

    def send_link(self, title, text, message_url="", pic_url=""):
        """发送链接消息，可以包含图片等url
        :param title: 消息标题
        :param text: 消息内容。如果太长只会部分展示
        :param message_url: 点击消息跳转的URL
        :param pic_url: 图片URL
        :return: 响应json
        """
        data = {
            "msgtype": "link",
            "link": {
                "text": text,
                "title": title,
                "picUrl": pic_url,
                "messageUrl": message_url,
            },
        }
        return self._send(data)

    def send_markdown(self, title, text, at_mobiles=[], at_all=False):
        """以markdown格式发送消息
        :param title: 消息标题
        :param text: 消息内容
        :param at_mobiles: 被@人的手机号，以列表格式传入，eg: ['13333333333', ]。默认为[]，即不@任何人
        :param at_all: @所有人时:true,否则为:false。默认为false
        :return: 响应json
        """
        data = {
            "msgtype": "markdown",
            "markdown": {"title": title, "text": text},
            "at": {"atMobiles": at_mobiles, "isAtAll": at_all},
        }
        return self._send(data)

    def send_single_action_card(self, title, text, single_title, single_url, btn_orientation=BTN_LENGTHWAYS, hide_avatar=SHOW_AVATAR):
        """整体跳转ActionCard类型
        :param title: 消息标题
        :param text: 消息内容
        :param single_title: 单个按钮的方案。(设置此项和singleURL后btns无效。)
        :param single_url: 点击singleTitle按钮触发的URL
        :param btn_orientation: 0-按钮竖直排列，1-按钮横向排列
        :param hide_avatar: 0-正常发消息者头像,1-隐藏发消息者头像
        :return: 响应json
        """
        data = {
            "actionCard": {
                "title": title,
                "text": text,
                "hideAvatar": hide_avatar,
                "btnOrientation": btn_orientation,
                "singleTitle": single_title,
                "singleURL": single_url,
            },
            "msgtype": "actionCard",
        }
        return self._send(data)

    def send_action_card(self, title, text, btns, btn_orientation=BTN_LENGTHWAYS, hide_avatar=SHOW_AVATAR):
        """独立跳转ActionCard类型
        :param title: 消息标题
        :param text: 消息内容
        :param btns: 按钮的信息：title-按钮方案，actionURL-点击按钮触发的URL
        :param btn_orientation: 0-按钮竖直排列，1-按钮横向排列
        :param hide_avatar: 0-正常发消息者头像,1-隐藏发消息者头像
        :return: 响应json
        """
        btns = [{"title": btn[0], "actionURL": btn[1]} for btn in btns]
        data = {
            "actionCard": {
                "title": title,
                "text": text,
                "hideAvatar": hide_avatar,
                "btnOrientation": btn_orientation,
                "btns": btns,
            },
            "msgtype": "actionCard",
        }
        return self._send(data)

    def send_feed_card(self, rows):
        """FeedCard类型
        :param rows: [(title, messageURL, picURL), (...)]
        :return: 响应json
        """
        rows = [{"title": title, "messageURL": message_url, "picURL": pic_url} for title, message_url, pic_url in rows]
        data = {"feedCard": {"links": rows}, "msgtype": "feedCard"}
        return self._send(data)

    def _send(self, data):
        """实际发送消息的方法"""
        url = self.url
        if self.secret:
            sign, timestamp = self.get_sign_timestamp()
            url = url + "&sign=" + sign + "&timestamp=" + timestamp

        data = json.dumps(data)
        req = Request(url, data=data.encode("utf-8"), headers=self.headers)
        response = urlopen(req)
        the_page = response.read()
        return json.loads(the_page.decode("utf-8"))

    def get_sign_timestamp(self):
        """给予secret计算签名和时间戳"""
        timestamp = "%d" % (round(time.time() * 1000))
        secret_enc = self.secret.encode("utf-8")
        string_to_sign = "{}\n{}".format(timestamp, self.secret)
        string_to_sign_enc = string_to_sign.encode("utf-8")
        hmac_code = hmac.new(
            secret_enc, string_to_sign_enc, digestmod=hashlib.sha256
        ).digest()
        sign = quote_plus(base64.b64encode(hmac_code))
        return sign, timestamp