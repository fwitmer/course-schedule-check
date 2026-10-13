#!/bin/bash
set -e

echo "==> Pulling latest changes from GitHub..."
git pull origin main

if [ -d "ScheduleChecker/assets" ]; then
    echo "==> Syncing static files to ScheduleChecker/assets..."
    cp -r ScheduleChecker/static/* ScheduleChecker/assets/
fi

echo "==> Setting permissions for Apache (www-data)..."
sudo chmod -R g+rX,o+rX .
if [ -f "ScheduleChecker/class_information.sqlite3" ]; then
    sudo chmod 664 ScheduleChecker/class_information.sqlite3
    sudo chmod 775 ScheduleChecker
fi

echo "==> Restarting Apache..."
sudo systemctl restart apache2

echo "==> Deployment complete!"
