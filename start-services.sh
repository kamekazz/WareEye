#!/bin/bash
# Unified startup script for WareEye services

export FLASK_APP=app.py
venv/bin/python app.py
