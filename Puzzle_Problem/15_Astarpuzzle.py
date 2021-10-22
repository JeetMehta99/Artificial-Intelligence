#A Star Search on 15 Puzzle
#Jeet Mehta
#668581235

import sys
from psutil import Process
from time import time
from bisect import insort
import math

#Defines the node
class Node:
    def __init__(self, path, state, action, max_recursion_depth, cost, valueOfHeuristic):
        self.path = path
        self.state = state
        self.action = action
        self.max_recursion_depth = max_recursion_depth
        self.cost = cost
        self.valueOfHeuristic = valueOfHeuristic
    def __lt__(self,other):
        return (self.cost + self.valueOfHeuristic) < (other.cost + other.valueOfHeuristic)

#Defines state 
class board:
    def __init__(self, size, curr_state,time, recursion):
        self.size = size
        self. curr_state = curr_state
        self.time = time
        self.recursion = recursion
        self.constant = list(range(1, self.size ** 2)) + [0]

    @classmethod
    def from_string(cls):
        try:
            size = int(input("Puzzle size:"))
            input_string = input("Input initial state: ")
            inp = input_string.split(" ")
            intInp = []
            for i in inp:
                intInp.append(int(i))
            curr_state = []
            for i in range(size**2):
                curr_state.append(intInp[i])
            time = float(input("Time:"))
            recursion = int(input("Recursion: 1st or 2nd? "))
            return cls(size, curr_state, time, recursion)
        except Exception as e:
            print("Error",e)
    
    ##Manhattan Heuristics
    def fn(self, state):
        return sum([1 if state[i] != self.constant[i] else 0 for i in range(self.size ** 2)])

    def hn(self, state):
        h = 0
        for i in range(self.size ** 2):
            row = state.index(i) // self.size
            column = state.index(i) % self.size
            row1 = self.constant.index(i) // self.size
            column1 = self.constant.index(i) % self.size
            h += abs(row - row1) + abs(column - column1)  
        return h
        
    #A Star search
    def astar_exec(self):
        #Init parameters
        expanded = 0
        start_time = time()
        initial_mem = Process().memory_info().rss
        frontier = [Node([], self.curr_state, None, 0, 0, self.fn(self.curr_state) if self.recursion == 1 else self.hn(self.curr_state))]
        visited = []

        while len(frontier) >0 and time() - start_time < self.time:
            node = frontier.pop(0)
            #Goal reached or not?
            if self.goal_test(node):
                return node.path[1:] + [node], expanded, time()- start_time, Process().memory_info().rss - initial_mem
            
            if not any([node.state == other for other in visited]):          
                visited.append(node.state)
                expanded += 1
                for child in self.expand(node):
                    insort(frontier, child)
                
        return False, False, False, False
    
    #Check for list of ordered integers
    def goal_test(self, node):
        
        return node.state == self.constant
        
    def expand(self, node):
        #Calculate next actions & states
        actions, states = self.get_children(node.state)
        children = []
        #children nodes are created
        for i in range(len(actions)):
            temp = Node(node.path + [node], states[i], actions[i], node.max_recursion_depth + 1, node.cost + 1, self.fn(states[i]) if self.recursion == 1 else self.hn(states[i]))
            children.append(temp)
        return children
    
    def get_children(self, state):
        actions = []
        states = []
        
        row = state.index(0) // self.size
        column = state.index(0) % self.size
        
        #1st Column: L
        if column != 0:
            actions.append("L")
            present_state = list(state)
            present_state[row * self.size + column] = present_state[row * self.size + column - 1]
            present_state[row * self.size + column - 1] = 0

            states.append(present_state)
        
        #1st Row: U
        if row != 0:
            actions.append("U")
            present_state = list(state)

            present_state[row * self.size + column] = present_state[(row - 1) * self.size + column]
            present_state[(row - 1) * self.size + column] = 0

            states.append(present_state)
        
        #last Column: R
        if column != self.size - 1:
            actions.append("R")
            present_state = list(state)
            present_state[row * self.size + column] = present_state[row * self.size + column + 1]
            present_state[row * self.size + column + 1] = 0

            states.append(present_state)
        
        #last Row: D
        if row != self.size - 1:
            actions.append("D")
            present_state = list(state)

            present_state[row * self.size + column] = present_state[(row + 1) * self.size + column]
            present_state[(row + 1) * self.size + column] = 0

            states.append(present_state)

        return actions, states


if __name__ == "__main__":

    puzzle = board.from_string()
    if puzzle is None:
        exit()
    
    path, expanded, total_time, memory_required = puzzle.astar_exec()

    if path != False:
        print("Moves = {}".format([n.action for n in path]))
        print("Total Nodes expanded={} ".format(expanded))
        print("Time Taken ={}".format(total_time))
        print("Memory consumed in bytes = {}".format(memory_required))
    else:
        print("Solution does not exist at this depth")