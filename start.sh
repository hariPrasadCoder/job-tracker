#!/bin/bash

cd "$(dirname "$0")"
python3 -m uvicorn main:app --host=0.0.0.0 --workers=4