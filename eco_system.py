import random
import matplotlib.pyplot as plt

# Налаштування симуляції
NUM_ORGANISMS = 50  # Початкова кількість організмів
NUM_ITERATIONS = 100  # Кількість ітерацій
RESOURCE_GENERATION = 10  # Ресурси, що додаються кожної ітерації
RESOURCE_COST = 10  # Мінімальна кількість ресурсів для виживання
RESOURCE_REPRODUCTION_COST = 30  # Ресурси для розмноження
RESOURCE_EXPIRATION = 4  # Термін придатності ресурсів (у ітераціях)
MUTATION_RATE = 0.1  # Ймовірність мутації
PREDATION_RATE = 0.5  # Частка ресурсів, яку хижак забирає у жертви
STARTING_RESOURCES = 0  # Початковий запас ресурсів у кожного організму
PREDATION_THRESHOLD = 4  # Кількість ітерацій без розмноження для активації хижацтва

# Клас для ресурсів
class Resource:
    def __init__(self, amount):
        self.amount = amount
        self.age = 0

    def age_one_turn(self):
        self.age += 1

    def is_expired(self):
        return self.age > RESOURCE_EXPIRATION

# Клас для організмів
class Organism:
    def __init__(self, efficiency):
        self.efficiency = efficiency  # Ефективність отримання ресурсів
        self.resources = STARTING_RESOURCES  # Стартові ресурси
        self.no_resources_turns = 0  # Лічильник ітерацій без ресурсів
        self.reproduction_ready_turns = 0  # Лічильник ітерацій для розмноження
        self.time_since_last_reproduction = 0  # Лічильник ітерацій з останнього розмноження

    def compete(self, available_resources):
        needed = max(RESOURCE_COST, self.efficiency)  # Мінімальна потреба
        gained = self.efficiency*available_resources  # Ресурси, які можна отримати
        self.resources += gained
        return gained

    def prey_on(self, victim):
        if victim.resources > 0:
            needed = max(RESOURCE_COST, RESOURCE_REPRODUCTION_COST - self.resources)
            stolen = min(needed, victim.resources)
            self.resources += stolen
            victim.resources -= stolen
            return stolen
        return 0

    def can_reproduce(self):
        return self.reproduction_ready_turns >= 3  # Три ітерації накопичення достатніх ресурсів

    def ready_for_reproduction(self):
        if self.resources >= RESOURCE_REPRODUCTION_COST:
            self.reproduction_ready_turns += 1
        else:
            self.reproduction_ready_turns = 0

    def reproduce(self):
        self.resources -= RESOURCE_REPRODUCTION_COST
        self.reproduction_ready_turns = 0
        self.time_since_last_reproduction = 0
        new_efficiency = max(0.1, self.efficiency + random.uniform(-MUTATION_RATE, MUTATION_RATE))
        return Organism(new_efficiency)

    def survive(self):
        if self.resources >= RESOURCE_COST:
            self.resources -= RESOURCE_COST
            self.no_resources_turns = 0
        else:
            self.no_resources_turns += 1
        self.time_since_last_reproduction += 1

    def is_dead(self):
        return self.no_resources_turns >= 2  # Смерть після двох ітерацій без ресурсів

    def is_stressed(self):
        return (
            self.resources < RESOURCE_COST
            or self.time_since_last_reproduction > PREDATION_THRESHOLD
        )

# Ініціалізація популяції
population = [Organism(random.uniform(0.1, 1.0)) for _ in range(NUM_ORGANISMS)]
resources = [Resource(RESOURCE_GENERATION) for _ in range(RESOURCE_GENERATION)]
statistics = {"iteration": [], "population_size": [], "average_efficiency": []}

# Основний цикл симуляції
for iteration in range(NUM_ITERATIONS):
    # Генерація нових ресурсів
    resources.extend(Resource(RESOURCE_GENERATION) for _ in range(RESOURCE_GENERATION))

    # Старіння ресурсів
    for resource in resources:
        resource.age_one_turn()

    # Видалення прострочених ресурсів
    resources = [r for r in resources if not r.is_expired()]

    # Підрахунок доступних ресурсів
    total_available_resources = sum(r.amount for r in resources)

    # Конкуренція за ресурси
    random.shuffle(population)
    for organism in population:
        if total_available_resources <= 0:
            break
        gained_resources = organism.compete(total_available_resources)
        total_available_resources -= gained_resources

    # Хижацтво для стресових організмів
    for predator in population:
        if predator.is_stressed():  # Хижак активується лише у стресовому стані
            victim = random.choice(population)
            if predator != victim:
                predator.prey_on(victim)

    # Виживання та смерть
    for organism in population:
        organism.survive()
    population = [o for o in population if not o.is_dead()]

    # Розмноження
    new_population = []
    for organism in population:
        organism.ready_for_reproduction()
        if organism.can_reproduce():
            new_population.append(organism.reproduce())
    population.extend(new_population)

    # Збір статистики
    average_efficiency = sum(o.efficiency for o in population) / len(population) if population else 0
    statistics["iteration"].append(iteration)
    statistics["population_size"].append(len(population))
    statistics["average_efficiency"].append(average_efficiency)

    # Завершення, якщо популяція вимерла
    if not population:
        print(f"Популяція вимерла на {iteration}-й ітерації.")
        break

# Графічна візуалізація
plt.figure(figsize=(12, 6))

# Розмір популяції
plt.subplot(1, 2, 1)
plt.plot(statistics["iteration"], statistics["population_size"], label="Population Size")
plt.xlabel("Iteration")
plt.ylabel("Population Size")
plt.title("Population Size Over Time")
plt.legend()

# Середня ефективність
plt.subplot(1, 2, 2)
plt.plot(statistics["iteration"], statistics["average_efficiency"], label="Average Efficiency", color="orange")
plt.xlabel("Iteration")
plt.ylabel("Average Efficiency")
plt.title("Average Efficiency Over Time")
plt.legend()

plt.tight_layout()
plt.show()
