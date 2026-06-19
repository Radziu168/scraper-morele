import requests
import os

def get_turso_url():
    return os.getenv("TURSO_URL", "").replace("libsql://", "https://")

def get_turso_token():
    return os.getenv("TURSO_AUTH_TOKEN", "")

def execute(sql: str, params: list = []):
    url = get_turso_url()
    token = get_turso_token()
    
    args = []
    for p in params:
        if p is None:
            args.append({"type": "null"})
        elif isinstance(p, int):
            args.append({"type": "integer", "value": str(p)})
        elif isinstance(p, float):
            args.append({"type": "float", "value": str(p)})
        else:
            args.append({"type": "text", "value": str(p)})

    res = requests.post(
        f"{url}/v2/pipeline",
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
        json={
            "requests": [
                {
                    "type": "execute",
                    "stmt": {"sql": sql, "args": args}
                },
                {"type": "close"}
            ]
        }
    )
    return res.json()

def query(sql: str, params: list = []) -> list[dict]:
    result = execute(sql, params)
    try:
        rows = result["results"][0]["response"]["result"]["rows"]
        cols = result["results"][0]["response"]["result"]["cols"]
        return [
            {
                cols[i]["name"]: (
                    None if row[i]["type"] == "null"
                    else float(row[i]["value"]) if row[i]["type"] == "float"
                    else int(row[i]["value"]) if row[i]["type"] == "integer"
                    else row[i]["value"]
                )
                for i in range(len(cols))
            }
            for row in rows
        ]
    except (KeyError, IndexError):
        return []