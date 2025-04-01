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


import logging

# Configuração do logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")

def calcular_nivel_beep(distancia_minima, niveis_beep):
    """
    Calcula o nível de beep com base na distância mínima.
    
    Parâmetros:
        distancia_minima (int ou float): Distância mínima entre o carro e o objeto.
        niveis_beep (list): Lista de níveis de beep, ordenados do mais intenso para o menos intenso.
    
    Retorna:
        int: Índice do nível de beep correspondente.
    """
    for i, beep in enumerate(niveis_beep):
        if distancia_minima <= beep:
            return i
    return len(niveis_beep) - 1


def obter_distancia_minima(distancias):
    """
    Obtém a distância mínima entre os sensores do carro e o objeto.
    
    Parâmetros:
        distancias (list): Lista de distâncias medidas pelos sensores.
    
    Retorna:
        float: Distância mínima calculada.
    """
    try:
        return min(distancias)
    except ValueError:
        logging.error("Lista de distâncias vazia ou inválida.")
        return -1


def fr4(distancias, niveis_beep):
    """
    Função principal do FR4 que calcula o nível de beep com base nas distâncias dos sensores.
    
    Parâmetros:
        distancias (list): Lista de distâncias fornecidas pelos sensores.
        niveis_beep (list): Lista de níveis de beep, ordenados por intensidade.
    
    Retorna:
        int: Índice do nível de beep.
    """
    if len(distancias) < 2:
        logging.error("Número insuficiente de sensores. Mínimo necessário: 2.")
        return -1
    
    distancia_minima = obter_distancia_minima(distancias)
    if distancia_minima == -1:
        return -1

    return calcular_nivel_beep(distancia_minima, niveis_beep)


# Casos de Teste para o FR4
def test_fr4():
    """
    Função de teste para verificar o funcionamento do FR4.
    """
    test_cases = [
        # Formato: (distancias, niveis_beep, resultado_esperado)
        ([30, 100], [5, 10, 20, 40, 70], 3),  # Distância mínima 30 -> Beep nível 3
        ([10, 50, 5], [5, 15, 30, 50, 100], 0),  # Distância mínima 5 -> Beep nível 0
        ([200, 150], [50, 100, 150, 200], 3),  # Distância mínima 150 -> Beep nível 3
        ([15], [5, 10, 20], -1),  # Apenas um sensor -> Erro (-1)
        ([], [5, 10, 20], -1),  # Lista vazia -> Erro (-1)
    ]

    for i, (distancias, niveis_beep, esperado) in enumerate(test_cases):
        resultado = fr4(distancias, niveis_beep)
        print(f"Teste {i + 1}: {'Passou' if resultado == esperado else 'Falhou'} (Resultado: {resultado}, Esperado: {esperado})")


if __name__ == "__main__":
    test_fr4()

