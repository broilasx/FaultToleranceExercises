import unittest
import random
from teste3 import (
    KalmanFilter, checksum, is_valid_data, safe_reading,
    get_distance_with_backup, majority_voting,
    get_beep_level_with_fault_tolerance
)

class TestFaultToleranceMethods(unittest.TestCase):
    
    def test_kalman_filter(self):
        kalman = KalmanFilter()
        noisy_readings = [10, 12, 8, 11, 9, 10]
        smoothed_values = [kalman.update(meas) for meas in noisy_readings]
        self.assertTrue(all(abs(smoothed_values[i] - smoothed_values[i-1]) < 2 for i in range(1, len(smoothed_values))))
    
    def test_checksum_verification(self):
        data = [10, 20, 30, 40]
        valid_checksum = checksum(data)
        self.assertTrue(is_valid_data(data + [valid_checksum]))
        self.assertFalse(is_valid_data(data + [valid_checksum + 1]))
    
    def test_safe_reading(self):
        def faulty_sensor():
            return random.choice([-1, -5, 50, 105])
        reading = safe_reading(faulty_sensor)
        self.assertIn(reading, range(0, 101))
    
    def test_backup_distance(self):
        global last_valid_distance
        last_valid_distance = 30
        self.assertEqual(get_distance_with_backup(40), 40)
        self.assertEqual(get_distance_with_backup(-5), 40)
    
    def test_majority_voting(self):
        self.assertEqual(majority_voting([10, 10, 20]), 10)
        self.assertEqual(majority_voting([30, 20, 20]), 20)
        self.assertEqual(majority_voting([30, 30, 20]), 30)
    
    def test_get_beep_level_with_fault_tolerance(self):
        levels = [5, 10, 20, 40, 70]
        sensors = [30, 30, 30, 100, 100, 100, 10, 10, 10]
        self.assertEqual(get_beep_level_with_fault_tolerance(sensors, levels), 1)
        
        sensors_faulty = [5, 5, 5, 50, 50, 50, 80, 80, 80]  # Fault in first set
        self.assertEqual(get_beep_level_with_fault_tolerance(sensors_faulty, levels), 2)
        
        sensors_invalid = [300, 300, 300, -10, -10, -10, 10, 10, 10]  # Out-of-range values
        self.assertEqual(get_beep_level_with_fault_tolerance(sensors_invalid, levels), -1)

if __name__ == "__main__":
    unittest.main()
