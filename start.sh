#!/bin/bash

echo "Starting internal service..."
python service_app.py &

echo "Starting main app..."
python app.py
