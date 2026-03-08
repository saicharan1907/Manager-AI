import os
from dotenv import load_dotenv

# Ensure environment variables are loaded for Vercel Serverless Functions
load_dotenv(override=True)

# Import our actual FastAPI application from the backend module
from backend.main import app
