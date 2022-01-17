set -euo pipefail
echo "⚒ Bulding docker image.."
make build
echo "🧪 Running tests"
make test
echo "✅ All checks passed ✨"
