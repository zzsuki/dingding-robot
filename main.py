from typing import Any, List
from src.dingding import DingDing
from src.settings import TEMPLATE_PATH, ROBOT_SECRET, ROBOT_TOKEN
from fastapi import FastAPI
from pydantic import BaseModel
from jinja2 import Environment, select_autoescape, PackageLoader, FileSystemLoader
from datetime import datetime, timedelta
import uvicorn


class PrometheusAlert(BaseModel):
    status: str
    labels: Any
    annotations : Any
    startsAt: str
    endsAt: str
    generatorURL: str
    fingerprint: str
    

class PrometheusHookRequest(BaseModel):
    status: str
    alerts: List[PrometheusAlert]
    

app = FastAPI()

@app.post("/webhook")
async def webhook(hook_request: PrometheusHookRequest):
    """webhook主业务，将alertmanager的告警推送至dingding机器人"""
    # 修复发生时间
    time_format = "%Y-%m-%dT%H:%M:%S.%fZ"
    for item in hook_request.alerts:
        source_time = datetime.strptime(item.startsAt, time_format) 
        real_time = source_time + timedelta(hours=8)
        real_time = real_time.strftime("%Y-%m-%d %H:%M:%S")
        item.startsAt = real_time
    # 生成发送的信息内容
    env = Environment(loader=FileSystemLoader(TEMPLATE_PATH), autoescape=select_autoescape(), trim_blocks=False)
    template = env.get_template('message.template')
    alerts = [item for item in hook_request.alerts if item.status == 'firing']
    resolved = [item for item in hook_request.alerts if item.status == 'resolved']
    text = template.render(alerts=alerts, resolved=resolved)
    dd = DingDing(token=ROBOT_TOKEN, secret=ROBOT_SECRET)
    dd.send_markdown(title="Prometheus告警", text=text)
    return {"status": "ok"}
    # return hook_request

@app.get("/")
async def webhook():
    return {"message": "Hello World"}


if __name__ == '__main__':  
    if not ROBOT_SECRET or not ROBOT_TOKEN:
        raise ValueError('未同时提供机器人secret和token, 请检查环境变量配置是否正确')
    uvicorn.run("main:app", host="0.0.0.0", port=8020, log_level="info")