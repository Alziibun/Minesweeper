from tkinter import *
from tkinter import ttk

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
	current = None
	field   = list()
	player  = None
	window  = None
	rules   = dict(
		size       = 10,
		mines      = 10,
		flag_limit = 0)
	def __init__(self, size=20, mines=60, flag_limit = 0):
		print('Initializing new Game.')
		cls = self.__class__
		cls.current = self
		cls.rules = dict(
			size       = size,
			mines      = mines,
			flag_limit = flag_limit)
		if not cls.player:
			cls.player = Player()
		if not cls.window:
			cls.window = Window()
		size, mines, _ = cls.rules.values()
		self.new_field(size, mines)
		self.window.render_field()
		self.window.title = f'Grid Size : {size} | Mines : {mines}'


	"""
	Methods
	"""

	def new_field(self, size, mines):
		print('Creating new minefield...')
		_field = [[Minefield() for _ in range(size)] for _ in range(size)]
		for i in range(mines):
			x = r.randint(0, size-1)
			y = r.randint(0, size-1)
			_field[y][x].ismine = True
		print('Mines planted.')
		self.__class__.field = _field

	@classmethod
	def end(cls, result=False):
		print('Ending game...')
		cls.window.playfield.destroy()


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

class Player(Game):
	"""
	Handles Player data
	"""
	def __init__(self, name='UNKNOWN'):
		print('Initializing Player: ' + name)
		self._name = name
		self._flags = int( super().current.rules['flag_limit'] )
		self.mouse = Mouse()

	"""
	Properties
	"""
	@property
	def name(self):
		return self._name

	@property
	def flags(self):
		return self._flags
	# setters
 
	@name.setter
	def name(self, new_name):
		self._name = new_name

	@flags.setter
	def flags(self, value):
		self._flags = value

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

class Minefield(Game):
	"""
	handles Minefields
	"""
	class states(Enum):
		fresh   = 1
		dug     = 2
		flagged = 3

	def __init__(self, ismine = False):
		self._ismine = ismine
		self._state = self.states.fresh   # a new minefield shall always be fresh
		self._x = 0
		self._y = 0
		self._button = Button(Game.current.window.playfield,
			height=1,
			width=2)
		self._button.configure(command=lambda: self.onclick())

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
				print(f'The Minefield at ({self.x}, {self.y}) has been {s}.')
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
	def onclick(self):
		# change the state of the minefield and update the button
		mouse = super().current.player.mouse
		if mouse.__class__ is not Mouse:
			return
		match mouse.state.name:
			case 'dig':
				# the field is dug
				if self.state.value < 2:

					if self.ismine:
						print('BOOM!')
						super().current.window.alert()
					else:
						print('The player is safe... for now.')
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
		if self.state.value > 1:
			return
		gamefield = Game.current.field
		_max  = Game.current.rules['size'] - 1
		x, y = self.cord
		go = dict(
			up        = gamefield[y - 1][x + 0] if y > 0 else None,
			right     = gamefield[y + 0][x + 1] if x != _max else None, 
			down      = gamefield[y + 1][x + 0] if y != _max else None,
			left      = gamefield[y + 0][x - 1] if x > 0 else None,

			# used for check()
			upright   = gamefield[y - 1][x + 1] if (y != 0 and x != _max) else None,
			upleft    = gamefield[y - 1][x - 1] if (0 not in [x, y]) else None,
			downright = gamefield[y + 1][x + 1] if (_max not in [x, y]) else None,
			downleft  = gamefield[y + 1][x - 1] if (x != 0 and y != _max) else None)
		def check():
			# check how many mines are nearby
			_found = []
			for i, m in list(go.items()):
				try:
					if m.state.value <= 1:
						if m.ismine:
							_found.append(i)
				except:
					continue
			return _found

		checklist = check()
		if self.ismine:
			return
		if len(checklist) > 0:
			self.button['text'] = str(len(checklist))
			self.state = 'dug'
			return
		self.state = 'dug'
		for direction, m in list(go.items()):
			if m == None:
				continue
			m.bloom()

class Window(Game):
	"""
	handles most of the rendering side of things
	"""
	def __init__(self):
		self.playfield = Frame(tk)
		self._title = Label(tk, text='bottom text')

		# packing
		self._title.pack()
		self.playfield.pack()


	@property
	def title(self):
		return self._title


	@title.setter
	def title(self, value):
		self._title['text'] = value
	
	def render_field(self):
		print('rendering buttons')
		_field = super().current.field
		print(type(_field))
		field_list_simple = list()
		for y, field_list in enumerate(_field):
			for x, field_obj in enumerate(field_list):
				field_obj.button.grid(row=y,column=x)
				field_obj.cord = (x, y)
				#field_obj.button['text'] = f'{x}, {y}' # debug
		return field_list_simple

	def alert(self, win=False):
		alert = Toplevel(tk)
		info = Label(alert)
		if win:
			info['text'] = 'You win!'
		else:
			info['text'] = "Game over."
		alert_close = Button(alert, text='OK', command=lambda: alert.destroy())
		info.pack()
		alert_close.pack()

new =Game()
tk.title("Minesweeper by Alzii!")
tk.mainloop()