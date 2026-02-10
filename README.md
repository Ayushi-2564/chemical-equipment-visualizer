# Chemical Equipment Parameter Visualizer (Hybrid Web + Desktop App)

## Project Title

Chemical Equipment Parameter Visualizer
Hybrid Web + Desktop Data Visualization and Analytics Application

---

## Project Overview

This project is a Hybrid Application that runs both as a:

* Web Application
* Desktop Application

The system allows users to upload CSV datasets containing chemical equipment parameters. The backend processes the dataset, performs analytical computations, and exposes APIs consumed by both frontends for visualization and reporting.

The goal is to demonstrate:

* Data handling and analytics
* Backend API development
* Cross‑platform frontend integration
* Visualization consistency

---

## Tech Stack

| Layer              | Technology                     | Purpose                      |
| ------------------ | ------------------------------ | ---------------------------- |
| Frontend (Web)     | React.js + Chart.js            | Data tables and charts       |
| Frontend (Desktop) | PyQt5 + Matplotlib             | Desktop visualization        |
| Backend            | Django + Django REST Framework | API and data processing      |
| Data Handling      | Pandas                         | CSV parsing and analytics    |
| Database           | SQLite                         | Store last 5 datasets        |
| Version Control    | Git + GitHub                   | Collaboration and submission |

---

## Sample Dataset

File: `sample_equipment_data.csv`

Columns included:

* Equipment Name
* Type
* Flowrate
* Pressure
* Temperature

Used for:

* Testing
* Demo visualization
* API validation

---

## Key Features

### 1. CSV Upload

* Available in both Web and Desktop apps
* Upload CSV file to Django backend
* Backend validates and stores dataset

### 2. Data Summary API

Django REST API computes:

* Total equipment count
* Average flowrate
* Average pressure
* Average temperature
* Equipment type distribution

### 3. Visualization

Web (React + Chart.js):

* Bar charts
* Pie charts
* Dataset tables

Desktop (PyQt5 + Matplotlib):

* Embedded charts
* Summary graphs
* Equipment distribution plots

### 4. History Management

* Stores last 5 uploaded datasets
* Displays dataset summaries
* Enables quick comparison

### 5. PDF Report Generation

* Generate downloadable summary reports
* Includes statistics and charts

### 6. Basic Authentication

* Login system for secure access
* Dataset upload restricted to authenticated users

---

## Project Architecture

```
chemical-equipment-visualizer/
│
├── backend/                # Django + DRF Backend
│   ├── api/
│   ├── models.py
│   ├── views.py
│   ├── serializers.py
│   └── urls.py
│
├── web-frontend/          # React Application
│   ├── src/
│   ├── components/
│   └── charts/
│
├── desktop-app/           # PyQt5 Application
│   ├── ui/
│   ├── charts/
│   └── main.py
│
├── sample_data/
│   └── sample_equipment_data.csv
│
└── README.md
```

---

## Backend Setup (Django)

### 1. Clone Repository

```bash
git clone https://github.com/Ayushi-2564/chemical-equipment-visualizer.git
cd chemical-equipment-visualizer/backend
```

### 2. Create Virtual Environment

```bash
python -m venv venv
source venv/bin/activate     # Mac/Linux
venv\\Scripts\\activate      # Windows
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Start Server

```bash
python manage.py runserver
```

Backend runs at:

```
http://127.0.0.1:8000/
```

---

## Web Frontend Setup (React)

### 1. Navigate to Web App

```bash
cd web-frontend
```

### 2. Install Dependencies

```bash
npm install
```

### 3. Start React App

```bash
npm start
```

Runs at:

```
http://localhost:3000/
```

---

## Desktop App Setup (PyQt5)

### 1. Navigate to Desktop Folder

```bash
cd desktop-app
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run Application

```bash
python main.py
```

---
## Testing the Application

1. Use provided sample CSV
2. Upload via Web or Desktop
3. Verify:

   * Table rendering
   * Chart visualization
   * Summary statistics
   * Dataset history

---

## Credits

Created by Ayushi Chauhan

---

## License

This project is for educational and evaluation purposes only.
