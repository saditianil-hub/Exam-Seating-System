"""
test_backend.py
Comprehensive unit tests for backend.py in Exam Seating Arrangement System.
Validates:
1. Validation of empty names, empty roll numbers, and duplicate roll numbers.
2. Capacity calculation.
3. Seating allocation order and vacant seat handling.
4. Capacity shortfall calculation and error message formatting.
5. Student search by roll number (case-insensitive).
6. Statistics computation (total students, capacity, occupied, vacant, utilization).
7. DataFrame and HTML report generation.
"""

import unittest
import backend


class TestBackend(unittest.TestCase):

    def setUp(self):
        self.sample_students = backend.get_sample_students()

    def test_validation_single_student_valid(self):
        is_valid, msg = backend.validate_single_student("22IT999", "John Doe", self.sample_students)
        self.assertTrue(is_valid)
        self.assertEqual(msg, "")

    def test_validation_single_student_empty_roll(self):
        is_valid, msg = backend.validate_single_student("  ", "John Doe", self.sample_students)
        self.assertFalse(is_valid)
        self.assertIn("Roll number cannot be empty", msg)

    def test_validation_single_student_empty_name(self):
        is_valid, msg = backend.validate_single_student("22IT999", "   ", self.sample_students)
        self.assertFalse(is_valid)
        self.assertIn("Student name cannot be empty", msg)

    def test_validation_single_student_duplicate_roll(self):
        is_valid, msg = backend.validate_single_student("22IT101", "Different Name", self.sample_students)
        self.assertFalse(is_valid)
        self.assertIn("Duplicate roll number", msg)

    def test_validation_student_list_duplicates(self):
        records = [
            {"roll_no": "IT01", "name": "Alice"},
            {"roll_no": "IT02", "name": "Bob"},
            {"roll_no": "IT01", "name": "Duplicate Alice"}
        ]
        is_valid, errors = backend.validate_student_list(records)
        self.assertFalse(is_valid)
        self.assertTrue(any("Duplicate" in err for err in errors))

    def test_capacity_calculation(self):
        # 2 classrooms, 4 benches per classroom, 3 seats per bench = 24
        capacity = backend.calculate_capacity(2, 4, 3)
        self.assertEqual(capacity, 24)

        # Zero or negative handling
        self.assertEqual(backend.calculate_capacity(0, 5, 2), 0)
        self.assertEqual(backend.calculate_capacity(-1, 5, 2), 0)

    def test_allocation_success(self):
        # 24 students into 2 rooms, 4 benches, 3 seats = 24 seats (100% capacity)
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        self.assertTrue(success)
        self.assertEqual(shortfall, 0)
        self.assertEqual(len(allocs), 24)
        self.assertEqual(stats["occupied_seats"], 24)
        self.assertEqual(stats["vacant_seats"], 0)
        self.assertEqual(stats["utilization_percentage"], 100.0)

        # Verify sequential ordering:
        # First student in Room 101, Bench 1, Seat 1
        self.assertEqual(allocs[0]["classroom"], "Room 101")
        self.assertEqual(allocs[0]["bench_number"], 1)
        self.assertEqual(allocs[0]["seat_number"], 1)
        self.assertEqual(allocs[0]["roll_no"], self.sample_students[0]["roll_no"])

        # Second student in Room 101, Bench 1, Seat 2
        self.assertEqual(allocs[1]["bench_number"], 1)
        self.assertEqual(allocs[1]["seat_number"], 2)
        self.assertEqual(allocs[1]["roll_no"], self.sample_students[1]["roll_no"])

    def test_allocation_with_vacant_seats(self):
        # 10 students into 2 rooms, 3 benches, 2 seats = 12 capacity
        ten_students = self.sample_students[:10]
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=ten_students,
            num_classrooms=2,
            benches_per_room=3,
            seats_per_bench=2
        )
        self.assertTrue(success)
        self.assertEqual(len(allocs), 12)
        self.assertEqual(stats["occupied_seats"], 10)
        self.assertEqual(stats["vacant_seats"], 2)
        self.assertAlmostEqual(stats["utilization_percentage"], 83.3, places=1)

        # Last two seats should be vacant
        self.assertEqual(allocs[-1]["status"], "Vacant")
        self.assertEqual(allocs[-2]["status"], "Vacant")

    def test_allocation_insufficient_capacity_error(self):
        # 24 students into 1 room, 2 benches, 2 seats = 4 capacity
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=1,
            benches_per_room=2,
            seats_per_bench=2
        )
        self.assertFalse(success)
        self.assertEqual(shortfall, 20)  # 24 - 4 = 20
        self.assertIn("Insufficient seating capacity", msg)
        self.assertIn("at least 20 more seats", msg)
        self.assertEqual(allocs, [])

    def test_search_student_found(self):
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        result = backend.search_student_seat(allocs, "22IT105")
        self.assertIsNotNone(result)
        self.assertEqual(result["roll_no"], "22IT105")
        self.assertEqual(result["student_name"], "Bhavya Nair")
        self.assertEqual(result["classroom"], "Room 101")
        self.assertEqual(result["bench_number"], 2)
        self.assertEqual(result["seat_number"], 2)

    def test_search_student_case_insensitive(self):
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        result = backend.search_student_seat(allocs, "  22it105  ")
        self.assertIsNotNone(result)
        self.assertEqual(result["roll_no"], "22IT105")

    def test_search_student_not_found(self):
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        result = backend.search_student_seat(allocs, "NONEXISTENT")
        self.assertIsNone(result)

    def test_search_by_name_exact_and_partial(self):
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        # Partial match: "Aditi" matches "Aditi Patel"
        results = backend.search_students_by_name(allocs, "Aditi")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["student_name"], "Aditi Patel")
        self.assertEqual(results[0]["roll_no"], "22IT102")
        self.assertEqual(results[0]["classroom"], "Room 101")
        self.assertEqual(results[0]["bench_number"], 1)
        self.assertEqual(results[0]["seat_number"], 2)

    def test_search_by_name_case_insensitive_and_whitespace(self):
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        # Lowercase with leading and trailing spaces
        results = backend.search_students_by_name(allocs, "   aDiTi   ")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["student_name"], "Aditi Patel")

    def test_search_by_name_multiple_matches(self):
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        # "Sharma" only matches Aarav Sharma
        results_sharma = backend.search_students_by_name(allocs, "sharma")
        self.assertEqual(len(results_sharma), 1)

        # "a" appears in multiple student names
        results_multi = backend.search_students_by_name(allocs, "ar")
        # e.g., Aarav Sharma, Arjun Rao, Farhan Khan, Karan Malhotra, Varun Sengupta, Yash Vardhan
        self.assertGreater(len(results_multi), 1)
        for r in results_multi:
            self.assertEqual(r["status"], "Occupied")
            self.assertIn("ar", r["student_name"].lower())

    def test_search_by_name_not_found_and_empty(self):
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        # Non-matching name
        self.assertEqual(backend.search_students_by_name(allocs, "Nonexistent Person"), [])
        # Empty or spaces
        self.assertEqual(backend.search_students_by_name(allocs, ""), [])
        self.assertEqual(backend.search_students_by_name(allocs, "    "), [])

    def test_unified_search_students(self):
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        # Search by Roll Number mode (exact match)
        roll_res = backend.search_students(allocs, "22IT103", search_by="Roll Number")
        self.assertEqual(len(roll_res), 1)
        self.assertEqual(roll_res[0]["student_name"], "Ananya Verma")

        # Search by Roll Number mode (partial match e.g. "103")
        roll_partial = backend.search_students(allocs, "103", search_by="Roll Number")
        self.assertEqual(len(roll_partial), 1)
        self.assertEqual(roll_partial[0]["roll_no"], "22IT103")

        # Search by Student Name mode
        name_res = backend.search_students(allocs, "Ananya", search_by="Student Name")
        self.assertEqual(len(name_res), 1)
        self.assertEqual(name_res[0]["roll_no"], "22IT103")

        # Case-insensitive search_by parameter values
        name_res2 = backend.search_students(allocs, "Aditi", search_by="name")
        self.assertEqual(len(name_res2), 1)
        self.assertEqual(name_res2[0]["student_name"], "Aditi Patel")

    def test_search_students_by_roll_exact_and_partial(self):
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        # Exact roll match
        exact = backend.search_students_by_roll(allocs, "22IT101")
        self.assertEqual(len(exact), 1)
        self.assertEqual(exact[0]["student_name"], "Aarav Sharma")

        # Partial roll match with common prefix "22IT1"
        partial = backend.search_students_by_roll(allocs, "22IT1")
        self.assertEqual(len(partial), 24)

        # Non-matching roll
        none_res = backend.search_students_by_roll(allocs, "99999")
        self.assertEqual(none_res, [])

    def test_html_and_dataframe_generation(self):
        success, msg, shortfall, allocs, stats = backend.allocate_seats(
            students=self.sample_students,
            num_classrooms=2,
            benches_per_room=4,
            seats_per_bench=3
        )
        df = backend.convert_allocations_to_dataframe(allocs)
        self.assertEqual(len(df), 24)
        self.assertIn("Classroom", df.columns)
        self.assertIn("Bench Number", df.columns)

        html = backend.generate_printable_html(allocs, stats)
        self.assertIn("Semester Examination Seating Plan", html)
        self.assertIn("Room 101", html)
        self.assertIn("Room 102", html)
        self.assertIn("window.print()", html)


if __name__ == "__main__":
    unittest.main()
