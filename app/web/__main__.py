from app.config import charger_env
from app.web import create_app

charger_env()
print("Colle de maths : http://127.0.0.1:5000  (Ctrl+C pour arrêter)")
create_app().run(host="127.0.0.1", port=5000, threaded=True, load_dotenv=False)
