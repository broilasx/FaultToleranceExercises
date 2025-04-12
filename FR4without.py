def get_beep_level_without_fault_tolerance(distances, levels): 
    
    if distances:
        min_distance = min(distances)  # vai buscar o objeto mais perto
    
    if not distances:
        return -1
    # procura o nivel correspondente ao objeto mais perto
    for i, level in reversed(list(enumerate(levels))):
        if level <= min_distance:
            return i
    
    return 0  # se nao tiver nenhum nivel correspondente ao objeto mais perto, retorna o beep level mais baixo


def FR4():
    test_cases = [
        ([], [], -1), #TC1
        ([100, 30, 100, 100, 100, 100], [5, 10, 20, 40, 70], 2), #TC2
        ([100, 60, 100, 30, 30, 30, 7, 7, 7], [5, 10, 20, 40, 70], 0), # TC3
        ([30, 30, 30, 100, 100, 100, 7, 7, 7], [5, 10, 20, 40, 70], 0), # TC4
        ([1, 1, 1, 7, 7, 7, 13, 13, 13], [5, 10, 20, 40, 70], 0),        # TC5
        ([2, 2, 2, 4, 4, 4, 5, 5, 5], [1], 0),                          # TC6
        ([1, 1, 1], [5, 10, 20], 0),                                   # TC7
    ]

    print("Executing FR4 Test Cases:")
    for i, (sensors, levels, expected) in enumerate(test_cases):
        result = get_beep_level_without_fault_tolerance(sensors, levels)
        print(f"Test Case {i + 1}: {'PASS' if result == expected else 'FAIL'} (Expected: {expected}, Got: {result})")

# Executar os testes
if __name__ == '__main__':
    FR4()
    #simulate_reverse_drive()
