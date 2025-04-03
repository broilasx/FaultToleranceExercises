import logging
# import hashlib
from reedsolo import RSCodec, ReedSolomonError  # Import Reed-Solomon library
import ast
import numpy as np
import threading

class WatchdogTimer:
    def __init__(self, timeout, fallback_value):
        self.timeout = timeout
        self.fallback_value = fallback_value
        self.timer = None

    def start(self, func, *args):
        """
        Runs a function with a timeout. Returns function result or fallback value if timeout occurs.
        """
        result = [self.fallback_value]  # Default to fallback if timeout occurs

        def wrapper():
            try:
                result[0] = func(*args)
            except Exception as e:
                logging.error(f"Watchdog detected error: {e}")
                result[0] = self.fallback_value  # Fault isolation: use fallback

        thread = threading.Thread(target=wrapper)
        thread.start()
        thread.join(self.timeout)  # Wait for completion up to timeout

        if thread.is_alive():
            logging.error("Watchdog timeout: Function took too long.")
            return self.fallback_value  # Return degraded functionality

        return result[0]


parameters_rs = np.empty(4, dtype=object)

def count_objects_without_fault_tolerance(image, width, height, threshold):
    '''
    Fault-tolerant object counting in an image matrix.

    Input Parameters:
        image = Matrix with dimensions 'width' and 'height' (List of floats)
        width = Width of the image (int)
        height = Height of the image (int)
        threshold = Threshold value to detect objects (float)
    '''
    def bfs(x, y):

        queue = [(x, y)]
        visited.add((x, y))

        while queue:
            cx, cy = queue.pop(0)
            for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
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


def tmr_safe_execution(func, timeout,fallback_value, *args):
    """
        Executes a function 3 times under watchdog monitoring and returns the majority result.
        If all executions fail, it returns the fallback value.
        """
    watchdog = WatchdogTimer(timeout, fallback_value)
    results = [watchdog.start(func, *args) for _ in range(3)]

    # Remove invalid results (fallback value) before taking the majority vote
    valid_results = [r for r in results if r != fallback_value]

    if not valid_results:
        logging.error("All executions failed. Using degraded functionality.")
        return fallback_value  # Graceful degradation

    return max(set(valid_results), key=valid_results.count)  # Majority vote


# Initialize Reed-Solomon codec (can correct up to 4 symbol errors)
rs = RSCodec(10)

def encode_rs(data):
    """Encodes data using Reed-Solomon for error correction."""
    return rs.encode(bytearray(str(data), 'utf-8'))


# Store last known good values for fallback
last_valid_values = {}


def decode_rs(encoded_data, param_name):
    """Decodes and corrects data using Reed-Solomon."""
    try:
        decoded_bytes = rs.decode(encoded_data)
        if isinstance(decoded_bytes, tuple):
            decoded_bytes = decoded_bytes[0]  # Extract actual corrected data
        result = decoded_bytes.decode('utf-8')

        # Store last valid value for fallback
        last_valid_values[param_name] = result
        return result

    except ReedSolomonError:
        logging.error(f"Soft error detected in '{param_name}', unable to correct.")

        # Fault Isolation: Use last valid value instead of returning None
        if param_name in last_valid_values:
            logging.warning(f"Using last known good value for '{param_name}'.")
            return last_valid_values[param_name]

        return None  # Graceful Degradation: No valid fallback

def compare_rs(data,encoded_data,param_name):
    b = decode_rs(encoded_data,param_name)
    try:
        b = ast.literal_eval(str(b))  # Ensure it is correctly parsed as a Python object
    except (ValueError, SyntaxError):
        logging.error(f"Failed to evaluate decoded data for {param_name}, using original.")
        return data

    if b == data:
        return data
    else:
        return b


# Configure logging
logging.basicConfig(level=logging.ERROR, format="%(asctime)s - %(levelname)s - %(message)s")



def count_objects_with_fault_tolerance(image, width, height, threshold):

    '''
    Input Parameters:
        image = Matrix with dimensions 'width' and 'height' (list with lists of floats)
        width = Width of the image (int)
        height = Height of the image (int)
        threshold = Threshold value to detect objects (float)
    '''
    if not isinstance(image, list) or not all(isinstance(row, list) for row in image):
        logging.error("Invalid image format: Image must be a list of lists.")
        return -1

    if not len(image) > 0:
        logging.error("Invalid image data: Image is empty.")
        return -1

    if not all(isinstance(val, float) and val >= 0 for row in image for val in row):
        logging.error("Invalid image data: All values must be positive integers or floats.")
        return -1

    if len(image) != height or any(len(row) != width for row in image):
        logging.error("Dimension mismatch: Provided width/height do not match image structure.")
        return -1

    if not isinstance(threshold, float):
        logging.error("Invalid threshold: Must be a numerical value.")
        return -1

    # # Ensure successful recovery, else return failure state
    # if None in (image, width, height, threshold):
    #     return -1
    # Encode parameters using RS codes
    parameters_rs[0] = encode_rs(image)
    parameters_rs[1] = encode_rs(width)
    parameters_rs[2] = encode_rs(height)
    parameters_rs[3] = encode_rs(threshold)

    visited = set()
    object_count = 0
    object_count_rs = encode_rs(object_count)

    def bfs(x, y,visited_rs):
        try:
            queue = [(x, y)]
            # queue_rs= encode_rs(queue)


            # visited_temp = compare_rs(visited,visited_rs,"visited")
            # visited.clear()
            # visited.union(visited_temp)
            visited.add((x, y))
            # visited_rs = encode_rs(visited)

            while queue:
                # queue = compare_rs(queue, queue_rs, "queue")
                cx, cy = queue.pop(0)
                # queue_rs = encode_rs(queue)

                for dx, dy in [(0, 1), (1, 0), (-1, 0), (0, -1)]:
                    nx, ny = cx + dx, cy + dy

                    if (0 <= nx < compare_rs(height,parameters_rs[2],"height")
                            and 0 <= ny < compare_rs(width,parameters_rs[1],"width")
                            and (nx, ny) not in visited
                            and compare_rs(image,parameters_rs[0],"image")[nx][ny] > compare_rs(threshold,parameters_rs[3],"threshold") ):

                        # queue = compare_rs(queue, queue_rs, "queue")
                        queue.append((nx, ny))
                        # queue_rs = encode_rs(queue)

                        # visited_temp = compare_rs(visited, visited_rs, "visited")
                        # visited.clear()
                        # visited.union(visited_temp)
                        visited.add((nx, ny))
                        # visited_rs = encode_rs(visited)

        except Exception as e:
            logging.error(f"Error during BFS traversal: {e}") # Fault Isolation: if bfs crashes, it's only the function, not the whole process
            return -1

    try:
        for i in range(compare_rs(height,parameters_rs[2],"height") ):
            for j in range(compare_rs(width,parameters_rs[1],"width")):
                visited_rs = encode_rs(visited)
                if image[i][j] > compare_rs(threshold,parameters_rs[3],"threshold") and (i, j) not in visited:
                    bfs(i, j, visited_rs)

                    object_count = compare_rs(object_count,object_count_rs,"object_count")
                    object_count += 1
                    object_count_rs = encode_rs(object_count)

        return object_count
    except Exception as e:
        logging.error(f"Unexpected error in count_objects: {e}")
        return -1  # Graceful Degradation


# Sample Test Cases
def FR5():
    test_cases = [

        ([[0.2, 0.2], [0.2, 0.2]], 2, 2, 0.1), #TC1
        ([[0.2, 0.2], [0.2, 0.2]], 2, 2, 0.3), #TC2
        ([[0.2]], 1, 1, 0.1), #TC3
        ([[1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0]], 3, 3, 0.1), #TC4
        ([[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]], 3, 3, 0.1), #TC5
        ([], 0, 0, 0.1),  # Edge case: empty image
        ([[0.2, "X"], [0.2, 0.2]], 2, 2, 0.1),  # Invalid data

    ]
    # # Execute without fault tolerance
    # for i, (image, width, height, threshold) in enumerate(test_cases):
    #     print(f"Test Case {i + 1}: {count_objects_without_fault_tolerance(image, width, height, threshold)}")

    # Watchdog parameters
    timeout = 2  # Max time per function execution (seconds)
    fallback_value = -1  # Fallback value if all executions fail

    # Execute with fault tolerance
    for i, (image, width, height, threshold) in enumerate(test_cases):

        #print(compare_rs(image,parameters_rs[0],"width"))
        print(f"Test Case {i + 1}: {tmr_safe_execution(count_objects_with_fault_tolerance, timeout, fallback_value, image, width, height, threshold)}")





# # ## TC1 ##
#     image = [ [ 0.2, 0.2 ], [ 0.2, 0.2 ] ]
#     width = 2
#     height = 2
#     threshold = 0.1
#     print(count_objects(image, width, height, threshold))
#     # ## TC2 ##
#     image = [[0.2, 0.2], [0.2, 0.2]]
#     width =2
#     height = 2
#     threshold = 0.3
#     print(count_objects(image, width, height, threshold))
#     # ## TC3 ##
#     image = [[0.2]]
#     width = 1
#     height = 1
#     threshold = 0.1
#     print(count_objects(image, width, height, threshold))
#     ## TC4 ##
#     image = [[1.0, 0.0, 0.0], [0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]
#     width = 3
#     height = 3
#     threshold = 0.1
#     print(count_objects(image, width, height, threshold))
#     # ## TC5 ##
#     image = [[1.0, 1.0, 1.0], [1.0, 1.0, 1.0], [1.0, 1.0, 1.0]]
#     width = 3
#     height = 3
#     threshold = 0.1
#     print(count_objects(image, width, height, threshold))



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    #FR4()
    FR5()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/



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

# Versao sem Fault Tolerance




