# WebUntis ICS Exporter

This project provides a way to export school timetables from WebUntis into `.ics` calendar files. It allows students to import their schedules into calendars like iCloud, Google Calendar, or Outlook.

Example hosted timetable: [http://45.131.109.42:8080/timetable?class=6ari](http://45.131.109.42:8080/timetable?class=6ari)

---

## Features

* Mimics the WebUntis web client as closely as possible.
* Fetches timetable data via the WebUntis API using proper headers, cookies, and referers.
* Converts response data into `.ics` format for calendar apps.
* Marks cancelled classes (`❌`), substitutions (`🟢`), and regular events.
* Supports class lookup by common name (e.g., `6ari`) or internal WebUntis ID (e.g., `1898`).

---

## Installation

1. Clone the repository:

```bash
git clone <repo-url>
cd <repo-directory>
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

Dependencies:

* `Flask` – web server
* `requests` – HTTP requests to WebUntis
* `ics` – create `.ics` calendar files
* `pytz` – timezone handling

---

## Usage

Run the Flask app:

```bash
python app.py
```

The server will start on `http://0.0.0.0:8080`.

### Fetching a timetable

Visit:

```
http://<server>:8080/timetable?class=<class_name_or_id>
```

* Example: `http://localhost:8080/timetable?class=6ari`
* Example using internal ID: `http://localhost:8080/timetable?class=1898`

Available class shortcuts:

| Shortcut | Internal ID |
| -------- | ----------- |
| 4grl     | 1871        |
| 6ag      | 1895        |
| 6ari     | 1898        |
| ...      | ...         |

---

## How It Works

1. Sends a GET request to the WebUntis API endpoint:

```
https://<school>.webuntis.com/WebUntis/api/rest/view/v1/timetable/entries
```

2. Uses headers, cookies, and referers to mimic a real browser session.
3. Parses JSON response and maps the following data for each entry:

   * Subject (with abbreviation mapping for weird original names)
   * Teacher
   * Room
   * Start and end times
   * Status (cancelled, substituted, added)
4. Creates an `.ics` file with events, emojis, and descriptions.
5. Serves the `.ics` file via Flask for download.

---

## Example iCloud View

The resulting `.ics` file appears roughly like this in iCloud Calendar:

![iCloud timetable example](https://i.imgur.com/EKLGAwp.jpeg)

---

## Customization

* Timezone: Currently set to `Europe/Vienna`. Adjust `LOCAL_TZ` if needed.
* Subject abbreviations: Modify the `abbreviations` dictionary inside `generate_ics_file()` for custom names.
* API headers/cookies: Replace with valid cookies for your school year and user session.

---

## License

This project is for personal/educational use. Use responsibly and respect WebUntis' terms of service.
