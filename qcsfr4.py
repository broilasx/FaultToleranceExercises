#Tipos de fault tolerance

# "!"" - IMPLEMENTADOS

#1. Time Redundancy !
#2. Data Redundancy !
#3. Software Redundancy !
#4. Hardware Redundancy !
#5. Information Redundancy
#6. Exception Handling !

# **Como funciona o exercicio** - basicamente cada distancia é uma distancia calculada por um sensor do carro a um objeto, ou seja por exemplo se receber 2 distancias
# isso significa que o carro tem 2 sensores e que uma das distancias é a distancia de um sensor ao objeto e a outra é a distancia do outro sensor ao objeto
# depois é recebido uma lista de niveis de beep, que é quao intenso vai ser o aviso que vai ser dado ao condutor do veiculo, ou seja se por exemplo o carro estiver muito proximo do objeto
# o beep tem que ser um dos mais intensos, e se estiver longe o beep tem que ser um dos mais fracos, o beep que é atribuido é consoante a distancia minima entre os 2 sensores do carro
# basicamente é isso, nao sei se me fiz entender bem mas pronto


#Versao sem Fault Tolerance

def get_beep_level_without_fault_tolerance(distances, levels):
    if len(distances) < 2:
        return -1  # sao necessarios pelo menos 2 sensores 
    
    min_distance = min(distances)  # vai buscar o objeto mais perto
    
    # procura o nivel correspondente ao objeto mais perto
    for i, level in enumerate(levels):
        if min_distance <= level:
            return i
    
    return len(levels)  # se nao tiver nenhum nivel correspondente ao objeto mais perto, retorna o beep level mais baixo

# Test cases
# print(get_beep_level([], []))  # Experado -1
# print(get_beep_level([100, 100], [5, 10, 20, 40, 70]))  # Experado 4
# print(get_beep_level([30, 100], [5, 10, 20, 40, 70]))  # Experado 2
# print(get_beep_level([1, 7, 13, 25, 45, 80], [5, 10, 20, 40, 70]))  # Experado 0
# print(get_beep_level([2, 4, 5, 5], [1]))  # Experado 0

#Versao com Fault Tolerance
# **DATA REDUNDANCY** - guardar valores passados
import statistics
import random

# Filtro de Kalman para suavizar leituras dos sensores
class KalmanFilter:
    def __init__(self, process_variance=1e-5, measurement_variance=1e-2):
        self.estimate = 0.0  # Estimativa inicial
        self.error_covariance = 1.0  # Covariância do erro inicial
        self.process_variance = process_variance  # Variância do processo
        self.measurement_variance = measurement_variance  # Variância da medição

    def update(self, measurement):
        # Predição
        predicted_estimate = self.estimate
        predicted_error_covariance = self.error_covariance + self.process_variance

        # Atualização
        kalman_gain = predicted_error_covariance / (predicted_error_covariance + self.measurement_variance)
        self.estimate = predicted_estimate + kalman_gain * (measurement - predicted_estimate)
        self.error_covariance = (1 - kalman_gain) * predicted_error_covariance

        return self.estimate


def majority_voting(distances):
    """
    Aplica o majority voting a uma lista de três distâncias para determinar a mais confiável.
    """
    # Verificar a maioria (2 ou mais valores iguais)
    most_common = max(set(distances), key=distances.count)
    if distances.count(most_common) >= 2:
        return most_common
    else:
        # Se não houver maioria clara, retorna a mediana para evitar outliers
        return statistics.median(distances)


def get_beep_level_with_fault_tolerance(sensors, levels):
    # **EXCEPTION HANDLING** - Verificação de entrada
    if not isinstance(sensors, list) or not isinstance(levels, list) or len(sensors) % 3 != 0:
        print("exception one")
        return -1

    if not all(isinstance(d, (int, float)) and d >= 0 for d in sensors):
        print("exception two")
        return -1  # Leituras de sensor inválidas

    if not all(isinstance(l, (int, float)) and l >= 0 for l in levels):
        print("exception three")
        return -1  # Níveis de beep inválidos

    if len(levels) == 0:
        print("Nao ha sensores no carro")  # Se não houver níveis, retornar 0
        return -1
    
    if len(sensors) == 0:
        print("Nao foram recebidas distancias")
        return -1

    # **Simulação de Falha Aleatória:**  
    if random.random() < 0.05:  # 5% de chance de uma falha brusca em cada leitura
        faulty_sensor = random.randint(0, 2)
        sensors[faulty_sensor] = max(0, sensors[faulty_sensor] - random.randint(30, 60))  # Mudança abrupta
        print(f"⚠️ Falha detectada no sensor {faulty_sensor + 1} : valor brusco {sensors[faulty_sensor]}")

    # Criar filtros de Kalman
    kalman_filters = [KalmanFilter() for _ in range(len(sensors) // 3)]

    # Agrupar os sensores em conjuntos de 3
    grouped_sensors = [sensors[i:i + 3] for i in range(0, len(sensors), 3)]

    # Aplicar majority voting e filtro de Kalman
    smoothed_distances = []
    for i, group in enumerate(grouped_sensors):
        # Obter a distância com majority voting
        valid_distance = majority_voting(group)
        # Suavizar com filtro de Kalman
        smoothed_distance = kalman_filters[i].update(valid_distance)
        smoothed_distances.append(smoothed_distance)

    # **OUTLIER DETECTION** - Verificar alterações bruscas
    max_change = 50  # Limite de mudança aceitável em 10 ms
    valid_distances = [
        dist for dist in smoothed_distances if abs(dist - statistics.median(smoothed_distances)) <= max_change
    ]

    if len(valid_distances) < len(smoothed_distances) // 2:
        return -1  # Dados insuficientes após filtragem

    # Escolher a menor distância válida para determinar o nível de beep
    min_distance = min(valid_distances)
    beep_level = next((i for i, level in reversed(list(enumerate(levels))) if level <= min_distance), 0)
    return beep_level

def simulate_reverse_drive():
    test_cases = []
    levels = [5, 10, 20, 40, 70]  # Níveis de beep

    distance = 100  # Começa longe (100 cm) e aproxima gradualmente

    for i in range(200):  # 100 leituras (3 segundos a cada 10 ms)
        # Aproxima gradualmente (simulando o carro a andar para trás)
        if i % 10 == 0 and distance > 0:  # A cada 100 ms (10 leituras), aproxima 2 cm
            distance = max(0, distance - 4)
        
        # Gerar 3 leituras de sensor para a mesma distância (com pequenas variações)
        sensor_readings = [
            max(0, distance + (j - 1))  # Pequena variação nos sensores
            for j in range(3)
        ]
        min_distance = min(sensor_readings)
        expected_level = next((i for i, level in reversed(list(enumerate(levels))) if level <= min_distance), 0)
        
        test_cases.append((sensor_readings, levels, expected_level))

    # Executar os testes com fault tolerance
    print("\n🚗 Simulação de marcha-atrás (3 segundos com falhas aleatórias)\n")
    for i, (sensors, levels, expected) in enumerate(test_cases):
        result = get_beep_level_with_fault_tolerance(sensors, levels)
        status = "PASS" if result == expected else f"FAIL (Expected: {expected}, Got: {result})"
        print(f"Test Case {i + 1}: {status} | Sensores: {sensors} | Níveis: {levels} | Resultado: {result}")

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
        ([2, 2, 2, 4, 4, 4, 5, 5, 5], [], -1),                           # TC10
        ([-1, -1, -1, -1, -1, -1, -1, -1, -1], [5, 10, 20, 40, 70], -1), # TC11
        ([50, 50, 50, 30, 30, 30, 40, 40, 40], [5, 10, 20, 40, 70], 2),  # TC12
        ([-1, -1, -1, -1, -1, -1, -1, -1, -1], [5, 10, 20, 40, 70], -1), # TC13
    ]

    print("Executing FR4 Test Cases:")
    for i, (sensors, levels, expected) in enumerate(test_cases):
        result = get_beep_level_with_fault_tolerance(sensors, levels)
        print(f"Test Case {i + 1}: {'PASS' if result == expected else 'FAIL'} (Expected: {expected}, Got: {result})")

# Executar os testes
if __name__ == '__main__':
    #FR4()
    simulate_reverse_drive()
