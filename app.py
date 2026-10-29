"""
app.py
Exam Seating Arrangement System - Streamlit Web Application
Second-Year B.Tech Information Technology Project

This application provides an interactive, beautiful interface for:
1. Adding and managing student records (Single, Bulk CSV, or Sample data).
2. Configuring classroom seating parameters (Classrooms, Benches, Seats per bench).
3. Automatically allocating seats with capacity validation.
4. Visualizing physical bench layouts and full tabular reports.
5. Searching assigned seats by Student Roll Number.
6. Exporting to CSV and generating print-friendly examination reports.
"""

import importlib
import streamlit as st
import pandas as pd
import backend

# Ensure backend module updates reload live without requiring a server restart
try:
    importlib.reload(backend)
except Exception:
    pass

# ---------------------------------------------------------
# Streamlit Page Configuration
# ---------------------------------------------------------
st.set_page_config(
    page_title="Exam Seating Arrangement System",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# Custom CSS for Modern, College-Project Presentation
# ---------------------------------------------------------
st.markdown("""
<style>
    /* Main container styling */
    .main-header {
        background: linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%);
        color: white;
        padding: 22px 28px;
        border-radius: 12px;
        margin-bottom: 24px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        margin: 0;
        font-size: 28px;
        font-weight: 700;
        color: #ffffff;
    }
    .main-header p {
        margin: 6px 0 0 0;
        font-size: 14px;
        color: #e0e7ff;
    }
    .badge {
        display: inline-block;
        background-color: rgba(255, 255, 255, 0.2);
        padding: 3px 10px;
        border-radius: 9999px;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
    }
    /* Bench visual cards */
    .bench-card {
        background-color: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        margin-bottom: 12px;
        transition: all 0.2s ease;
    }
    .bench-card:hover {
        border-color: #3b82f6;
        box-shadow: 0 2px 4px rgba(59, 130, 246, 0.1);
    }
    .seat-badge {
        display: inline-block;
        padding: 6px 10px;
        border-radius: 6px;
        margin: 4px 2px;
        font-size: 13px;
    }
    .seat-occupied {
        background-color: #dbeafe;
        color: #1e40af;
        border: 1px solid #bfdbfe;
    }
    .seat-vacant {
        background-color: #f1f5f9;
        color: #94a3b8;
        border: 1px dashed #cbd5e1;
    }
    /* Search Result Card */
    .search-card {
        background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%);
        border: 1px solid #86efac;
        border-radius: 10px;
        padding: 18px;
        margin-top: 10px;
        margin-bottom: 12px;
    }
</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Session State Initialization
# ---------------------------------------------------------
if "students" not in st.session_state:
    st.session_state.students = []

if "allocations" not in st.session_state:
    st.session_state.allocations = []

if "stats" not in st.session_state:
    st.session_state.stats = {}

if "allocation_done" not in st.session_state:
    st.session_state.allocation_done = False

if "last_error" not in st.session_state:
    st.session_state.last_error = ""


# ---------------------------------------------------------
# Header Section
# ---------------------------------------------------------
st.markdown("""
<div class="main-header">
    <span class="badge">🎓 B.Tech IT Mini Project</span>
    <h1>Exam Seating Arrangement System</h1>
    <p>Automated, capacity-checked examination hall seat allocation and desk mapping system</p>
</div>
""", unsafe_allow_html=True)


# ---------------------------------------------------------
# Sidebar: Hall Configuration & Student Management
# ---------------------------------------------------------
with st.sidebar:
    st.header("⚙️ Hall Configuration")
    st.caption("Define the examination venue parameters:")

    col_c1, col_c2 = st.columns(2)
    with col_c1:
        num_classrooms = st.number_input("Classrooms", min_value=1, max_value=20, value=2, step=1, help="Total number of exam halls/rooms")
    with col_c2:
        benches_per_room = st.number_input("Benches / Room", min_value=1, max_value=50, value=4, step=1, help="Number of benches in each classroom")

    seats_per_bench = st.number_input("Seats per Bench", min_value=1, max_value=4, value=3, step=1, help="Number of students per bench (e.g. 2 or 3)")

    # Live calculated total capacity
    current_capacity = backend.calculate_capacity(num_classrooms, benches_per_room, seats_per_bench)
    st.info(f"📐 **Total Seating Capacity:** **{current_capacity}** seats\n\n({num_classrooms} rooms × {benches_per_room} benches × {seats_per_bench} seats)")

    st.divider()

    # -----------------------------------------------------
    # Student Data Input
    # -----------------------------------------------------
    st.header("👥 Student Registration")
    
    input_mode = st.radio(
        "Choose Entry Method:",
        ["➕ Single Entry", "📁 CSV Upload", "⚡ Quick Sample Data"],
        index=0
    )

    if input_mode == "➕ Single Entry":
        with st.form("single_student_form", clear_on_submit=True):
            new_roll = st.text_input("Roll Number", placeholder="e.g. 22IT101")
            new_name = st.text_input("Student Name", placeholder="e.g. Aarav Sharma")
            submitted = st.form_submit_button("Add Student", use_container_width=True)

            if submitted:
                is_valid, err_msg = backend.validate_single_student(
                    new_roll, new_name, st.session_state.students
                )
                if not is_valid:
                    st.error(f"⚠️ {err_msg}")
                else:
                    st.session_state.students.append({
                        "roll_no": new_roll.strip(),
                        "name": new_name.strip()
                    })
                    st.success(f"Added {new_name.strip()} ({new_roll.strip()})")

    elif input_mode == "📁 CSV Upload":
        st.caption("Upload a CSV file with columns: `roll_no`, `name`")
        
        # Downloadable sample CSV template
        sample_template_df = pd.DataFrame([
            {"roll_no": "22IT101", "name": "Aarav Sharma"},
            {"roll_no": "22IT102", "name": "Aditi Patel"}
        ])
        template_csv = sample_template_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📄 Download CSV Template",
            data=template_csv,
            file_name="student_template.csv",
            mime="text/csv",
            use_container_width=True
        )

        uploaded_file = st.file_uploader("Upload CSV", type=["csv"])
        if uploaded_file is not None:
            try:
                df_uploaded = pd.read_csv(uploaded_file)
                # Standardize column names
                col_map = {}
                for col in df_uploaded.columns:
                    c_clean = col.strip().lower().replace(" ", "_")
                    if c_clean in ["roll", "roll_no", "roll_number", "rollno", "id"]:
                        col_map[col] = "roll_no"
                    elif c_clean in ["name", "student_name", "fullname"]:
                        col_map[col] = "name"
                
                df_uploaded = df_uploaded.rename(columns=col_map)
                
                if "roll_no" in df_uploaded.columns and "name" in df_uploaded.columns:
                    raw_records = df_uploaded[["roll_no", "name"]].dropna().to_dict(orient="records")
                    is_valid, validation_errors = backend.validate_student_list(raw_records)
                    
                    if not is_valid:
                        st.error("Validation failed in uploaded CSV:")
                        for err in validation_errors[:5]:
                            st.write(f"- {err}")
                        if len(validation_errors) > 5:
                            st.write(f"... and {len(validation_errors) - 5} more errors.")
                    else:
                        if st.button("Import Students from CSV", use_container_width=True):
                            st.session_state.students = raw_records
                            st.session_state.allocation_done = False
                            st.success(f"Successfully imported {len(raw_records)} students!")
                else:
                    st.error("Uploaded CSV must contain 'roll_no' and 'name' columns.")
            except Exception as e:
                st.error(f"Error parsing CSV: {e}")

    elif input_mode == "⚡ Quick Sample Data":
        st.caption("Load pre-configured 24 student records for testing.")
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            if st.button("📥 Load Sample", use_container_width=True):
                st.session_state.students = backend.get_sample_students()
                st.session_state.allocation_done = False
                st.session_state.last_error = ""
                st.success(f"Loaded {len(st.session_state.students)} sample students!")
        with col_s2:
            if st.button("🗑️ Clear All", use_container_width=True):
                st.session_state.students = []
                st.session_state.allocations = []
                st.session_state.stats = {}
                st.session_state.allocation_done = False
                st.session_state.last_error = ""
                st.info("Cleared student list.")

    st.divider()

    # -----------------------------------------------------
    # Registered Students Summary
    # -----------------------------------------------------
    st.subheader(f"📋 Registered: {len(st.session_state.students)} Students")
    if st.session_state.students:
        with st.expander("View / Edit Registered Students", expanded=False):
            df_preview = pd.DataFrame(st.session_state.students)
            df_preview.index = df_preview.index + 1
            st.dataframe(df_preview, use_container_width=True, height=200)

            # Option to remove a specific student
            roll_to_delete = st.selectbox(
                "Select student to remove:",
                options=[s["roll_no"] for s in st.session_state.students],
                key="del_roll"
            )
            if st.button("Remove Selected Student"):
                st.session_state.students = [
                    s for s in st.session_state.students if s["roll_no"] != roll_to_delete
                ]
                st.session_state.allocation_done = False
                st.rerun()

    # -----------------------------------------------------
    # Generate Allocation Button
    # -----------------------------------------------------
    st.markdown("### 🚀 Run Allocation")
    if st.button("Generate Seating Arrangement", type="primary", use_container_width=True):
        if not st.session_state.students:
            st.error("Please add at least one student before allocating seats.")
        else:
            success, msg, shortfall, allocations, stats = backend.allocate_seats(
                students=st.session_state.students,
                num_classrooms=int(num_classrooms),
                benches_per_room=int(benches_per_room),
                seats_per_bench=int(seats_per_bench)
            )

            if not success:
                st.session_state.allocation_done = False
                st.session_state.last_error = msg
                st.session_state.stats = stats
                st.session_state.allocations = []
            else:
                st.session_state.allocation_done = True
                st.session_state.last_error = ""
                st.session_state.allocations = allocations
                st.session_state.stats = stats
                st.session_state.config = {
                    "num_classrooms": num_classrooms,
                    "benches_per_room": benches_per_room,
                    "seats_per_bench": seats_per_bench
                }


# ---------------------------------------------------------
# Main Body: Statistics, Error Handling, and Arrangements
# ---------------------------------------------------------

# Display Insufficient Capacity Error if any
if st.session_state.last_error:
    st.error(st.session_state.last_error)
    stats = st.session_state.stats
    shortfall = stats.get("shortfall", 0)
    
    st.warning(
        f"💡 **Suggested Fix:**\n\n"
        f"- Current Capacity: **{stats.get('total_capacity', 0)}** seats\n"
        f"- Students to be seated: **{stats.get('total_students', 0)}**\n"
        f"- **Additional seats required: {shortfall}**\n\n"
        f"👉 Increase the **Benches per Room**, add **Classrooms**, or increase **Seats per Bench** in the sidebar."
    )


# Show Dashboard Metrics if we have students or allocation
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)

total_stud = len(st.session_state.students)
cap = current_capacity
occ = st.session_state.stats.get("occupied_seats", 0) if st.session_state.allocation_done else 0
vac = (cap - total_stud) if total_stud <= cap else 0
util = st.session_state.stats.get("utilization_percentage", 0.0) if st.session_state.allocation_done else 0.0

with col_m1:
    st.metric(label="👥 Registered Students", value=total_stud)
with col_m2:
    st.metric(label="🪑 Total Hall Capacity", value=cap)
with col_m3:
    st.metric(label="✅ Allocated Seats", value=occ)
with col_m4:
    st.metric(label="🟢 Vacant Seats", value=vac)
with col_m5:
    st.metric(label="📊 Hall Utilization", value=f"{util}%")

st.divider()


# ---------------------------------------------------------
# Seating Arrangement Display Tabs
# ---------------------------------------------------------
if st.session_state.allocation_done and st.session_state.allocations:
    
    tab_plan, tab_search, tab_stats, tab_export = st.tabs([
        "🏛️ Classroom Seating Plan",
        "🔍 Search Student Seat",
        "📊 Detailed Statistics",
        "📥 Download & Print"
    ])

    # -----------------------------------------------------
    # TAB 1: Classroom Seating Plan
    # -----------------------------------------------------
    with tab_plan:
        st.subheader("Classroom Seating Arrangement")
        st.caption("Browse physical desk layouts or inspect full tabular seating rosters for each classroom.")

        rooms = sorted(list({a["classroom"] for a in st.session_state.allocations}))
        
        col_sel, col_mode = st.columns([2, 1])
        with col_sel:
            selected_room = st.selectbox("Select Classroom to View:", rooms)
        with col_mode:
            view_mode = st.radio("Display Style:", ["🪑 Physical Bench Layout", "📄 Tabular Roster"], horizontal=True)

        room_allocations = [a for a in st.session_state.allocations if a["classroom"] == selected_room]
        
        if view_mode == "🪑 Physical Bench Layout":
            # Group by bench number
            benches = sorted(list({a["bench_number"] for a in room_allocations}))
            
            st.markdown(f"#### 🚪 Front of Classroom ({selected_room}) - Blackboard / Podium")
            st.markdown("<hr style='border: 2px dashed #94a3b8; margin: 10px 0 20px 0;'>", unsafe_allow_html=True)
            
            # Display benches in 2 columns for a realistic room layout
            col_b1, col_b2 = st.columns(2)
            
            for idx, bench_no in enumerate(benches):
                bench_seats = [a for a in room_allocations if a["bench_number"] == bench_no]
                target_col = col_b1 if (idx % 2 == 0) else col_b2
                
                with target_col:
                    st.markdown(f"""
                    <div class="bench-card">
                        <div style="font-weight: 700; color: #1e3a8a; margin-bottom: 8px;">
                            🪑 Bench {bench_no}
                        </div>
                    """, unsafe_allow_html=True)
                    
                    for seat in bench_seats:
                        is_occ = seat["status"] == "Occupied"
                        cls_name = "seat-occupied" if is_occ else "seat-vacant"
                        icon = "👤" if is_occ else "⚪"
                        
                        st.markdown(f"""
                        <div class="seat-badge {cls_name}">
                            <strong>Seat {seat['seat_number']}:</strong> {icon} <b>{seat['roll_no']}</b> - {seat['student_name']}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    st.markdown("</div>", unsafe_allow_html=True)

        else:
            # Tabular Roster
            df_room = backend.convert_allocations_to_dataframe(room_allocations, include_vacant=True)
            st.dataframe(df_room, use_container_width=True, hide_index=True)

    # -----------------------------------------------------
    # TAB 2: Search Student Seat
    # -----------------------------------------------------
    with tab_search:
        st.subheader("🔍 Search Student Seat")
        st.caption("Locate any student's assigned classroom, bench, and seat by Roll Number or Student Name.")

        # Search Mode Selection
        search_mode = st.radio(
            "Select Search Mode:",
            ["Roll Number", "Student Name"],
            horizontal=True
        )

        if search_mode == "Roll Number":
            search_query = st.text_input(
                "Enter Roll Number:",
                placeholder="e.g. 22IT105",
                help="Type the student's roll number (case-insensitive)"
            )
        else:
            search_query = st.text_input(
                "Enter Student Name (or partial name):",
                placeholder="e.g. Aditi or Sharma",
                help="Type full or partial name (case-insensitive, e.g. 'Aditi')"
            )

        if search_query and search_query.strip():
            # Robust backend call with fallback
            if hasattr(backend, "search_students"):
                results = backend.search_students(
                    st.session_state.allocations,
                    query=search_query,
                    search_by=search_mode
                )
            elif search_mode == "Student Name" and hasattr(backend, "search_students_by_name"):
                results = backend.search_students_by_name(st.session_state.allocations, search_query)
            elif hasattr(backend, "search_students_by_roll"):
                results = backend.search_students_by_roll(st.session_state.allocations, search_query)
            elif hasattr(backend, "search_student_seat"):
                single_res = backend.search_student_seat(st.session_state.allocations, search_query)
                results = [single_res] if single_res else []
            else:
                results = []

            if results:
                count = len(results)
                match_label = "1 matching student" if count == 1 else f"{count} matching students"
                st.success(f"✅ Found {match_label} for '{search_query.strip()}':")

                if count == 1:
                    result = results[0]
                    st.markdown(f"""
                    <div class="search-card">
                        <h3 style="margin: 0 0 10px 0; color: #166534;">✅ Student Found!</h3>
                        <table style="width: 100%; font-size: 15px; color: #14532d;">
                            <tr><td style="width: 30%;"><b>Student Name:</b></td><td>{result['student_name']}</td></tr>
                            <tr><td><b>Roll Number:</b></td><td><code>{result['roll_no']}</code></td></tr>
                            <tr><td><b>Assigned Classroom:</b></td><td>🏛️ <b>{result['classroom']}</b></td></tr>
                            <tr><td><b>Bench Number:</b></td><td>🪑 <b>Bench {result['bench_number']}</b></td></tr>
                            <tr><td><b>Seat Number:</b></td><td>💺 <b>Seat {result['seat_number']}</b></td></tr>
                        </table>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    cols = st.columns(2)
                    for idx, result in enumerate(results):
                        with cols[idx % 2]:
                            st.markdown(f"""
                            <div class="search-card">
                                <h4 style="margin: 0 0 8px 0; color: #166534;">👤 {result['student_name']}</h4>
                                <table style="width: 100%; font-size: 14px; color: #14532d;">
                                    <tr><td style="width: 40%;"><b>Roll Number:</b></td><td><code>{result['roll_no']}</code></td></tr>
                                    <tr><td><b>Classroom:</b></td><td>🏛️ <b>{result['classroom']}</b></td></tr>
                                    <tr><td><b>Bench Number:</b></td><td>🪑 <b>Bench {result['bench_number']}</b></td></tr>
                                    <tr><td><b>Seat Number:</b></td><td>💺 <b>Seat {result['seat_number']}</b></td></tr>
                                </table>
                            </div>
                            """, unsafe_allow_html=True)
            else:
                if search_mode == "Roll Number":
                    st.warning(f"❌ No student found with Roll Number '{search_query.strip()}'. Please double-check the roll number.")
                else:
                    st.warning(f"❌ No student found matching name '{search_query.strip()}'. Please check the spelling or try a partial name.")

    # -----------------------------------------------------
    # TAB 3: Detailed Statistics
    # -----------------------------------------------------
    with tab_stats:
        st.subheader("📊 Examination Hall & Room Statistics")
        stats = st.session_state.stats

        col_st1, col_st2 = st.columns([1, 1])
        with col_st1:
            st.markdown("#### Overall Summary")
            summary_data = {
                "Metric": ["Total Registered Students", "Total Seating Capacity", "Occupied Seats", "Vacant Seats", "Hall Utilization"],
                "Value": [
                    f"{stats.get('total_students', 0)} students",
                    f"{stats.get('total_capacity', 0)} seats",
                    f"{stats.get('occupied_seats', 0)} seats",
                    f"{stats.get('vacant_seats', 0)} seats",
                    f"{stats.get('utilization_percentage', 0.0)}%"
                ]
            }
            st.table(pd.DataFrame(summary_data))

        with col_st2:
            st.markdown("#### Classroom Breakdown")
            room_summary = stats.get("room_summary", [])
            if room_summary:
                df_rooms = pd.DataFrame(room_summary)
                df_rooms.columns = ["Classroom", "Capacity", "Occupied", "Vacant", "Utilization (%)"]
                st.dataframe(df_rooms, use_container_width=True, hide_index=True)

    # -----------------------------------------------------
    # TAB 4: Download & Print
    # -----------------------------------------------------
    with tab_export:
        st.subheader("📥 Export & Print Arrangements")
        st.caption("Export the complete seating plan for notice boards, invigilators, and student records.")

        col_d1, col_d2 = st.columns(2)

        # 1. CSV Download
        with col_d1:
            st.markdown("#### 📄 CSV Roster Export")
            st.caption("Download the complete seating chart as a CSV file to open in Excel or Google Sheets.")
            
            df_full = backend.convert_allocations_to_dataframe(st.session_state.allocations, include_vacant=True)
            csv_data = df_full.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Download Seating Arrangement (CSV)",
                data=csv_data,
                file_name="exam_seating_arrangement.csv",
                mime="text/csv",
                type="primary",
                use_container_width=True
            )

        # 2. Print-Friendly HTML View & Download
        with col_d2:
            st.markdown("#### 🖨️ Print-Ready Examination Chart")
            st.caption("Professional, formatted print layout with invigilator signature line and room tables.")

            printable_html = backend.generate_printable_html(
                st.session_state.allocations,
                st.session_state.stats
            )

            st.download_button(
                label="🖨️ Download Printable Report (HTML)",
                data=printable_html.encode('utf-8'),
                file_name="exam_seating_report.html",
                mime="text/html",
                use_container_width=True
            )

        st.divider()
        st.markdown("#### 👁️ Print Preview")
        st.caption("You can print directly from the preview below or open the downloaded HTML file in your browser to print / save as PDF.")
        st.components.v1.html(printable_html, height=450, scrolling=True)

else:
    # Initial instructions when no allocation has been generated yet
    st.info(
        "👋 **Welcome to the Exam Seating Arrangement System!**\n\n"
        "To get started:\n"
        "1. Configure the **Classrooms**, **Benches per Room**, and **Seats per Bench** in the sidebar.\n"
        "2. Add student records via **Single Entry**, **CSV Upload**, or click **'⚡ Quick Sample Data'** -> **'📥 Load Sample'**.\n"
        "3. Click **'🚀 Generate Seating Arrangement'** to produce the seating plan."
    )
