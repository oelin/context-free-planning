# CFP

Finding feasible solutions to planning problems using generative context-free grammars.

## 1. Introduction

Context-free planning is a method for finding feasible solutions to deterministic planning problems. 

It relies on the fact that such problems can often be modelled as automata, implying that they also have a corresponding context-free representation. Using a context-free grammar (CFG), we can then generate solutions automatically from the given set of production rules.


## 2. Modelling Problems With Automata

The first step in context-free planning is to devise an automaton which represents the problem of interest. For example, consider the problem of navigating within a 3x3 board towards some target cell.

```
+---+---+---+
| A |   |   |
+---+---+---+
|   |   |   |
+---+---+---+
|   |   | X |
+---+---+---+
```

Let $M = ( Q, \Sigma, \delta, q_0, F)$ be a finite state automaton, where:

- $Q =  \{ (x, y) | x, y \in \{0,\dots, 2\} \}$

- $\Sigma = \{ 0, \dots, 3\}$

- $\delta((x, y), 0) = (x, y -1)$

- $\delta((x, y), 1) = (x + 1, y)$

- $\delta((x, y), 2) = (x, y + 1)$

- $\delta((x,y), 3) = (x - 1, y)$

- $\delta((x,y), a) = (x, y)$ if $a$ would move the agent out-of-bounds.

- $q_0 = (0, 0)$

- $F = \{ (2, 2) \}$

This automaton accepts a language $\mathcal{L}$, consisting of all strings which represent successful paths to the target. If we can find a way to generate strings in $\mathcal{L}$, then we effectively generate solutions to the problem. 


## 3. Solving Problems With Context-free Grammars

An interesting feature of context-free languages is that they're a *superset* of regular languages. Then for any finite state automaton accepting some language there exists a context-free grammar accepting the same language. 

Specifically, if $M = ( Q, \Sigma, \delta, q_0, F)$ is a finite state automaton then the equivalent context-free grammar is given by  $G = (V, \Sigma', P, S)$, where:

- $V =Q$

- $\Sigma' = \Sigma \cup \{\epsilon\}$

- $P = \{ q_i \to a(q_j)\ |\  \delta(q_i,a)=q_j \} \cup \{ q_i \to \epsilon \\ |\ \delta(q_i, a) \in F\}$

- $S  = q_0$

This context-free grammar accepts the same language as $M$, however it additionally allows us to *generate* strings from the language using production rules. Applying this to the navigation problem, we can now solve it using a context-free grammar *constructed from* the automaton. Constructing the grammar, and generating strings are both linear time operations in the size of the original automaton. Hence, this approach is suitable for problems involving relatively small state or action spaces.


## 4. Optimal Planning

So far, we have provided an efficient method for solving deterministic planning problems using context-free grammars. However, we have not considered the extent to which these solutions are optimal. In general, an arbitrary solution selected from the language of all solutions will not be "optimal" for some measure of optimality. In many problems, there are an infinite number of sub-optimal while only a finite number of optimal ones. Navigation to a target is one such problem.


## 5. Implementation 

In this section, we describe how to implement context-free planning in Python. We'll again return to the navigation problem as it's both simple and practically useful to some extent. To start, we implement a class for representing finite state automata; which isn't much more than a tuple. The `has()` method takes a string and runs it through the automaton, returning whether the string was accepted or not. The transition function must be a callable which maps between state-symbol tuples and states.

```py
from typing import Type, Union, Callable, Tuple
from dataclasses import dataclass
from functools import reduce
```

```py
State: Type = str 
Symbol: Type = str
String: Type = Tuple[Symbol]
```

```py
@dataclass
class Automaton:
	"""
	Implements a finite state automaton.
	"""
	
	states: set[State]
	alphabet: set[Symbol]
	transition: Callable[Tuple[State, Symbol], State]
	start: State
	final: set[State]
	
	
	def reduce(self, string: String) -> State:
		"""
		Reduces a string using the automaton's state transition 
		function.
		"""
		
		return reduce(self.transition, string, self.start)	


	def has(self, string: String) -> bool:
		"""
		Checks whether a string is in the automaton's language.
		"""
		
		return self.reduce(string) in self.final 
```

Next, let's define a class for representing context-free grammars. The `expand()` method expands symbol by recursively applying production rules until only terminal symbols are left. The production rule function must map between variable symbols and strings.

```py
@dataclass 
class Grammar:
	"""
	Implements a typical context-free grammar.
	"""
	
	variables: set[Symbol]
	terminals: set[Symbol]
	production: Callable[Symbol, String]
	start: Symbol
	
	
	def expand(self, symbol: Symbol) -> String:
		"""
		Expands a symbol by recursively applying production 
		rules until only terminal symbols are left.
		"""
		
		return symbol if symbol not in self.variables else ''.join(map(
			self.expand,
			self.production(symbol),
		))
```


With these two classes defined, we can now work on creating a function which convert an automaton *into* an equivalent context-free grammar. We will use the same construction as defined in (3). 


```py
import random
from collactions import defaultdict
```


```py
def convertAutomatonToGrammar(automaton: Automaton) -> Grammar:
	"""
	Converts an automaton into a context-free grammar.
	"""
	
	
	variables = automaton.states 
	terminals = automaton.alphabet 
	start = automaton.start 
	
	
	productions = defaultdict(lambda: [])
	
	
	for variable in variables:
		for terminal in terminals:
		
			state = automaton.transition((variable, terminal))
			
			if state in automaton.final:
				state = '$'
			
			productions[variable].append((terminal, state))
	
	
	def production(symbol: Symbol) -> String:
		return random.choice(productions[symbol])
	
	
	return Grammar(
		variables, 
		terminals,
		production,
		start,
	)
```

