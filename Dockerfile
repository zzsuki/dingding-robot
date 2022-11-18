FROM python:3.10.4

WORKDIR /work

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

COPY . .

EXPOSE 8000

ENV TZ=Asia/Shanghai

ENTRYPOINT ["python3", "main.py"]
