from tkinter import *
from tkinter import ttk
import tkinter.font as font
import time
import os

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
	new_game = True
	scores = None
	def __init__(self, size=16, mines=40, flag_limit = 0):
		print(f'========= MINESWEEPER ==========')
		print(f'| Grid: {size}x{size}  || Mines: {mines} |')
		print(f'=========== NEW GAME ==========')
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
		size, _,_ = cls.rules.values()
		cls.new_game = True
		self.new_field(size)
		self.window.render_field()
		self.load_scores()
		Window.setTitlebar(f'Grid Size : {size} | Mines : {mines}')


	"""
	Methods
	"""

	@classmethod
	def new_field(cls, size):
		print('Creating new minefield...')
		cls.field = [[Minefield() for _ in range(size)] for _ in range(size)]

	@classmethod
	def set_mines(cls, selcord):
		print(f'Planting mines with the exception of {selcord}.')
		mines = cls.rules['mines']
		size = cls.rules['size']
		for i in range(mines):
			x = r.randint(0, size-1)
			y = r.randint(0, size-1)
			if (x, y) == selcord:
				continue
			cls.field[y][x].ismine = True
		cls.new_game = False
		print('Mines planted.')

	@classmethod
	def end(cls, result=False):
		print('Ending game...')
		cls.reveal_mines()
		tk.after(3000, lambda: cls.window.menu_main())

	@classmethod
	def load_scores(cls):
		with open("scores.json", "a+") as file:
			file.seek(0)
			try:     cls.scores = json.load(file)
			except:  cls.scores = json.loads('{}')

	@classmethod
	def write_scores(cls):
		with open("scores.json", 'w') as file:
			file.write(cls.scores)

	@classmethod
	def reveal_mines(cls):
		for fieldlist in cls.field:
			for field in fieldlist:
				if field.ismine:
					field.state = 'mine'

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
		dig   = 1
		flag  = 2
		query = 3

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
		print('|-- Initializing Mouse.')
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
		try:
			self._state = Mouse.States(s)
			Window.mouseFunc['text'] = self.state.name
		except Exception as e:
			print(e)
	"""
	Methods
	"""
	def switch(self, *args):
		self.state = self.state.next
		print("Mouse function is now " + self.state.name)
		return self.state # for the sake of match ... case statements

class Minefield(Game):
	"""
	handles Minefields
	"""
	class States(Enum):
		def __new__(cls, *args, **kwargs):
			value = len(cls.__members__) + 1
			obj = object.__new__(cls)
			obj._value_ = value
			return obj
		def __init__(self, bRelief, bgColor, text, state):
			self.style = dict(
				relief = bRelief,
				bg = bgColor or 'SystemButtonFace',
				text = text or '',
				state = state)
			cls = self.__class__
			if len(cls):
				all = list(cls)
				first, prev = all[0], all[-1]
				prev.next = self
				self.prev = prev
				self.next = first

			#   Relief  | button color | Text | State
		FRESH = GROOVE,  None,          None,  NORMAL
		DUG   = SUNKEN,  'light grey',  None,  NORMAL
		QUERY = GROOVE,  None,          '?',   NORMAL
		FLAG  = GROOVE,  None,          'X',   DISABLED
		MINE  = GROOVE,  'red',         'M',   DISABLED

	def __init__(self, ismine = False):
		self._ismine = ismine
		self._state = self.States(1)  # a new minefield shall always be fresh
		self._x = 0
		self._y = 0
		buttonfont = font.Font(weight='bold')
		self._button = Button(Game.current.window.playfield,
			height=1,
			width=2,
			font=buttonfont,
			padx=-3,
			pady=-3)
		self._button.configure(command=lambda: self.onclick())
		self.stylize()
		self._button.bind('<Button-3>', lambda x: self.onRightClick())

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
			if type(s) is int:
				self._state = Minefield.States(s)
			elif type(s) is str:
				for index in Minefield.States:
					if s.lower() == index.name.lower():
						self._state = index
						break
			elif type(s) is self.States:
				self._state = s
			else:
				print('State not found.')
			self.stylize()
		except:
			raise ValueError(f"'{s}' is not a valid Minefield state.")

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
	def stylize(self):
		# changes the button style to match the current state
		print(f'Updating button style to match {self.state.name}...')
		ref = self.state
		for index in ['relief', 'bg', 'text', 'state']:
			print(f'| - Changing button {index}...')
			self.button[index] = ref.style[index]
		print('Finished styling button.')

	def onclick(self):
		# change the state of the minefield and update the button
		mouse = super().current.player.mouse
		if mouse.__class__ is not Mouse:
			return
		if Game.new_game:
			Game.current.set_mines(self.cord)
		if self.state.value < 2 or self.state is self.States.QUERY:
			if self.ismine:
				print('BOOM!')
				Game.current.end()
			else:
				print('The player is safe... for now.')
				self.state = 'fresh'
			self.bloom()
		else:
			print('The Player cannot dig here.')

	def onRightClick(self):
		# cycle through field states
		if self.state is self.States.DUG:
			return
		# Simply put: skip over the dug state if it's next
		_next = self.state.next if self.state.next is not self.States.DUG else self.state.next.next
		print(f'Changing field state to {_next.name.lower()}.')
		self.state = _next

	def bloom(self):
		# branch out and find mines
		if self.state.value > 1 and self.state is not self.States.QUERY:
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
			self.state = 'dug'
			self.button['text'] = str(len(checklist))
			match len(checklist):
				case 1: self.button['fg'] = 'blue'
				case 2: self.button['fg'] = 'green'
				case 3: self.button['fg'] = 'goldenrod'
				case 4: self.button['fg'] = 'violet red'
				case _: self.button['fg'] = 'red'
			return
		self.state = 2
		for direction, m in list(go.items()):
			if m == None:
				continue
			m.bloom()

class Window(Game):
	"""
	handles most of the rendering side of things
	"""
	playfield = None
	title     = None
	def __init__(self):
		print('Making a new window')
		cls = self.__class__
		tk.resizable(False, False)
		cls.playfield = Frame(tk)
		cls.title = Label(tk, text='bottom text')
		# packing
		self.title.pack()
		self.playfield.pack(padx=10, pady=10)
	
	###########
	# Methods #
	###########
	@classmethod
	def setTitlebar(cls, text):
		if cls.title:
			cls.title['text'] = text
	@classmethod
	def clear_field(cls):
		print('Clearing field...')
		for child in cls.playfield.winfo_children():
			child.destroy()
		print('Field cleared.')

	@classmethod
	def menu_main(cls):
		if cls.playfield:
			cls.clear_field()
			menu_frame = Frame(cls.playfield, relief=RAISED)
			menu_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
			menu_title = Label(menu_frame, text='Start new game?')
			menu_start = Button(menu_frame, text='New Game', command=Game)
			menu_title.pack()
			menu_start.pack()

	def render_field(self):
		# Sends a list of Tk Button objects.  Usually for rendering.
		print('Rendering buttons...')
		_field = Game.current.field
		field_list_simple = list()
		for y, field_list in enumerate(_field):
			for x, field_obj in enumerate(field_list):
				field_obj.button.grid(row=y,column=x)
				field_obj.cord = (x, y)
				#field_obj.button['text'] = f'{x}, {y}' # debug
		return field_list_simple

new =Game()
tk.title("Minesweeper by Alzii!")
tk.mainloop()