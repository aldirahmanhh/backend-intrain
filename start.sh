#!/bin/bash

# Start Flask in the background
flask --app server.py run --host=0.0.0.0 &

# Start Cloudflared tunnel
cloudflared tunnel --url http://localhost:5000 --no-autoupdate 