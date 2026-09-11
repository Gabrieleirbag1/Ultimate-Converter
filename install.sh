docker build -t autotrace ./docker-autotrace
docker build -t inkscape ./docker-inkscape
docker build -t spotdl ./docker-spotdl

#check if venv
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt

#generate secrets file (whith empty value for the constants)
mkdir -p src/secrets
touch src/secrets/instagram.secret
touch src/secrets/spotify.secret
echo "USERNAME=" > src/secrets/instagram.secret
echo "CLIENT_ID=" > src/secrets/spotify.secret
echo "CLIENT_SECRET=" >> src/secrets/spotify.secret