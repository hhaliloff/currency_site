import requests

def get_currencies(url="https://www.cbr-xml-daily.ru/daily_json.js") -> dict:
    request = requests.get(url)
    data = request.json()
    cur = []
    keys = data["Valute"].keys()
    for key in keys:
        cur.append([data["Valute"][key]["NumCode"],
            data["Valute"][key]["CharCode"],
            data["Valute"][key]["Name"],
            data["Valute"][key]["Value"],
            data["Valute"][key]["Nominal"]
        ])
    return cur
