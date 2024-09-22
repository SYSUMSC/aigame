# change your python version
FROM python:3.12

WORKDIR /app

# change your pip env
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

COPY . .

EXPOSE 5000

CMD ["python", "app.py"]
