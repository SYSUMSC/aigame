# TODO! change your python version
FROM python:3.12

WORKDIR /app

# download nginx
RUN apt-get update && apt-get install -y nginx && rm -rf /var/lib/apt/lists/*
COPY nginx.conf /etc/nginx/nginx.conf

# change your pip env
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple

COPY . .

EXPOSE 5000

CMD ["sh", "-c", "gunicorn -b 127.0.0.1:8000 app:app & nginx -g 'daemon off;'"]
