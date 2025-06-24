import heapq
import random
import matplotlib.pyplot as plt
from collections import deque, defaultdict

# Rozmiar planszy (4x4 dla Piętnastki)
N = 4

# Docelowy stan układanki (od 1 do 15, na końcu 0 jako puste pole)
GOAL_STATE = tuple(range(1, N * N)) + (0,)
GOAL_POS = {GOAL_STATE[i]: (i // N, i % N) for i in range(N * N)}

# Możliwe ruchy: góra, dół, lewo, prawo
MOVES = {
    'U': (-1, 0),  # przesunięcie w górę
    'D': (1, 0),   # przesunięcie w dół
    'L': (0, -1),  # przesunięcie w lewo
    'R': (0, 1),   # przesunięcie w prawo
}

# Funkcja generująca sąsiednie stany poprzez przesunięcie pustego pola
def get_neighbors(state):
    neighbors = []
    zero_index = state.index(0)
    zero_row, zero_col = divmod(zero_index, N)

    for move, (dr, dc) in MOVES.items():
        new_row, new_col = zero_row + dr, zero_col + dc
        if 0 <= new_row < N and 0 <= new_col < N:
            new_index = new_row * N + new_col
            new_state = list(state)
            # Zamiana pustego pola z sąsiadem
            new_state[zero_index], new_state[new_index] = new_state[new_index], new_state[zero_index]
            neighbors.append((move, tuple(new_state)))
    return neighbors

# Heurystyka Manhattan - suma odległości każdego kafelka od jego docelowej pozycji
# Mierzy minimalną liczbę ruchów potrzebnych do przesunięcia kafelka na miejsce
def manhattan_distance(state):
    return sum(
        abs((i // N) - GOAL_POS[val][0]) + abs((i % N) - GOAL_POS[val][1])
        for i, val in enumerate(state) if val != 0
    )

# Heurystyka Misplaced Tiles - liczba kafelków nie na swoich miejscach
# Mierzy ile kafelków jest źle ustawionych (nie uwzględnia odległości)
def misplaced_tiles(state):
    return sum(1 for i, val in enumerate(state) if val != 0 and val != GOAL_STATE[i])

# Algorytm A* - przeszukuje stany wybierając te z najniższym kosztem estymowanym
# Korzysta z heurystyki do przewidywania kosztu dojścia do celu
def a_star(start_state, heuristic_fn):
    frontier = []  # kolejka priorytetowa
    heapq.heappush(frontier, (heuristic_fn(start_state), 0, start_state, []))
    visited = set()
    visited.add(start_state)

    while frontier:
        est_total_cost, cost_so_far, current_state, path = heapq.heappop(frontier)

        # Jeśli osiągnęliśmy cel - zwracamy ścieżkę i liczbę odwiedzonych stanów
        if current_state == GOAL_STATE:
            return path, len(visited)

        # Przechodzimy po sąsiadach aktualnego stanu
        for move, neighbor in get_neighbors(current_state):
            if neighbor not in visited:
                visited.add(neighbor)
                new_cost = cost_so_far + 1
                est_cost = new_cost + heuristic_fn(neighbor)
                heapq.heappush(frontier, (est_cost, new_cost, neighbor, path + [move]))

    return None, len(visited)

# Generowanie losowego stanu początkowego przesuwając puste pole od celu
# Dzięki temu mamy pewność, że układanka jest rozwiązywalna
def generate_initial_state_from_goal(moves=30):
    state = GOAL_STATE
    path = []
    last_move = None
    reverse_move = {'U': 'D', 'D': 'U', 'L': 'R', 'R': 'L'}

    for _ in range(moves):
        neighbors = get_neighbors(state)
        if last_move:
            # Unikamy cofania ostatniego ruchu
            neighbors = [(m, s) for m, s in neighbors if m != reverse_move[last_move]]
        move, next_state = random.choice(neighbors)
        state = next_state
        path.append(move)
        last_move = move
    return state

# Funkcja wyświetlająca aktualny stan planszy w formacie 4x4
def print_board(state):
    for i in range(0, N * N, N):
        print(state[i:i+N])

# Tworzenie wykresów - długość ścieżki i liczba odwiedzonych stanów
def plot_results(name, steps_list, visited_list):
    trials = list(range(1, len(steps_list) + 1))

    plt.figure(figsize=(10, 4))

    # Wykres długości ścieżki
    plt.subplot(1, 2, 1)
    plt.plot(trials, steps_list, marker='o', label='Długość ścieżki')
    plt.axhline(sum(steps_list)/len(steps_list), color='r', linestyle='--', label='Średnia')
    plt.title(f'{name} - Długość ścieżki')
    plt.xlabel('Próba')
    plt.ylabel('Długość')
    plt.legend()

    # Wykres liczby odwiedzonych stanów
    plt.subplot(1, 2, 2)
    plt.plot(trials, visited_list, marker='o', color='orange', label='Odwiedzone stany')
    plt.axhline(sum(visited_list)/len(visited_list), color='r', linestyle='--', label='Średnia')
    plt.title(f'{name} - Liczba odwiedzonych stanów')
    plt.xlabel('Próba')
    plt.ylabel('Liczba stanów')
    plt.legend()

    plt.tight_layout()
    plt.show()

# Główna funkcja programu - testuje dwie heurystyki w 20 próbach i tworzy wykresy
def main():
    heuristics = [("Manhattan", manhattan_distance), ("Misplaced", misplaced_tiles)]
    trials = 20

    for name, heuristic in heuristics:
        print(f"\nHeurystyka: {name}")
        steps_list = []
        visited_list = []

        for t in range(trials):
            print(f"\nPróba {t+1}/{trials}")
            start_state = generate_initial_state_from_goal(30)
            print("Stan początkowy:")
            print_board(start_state)
            solution, visited = a_star(start_state, heuristic)
            print("Rozwiązanie:", solution)
            print("Liczba odwiedzonych stanów:", visited)
            steps_list.append(len(solution))
            visited_list.append(visited)

        print(f"Średnia długość ścieżki: {sum(steps_list) / trials:.2f}")
        print(f"Średnia liczba odwiedzonych stanów: {sum(visited_list) / trials:.2f}")

        plot_results(name, steps_list, visited_list)

# Uruchomienie programu\if __name__ == "__main__":
    main()
