import os
from sys import exit

from apps.config import config_dict
from apps import create_app

DEBUG = (os.getenv('DEBUG', 'False') == 'True')

get_config_mode = 'Debug' if DEBUG else 'Production'

try:
    
    # Load the configuration using the default values
    app_config = config_dict[get_config_mode.capitalize()]

except KeyError:
    exit('Error: Invalid <config_mode>. Expected values [Debug, Production] ')
    
app = create_app(app_config)

if DEBUG:
    app.logger.info('DEBUG       = ' + str(DEBUG)             )
    app.logger.info('FLASK_ENV   = ' + os.getenv('FLASK_ENV') )    
    app.logger.info('ASSETS_ROOT = ' + app_config.ASSETS_ROOT )

if __name__ == "__main__":
    # app.run(debug=True)
    # app.run(host='0.0.0.0')
    app.run(host='0.0.0.0', port=os.environ.get("PORT", 85))