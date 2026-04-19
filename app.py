#dependencies
import warnings
warnings.filterwarnings("ignore")

from flask import Flask
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import logger as _logger_config  #Triggers only basicConfig
import logging
from routes.chat import chat_bp
from src.extensions import limiter

logger = logging.getLogger(__name__)
app = Flask(__name__)
limiter.init_app(app)

app.register_blueprint(chat_bp)


if __name__ == '__main__':
    app.run(host='0.0.0.0',port = 8080,debug=True)