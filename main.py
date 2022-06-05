from tkinter import *

tk = Tk()

import random as r
import json
from enum import Enum
Decoder = json.JSONDecoder()
Encoder = json.JSONEncoder()

class Game:
	"""
	Handles Game data
	-------
	1) Time the Player
	2) Create new Minefields when needed
	3) Announce completion of round
	"""
	def __init__(self, size = 10, mines = 10, flag_limit = True):
		print('Initializing new Game.')
		self.scores = self.download_scores()
		# define game rules
		self.rules = {
			'size'  : size,
			'mines' : mines,
			'flag_limit' : flag_limit
		}
		self._field = list()

		# start game!
		self.field  = (size, mines)
		self.player = Player(self)

	"""
	Properties
	"""
	@property
	def field(self):
		return self._field

	# setters

	@field.setter
	def field(self, value):
		print('Creating new minefield...')
		dim, _mines = value
		_field = [[Minefield(self, False) for _ in range(dim)] for _ in range(dim)]
		for i in range(_mines):
			x = r.randint(0, dim-1)
			y = r.randint(0, dim-1)
			_field[x][y] = Minefield(self, True)
		print('Mines planted.')
		self._field = _field

	"""
	Methods
	"""
	

	def download_scores(self):
		file = None
		try:
			file = open("scores.json", 'r')
		except:
			print('Creating a new scores file...')
			file = open("scores.json", 'w')
			file.write(dict())
			file.close()
			file = open('scores.json', 'r')
		finally:
			try:
				obj, idx = Decoder.raw_decode(file)
				yield obj
			except TypeError as e:
				print(e)
				pass

	def upload_scores(self):
		file = open("scores.json", 'w')
		file.write(Encoder.encode(self.scores))



class Player:
	"""
	Handles Player data
	"""
	def __init__(self, Game, name="UNKNOWN"):
		print('Initializing Player: ' + name)
		self._name = name 
		print(Game.rules)
		self.flags = int( Game.rules['flag_limit'] )
		self._inf_flags = Game.rules['flag_limit'] is (bool and True)
		print('infinite flags? ' + str(self._inf_flags))
		self.mouse = Mouse()

	"""
	Properties
	"""
	@property
	def name(self):
		return self._name
	# setters
 
	@name.setter
	def name(self, new_name):
		self._name = new_name

	"""
	Methods
	"""

class Mouse:
	"""
	handles Mouse information
	"""
	class States(Enum):
		dig  = 1
		flag = 2

		# to be needlessly elegant
		def __init__(self, value):
			print('Creating Mouse class.')
			#assign a link for each value in mouse states
			cls = self.__class__
			if len(cls):
				all = list(cls)
				first, prev = all[0], all[-1]
				prev.next = self #the next of the previous is itself
				self.prev = prev
				self.next = first

	def __init__(self):
		self._state = self.States(1) # set mouse to default operation

	"""
	Properties
	"""
	@property
	def state(self):
		return self._state

    #  setters

	@state.setter
	def state(self, s):
		if s > 1:
			raise ValueError("Mouse state cannot be higher than 1.")
		self._state = s

	"""
	Methods
	"""
	def switch(self):
		self.state(self.state.next)
		print("Mouse function is now " + self.state.name)


class Minefield:
	"""
	handles Minefields
	"""
	class states(Enum):
		fresh   = 1
		dug     = 2
		flagged = 3

	def __init__(self, Game, ismine = False):
		self._ismine = ismine             # is this Minefield a mine?
		self._game = Game
		self._state = self.states.fresh   # a new minefield shall always be fresh

	"""
	Properties
	"""
	@property
	def ismine(self):
		return self._ismine

	@property
	def state(self):
		return self._state
	
	"""
	Setters
	"""
	@ismine.setter
	def ismine(self, m):
		self._ismine = bool(m)

	@state.setter
	def state(self, s):
		try:
			if type(s) is str:
				s = self.states[s]
			if s in self.states.__members__:
				self._state = s
		except:
			raise ValueError("Invalid Minefield state.")

	"""
	Methods
	"""
	def onclick(self, Game):
		mouse = Game.player.mouse
		if mouse.__class__ is not Mouse:
			pass
		match mouse.state.name:
			case 'dig':
				# the field is dug
				if self.state.value < 2:

					if self.ismine:
						print('BOOM!')
					else:
						print('The player is safe... for now.')
					self.state = 'dug'
					self.render()
				else:
					print('The Player cannot dig here.')

			case 'flag':
				# the field is flagged
				if self.state.value > 1:
					# check if the field is fresh or flagged
					print("The Player cannot place a flag here.")
				else:
					self.state = 'flagged'
					self.render()


	def render(self):
		field = Button(tk,
			padx=10,
			pady=3,
			command=lambda: self.onclick(self._game))

		if self.state.name == 'dug':
			field.config(relief=SUNKEN)
		else:
			field.config(relief=RAISED)
		if self.state.name == 'flagged':
			field.config(text='F')

		#field.command = 
		return field # a Tkinter Button

class Window:
	"""
	handles most of the rendering side of things
	"""
	def __init__(self, Game):
		self._game = Game
		self.render_field()


	def render_field(self):
		print('rendering buttons')
		_field = self._game.field
		for x, field_list in enumerate(_field):
			print(x)
			for y, field_obj in enumerate(field_list):
				field_obj.render().grid(row=x,column=y)

Window(Game())

tk.mainloop()