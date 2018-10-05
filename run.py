"""
Inventory Service Runner

Start the Inventory Service and initializes logging
"""

import os
from app import app, service

# Pull options from environment
DEBUG = (os.getenv('DEBUG', 'False') == 'True')
PORT = os.getenv('PORT', '5000')

######################################################################
#   M A I N
######################################################################
if __name__ == "__main__":
    print "*********************************"
    print " I N V E N T O R Y   S E R V I C E "
    print "*********************************"
    service.initialize_logging()
    app.run(host='0.0.0.0', port=int(PORT), debug=DEBUG)
