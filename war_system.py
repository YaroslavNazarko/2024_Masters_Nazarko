import random
import matplotlib.pyplot as plt

# Налаштування симуляції
NUM_ORGANISMS_A = 100
NUM_ORGANISMS_B = 90
NUM_ITERATIONS = 50
RESOURCE_GENERATION = 20
RESOURCE_COST = 10
RESOURCE_REPRODUCTION_COST_A = 21
RESOURCE_REPRODUCTION_COST_B = 60
RESOURCE_EXPIRATION = 3
EXPIRED = 8
MUTATION_RATE = 0.1
PREDATION_THRESHOLD = 4
STARTING_RESOURCES = 160
PREDATION_GAIN = 40
ESCAPE_CHANCE = 0.3 # Шанс втечі
COUNTERATTACK_CHANCE_FACTOR = 0.1  # Коефіцієнт для розрахунку шансу контратаки

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
        self.efficiency = efficiency
        self.resources = STARTING_RESOURCES
        self.no_resources_turns = 0
        self.reproduction_ready_turns = 0
        self.time_since_last_reproduction = 0
        self.reproduction_cost = reproduction_cost
        self.age = 0

    def age_one_turn(self):
        self.age += 1

    def is_expired(self):
        return self.age > EXPIRED
    def compete(self, available_resources):
        needed = max(RESOURCE_COST, self.efficiency)
        gained = self.efficiency*available_resources
        self.resources += gained
        return gained

    def can_reproduce(self):
        return self.reproduction_ready_turns >= 3

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
        return self.no_resources_turns >= 2

# Група A: стандартні організми
class OrganismA(Organism):
    def __init__(self, efficiency, reproduction_cost = RESOURCE_REPRODUCTION_COST_A):
        super().__init__(efficiency, RESOURCE_REPRODUCTION_COST_A)
    def can_reproduce(self):
        return self.reproduction_ready_turns >= 3
    def attempt_escape_or_counterattack(self, predator):
        if random.random() < ESCAPE_CHANCE:  # Шанс втечі
            predator.resources += self.resources
            self.resources = 0
            return "escaped"
        else:
            counterattack_chance = self.efficiency * COUNTERATTACK_CHANCE_FACTOR
            if random.random() < counterattack_chance:
                return "counterattack"
            return "attacked"

# Група B: хижаки
class OrganismB(Organism):
    def __init__(self, efficiency, reproduction_cost = RESOURCE_REPRODUCTION_COST_B):
        super().__init__(efficiency * 0.5, RESOURCE_REPRODUCTION_COST_B)

    def is_stressed(self):
        return self.resources < RESOURCE_COST or self.time_since_last_reproduction > PREDATION_THRESHOLD
    def can_reproduce(self):
        return self.reproduction_ready_turns >= 7
    def prey_on(self, victim):
        if True: #isinstance(victim, OrganismA):
            outcome = victim.attempt_escape_or_counterattack(self)
            if outcome == "escaped":
                return False  # Жертва втекла
            elif outcome == "counterattack":
                return "killed"  # Хижак помер через контратаку
            else:
                self.resources += victim.resources
                victim.resources = 0
                return True
        return False

# Ініціалізація популяції
population = [OrganismA(random.uniform(0.1, 1.0)) for _ in range(NUM_ORGANISMS_A)] + \
             [OrganismB(random.uniform(0.1, 1.0)) for _ in range(NUM_ORGANISMS_B)]
resources = [Resource(RESOURCE_GENERATION) for _ in range(RESOURCE_GENERATION)]
statistics = {"iteration": [], "population_size_a": [], "population_size_b": [], "average_efficiency_a": [], "average_efficiency_b": []}

# Основний цикл симуляції
for iteration in range(NUM_ITERATIONS):
    resources.extend(Resource(RESOURCE_GENERATION) for _ in range(RESOURCE_GENERATION))
    for resource in resources:
        resource.age_one_turn()
    resources = [r for r in resources if not r.is_expired()]
    total_available_resources = sum(r.amount for r in resources)

    random.shuffle(population)
    for organism in population:
        organism.age_one_turn()
        if total_available_resources <= 0:
            break
        gained_resources = organism.compete(total_available_resources)
        total_available_resources -= gained_resources

    predators = [o for o in population if isinstance(o, OrganismB) and o.is_stressed()]
    for predator in predators:
        victims = [o for o in population if isinstance(o, OrganismA)] 
        if not victims:
            break 
        victim = random.choice([o for o in population if isinstance(o, OrganismA)])
        result = predator.prey_on(victim)
        if result == "killed":
            population.remove(predator)
        elif result:
            population.remove(victim)

    for organism in population:
        organism.survive()
    population = [o for o in population if not o.is_dead() and not o.is_expired()]

    new_population = []
    for organism in population:
        organism.ready_for_reproduction()
        if organism.can_reproduce():
            new_population.append(organism.reproduce())
    population.extend(new_population)

    group_a = [o for o in population if isinstance(o, OrganismA)]
    group_b = [o for o in population if isinstance(o, OrganismB)]
    statistics["iteration"].append(iteration)
    statistics["population_size_a"].append(len(group_a))
    statistics["population_size_b"].append(len(group_b))
    statistics["average_efficiency_a"].append(sum(o.efficiency for o in group_a) / len(group_a) if group_a else 0)
    statistics["average_efficiency_b"].append(sum(o.efficiency for o in group_b) / len(group_b) if group_b else 0)

    if not group_a or not group_b:
        print(f"Популяція вимерла на {iteration}-й ітерації.")
        break
    if len(group_a)>10000 or len(group_b)>10000:
        print(f"Популяція перемножилась на {iteration}-й ітерації.")
        break

plt.figure(figsize=(12, 6))
plt.subplot(1, 2, 1)
plt.plot(statistics["iteration"], statistics["population_size_a"], label="Population A")
plt.plot(statistics["iteration"], statistics["population_size_b"], label="Population B")
plt.xlabel("Iteration")
plt.ylabel("Population Size")
plt.title("Population Size Over Time")
plt.legend()

plt.subplot(1, 2, 2)
plt.plot(statistics["iteration"], statistics["average_efficiency_a"], label="Efficiency A", color="blue")
plt.plot(statistics["iteration"], statistics["average_efficiency_b"], label="Efficiency B", color="red")
plt.xlabel("Iteration")
plt.ylabel("Average Efficiency")
plt.title("Average Efficiency Over Time")
plt.legend()

plt.tight_layout()
plt.show()
