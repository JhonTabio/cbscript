from mcfunction import mcfunction

class global_context(object):
	def __init__(self, friendly_name):
		self.clocks = []
		self.functions = {}
		self.reset = None
		self.objectives = {}
		self.constants = []
		self.arrays = {}
		self.scratch = {}
		self.temp = 0
		self.rand = 0
		self.unique = 0
		self.friendly_name = friendly_name
		self.block_tags = {}
		self.scratch_prefixes = {}

	def register_block_tag(self, name, blocks):
		self.block_tags[name] = blocks
		
	def get_unique_id(self):
		self.unique += 1
		return self.unique
	
	def register_clock(self, name):
		self.clocks.append(name)
		
	def register_function(self, name, func):
		if name in self.functions:
			raise Exception('Function "{}" is defined multiple times.'.format(name))
		self.functions[name] = func
		
	def register_array(self, name, from_val, to_val):
		if name in self.arrays:
			raise Exception('Array "{}" is defined multiple times.'.format(name))
		self.arrays[name] = (from_val, to_val)
		
	def get_placeholder_clock(self, namespace, environment):
		f = mcfunction(environment)
		for clock in self.clocks:
			f.add_command('/function {0}:{1}'.format(namespace, clock))
		
		return f
		
	def register_objective(self, objective):
		if len(objective) > 16:
			raise Exception('Cannot create objective "{0}", name is {1} characters (max is 16)'.format(objective, len(objective)))
		self.objectives[objective] = True
	
	def get_reset_function(self):
		return self.functions['reset']
		
	def get_constant_name(self, c):
		if c == -1:
			return 'minus'
		elif c >= 0:
			return 'c{}'.format(c)
		else:
			return 'cm{}'.format(-c)
		
	def add_constant(self, c):
		if c not in self.constants:
			self.constants.append(c)
	
		return self.get_constant_name(c)
		
	def add_constant_definitions(self):
		f = self.get_reset_function()
	
		if len(self.constants) > 0:
			f.insert_command('/scoreboard objectives add Constant dummy', 0)
			for c in self.constants:
				f.insert_command('/scoreboard players set {} Constant {}'.format(self.get_constant_name(c), c), 1)

	def allocate_scratch(self, prefix, n):
		if prefix not in self.scratch:
			self.scratch[prefix] = 0
			
		if n > self.scratch[prefix]:
			self.scratch[prefix] = n
	
	def allocate_temp(self, temp):
		if temp > self.temp:
			self.temp = temp
	
	def allocate_rand(self, rand):
		if rand > self.rand:
			self.rand = rand
	
	def finalize_functions(self):
		for func in self.functions.values():
			func.finalize()
			
	def get_scratch_prefix(self, name):
		name = name[:3]
		if name in self.scratch_prefixes:
			i = 2
			while '{0}{1}'.format(name, i) in self.scratch_prefixes:
				i += 1
			
			name = '{0}{1}'.format(name, i)
			self.scratch_prefixes[name] = True
			return name
		else:
			self.scratch_prefixes[name] = True
			return name