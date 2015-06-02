from spendb.core import create_web_app
from spendb.command import assets

app = create_web_app()

if not app.config.get('ASSETS_DEBUG'):
    with app.app_context():
        assets.auto_build = False
