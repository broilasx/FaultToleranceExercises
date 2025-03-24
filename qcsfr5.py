#Tipos de fault tolerance

# "!"" - IMPLEMENTADOS

#1. Time Redundancy !
#2. Data Redundancy !
#3. Software Redundancy 
#4. Hardware Redundancy !
#5. Information Redundancy
#6. Exception Handling !

# **Como funciona o FR5**
# o sistema recebe como entrada uma câmera que fornece uma matriz de valores entre 0 e 1.
# cada valor representa a intensidade de um pixel na escala do cinzento.
# o objetivo do sistema é identificar e contar os objetos presentes na imagem.
# **Como funciona a deteçao dos objetos**
# um objeto é formado por pixeis conectados (so na vertical e horizontal, nunca na diagonal).
# apenas pixels com valor acima de um determinado valor, que neste caso é o threshold, são considerados parte de um objeto.
# ou seja, se um valor da imagem for 0.2 e o threshold for 0.5, essa parte da imagem nao vai ser lida, ou seja nao vai contar como um objeto, a função deve contar quantos objetos distintos existem na imagem.
# 
# **Exemplo**
# para criarmos esta matriz que está no enunciado, iriamos receber a imagem  [1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 1.0]
# o width e o height seriam 3 e o threshold seria 0.5, isto iria fazer esta matriz
#   1.0  1.0  0.0
#   1.0  1.0  0.0
#   0.0  0.0  1.0
# os pixels 1.0 conectados na parte superior formam um único objeto.
# o pixel 1.0 isolado no canto inferior direito é outro objeto separado.
# isso significa que vamos ter 2 objetos separados, ou seja vai retornar 2.

#Versao sem Fault Tolerance


def count_objects(image, width, height, threshold):
    def bfs(x, y):
        queue = [(x, y)]
        visited.add((x, y))
        
        while queue:
            cx, cy = queue.pop(0)
            for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:  # Apenas vertical e horizontal
                nx, ny = cx + dx, cy + dy
                if 0 <= nx < height and 0 <= ny < width and (nx, ny) not in visited and image[nx][ny] > threshold:
                    queue.append((nx, ny))
                    visited.add((nx, ny))

    visited = set()
    object_count = 0

    for i in range(height):
        for j in range(width):
            if image[i][j] > threshold and (i, j) not in visited:
                bfs(i, j)
                object_count += 1

    return object_count

# Teste
image = [[1.0, 1.0, 0.0], [1.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
print(count_objects(image, 3, 3, 0.5))  # Experado 2