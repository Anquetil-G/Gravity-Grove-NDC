import pyxel
import math

TRANSPARENT_COLOR = 5
TILE_COLLISION_WALL = [(1, 3), (0, 1), (1, 1), (2, 1), (3, 1), (1, 2)]
TILE_COLLISION_FLOOR = [(0, 1), (1, 1), (2, 1), (3, 1), (1, 3), (1, 2)]
TILE_COLLISION_DEATH = [(4, 11), (5, 14)]



def handleCollision(x, y, in_jump):
  tile_x = math.floor(x) // 8
  tile_y = math.floor(y) // 8
  tile_x2 = (math.ceil(x) + 6) // 8
  tile_y2 = (math.ceil(y) + 7) // 8

  for xi in range(tile_x, tile_x2 + 1):
    for yi in range(tile_y, tile_y2 + 1):
      for i in TILE_COLLISION_WALL:
          if pyxel.tilemaps[0].pget(xi, yi) == i:
            return True
      for i in TILE_COLLISION_DEATH:
          if pyxel.tilemaps[0].pget(xi, yi) == i:
            return "death"
        
  if in_jump and y % 16 == 1:
    for xi in range(tile_x, tile_x2 + 1):
        for i in TILE_COLLISION_FLOOR:
          if pyxel.tilemaps[0].pget(xi, tile_y+1) == i:
            return True

  return False


def handleMove(distance_x, x, distance_y, y, in_jump):
  step = 0
  death = False

  for i in range(pyxel.ceil(abs(distance_x))):
    if distance_x > 0:
        step = 1
    elif distance_x < 0:
        step = -1
    else:
        step = 0
    if handleCollision(x + step, y, distance_y > 0) == "death":
      death = True
      break
    elif handleCollision(x + step, y, distance_y > 0):
       break
    x += step
    distance_x -= step

  for i in range(pyxel.ceil(abs(distance_y))):
    if distance_y > 0:
        step = 1
    elif distance_y < 0:
        step = -1
    else:
        step = 0
    if handleCollision(x, y + step, distance_y > 0) == "death":
      death = True
      break
    elif handleCollision(x, y + step, distance_y > 0):
      break
    y += step
    distance_y -= step
  
  return x, y, death


class Player:
  def __init__(self):
    self.width = 8
    self.height = 8
    self.x = 10
    self.y = 100
    self.distance_x = 0
    self.distance_y = 0
    self.direction = 1
    self.walk_position = 0
    self.in_walk = False
    self.speed = 1
    self.in_jump = False
    self.gravity = 1
    self.dash = 0
    self.cooldown_dash = 0
    self.cooldown_gravity = 0
    self.cooldown_death = 0
    self.death = False

  def update(self):
    if self.death:
      self.cooldown_death += 120
      self.x = 10
      self.y = 100
      self.distance_x = 0
      self.distance_y = 0
      self.direction = 1
      self.walk_position = 0
      self.in_walk = False
      self.in_jump = False
      self.gravity = 1
      self.dash = 0
      self.cooldown_dash = 0
      self.cooldown_gravity = 0
      self.cooldown_death = 0
      if self.cooldown_death == 0:
        self.death = False

    self.in_walk = False
    if pyxel.btn(pyxel.KEY_LEFT):
      self.distance_x = -self.speed
      self.direction = -1
      self.in_walk = True
    if pyxel.btn(pyxel.KEY_RIGHT):
      self.distance_x = self.speed
      self.direction = 1
      self.in_walk = True
    if pyxel.btnp(pyxel.KEY_SPACE):
      if not self.in_jump:
        self.distance_y = -3.3*self.gravity
        pyxel.play(0, 9, False)
    if pyxel.btnp(pyxel.KEY_F):
      if self.cooldown_gravity == 0:
        self.gravity *= -1
        self.cooldown_gravity = 60
        pyxel.play(0, 10, False)
    if pyxel.btnp(pyxel.KEY_E):
      if self.cooldown_dash == 0:
        self.dash += 25
        self.cooldown_dash = 120
        pyxel.play(0, 11, False)

    if self.dash > 0:
      if self.direction == 1:
        self.distance_x = 7
      if self.direction == -1:
        self.distance_x = -7

    self.dash = max(self.dash-4, 0)
    self.cooldown_dash = max(self.cooldown_dash-1, 0)
    self.cooldown_gravity = max(self.cooldown_gravity-1, 0)
    # self.cooldown_death = max(self.cooldown_death-1, 0)


    # if self.gravity > 0:
    tile_x = (math.floor(self.x)) // 8
    tile_y = (math.floor(self.y)) // 8
    tile_x2 = (math.ceil(self.x) + 6) // 8
    # else:
    #   tile_x = math.ceil(self.x) // 8
    #   tile_y = math.ceil(self.y) // 8
    #   tile_x2 = (math.floor(self.x) - 12) // 8
    for xi in range(tile_x, tile_x2 + 1):
      for i in TILE_COLLISION_FLOOR:
        if pyxel.tilemaps[0].pget(xi, tile_y+1) == i:
          if self.gravity > 0:
            self.in_jump = False
          else:
            self.in_jump = True
        else:
          if self.gravity > 0:
            self.in_jump = True
          else:
            self.in_jump = False


    self.x, self.y, self.death = handleMove(self.distance_x, self.x, self.distance_y, self.y, self.in_jump)

    self.distance_x = 0
    if self.gravity > 0:
      self.distance_y = min(self.distance_y + 0.4, 2.35)
    else:
      self.distance_y = max(self.distance_y - 0.4, -2.35)

    if self.in_jump:
      self.walk_position = 3
    elif self.in_walk:
      self.walk_position = 1
      if pyxel.frame_count % 12 > 6:
        self.walk_position = 2
    else: 
      self.walk_position = 0


  def draw(self):
    if self.walk_position == 0:
      pyxel.blt(self.x, self.y, 0, 0, 72, self.width*self.direction, self.height*self.gravity, TRANSPARENT_COLOR)
    if self.walk_position == 1:
      pyxel.blt(self.x, self.y, 0, 8, 72, self.width*self.direction, self.height*self.gravity, TRANSPARENT_COLOR)
    if self.walk_position == 2:
      pyxel.blt(self.x, self.y, 0, 24, 72, self.width*self.direction, self.height*self.gravity, TRANSPARENT_COLOR)
    if self.walk_position == 3:
      pyxel.blt(self.x, self.y, 0, 32, 72, self.width*self.direction, self.height*self.gravity, TRANSPARENT_COLOR)


class App:
  def __init__(self):
    pyxel.init(128, 128, title="Gravity Grove", quit_key=pyxel.KEY_ESCAPE, fps=60)
    pyxel.load('./1.pyxres')
    # pyxel.mouse(True)
    self.player = Player()
    pyxel.playm(0, 0, True)
    pyxel.run(self.update, self.draw)
    

  def update(self):
    self.player.update()

  def draw(self):
    pyxel.cls(5)

    if self.player.x >= 128-64:
      pyxel.camera()
      pyxel.bltm(0, 0, 0, self.player.x -(128-64), self.player.y - 75, 128, 128, TRANSPARENT_COLOR)
      pyxel.camera(self.player.x -(128-64), self.player.y - 75)
    else:
      pyxel.camera()
      pyxel.bltm(0, 0, 0, 0, self.player.y - 75, 128, 128, TRANSPARENT_COLOR)
      pyxel.camera(0 , self.player.y - 75)

    self.player.draw()
    if self.player.death:
      pyxel.text(self.player.x - 15, self.player.y - 20, "Game Over!", 0)
  

App()