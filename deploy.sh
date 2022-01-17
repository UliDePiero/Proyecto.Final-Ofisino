# Asumes it will be run on docker droplet on digital ocean
set -eo pipefail

# Check if env var is defined
if [[ -z "${VMIP}" ]]; then
    echo "❌ You must set VMIP environment variable pointing to the remote vm"
    exit 1
fi

echo "👷‍♂️ Creating frontend optimized build"
cd frontend && npm run build
cd -

echo "🏗 Zipping repo into ofisino.zip"

tar --exclude='*.git*' --exclude='*.idea*' \
    --exclude='*.vscode*' --exclude='*.pytest_cache*' \
    --exclude='*__pycache__*' --exclude='*node_modules*' \
    --exclude='*venv*' -cvf ofisino.zip .

echo "⏳ Copying zip to vm: '${VMIP}'."
scp ofisino.zip root@$VMIP:/tmp
echo "✅ Copy finished"
echo "🖥️  Updating new app in VM"
ssh -tt root@$VMIP < update.sh
