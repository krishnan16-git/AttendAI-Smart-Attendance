# AttendAI — Smart Attendance System Using Face Recognition

Beginner-friendly starter project using HTML/CSS/JavaScript, Python Flask and MySQL.

## Included
- Dashboard metrics and recent attendance
- Student registration and search
- Camera preview using browser permissions
- Demo attendance recording (explicitly labelled Manual Demo)
- Attendance reports and duplicate-per-day prevention in MySQL

## Important status
This starter does **not** yet perform actual face identification. The camera page is only a preview and the demo button records a manual demo entry. A trained recognition model and a carefully tested matching workflow are a separate next step. Do not present demo records as AI-recognized attendance.

## 1. Install requirements
Use Python 3.10+ and MySQL 8+.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

## 2. Create the database
Open MySQL Workbench or the MySQL command-line client and run all commands in `database.sql`.

## 3. Configure credentials
Copy `.env.example` to `.env` and set your MySQL username/password. Example:
```
DB_HOST=127.0.0.1
DB_PORT=3306
DB_NAME=attendai
DB_USER=root
DB_PASSWORD=your_actual_password
SECRET_KEY=use-a-long-random-secret
```
Do not upload `.env` to GitHub.

## 4. Run
```bash
python app.py
```
Open `http://127.0.0.1:5000` in your browser. Keep the terminal running.

## 5. Try it
1. Open Students and add a student.
2. Open Face Recognition and press Start Camera; allow camera permission.
3. Select the student and press Mark Demo Attendance.
4. Open Dashboard or Reports to see the saved record.
5. Try marking that student a second time on the same day; the database prevents duplicates.

## Troubleshooting
- MySQL connection failure: check MySQL is running and `.env` credentials/database are correct.
- `ModuleNotFoundError`: activate the virtual environment and run `pip install -r requirements.txt`.
- Camera failure: use `localhost`/`127.0.0.1`, allow camera permission, and close other apps using the camera.
- Port 5000 busy: change the final `app.run(debug=True)` line to `app.run(debug=True, port=5001)` and open port 5001.

## Before deployment
Disable debug mode, use a strong secret, add login/role permissions and CSRF protection, validate uploads, add audit logging and backups, and protect biometric data. Do not expose `/setup-db` publicly.
