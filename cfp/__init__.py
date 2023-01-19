# Problem formulation for discrete deterministic planning:
# 
# Let S be a set of states.
# Let A be a set of actions.
# Let f : S x A -> S be a state transition function 
# Let G be a set of "goal" states.
# Let s0 be an initial/starting state.
# 
# The goal is to take a series of actions which move from the initial state
# to a goal state.
#
# Notice that this formulation is just an instance of a DFA:
#
# Let S be a set of states.
# Let A be an alphabet.
# Let f : S x A -> S be a state transition function.
# Let F be a set of final/accepting states.
# Let s0 be an initial state. 
#
# The goal is to find a string which is a member of the language described
# by this DFA.
#
# Hence, if we can find a way to generate strings from this language then we can 
# find feasible solutions to the planning problem.



# Example 1 - Navigating to a target square in a small grid.


from typing import Any, Callable 
from dataclasses import dataclass
from collections import defaultdict 


@dataclass 
class FSA:
    """
    An abstract class for finite state automata.
    """
    
    alphabet: set 
    states: set
    finalStates: set 
    startState: Any
    transition: Callable
    
    
    def parse(self, string):
    
        state = self.startState 
        
        for letter in string:
            state = self.transition(state, letter)
        
        accepted = state in self.finalStates
        return state, accepted 
    

def gridTransitionFunction(state, letter):

    y = int(state / 4)
    x = state - (4 * y)
    
    x_new = x
    y_new = y
    
    if letter == 'N':
        y_new -= 1
     
    elif letter == 'E':
        x_new += 1
    
    elif letter == 'S':
        y_new += 1
    
    elif letter == 'W':
        x_new -= 1
    
    
    is_within_grid = (x_new >= 0 and x_new < 4) and (y_new >= 0 and y_new < 4)
    
    if is_within_grid:
        return (y_new * 4) + x_new
    
    return state 

N,E,S,W = 0,1,2,3
    
gridFSA = FSA(
    alphabet = {
        'N', # Move noth 
        'E', # Move east
        'S', # Move south
        'W', # Move west 
    },
    states = {
        0x00, 0x01, 0x02, 0x03, # a 4x4 grid of cells 
        0x04, 0x05, 0x06, 0x07,
        0x08, 0x09, 0x0a, 0x0b,
        0x0c, 0x0d, 0x0e, 0x0f,
    },
    finalStates = {
        0x0f, # the bottom right corner cell
    },
    startState = 0x00,
    transition = gridTransitionFunction,
)

# An example of a feasible solution: the string EEESSS


import random   

@dataclass 
class CFG:

    def __init__(
        self,
        variables: set,
        terminals: set,
        startVariable: Any,
    ):
        self.variables = variables 
        self.terminals = terminals 
        self.startVariable = startVariable 
        self.productions = defaultdict(lambda: [])
    
    
    def add_production(self, variable, branches):
        self.productions[variable] += branches 
    
    
    def get_production(self, variable):
        return self.productions[variable]
        
    
    def is_terminal(self, variable):
        return self.productions.get(variable) == None
    
    
    def generate(self, variable = None):

        variable = variable or self.startVariable
        
        if (self.is_terminal(variable)):
            return variable
    
    
        branches = self.get_production(variable)
        branch = random.choice(branches)
        result = '' 
        
        for branch_variable in branch:
            result += self.generate(branch_variable)
            
        return result 
 

ketsCFG = CFG(
    terminals = {
        '(',
        ')',
        '[',
        ']',
        '.',
    },
    variables = {
        'BRACE',
        'RIGHT',
        'START',
    },
    startVariable = 'START',
)

ketsCFG.add_production('BRACE', [
    ('(', 'START', ')'),
])

ketsCFG.add_production('SQUARE', [
    ('[', 'START', ']'),
])

ketsCFG.add_production('START', [
    ('BRACE',),
    ('SQUARE',),
    ('.',),
])


# A context-free grammar for the 4x4 grid example...

gridCFG = CFG(

    # Create a variable (qi) for every state...
    
    variables = {
        '00', '01', '02', '03', # a 4x4 grid of cells 
        '04', '05', '06', '07',
        '08', '09', '0a', '0b',
        '0c', '0d', '0e', '0f',
    },
    
    terminals = {
        '$',
        'N',
        'E',
        'S',
        'W',
    },
    startVariable = '00',
)

# Add rule (qi) -> a(qj) if T(qi, a) = qj
# Add rule (qk) -> $ if qk is an accepting state.


gridCFG.add_production('0f', [
    ('$',),
])


gridCFG.add_production('0e', [
    ('N', '0a'),
    ('E', '0f'),
    ('S', '0e'),
    ('W', '0d'),
])


gridCFG.add_production('0d', [
    ('N', '09'),
    ('E', '0e'),
    ('S', '0d'),
    ('W', '0c'),
])


gridCFG.add_production('0c', [
    ('N', '08'),
    ('E', '0d'),
    ('S', '0c'),
    ('W', '0c'),
])


gridCFG.add_production('0b', [
    ('N', '07'),
    ('E', '0b'),
    ('S', '0f'),
    ('W', '0a'),
])


gridCFG.add_production('0a', [
    ('N', '06'),
    ('E', '0b'),
    ('S', '0e'),
    ('W', '09'),
])


gridCFG.add_production('09', [
    ('N', '05'),
    ('E', '0a'),
    ('S', '0d'),
    ('W', '08'),
])


gridCFG.add_production('08', [
    ('N', '04'),
    ('E', '09'),
    ('S', '0c'),
    ('W', '08'),
])


gridCFG.add_production('07', [
    ('N', '03'),
    ('E', '07'),
    ('S', '0b'),
    ('W', '06'),
])


gridCFG.add_production('06', [
    ('N', '02'),
    ('E', '07'),
    ('S', '0a'),
    ('W', '05'),
])


gridCFG.add_production('05', [
    ('N', '01'),
    ('E', '06'),
    ('S', '09'),
    ('W', '04'),
])


gridCFG.add_production('04', [
    ('N', '00'),
    ('E', '05'),
    ('S', '08'),
    ('W', '04'),
])


gridCFG.add_production('03', [
    ('N', '03'),
    ('E', '03'),
    ('S', '07'),
    ('W', '02'),
])


gridCFG.add_production('02', [
    ('N', '02'),
    ('E', '03'),
    ('S', '06'),
    ('W', '02'),
])



gridCFG.add_production('01', [
    ('N', '01'),
    ('E', '02'),
    ('S', '05'),
    ('W', '00'),
])


gridCFG.add_production('00', [
    ('N', '00'),
    ('E', '01'),
    ('S', '04'),
    ('W', '00'),
])



def find_short_sentence(cfg, n = 100):

    sentences = [cfg.generate() for _ in range(n)]
    
    return min(sentences, key=lambda sentence: len(sentence))


# Example solution produce by the CFG: gridFSA.parse('ESSWSWWESEE')
