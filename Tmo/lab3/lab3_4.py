import numpy as np

P = np.array([[2, 5, 3, 4],
              [8, 5, 4, 2],
              [5, 4, 3, 2],
              [1, 5, 4, 4]])

P = P / P.sum(axis=1, keepdims=True)

states = ['Healthy', 'Unwell', 'Sick', 'Very sick']

def simulate_markov_chain(P, states, initial_state, n_iterations):
    current_state = states.index(initial_state)
    chain = [states[current_state]]
    for _ in range(n_iterations):
        next_state = np.random.choice(len(states), p=P[current_state])
        chain.append(states[next_state])
        current_state = next_state
    return chain

initial_state = 'Healthy'
n_iterations = 200
simulated_states = simulate_markov_chain(P, states, initial_state, n_iterations)
print("Матрица переходов:")
print(P)
print("\nСимуляция:")
print(simulated_states)
