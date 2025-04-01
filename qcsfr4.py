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
from collections import Counter

previous_distances = []

def majority_voting(group):
    """Aplica majority voting para obter a distância mais frequente em um grupo de 3 sensores."""
    counter = Counter(group)
    most_common = counter.most_common(1)
    return most_common[0][0] if most_common else statistics.median(group)

def smooth_readings(distances):
    """Aplica uma média móvel simples para suavizar leituras."""
    if len(distances) < 3:
        return statistics.mean(distances)
    window_size = min(5, len(distances))
    return statistics.mean(distances[-window_size:])

def get_beep_level_with_fault_tolerance(sensors, levels):
    global previous_distances

    # **EXCEPTION HANDLING** - Verificação de entrada
    if not isinstance(sensors, list) or not isinstance(levels, list):
        return -1
    if len(sensors) == 0 or len(sensors) % 3 != 0:
        return -1  # Lista vazia ou número de sensores não é múltiplo de 3
    if not all(isinstance(d, (int, float)) and d >= 0 for d in sensors):
        return -1
    if not all(isinstance(l, (int, float)) and l >= 0 for l in levels):
        return -1
    if len(levels) == 0:
        return 0

    # **REDUNDANCY AND VOTING** - Agrupar sensores em conjuntos de 3 e aplicar majority voting
    distances = []
    for i in range(0, len(sensors), 3):
        group = sensors[i:i+3]
        distance = majority_voting(group)
        distances.append(distance)

    # **TIME REDUNDANCY** - Suavização das leituras
    smoothed_distance = smooth_readings(distances)

    # **DATA REDUNDANCY** - Armazenar últimas distâncias válidas
    previous_distances = distances.copy()

    # **SOFTWARE REDUNDANCY** - Determinar o beep level por dois métodos
    min_distance = min(distances)
    method_1 = next((i for i, level in enumerate(levels) if min_distance <= level), len(levels))
    method_2 = next((i for i, level in enumerate(levels) if smoothed_distance <= level), len(levels))

    # **GRACEFUL DEGRADATION** - Garantir o beep level mais seguro (mínimo dos dois)
    return min(method_1, method_2)

# Função para executar os testes
def FR4():
    test_cases = [
        ([], [], -1),
        ([100, 100, 100, 100, 100, 100], [5, 10, 20, 40, 70], 4),
        ([100, 60, 100, 30, 30, 30, 7, 7, 7], [5, 10, 20, 40, 70], 0), # TC1
        ([30, 30, 30, 100, 100, 100, 7, 7, 7], [5, 10, 20, 40, 70], 2), # TC2
        ([1, 1, 1, 7, 7, 7, 13, 13, 13], [5, 10, 20, 40, 70], 0),        # TC3
        ([2, 2, 2, 4, 4, 4, 5, 5, 5], [1], 0),                          # TC4
        ([1, 1, 1], [5, 10, 20], -1),                                   # TC5
        ([1, 1, "a", 2, 2, 2], [5, 10, 20], -1),                        # TC6
        ([1, 1, 1, 2, 2, 2, 3, 3, 3], ["a", 10], -1),                   # TC7
        ([2, 2, 2, 4, 4, 4, 5, 5, 5], [], 0),                           # TC8
        ([-1, -1, -1, -1, -1, -1, -1, -1, -1], [5, 10, 20, 40, 70], -1), # TC9
        ([50, 50, 50, 30, 30, 30, 40, 40, 40], [5, 10, 20, 40, 70], 2),  # TC10
        ([-1, -1, -1, -1, -1, -1, -1, -1, -1], [5, 10, 20, 40, 70], -1), # TC11
    ]

    print("Executing FR4 Test Cases:")
    for i, (sensors, levels, expected) in enumerate(test_cases):
        result = get_beep_level_with_fault_tolerance(sensors, levels)
        print(f"Test Case {i + 1}: {'PASS' if result == expected else 'FAIL'} (Expected: {expected}, Got: {result})")

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    FR4()