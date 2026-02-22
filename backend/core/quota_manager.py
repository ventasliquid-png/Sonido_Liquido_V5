import json
import os
from datetime import datetime, timedelta

STATUS_FILE = "quota_status.json"

def registrar_penalizacion(retry_after=60):
    release_time = datetime.now() + timedelta(seconds=retry_after)
    status = {
        "status": "DEGRADADO",
        "release_timestamp": release_time.isoformat(),
        "last_update": datetime.now().isoformat()
    }
    with open(STATUS_FILE, "w") as f:
        json.dump(status, f, indent=4)

def get_quota_status():
    if not os.path.exists(STATUS_FILE):
        return {"status": "OK"}
    try:
        with open(STATUS_FILE, "r") as f:
            data = json.load(f)
        release_time = datetime.fromisoformat(data["release_timestamp"])
        if datetime.now() > release_time:
            os.remove(STATUS_FILE)
            return {"status": "OK"}
        return data
    except:
        return {"status": "OK"}
