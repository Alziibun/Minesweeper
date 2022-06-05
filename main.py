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
			_field[y][x] = Minefield(self, True)
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
		self._x = 0
		self._y = 0
		self._button = Button(tk,
			padx=10,
			pady=3)
		self._button.configure(command=lambda: self.onclick(self._button))

	"""
	Properties
	"""
	@property
	def ismine(self):
		return self._ismine

	@property
	def state(self):
		return self._state

	@property  # getter for X value
	def x(self):
		return self._x

	@property
	def y(self):
		return self._y
	
	@property
	def cord(self):
		return (self.x, self.y)

	@property
	def button(self):
		return self._button
	
	
	"""
	Setters
	"""
	@ismine.setter
	def ismine(self, m):
		self._ismine = bool(m)

	@state.setter
	def state(self, s):
		try:
			if type(s) is not str:
				s = s.name
			if s in self.states.__members__:
				button = self._button
				match s:
					case 'dug':
						button['relief'] = SUNKEN
					case 'flagged':
						button['text'] = 'P'
				print('Minefield has been ' + s)
				self._state = self.states[s]
		except:
			raise ValueError("Invalid Minefield state.")

	@x.setter
	def x(self, value):
		self._x = value

	@y.setter
	def y(self, value):
		self._y = value

	@cord.setter
	def cord(self, value):
		self.x, self.y = value

	"""
	Methods
	"""
	def onclick(self, button):
		# change the state of the minefield and update the button
		mouse = self._game.player.mouse
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
					self.bloom()
				else:
					print('The Player cannot dig here.')
			case 'flag':
				# the field is flagged
				if self.state.value > 1:
					# check if the field is fresh or flagged
					print("The Player cannot place a flag here.")
				else:
					self.state = 'flagged'

	def bloom(self):
		# branch out and find mines
		gamefield = self._game.field
		x, y = self.cord
		go = dict(
			up        = lambda n=1, nx=x, ny=y: gamefield[ny - n][nx + 0],
			right     = lambda n=1, nx=x, ny=y: gamefield[ny + 0][nx + n], 
			down      = lambda n=1, nx=x, ny=y: gamefield[ny + n][nx + 0],
			left      = lambda n=1, nx=x, ny=y: gamefield[ny + 0][nx - n],

			# used for check()
			upright   = lambda n=1, nx=x, ny=y: gamefield[ny - n][nx + n],
			upleft    = lambda n=1, nx=x, ny=y: gamefield[ny - n][nx - n],
			downright = lambda n=1, nx=x, ny=y: gamefield[ny + n][nx + n],
			downleft  = lambda n=1, nx=x, ny=y: gamefield[ny + n][nx - n],)

		def check(obj=self, directions=[]):
			# check how many mines are nearby
			_directions = directions
			_found = []
			gox, goy = obj.cord
			if len(_directions) == 0:
				# creates a default list based on fresh, untouched minefields
				for i, v in list(go.items()):
					if v().state.value <= 1:
						_directions.append(i)
			for there in _directions:
				if go[there](nx = gox, ny = goy).ismine:
					_found.append(there)
			print(_found)
			return _found

		def branch(direction):
			# nested method to yield minefields until finding a mine
			print('branching ' + direction)
			index = 1
			fields = []
			try:
				while True:
					print(f'[{index}] Branching {direction}.')
					yield go[direction](index)
					index += 1
			except Exception as e:
				print(e)

		inicheck = check() # first make sure there are no mines nearby
		checked = dict()
		go_cardinal = list(go.items())[0:4]
		go_fan = iter(go_cardinal)
		for direction, thisfield in go_cardinal:
			if direction in inicheck:
				continue  # there's already a mine here so there's no need to check
			for i in branch(direction):
				if len(check(i)) > 0:
					i.button['text'] = len(check(i))
					break #the next field in this direction is a mine, stop here
				i.state = 'dug'
				for e in branch(next(go_fan)[0]):
					if len(check(e)) > 0:
						e.button['text'] = len(check(e))
						break
					e.state = 'dug'

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
		field_list_simple = list()
		for y, field_list in enumerate(_field):
			for x, field_obj in enumerate(field_list):
				field_obj.button.grid(row=y,column=x)
				field_obj.cord = (x, y)
				#field_obj.button['text'] = f'{x}, {y}' # debug
		return field_list_simple

Window(Game())

tk.mainloop()