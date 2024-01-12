import pygame
import random
import numpy as np
import sys

pygame.init()

# Створення шрифту для текстового поля
font = pygame.font.Font(None, 24)

# Клас для представлення міст
class City:
    def __init__(self, x, y, name):
        self.x = x
        self.y = y
        self.name = name

# Клас для представлення маршруту
class Route:
    def __init__(self, city_indices, cities):
        self.city_indices = city_indices
        self.distance = self.calculate_distance(cities)

    def calculate_distance(self, cities):
        total_distance = 0
        for i in range(len(self.city_indices) - 1):
            city1 = cities[self.city_indices[i]]
            city2 = cities[self.city_indices[i + 1]]
            total_distance += np.linalg.norm(np.array([city1.x, city1.y]) - np.array([city2.x, city2.y]))
        return total_distance

    def __repr__(self):
        return str(self.city_indices)

# Функція для отримання об'єктів міст за індексами
def get_cities_by_indices(city_indices, all_cities):
    return [all_cities[index] for index in city_indices]
# Функція для відображення міст та маршруту
def draw_cities_and_routes(cities, routes, shortest_route_index):
    # Відображення міст
    for city in cities:
        pygame.draw.circle(screen, (0, 0, 255), (city.x, city.y), 5)

    # Відображення маршрутів
    for i, route in enumerate(routes):
        route_cities = [(city.x, city.y) for city in get_cities_by_indices(route.city_indices, cities)]
        if i == shortest_route_index:
            color = (255, 0, 0)
            width = 4
        else:
            color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
            width = 2
        pygame.draw.lines(screen, color, False, route_cities, width)

    # Обводка для найкоротшого маршруту
    if shortest_route_index is not None:
        shortest_route_cities = [(city.x, city.y) for city in get_cities_by_indices(routes[shortest_route_index].city_indices, cities)]
        pygame.draw.lines(screen, (255, 0, 0), False, shortest_route_cities, 6)

    # Відображення тексту (номерів міст) поверх інших елементів
    for city in cities:
        font = pygame.font.Font(None, 24)
        text = font.render(city.name, True, (0, 0, 0))
        screen.blit(text, (city.x + 10, city.y + 10))

# Функція для запуску генетичного алгоритму
# Функція для запуску генетичного алгоритму
def genetic_algorithm(num_generations, mutation_rate, num_cities):
    cities = [City(random.randint(50, 750), random.randint(50, 550), str(i + 1)) for i in range(num_cities)]
    population_size = 30
    population = [Route(random.sample(range(len(cities)), len(cities)), cities) for _ in range(population_size)]

    all_generations = []  # Зберігає всі покоління маршрутів

    for generation in range(num_generations):
        population = sorted(population, key=lambda route: route.distance)
        all_generations.append(list(population))  # Зберегти маршрути поточного покоління

        shortest_route_index = population.index(min(population, key=lambda route: route.distance))

        # Відображення маршрутів на інтерфейсі
        screen.fill((255, 255, 255))
        draw_cities_and_routes(cities, all_generations[generation], shortest_route_index)

        # Перевірка, чи всі міста вже відвідані
        if set(range(num_cities)) == set(all_generations[generation][shortest_route_index].city_indices):
            print("All cities visited. Stopping the algorithm.")
            break

        new_population = []

        for i in range(population_size):
            parent1, parent2 = np.random.choice(population[:10], 2, replace=False)

            # Crossover
            crossover_point = random.randint(0, len(parent1.city_indices) - 1)
            child_indices = parent1.city_indices[:crossover_point] + [index for index in parent2.city_indices if
                                                                      index not in parent1.city_indices[
                                                                                   :crossover_point]] + parent1.city_indices[
                                                                                                        crossover_point:] + [parent1.city_indices[0]]
            child_route = Route(child_indices, cities)

            # Mutation
            if random.uniform(0, 1) < mutation_rate:
                mutation_indices = random.sample(range(1, len(child_route.city_indices) - 1), 2)
                mutation_indices.sort()
                child_route.city_indices[mutation_indices[0]], child_route.city_indices[mutation_indices[1]] = \
                    child_route.city_indices[mutation_indices[1]], child_route.city_indices[mutation_indices[0]]

            new_population.append(child_route)

        population = new_population

        pygame.display.flip()

    # Додамо перехід в початкове місто в останню ітерацію
    all_generations[-1][shortest_route_index].city_indices.append(all_generations[-1][shortest_route_index].city_indices[0])

    # Відображення всіх маршрутів та виділення найкоротшого останнього покоління
    screen.fill((255, 255, 255))
    draw_cities_and_routes(cities, all_generations[-1], shortest_route_index)
    pygame.display.flip()

    # Збереження маршруту у файл
    save_route_to_file(all_generations[-1][shortest_route_index].city_indices, cities, 'optimal_route.txt')

    lengths = [route.distance for route in population]
    print(f"Shortest Route: {shortest_route_index + 1} (Length = {population[shortest_route_index].distance:.2f})")

    # Save lengths to a text file
    save_lengths_to_file(lengths, 'route_lengths.txt')

# Функція для збереження маршруту у файл
def save_route_to_file(route, cities, filename):
    with open(filename, 'w') as file:
        for city_index in route:
            city = cities[city_index]
            file.write(f'{city.name}\n')

def save_lengths_to_file(lengths, filename):
    with open(filename, 'w') as file:
        for i, length in enumerate(lengths):
            file.write(f"Route {i + 1}: Length = {length:.2f}\n")

# Отримання введення від користувача через вікно Pygame
def get_user_input():
    user_input = {}
    user_input['num_cities'] = int(input_field("Enter the number of cities: ", (10, 10)))
    user_input['num_iterations'] = int(input_field("Enter the number of iterations: ", (10, 60)))
    user_input['mutation_rate'] = float(input_field("Enter the mutation rate: ", (10, 110)))
    return user_input

# Функція для введення текстового поля через вікно Pygame
def input_field(prompt, pos):
    text = ''
    input_rect = pygame.Rect(pos[0], pos[1], 140, 32)
    color_active = pygame.Color('gray15')
    color_passive = pygame.Color('lightskyblue3')
    color = color_passive
    active = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = not active
                else:
                    active = False
                color = color_active if active else color_passive
            if event.type == pygame.KEYDOWN:
                if active:
                    if event.key == pygame.K_RETURN:
                        return text
                    elif event.key == pygame.K_BACKSPACE:
                        text = text[:-1]
                    else:
                        text += event.unicode

        screen.fill((250, 250, 250))
        txt_surface = font.render(prompt + text, True, color)
        width = max(200, txt_surface.get_width()+10)
        input_rect.w = width
        screen.blit(txt_surface, (input_rect.x+5, input_rect.y+5))
        pygame.draw.rect(screen, color, input_rect, 2)
        pygame.display.flip()
        pygame.time.wait(30)

# Створення вікна Pygame
screen = pygame.display.set_mode((1200, 900))
pygame.display.set_caption("Genetic Algorithm - Traveling Salesman Problem")

# Отримання введення від користувача
user_input = get_user_input()

# Запуск генетичного алгоритму
genetic_algorithm(user_input['num_iterations'], user_input['mutation_rate'], user_input['num_cities'])

# Очікування закриття вікна Pygame
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
