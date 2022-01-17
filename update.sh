# Stop docker
cd /root/ofisino
echo "✋ Stopping app..."
docker-compose stop

# Unzip new source code into app dir
echo "🏗 Unzipping new source into app dir"
tar -xvf /tmp/ofisino.zip

# Copy frontend code into nginx folder
echo "🪄  Copying frontend build into nginx folder"
cp -r /root/ofisino/frontend/build/* /usr/share/nginx/html/

# Restart backend
echo "🚀 Starting app new version.."
docker-compose -f docker-compose.prod.yml up -d

# Test api and restart nginx
echo "🔎 Running deploy checks.."
sleep 5
curl http://localhost:8000/
