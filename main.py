# Python Zusatzaufgabe / Eigenprojekt

# WebUntis "reverse engineered"
# Beispiel gehosted auf http://45.131.109.42:8080/timetable?class=6ari
# Damit ich meine Stundenpläne in meinen Kalender importieren kann

# Imitiert bestmöglichst den Untis Webclient
# Sendet einen Request an die exposed WebUntis API (mit gültigen Cookies, Referer, etc.)
# Responsedaten werden als Dictionary/Object in eine .ics Datei umgewandelt

# Am Ende wird auf http://<server>:8080/timetable?class=<klassenName/klassenId> die .ics Datei zum Download freigegeben
# Mögliche Klassen Parameter: 6ag, 6ari, 4grl oder direkt die interne Klassen-ID (z.B. 1898 für 6ari)
# Sieht im iCloud Kalendar ungefähr so aus: https://i.imgur.com/EKLGAwp.jpeg

import requests
from ics import Calendar, Event
from datetime import datetime, timedelta, timezone
from flask import Flask, send_file, request
from io import BytesIO
import pytz

app = Flask(__name__)

LOCAL_TZ = pytz.timezone("Europe/Vienna")

def generate_ics_file(resource_id="1898"):
    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "anonymous-school": "porciagymnasium",
        "priority": "u=1, i",
        "sec-ch-ua": "\"Google Chrome\";v=\"143\", \"Chromium\";v=\"143\", \"Not A(Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-webuntis-api-school-year-id": "21",
        "cookie": "schoolname=\"_cG9yY2lhZ3ltbmFzaXVt\"; Tenant-Id=\"7000500\"; traceId=5dead6fddcfdf992499289486e149d3db714d3b7; JSESSIONID=945C795336490B2DA359D713CFB84B06; _sleek_session=%7B%22init%22%3A%222025-08-31T14%3A47%3A27.866Z%22%7D",
        "Referer": f"https://porciagymnasium.webuntis.com/timetable/class?date=2026-01-12&entityId={resource_id}"
    }

    today = datetime.now()
    start_date = (today - timedelta(weeks=4)).strftime("%Y-%m-%d")
    end_date = (today + timedelta(weeks=24)).strftime("%Y-%m-%d")

    url = "https://porciagymnasium.webuntis.com/WebUntis/api/rest/view/v1/timetable/entries"
    params = {
        "start": start_date,
        "end": end_date,
        "format": "1",
        "resourceType": "CLASS",
        "resources": resource_id,
        "periodTypes": "",
        "timetableType": "STANDARD",
        "layout": "START_TIME"
    }

    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    data = response.json()

    cal = Calendar()

    def safe_long_name(position):
        try:
            return position[0]["current"].get("longName", "Unknown") if position and position[0]["current"] else "Unknown"
        except (IndexError, AttributeError):
            return "Unknown"

    for day in data.get("days", []):
        for entry in day.get("gridEntries", []):
            start_str = entry["duration"]["start"]
            end_str = entry["duration"]["end"]

            start = LOCAL_TZ.localize(datetime.fromisoformat(start_str))
            end = LOCAL_TZ.localize(datetime.fromisoformat(end_str))

            subject = safe_long_name(entry.get("position2")) or "Unknown Subject"
            # Abbreviate subjects
            abbreviations = {
                "Geographie und wirtschaftliche Bildung (2023)": "GEOGRAPHIE",
                "Biologie und Umweltbildung (2023)": "BIOLOGIE",
                "Geschichte und politische Bildung (2023)": "GESCHICHTE",
                "Musik (2023)": "MUSIK",
                "Kunst und Gestaltung (2023)": "KUNST",
                "RELIGION katholisch": "RK",
                "RELIGION evangelisch": "RE",
                "J BEWEGUNG u. SPORT": "SPORT",
                "H Informatik SP": "INFORMATIK",
                "Französisch Langform": "FRANZÖSISCH",
                "RELIGION islamisch": "ISLAM",
                "Latein Kurzform": "LATEIN",
                "W Geschichte (2023)": "GPB+",
                "F LABOR PH": "PHYSIK LABOR",
                "LABOR CHE": "CHEMIE LABOR",
                "LABOR BIUB": "BIOLOGIE LABOR",
                "H DIGITALE GRUNDBILDUNG": "DIGI",
                "B GZ/CAD": "GZ",
                "ZY Freizeit": "TABE",
            }
            for key, val in abbreviations.items():
                subject = subject.replace(key, val)

            teacher = safe_long_name(entry.get("position1")) or "Unknown Teacher"
            room = safe_long_name(entry.get("position3")) or "Unknown Room"

            event = Event()
            if entry.get("status") == "CANCELLED":
                event.name = f"❌ {subject}"
            elif entry.get("status") in ["ADDED", "ADDITIONAL", "SUBSTITUTED"]:
                event.name = f"🟢 {subject}"
            else:
                event.name = subject

            event.begin = start
            event.end = end
            event.location = room
            event.description = f"Teacher: {teacher}"

            cal.events.add(event)

    # Return ICS as bytes
    return cal.serialize().encode("utf-8")

@app.route("/timetable")
def download_ics():
    class_map = {
        "1a": "1755",
        "1b": "1758",
        "1c": "1761",
        "1d": "1764",
        "1e": "1767",
        "1f": "1770",
        "1g": "1773",
        "1s": "1776",
        "2a": "1779",
        "2b": "1781",
        "2c": "1784",
        "2d": "1787",
        "2e": "1790",
        "2f": "1793",
        "2g": "1796",
        "2h": "1799",
        "2s": "1802",
        "3ari": "1805",
        "3arl": "1808",
        "3bg": "1811",
        "3cri": "1814",
        "3crl": "1817",
        "3drl": "1820",
        "3eri": "1823",
        "3erl": "1826",
        "3fri": "1829",
        "3frl": "1832",
        "3gri": "1835",
        "3grl": "1838",
        "3s": "1841",
        "4ag": "1844",
        "4ari": "1847",
        "4arl": "1850",
        "4bg": "1853",
        "4bri": "1856",
        "4brl": "1859",
        "4cri": "1862",
        "4crl": "1865",
        "4gri": "1868",
        "4grl": "1871",
        "4s": "1874",
        "5ag": "1877",
        "5ari": "1880",
        "5bri": "1883",
        "5brl": "1886",
        "5cri": "1889",
        "5crl": "1892",
        "6ag": "1895",
        "6ari": "1898",
        "6brl": "1901",
        "7ag": "1904",
        "7bri": "1907",
        "7brl": "1910",
        "8ag": "1913",
        "8ari": "1916",
        "8arl": "1919",
        "8bri": "1922",
        "8brl": "1925",
    }

    class_arg = request.args.get("class", "1898")
    resource_id = class_map.get(class_arg, class_arg)

    try:
        ics_bytes = generate_ics_file(resource_id)
    except Exception as e:
        return f"Error generating ICS: {e}", 500

    buf = BytesIO(ics_bytes)
    buf.seek(0)
    return send_file(
        buf,
        as_attachment=True,
        download_name=f"timetable_{resource_id}.ics",
        mimetype="text/calendar"
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)