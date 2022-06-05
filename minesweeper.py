from tkinter import *
import random as r
from enum import Enum
root = Tk()

class Game:
	def __init__(self):
		Minefield()

class Player:
	pass

class Mouse:

	def __init__(self):
		self._state = 0

	@property
	def state(self):
		return self._state

	@state.setter
	def state(self, s):
		if States.has_value(s):
			self._state = s
		else:
			raise ValueError("Mouse state invalid.")

	def switch(self):
		self.state( int( not bool( self.state ) ) )
		print('mouse state switched')

class Minefield:

	def __init__(self, dim_size=11, bombs_count=10):

		self.dim = dim_size
		self.bombs_count = bombs_count
		self.dug = list()

		self.render( self.plant( self._await() ) )

	def plant(self, start_sel):

		# generate empty board
		_board = [[0 for _ in range(self.dim)] for _ in range(self.dim)]

		bombs_planted = 0

		while bombs_planted < self.bombs_count:
			loc = r.randint(0, self.dim ** 2 - 1)
			row = loc // self.dim
			col = loc % self.dim

			if _board[row][col] == 1 or [row, col] == start_sel:
				continue  #skip this possibility

			_board[row][col] = 1   # return later for tkinter
			bombs_planted   += 1
		print("Bombs planted!")
		return _board

	def render(self, board):
		_board = board
		for i in range(self.dim+1):
			for e in range(self.dim+1):
				Button(root, 
					padx=10, 
					pady=3).grid(row=i, column=e)

	def _await(self):
		pass

	class field(super,)

big = Game()
root.mainloop()