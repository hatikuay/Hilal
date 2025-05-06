from app import create_app, db
from flask_migrate import Migrate
import os

app = create_app()
migrate = Migrate(app, db)

if __name__ == "__main__":
    #app.run(debug=True)
    with app.app_context():
        db.create_all()     # ← users, notes tablolarını (ve varsa diğerlerini) yaratır
    debug = (os.environ.get("FLASK_ENV") != "production")
    app.run(host="0.0.0.0", debug=True)
