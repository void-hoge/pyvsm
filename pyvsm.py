#!/usr/bin/env python3
import sys

class instruction():
	def __init__(self, num = 0, name='EXIT', first=0, second=0):
		self.num = num
		self.name = name
		self.first = first
		self.second = second
	def __repr__(self):
		return 'instruction<num:{}, name:{}, first:{}, second:{}>'.format(self.num, self.name, self.first, self.second)

def remove_comments(str):
	# x86 comment style
	result = ''
	i = 0
	while i < len(str):
		if str[i] == ';':
			while i < len(str) and str[i] != '\n':
				i+=1
		if i < len(str):
			result = result+str[i]
		i+=1
	return result

def lex(str):
	all = str.split('\n')
	result = []
	count = 0
	for line in all[:-1]:
		tmp = line.split()
		linenum = 0
		name = ''
		first = 0
		second = 0
		try:
			linenum = int(tmp[0])
			linenum = count
			if len(tmp) == 2:
				name = tmp[1]
			elif len(tmp) == 3:
				name = tmp[1]
				try:
					first = int(tmp[2])
				except Exception as e:
					raise Exception('line {}, Invalid token {}.'.format(count,tmp[2]))
			elif len(tmp) >= 4:
				name = tmp[1]
				try:
					first = int(tmp[2])
					second = int(tmp[3])
				except Exception as e:
					raise Exception('line {}, Invalid token {} {}.'.format(count, tmp[2], tmp[3]))
		except Exception as e:
			linenum = count
			if len(tmp) == 1:
				name = tmp[0]
			elif len(tmp) == 2:
				name = tmp[0]
				try:
					first = int(tmp[1])
				except Exception as e:
					raise Exception('line {}, Invalid token {}.'.format(count,tmp[1]))
			elif len(tmp) >= 3:
				name = tmp[0]
				try:
					first = int(tmp[1])
					second = int(tmp[2])
				except Exception as e:
					raise Exception('line {}, Invalid token {} {}.'.format(count, tmp[1], tmp[2]))
		result.append(instruction(count, name, first, second))
		count+=1
	return result

class vsm:
	def __init__(self, prog):
		self.stack_pointer = -1
		self.program_counter = 0
		self.memory = [0 for _ in range(200)]
		self.base0 = 0
		self.base1 = 0
		self.prog = prog
		self.max_sp = self.stack_pointer

	def dump_memory(self):
		for a in self.memory:
			print(a, end=' ')
		print()

	def dump_prog(self):
		for tmp in self.prog:
			print('{}: {} {} {}'.format(tmp.num, tmp.name, tmp.first, tmp.second))

	def exec(self):
		if self.program_counter >= len(self.prog):
			return False
		code = self.prog[self.program_counter]
		if code.name == 'EXIT':
			self.exit()
		elif code.name == 'LC':
			self.load_constant(code.first)
		elif code.name == 'LA':
			self.load_adress(code.first, code.second)
		elif code.name == 'LV':
			self.load_variable(code.first, code.second)
		elif code.name == 'LI':
			self.load_indirect()
		elif code.name == 'SI':
			self.store_indirect()
		elif code.name == 'SV':
			self.store_variable(code.first, code.second)
		elif code.name == 'DUP':
			self.duplicate()
		elif code.name == 'ISP':
			self.increment_stack_pointer(code.first)
		elif code.name == 'GETC':
			self.get_charactor()
		elif code.name == 'GETI':
			self.get_integer()
		elif code.name == 'PUTC':
			self.put_charactor()
		elif code.name == 'PUTI':
			self.put_integer()
		elif code.name == 'ADD':
			self.add()
		elif code.name == 'SUB':
			self.subtruct()
		elif code.name == 'MUL':
			self.multiply()
		elif code.name == 'DIV':
			self.divide()
		elif code.name == 'MOD':
			self.modulo()
		elif code.name == 'INV':
			self.invert()
		elif code.name == 'EQ':
			self.equal()
		elif code.name == 'NE':
			self.not_equal()
		elif code.name == 'GT':
			self.greater_than()
		elif code.name == 'LT':
			self.less_than()
		elif code.name == 'GE':
			self.greater_than()
		elif code.name == 'LE':
			self.less_or_equal_than()
		elif code.name == 'B':
			self.branch(code.first)
		elif code.name == 'BZ':
			self.branch_if_zero(code.first)
		elif code.name == 'SB':
			self.set_base(code.second)
		elif code.name == 'CALL':
			self.call(code.first)
		elif code.name == 'RET':
			self.ret()
		else:
			raise Exception('At line {}, invalid token {}.'.format(code.num, code.name))
		self.program_counter+=1
		if self.stack_pointer > self.max_sp:
			self.max_sp = self.stack_pointer
		sys.stdout.flush()
		return True

	def run(self):
		while self.exec():
			pass

	def exit(self):
		 sys.exit(self.memory[self.stack_pointer])

	def load_constant(self, val):
		self.stack_pointer+=1
		self.memory[self.stack_pointer] = val

	def load_adress(self, b, a):
		self.stack_pointer+=1
		if b == 0:
			self.memory[self.stack_pointer] = self.base0+a
		elif b == 1:
			self.memory[self.stack_pointer] = self.base1+a
		else:
			raise Exception('Invalid base register B{}. There are B0 or B1.'.format(b))

	def load_variable(self, b, a):
		self.stack_pointer+=1
		if b == 0:
			self.memory[self.stack_pointer] = self.memory[self.base0+a]
		elif b == 1:
			self.memory[self.stack_pointer] = self.memory[self.base1+a]
		else:
			raise Exception('Invalid base register B{}. There are B0 or B1.'.format(b))

	def load_indirect(self):
		self.memory[self.stack_pointer] = self.memory[self.memory[self.stack_pointer]]

	def store_indirect(self):
		self.memory[self.memory[self.stack_pointer-1]] = self.memory[self.stack_pointer]
		self.stack_pointer-=2

	def store_variable(self, b, a):
		if b == 0:
			self.memory[self.base0+a] = self.memory[self.stack_pointer]
		elif b == 1:
			self.memory[self.base1+a] = self.memory[self.stack_pointer]
		else:
			raise Exception('Invalid base register B{}. There are B0 or B1'.format(b))
		self.stack_pointer-=1

	def duplicate(self):
		self.stack_pointer+=1
		self.memory[self.stack_pointer] = self.memory[self.stack_pointer-1]

	def increment_stack_pointer(self, c):
		self.stack_pointer += c

	def get_charactor(self):
		self.stack_pointer+=1
		self.memory[self.stack_pointer] = ord(input()[0])

	def get_integer(self):
		self.stack_pointer+=1
		self.memory[self.stack_pointer] = int(input())

	def put_charactor(self):
		print(chr(self.memory[self.stack_pointer]), end='')
		self.stack_pointer-=1

	def put_integer(self):
		print(self.memory[self.stack_pointer], end='')
		self.stack_pointer-=1

	def add(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=self.memory[self.stack_pointer]+self.memory[self.stack_pointer+1]

	def subtruct(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=self.memory[self.stack_pointer]-self.memory[self.stack_pointer+1]

	def multiply(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=self.memory[self.stack_pointer]*self.memory[self.stack_pointer+1]

	def divide(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=self.memory[self.stack_pointer]//self.memory[self.stack_pointer+1]

	def modulo(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=self.memory[self.stack_pointer]%self.memory[self.stack_pointer+1]

	def invert(self):
		self.memory[self.stack_pointer]=-self.memory[self.stack_pointer];

	def equal(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=int(self.memory[self.stack_pointer]==self.memory[self.stack_pointer+1])

	def not_equal(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=int(self.memory[self.stack_pointer]!=self.memory[self.stack_pointer+1])

	def greater_than(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=int(self.memory[self.stack_pointer]>self.memory[self.stack_pointer+1])

	def less_than(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=int(self.memory[self.stack_pointer]<self.memory[self.stack_pointer+1])

	def greater_or_equal(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=int(self.memory[self.stack_pointer]>=self.memory[self.stack_pointer+1])

	def less_or_equal_than(self):
		self.stack_pointer-=1
		self.memory[self.stack_pointer]=int(self.memory[self.stack_pointer]<=self.memory[self.stack_pointer+1])

	def branch(self, a):
		self.program_counter+=a

	def branch_if_zero(self, a):
		if self.memory[self.stack_pointer] == 0:
			self.program_counter+=a
		self.stack_pointer-=1

	def set_base(self, b):
		if b == 0:
			self.base0 = self.memory[self.stack_pointer]
		elif b == 1:
			self.base1 = self.memory[self.stack_pointer]
		else:
			raise Exception('Invalid base register B{}. There are B0 or B1'.format(b))
		self.stack_pointer-=1

	def call(self, a):
		self.memory[self.stack_pointer+2] = self.base1
		self.memory[self.stack_pointer+3] = self.program_counter
		self.base1 = self.stack_pointer+1
		self.program_counter = a-1

	def ret(self):
		self.stack_pointer = self.base1
		self.base1 = self.memory[self.stack_pointer+1]
		self.program_counter = self.memory[self.stack_pointer+2]

def main():
	file = sys.argv[1]
	code = open(file).read()
	hoge = vsm(lex(remove_comments(code)))
	hoge.run()

if __name__ == '__main__':
	main()
