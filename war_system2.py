import random
import tkinter as tk
from tkinter import messagebox
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox

# Налаштування симуляції
NUM_ORGANISMS_A = 100
NUM_ORGANISMS_B = 90
NUM_ITERATIONS = 1
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
iteration = 0
# Основний цикл симуляції
# for iteration in range(NUM_ITERATIONS):
    

# Function to show a popup on error
def show_error_popup(error_message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showerror("Error", error_message)

# Function to show a popup on error
def show_info_popup(error_message):
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    messagebox.showinfo("Info", error_message)

# Функція для оновлення популяції вручну
def manual_update(event):
    global population, resources, statistics,iteration
    try:
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
            show_error_popup(f"Популяція вимерла на {iteration}-й ітерації.")

        if len(group_a)>10000 or len(group_b)>10000:
            print(f"Популяція перемножилась на {iteration}-й ітерації.")
            show_error_popup(f"Популяція перемножилась на {iteration}-й ітерації.")
        # Оновлення графіка
        ax1.clear()
        ax1.plot(statistics["iteration"], statistics["population_size_a"], label="Population A")
        ax1.plot(statistics["iteration"], statistics["population_size_b"], label="Population B")
        ax1.set_title("Population Size Over Time")
        ax1.set_xlabel("Iteration")
        ax1.set_ylabel("Population Size")
        ax1.legend()
        ax1.grid()
        
        # Оновлення графіка
        ax2.clear()
        ax2.plot(statistics["iteration"], statistics["average_efficiency_a"], label="Efficiency A", color="blue")
        ax2.plot(statistics["iteration"], statistics["average_efficiency_b"], label="Efficiency B", color="red")

        ax2.set_title("Average Efficiency Over Time")
        ax2.set_xlabel("Iteration")
        ax2.set_ylabel("Average Efficiency")
        ax2.legend()
        ax2.grid()
        plt.draw()
        iteration+=1
    except ValueError as e:
        print(f"Помилка: {e}")

def restart_evolution(event):
    global population, resources, statistics,iteration  
      
    # # Налаштування симуляції
    # NUM_ORGANISMS_A = 100
    # NUM_ORGANISMS_B = 90
    # NUM_ITERATIONS = 1
    # RESOURCE_GENERATION = 20
    # RESOURCE_COST = 10
    # RESOURCE_REPRODUCTION_COST_A = 21
    # RESOURCE_REPRODUCTION_COST_B = 60
    # RESOURCE_EXPIRATION = 3
    # EXPIRED = 8
    # MUTATION_RATE = 0.1
    # PREDATION_THRESHOLD = 4
    # STARTING_RESOURCES = 160
    # PREDATION_GAIN = 40
    # ESCAPE_CHANCE = 0.3 # Шанс втечі
    # COUNTERATTACK_CHANCE_FACTOR = 0.1  # Коефіцієнт для розрахунку шансу контратаки

    population = [OrganismA(random.uniform(0.1, 1.0)) for _ in range(NUM_ORGANISMS_A)] + \
             [OrganismB(random.uniform(0.1, 1.0)) for _ in range(NUM_ORGANISMS_B)]
    resources = [Resource(RESOURCE_GENERATION) for _ in range(RESOURCE_GENERATION)]
    statistics = {"iteration": [], "population_size_a": [], "population_size_b": [], "average_efficiency_a": [], "average_efficiency_b": []}
    iteration = 0
    show_info_popup("Успішно розпочато")

def value_update(event):
    global NUM_ORGANISMS_A
    global NUM_ORGANISMS_B
    global NUM_ITERATIONS
    global RESOURCE_GENERATION
    global RESOURCE_COST
    global RESOURCE_REPRODUCTION_COST_A
    global RESOURCE_REPRODUCTION_COST_B
    global RESOURCE_EXPIRATION
    global EXPIRED
    global PREDATION_THRESHOLD
    global STARTING_RESOURCES
    global ESCAPE_CHANCE
    global MUTATION_RATE
    global COUNTERATTACK_CHANCE_FACTOR


    NUM_ORGANISMS_A = int(textbox_NUM_ORGANISMS_A.text)
    NUM_ORGANISMS_B = int(textbox_NUM_ORGANISMS_B.text)
    NUM_ITERATIONS = int(textbox_NUM_ITERATIONS.text)
    RESOURCE_GENERATION = int(textbox_RESOURCE_GENERATION.text)
    RESOURCE_COST = int(textbox_RESOURCE_COST.text)
    RESOURCE_REPRODUCTION_COST_A = int(textbox_RESOURCE_REPRODUCTION_COST_A.text)
    RESOURCE_REPRODUCTION_COST_B = int(textbox_RESOURCE_REPRODUCTION_COST_B.text)
    RESOURCE_EXPIRATION = int(textbox_RESOURCE_EXPIRATION.text)
    EXPIRED = int(textbox_EXPIRED.text)
    PREDATION_THRESHOLD = int(textbox_PREDATION_THRESHOLD.text)
    STARTING_RESOURCES = int(textbox_STARTING_RESOURCES.text)
    MUTATION_RATE = float(textbox_MUTATION_RATE.text)
    ESCAPE_CHANCE = float(textbox_ESCAPE_CHANCE.text)
    COUNTERATTACK_CHANCE_FACTOR = float(textbox_COUNTERATTACK_CHANCE_FACTOR.text)

    show_info_popup("Успішно оновлено")


plt.figure(figsize=(12, 8))
plt.subplots_adjust(bottom=0.4)  # Reserve space at the bottom for widgets

ax1 = plt.subplot(1, 2, 1)
plt.plot(statistics["iteration"], statistics["population_size_a"], label="Population A")
plt.plot(statistics["iteration"], statistics["population_size_b"], label="Population B")
plt.xlabel("Iteration")
plt.ylabel("Population Size")
plt.title("Population Size Over Time")
plt.legend()

ax2 = plt.subplot(1, 2, 2)
plt.plot(statistics["iteration"], statistics["average_efficiency_a"], label="Efficiency A", color="blue")
plt.plot(statistics["iteration"], statistics["average_efficiency_b"], label="Efficiency B", color="red")
plt.xlabel("Iteration")
plt.ylabel("Average Efficiency")
plt.title("Average Efficiency Over Time")
plt.legend()
# Adjust space for buttons/textboxes

# Налаштування симуляції
# NUM_ORGANISMS_A = 100
ax_textbox_NUM_ORGANISMS_A = plt.axes([0.1, 0.29, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_NUM_ORGANISMS_A = TextBox(ax_textbox_NUM_ORGANISMS_A, "К-ть А:", initial=NUM_ORGANISMS_A)

# NUM_ORGANISMS_B = 90
ax_textbox_NUM_ORGANISMS_B = plt.axes([0.1, 0.23, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_NUM_ORGANISMS_B = TextBox(ax_textbox_NUM_ORGANISMS_B, "К-ть B:", initial=NUM_ORGANISMS_B)

# NUM_ITERATIONS = 1
ax_textbox_NUM_ITERATIONS = plt.axes([0.1, 0.17, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_NUM_ITERATIONS = TextBox(ax_textbox_NUM_ITERATIONS, "Ітерацій:", initial=NUM_ITERATIONS)

# RESOURCE_GENERATION = 20
ax_textbox_RESOURCE_GENERATION = plt.axes([0.1, 0.11, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_RESOURCE_GENERATION = TextBox(ax_textbox_RESOURCE_GENERATION, "Ген. Ресурсів:", initial=RESOURCE_GENERATION)

# RESOURCE_COST = 10
ax_textbox_RESOURCE_COST = plt.axes([0.1, 0.05, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_RESOURCE_COST = TextBox(ax_textbox_RESOURCE_COST, "Ціна життя:", initial=RESOURCE_COST)

# RESOURCE_REPRODUCTION_COST_A = 21
ax_textbox_RESOURCE_REPRODUCTION_COST_A = plt.axes([0.4, 0.29, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_RESOURCE_REPRODUCTION_COST_A = TextBox(ax_textbox_RESOURCE_REPRODUCTION_COST_A, "Ціна Репродукції A:", initial=RESOURCE_REPRODUCTION_COST_A)

# RESOURCE_REPRODUCTION_COST_B = 60
ax_textbox_RESOURCE_REPRODUCTION_COST_B = plt.axes([0.4, 0.23, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_RESOURCE_REPRODUCTION_COST_B = TextBox(ax_textbox_RESOURCE_REPRODUCTION_COST_B, "Ціна Репродукції B:", initial=RESOURCE_REPRODUCTION_COST_B)

# RESOURCE_EXPIRATION = 3
ax_textbox_RESOURCE_EXPIRATION = plt.axes([0.4, 0.17, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_RESOURCE_EXPIRATION = TextBox(ax_textbox_RESOURCE_EXPIRATION, "Придатність Ресурсу:", initial=RESOURCE_EXPIRATION)

# EXPIRED = 8
ax_textbox_EXPIRED = plt.axes([0.4, 0.11, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_EXPIRED = TextBox(ax_textbox_EXPIRED, "Час життя Організму:", initial=EXPIRED)

# MUTATION_RATE = 0.1
ax_textbox_MUTATION_RATE = plt.axes([0.4, 0.05, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_MUTATION_RATE = TextBox(ax_textbox_MUTATION_RATE, "Фактор мутації:", initial=MUTATION_RATE)

# PREDATION_THRESHOLD = 4
ax_textbox_PREDATION_THRESHOLD = plt.axes([0.7, 0.29, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_PREDATION_THRESHOLD = TextBox(ax_textbox_PREDATION_THRESHOLD, "Грань хижака:", initial=PREDATION_THRESHOLD)

# STARTING_RESOURCES = 160
ax_textbox_STARTING_RESOURCES = plt.axes([0.7, 0.23, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_STARTING_RESOURCES = TextBox(ax_textbox_STARTING_RESOURCES, "Початкові рес:", initial=STARTING_RESOURCES)

# ESCAPE_CHANCE = 0.3 # Шанс втечі
ax_textbox_ESCAPE_CHANCE = plt.axes([0.7, 0.17, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_ESCAPE_CHANCE = TextBox(ax_textbox_ESCAPE_CHANCE, "Шанс втечі:", initial=ESCAPE_CHANCE)

# COUNTERATTACK_CHANCE_FACTOR = 0.1  # Коефіцієнт для розрахунку шансу контратаки
ax_textbox_COUNTERATTACK_CHANCE_FACTOR = plt.axes([0.7, 0.11, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
textbox_COUNTERATTACK_CHANCE_FACTOR = TextBox(ax_textbox_COUNTERATTACK_CHANCE_FACTOR, "Ко-ф. контратаки:", initial=COUNTERATTACK_CHANCE_FACTOR)

# Додавання кнопки для ручного оновлення
ax_button_manual = plt.axes([0.7, 0.05, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
button_manual = Button(ax_button_manual, "Крок Еволюції")
button_manual.on_clicked(manual_update)

ax_button_manual_u = plt.axes([0.58, 0.05, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
button_manual_u = Button(ax_button_manual_u, "Оновлення")
button_manual_u.on_clicked(value_update)


ax_button_manual_r = plt.axes([0.85, 0.05, 0.1, 0.05])  # [x, y, width, height] in figure coordinates
button_manual_r = Button(ax_button_manual_r, "Рестарт")
button_manual_r.on_clicked(restart_evolution)

# plt.tight_layout()
plt.show()
