#Temel Python imajı
FROM python:3.11

WORKDIR /app

COPY . . 

RUN pip install --no-cache-dir -r requirements.txt

CMD ["python", "run.py"]

# Çalışma dizinine kopyalayalım
COPY . /app
WORKDIR /app

# entrypoint betiğini kopyala ve çalıştırılabilir yap
COPY entrypoint.sh /usr/local/bin/entrypoint.sh
RUN chmod +x /usr/local/bin/entrypoint.sh

# Flask ihtiyaçları
RUN pip install -r requirements.txt

# ENTRYPOINT ve CMD
ENTRYPOINT ["entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]