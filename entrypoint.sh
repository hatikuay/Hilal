#!/usr/bin/env sh
set -e

# 1) Veritabanına migration’ları uygula
flask db upgrade

# 2) Başlangıç seed’ini çalıştır
python - << 'EOF'
from app import create_app, db
from app.models import User, Role
from werkzeug.security import generate_password_hash

app = create_app()
with app.app_context():
    # eğer 'hilal' daha önce yoksa ekle
    if not User.query.filter_by(username='hilal').first():
        admin = User(
            username='hilal',
            password=generate_password_hash('123456789', method='scrypt'),
            role=Role.ADMIN
        )
        db.session.add(admin)
        db.session.commit()
        print("Başlangıç admin kullanıcı oluşturuldu: hilal / 123456789")
    else:
        print("Başlangıç admin zaten mevcut.")
EOF

# 3) Ana container komutunu çalıştır
exec "$@"
