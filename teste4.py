import statistics
import random

# Sistemas de Fault Tolerance:
# Majority Voting:
# Escolhe o valor mais frequente entre três leituras de sensores.
# Se não houver maioria clara, retorna a mediana.
# Propósito: Minimizar o impacto de uma leitura errada entre várias.
# Filtro de Kalman:
# Suaviza as leituras de sensores para reduzir o ruído.
# Atualiza a estimativa com base na leitura mais recente e na variância configurada.
# Propósito: Filtrar leituras com ruído e estabilizar as medições.
# Retry Mechanism:
# Tenta recolher uma leitura várias vezes antes de falhar.
# Propósito: Garantir que uma falha temporária não comprometa o resultado.
# Backward Recovery (Última Leitura Válida):
# Se a leitura atual for inválida, usa a última leitura válida.
# Propósito: Garantir continuidade no caso de uma falha pontual.
# Checksum:
# Garante a integridade dos dados verificando se a soma das leituras corresponde ao checksum esperado.
# Propósito: Detectar corrupção dos dados dos sensores.

# Redundancia:
# Majority Voting vs. Filtro de Kalman:
# Ambos têm o objetivo de lidar com leituras erradas ou ruidosas.
# O Majority Voting tenta determinar a leitura correta pela frequência, enquanto o Filtro de Kalman suaviza as leituras para reduzir o ruído.
# Redundância: Utilizar ambos para o mesmo conjunto de leituras pode ser considerado redundante, pois o filtro de Kalman já é capaz de suavizar leituras inconsistentes.
# Backward Recovery vs. Retry Mechanism:
# O Retry Mechanism tenta recolher uma leitura válida várias vezes, enquanto o Backward Recovery utiliza a última leitura válida se a nova falhar.
# Redundância: Se o Retry Mechanism já tentou várias vezes obter uma leitura, usar o valor anterior pode ser redundante, visto que já foi feita uma tentativa robusta de recolha.

#ou seja, para tratar da redundancia vou deixar de utilizar o filtro de kalman e passar a usar apenas o majority voting e vou deixar de utilizar o backward recovery e passar a
#utilizar apenas o retry mechanism

# Retry Mechanism para leituras falhadas
def safe_reading(sensor_func, retries=3):
    for _ in range(retries):
        reading = sensor_func()
        if 0 <= reading <= 100:
            return reading
    return -1  # Falha após várias tentativas

# Checksum explícito
def checksum(data):
    return sum(data) % 256

def is_valid_data(sensors, checksum_value):
    expected_checksum = checksum(sensors)
    return expected_checksum == checksum_value

# Majority Voting
def majority_voting(distances):
    most_common = max(set(distances), key=distances.count)
    if distances.count(most_common) >= 2:
        return most_common
    else:
        return statistics.median(distances)

# Função principal com checksum explícito
def get_beep_level_with_fault_tolerance(sensors, checksum_value, levels):
    if not isinstance(sensors, list) or not isinstance(levels, list) or len(sensors) % 3 != 0:
        return -1

    if not all(isinstance(d, (int, float)) and d >= 0 for d in sensors):
        return -1

    if not all(isinstance(l, (int, float)) and l >= 0 for l in levels):
        return -1

    if len(levels) == 0 or len(sensors) == 0:
        return -1

    # Verificar integridade com checksum
    if not is_valid_data(sensors, checksum_value):
        print("Falha de integridade dos dados (checksum inválido).")
        return -1

    # Simulação de Falha Aleatória
    if random.random() < 0.05:
        faulty_sensor = random.randint(0, len(sensors) - 1)
        sensors[faulty_sensor] = max(0, sensors[faulty_sensor] - random.randint(30, 60))
        print(f"Falha detectada no sensor {faulty_sensor + 1}: valor brusco {sensors[faulty_sensor]}")

    # Agrupar os sensores em trios
    grouped_sensors = [sensors[i:i + 3] for i in range(0, len(sensors), 3)]

    # Aplicar majority voting diretamente
    smoothed_distances = [majority_voting(group) for group in grouped_sensors]

    min_distance = min(smoothed_distances)
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

        # Uso do safe_reading
        sensor_readings = [
            safe_reading(lambda: max(0, distance + (j - 1))) for j in range(3) for _ in range(3)
        ]
        min_distance = min(sensor_readings)
        expected_level = next((i for i, level in reversed(list(enumerate(levels))) if level <= min_distance), 0)
        
        test_cases.append((sensor_readings, levels, expected_level))

    print("\nSimulação de marcha-atrás\n")
    for i, (sensors, levels, expected) in enumerate(test_cases):
        result = get_beep_level_with_fault_tolerance(sensors, checksum(sensors), levels)
        status = "PASS" if result == expected else f"FAIL (Expected: {expected}, Got: {result})"
        print(f"Test Case {i + 1}: {status} | Sensores: {sensors} | Níveis: {levels} | Resultado: {result}")

# Testes FR4 atualizados com checksum explícito
def FR4():
    test_cases = [
        ([], [], -1), #TC1
        ([100, 30, 100, 100, 100, 100], [5, 10, 20, 40, 70], 4), #TC2
        ([100, 60, 100, 30, 30, 30, 7, 7, 7], [5, 10, 20, 40, 70], 0), # TC3
        ([30, 30, 30, 100, 100, 100, 7, 7, 7], [5, 10, 20, 40, 70], 0), # TC4
        ([1, 1, 1, 7, 7, 7, 13, 13, 13], [5, 10, 20, 40, 70], 0),        # TC5
        ([2, 2, 2, 4, 4, 4, 5, 5, 5], [1], 0),                          # TC6
        ([1, 1, 1], [5, 10, 20], 0),                                   # TC7
        ([1, 1, "a", 2, 2, 2], [5, 10, 20], -1),                        # TC8
        ([1, 1, 1, 2, 2, 2, 3, 3, 3], ["a", 10], -1),                   # TC9
        ([2, 2, 2, 4, 4, 4, 5, 5, 5], [], -1),                          # TC10
        ([-1, -1, -1, -1, -1, -1, -1, -1, -1], [5, 10, 20, 40, 70], -1), # TC11
        ([50, 50, 50, 30, 30, 30, 40, 40, 40], [5, 10, 20, 40, 70], 2),  # TC12
        ([-1, -1, -1, -1, -1, -1, -1, -1, -1], [5, 10, 20, 40, 70], -1), # TC13
    ]

    print("Executing FR4 Test Cases:")
    for i, (sensors, levels, expected) in enumerate(test_cases):
        checksum_value = checksum(sensors) if all(isinstance(x, (int, float)) and x >= 0 for x in sensors) else 0
        result = get_beep_level_with_fault_tolerance(sensors, checksum_value, levels)
        status = "PASS" if result == expected else f"FAIL (Expected: {expected}, Got: {result})"
        print(f"Test Case {i + 1}: {status}")

# Testes
if __name__ == '__main__':
    simulate_reverse_drive()
    #FR4()