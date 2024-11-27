import numpy as np
import matplotlib.pyplot as plt

def replicator_dynamics(payoff_matrix, initial_population, time_steps):
    """
    Симуляція динаміки популяції на основі еволюційної гри.
    
    Parameters:
        payoff_matrix (np.ndarray): Матриця виплат (розмір nxn).
        initial_population (np.ndarray): Початковий розподіл популяції (довжина n).
        time_steps (int): Кількість ітерацій симуляції.
        
    Returns:
        populations (np.ndarray): Масив часток стратегій у часі.
    """
    population = np.array(initial_population)
    populations = [population]
    
    for _ in range(time_steps):
        fitness = payoff_matrix @ population  # Фітнес для кожної стратегії
        average_fitness = population @ fitness  # Середній фітнес у популяції
        population = population * fitness / average_fitness  # Реплікаторна динаміка
        population = population / population.sum()  # Нормалізація (сумарна частка = 1)
        populations.append(population)
    
    return np.array(populations)

# Нова матриця виплат для трьох стратегій
payoff_matrix = np.array([
    [3, 0],  # Виграші для стратегії "Кооперація"
    [5, 1]   # Виграші для стратегії "Зрада"
])

# Початковий розподіл між трьома стратегіями
initial_population = [0.2, 0.8]  # Третина популяції для кожної стратегії
time_steps = 10  # Кількість ітерацій

# Виконання симуляції
populations = replicator_dynamics(payoff_matrix, initial_population, time_steps)

# Візуалізація результатів
plt.figure(figsize=(10, 6))
for i in range(populations.shape[1]):
    plt.plot(range(time_steps + 1), populations[:, i], label=f"Стратегія {i + 1}")

plt.title("Еволюція часток стратегій")
plt.xlabel("Кроки часу")
plt.ylabel("Частка в популяції")
plt.legend()
plt.grid()
plt.show()
