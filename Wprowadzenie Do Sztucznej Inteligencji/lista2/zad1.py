import heapq
import random
from typing import List, Tuple, Set
import matplotlib.pyplot as plt
from statistics import mean

# Ustawiamy rozmiar planszy 3x3
SIZE = 3

# Definiujemy stan docelowy układanki - liczby od 1 do 8, ostatnie pole to 0 (puste miejsce)
GOAL_STATE = tuple(range(1, SIZE * SIZE)) + (0,)

# Ruchy możliwe do wykonania: góra, dół, lewo, prawo
MOVES = {'U': -SIZE, 'D': SIZE, 'L': -1, 'R': 1}

# Funkcja sprawdzająca, czy dana układanka jest rozwiązywalna (parzysta liczba inwersji)
def is_solvable(puzzle: Tuple[int]) -> bool:
    inv_count = sum(
        1
        for i in range(len(puzzle))
        for j in range(i + 1, len(puzzle))
        if puzzle[i] and puzzle[j] and puzzle[i] > puzzle[j]
    )
    return inv_count % 2 == 0

# Generowanie losowego, rozwiązywalnego stanu początkowego
def generate_start_state() -> Tuple[int]:
    puzzle = list(GOAL_STATE)
    while True:
        random.shuffle(puzzle)
        if is_solvable(tuple(puzzle)) and puzzle.index(0) == SIZE * SIZE - 1:
            return tuple(puzzle)

# Heurystyka: Manhattan Distance
# Suma odległości każdego kafelka od jego docelowej pozycji (tylko ruchy poziome i pionowe)
# Manhattan Distance = |x1 - x2| + |y1 - y2|
# Ta heurystyka dobrze ocenia minimalną liczbę ruchów potrzebnych do przesunięcia kafelka na miejsce.
def manhattan(state: Tuple[int]) -> int:
    distance = 0
    for idx, value in enumerate(state):
        if value == 0:
            continue
        target_idx = value - 1
        x1, y1 = divmod(idx, SIZE)
        x2, y2 = divmod(target_idx, SIZE)
        distance += abs(x1 - x2) + abs(y1 - y2)
    return distance

# Heurystyka: Misplaced Tiles
# Liczy liczbę kafelków, które nie znajdują się w swojej docelowej pozycji.
# Ta heurystyka jest mniej dokładna niż Manhattan, bo nie uwzględnia odległości, tylko sam fakt, że kafelek jest nie na miejscu.
def misplaced(state: Tuple[int]) -> int:
    return sum(1 for i, val in enumerate(state) if val != 0 and val != GOAL_STATE[i])

# Generowanie wszystkich sąsiadów stanu poprzez przesunięcie pustego pola w dozwolonym kierunku.
def get_neighbors(state: Tuple[int]) -> List[Tuple[str, Tuple[int]]]:
    neighbors = []
    zero_index = state.index(0)
    x, y = divmod(zero_index, SIZE)
    for move, delta in MOVES.items():
        new_index = zero_index + delta
        new_x, new_y = divmod(new_index, SIZE)
        if 0 <= new_x < SIZE and 0 <= new_y < SIZE:
            if abs(new_x - x) + abs(new_y - y) == 1:
                new_state = list(state)
                new_state[zero_index], new_state[new_index] = new_state[new_index], new_state[zero_index]
                neighbors.append((move, tuple(new_state)))
    return neighbors

# Algorytm A* szuka najkrótszej ścieżki od stanu początkowego do celu, minimalizując koszt ruchów + heurystyka.
def a_star(start: Tuple[int], heuristic_func) -> Tuple[List[str], int]:
    open_set = []
    heapq.heappush(open_set, (heuristic_func(start), 0, start, []))
    visited: Set[Tuple[int]] = set()

    while open_set:
        f, g, current, path = heapq.heappop(open_set)
        if current == GOAL_STATE:
            return path, len(visited)
        if current in visited:
            continue
        visited.add(current)
        for move, neighbor in get_neighbors(current):
            if neighbor in visited:
                continue
            heapq.heappush(open_set, (g + 1 + heuristic_func(neighbor), g + 1, neighbor, path + [move]))
    return [], len(visited)

# Testowanie algorytmu dla dwóch heurystyk.
if __name__ == '__main__':
    heuristics = {'Manhattan': manhattan, 'Misplaced': misplaced}
    trials = 20

    for name, heuristic in heuristics.items():
        lengths = []
        visited_counts = []
        print(f"\nHeurystyka: {name}")
        for i in range(trials):
            print(f"\nPróba {i + 1}/{trials}")
            start = generate_start_state()
            print("Stan początkowy:")
            for j in range(0, SIZE * SIZE, SIZE):
                print(start[j:j + SIZE])
            solution, visited = a_star(start, heuristic)
            print("Rozwiązanie:", solution)
            print("Liczba odwiedzonych stanów:", visited)
            lengths.append(len(solution))
            visited_counts.append(visited)

        x = list(range(1, trials + 1))

        plt.figure(figsize=(12, 5))

        # Wykres długości ścieżki do rozwiązania
        plt.subplot(1, 2, 1)
        plt.bar(x, lengths, color='skyblue')
        plt.axhline(mean(lengths), color='blue', linestyle='--', label=f'Średnia: {mean(lengths):.2f}')
        plt.title(f"{name}: Długość ścieżki")
        plt.xlabel("Numer próby")
        plt.ylabel("Liczba ruchów")
        plt.legend()

        # Wykres liczby odwiedzonych stanów
        plt.subplot(1, 2, 2)
        plt.bar(x, visited_counts, color='salmon')
        plt.axhline(mean(visited_counts), color='red', linestyle='--', label=f'Średnia: {mean(visited_counts):.2f}')
        plt.title(f"{name}: Liczba odwiedzonych stanów")
        plt.xlabel("Numer próby")
        plt.ylabel("Liczba stanów")
        plt.legend()

        plt.suptitle(f"Wyniki dla heurystyki: {name}", fontsize=14)
        plt.tight_layout()
        plt.show()
