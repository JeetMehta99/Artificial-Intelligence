# Value and policy iteration on Grid World MDP
# Jeet Mehta
# 668581235

from math import inf
from sys import argv
from random import choice

class Square:
    def __init__(self, category, reward):
        self.category = category
        self.reward = reward
    
    def __repr__(self):
        return f"{self.category} ({self.reward})"

class MDP:
    def __init__(self, size, walls, terminal_states, reward, transition_prob, gamma, epsilon):
        self.size = size
        self.gamma = gamma
        self.epsilon = epsilon

        # Create world
        self.board = {}
        for i in range(size[0]):
            for j in range(size[1]):
                # Check if wall is encountered
                if (i, j) in walls:
                    self.board[(i, j)] = Square("wall", 0)
                
                # Check if current cell is a terminal state
                elif (i, j) in terminal_states:
                    self.board[(i, j)] = Square("terminal", terminal_states[(i, j)])
                
                # C
                else:
                    self.board[(i, j)] = Square("regular", reward)
        
        # Create transition model
        self.transition_model = {
            "up": {"up": transition_prob[0], "down": transition_prob[3], "left": transition_prob[1], "right": transition_prob[2]},
            "down": {"up": transition_prob[3], "down": transition_prob[0], "left": transition_prob[2], "right": transition_prob[1]},
            "left": {"up": transition_prob[2], "down": transition_prob[1], "left": transition_prob[0], "right": transition_prob[3]},
            "right": {"up": transition_prob[1], "down": transition_prob[2], "left": transition_prob[3], "right": transition_prob[0]}
        }

        #Function to move on the next state based on actions which include encountering a wall so that agent stays in same cell
    def move(self, state, action):
        if action == "up" and state[1] + 1 < self.size[1] and self.board[(state[0], state[1] + 1)].category not in "wall":
            return (state[0], state[1] + 1)
        elif action == "down" and state[1] - 1 >= 0 and self.board[(state[0], state[1] - 1)].category not in "wall":
            return (state[0], state[1] - 1)
        elif action == "left" and state[0] - 1 >= 0 and self.board[(state[0] - 1, state[1])].category not in "wall":
            return (state[0] - 1, state[1])
        elif action == "right" and state[0] + 1 < self.size[0] and self.board[(state[0] + 1, state[1])].category not in "wall":
            return (state[0] + 1, state[1])
        else:
            return state

    @classmethod
    def from_file(cls, filename):
        try:
            with open(filename) as f:
                for line in f:
                    
                    if line[0] == "#":
                        continue

                    # we split the lines on :
                    tokens = line.split(":")

                    # Parse size
                    if tokens[0].strip() == "size":
                        size = (int(tokens[1].strip().split(" ")[0]), int(tokens[1].strip().split(" ")[1]))
                    
                    # Parse walls
                    elif tokens[0].strip() == "walls":
                        walls = []
                        for wall in tokens[1].strip().split(","):
                            walls.append((int(wall.strip().split(" ")[0]) - 1, int(wall.strip().split(" ")[1]) - 1))
                    
                    # Parse terminal states
                    elif tokens[0].strip() == "terminal_states":
                        terminal_states = {}
                        for ts in tokens[1].strip().split(","):
                            terminal_states[(int(ts.strip().split(" ")[0]) - 1, int(ts.strip().split(" ")[1]) - 1)] = float(ts.strip().split(" ")[2])
                    
                    # Parse reward
                    elif tokens[0].strip() == "reward":
                        reward = float(tokens[1].strip())
                    
                    # Parse transition probabilities
                    elif tokens[0].strip() == "transition_probabilities":
                        transition_probabilities = (
                            float(tokens[1].strip().split(" ")[0]), float(tokens[1].strip().split(" ")[1]),
                            float(tokens[1].strip().split(" ")[2]), float(tokens[1].strip().split(" ")[3])
                        )
                    
                    # Parse discount rate
                    elif tokens[0].strip() == "discount_rate":
                        discount_rate = float(tokens[1].strip())
                    
                    # Parse epsilon
                    elif tokens[0].strip() == "epsilon":
                        epsilon = float(tokens[1].strip())

            return cls(size, walls, terminal_states, reward, transition_probabilities, discount_rate, epsilon)
        except Exception:
            return None
    
    def value_iteration(self):
        U = {}
        Up = {}
        delta = float('inf')
        models = []

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.board[(i, j)].category == "terminal":
                    Up[(i, j)] = self.board[(i, j)].reward
                else:
                    Up[(i, j)] = 0

        while delta > self.epsilon * (1 - self.gamma) / self.gamma:
            U = dict(Up)
            delta = 0
            for s in self.board:
                if self.board[s].category == "regular":
                    Up[s] = self.board[s].reward + self.gamma * max([
                        sum([self.transition_model[a][b] * U[self.move(s, b)] for b in ["up", "down", "left", "right"]])
                        for a in ["up", "down", "left", "right"]
                    ])

                # Update value of delta
                if abs(Up[s] - U[s]) > delta:
                    delta = abs(Up[s] - U[s])

            models.append(dict(Up))

            print(f"Iteration {len(models)}:")
            self.actionOfModel(Up)
            
        # Define the actual policy
        policy = {}
        for s in Up:
            if self.board[s].category != "regular":
                continue

            best_act, best_val = None, -inf
            for a in ["up", "down", "left", "right"]:
                v = sum([self.transition_model[a][ap] * Up[self.move(s, ap)] for ap in ["up", "down", "left", "right"]])
                if v > best_val:
                    best_act = a
                    best_val = v

            policy[s] = best_act
        
        # Print policy to console
        print(f"Overall policy:")
        self.policy_iter(policy)
    
        return policy, models

    # Modified policy
    def policy_iteration(self):
        policy = {}
        U = {}
        Up = {}
        unchanged = False
        models = []

        for i in range(self.size[0]):
            for j in range(self.size[1]):
                if self.board[(i, j)].category == "wall":
                    Up[(i, j)] = 0
                elif self.board[(i, j)].category == "terminal":
                    Up[(i, j)] = self.board[(i, j)].reward

                else:
                    policy[(i, j)] = choice(["up", "down", "left", "right"])
                    Up[(i, j)] = 0
        
        # Policy iteration
        while not unchanged:
            unchanged = True

            # Evaluate policy
            delta = float('inf')
            while delta > self.epsilon * (1 - self.gamma) / self.gamma:
                U = dict(Up)
                delta = 0

                for s in policy:
                    Up[s] = self.board[s].reward + self.gamma * sum(
                        [self.transition_model[policy[s]][ap] * U[self.move(s, ap)] for ap in ["up", "down", "left", "right"]]
                    )
                    
                    # Delta is updated
                    if abs(Up[s] - U[s]) > delta:
                        delta = abs(Up[s] - U[s])

            for s in policy:
                policy_val = sum([self.transition_model[policy[s]][ap] * Up[self.move(s, ap)] for ap in ["up", "down", "left", "right"]])
                best_act, best_val = None, -inf
                for a in ["up", "down", "left", "right"]:
                    v = sum([self.transition_model[a][ap] * Up[self.move(s, ap)] for ap in ["up", "down", "left", "right"]])
                    if v > best_val:
                        best_act = a
                        best_val = v
                
                if best_val > policy_val:
                    policy[s] = best_act
                    unchanged = False
            
            models.append(dict(Up))

            print(f"Iteration {len(models)}:")
            self.actionOfModel(Up)
        
        print(f"Overall policy:")
        self.policy_iter(policy)
        
        return policy, models

    def actionOfModel(self, model):
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                print(f"{model[(j, self.size[1] - 1 - i)]:+.4f} ", end="")
            print()
        print()

    def policy_iter(self, policy):
        for i in range(self.size[1]):
            for j in range(self.size[0]):
                print(f"{policy[(j, self.size[1] - 1 - i)] if (j, self.size[1] - 1 - i) in policy else '-':^7}", end="")
            print()
        print()

if __name__ == "__main__":
    if len(argv) < 3:
        print("Usage: python mdp.py [inputfile.txt] [iteration v or p] [list of states]")
        exit()
    
    # Create MDP
    mdp = MDP.from_file(argv[1])
    if mdp is None:
        print("Error! Insufficient args to create MDP")
        exit()

    # Select iteration i.e value(-v) or policy(-p)
    if argv[2] == "-v":
        policy, models = mdp.value_iteration()

    elif argv[2] == "-p":
        policy, models = mdp.policy_iteration()
    else:
        print("iteration provided is incorrect")
        exit()