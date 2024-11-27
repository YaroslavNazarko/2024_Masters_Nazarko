import random
import matplotlib.pyplot as plt

# Налаштування симуляції
NUM_ORGANISMS_A = 40  # Початкова кількість організмів групи A
NUM_ORGANISMS_B = 10  # Початкова кількість організмів групи B
NUM_ITERATIONS = 100  # Кількість ітерацій
RESOURCE_GENERATION = 50  # Ресурси, що додаються кожної ітерації
RESOURCE_COST = 10  # Мінімальна кількість ресурсів для виживання
RESOURCE_REPRODUCTION_COST_A = 20  # Ресурси для розмноження групи A
RESOURCE_REPRODUCTION_COST_B = 50  # Ресурси для розмноження групи B
RESOURCE_EXPIRATION = 4  # Термін придатності ресурсів (у ітераціях)
MUTATION_RATE = 0.1  # Ймовірність мутації
PREDATION_THRESHOLD = 5  # Кількість ітерацій без розмноження для активації хижацтва
STARTING_RESOURCES = 50  # Початковий запас ресурсів у кожного організму
PREDATION_GAIN = 40  # Кількість ресурсів, отриманих при хижацтві

# Клас для ресурсів
class Resource:
    def __init__(self, amount):
        self.amount = amount
        self.age = 0

    def age_one_turn(self):
        self.age += 1

    def is_expired(self):
        return self.age > RESOURCE_EXPIRATION

# Базовий клас для організмів
class Organism:
    def __init__(self, efficiency, reproduction_cost):
        self.efficiency = efficiency  # Ефективність отримання ресурсів
        self.resources = STARTING_RESOURCES  # Стартові ресурси
        self.no_resources_turns = 0  # Лічильник ітерацій без ресурсів
        self.reproduction_ready_turns = 0  # Лічильник ітерацій для розмноження
        self.time_since_last_reproduction = 0  # Лічильник ітерацій з останнього розмноження
        self.reproduction_cost = reproduction_cost  # Вимоги до ресурсів для розмноження

    def compete(self, available_resources):
        needed = max(RESOURCE_COST, self.efficiency)  # Мінімальна потреба
        gained = min(needed, available_resources)  # Ресурси, які можна отримати
        self.resources += gained
        return gained

    def can_reproduce(self):
        return self.reproduction_ready_turns >= 3  # Три ітерації накопичення достатніх ресурсів

    def ready_for_reproduction(self):
        if self.resources >= self.reproduction_cost:
            self.reproduction_ready_turns += 1
        else:
            self.reproduction_ready_turns = 0

    def reproduce(self):
        self.resources -= self.reproduction_cost
        self.reproduction_ready_turns = 0
        self.time_since_last_reproduction = 0
        new_efficiency = max(0.1, self.efficiency + random.uniform(-MUTATION_RATE, MUTATION_RATE))
        return self.__class__(new_efficiency, self.reproduction_cost)

    def survive(self):
        if self.resources >= RESOURCE_COST:
            self.resources -= RESOURCE_COST
            self.no_resources_turns = 0
        else:
            self.no_resources_turns += 1
        self.time_since_last_reproduction += 1

    def is_dead(self):
        return self.no_resources_turns >= 2  # Смерть після двох ітерацій без ресурсів

# Група A: стандартні організми
class OrganismA(Organism):
    def __init__(self, efficiency, reproduction_cost = RESOURCE_REPRODUCTION_COST_A):
        super().__init__(efficiency, RESOURCE_REPRODUCTION_COST_A)

# Група B: хижаки
class OrganismB(Organism):
    def __init__(self, efficiency, reproduction_cost = RESOURCE_REPRODUCTION_COST_B):
        super().__init__(efficiency * 0.5, RESOURCE_REPRODUCTION_COST_B)  # Зменшена ефективність для стандартних ресурсів

    def is_stressed(self):
        return self.resources < RESOURCE_COST or self.time_since_last_reproduction > PREDATION_THRESHOLD

    def prey_on(self, victim):
        if isinstance(victim, OrganismA) and victim.resources > 0:
            self.resources += PREDATION_GAIN
            victim.resources = 0  # Жертва вмирає
            return True
        return False

# Ініціалізація популяції
population = [OrganismA(random.uniform(0.1, 1.0)) for _ in range(NUM_ORGANISMS_A)] + \
             [OrganismB(random.uniform(0.1, 1.0)) for _ in range(NUM_ORGANISMS_B)]
resources = [Resource(RESOURCE_GENERATION) for _ in range(RESOURCE_GENERATION)]
statistics = {"iteration": [], "population_size_a": [], "population_size_b": [], "average_efficiency_a": [], "average_efficiency_b": []}

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

    # Хижацтво
    for predator in [o for o in population if isinstance(o, OrganismB) and o.is_stressed()]:
        victim = random.choice(population)
        if predator.prey_on(victim):
            population.remove(victim)

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
    group_a = [o for o in population if isinstance(o, OrganismA)]
    group_b = [o for o in population if isinstance(o, OrganismB)]
    statistics["iteration"].append(iteration)
    statistics["population_size_a"].append(len(group_a))
    statistics["population_size_b"].append(len(group_b))
    statistics["average_efficiency_a"].append(sum(o.efficiency for o in group_a) / len(group_a) if group_a else 0)
    statistics["average_efficiency_b"].append(sum(o.efficiency for o in group_b) / len(group_b) if group_b else 0)

    # Завершення, якщо популяція вимерла
    if not population:
        print(f"Популяція вимерла на {iteration}-й ітерації.")
        break

# Графічна візуалізація
plt.figure(figsize=(12, 6))

# Розмір популяції
plt.subplot(1, 2, 1)
plt.plot(statistics["iteration"], statistics["population_size_a"], label="Population A")
plt.plot(statistics["iteration"], statistics["population_size_b"], label="Population B")
plt.xlabel("Iteration")
plt.ylabel("Population Size")
plt.title("Population Size Over Time")
plt.legend()

# Середня ефективність
plt.subplot(1, 2, 2)
plt.plot(statistics["iteration"], statistics["average_efficiency_a"], label="Efficiency A", color="blue")
plt.plot(statistics["iteration"], statistics["average_efficiency_b"], label="Efficiency B", color="red")
plt.xlabel("Iteration")
plt.ylabel("Average Efficiency")
plt.title("Average Efficiency Over Time")
plt.legend()

plt.tight_layout()
plt.show()
