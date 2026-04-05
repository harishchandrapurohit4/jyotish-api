FROM python:3.11-slim
WORKDIR /app
RUN apt-get update && apt-get install -y wget curl && rm -rf /var/lib/apt/lists/*
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN mkdir -p /usr/share/ephem && \
    wget -q -P /usr/share/ephem https://www.astro.com/ftp/swisseph/ephe/seas_18.se1 && \
    wget -q -P /usr/share/ephem https://www.astro.com/ftp/swisseph/ephe/semo_18.se1 && \
    wget -q -P /usr/share/ephem https://www.astro.com/ftp/swisseph/ephe/sepl_18.se1
COPY main.py astro_engine.py ./
ENV EPHEM_PATH=/usr/share/ephem
EXPOSE 8000
CMD ["gunicorn", "main:app", "-w", "4", "-k", "uvicorn.workers.UvicornWorker", "-b", "0.0.0.0:8000"]
