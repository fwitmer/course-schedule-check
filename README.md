# UAA Course Schedule Conflict Checker

An interactive web application designed for academic department chairs and schedulers at the University of Alaska Anchorage (UAA) to analyze course schedules, detect time conflicts among major requirements, and simulate schedule adjustments.

Deployed at: [http://www.cse.uaa.alaska.edu/sc](http://www.cse.uaa.alaska.edu/sc)

---

## Overview

Planning course schedules across degree programs is complex. Department chairs need to ensure required courses for majors do not overlap in meeting times, preventing student progression bottlenecks.

This tool automates that process by:
1. **Catalog Requirement Mapping:** Storing undergraduate major requirements in a local database.
2. **Live Schedule Querying:** Fetching real-time class section data (meeting days, times, instructors, locations, and delivery methods) directly from the UAA Curric scheduling API.
3. **Visual Conflict Detection:** Rendering courses onto an interactive weekly calendar grid and automatically highlighting time conflicts between required courses.
4. **Interactive Simulation:** Allowing users to filter by instructor or location, hide/ignore specific courses, and test rescheduling moves with change logging.

---

## Key Features

- **Dynamic Term Selection:** Supports current and upcoming terms (Spring, Summer, Fall) across academic years.
- **Major & Subject Multi-Select:** Select one or more degree majors (e.g., Computer Science BS, Computer Systems Engineering BS) and supplemental subject codes.
- **Automated Conflict Detection:** Highlights overlapping time slots and provides detailed conflict summaries comparing course times, instructors, and CRNs.
- **Visual Weekly Calendar:** Interactive day/time schedule grid (M–U, 08:30–22:00) with visual course tiles.
- **Online & Asynchronous Separation:** Automatically separates online and asynchronous courses into dedicated side panels.
- **Advanced Filtering:**
  - Filter by instructor or building/room.
  - Temporarily ignore or hide courses/subjects from conflict calculations.
- **Schedule Simulation:** Edit or drag course blocks to explore alternative meeting times and track changes in a session log.
- **Excel Import / Export:** Export current schedule views or load custom schedule files.

---

## Architecture & Tech Stack

- **Backend:** Python 3.12, [Django 4.2 LTS](https://www.djangoproject.com/), [Pandas](https://pandas.pydata.org/)
- **Database:** SQLite (`class_information.sqlite3`) storing program requirements and subject tables
- **Data Source:** Live UAA Curric scheduling API (`https://curric.uaa.alaska.edu/ajax/ajaxScheduleSearch.php`)
- **Frontend:** HTML5, CSS3, JavaScript (ES6+), jQuery, [Select2](https://select2.org/), [SheetJS (xlsx)](https://sheetjs.com/)
- **Production Server:** Apache 2.4 with `mod_wsgi` daemon mode on Ubuntu Linux

---

## Directory Structure

```text
CourseScheduleCheck/
├── deploy.sh                        # Automated deployment script for the Linux server
├── requirements.txt                 # Python dependencies
├── Major_Requirements_Scraping.py   # Catalog scraping script to refresh requirement tables
├── ScheduleChecker/                 # Main Django project directory
│   ├── manage.py                    # Django management script
│   ├── class_information.sqlite3    # SQLite database with requirements and subjects
│   ├── ScheduleChecker/             # Project settings & WSGI config
│   │   ├── settings.py
│   │   ├── urls.py
│   │   └── wsgi.py
│   ├── website/                     # Core application
│   │   ├── models.py                # Database models (MajorRequirements, Subjects, etc.)
│   │   ├── views.py                 # Views & Curric API data fetching logic
│   │   ├── urls.py                  # App URL routing
│   │   └── templates/
│   │       └── scheduler.html       # Single-page application interface
│   └── static/                      # Static assets
│       ├── css/
│       ├── js/
│       │   └── schedule.js          # Calendar rendering, filters, and conflict logic
│       └── images/
└── README.md
```

---

## Local Development Setup

### 1. Prerequisites
- Python 3.10+ (Python 3.12 recommended)
- Git

### 2. Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/fwitmer/course-schedule-check.git
   cd course-schedule-check
   ```

2. **Create and activate a virtual environment:**
   ```bash
   # Windows (PowerShell)
   python -m venv env
   .\env\Scripts\Activate.ps1

   # macOS / Linux
   python3 -m venv env
   source env/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r ScheduleChecker/requirements.txt
   ```

4. **Run the development server:**
   ```bash
   cd ScheduleChecker
   python manage.py runserver
   ```

5. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Production Deployment (Apache on Ubuntu)

The production site is hosted on `anc-mocklinux` (`www.cse.uaa.alaska.edu`) under the `/sc` subpath.

### One-Step Server Update
To deploy committed changes from GitHub to the production server:

```bash
cd /var/www/html/course_check/Schedule-Conflict-Checker-main
./deploy.sh
```

The script will:
1. Pull the latest commits from the `main` branch.
2. Set proper read/write file permissions for the Apache `www-data` group.
3. Gracefully reload the Apache web service.

---

## Credits & License

- **Initial Development (Spring 2023):** Austin Edwards, John Schwenke, and Conner Trouy (UAA Computer Science Capstone).
- **Maintenance & Updates:** Department of Computer Science & Engineering, University of Alaska Anchorage.
- **License:** GNU General Public License v3.0 (GPL-3.0).
