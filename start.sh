#!/bin/bash

cd "$(dirname "$0")"
source venv/bin/activate
uvicorn main:app --workers=4