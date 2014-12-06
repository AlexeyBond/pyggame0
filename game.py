#!/usr/bin/python
# coding=UTF-8

from framework import *
import math, random

@ScreenClass('STARTUP')
class StartupScreen(AppScreen):
	def __init__(self):
		AppScreen.__init__(self)

		self.addLayer(StaticBackgroundLauer('rc/256x256bg.png','fill'))

		GAME_CONSOLE.write('Startup screen created.')

	def on_key_press(self,key,mod):
		GAME_CONSOLE.write('SSC:Key down:',KEY.symbol_string(key),'(',key,') [+',KEY.modifiers_string(mod),']')

anilist = AnimationList({
	'AAA':[
		{'img':'rc/256x256bg.png','t':1,'anchor':'center','rect':(64,0,32,32)},
		{'img':'rc/256x256bg.png','t':1,'anchor':'center','rect':(64,32,32,32)}
		]
	}
)


@ScreenClass('STARTUP')
@ScreenClass('GAME')
class GameScreen(AppScreen):
	def __init__(self):
		AppScreen.__init__(self)

		self.game = Game( )
		self.game.unpause( )
		self.camera = Camera( )

		# ent1 = SpriteGameEntity()
		ent1 = AnimatedGameEntity(anilist)
		ent1.scale = 10
		self.game.addEntity(ent1)

		self.addLayer(GameWorldLayer(self.game,self.camera))
		#self.addLayer(GUITextItemLayer(-10,0,text='Hello lol'))
		self.addLayer(GUIButtonItemLayer(0,0,'rc/128x128btn.png'))
		GAME_CONSOLE.write('Game screen created.')

		PreloadStaticSound('rc/snd/buttonclick.ogg','CLICK')

	def on_resize(self,width,height):
		AppScreen.on_resize(self,width,height)

		self.camera.set_size(width,height)

	def on_mouse_scroll(self,x,y,sx,sy):
		self.camera.scale *= 2 ** (sy*0.02)

	def on_key_press(self,key,mod):
		GAME_CONSOLE.write('SSC:Key down:',KEY.symbol_string(key),'(',key,') [+',KEY.modifiers_string(mod),']')
		PlayStaticSound('CLICK')

		if key == KEY.UP:
			self.camera.focus_y += 1
		if key == KEY.DOWN:
			self.camera.focus_y -= 1
		if key == KEY.RIGHT:
			self.camera.focus_x += 1
		if key == KEY.LEFT:
			self.camera.focus_x -= 1
#один класс на двух червей
class Worm(SpriteGameEntity):
	def __init__(self,sx,sy,sprite,id):
		SpriteGameEntity.__init__(self,sprite)
		self.id = id
		self.x = sx
		self.y = sy
		self.vx = 1
		self.vy = 0
		self.lastTurn = 0
		self.angle = 0
		self.angVelocity = 0
		#!!!подумать как ставить радиус
		self.radius = 1

	def update(self, dt):
		lastTurn += dt
		if lastTurn > 1000:
			self.turn()
			lastTurn = 0
		for ent in self.game.entities:
			#проверка на себя и невидимых сущностей
			if ent == self or ent.sprite.visiable:
				continue
			#проверка столкновения
			if self.distance(ent) < 10:
				self.collide(ent)

	def velocity(self):
		return math.sqrt(self.vx*self.vx + self.vy*self.vY)

	def setVelocity(slef, k = 1):
		self.vx = k*self.vx
		self.vy = k*self.vy

	def turn(self, angle = 0):
		if angle <= 0:
			angle = random.randint(-15,15)
			angVelocity = random.randint(0,angle)
			angleRad = angle / 180.0 * math.pi
			angVelocityRad = angVelocity / 180.0 * math.pi
		self.vx, self.vy =\
		self.vx * math.cos(angVelocityRad) - self.vy * math.sin(angVelocityRad),\
		self.vx * math.sin(angVelocityRad) + self.vy * math.cos(angVelocityRad)
		angle -= angVelocity
		#self.sprite.rotate(angVelocity)
 


	#возвращает расстояние от текущей сущности до указанной
	def distance(self, entity):
		dx = ent.x - self.x
		dy = ent.y - self.y
		return math.sqrt(dx*dx + dy*dy)-entity.radius

	#действие столкновения
	def collide(self, entity):
		if entity.a.__class__.__name__ == 'Apple':
			#ent.eaten method(self)
			self.eat()
		elif entity.a.__class__.__name__ == 'Worm':
			dx = abs(entity.x - self.x)
			dy = abs(entity.y - self.y)
			dl = math.sqrt(dx*dx + dy*dy)
			dx /= dl
			dy /= dl
			#скалярное проиведение
			scalarMul = self.vx*ent.vx + self.vy*ent.vy
			self.vx = self.vx - 2 * dx * scalarMul
			self.vy = self.vy - 2 * dy * scalarMul
			ent.vx = ent.vx - 2 * dx * scalarMul
			ent.vy = ent.vy - 2 * dy * scalarMul
			self.lastTurn = 0
			ent.lastTurn = 0

	def eat(self):
		#анимка, звук поедания яблока или надо будет переопределить для каждого червя
		pass

