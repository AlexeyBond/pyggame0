#!/usr/bin/python
# coding=UTF-8

import pyglet
from pyglet.gl import *
from pyglet.window import key as KEY

###############################################################################
# Очень базовые классы / Графический интерфейс                                #
###############################################################################

# Абстрактный класс для экранов и слоёв
# Имеет размеры, метод их изменения,
# и метод отрисовки.
class Drawable:
	def __init__(self):
		self.height = 0
		self.width = 0

	def resize(self,width,height):
		if self.width != width or self.height != height:
			self.on_resize(width,height)
			self.width = width
			self.height = height

	def draw(self):
		pass

	def on_resize(self,width,height):
		pass

### Абстрактный класс слоя
class Layer(Drawable):
	def __init__(self):
		Drawable.__init__(self)
		self.visible = True
		self.screen = None	# Установится при добавлении к экрану.

### Абстрактный класс экрана
class AppScreen(Drawable):
	### Работа с сокращёнными обозначениями
	# Словарь, содержащий обозначения классов экранов.
	SCREEN_CLASSES = {}

	# Статический метод, создающий новый экран
	@staticmethod
	def new(classname,*args,**kwargs):
		if classname in AppScreen.SCREEN_CLASSES:
			return AppScreen.SCREEN_CLASSES[classname](*args,**kwargs)
		else:
			return None

	###
	#
	def __init__(self):
		Drawable.__init__(self)

		# Список слоёв, из которых состоит экран
		self.layers = []

		# Ссылка на экран, к которому нужно переключиться
		# при первой возможности
		self.next = None

		# True если нужно выйти из приложения
		self.need_exit = False

		# True если нужно сохранять ссылку на предидущий экран.
		# Иначе он будет уничтожаться.
		self.keep_prevous = False
		# Та самая ссылка
		self.prevous = None

	# Вызывается, когда зкран становится активным
	# prevous - предидущий активный экран
	def activate(self,prevous):
		if prevous != None and not self.keep_prevous:
			prevous.exit( )
			prevous.next = None
		else:
			if self.prevous != None:
				self.prevous.exit( )
			self.prevous = prevous

	# Метод, создающий новый экран, который затем станет активным
	def set_next(self,classname,*args,**kwargs):
		self.next = AppScreen.new(classname,*args,**kwargs)

	# Вернуться к предидущему экрану, если ссылка сохранена
	def go_back(self):
		if self.prevous != None:
			self.next = self.prevous

	# Обработка событий
	def dispatch_event(self,event_type,*args):
		if event_type in dir(self):
			getattr(self,event_type)(*args)
		for layer in self.layers:
			if event_type in dir(layer):
				getattr(layer,event_type)(self,*args)

	#
	def draw(self):
		for layer in self.layers:
			if layer.visible:
				layer.draw( )

	#
	def on_resize(self,width,height):
		for layer in self.layers:
			layer.resize(width,height)

	# Добавить слой на экран
	def addLayer(self,layer):
		self.layers.append(layer)
		layer.screen = self

	# Вызывается при уничтожении экрана
	def exit(self):
		if self.prevous != None:
			self.prevous.exit( )

### Декоратор, дающий классу экрана короткое обозначение
def ScreenClass(cname):
	def ScreenClassDecorator(sclass):
		AppScreen.SCREEN_CLASSES[cname] = sclass
		return sclass
	return ScreenClassDecorator

### Консолька внутри игры. Удобно для отладки
class GameConsole:
	def __init__(self,nlines=40,fsize=18):
		self.fsize = fsize
		self.nlines = nlines
		self.lines = []
		self.current_line = 0
		self.visible = True
		self.fps_display = pyglet.clock.ClockDisplay()
		for i in range(nlines):
			newln = pyglet.text.Label(text='',font_size=18,x=0,y=0,font_name='Courier New')
			newln.console_line_id = i
			self.lines.append( newln )

	def update_positions(self):
		for ln in self.lines:
			ln.begin_update( )
			lnid = (ln.console_line_id + self.nlines - self.current_line) % self.nlines
			ln.y = lnid * (self.fsize * 1.0) + 10
			ln.end_update( )

	def _insert_line(self,text):
		self.current_line = (self.nlines + self.current_line - 1) % self.nlines
		ln = self.lines[self.current_line]
		ln.begin_update( )
		ln.text = str(text)
		ln.end_update( )

	def insert_line(self,text):
		self._insert_line(text)
		self.update_positions( )

	def insert_text(self,text):
		for ln in text.split('\n'):
			self._insert_line(ln)
		self.update_positions( )

	def write(self,*args):
		text = ''
		for a in args:
			text += str(a)
		print text
		self.insert_text(text)

	def draw(self):
		if self.visible:
			for l in self.lines:
				l.draw( )
			self.fps_display.draw( )

# Не самая лучшая идея создавать её прямо здесь,
# но по-другому оно не хотело работать.
GAME_CONSOLE = GameConsole( )

### Класс главного окна
class MainWindow(pyglet.window.Window):
	def __init__(self):
		global GAME_CONSOLE
		pyglet.window.Window.__init__(self)

		self.init_opengl( )

		# Ограничение частоты кадров
		pyglet.clock.set_fps_limit(60)

		GAME_CONSOLE.write('-- Starting --')

		#
		self.cur_screen = None
		self.change_screen(AppScreen.new('STARTUP'))

	### Вспомогательные функции

	# Предварительная настройка OpenGL
	def init_opengl(self):
		glClearColor(0.3, 0.3, 0.3, 1.0)

	# Настройка матрицы проекции и вьюпорта под размеры окна
	def setup_projection(self,width,height):
		glViewport(0,0,width,height)
		glMatrixMode(GL_PROJECTION)
		glLoadIdentity( )
		glOrtho(0,width,0,height,-1,1)
		glMatrixMode(GL_MODELVIEW)
		glLoadIdentity( )

	# Переключится на другой экран
	def change_screen(self,screen):
		screen.activate(self.cur_screen)
		self.cur_screen = screen
		self.cur_screen.resize(self.width,self.height)

	### Обработка событий

	def dispatch_event(self, event_type, *args):
		if event_type in ('on_key_press','on_key_release','on_mouse_drag','on_mouse_enter','on_mouse_leave','on_mouse_motion','on_mouse_press','on_mouse_release','on_mouse_scroll'):
			self.cur_screen.dispatch_event(event_type,*args)
			if self.cur_screen.need_exit:
				self.close( )
			elif self.cur_screen.next != None:
				self.change_screen(self.cur_screen.next)
		super(MainWindow,self).dispatch_event(event_type,*args)

	# Отрисовка содержимого окна
	def on_draw(self):
		# Очистить окно
		self.clear( )

		# На всякий случай ещё и так
		glClear(GL_COLOR_BUFFER_BIT)

		# Рисуем текущий зкран
		self.cur_screen.draw( )

		# И консольку сверху
		GAME_CONSOLE.draw( )

	# Изменение размера окна
	def on_resize(self,width,height):
		GAME_CONSOLE.write( 'Window resized: %sx%s'%(width,height) )
		self.setup_projection(width,height)
		self.cur_screen.resize(width,height)

	# Нажатие кнопки на клавиатуре
	def on_key_press(self,key,mod):
		if key in (KEY.QUOTELEFT,KEY.ASCIITILDE):
			GAME_CONSOLE.visible = not GAME_CONSOLE.visible
		elif key == KEY.ESCAPE and mod == KEY.MOD_CTRL:
			self.close( )

	# Закрытие окна [Х]рестикомъ
	def on_close(self):
		print 'Window closed by user'
		exit(0)


###############################################################################
# Просто полезные штуки / Графический интерфейс                               #
###############################################################################

### 
def ApplyTextureAnchor(texture,anchor='default'):
	if anchor == 'center':
		texture.anchor_x = texture.width // 2
		texture.anchor_y = texture.height // 2

### Загружает текстуру.
def LoadTexture(name,anchor='default'):
	tex = pyglet.resource.image(name).get_texture( )
	ApplyTextureAnchor(tex,anchor)
	return tex


### Статический задний фон.
class StaticBackgroundLauer(Layer):
	### Конструктор
	# Аргументы:
	# imgpath - путь к файлу изображения
	# mode - одно из следующих значений:
	# - 'fit' - изображение растягивается на весь экран
	# - 'center' - изображение по центру
	# - 'scale' - на весь экран с соблюдением пропорций
	# - 'fill' - на весь экран с соблюдением пропорций
	#               и полным заполнением пространства
	def __init__(self,imgpath,mode='fit'):
		Layer.__init__(self)
		self.mode = mode
		self.texture = LoadTexture(imgpath)
		self.recalc( )
		self.tx = 0
		self.ty = 0
		self.tw = self.width
		self.th = self.height

	# Зло злое
	def recalc(self):
		if self.mode == 'fit':
			self.tx = 0
			self.ty = 0
			self.tw = self.width
			self.th = self.height
			return
		cx = self.width // 2
		cy = self.height // 2
		hw = self.texture.width // 2
		hh = self.texture.height // 2
		if self.mode == 'center':
			self.tx = cx - hw
			self.ty = cy - hw
			self.tw = self.texture.width
			self.th = self.texture.height
		elif (self.mode == 'scale') or (self.mode == 'fill'):
			fill = (self.mode == 'fill')
			tw = float(self.texture.width)
			th = float(self.texture.height)
			sw = float(self.width)
			sh = float(self.height)
			if sh == 0 or sw == 0:
				return
			tr = tw / th
			sr = sw / sh
			if tr == sr:
				self.tx = 0
				self.ty = 0
				self.tw = self.width
				self.th = self.height
			elif (tr > sr) != fill:
				self.tx = 0
				self.tw = self.width
				hh = hh * (sw / tw)
				self.ty = int(cy - hh)
				self.th = int(hh * 2)
			elif (tr < sr) != fill:
				self.ty = 0
				self.th = self.height
				hw = hw * (sh / th)
				self.tx = int(cx - hw)
				self.tw = int(hw * 2)

	def on_resize(self,width,height):
		self.width = width
		self.height = height
		self.recalc( )

	def draw(self):
		self.texture.blit(x=self.tx,y=self.ty,width=self.tw,height=self.th)

### Слой, рисующий игровой мир.
class GameWorldLayer(Layer):
	def __init__(self,game,camera):
		Layer.__init__(self)

		self.game = game
		self.camera = camera

	def draw(self):
		glPushMatrix( )
		self.camera.apply_transform( )
		self.game.draw_all( )
		glPopMatrix( )

###############################################################################
# Звук                                                                        #
###############################################################################

###
# !!! НЕИСТОВЫЙ ВАРНИНГ !!!
# Для загрузки сжатых форматов (mp3, ogg)
# требует наличия в системе библиотеки AVbin
###

#
STATIC_SOUND_SOURCES = {}
MUSIC_SOUND_SOURCES = {}
MUSIC_PLAYER = None

# Проигрывает короткий звук
def PlayStaticSound(name):
	if name in STATIC_SOUND_SOURCES:
		if STATIC_SOUND_SOURCES[name] != None:
			return STATIC_SOUND_SOURCES[name].play( )
		else:
			return None
	try:
		STATIC_SOUND_SOURCES[name] = pyglet.media.load(filename=name,streaming=False)
	except Exception as e:
		STATIC_SOUND_SOURCES[name] = None
		GAME_CONSOLE.write("Couldn't load sound file: ",name)
		print e
	PlayStaticSound(name)

# Играет музыку
def PlayMusic(name):
	if name in MUSIC_SOUND_SOURCES:
		if MUSIC_SOUND_SOURCES[name] != None:
			MUSIC_PLAYER.queue(MUSIC_SOUND_SOURCES[name])
			if MUSIC_PLAYER.playing:
				MUSIC_PLAYER.next( )
			else:
				MUSIC_PLAYER.play( )
		else:
			MUSIC_PLAYER.next( )
	# Создаём плеер, если его ещё нет
	if MUSIC_PLAYER == None:
		MUSIC_PLAYER = pyglet.media.player( )
		MUSIC_PLAYER.eos_action = pyglet.media.player.EOS_LOOP
	#
	try:
		MUSIC_SOUND_SOURCES[name] = pyglet.media.load(filename=name,streaming=True)
	except Exception e:
		MUSIC_SOUND_SOURCES[name] = None
		GAME_CONSOLE.write("Couldn't load sound file: ",name)
		print e
	PlayMusic(name)


###############################################################################
# Очень базовые классы / Игра                                                 #
###############################################################################

# Собстна игра.
class Game:
	def __init__(self):
		self.upd_callback = lambda dt: self.update(dt)

		# Пространства
		self.world_space = EuclidianWorldSpace( )
		self.view_space = EuclidianViewSpace( )

		# Список сущностей
		self.entities = []
		# ~ требующих дополнительного вызова draw()
		self.custom_draw_entities = []
		# ~ имеющих уникальные иденитфикаторы
		self.indexed_entities = {}

		# Батч для спрайтов сущностей
		self.sprite_batch = pyglet.graphics.Batch( )

		# Игровое время
		self.time = 0

	def newSprite(self,image,**kwargs):
		return pyglet.sprite.Sprite(img=image,batch=self.sprite_batch,**kwargs)

	# Включает/возобновляет обновление сущностей
	def unpause(self):
		pyglet.clock.schedule(self.upd_callback)

	# Приостанавливает обновление сущностей
	def pause(self):
		pyglet.clock.unschedule(self.upd_callback)

	# Обновить все сущности
	def update(self,dt):
		self.time += dt
		for ent in self.entities:
			ent.update(dt)

	# Добавление сущности в игру
	def addEntity(self,entity):
		self.entities.append(entity)
		entity.game = self
		entity.spawn( )
		if entity.id != None:
			self.indexed_entities[entity.id] = entity

	# Нарисовать все объекты
	def draw_all(self):
		self.sprite_batch.draw( )
		for ent in self.custom_draw_entities:
			ent.draw( )

# Класс описывающий пространство игрового мира.
# Перегрузив, можно получить неевклидово пространство
# Например, зацикленное по одной из осей...
class EuclidianWorldSpace:
	def __init__(self):
		pass
	# Единственный метод - преобразование координат точки
	# для зацикленных пространств - что-то надо брать по модулю.
	def translate_point(self,x,y):
		return x,y

# Класс, описывающий пространство отображения игрового мира.
# Можно изменить для отображения зацикленного пространства
# так, чтобы горизонтальные линии отображались в концентричесские
# окружностти или n-угольники а-ля super-hexogon
class EuclidianViewSpace:
	def __init__(self):
		pass
	# Изменяет трансформацию визуального объекта (спрайта)
	# в соответствии с заданными параметрами игрового объекта
	# и свойствами  пространства
	def transform_object(self,vobject,x,y,rotation=0,scale=1):
		vobject.x = x
		vobject.y = y
		vobject.rotation = rotation
		vobject.scale = scale
	# Отображает вектор (x,y) начинающийся в точке (px,py)
	# из координат игрового мира в координаты видимого пространства.
	# Полезно, например, если нужно (зачем-то) нарисовать вектор
	# скорости (x,y) объекта центр которого расположен в (px,py).
	def translate_vector(self,px,py,x,y):
		return x, y

# Класс игровой сущности
# Игрок, ящик, червестраус и т.д.
class GameEntity:
	#
	def __init__(self):
		# Ссылка на объект игры
		self.game = None

		# Положение, трансфотмации ..
		self.x = 0
		self.y = 0
		self.rotation = 0.0
		self.scale = 1

		# Спрайт
		self.sprite = None

		# Уникальный идентификатор. Можно установить
		# в конструкторе или в spawn()
		self.id = None

	# Стоит вызывать каждый раз, когда меняюрся x, y, scale или rotation.
	def end_update_coordinates(self):
		self.x,self.y = self.game.world_space.translate_point(self.x,self.y)
		if self.sprite != None:
			self.game.view_space.transform_object(self.sprite,self.x,self.y,self.rotation,self.scale)

	# Вызывается при добавлении сущности в игру
	def spawn(self):
		pass

	# Вызывается в каждом кадре игры
	def update(self,dt):
		pass

# Простая сущность, рисуемая как спрайт
# без анимации
class SpriteGameEntity(GameEntity):
	def __init__(self,sprite_name='rc/64x64fg.png'):
		GameEntity.__init__(self)

		self.image_name = sprite_name

	def spawn(self):
		GameEntity.spawn(self)
		self.texture = LoadTexture(self.image_name,anchor='center')
		self.sprite = self.game.newSprite(self.texture)

	def update(self,dt):
		self.rotation += dt * 10
		self.end_update_coordinates( )

# Набор анимаций для класса сущностей c анимацией
class AnimationList:
	# Описание анимации в таком виде:
	# desc = {'IDLE':[{'img':'rc/i/a1_0.png','t':1},{'img':'rc/i/a1_1.png','t':1}],
	# 		'WALK':[{'img':'rc/i/a2.png','t':0.5,'rect':[0,0,64,64]},
	# 			{'img':'rc/i/a2.png','t':0.5,'rect':[64,0,64,64]}]}
	# т.е.
	# описание ::= {'назавние':[спиоок_кадров]}
	# кадр ::= {'img':'путь_к_текстуре','t':продолжительность,'rect':фрагмент_текстуры}
	# фрагмент_текстуры ::= [x,y,ширина,высота]
	def __init__(self,description):
		self.animations = {}
		self.description = description
		self.initialized = False
		self.default_anim = None

	#
	def init(self):
		if self.initialized:
			return
		self.initialized = True
		for name,framedescs in self.description.items():
			frames = []
			for framedesc in framedescs:
				texture = LoadTexture(framedesc['img'])
				if 'rect' in framedesc:
					texture = texture.get_region(*(framedesc['rect'])).get_texture( )
				if 'anchor' in framedesc:
					ApplyTextureAnchor(texture,framedesc['anchor'])
				time = framedesc.get('t',None)
				frames.append(pyglet.image.AnimationFrame(texture,time))
			anim = pyglet.image.Animation(frames)
			self.animations[name] = anim
			if self.default_anim == None:
				self.default_anim = anim

	#
	def get(self,name):
		if name in self.animations:
			return self.animations[name]
		else:
			GAME_CONSOLE.write('Cannot find animation "',name,'" in list ',self.description)
			return self.default_anim

# Класс сущности, рисуемой как спрайт
# с анимацией
class AnimatedGameEntity(GameEntity):
	def __init__(self,animlist):
		GameEntity.__init__(self)

		self.animlist = animlist
		self.animlist.init( )

	# Переключится к другой анимации.
	def set_animation(self,name):
		if self.sprite != None:
			self.sprite.image = self.animlist.get(name)

	def spawn(self):
		self.sprite = self.game.newSprite(self.animlist.default_anim)



# Камера - определяет, как мы видим мир.
class Camera:
	def __init__(self):
		# Точка, которая окажется в центре экрана
		self.focus_x = 0
		self.focus_y = 0

		# Размеры экрана
		self.width = 1
		self.height = 1

		# Масштабирование изображения
		# по осям и целиком
		self.scale_x = 1
		self.scale_y = 1
		self.scale = 1

		# Поворот изображения
		self.rotation = 0	# В градусах!

	#
	def set_focus(self,x,y):
		self.focus_x = x
		self.focus_y = y

	#
	def set_size(self,width,height):
		self.width = width
		self.height = height

	# Применить изменения к матрице трансформации OpenGL
	def apply_transform(self):
		# Из-за особенностей OpenGL преобразования
		# применяются в обратном порядке

		# 4 - переместить (0,0) в (width/2,height/2)
		glTranslatef(self.width / 2,self.height / 2,0)

		# 3 - поворот вокруг (0,0)
		glRotatef(self.rotation,0,0,1)

		# 2 - масштабирование относительно (0,0)
		glScalef(self.scale_x * self.scale,self.scale_y * self.scale,1)

		# 1 - переместить (focus_x,focus_y) в (0,0)
		glTranslatef(-self.focus_x,-self.focus_y,0)

