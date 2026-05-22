docker build -t autotrace ./docker-autotrace
docker build -t inkscape ./docker-inkscape
docker build -t spotdl ./docker-spotdl

#check if venv
if [ ! -d ".venv" ]; then
    python3 -m venv .venv
fi
source .venv/bin/activate
pip install -r requirements.txt