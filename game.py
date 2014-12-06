#!/usr/bin/python
# coding=UTF-8

from framework import *

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

		self.pbar = GUIVerticalProgressBarItemLayer(offset_x=-50,offset_y=0,height=300,width=30)

		self.addLayer(self.pbar)

	def on_resize(self,width,height):
		AppScreen.on_resize(self,width,height)

		self.camera.set_size(width,height)

	def on_mouse_scroll(self,x,y,sx,sy):
		self.camera.scale *= 2 ** (sy*0.02)

		self.pbar.status *= 2 ** (sy*0.02)

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
			
class GravityBox(SpriteGameEntity):
	boxes = []
	def __init__(self, sx, sy):
		SpriteGameEntity.__init__(self, "rc/32x32fgA.png")
		self.x = sx
		self.y = sy
		GravityBox.boxes.append(self)
	def update(self, dt):
		dt = dt*20
		vx = 0
		vy = 0
		for ent in GravityBox.boxes:
			if ent == self:
				continue
			dx = ent.x - self.x
			dy = ent.y - self.y
			k = 1.0 / math.sqrt(dx*dx + dy*dy)
			vx += k*dx*dt
			vy += k*dy*dt
		self.x += vx
		self.y += vy
		self.end_update_coordinates


class Apple(SpriteGameEntity):
	apple_image_1 = LoadTexture('rc/apple1.png',anchor='center')
	apple_image_2 = LoadTexture('rc/apple2.png',anchor='center')
	def __init__(self):
		SpriteGameEntity.__init__(self,sprite_image=Apple.apple_image_1)
		self.radius = 32
		self.reset( )

	def eat(self,worm):
		if self.eaten and worm.id == 2:
			self.game.on_apple_eat( )
			self.reset( ) 
		elif worm.id == 1 and not self.eaten:
			self.eaten = True
			self.sprite.image = Apple.apple_image_2

	def put(self,x,y):
		self.x,self.y = x,y
		self.sprite.visible = True
		self.end_update_coordinates( )

	def reset(self):
		self.sprite.visible = False
		self.eaten = False
		self.sprite.image = Apple.apple_image_1

	def update(self,dt):
		self.scale = 1.0 + 0.2 * math.sin(self.game.time)
		self.end_update_coordinates( )

