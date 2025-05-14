FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulamanın tamamını kopyala (entrypoint.sh da dahil)
COPY . .

# /app altındaki entrypoint.sh dosyasına çalıştırma izni ver
RUN chmod +x ./entrypoint.sh

ENV FLASK_APP=run.py \
    FLASK_ENV=production

# Dosyanın doğru konumundan çalıştır
ENTRYPOINT ["./entrypoint.sh"]
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "run:app"]
