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

# Налаштування гри "Полювання на оленя"
payoff_matrix = np.array([
    [3, 0],  # Виграші для "Оленя"
    [2, 2]   # Виграші для "Кролика"
])

# Початкові параметри
population = np.array([0.5, 0.5])  # 50% Олень, 50% Кролик
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
    ax.plot(range(time_step + 1), [p[0] for p in populations_over_time], label="Олень")
    ax.plot(range(time_step + 1), [p[1] for p in populations_over_time], label="Кролик")
    ax.set_title("Еволюція популяції (Полювання на оленя)")
    ax.set_xlabel("Крок часу")
    ax.set_ylabel("Частка в популяції")
    ax.legend()
    ax.grid()
    plt.draw()

# Функція для ручного оновлення популяції
def manual_update(event):
    global population, populations_over_time, time_step
    try:
        stag = float(textbox_stag.text)
        hare = float(textbox_hare.text)
        
        if not np.isclose(stag + hare, 1.0):
            raise ValueError("Сума має бути рівною 1.")
        if stag < 0 or hare < 0:
            raise ValueError("Частки не можуть бути від’ємними.")
        
        population = np.array([stag, hare])
        populations_over_time.append(population)
        time_step += 1

        # Оновлення графіка
        ax.clear()
        ax.plot(range(time_step + 1), [p[0] for p in populations_over_time], label="Олень")
        ax.plot(range(time_step + 1), [p[1] for p in populations_over_time], label="Кролик")
        ax.set_title("Еволюція популяції (Полювання на оленя)")
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
ax_textbox_stag = plt.axes([0.2, 0.3, 0.3, 0.05])
textbox_stag = TextBox(ax_textbox_stag, "Олень:", initial="0.5")

ax_textbox_hare = plt.axes([0.6, 0.3, 0.3, 0.05])
textbox_hare = TextBox(ax_textbox_hare, "Кролик:", initial="0.5")

# Ініціалізація графіка
ax.plot([0], [population[0]], label="Олень")
ax.plot([0], [population[1]], label="Кролик")
ax.set_title("Еволюція популяції (Полювання на оленя)")
ax.set_xlabel("Крок часу")
ax.set_ylabel("Частка в популяції")
ax.legend()
ax.grid()

plt.show()
