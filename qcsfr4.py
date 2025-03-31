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

def get_beep_level(distances, levels):
    if len(distances) < 2:
        return -1  # sao necessarios pelo menos 2 sensores 
    
    min_distance = min(distances)  # vai buscar o objeto mais perto
    
    # procura o nivel correspondente ao objeto mais perto
    for i, level in enumerate(levels):
        if min_distance <= level:
            return i
    
    return len(levels)  # se nao tiver nenhum nivel correspondente ao objeto mais perto, retorna o beep level mais baixo

# Test cases
print(get_beep_level([], []))  # Experado -1
print(get_beep_level([100, 100], [5, 10, 20, 40, 70]))  # Experado 4
print(get_beep_level([30, 100], [5, 10, 20, 40, 70]))  # Experado 2
print(get_beep_level([1, 7, 13, 25, 45, 80], [5, 10, 20, 40, 70]))  # Experado 0
print(get_beep_level([2, 4, 5, 5], [1]))  # Experado 0

#Versao com Fault Tolerance

import statistics

# **DATA REDUNDANCY** - guardar valores passados
previous_distances = []

def get_beep_level(primary_sensors, backup_sensors, levels):
    global previous_distances  # Store past valid readings

    # **EXCEPTION HANDLING** - input valido
    if not isinstance(primary_sensors, list) or not isinstance(backup_sensors, list) or not isinstance(levels, list):
        return -1  #Tipo de dados recebidos invalidos

    if len(primary_sensors) < 2:
        return -1  # Sao necessarios pelo menos 2 sensores

    if len(primary_sensors) != len(backup_sensors):
        return -1  # Cada sensor primario deve ter um sensor de backup correspondente

    if not all(isinstance(d, (int, float)) and d >= 0 for d in primary_sensors + backup_sensors):
        return -1  # Leituras de sensor invalidas

    if not all(isinstance(l, (int, float)) and l >= 0 for l in levels):
        return -1  # Niveis de beep invalidos

    if len(levels) == 0:
        return 0  # Levels nao definidos, retornar beep level mais baixo que neste caso é 0

    # **HARDWARE REDUNDANCY** Vai dar replace a sensores invalidos com sensores de backup
    validated_sensors = [
        primary if primary >= 0 else backup
        for primary, backup in zip(primary_sensors, backup_sensors)
    ]

    # **TIME REDUNDANCY** Vai remover valores negativos do sensor
    valid_distances = [d for d in validated_sensors if d >= 0]

    if len(valid_distances) < 2:
        if previous_distances:
            valid_distances = previous_distances  # Usa a utima leitura de sensor valida
        else:
            return -1  # Nao ha leituras de sensores validas

    # **DATA REDUNDANCY** guardar as ultimas distancias validas
    previous_distances = valid_distances.copy()

    # **SOFTWARE REDUNDANCY** Dois metodos para determinar o beep level // nao sei se é suposto ser bem isto, nao entendi bem este!!!!
    min_distance = min(valid_distances)

    # Metodo 1: Nivel mais baixo que a distancia minima
    method_1 = next((i for i, level in enumerate(levels) if min_distance <= level), len(levels))

    # Metodo 2: Nivel mais baixo que a mediana das distancias validas
    method_2 = next((i for i, level in enumerate(levels) if statistics.median(valid_distances) <= level), len(levels))

    # Decisao final, escolher o beep level mais baixo
    return min(method_1, method_2)


#Alguns casos de teste
print(get_beep_level([], [], []))  # experado -1
print(get_beep_level([100, 100], [100, 100], [5, 10, 20, 40, 70]))  # experado 4
print(get_beep_level([30, 100], [30, 100],[5, 10, 20, 40, 70]))  # experado 2
print(get_beep_level([1, 7, 13, 25, 45, 80], [1, 7, 13, 25, 45, 80],[5, 10, 20, 40, 70]))  # experado 0
print(get_beep_level([2, 4, 5, 5], [2, 4, 5, 5],[1]))  # experado 0

print(get_beep_level([1], [1],[5, 10, 20]))  # experado -1 (falta um sensor)
print(get_beep_level([1, "a"], [1, "a"],[5, 10, 20]))  # experado -1 (sensor invalido)
print(get_beep_level([1, 2], [1, 2],["a", 10]))  # Experado -1 (nivel invalido)
print(get_beep_level([2, 4, 5, 5], [2, 4, 5, 5],[]))  # Experado 0 (sem niveis)

# Testes do data redundancy
print(get_beep_level([-1, -1], [-1, -1],[5, 10, 20, 40, 70]))  # experado -1 
print(get_beep_level([50, 30], [50, 30],[5, 10, 20, 40, 70]))  # experado 2
print(get_beep_level([-1, -1], [-1, -1],[5, 10, 20, 40, 70]))  # experado -1
