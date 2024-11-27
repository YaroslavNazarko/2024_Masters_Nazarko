import subprocess

def display_menu():
    print("\n=== Меню симуляції ===")
    print("1. Налаштувати параметри та запустити симуляцію")
    print("2. Вийти")
    choice = input("Введіть номер опції: ")
    return choice

def get_simulation_settings():
    print("\n=== Налаштування симуляції ===")
    try:
        num_organisms_a = int(input("Кількість організмів групи A: "))
        num_organisms_b = int(input("Кількість організмів групи B: "))
        num_iterations = int(input("Кількість ітерацій: "))
        resource_generation = int(input("Кількість нових ресурсів на ітерацію: "))
        resource_cost = int(input("Кількість ресурсів для виживання: "))
        resource_reproduction_cost_a = int(input("Кількість ресурсів для розмноження (група A): "))
        resource_reproduction_cost_b = int(input("Кількість ресурсів для розмноження (група B): "))
        resource_expiration = int(input("Термін придатності ресурсів (у ітераціях): "))
        predation_gain = int(input("Кількість ресурсів, отриманих при хижацтві: "))
        predation_threshold = int(input("Поріг голоду для хижацтва (у ітераціях): "))
        mutation_rate = float(input("Шанс мутації (напр., 0.1): "))
        escape_chance = float(input("Шанс втечі (напр., 0.5): "))
        counterattack_factor = float(input("Фактор контратаки (напр., 0.1): "))

        settings = {
            "NUM_ORGANISMS_A": num_organisms_a,
            "NUM_ORGANISMS_B": num_organisms_b,
            "NUM_ITERATIONS": num_iterations,
            "RESOURCE_GENERATION": resource_generation,
            "RESOURCE_COST": resource_cost,
            "RESOURCE_REPRODUCTION_COST_A": resource_reproduction_cost_a,
            "RESOURCE_REPRODUCTION_COST_B": resource_reproduction_cost_b,
            "RESOURCE_EXPIRATION": resource_expiration,
            "PREDATION_GAIN": predation_gain,
            "PREDATION_THRESHOLD": predation_threshold,
            "MUTATION_RATE": mutation_rate,
            "ESCAPE_CHANCE": escape_chance,
            "COUNTERATTACK_CHANCE_FACTOR": counterattack_factor,
        }
        return settings
    except ValueError:
        print("\nПомилка: Введіть коректні числові значення.")
        return None

def write_settings_to_file(settings):
    with open("war_system_settings.py", "w") as f:
        for key, value in settings.items():
            f.write(f"{key} = {repr(value)}\n")
    print("\nНалаштування збережено у файлі war_system_settings.py.")

def run_simulation():
    print("\nЗапуск симуляції...")
    try:
        subprocess.run(["python", "war_system.py"])
    except FileNotFoundError:
        print("\nПомилка: Файл war_system.py не знайдено. Переконайтеся, що файл знаходиться у тій самій папці.")

# Основний цикл меню
while True:
    choice = display_menu()
    if choice == "1":
        settings = get_simulation_settings()
        if settings:
            write_settings_to_file(settings)
            run_simulation()
    elif choice == "2":
        print("\nВихід з меню.")
        break
    else:
        print("\nНеправильний вибір. Спробуйте знову.")
