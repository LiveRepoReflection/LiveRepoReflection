import unittest
from meet_optimal import find_optimal_meeting_time


class TestOptimalMeetingScheduler(unittest.TestCase):

    def test_basic_scheduling(self):
        employees = [
            {'id': 1, 'level': 3, 'availability': [(600, 720)]},  # 10:00 AM - 12:00 PM
            {'id': 2, 'level': 5, 'availability': [(660, 780)]},  # 11:00 AM - 1:00 PM
            {'id': 3, 'level': 2, 'availability': [(600, 660), (720, 780)]}  # 10:00-11:00 and 12:00-1:00
        ]
        meeting_duration = 60
        required_attendees = [1, 2]
        optional_attendees = [3]
        working_hours = (540, 840)  # 9:00 AM - 2:00 PM

        expected_output = (660, 720)  # 11:00 AM - 12:00 PM
        self.assertEqual(
            find_optimal_meeting_time(employees, meeting_duration, required_attendees, optional_attendees, working_hours),
            expected_output
        )

    def test_no_suitable_time(self):
        employees = [
            {'id': 1, 'level': 3, 'availability': [(600, 630)]},  # 10:00 AM - 10:30 AM
            {'id': 2, 'level': 5, 'availability': [(660, 690)]},  # 11:00 AM - 11:30 AM
        ]
        meeting_duration = 60
        required_attendees = [1, 2]
        optional_attendees = []
        working_hours = (540, 840)  # 9:00 AM - 2:00 PM

        self.assertIsNone(
            find_optimal_meeting_time(employees, meeting_duration, required_attendees, optional_attendees, working_hours)
        )

    def test_no_required_attendees(self):
        employees = [
            {'id': 1, 'level': 3, 'availability': [(600, 720)]},  # 10:00 AM - 12:00 PM
            {'id': 2, 'level': 5, 'availability': [(660, 780)]},  # 11:00 AM - 1:00 PM
        ]
        meeting_duration = 60
        required_attendees = []
        optional_attendees = [1, 2]
        working_hours = (540, 840)  # 9:00 AM - 2:00 PM

        expected_output = (660, 720)  # 11:00 AM - 12:00 PM (both optional attendees available)
        self.assertEqual(
            find_optimal_meeting_time(employees, meeting_duration, required_attendees, optional_attendees, working_hours),
            expected_output
        )

    def test_outside_working_hours(self):
        employees = [
            {'id': 1, 'level': 3, 'availability': [(480, 600)]},  # 8:00 AM - 10:00 AM
            {'id': 2, 'level': 5, 'availability': [(480, 600)]},  # 8:00 AM - 10:00 AM
        ]
        meeting_duration = 60
        required_attendees = [1, 2]
        optional_attendees = []
        working_hours = (600, 840)  # 10:00 AM - 2:00 PM (no overlap with employees)

        self.assertIsNone(
            find_optimal_meeting_time(employees, meeting_duration, required_attendees, optional_attendees, working_hours)
        )
        
    def test_different_disruption_scores(self):
        employees = [
            {'id': 1, 'level': 10, 'availability': [(600, 660)]},  # 10:00 AM - 11:00 AM
            {'id': 2, 'level': 1, 'availability': [(720, 780)]},   # 12:00 PM - 1:00 PM
            {'id': 3, 'level': 5, 'availability': [(600, 780)]},   # 10:00 AM - 1:00 PM
        ]
        meeting_duration = 60
        required_attendees = [3]  # Only employee 3 is required
        optional_attendees = [1, 2]
        working_hours = (540, 840)  # 9:00 AM - 2:00 PM
        
        # Two possible solutions: (600, 660) or (720, 780)
        # At (600, 660): Employee 1 can attend, Employee 2 cannot (disruption = 1)
        # At (720, 780): Employee 2 can attend, Employee 1 cannot (disruption = 10)
        # Therefore, the optimal time should be (600, 660) as it has less disruption
        expected_output = (600, 660)
        self.assertEqual(
            find_optimal_meeting_time(employees, meeting_duration, required_attendees, optional_attendees, working_hours),
            expected_output
        )
        
    def test_multiple_equally_optimal_times(self):
        employees = [
            {'id': 1, 'level': 5, 'availability': [(600, 720)]},  # 10:00 AM - 12:00 PM
            {'id': 2, 'level': 5, 'availability': [(600, 720)]},  # 10:00 AM - 12:00 PM
        ]
        meeting_duration = 30
        required_attendees = [1, 2]
        optional_attendees = []
        working_hours = (540, 840)  # 9:00 AM - 2:00 PM
        
        # Multiple equally optimal solutions exist: any 30-minute slot between 10:00 AM - 12:00 PM
        # The function should return the earliest one: (600, 630)
        expected_output = (600, 630)
        self.assertEqual(
            find_optimal_meeting_time(employees, meeting_duration, required_attendees, optional_attendees, working_hours),
            expected_output
        )
    
    def test_large_number_of_employees(self):
        # Create a test with 1000 employees
        employees = []
        for i in range(1, 1001):
            # Assign different availability patterns based on ID to create a mix
            if i % 3 == 0:
                availability = [(600, 720)]  # 10:00 AM - 12:00 PM
            elif i % 3 == 1:
                availability = [(660, 780)]  # 11:00 AM - 1:00 PM
            else:
                availability = [(600, 660), (720, 780)]  # 10:00-11:00 and 12:00-1:00
            
            employees.append({
                'id': i,
                'level': (i % 10) + 1,  # Levels from 1-10
                'availability': availability
            })
        
        meeting_duration = 60
        required_attendees = [1, 334, 667, 1000]  # Select some attendees from different availability patterns
        optional_attendees = [i for i in range(2, 1000) if i not in required_attendees]
        working_hours = (540, 840)  # 9:00 AM - 2:00 PM
        
        # Verify solution exists and returns in a reasonable time
        result = find_optimal_meeting_time(employees, meeting_duration, required_attendees, optional_attendees, working_hours)
        self.assertIsNotNone(result)
        
    def test_edge_case_exact_fit(self):
        employees = [
            {'id': 1, 'level': 3, 'availability': [(600, 660)]},  # 10:00 AM - 11:00 AM (exactly 60 minutes)
            {'id': 2, 'level': 5, 'availability': [(600, 660)]},  # 10:00 AM - 11:00 AM (exactly 60 minutes)
        ]
        meeting_duration = 60
        required_attendees = [1, 2]
        optional_attendees = []
        working_hours = (540, 840)  # 9:00 AM - 2:00 PM
        
        expected_output = (600, 660)  # Should fit exactly
        self.assertEqual(
            find_optimal_meeting_time(employees, meeting_duration, required_attendees, optional_attendees, working_hours),
            expected_output
        )
        
    def test_meeting_duration_too_long(self):
        employees = [
            {'id': 1, 'level': 3, 'availability': [(600, 650)]},  # 10:00 AM - 10:50 AM (50 minutes)
            {'id': 2, 'level': 5, 'availability': [(600, 650)]},  # 10:00 AM - 10:50 AM (50 minutes)
        ]
        meeting_duration = 60  # 60 minutes, won't fit in the 50-minute slot
        required_attendees = [1, 2]
        optional_attendees = []
        working_hours = (540, 840)  # 9:00 AM - 2:00 PM
        
        self.assertIsNone(
            find_optimal_meeting_time(employees, meeting_duration, required_attendees, optional_attendees, working_hours)
        )


if __name__ == '__main__':
    unittest.main()