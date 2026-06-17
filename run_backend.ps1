$env:DATA_DIR = "C:\Users\Gaurav\Task - Lila\player_data"
Set-Location "C:\Users\Gaurav\Task - Lila\lila-black\backend"
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001 --log-level info
