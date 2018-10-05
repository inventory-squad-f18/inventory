"""
Package: app

Package for the application models and services
This module also sets up the logging to be used with gunicorn
"""
import logging
from flask import Flask

# Create Flask application
app = Flask(__name__)
