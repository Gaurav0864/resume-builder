# job-copilot (Phase 1)

A beginner-friendly local tool for a fresher in Pune preparing for Data Analyst and Junior Analyst roles. Phase 1 provides a numbered menu, first-run setup, a local SQLite database, logging, and safe dry-run defaults. It does not search job sites or submit applications.

## Requirements

- Python 3.10 or newer
- Internet access to install the small YAML dependency

## Setup on Windows

Open PowerShell in this project folder and run:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py run.py
```

On the first run, the wizard asks for your name, city, and target roles. Press Enter to accept a suggested value; you can change the settings in `config.yaml` later. It creates `config.yaml` and `.env`. The environment file starts empty and no password is requested or stored. Both local files are ignored by Git.

## Phase 1 menu

1. Show status and local record counts.
2. View profile and safety settings.
3. Confirm dry-run mode is on.
4. Create or check the local database.
0. Exit.

Dry-run cannot be turned off in Phase 1. SQLite data is stored in `data/job_copilot.db`, and rotating logs are in `logs/job-copilot.log`. The starter database has `jobs` and `applications` tables but contains no imported job data.

## Tests

```powershell
py -m unittest discover -s tests -v
```

## Troubleshooting

- **`No module named yaml`**: activate the virtual environment and run `py -m pip install -r requirements.txt` again.
- **PowerShell says scripts are disabled**: skip activation and run the virtual environment's Python interpreter from `.venv/Scripts/python.exe`.
- **Invalid YAML error**: close the app, copy `config.example.yaml` to `config.yaml`, then run `py run.py` and edit the settings carefully.
- **Database or log permission error**: check that this project folder is writable, then start `py run.py` again.

## Safety

This phase works locally and performs no network requests, application submissions, CAPTCHA handling, browser automation, or stealth behavior. Later phases should continue to prepare materials for you to review and submit yourself.
