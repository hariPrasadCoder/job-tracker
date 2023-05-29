#!/bin/bash

cd "$(dirname "$0")"
sudo uvicorn main:app --host=0.0.0.0 --workers=4