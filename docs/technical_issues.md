# Technical Issues & Resolutions

This file tracks technical issues encountered during development, along with their resolutions.

## 1. Alembic Not Found in venv
- **Step:** After installing Alembic, running `alembic` gave `command not found`.
- **Root Cause:** Alembic was installed in the user site-packages, not the venv, due to shell aliases and/or venv not being properly activated.
- **Resolution:** Removed shell aliases, recreated and activated the venv, installed Alembic inside the venv, and used the full path to the venv's Python and pip.

## 2. venv Python/Pip Path Issues
- **Step:** `which python` and `which pip` pointed to system Python, not venv, even after activation.
- **Root Cause:** Shell aliases for python/pip overrode venv activation.
- **Resolution:** Used `unalias python; unalias pip` in the session, then activated venv and used full path to venv's executables.

## 3. Moved Project Directory Broke venv
- **Step:** After moving/renaming the project directory, venv's pip/python scripts pointed to the old path.
- **Root Cause:** venv scripts hardcode the original path.
- **Resolution:** Deleted and recreated the venv in the new location, reinstalled dependencies.

## 4. Alembic Migration Error: NameError: name 'ForeignKey' is not defined
- **Step:** Running `alembic revision --autogenerate` failed with NameError.
- **Root Cause:** `ForeignKey` was used in models.py but not imported.
- **Resolution:** Added `ForeignKey` to the SQLAlchemy imports in models.py.

## 5. General Migration/DB Troubleshooting
- **Step:** Schema changes not reflected in DB.
- **Root Cause:** Alembic migration not generated/applied, or DB URL misconfigured.
- **Resolution:** Ensured correct DB URL in alembic.ini, ran `alembic revision --autogenerate` and `alembic upgrade head` after every model change.

---

Add new technical issues and resolutions below as they arise. 