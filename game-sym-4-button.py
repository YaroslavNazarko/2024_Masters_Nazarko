import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Button, TextBox

# Функція для одного кроку реплікаторної динаміки
def step_replicator_dynamics(payoff_matrix, population):
    fitness = payoff_matrix @ population  # Фітнес для кожної стратегії
    average_fitness = population @ fitness  # Середній фітнес у популяції
    
    if average_fitness == 0:  # Уникнення ділення на нуль
        return population  # Повертаємо поточну популяцію без змін
    
    new_population = population * fitness / average_fitness  # Реплікаторна динаміка
    return new_population / new_population.sum()  # Нормалізація (сума часток = 1)

# Налаштування гри "Камінь, ножиці, папір"
payoff_matrix = np.array([
    [0, -1, 1],  # Камінь
    [1, 0, -1],  # Ножиці
    [-1, 1, 0]   # Папір
])

# Початкові параметри
population = np.array([0.33, 0.33, 0.33])  # Частка каменю, ножиць, паперу
time_step = 0
populations_over_time = [population]

# Функція для оновлення графіка
def update_graph(event):
    global population, time_step, populations_over_time
    population = step_replicator_dynamics(payoff_matrix, population)
    populations_over_time.append(population)
    time_step += 1

    # Оновлюємо графік
    ax.clear()
    ax.plot(range(time_step + 1), [p[0] for p in populations_over_time], label="Камінь")
    ax.plot(range(time_step + 1), [p[1] for p in populations_over_time], label="Ножиці")
    ax.plot(range(time_step + 1), [p[2] for p in populations_over_time], label="Папір")
    ax.set_title("Еволюція популяції (Камінь, ножиці, папір)")
    ax.set_xlabel("Крок часу")
    ax.set_ylabel("Частка в популяції")
    ax.legend()
    ax.grid()
    plt.draw()

# Функція для ручного оновлення популяції
def manual_update(event):
    global population, populations_over_time, time_step
    try:
        rock = float(textbox_rock.text)
        scissors = float(textbox_scissors.text)
        paper = float(textbox_paper.text)
        if not np.isclose(rock + scissors + paper, 1.0):
            raise ValueError("Сума має бути рівною 1.")
        population = np.array([rock, scissors, paper])
        populations_over_time.append(population)
        time_step += 1

        # Оновлення графіка
        ax.clear()
        ax.plot(range(time_step + 1), [p[0] for p in populations_over_time], label="Камінь")
        ax.plot(range(time_step + 1), [p[1] for p in populations_over_time], label="Ножиці")
        ax.plot(range(time_step + 1), [p[2] for p in populations_over_time], label="Папір")
        ax.set_title("Еволюція популяції (Камінь, ножиці, папір)")
        ax.set_xlabel("Крок часу")
        ax.set_ylabel("Частка в популяції")
        ax.legend()
        ax.grid()
        plt.draw()
    except ValueError as e:
        print(f"Помилка: {e}")

# Налаштування графіка
fig, ax = plt.subplots(figsize=(8, 5))
plt.subplots_adjust(bottom=0.4)

# Додавання кнопки для автоматичного оновлення
ax_button_auto = plt.axes([0.15, 0.05, 0.3, 0.075])
button_auto = Button(ax_button_auto, "Авто-крок")
button_auto.on_clicked(update_graph)

# Додавання кнопки для ручного оновлення
ax_button_manual = plt.axes([0.55, 0.05, 0.3, 0.075])
button_manual = Button(ax_button_manual, "Ручне оновлення")
button_manual.on_clicked(manual_update)

# Додавання текстових полів для введення нових часток
ax_textbox_rock = plt.axes([0.1, 0.3, 0.2, 0.05])
textbox_rock = TextBox(ax_textbox_rock, "Камінь:", initial="0.33")

ax_textbox_scissors = plt.axes([0.4, 0.3, 0.2, 0.05])
textbox_scissors = TextBox(ax_textbox_scissors, "Ножиці:", initial="0.33")

ax_textbox_paper = plt.axes([0.7, 0.3, 0.2, 0.05])
textbox_paper = TextBox(ax_textbox_paper, "Папір:", initial="0.34")

# Ініціалізація графіка
ax.plot([0], [population[0]], label="Камінь")
ax.plot([0], [population[1]], label="Ножиці")
ax.plot([0], [population[2]], label="Папір")
ax.set_title("Еволюція популяції (Камінь, ножиці, папір)")
ax.set_xlabel("Крок часу")
ax.set_ylabel("Частка в популяції")
ax.legend()
ax.grid()

plt.show()
