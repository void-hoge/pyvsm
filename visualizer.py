#!/usr/bin/env python3
import pygame
import pyvsm
import sys

class visualizer():
	background = (0,0,0)
	def __init__(self, file):
		self.code = open(file).read()
		self.vsm = pyvsm.vsm(pyvsm.lex(pyvsm.remove_comments(self.code)))
		self.screen_size = (1280, 720)
		self.mem_zero = (0,0)
		self.mem_height = 50
		self.mem_width = 200
		self.prog_zero = (400,0)
		self.prog_height = 50
		self.prog_width = 200
		pygame.init()
		self.screen = pygame.display.set_mode(self.screen_size, pygame.RESIZABLE)
		self.font = pygame.font.SysFont("Roboto", 30)
		pygame.display.flip()
		self.set_pos()
		self.set_prog()
		self.set_memory()

	def set_memory(self):
		i = 0
		panel_color = (255,255,255)
		while i <= self.vsm.max_sp:
			if i == self.vsm.stack_pointer:
				panel_color = (255, 255, 0)
			else:
				panel_color = (255,255,255)
			pygame.draw.rect(self.screen, panel_color, pygame.Rect(self.mem_zero[0], self.mem_zero[1]+i*self.mem_height, self.mem_width, self.mem_height-5))
			self.screen.blit(self.font.render('{}: {}'.format(i, self.vsm.memory[i]), True, (0,0,0)), (self.mem_zero[0], self.mem_zero[1]+i*self.mem_height))
			i+=1

	def set_base(self):
		pygame.draw.rect(self.screen, (0,255,0), pygame.Rect(self.mem_zero[0]+self.mem_width, self.mem_zero[1]+self.vsm.base0*self.mem_height, self.mem_width/2, self.mem_height-5))
		self.screen.blit(self.font.render('B0', True, (0,0,0)), (self.mem_zero[0]+self.mem_width, self.mem_zero[1]+self.vsm.base0*self.mem_height))

		pygame.draw.rect(self.screen, (0,0,255), pygame.Rect(self.mem_zero[0]+self.mem_width*1.5, self.mem_zero[1]+self.vsm.base1*self.mem_height, self.mem_width/2, self.mem_height-5))
		self.screen.blit(self.font.render('B1', True, (0,0,0)), (self.mem_zero[0]+self.mem_width*1.5, self.mem_zero[1]+self.vsm.base1*self.mem_height))

	def set_prog(self):
		i = 0
		panel_color = (255,255,255)
		while i < len(self.vsm.prog):
			if i == self.vsm.program_counter:
				panel_color = (255,255,0)
			else:
				panel_color = (255,255,255)
			tmp = self.vsm.prog[i]
			pygame.draw.rect(self.screen, panel_color, pygame.Rect(self.prog_zero[0], self.prog_zero[1]+i*self.prog_height, self.prog_width, self.prog_height-5))
			self.screen.blit(self.font.render(str('{}: {} {} {}'.format(tmp.num,tmp.name,tmp.first,tmp.second)), True, (0,0,0)),(self.prog_zero[0], self.prog_zero[1]+i*self.prog_height))
			i+=1

	def mem_selected(self, pos):
		if self.mem_zero[0] <= pos[0] and pos[0] < self.mem_zero[0]+self.mem_width:
			return True
		else:
			return False

	def prog_selected(self, pos):
		if self.prog_zero[0] <= pos[0] and pos[0] < self.prog_zero[0]+self.prog_width:
			return True
		else:
			return False

	def exec(self):
		flag = self.vsm.exec()
		self.set_pos()
		return flag

	def set_pos(self):
		self.mem_zero = (self.mem_zero[0], 360-self.vsm.stack_pointer*self.mem_height)
		self.prog_zero = (self.prog_zero[0], 360-self.vsm.program_counter*self.prog_height)

	def draw(self):
		self.screen.fill(self.background)
		pos = pygame.mouse.get_pos()
		self.set_memory()
		self.set_prog()
		self.set_base()
		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				return False
			if event.type == pygame.KEYDOWN:
				if event.key == ord('q'): # quit
					return False
				if event.key == ord(' '): # execute
					return self.exec()
			if event.type == pygame.MOUSEBUTTONDOWN:
				if event.button == 4: # scroll
					if self.mem_selected(pos):
						self.mem_zero = (self.mem_zero[0], self.mem_zero[1]+20)
					elif self.prog_selected(pos):
						self.prog_zero = (self.prog_zero[0], self.prog_zero[1]+20)
				elif event.button == 5:
					if self.mem_selected(pos):
						self.mem_zero = (self.mem_zero[0], self.mem_zero[1]-20)
					elif self.prog_selected(pos):
						self.prog_zero = (self.prog_zero[0], self.prog_zero[1]-20)
		pygame.display.flip()
		return True

def main():
	file = sys.argv[1]
	vsl = visualizer(file)
	while vsl.draw():
		pass

if __name__ == '__main__':
	main()
