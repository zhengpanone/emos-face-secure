# 使用官方Python基础镜像
FROM python:3.12.9-slim

# 设置环境变量，防止Python输出缓冲
ENV PYTHONUNBUFFERED=1

# 安装系统依赖项
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    libgl1-mesa-glx \
    cmake \
    libboost-all-dev &&\
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# 设置工作目录
WORKDIR /app

# 将当前目录中的所有文件复制到容器中的工作目录
COPY . /app

# 安装所需的Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 暴露Flask应用的端口
EXPOSE 5000

# 设置环境变量以便Flask能够找到应用
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# 运行Flask应用
CMD ["flask", "run"]
