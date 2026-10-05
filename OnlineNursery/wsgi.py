"""
WSGI config for OnlineNursery project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os
import sys
import logging
from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise
from django.conf import settings

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the project directory to the Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(project_root)
logger.info(f"Added {project_root} to Python path")

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OnlineNursery.settings')
logger.info("Set DJANGO_SETTINGS_MODULE to OnlineNursery.settings")

try:
    logger.info("Initializing Django application")
    application = get_wsgi_application()
    
    logger.info("Configuring WhiteNoise")
    application = WhiteNoise(
        application,
        root=settings.STATIC_ROOT,
        prefix=settings.STATIC_URL,
    )
    
    # Add media files if needed
    if hasattr(settings, 'MEDIA_ROOT') and hasattr(settings, 'MEDIA_URL'):
        logger.info("Adding media files to WhiteNoise")
        application.add_files(settings.MEDIA_ROOT, prefix=settings.MEDIA_URL)
    
    logger.info("Application initialization completed successfully")
except Exception as e:
    logger.error(f"Error during WSGI application initialization: {str(e)}", exc_info=True)
    raise
