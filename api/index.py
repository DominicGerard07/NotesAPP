import os
import sys

# Ensure project root is in sys.path for module resolution in Vercel serverless environment
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

from app import create_app

# Vercel looks for the WSGI application instance named `app`
app = create_app()

