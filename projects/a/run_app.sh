#!/bin/bash

# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies from requirements.txt
pip install -r requirements.txt

# Run the weather application
python weather_app.py

# Deactivate the virtual environment (optional)
deactivate