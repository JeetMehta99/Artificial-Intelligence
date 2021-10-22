#Iterative Deepening Depth First Search on 15 Puzzle
#Jeet Mehta
#668581235

import sys
from psutil import Process
from time import time
import math

#Defines the node
class Node:
    def __init__(self, path, state, action, max_recursion_depth, cost):
        self.path = path
        self.state = state
        self.action = action
        self.max_recursion_depth = max_recursion_depth
        self.cost = cost
#Defines state 
class board:
    def __init__(self, size, curr_state,time, recursion):
        self.size = size
        self. curr_state = curr_state
        self.time = time
        self.recursion = recursion

    @classmethod
    def from_string(stt):
        try:
            size = int(input("Puzzle size:"))
            input_string = str(input("Input initial state:"))
            inp = input_string.split(" ")
            intInp = []
            for i in inp:
                intInp.append(int(i))
            curr_state = []
            for i in range(size**2):
                curr_state.append(intInp[i])
            time = float(input("Time:"))
            recursion = input("Recursion: 1 or 0?")!= '0'
            return stt(size, curr_state, time, recursion)
        except Exception as e:
            print("Error",e)
#Check for list of ordered integers
    def goal_test(self,node):
        return node.state == list(range(1,self.size**2)) +[0]

    def ids_exec(self):
        #Init parameters
        limit = 0
        final_result = False
        expanded = 0
        start_time = time()
        initial_mem = Process().memory_info().rss
        visited = []


        while time() - start_time < self.time:
            if self.recursion:
                final_result, expanded1 = self.dls_exec_recursion(Node([], self.curr_state, None, 0, 0), 0, limit, start_time, [])    
            else:
                final_result, expanded1 = self.dls_exec_i(limit, start_time)

            expanded += expanded1
            if final_result != False:
                return final_result, expanded, time() - start_time, Process().memory_info().rss - initial_mem
            limit += 1   
        return False, False, False, False
    
    def dls_exec_recursion(self, node, expanded, limitOfdepth, start_time, visited):
        if self.goal_test(node):
            return node.path[1:] + [node], expanded
        
        if node.max_recursion_depth >= limitOfdepth:
            return False, expanded
        
        if any([node.state == other for other in visited]):
            return False, expanded

        if time() - start_time >= self.time:
            return False, expanded
        
        visited.append(node.state)

        expanded += 1

        for children in self.expand(node):
            final_result, expanded = self.dls_exec_recursion(children, expanded, limitOfdepth, start_time, visited)
            if final_result != False:
                return final_result, expanded
            
        return False, expanded

    def dls_exec_i(self, limitOfdepth, start_time):
        #Init parameters
        expanded = 0
        frontier = [Node([], self.curr_state, None, 0, 0)]
        visited = []

        while len(frontier) >0 and time() - start_time < self.time:
            node = frontier.pop(0)
            #Goal reached or not?
            if self.goal_test(node):
                return node.path[1:] + [node], expanded
            if not any([node.state == other for other in visited]) and node.max_recursion_depth < limitOfdepth:
                visited.append(node.state)
                expanded +=1
                       
        return False, expanded



        
    def expand(self, node):
        #Calculate next actions & states
        actions, states = self.get_children(node.state)
        children = []
        #children nodes are created
        for i in range(len(actions)):
            temp = Node(node.path + [node], states[i], actions[i], node.max_recursion_depth + 1, node.cost + 1)
            children.append(temp)
        return children
    
    def get_children(self, state):
        actions = []
        states = []
        
        for i in range(self.size ** 2):
            if state[i] == 0:
                row = i // self.size
                column = i % self.size
                break
        
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
    
    path, expanded, total_time, memory_required = puzzle.ids_exec()

    if path != False:
        print("Moves = {}".format([n.action for n in path]))
        print("Total Nodes expanded={} ".format(expanded))
        print("Time Taken ={}".format(total_time))
        print("Memory consumed in bytes = {}".format(memory_required))
    else:
        print("Solution does not exist at this depth")