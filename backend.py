"""
backend.py
Core business logic for the Exam Seating Arrangement System.
Handles validation, capacity calculation, seat allocation, search, and statistics.
Designed to be clean, modular, and easy to understand for second-year IT students.
"""

from dataclasses import dataclass, asdict
from typing import List, Dict, Tuple, Optional
import pandas as pd

__all__ = [
    "Student",
    "SeatAssignment",
    "validate_single_student",
    "validate_student_list",
    "calculate_capacity",
    "allocate_seats",
    "search_students",
    "search_students_by_name",
    "search_students_by_roll",
    "search_student_seat",
    "get_sample_students",
    "convert_allocations_to_dataframe",
    "generate_printable_html",
]


@dataclass
class Student:
    """Represents a student taking the examination."""
    roll_no: str
    name: str

    def to_dict(self) -> Dict[str, str]:
        return {"roll_no": self.roll_no.strip(), "name": self.name.strip()}


@dataclass
class SeatAssignment:
    """Represents a single bench seat and its assigned student."""
    classroom: str
    bench_number: int
    seat_number: int
    roll_no: str
    student_name: str
    status: str  # 'Occupied' or 'Vacant'

    def to_dict(self) -> Dict[str, any]:
        return asdict(self)


def validate_single_student(
    roll_no: str,
    name: str,
    existing_students: Optional[List[Dict[str, str]]] = None
) -> Tuple[bool, str]:
    """
    Validates a single student entry.
    Checks for:
    1. Empty or whitespace-only name
    2. Empty or whitespace-only roll number
    3. Duplicate roll number in the existing student list (case-insensitive)
    
    Returns:
        (is_valid: bool, error_message: str)
    """
    cleaned_roll = (roll_no or "").strip()
    cleaned_name = (name or "").strip()

    if not cleaned_roll:
        return False, "Roll number cannot be empty."

    if not cleaned_name:
        return False, "Student name cannot be empty."

    # Check for duplicate roll numbers
    if existing_students:
        existing_rolls = {
            s.get("roll_no", "").strip().upper() for s in existing_students
        }
        if cleaned_roll.upper() in existing_rolls:
            return False, f"Duplicate roll number '{cleaned_roll}'. Each student must have a unique roll number."

    return True, ""


def validate_student_list(students: List[Dict[str, str]]) -> Tuple[bool, List[str]]:
    """
    Validates a batch of students (e.g. from file upload or sample data).
    Checks for missing fields and duplicates within the list.
    
    Returns:
        (is_valid: bool, list_of_errors: List[str])
    """
    errors = []
    seen_rolls = set()

    if not students:
        return False, ["Student list is empty. Please add at least one student."]

    for idx, student in enumerate(students, start=1):
        roll = str(student.get("roll_no", "")).strip()
        name = str(student.get("name", "")).strip()

        if not roll:
            errors.append(f"Row {idx}: Roll number is missing or empty.")
        if not name:
            errors.append(f"Row {idx}: Student name is missing or empty.")

        if roll:
            upper_roll = roll.upper()
            if upper_roll in seen_rolls:
                errors.append(f"Row {idx}: Duplicate roll number '{roll}' detected.")
            else:
                seen_rolls.add(upper_roll)

    return (len(errors) == 0), errors


def calculate_capacity(
    num_classrooms: int,
    benches_per_room: int,
    seats_per_bench: int
) -> int:
    """
    Calculates total seating capacity.
    Formula: classrooms * benches_per_room * seats_per_bench
    """
    if num_classrooms <= 0 or benches_per_room <= 0 or seats_per_bench <= 0:
        return 0
    return num_classrooms * benches_per_room * seats_per_bench


def allocate_seats(
    students: List[Dict[str, str]],
    num_classrooms: int,
    benches_per_room: int,
    seats_per_bench: int,
    classroom_prefix: str = "Room "
) -> Tuple[bool, str, int, List[Dict[str, any]], Dict[str, any]]:
    """
    Automatically assigns students to seats in classroom, bench, and seat order.
    
    Rule 1: Never allocate more students than available capacity.
    Rule 2: If insufficient capacity, report an error with exact shortfall.
    Rule 3: Seats are assigned sequentially (Classroom 1 -> Bench 1 -> Seat 1, Seat 2...).
    
    Returns:
        success: bool
        message: str
        seats_shortfall: int (0 if sufficient)
        allocations: List[Dict] (empty if capacity insufficient)
        statistics: Dict
    """
    # Basic input checks
    if num_classrooms <= 0 or benches_per_room <= 0 or seats_per_bench <= 0:
        return False, "Room count, benches per room, and seats per bench must all be greater than zero.", 0, [], {}

    total_capacity = calculate_capacity(num_classrooms, benches_per_room, seats_per_bench)
    total_students = len(students)

    # Check capacity constraints
    if total_students > total_capacity:
        shortfall = total_students - total_capacity
        error_msg = (
            f"Insufficient seating capacity! "
            f"Total available capacity is {total_capacity} seats, but {total_students} students need to be seated. "
            f"You need at least {shortfall} more seat{'s' if shortfall > 1 else ''}."
        )
        stats = {
            "total_students": total_students,
            "total_capacity": total_capacity,
            "occupied_seats": 0,
            "vacant_seats": total_capacity,
            "utilization_percentage": 0.0,
            "shortfall": shortfall
        }
        return False, error_msg, shortfall, [], stats

    # Allocation process
    allocations: List[Dict[str, any]] = []
    student_index = 0

    for room_idx in range(1, num_classrooms + 1):
        classroom_name = f"{classroom_prefix}{100 + room_idx}"

        for bench_idx in range(1, benches_per_room + 1):
            for seat_idx in range(1, seats_per_bench + 1):
                if student_index < total_students:
                    current_student = students[student_index]
                    assignment = SeatAssignment(
                        classroom=classroom_name,
                        bench_number=bench_idx,
                        seat_number=seat_idx,
                        roll_no=str(current_student.get("roll_no", "")).strip(),
                        student_name=str(current_student.get("name", "")).strip(),
                        status="Occupied"
                    )
                    student_index += 1
                else:
                    # Seat exists in the room but has no student assigned
                    assignment = SeatAssignment(
                        classroom=classroom_name,
                        bench_number=bench_idx,
                        seat_number=seat_idx,
                        roll_no="-",
                        student_name="[Vacant]",
                        status="Vacant"
                    )
                allocations.append(assignment.to_dict())

    # Calculate overall statistics
    occupied_count = total_students
    vacant_count = total_capacity - occupied_count
    utilization = (occupied_count / total_capacity * 100) if total_capacity > 0 else 0.0

    # Classroom-wise breakdown
    room_summary = []
    for room_idx in range(1, num_classrooms + 1):
        room_name = f"{classroom_prefix}{100 + room_idx}"
        room_allocs = [a for a in allocations if a["classroom"] == room_name]
        room_occ = sum(1 for a in room_allocs if a["status"] == "Occupied")
        room_cap = benches_per_room * seats_per_bench
        room_vac = room_cap - room_occ
        room_summary.append({
            "classroom": room_name,
            "capacity": room_cap,
            "occupied": room_occ,
            "vacant": room_vac,
            "utilization": round((room_occ / room_cap * 100), 1) if room_cap > 0 else 0
        })

    stats = {
        "total_students": total_students,
        "total_capacity": total_capacity,
        "occupied_seats": occupied_count,
        "vacant_seats": vacant_count,
        "utilization_percentage": round(utilization, 1),
        "shortfall": 0,
        "room_summary": room_summary
    }

    success_msg = f"Successfully arranged {occupied_count} students across {num_classrooms} classroom(s)."
    return True, success_msg, 0, allocations, stats


def search_students_by_roll(
    allocations: List[Dict[str, any]],
    search_roll: str
) -> List[Dict[str, any]]:
    """
    Searches for students by roll number within the allocated seating list.
    Supports exact match first; if not exact, supports partial match.
    Matching is case-insensitive and ignores extra whitespace.
    
    Returns:
        List of matching allocation dicts for occupied seats.
    """
    if not search_roll:
        return []

    target = search_roll.strip().upper()
    if not target:
        return []

    # Priority 1: Exact roll number match
    exact_matches = [
        item for item in allocations
        if item.get("status") == "Occupied" and str(item.get("roll_no", "")).strip().upper() == target
    ]
    if exact_matches:
        return exact_matches

    # Priority 2: Partial roll number match (e.g. searching "105" matches "22IT105")
    partial_matches = [
        item for item in allocations
        if item.get("status") == "Occupied" and target in str(item.get("roll_no", "")).strip().upper()
    ]
    return partial_matches


def search_student_seat(
    allocations: List[Dict[str, any]],
    search_roll_no: str
) -> Optional[Dict[str, any]]:
    """
    Searches for a student by roll number within the allocated seating list.
    Maintained for direct single-result lookup and backward compatibility.
    
    Returns:
        Allocation dict if found and occupied, else None.
    """
    matches = search_students_by_roll(allocations, search_roll_no)
    return matches[0] if matches else None


def search_students_by_name(
    allocations: List[Dict[str, any]],
    search_name: str
) -> List[Dict[str, any]]:
    """
    Searches for students by student name within the allocated seating list.
    Supports partial-name matching, is case-insensitive, and ignores leading/trailing spaces.
    
    Returns:
        List of matching allocation dicts (all occupied seats whose student_name contains search_name).
    """
    if not search_name:
        return []

    target = search_name.strip().lower()
    if not target:
        return []

    matches = []
    for item in allocations:
        if item.get("status") == "Occupied":
            current_name = str(item.get("student_name", "")).strip().lower()
            if target in current_name:
                matches.append(item)

    return matches


def search_students(
    allocations: List[Dict[str, any]],
    query: str,
    search_by: str = "Roll Number"
) -> List[Dict[str, any]]:
    """
    Unified search function supporting both Roll Number and Student Name modes.
    
    Parameters:
        allocations: List of seat allocation dictionaries
        query: Search string (roll number or name/partial name)
        search_by: "Roll Number" or "Student Name"
        
    Returns:
        List of matching allocation dictionaries.
    """
    if not query or not query.strip():
        return []

    # Case-insensitive mode detection
    mode = str(search_by).strip().lower()
    if "name" in mode:
        return search_students_by_name(allocations, query)
    else:
        return search_students_by_roll(allocations, query)


def get_sample_students() -> List[Dict[str, str]]:
    """
    Returns a sample list of 24 college students for instant demo and testing.
    """
    return [
        {"roll_no": "22IT101", "name": "Aarav Sharma"},
        {"roll_no": "22IT102", "name": "Aditi Patel"},
        {"roll_no": "22IT103", "name": "Ananya Verma"},
        {"roll_no": "22IT104", "name": "Arjun Rao"},
        {"roll_no": "22IT105", "name": "Bhavya Nair"},
        {"roll_no": "22IT106", "name": "Chetan Reddy"},
        {"roll_no": "22IT107", "name": "Deepika Iyer"},
        {"roll_no": "22IT108", "name": "Devansh Gupta"},
        {"roll_no": "22IT109", "name": "Esha Kulkarni"},
        {"roll_no": "22IT110", "name": "Farhan Khan"},
        {"roll_no": "22IT111", "name": "Gaurav Joshi"},
        {"roll_no": "22IT112", "name": "Ishita Saxena"},
        {"roll_no": "22IT113", "name": "Karan Malhotra"},
        {"roll_no": "22IT114", "name": "Meera Nambiar"},
        {"roll_no": "22IT115", "name": "Nikhil Deshmukh"},
        {"roll_no": "22IT116", "name": "Pooja Hegde"},
        {"roll_no": "22IT117", "name": "Pranav Bansal"},
        {"roll_no": "22IT118", "name": "Rohan Bhatia"},
        {"roll_no": "22IT119", "name": "Sanya Chopra"},
        {"roll_no": "22IT120", "name": "Siddharth Jain"},
        {"roll_no": "22IT121", "name": "Tanvi Menon"},
        {"roll_no": "22IT122", "name": "Varun Sengupta"},
        {"roll_no": "22IT123", "name": "Vidya Pillai"},
        {"roll_no": "22IT124", "name": "Yash Vardhan"},
    ]


def convert_allocations_to_dataframe(
    allocations: List[Dict[str, any]],
    include_vacant: bool = True
) -> pd.DataFrame:
    """
    Converts seating allocation list into a clean Pandas DataFrame.
    """
    if not allocations:
        return pd.DataFrame(columns=[
            "Classroom", "Bench Number", "Seat Number", "Roll Number", "Student Name", "Status"
        ])

    data = allocations if include_vacant else [a for a in allocations if a["status"] == "Occupied"]

    df = pd.DataFrame(data)
    rename_map = {
        "classroom": "Classroom",
        "bench_number": "Bench Number",
        "seat_number": "Seat Number",
        "roll_no": "Roll Number",
        "student_name": "Student Name",
        "status": "Status"
    }
    df = df.rename(columns=rename_map)
    return df[["Classroom", "Bench Number", "Seat Number", "Roll Number", "Student Name", "Status"]]


def generate_printable_html(
    allocations: List[Dict[str, any]],
    stats: Dict[str, any],
    exam_title: str = "Semester Examination Seating Plan"
) -> str:
    """
    Generates a clean, professional HTML document suitable for browser printing or saving as PDF.
    Includes print CSS styles to hide screen buttons and format headers cleanly.
    """
    occupied_allocs = [a for a in allocations if a["status"] == "Occupied"]
    
    # Group by classroom
    rooms = sorted(list({a["classroom"] for a in allocations}))

    rows_html = ""
    for room in rooms:
        room_seats = [a for a in allocations if a["classroom"] == room]
        rows_html += f"""
        <div class="room-section">
            <h2 class="room-heading">🏛️ {room} (Total: {len(room_seats)} Seats | Occupied: {sum(1 for a in room_seats if a['status'] == 'Occupied')})</h2>
            <table class="print-table">
                <thead>
                    <tr>
                        <th style="width: 15%;">Bench No.</th>
                        <th style="width: 15%;">Seat No.</th>
                        <th style="width: 25%;">Roll Number</th>
                        <th style="width: 30%;">Student Name</th>
                        <th style="width: 15%;">Status</th>
                    </tr>
                </thead>
                <tbody>
        """
        for s in room_seats:
            is_occ = s["status"] == "Occupied"
            status_badge = f'<span class="badge badge-occ">Occupied</span>' if is_occ else f'<span class="badge badge-vac">Vacant</span>'
            row_style = "" if is_occ else 'style="color: #888;"'
            rows_html += f"""
                    <tr {row_style}>
                        <td style="font-weight: bold;">Bench {s['bench_number']}</td>
                        <td>Seat {s['seat_number']}</td>
                        <td><strong>{s['roll_no']}</strong></td>
                        <td>{s['student_name']}</td>
                        <td>{status_badge}</td>
                    </tr>
            """
        rows_html += """
                </tbody>
            </table>
        </div>
        """

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>{exam_title}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 20px;
            color: #222;
            background-color: #fff;
        }}
        .header {{
            text-align: center;
            border-bottom: 2px solid #2563eb;
            padding-bottom: 12px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
            color: #1e3a8a;
            font-size: 24px;
        }}
        .header p {{
            margin: 4px 0;
            color: #555;
            font-size: 14px;
        }}
        .stats-summary {{
            display: flex;
            justify-content: space-around;
            background: #f1f5f9;
            border-radius: 8px;
            padding: 12px;
            margin-bottom: 25px;
            border: 1px solid #cbd5e1;
        }}
        .stat-item {{
            text-align: center;
        }}
        .stat-value {{
            font-size: 20px;
            font-weight: bold;
            color: #1e3a8a;
        }}
        .stat-label {{
            font-size: 12px;
            color: #64748b;
            text-transform: uppercase;
        }}
        .room-section {{
            margin-bottom: 30px;
            page-break-inside: avoid;
        }}
        .room-heading {{
            font-size: 18px;
            color: #1e40af;
            border-left: 4px solid #2563eb;
            padding-left: 8px;
            margin-bottom: 10px;
        }}
        .print-table {{
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
            font-size: 13px;
        }}
        .print-table th, .print-table td {{
            border: 1px solid #e2e8f0;
            padding: 8px 12px;
            text-align: left;
        }}
        .print-table th {{
            background-color: #f8fafc;
            color: #334155;
            font-weight: 600;
        }}
        .print-table tr:nth-child(even) {{
            background-color: #fcfcfd;
        }}
        .badge {{
            display: inline-block;
            padding: 2px 8px;
            border-radius: 4px;
            font-size: 11px;
            font-weight: bold;
        }}
        .badge-occ {{
            background-color: #dbeafe;
            color: #1e40af;
        }}
        .badge-vac {{
            background-color: #f1f5f9;
            color: #64748b;
        }}
        .no-print {{
            text-align: center;
            margin-bottom: 20px;
        }}
        .print-btn {{
            background-color: #2563eb;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 6px;
            font-size: 14px;
            font-weight: bold;
            cursor: pointer;
        }}
        .print-btn:hover {{
            background-color: #1d4ed8;
        }}
        @media print {{
            .no-print {{
                display: none !important;
            }}
            body {{
                margin: 0;
            }}
            .room-section {{
                page-break-after: auto;
            }}
        }}
    </style>
</head>
<body>
    <div class="no-print">
        <button class="print-btn" onclick="window.print()">🖨️ Print / Save as PDF</button>
    </div>

    <div class="header">
        <h1>{exam_title}</h1>
        <p>Information Technology Department • Examination Seating Arrangement</p>
    </div>

    <div class="stats-summary">
        <div class="stat-item">
            <div class="stat-value">{stats.get('total_students', 0)}</div>
            <div class="stat-label">Total Students</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{stats.get('total_capacity', 0)}</div>
            <div class="stat-label">Total Capacity</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{stats.get('occupied_seats', 0)}</div>
            <div class="stat-label">Occupied Seats</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{stats.get('vacant_seats', 0)}</div>
            <div class="stat-label">Vacant Seats</div>
        </div>
        <div class="stat-item">
            <div class="stat-value">{stats.get('utilization_percentage', 0)}%</div>
            <div class="stat-label">Seat Utilization</div>
        </div>
    </div>

    {rows_html}

    <div style="margin-top: 30px; border-top: 1px dashed #cbd5e1; padding-top: 15px; display: flex; justify-content: space-between; font-size: 12px; color: #64748b;">
        <span>Generated by Exam Seating Arrangement System</span>
        <span>Signature of Chief Superintendent: _______________________</span>
    </div>
</body>
</html>
"""
    return html
