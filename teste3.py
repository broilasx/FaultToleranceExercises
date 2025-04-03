import statistics
import random

# Filtro de Kalman para suavizar leituras dos sensores
class KalmanFilter:
    def __init__(self, process_variance=1e-5, measurement_variance=1e-2):
        self.estimate = 0.0
        self.error_covariance = 1.0
        self.process_variance = process_variance
        self.measurement_variance = measurement_variance

    def update(self, measurement):
        predicted_estimate = self.estimate
        predicted_error_covariance = self.error_covariance + self.process_variance

        kalman_gain = predicted_error_covariance / (predicted_error_covariance + self.measurement_variance)
        self.estimate = predicted_estimate + kalman_gain * (measurement - predicted_estimate)
        self.error_covariance = (1 - kalman_gain) * predicted_error_covariance

        return self.estimate

# Information Redundancy: Checksum para garantir a integridade dos dados
def checksum(data):
    return sum(data) % 256

def is_valid_data(sensors):
    expected_checksum = checksum(sensors[:-1])
    return expected_checksum == sensors[-1]

# Retry Mechanism para leituras falhadas
def safe_reading(sensor_func, retries=3):
    for _ in range(retries):
        reading = sensor_func()
        if 0 <= reading <= 100:
            return reading
    return -1  # Falha após várias tentativas

# Backward Recovery: Utilizar a última leitura válida se houver falha
last_valid_distance = 50  # Valor inicial seguro

def get_distance_with_backup(current_distance):
    global last_valid_distance
    if 0 <= current_distance <= 100:
        last_valid_distance = current_distance
        return current_distance
    print(f"⚠️ Falha na leitura ({current_distance}), utilizando valor anterior: {last_valid_distance}")
    return last_valid_distance

def majority_voting(distances):
    most_common = max(set(distances), key=distances.count)
    if distances.count(most_common) >= 2:
        return most_common
    else:
        return statistics.median(distances)

def get_beep_level_with_fault_tolerance(sensors, levels):
    if not isinstance(sensors, list) or not isinstance(levels, list) or len(sensors) % 3 != 0:
        return -1

    if not all(isinstance(d, (int, float)) and d >= 0 for d in sensors):
        return -1

    if not all(isinstance(l, (int, float)) and l >= 0 for l in levels):
        return -1

    if len(levels) == 0 or len(sensors) == 0:
        return -1

    # Verificar integridade com checksum
    if not is_valid_data(sensors + [checksum(sensors)]):
        print("⚠️ Falha de integridade dos dados (checksum inválido).")
        return -1

    # Simulação de Falha Aleatória
    if random.random() < 0.05:
        faulty_sensor = random.randint(0, len(sensors) - 1)
        sensors[faulty_sensor] = max(0, sensors[faulty_sensor] - random.randint(30, 60))
        print(f"⚠️ Falha detectada no sensor {faulty_sensor + 1}: valor brusco {sensors[faulty_sensor]}")

    # Criar filtros de Kalman
    kalman_filters = [KalmanFilter() for _ in range(len(sensors) // 3)]
    grouped_sensors = [sensors[i:i + 3] for i in range(0, len(sensors), 3)]

    # Aplicar majority voting e filtro de Kalman
    smoothed_distances = []
    for i, group in enumerate(grouped_sensors):
        valid_distance = majority_voting(group)
        safe_distance = get_distance_with_backup(valid_distance)
        smoothed_distance = kalman_filters[i].update(safe_distance)
        smoothed_distances.append(smoothed_distance)

    max_change = 50
    valid_distances = [
        dist for dist in smoothed_distances if abs(dist - statistics.median(smoothed_distances)) <= max_change
    ]

    if len(valid_distances) < len(smoothed_distances) // 2:
        return -1

    min_distance = min(valid_distances)
    beep_level = next((i for i, level in reversed(list(enumerate(levels))) if level <= min_distance), 0)
    return beep_level

# Simulação para testar o sistema com fault tolerance melhorado
def simulate_reverse_drive():
    test_cases = []
    levels = [5, 10, 20, 40, 70]
    distance = 100

    for i in range(200):
    
        if i % 10 == 0 and distance > 0:
            distance = max(0, distance - 4)

        sensor_readings = [
            max(0, distance + (j - 1)) for j in range(3) for i in range(3)
        ]
        min_distance = min(sensor_readings)
        expected_level = next((i for i, level in reversed(list(enumerate(levels))) if level <= min_distance), 0)
        
        test_cases.append((sensor_readings, levels, expected_level))

    print("\n🚗 Simulação de marcha-atrás com fault tolerance melhorado\n")
    for i, (sensors, levels, expected) in enumerate(test_cases):
        result = get_beep_level_with_fault_tolerance(sensors, levels)
        status = "PASS" if result == expected else f"FAIL (Expected: {expected}, Got: {result})"
        print(f"Test Case {i + 1}: {status} | Sensores: {sensors} | Níveis: {levels} | Resultado: {result}")

def FR4():
    test_cases = [
        ([], [], -1), #TC1
        ([100, 30, 100, 100, 100, 100], [5, 10, 20, 40, 70], 4), #TC2
        ([100, 60, 100, 30, 30, 30, 7, 7, 7], [5, 10, 20, 40, 70], 0), # TC3
        ([30, 30, 30, 100, 100, 100, 7, 7, 7], [5, 10, 20, 40, 70], 1), # TC4
        ([1, 1, 1, 7, 7, 7, 13, 13, 13], [5, 10, 20, 40, 70], 0),        # TC5
        ([2, 2, 2, 4, 4, 4, 5, 5, 5], [1], 0),                          # TC6
        ([1, 1, 1], [5, 10, 20], 0),                                   # TC7
        ([1, 1, "a", 2, 2, 2], [5, 10, 20], -1),                        # TC8
        ([1, 1, 1, 2, 2, 2, 3, 3, 3], ["a", 10], -1),                   # TC9
        ([2, 2, 2, 4, 4, 4, 5, 5, 5], [], -1),                           # TC10
        ([-1, -1, -1, -1, -1, -1, -1, -1, -1], [5, 10, 20, 40, 70], -1), # TC11
        ([50, 50, 50, 30, 30, 30, 40, 40, 40], [5, 10, 20, 40, 70], 2),  # TC12
        ([-1, -1, -1, -1, -1, -1, -1, -1, -1], [5, 10, 20, 40, 70], -1), # TC13
    ]

    print("Executing FR4 Test Cases:")
    for i, (sensors, levels, expected) in enumerate(test_cases):
        result = get_beep_level_with_fault_tolerance(sensors, levels)
        print(f"Test Case {i + 1}: {'PASS' if result == expected else 'FAIL'} (Expected: {expected}, Got: {result})")

# Testes
if __name__ == '__main__':
    #FR4()
    simulate_reverse_drive()