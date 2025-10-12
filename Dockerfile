FROM python:3.12-slim

# =============================
# STAGE 2: PYTHON DEPENDENCIES
# =============================
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

FROM python:3.13-slim AS base
WORKDIR /app
ENV PYTHONUNBUFFERED=1
# instalar dependências do sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl unzip gnupg ca-certificates \
    default-mysql-client \
    fonts-liberation \
    libasound2 libatk-bridge2.0-0 libatk1.0-0 libatspi2.0-0 libcups2 \
    libdbus-1-3 libdrm2 libgbm1 libgtk-3-0 libnspr4 libnss3 libx11-6 libx11-xcb1 \
    libxcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 libxrandr2 libxrender1 \
    libxshmfence1 xdg-utils \
 && rm -rf /var/lib/apt/lists/* /tmp/*

# copiar Python packages instalados
COPY --from=builder /install /usr/local

# instalar Chrome Latest + ChromeDriver
RUN CHROME_VERSION=$(curl -s https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_STABLE) \
    && curl -Lo /tmp/chrome-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chrome-linux64.zip \
    && curl -Lo /tmp/chromedriver-linux64.zip https://storage.googleapis.com/chrome-for-testing-public/${CHROME_VERSION}/linux64/chromedriver-linux64.zip \
    && unzip /tmp/chrome-linux64.zip -d /opt/ \
    && unzip /tmp/chromedriver-linux64.zip -d /opt/ \
    && mv /opt/chrome-linux64 /opt/chrome \
    && mv /opt/chromedriver-linux64/chromedriver /usr/local/bin/chromedriver \
    && ln -s /opt/chrome/chrome /usr/local/bin/google-chrome \
    && chmod 755 /usr/local/bin/chromedriver /opt/chrome/chrome \
    && rm -rf /tmp/*.zip

FROM base AS web
COPY . .
RUN chmod +x celery.sh
RUN rm -rf frontend

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
