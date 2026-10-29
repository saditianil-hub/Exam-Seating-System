# 📝 Exam Seating Arrangement System

A clean, modern, and user-friendly web application built with **Python** and **Streamlit** to automate the process of arranging student seating for college and university examinations.

Designed as an academic mini-project for **Second-Year B.Tech Information Technology** students.

---

## 🌟 Key Features

1. **Student Registration & Validation**:
   - Single student manual entry with name and roll number.
   - Bulk student import via CSV file upload with a downloadable template.
   - 1-click **⚡ Quick Sample Data** loader (loads 24 realistic student records for fast testing and viva demos).
   - Strict validation preventing empty fields, whitespace inputs, and duplicate roll numbers.

2. **Hall & Seating Configuration**:
   - Configure the number of **Classrooms**, **Benches per Classroom**, and **Seats per Bench**.
   - Real-time seating capacity computation (\(\text{Rooms} \times \text{Benches} \times \text{Seats}\)).

3. **Intelligent Seat Allocation Algorithm**:
   - Assigns students systematically in classroom, bench, and seat order.
   - **Capacity Safeguard**: Never assigns more students than available capacity.
   - **Accurate Shortfall Warning**: If seats are insufficient, displays a clear error indicating the exact number of extra seats required and suggests fixes.

4. **Classroom-Wise Layout & Seating Roster**:
   - **Physical Bench View**: Visual card-based representation of each bench (e.g., Seat 1, Seat 2, Seat 3) with color-coded occupied and vacant statuses.
   - **Tabular Roster View**: Clean, searchable data table displaying Classroom, Bench, Seat, Roll Number, Student Name, and Status.

5. **Dual-Mode Student Search**:
   - **Search by Roll Number**: Case-insensitive and whitespace-trimmed search to find the exact student.
   - **Search by Student Name**: Case-insensitive partial-name match (e.g. searching "Aditi" matches "Aditi Patel" or "Aditi Sharma").
   - **Multi-Match Display**: If multiple students match a name search, all matching students are displayed alongside their classroom, bench, seat number, name, and roll number.
   - Clear warning message if no match is found.

6. **Comprehensive Examination Statistics**:
   - Dashboard metric cards: Total Students, Total Capacity, Occupied Seats, Vacant Seats, and Hall Utilization Percentage.
   - Per-classroom capacity and occupancy breakdown table.

7. **Export & Print Ready**:
   - Download the full seating arrangement as a `.csv` spreadsheet for Excel or Google Sheets.
   - Built-in **Print-Ready Examination Chart** with department header, room tables, invigilator signature area, and a 1-click browser print / Save as PDF button.

---

## 📁 Project Structure

```text
ExamSeatingSystem/
│
├── app.py              # Streamlit web user interface, dashboard, and visual components
├── backend.py          # Core logic: capacity calculation, allocation algorithm, search, validation, and export
├── requirements.txt    # Project dependencies (streamlit, pandas)
└── README.md           # Documentation, setup guide, and viva preparation
```

---

## ⚙️ Installation and Setup on Windows

Follow these steps to run the application on your Windows machine using PowerShell or Command Prompt.

### Step 1: Open Terminal in the Project Directory
Open **PowerShell** or **Command Prompt** and navigate to your project directory:
```powershell
cd c:\Users\Anil\OneDrive\Documents\ExamSeatingSystem
```

### Step 2: (Optional but Recommended) Create a Virtual Environment
```powershell
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
Install the required packages using `pip`:
```powershell
python -m pip install -r requirements.txt
```

### Step 4: Run the Streamlit Application
Start the Streamlit development server:
```powershell
streamlit run app.py
```

### Step 5: Open in Your Browser
Once started, Streamlit will display local URLs. Open your browser and visit:
```text
http://localhost:8501
```

---

## 🧪 Demonstration & Test Scenarios

### Scenario 1: Quick 1-Click Demo
1. In the sidebar, set:
   - **Classrooms**: `2`
   - **Benches / Room**: `4`
   - **Seats per Bench**: `3`
   *(Total Capacity = 2 × 4 × 3 = 24 seats)*
2. In **Student Registration**, select **⚡ Quick Sample Data** and click **📥 Load Sample**. (Loads 24 students).
3. Click **🚀 Generate Seating Arrangement**.
4. Explore the **Classroom Seating Plan** tab to see physical benches and the **Detailed Statistics** tab.

### Scenario 2: Insufficient Capacity Handling
1. Change **Classrooms** to `1` and **Benches / Room** to `3` with `2` seats per bench *(Total Capacity = 6 seats)*.
2. Attempt to generate seating for 24 students.
3. Observe the system halt allocation and display:
   > ❌ **Insufficient seating capacity!** Total available capacity is 6 seats, but 24 students need to be seated. You need at least 18 more seats.

### Scenario 3: Student Search (Roll Number & Name)
1. With students allocated, switch to the **🔍 Search Student Seat** tab.
2. Select **Roll Number** mode and search `22IT105`.
   - The system instantly returns `Bhavya Nair` in `Room 101`, `Bench 2`, `Seat 2`.
3. Select **Student Name** mode and search `Aditi` (or `Sharma`).
   - The system returns matching students with their full details. If multiple students match, each result card displays their name, roll number, classroom, bench, and seat number.

### Scenario 4: Export & Print
1. Switch to the **📥 Download & Print** tab.
2. Click **📥 Download Seating Arrangement (CSV)** to obtain the spreadsheet.
3. Click **🖨️ Download Printable Report (HTML)** or use the interactive print preview to print or save the roster as a PDF.

---

## 💡 Viva / Project Presentation Q&A

1. **Q: How does the seat allocation algorithm work?**
   - **A:** The algorithm operates sequentially. It calculates total capacity first. If capacity is sufficient, it iterates across each classroom, each bench within the room, and each seat on the bench, mapping registered students in order until all students are seated. Any remaining seats are marked as `Vacant`.

2. **Q: How are edge cases and errors handled?**
   - **A:** The system enforces strict input validation:
     - Rejects empty strings and whitespace-only entries.
     - Prevents duplicate student roll numbers using hash set lookups.
     - Rejects non-positive room or bench dimensions.
     - Strictly halts allocation if student count exceeds capacity, calculating and displaying the exact shortfall.

3. **Q: Why separate `app.py` and `backend.py`?**
   - **A:** This follows the **Separation of Concerns (SoC)** architectural pattern. `backend.py` contains pure Python business logic and data structures without UI dependencies, making the code testable and maintainable. `app.py` focuses purely on rendering the user interface and handling session state.

---

## 👨‍💻 Author
- **Academic Stream:** B.Tech Information Technology (Second Year)
- **Project:** Exam Seating Arrangement System
