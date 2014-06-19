import random

MAP = None
MAP_size = None
MAIN_looper = None

ulangle = "╔"
urangle = "╗"
dlangle = "╚"
drangle = "╝"
horline = "═"
verline = "║"
blankquadrant = "╔════╗║    ║╚════╝"

sample_specials = {	'nebula' : 2,
					'wreckage' : 2,
					'singularity' : 1,
					'proton_superstring' : 1}

def diff(numa, numb):
	if numa > numb:
		return numa - numb
	else:
		return numb - numa

def distance(posa,posb):
	if isinstance(posa,tuple) != True or isinstance(posb,tuple) != True:
		raise ValueError("Bad input. {} and {} received.".format(posa,posb))
	
	ax,ay = posa
	bx,by = posb
	
	ax = abs(ax)
	ay = abs(ay)
	bx = abs(bx)
	by = abs(by)
	
	diffx = diff(ax,bx)
	diffy = diff(ay,by)
		
	if diffx is 1 and diffy is 1:
		return 1
	
	else:
		return diffx + diffy
			
def randomnumber(length):
	number = ""
	for i in range(length):
		num = random.choice(list("1234567890"))
		number += num
	
	return num

class roundloop:
	
	def __init__(self):
		
		global MAIN_looper
		
		MAIN_looper = self
		self.turn = 0 
		self.players = []
		self.schedule = {}
		# waitforplayers
		
	def startLooping(self):
		
		while True:
			self.nextTurn()
	
	def addToSchedule(self,turn,function,arguments):
		
		if turn not in list(self.schedule.keys()):
			self.schedule[turn] = []
		
		self.schedule[turn].append(function,arguments)

	def runSchedule(self):
		
		if self.turn in list(self.schedule.keys()):
			function,arguments = self.schedule[turn]
			
			##
			function(*arguments) # we call the function on the provided arguments
			##
			
	def nextTurn(self):
		
		self.turn +=1
		
		print("Turn {}.".format(self.turn))
		
		self.runSchedule() # we check if there are scheduled actions
		
		for player in self.players:
			player.energyCheck()
			player.askToMove()
			#player.asktoact()
			#player.asktocreate()
			pass
		
class quadrant:
	def __init__(self,position,slots = 0, special = None):
		self.position = position
		self.slots = slots
		self.structures = []
		self.ships = []
		self.influence = None
		self.special = special
		self.discovered = False
		self.states = {'position' : self.position,
						'influence' : self.influence,
						'slots' : self.slots,
						'structures' : self.structures,
						'ships' : self.ships,
						'specials' : self.special}
	
	def pos(self):
		return self.position
		
	def __str__(self):
		return str(self.states)
	
	def attack(self,attacker,destination):
		"""The attack function is defined from a quadrant to a quadrant: a playerA-controlled quadrant attacks a playerB-controlled quadrant."""
		targetships = destination.ships
		targetstructs = destination.structures
		
		if attacker == "any":
			atkships = self.ships
			atkstructs = self.structures
		elif isinstance(attacker,player):
			atkships = [shp for shp in self.ships if shp.player is attacker]
			atkstructs = [shp for shp in self.structures if shp.player is attacker]
		else:
			raise ValueError("Bad input for attack function.")
		
		cannons = 0
		missiles = 0
		for elem in atkships + atkstructs:
			cannons += elem.cannons
			missiles += elem.missiles
		
		if distance(self.pos(),destination.pos()) == 0:
			totguns = cannons + missiles
		elif distance(self.pos(),destination.pos()) == 1:
			totguns = cannons + missiles
		elif distance(self.pos(),destination.pos()) == 2:
			totguns = missiles
		else:
			totguns = 0
			
		totdamage = 0
		
		for gun in range(totguns):
			res = random.choice([0,1])
			totdamage += res
			
		layers = []
		layers[0] = [shp for shp in targetships if shp.shipclass == 'fighter'] # first fighters
		layers[1] = [shp for shp in targetships if shp.shipclass == 'destroyer']
		layers[2] = [shp for shp in targetships if shp.shipclass == 'capital']
		layers[3] = [stt for stt in targetstructures if stt.structureclass == 'battery'] # the rest can't be damaged this way, but only conquered
		
		for layer in layers:
			if len(layer) == 0:
				pass
			elif totdamage == 0:
				print('Cannot attack!')
				break
			else:
				for elem in layer:
					extra = elem.dealDamage(damage) # absorbs the damage necessary to destroy ELEM and returns the rest
					totdamage = extra
					if totdamage == 0:
						break
			
						
		
		
		# counterattack
		
		destination.attack("any",destination)
		
	def discover(self):
		self.discovered = True
		
		if self.special is not None:
			print("New quadrant explored!")
		
		
	def freeSlots(self):
		"""Returns the number of free slots."""
		
		areas = 0
		
		for structure in self.structures:
			areas += structure.area
		
		freeslots = self.slots - areas
		
		return freeslots
			
class ship:
	
	def __init__(self,shipclass,quad,overrides = None):
		
		# shipname : (hull, cannons, missiles, speed, armor, cost)
		chardb = { 	'fighter' : 	(1,1,0,1,0,1,"f"),
					'destroyer': 	(10,10,0,1,1,7,"d"),
					'capital_ship': (20,20,5,1,1,14,"c")}
					
		if quad not in MAP:
			raise ValueError("Wrong quadrant identification: {}".format(quadrant))
		
		quad.ships.append(self)
		self.quadrant = quad

		if shipclass not in chardb:
			raise ValueError("Unrecognized shipclass: {}".format(shipclass))

		hull, cannons, missiles, speed, armor, cost, code = chardb[shipclass]
		
		self.shipclass = shipclass
		self.hull = hull
		self.player = None
		self.cannons = cannons
		self.missiles = missiles
		self.speed = speed
		self.armor = armor
		self.cost = cost
		self.code = code
		self.states = {	'shipclass' : shipclass,
						'position' : self.pos(),
						'hull' : hull,
						'cannons' : cannons,
						'missiles' : missiles,
						'speed' : speed,
						'armor' : armor,
						'cost' : cost}
		
		if MAP is None:
			newmap()
	
	def pos(self):
		return self.quadrant.position
		
	def destroy(self):
		self.player.ships.remove(self)
		self.quadrant.ships.remove(self)
		self.player = None
		self.quadrant = None
	
	def dealDamage(self,hits):
		
		inflicted = hits - self.armor
		
		if inflicted >= self.hull:
			self.destroy()
			return hits - inflicted
			
		else:
			self.damage = inflicted
			return 0
	
	def move(self,destination):
		
		if isinstance(destination,quadrant) == False:
			raise ValueError('Bad input: received a {} as -destination-.'.format(destination))
			
		if distance(self.pos(),destination.pos()) > self.speed:
			return 'Nope'
		
		if destination.influence is not None:
			if destination.influence is not self.player:
				self.player.getInfluence(destination)
		
		self.goto(destination)
	
	def goto(self,destination):
		
		if isinstance(destination,quadrant) == False:
			raise ValueError("Unrecognized quadrant type: {} received".format(destination))
			
		if destination is self.quadrant:
			return None
		
		self.quadrant.ships.remove(self)
		self.quadrant = destination
		destination.ships.append(self)
		
		destination.discover()
		
		return None
	def destroy(self):
		exquad = self.quadrant
		self.quadrant = None
		exquad.ships.remove(self)
		self.player.ships.remove(self)
	
	
	def __str__(self):
		return '{}, at {}'.format(self.shipclass, self.pos())

class character:
	
	def __init__(self,stats):
		
		for key in stats:
			self.key = stats[key]
		
class player:
	
	def __init__(self,planet = None):
		
		global MAP, MAIN_looper
		
		if MAP is None or MAIN_looper is None:
			newgame()
		
		MAIN_looper.players.append(self) # appends itself to the players loop.
		
		if planet is None:
			planet = random.choice([i for i in MAP if i.slots == 9])
		
		self.planet = planet
		self.ships = []
		self.structures = []
		self.influence_area = [] 		# List of controlled quadrants
		self.energy_per_turn = 1
		self.energy = 0
		self.ID = randomnumber(7)
		self.character = None
		self.objective = None
		self.haskilled = []
		
		for i in range(3): 					# gives three ships
			self.giveShip('fighter',planet)
		
											# gives the first space_station
		
		self.giveStructure('space_station',planet)
		
		self.discover(planet)
		
	def assignCharacter(self,character):
		self.character = character
		
	def assignObjective(self,objective):
		self.objective = objective
		
	def discover(self,quadrant):
		quadrant.discovered = True
	
	def attack(self,origin,destination):
		"""The quadrant origin attacks the quadrant destination."""
		origin.attack(self,destination) # all the player's ships here attack all that's there.
		
	
	def build(self,structureclass,where):
		
		spaces = {	'bunker' :(2,3) , # area,cost
					'battery' :(1,1),
					'space_station': (4,2),
					'central': (4,3),
					'portal' : (4,3)}
		
		if where.freeSlots() < spaces[structureclass][0]:
			return 'Nope'
		
		cost = spaces[structureclass][1]
		myshipsthere = [shp for shp in where.ships if shp in self.ships]
		if len(myshipsthere) < cost:
			return 'Nope'
		
		for i in range(cost): # pays
			aship = myshipsthere[0]
			aship.destroy()
	
	def hasHostiles(self,quad):
		"""Returns True iff quad contains enemy-controlled units."""

		units = quad.structures.extend(quad.ships)	
		if units != [] and units[0].player is not self:
			return False
		else:
			return True
	
	def energyCheck(self):
		"""Receives the current value of self.energy_per_turn in energy."""
		
		self.giveEnergyBoost('now',self.energy_per_turn)
		
	def giveStructure(self,structureclass,where):
		
		newstructure = structure(structureclass,where)
		newstructure.player = self
		
		self.structures.append(newstructure)
		
	def giveShip(self,shipclass,where):
		
		newship = ship(shipclass,where)
		newship.player = self
		
		self.ships.append(newship)
	
	def giveInfluence(self,quad):
		"""Gives to the player influence over a quadrant. If the quadrant contains a portal, then the influence is not assigned."""
		
		if 'portal' in quad.special or quad.influence is self:
			return None
		
		if quad.influence is None:
			quad.influence = self
			self.influence_area.append(quad)
			return None
		else:
			if hasHostiles(quad):
				print("Can't gain influence over quadrant. There are hostiles, and that's not neutral territory.")		
		
	def giveEnergyBoost(self,when,amount):
		
		if when is 'now':
			self.energy += amount
		
		if when is 'nextturn':
			roundloop.addToSchedule(roundloop.turn()+1, player.giveenergyboost,self,('now',amount))
	
	def recordKill(self,obj):
		if isinstance(obj,ship):
			record = ('ship', obj.shipclass)
			
		elif isinstance(obj,structure):
			record = ('structure', obj.structureclass)
		
		elif isinstance(obj,player):
			record = ('player', obj.ID)
		
		self.haskilled.append(record)
	
	# interface
	def askToMove(self):
		global MAP
		quadstomovefrom = [qd for qd in MAP if qd.ships != [] and qd.ships[0].player is self]
		# all and only the quadrants in which you have some ships
		
		if quadstomovefrom == []:
			print('You have no ships to move this turn.')
			return None
		
		for quad in quadstomovefrom:
			fighters = [shp for shp in quad.ships if shp.shipclass == "fighter"]
			
			digits = "1234567890"
			
			brk = False # breaking condition for move from a quadrant
			superbrk = False # breaking condition for askToMove as a whole
			
			if superbrk == True:
				print("Move sequence aborting...")
				break
			
			while True:
				
				if brk == True:
					print("Skipping the quadrant...")
					break				
				
				print("You have {} fighters in quadrant {}; do you wish to move them?".format(len(quad.ships),quad.pos()))
				
				choice = input("       >>> :: = ")
				
				choice = choice.split(",")
				
				if choice == "no":
					brk = True
					
										
				elif choice == "excape":
					superbrk = True 
				
				for elem in choice: # "e.g: 1a"
					num = 0
					where = ""
					for letter in elem:
						if letter in digits:
							num = int(letter)
						elif letter in "uldr":
							where += letter
					# now num is an integer (max 9) and where is something like "u", "ul" or even "udurluddwaswdauwsd".
					
					direction = None
					up = 0
					right = 0
					left = 0
					down = 0
					
					curpos = quad.pos()
					x,y = curpos
					
					for letter in where:
						if letter in "u":
							direction = "up"
							up += 1
							y -= 1
						elif letter in "l":
							direction = "left"
							left += 1
							x -= 1
						elif letter in "r":
							direction = "right"
							right += 1
							x += 1							
						elif letter in "d":
							direction = "down"
							down += 1
							y += 1
						else:
							pass
					
					global MAP_size
					height,width = MAP_size
					
					targetpos = (x,y)
					
					print("Trying to send {} ships to {}...".format(num, targetpos))
					
					if up + down + left + right == 0:
						print("Possible inputs are '1d,2r' or 'stop' if you don't wish to move from this quadrant anymore.")
					
					elif not 0 <= x <= width or not 0 <= y <= height:
						print("Bad position parameter: coords must be within x{} and y{}.".format(width,height))
					
					elif num > len(quad.ships):
						print("Bad number: you don't have *that* many ships at {}!".format(curpos))
							
					else:
						print("Engines ready... Jump!")
						
						destinations = [qd for qd in MAP if qd.pos() == targetpos]
						destination = destinations[0] # should be the only one anyway
						
						for i in range(num):
							quad.ships[0].move(destination)
						
						brk = True
				

	
	# BOOLEAN OBJECTIVE-CHECKING FUNCTIONS
	def hasEnergy(self,amount):
		if self.energy >= amount:
			return True
		
		else:
			return False
			
	def hasTerritories(self,territorytype,amount):
		
		if territorytype == "planets":
			terr = [a for a in self.influence_area if a.slots == 9]
		elif territorytype == 'asteroid':
			terr = [a for a in self.influence_area if a.slots != 0]
		elif territorytype == 'any':
			terr = self.influence_area
			
		if len(terr) >= amount:
			return True
			
		else:
			return False
	
	def hasKilled(self,enemytype,amount):
		
		if enemytype == 'ships':
			kills = [a for a in self.haskilled if a[0] == 'ship']
			
		elif enemytype == 'structures':
			kills = [a for a in self.haskilled if a[0] == 'structure']
			
		elif enemytype == 'player':
			kills = [a for a in self.haskilled if a[0] == 'player' and a.ID == amount]
			# in this case, amount is the target player's ID
			if len(kills) == 0:
				return False
			else:
				return True
				
		if len(kills) >= amount:
			return True
		else:
			return False
	
class structure:
	
	def __init__(self,structureclass,quadrant):
		
		self.structureclass = structureclass
		self.quadrant = quadrant
		self.player = None
		quadrant.structures.append(self)
		self.initchars()
		
		
	def initchars(self):
		
		# name : cost, canspawn (0/1), defence (5 = 1/5), repair (0/amount), to_conquer, area, energy_production, teleport (0/1), cannons, missiles
		charsDB = {	'space_station' : (2,1,5,1,0,4,0,0,2,0,"S"),
					'portal' 		: (3,0,0,0,0,4,0,1,0,0,"P"),
					'central'		: (3,0,0,0,2,4,1,0,0,0,"C"),
					'bunker'		: (2,0,3,0,2,2,0,0,2,0,"B"),
					'battery'		: (1,0,0,0,0,1,0,0,0,1,"b")}
					
		self.cost, self.canspawn, self.defence, self.repair, self.to_conquer, self.area, self.energy_production, self.teleport, self.code, self.cannons, self.missiles = charsDB[self.structureclass]
		
		if self.structureclass == 'battery':
			self.hull = 1
		
	
	def destroy(self):
		self.player.structures.remove(self)
		self.quadrant.structures.remove(self)
		self.player = None
		self.quadrant = None
	
	def dealDamage(self,hits):
		
		if self.structureclass != 'battery':
			print("This structure can't be damaged in this way!")
			return hits
		
		inflicted = hits - self.armor
		
		if inflicted >= self.hull:
			self.destroy()
			return hits - inflicted
			
		else:
			self.damage = inflicted
			return 0
	
class objective:
	
	def __init__(self,conditions):
		self.conditions = conditions # a list
		self.fulfilled = False
		
	def checkFulfilment(self):
		
		for condition in self.conditions:
			# a condition is a function-arguments boolean function
			function,arguments = condition
			
			if function(*arguments) == True:
				pass
				
			else:
				return False
				
		self.fulfilled = True

def newmap(height,width,specials = {}):
	
	slotsprob = {	0.30 : 1, # 30% to be a 1-slot quadrant
					0.30 : 4, # 30% to be a 4-slot
					0.10 : 9} # 10% to be a planet (9-slot quadrant)
	
	quadrantslist = []
	
	for y in range(height): # Main Body
		for x in range(width):
			
			curpos = (x,y)
			seed = random.random()
			
			for prob in slotsprob:
				if seed <= prob:
					slots = slotsprob[prob]			
				else:
					slots = 0
					
			quad = quadrant(curpos,slots)
			quadrantslist.append(quad)
	
	if specials != {}: # SPECIALS
		for special in specials:
			for times in range(specials[special]):
				while True:
					randomquad = random.choice(quadrantslist)
					if special in randomquad.specials:
						pass
					else:
						randomquad.specials.append(special)
						break
	
	name = ""
	digits = list("0123456789")
	for i in range(4):
		a = random.choice(digits)
		digits.append('.')
		b = random.choice(digits)
		c = "0"
		name += a + b + c
	
	global MAP, MAP_size, MAP_name
	MAP = quadrantslist
	MAP_size = (height,width)
	MAP_name = name
	
	return quadrantslist

def repres_struct(code):
	return "╔═{}║ ║╚═╝".format(code)

def rawMap(): # ╝ ╗ ╔ ╚ ═ ║ 
	global MAP,ulangle,urangle,dlangle,drangle,horline,verline,blankquadrant
	
	list_ref = []
	
	for quad in MAP:
		
		if quad.discovered == False:
			todisplay = list(blankquadrant)
			
			if quad.slots == 9:
				blanklist = list(blankquadrant)
				blanklist[8:10] = "pl"
				todisplay = blanklist

		else:				# 012345678901234567
			blanklist = list("╔    ╗      ╚    ╝")
			
			smallships = "f" + str(len([a for a in quad.ships if a.shipclass == "fighter"])) # max 9: 2 chars tot
			bigships = "d" + str(len([a for a in quad.ships if a.shipclass == 'destroyer'])) # max 1: 2 chars tot
			capital = "c" + str(len([a for a in quad.ships if a.shipclass == 'capital'])) # max 1: 2 chars tot
			
			if smallships == "f0":
				smallships = "══"
			if bigships == "d0":
				bigships = "══"
			if capital == "c0":
				capital = "  "
			
			structures = ""
			if len(quad.structures) == 2:
				for struct in quad.structures:     # no more than 2 structures per quadrant
					structures += struct.code
			elif len(quad.structures) == 1:
				for struct in quad.structures:   
					structures += str(struct.code)
					structures += " "
			elif len(quad.structures) == 0:
				structures = "  "
				
			codecos = {	0 : "°═══",
						1 : "°══*",
						4 : "°═**",
						9 : "°***"}		
			slotcode = codecos[quad.slots]
			
			coderef = { "black_hole" : "@",
						"proton_superstring": "§",
						"alien_station" : "A",
						"wreckage" : "w",
						"nebula": "N",
						"singularity" : "#",
						None : "╗"}
						
			special = quad.special
			
			specialsym = coderef[special]
			
			todisplay = list("╔{}{}{}║{}{}║╚{}╝".format(smallships, bigships, specialsym, structures, capital, slotcode))
			

		list_ref.append(todisplay)
	
	return list_ref

def displayGrid():
	
	global MAP_size, MAP, MAIN_looper, MAP_name
	
	height,width = MAP_size
	
	rawmap = rawMap() # returns a list of 18-elems lists of strings; each of which represents a 6x3-chars quadrant
	
	rawmap_normalised = []
	
	toplines = []
	midlines = []
	botlines = []
	
	print("[The Conquest Of Space v0.1] sector {}, turn {}.".format(MAP_name,MAIN_looper.turn))
	
	def glue(listofstrings):
		line = ""
		for a in  listofstrings:
			line += a
		return line
	
	for elem in rawmap:
		topline = elem[:6]
		midline = elem[6:12]
		botline = elem[12:18]
		
		topline = glue(topline)
		midline = glue(midline)
		botline = glue(botline)
		
		toplines.append(topline)
		midlines.append(midline)
		botlines.append(botline)
	
	for i in range(height):
		Tline = ""
		for e in range(width):
			to_add = toplines.pop(0)
			Tline += to_add	
		print(Tline)
		
		Mline = ""
		for e in range(width):
			to_add = midlines.pop(0)
			Mline += to_add	
		print(Mline)
		
		Bline = ""
		for e in range(width):
			to_add = botlines.pop(0)
			Bline += to_add	
		print(Bline)
	
	print("")

def newgame(loop):
	newmap(10,10)
	newloop = roundloop()
	if loop == 1:
		newloop.startLooping()
	else:
		print('Done. To loop: tcos.MAIN_looper.startLooping()')

newgame(0)
displayGrid()
aldo = player()
displayGrid()
#MAIN_looper.startLooping()


sample_character = {'descriptor_name': 'The Scavenger',
					'on_big_ship_destroy': (player.giveEnergyBoost,'nextturn',1),
					'on_structure_destroy': (player.giveEnergyBoost,'nextturn',1)}

sample_objective = [ 	(player.hasKilled,('ships',25)),
						(player.hasEnergy,(20)),
						(player.hasTerritories,('planets',2))]
