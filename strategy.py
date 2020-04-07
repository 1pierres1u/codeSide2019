import model
import random
import heapq
import math
import sys
import numpy as np
import json
np.set_printoptions(threshold=sys.maxsize)


class Line:
    def __init__(self,a,b):
        self.a = a
        self.b = b

    def img(self,x):
        return self.a*x + self.b

    def slope(self):
        return self.a

    def length(self,p,q):
        dx = (p.x - q.x)**2
        dy = (p.y - q.y)**2
        return math.sqrt(dx + dy)

    def intercept(self,aLine):
        db = self.b - aLine.b
        da = aLine.a - self.a
        if db==0 and da==0:
            return aLine
        elif db ==0:
            return Point(0,self.b)
        elif da==0:
            return None
        else:
            return Point(db/da, self.img(db/da))

    def find_eq(self,p,q):
        if q.x != p.x:
            self.a = (p.y-q.y)/(p.x-q.x)
            self.b = p.y - self.a*p.x

    def dist_to(self,p):
        x = p.x
        y = self.img(x)
        num = abs(y - self.a*x -self.b)
        den = math.sqrt(self.a**2+self.b**2)
        return num/den
    
    def further_from(self,L):
        j=0
        ma=-1
        p=None
        for i in range(len(L)):
            pi = model.Vec2Double(L[i][0],L[i][1])
            d = self.dist_to(pi)
            if d > ma:
                j = i
                p = L[j]
                ma = d
        return (p,j)


class Sparta:
    def __init__(self):
        self.eye = Eyes()
        self.control = Control()
        #
        self.unit = None
        self.game = None
        self.debug = None
        #
        self.dist=5
        self.step=0.5
        #
        self.map=None
        #
        self.state =[
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0],
                [0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0]
                ]
        self.index=0
        #
        self.i_avoid=0



    
    ###################################################
    #01/01/2020
    def condition_interpreter(self,v):
        if v == 'p100':
            return self.should_get_pack_100()
        elif v == "ples":
            return self.should_get_pack_less()
        


    def should_get_pack_100(self):
        pa = self.eye.search_pack(None,None,None)
        if self.unit.health != 100 and len(pa) !=0:
            return pa[0].position
        else:
            return None

    def should_get_pack_less(self):
        pa = self.eye.search_pack(None,None,None)
        u = self.unit.health
        v = self.eye.search_enemy(None,None,None)[0].health
        if (u < v) and len(pa) !=0:
            return pa[0].position
        else:
            return None


    def should_avoid_bullet(self):
       u = self.unit
       L = self.eye.search_bullet(10,u)
       if len(L) != 0:
           #build line
           aL = Line(1,2)
           p1 = L[0]
           p1x = p1.position.x
           p1y = p1.position.y
           p1vx = p1.velocity.x
           p1vy = p1.velocity.y
           p2 = model.Vec2Double(p1x + p1x*p1vx*0.1,p1y + p1y*p1vy*0.1)
           aL.find_eq(p1.position,p2)
           return aL
       else:
           return None


    ###################################################
    #01/01-02/2020
    def distance_interpreter(self,v):
        if v == '15':
            return self.distance_15()
        elif v == '13' :
            return self.distance_13()
        elif v == '11' :
            return self.distance_11()
        elif v == '9' :
            return self.distance_9()
        elif v == '7' :
            return self.distance_7()
        elif v == '5' :
            return self.distance_5()
        elif v == 'rand':
            return self.distance_rand()
        elif v == 'tick':
            return self.distance_tick()
        elif v == 'tick1':
            return self.distance_tick_1()
        elif v == 'life_ratio':
            return self.distance_life_ratio()
        elif v == 'bullet':
            return self.distance_bullet()
        elif v == 'gun':
            return self.distance_gun()

    def distance_15(self):
        return 15

    def distance_13(self):
        return 13

    def distance_11(self):
        return 11

    def distance_9(self):
        return 9

    def distance_7(self):
        return 7

    def distance_5(self):
        return 5
    
    def distance_rand(self):
        return random.randint(5,9)

    def distance_tick(self):
        t = self.game.current_tick
        if t >= 2000:
            return 9
        elif 1000 <= t and t < 2000:
            return 7
        elif 0 <= t and t < 1000:
            return 5

    def distance_tick_1(self):
        t = self.game.current_tick
        if t >= 2000:
            return 7
        elif 1000 <= t and t < 2000:
            return 9
        elif 0 <= t and t < 1000:
            return 11
    
    def distance_life_ratio(self):
        u = self.unit.health
        e = self.eye.search_enemy(None,None,None)[0].health
        if u==e :
            return 9
        elif u/e  <= 0.5 :
            return 13
        elif u/e <= 1:
            return 11
        elif u/e >= 1.5:
            return 7
        elif u/e > 1:
            return 5
    
    def distance_bullet(self):
        i = (self.index-1)%2
        n = self.state[i][5]
        if n > 0:
            return 9
        else:
            return 5
    
    def distance_gun(self):
        e = self.eye.search_enemy(None,None,None)[0]
        if e.weapon is None:
            return 5
        elif e.weapon.typ == 0: #pistol
            return 7
        elif e.weapon.typ == 1: #riffle
            return 9
        elif e.weapon.typ == 2: #rocket
            return 11
        
   

    ###################################################
    #12/29/2019

    def get_pack(self):
        if len(self.eye.search_pack(None,None,None))!=0:
            p = self.eye.find_pack(0,2)[1]
            return p
        else:
            return None
    

    ###################################################
    #12/28/2019
    def observe(self):
        o = self.index
        #values for this tick
        self.state[o][1] = self.unit.health
        if self.unit.weapon is not None:
            self.state[o][2] = self.unit.weapon.typ+1 
            self.state[o][3] = self.unit.weapon.magazine+1
            if self.unit.weapon.fire_timer is None:
                self.state[o][4] = 1
            else:
                self.state[o][4] = self.unit.weapon.fire_timer
        q = self.eye.search_enemy(None,None,None)[0]
        self.state[o][5] = len(self.eye.find_bullet(q.position,16.4,q.player_id))
        
        self.state[o][8] = q.health
        if q.weapon is not None:
            self.state[o][9] = q.weapon.typ+1 
            self.state[o][10] = q.weapon.magazine+1
            if q.weapon.fire_timer is None:
                self.state[o][11] = 1
            else:
                self.state[o][11] = q.weapon.fire_timer
       #variation of values observed
        r = (o+1)%2
        for j in range(16):
           self.state[2][j]=self.state[o][j] - self.state[r][j]
        #move index 
        self.index = r

    
    ###################################################

    def update(self,unit,game,debug):
        self.unit = unit
        self.game = game 
        self.debug = debug 
        #
        self.control.update(unit,game,debug)
        self.control.update_id()
        self.eye.update(unit,game,debug)
        self.observe()


    def brain(self,unit,game,debug,param):
        #update 
        self.update(unit,game,debug)
        #
        if len(self.control.get_active_stack("action"))!=0:
            return self.control.interpreter()
        #setup the environment
        co = Coordination()
        co.update(unit,game,debug)
        co.set_2d_field(self.unit.position,8)
        #get a gun 
        p=self.get_gun()
        if p is not None:
            self.control.append(("XY",p,"N",None))
            return self.control.interpreter()
        #get health pack
        p = self.condition_interpreter(param["pack"])
        if p is not None:
            self.control.append(("XY",p,"N",None))
            return self.control.interpreter()
        #find enemy
        u = self.unit.position
        e = self.eye.find_enemy(0,2)
        #
        co1 = Coordination()
        co1.update(unit,game,debug)
        #parameters
        di = param["distance"]
        kata = param["kata"]
        di = self.distance_interpreter(di)
        #
        if e[0] < di:
            co1.center = e[1]
            self.dist = di 
            e  = self.keep_distance(e[1])
            e = co1.avoidance_points_proxy(kata,e,self.i_avoid)
            #detect bullet
            w = self.should_avoid_bullet()
            if w is not None:
                e  = w.further_from(co1.avoidance_points)
                e = e[0]
            e = model.Vec2Double(e[0],e[1])
            self.i_avoid+=1
            self.i_avoid%=len(co1.avoidance_points)
            self.control.append(("DI",e,"T",3))
            return self.control.interpreter()
        else:
            e=e[1]
            self.control.append(("XY",e,"N",None))
            return self.control.interpreter()


    def get_gun(self):
        if self.unit.weapon == None:
            p = self.eye.find_gun(0,2)[1]
            return p
        else:
            return None

    def get_health_pack(self):
        p = self.eye.search_pack(None,None,None)
        e = self.eye.search_enemy(None,None,None)[0]
        c = (self.unit.health != 100)
        c1=True 
        c2=True
        if len(p)!=0:
            c1 = p[0].position.x >= self.unit.position.x and self.unit.position.x >= e.position.x
            c2 = p[0].position.x <= self.unit.position.x and self.unit.position.x <= e.position.x
        if (c1 or c2) and c and len(p) !=0:
            return p[0].position
        else:
            return None


    def keep_distance(self,p):
        q = self.unit.position
        tw = self.eye.toward(p,q)
        ######
        d = p.x - q.x  #0  20 
        if d==0:
            d=1
        d1 =abs(d)/d
        if d==0:
           d1 = 0
        elif abs(d)>self.dist:
             #decrease distance
             if abs(d) > self.step: #mininum step
                 d1 = d1*self.step
             else:
                 d1 = d1*abs(d)
        elif abs(d) < self.dist:
             #increase distance
             if abs(d) > self.step:  #minimum step
                 d1 = -d1*self.step
             else :
                 d1 = -d1*abs(d)
        else:
            d1 = abs(d) - self.dist  #3 -20
            if d1 !=0:
                d1 = abs(d1)/d1
        ####
        w = q.x + d1
        #always stay on the field
        if w < 0.2:
            w =0.2
        elif w > 38:
            w = 38
        if d1 ==0:
            d1 = 1
        where = self.eye.find_tile_valid(w,abs(d1)/d1)
        return where

class Eyes:
    def __init__(self):
        self.unit = None
        self.game = None
        self.debug = None
        #
        self.map = None

    #################################################################
    #########12/28/2019
    def find_enemy(self,which,where):
        e = self.search_enemy(None,None,None)[which].position
        u = self.unit.position 
        f = (int(e.x),int(e.y))
        v = (int(u.x),int(u.y))
        path = self.astar(self.map,v,f)
        l = len(path)
        if where < l :
            x = path[l-where]
            w = model.Vec2Double(x[0],x[1])
            return [l,w,e]
        elif l == 1:
            x = path[0]
            w = model.Vec2Double(x[0],x[1])
            return [l,w,e]
        else:
            return [l,e,e] 
        

    def find_pack(self,which,where):
        e = self.search_pack(None,None,None)
        if len(e)==0:
            return None
        e = e[which].position
        u = self.unit.position 
        f = (int(e.x),int(e.y))
        v = (int(u.x),int(u.y))
        path = self.astar(self.map,v,f)
        l = len(path)
        if where < l :
            x = path[l-where]
            w = model.Vec2Double(x[0],x[1])
            return [l,w,e]
        elif l == 1:
            x = path[0]
            w = model.Vec2Double(x[0],x[1])
            return [l,w,e]
        else:
            return [l,e,e] 

    def find_gun(self,which,where):
        e = self.search_gun(None,None,None)
        if len(e)==0:
            return None
        e = e[which].position
        u = self.unit.position 
        f = (int(e.x),int(e.y))
        v = (int(u.x),int(u.y))
        path = self.astar(self.map,v,f)
        l = len(path)
        if where < l :
            x = path[l-where]
            w = model.Vec2Double(x[0],x[1])
            return [l,w,e]
        elif l == 1:
            x = path[0]
            w = model.Vec2Double(x[0],x[1])
            return [l,w,e]
        else:
            return [l,e,e] 

    def find_mine(self,which,where):
        e = self.search_mine(None,None,None)
        if len(e)==0:
            return None
        e = e[which].position
        u = self.unit.position 
        f = (int(e.x),int(e.y))
        v = (int(u.x),int(u.y))
        path = self.astar(self.map,v,f)
        l = len(path)
        if where < l :
            x = path[l-where]
            w = model.Vec2Double(x[0],x[1])
            return [l,w,e]
        elif l == 1:
            x = path[0]
            w = model.Vec2Double(x[0],x[1])
            return [l,w,e]
        else:
            return [l,e,e] 

    def closest_valid_neighbor(self,p,step):
        n = 2
        L = []
        row = len(self.game.level.tiles)
        col = len(self.game.level.tiles[0])
        for i in range(2*n):
            for j in range(2*n):
                q = model.Vec2Double(p.x+(-n+i)*step, p.y+(-n-j)*step) 
                cond = (0 <= q.x and q.x<=row) and ( 0 <= q.y and q.y <= col) and self.reachable(p,q)  
                if cond:
                    cond = self.game.level.tiles[int(q.x)][int(q.y)] != model.Tile.WALL 
                    cond = cond and self.game.level.tiles[int(q.x)][int(q.y)] != model.Tile.JUMP_PAD
                    if cond:
                        L.append(q)
        return L[0]    


    def heuristic(self,a,b):
        return math.sqrt((b[0]-a[0])**2 + (b[1]-a[1])**2)

    def astar(self,array,start,goal):
        neighbors=[(1,0),(0,-1),(0,1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]

        close_set = set()
        came_from = {}
        gscore = {start:0}
        fscore = {start:self.heuristic(start,goal)}
        oheap=[]
        heapq.heappush(oheap,(fscore[start],start))

        while oheap:
            current = heapq.heappop(oheap)[1]
            if current == goal:
                data =[]
                while current in came_from:
                    data.append(current)
                    current = came_from[current]
                return data
            close_set.add(current)
            for i,j in neighbors:
                neighbor = current[0]+i,current[1]+j
                tentative_g_score = gscore[current] + self.heuristic(current,neighbor)
                if 0 <= neighbor[0] < array.shape[0]:
                    if 0 <= neighbor[1] < array.shape[1]:
                        if array[neighbor[0]][neighbor[1]] ==1:
                            continue
                    else:
                        continue
                else:
                    continue
                if neighbor in close_set and tentative_g_score >= gscore.get(neighbor,0):
                    continue
                if tentative_g_score < gscore.get(neighbor,0) or neighbor not in [i[1]for i in oheap]:
                    came_from[neighbor] = current
                    gscore[neighbor] = tentative_g_score
                    fscore[neighbor] = tentative_g_score + self.heuristic(neighbor,goal)
                    heapq.heappush(oheap,(fscore[neighbor],neighbor))
    

    def load_map(self):
        if self.map is not None:
            return
        row = len(self.game.level.tiles)
        col = len(self.game.level.tiles[0])
        self.map = [[0]*col]*row
        self.map = np.array(self.map)
        for i in range(row):
            for j in range(col):
                if self.game.level.tiles[i][j] == model.Tile.WALL:
                    self.map[i][j] = 1

    def reachable(self,p,q):
       L = Line(1,2)
       L.find_eq(p,q)
       x1 = p.x
       x2 = q.x 
       ma = 0
       mi = 0
       d = 0.1
       if x1 > x2:
           ma = x1
           mi = x2
       else:
           ma = x2
           mi = x1
       while mi < ma:
           if self.game.level.tiles[int(mi)][int(L.img(mi))] == model.Tile.WALL:
               return False
           mi += d
       return True

    #####################################################################

    def update(self,unit,game,debug):
        self.unit = unit
        self.game = game
        self.debug = debug
        #
        self.load_map()

  ##################################
  ## LIST 
    ##GUNS 
    def gun_list(self):
          L=[]
          for i in self.game.loot_boxes:
              if isinstance(i.item,model.Item.Weapon):
                  L.append(i)
          return L

    def gun_type(typ):
        L=self.gun_list()
        S=[]
        for i in L:
            if i.typ == typ:
                S.append(i)
        return S
    ##

    ## HEALTH PACK
    def pack_list(self):
          L=[]
          for i in self.game.loot_boxes:
              if isinstance(i.item,model.Item.HealthPack):
                  L.append(i)
          return L
    ##

    ##MINES
    def mine_list(self):
          L=[]
          for i in self.game.loot_boxes:
              if isinstance(i.item,model.Item.Mine):
                  L.append(i)
          return L
 
    def mine_type(typ):
        L = self.mine_list()
        S =[]
        for i in L:
            if i.state == typ:
                S.append(i)
        return S
    ##

    def point_list(self):
         pass
 
    def enemy_list(self):
         L=[]
         for i in self.game.units:
             if i.player_id != self.unit.player_id:
                 L.append(i)
         return L
 
    def unit_list(self):
         L=[]
         for i in self.game.units:
             if i.player_id == self.unit.player_id:
                 L.append(i)
         return L

  ########################################
  # distance 
    def distance_sqr(self,a, b):
            return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

    def x_distance_sqr(self,a, b):
            return (a.x - b.x) ** 2

    def y_distance_sqr(self,a, b):
            return (a.y - b.y) ** 2

    def sort_distance(self,q):
        p1 = self.unit.position
        q1 = q.position
        return self.distance_sqr(p1,q1)
    
   
   ######################################
   # position 
    
    #i behind p
    def behind(L,p):
        L =[]
        for i in L:
            if i.x < p.x:
                L.append(i)
        return L

    #i in front p
    def in_front(L,p):
        L =[]
        for i in L:
            if i.x >= p.x:
                L.append(i)
        return L

    #i above p
    def above(L,p):
        L =[]
        for i in L:
            if i.y < p.y:
                L.append(i)
        return L

    #i below p
    def below(L,p):
        L =[]
        for i in L:
            if i.y >= p.y:
                L.append(i)
        return L

   ######################################
   # time

    def tick_left(self):
       return 3600 - self.game.current_tick

      
   ######################################
   # SEARCH
    def search_points(self,p,typ,horizontal,vertical):
        pass
    def search_points_me(self,horizontal,vertical):
        pass
    def search_pack(self,p,horizontal,vertical):
        L = self.pack_list()
        L.sort(key=self.sort_distance)
        return L
    def search_gun(self,p,horizontal,vertical): 
        L = self.gun_list()
        L.sort(key=self.sort_distance)
        return L
    def search_mine(self,p,horizontal,vertical):
        L = self.mine_list()
        L.sort(key=self.sort_distance)
        pass
    def search_enemy(self,d,horizontal,vertical):
        L = self.enemy_list()
        L.sort(key=self.sort_distance)
        
        Q=[]
        if d is not None:
            for i in L:
                if self.sort_distance(i)<d:
                    Q.append(i)
            return Q

        return L
    def search_unit(self,p,horizontal,vertical):
        L = self.unit_list()
        L.sort(key=self.sort_distance)
        return L
    def search_bullet(self,d,p):
        L =[]
        for i in self.game.bullets:
            if self.sort_distance(i) < d and i.player_id !=p:
                L.append(i)
        return L
   
    
   ####################################
   ## 01-02-2020
    def find_bullet(self,u,d,p):
        L = []
        for i in self.game.bullets:
            if self.distance_sqr(u,i.position) < d and i.player_id==p:
                L.append(i)
        return L

   ####################################
    def toward(self,p,q):
        d = p.x - q.x
        if d==0:
            d = 1
        else:
            d = abs(d)/d
        return d
   
    def valid(self,i):
        ii = i-1
        if ii < 0.8:
            ii=0.8
        p = self.find_tile(ii,0)
        if p is None:
            p = model.Vec2Double(int(self.unit.position.x),int(self.unit.position.y))
        ii = i+1
        if ii>36:
            ii=36
        q = self.find_tile(ii,0)
        if q is None:
            q = model.Vec2Double(int(self.unit.position.x),int(self.unit.position.y))
        if self.game.level.tiles[int(i)][p.y-1] != model.Tile.JUMP_PAD and (p.y==q.y):
            return [True,model.Vec2Double(i,p.y)]
        else:
            return [False,None]

    def find_tile_valid(self,i,d):
        while True:
          x = self.valid(i)
          if not x[0]:
            i+=d
            x = self.valid(i)
          else:
              break
        return x[1]

    def find_tile(self,i,typ):
        j=0
        n = len(self.game.level.tiles[int(i)])
        t = None
        if typ==0:
            while j < n:
                if self.game.level.tiles[int(i)][j] != 0:
                    break
                j+=1
            while j < n:
                if self.game.level.tiles[int(i)][j]==0:
                   t = model.Vec2Double(i,j+2)
                   break
                j+=1
        return t
   ####################################
   ####################################
   ####################################
    def canMoveForward(self,w,unit,game):
        a = None
        if(unit.position.x <= w.x):
            a = game.level.tiles[int(unit.position.x)+1][int(unit.position.y)]
        else:
            a = game.level.tiles[int(unit.position.x)-1][int(unit.position.y)]
        if a == model.Tile.WALL or a == model.Tile.JUMP_PAD:
            return False
        else:
            return True

class Duration:
    def __init__(self):
        self.count = False
        self.saved_time = None

    def ticksPassed(self,x,game):
        if game.current_tick - self.saved_time > x:
            return True
        else:
            return False

    def saveTime(self,game):
        self.saved_time = game.current_tick
        self.count = True

    def wait(self,x,game):
        if self.count == False:
            self.count = True
            self.saved_time = game.current_tick
        elif not self.ticksPassed(x,game):
           return True 
        else:
            return False

class Control:
    def __init__(self):
        self.shoot = Shoot()
        self.eye = Eyes()
        #
        self.actions_stack=[]
        self.actions_stack_1=[]
        self.avoid_stack=[]
        self.avoid_stack_1=[]
        #
        self.who=-1
        self.which_stack=0
        #
        self.active_stack=1
        self.active_stack_1=1
        #
        self.xclose = 0.30
        self.yclose = 0.20
        self.close = 0.01
        self.aclose =0.0001
        self.bclose =1
        #
        self.time_control=-1
        self.plant=False
        self.swap=False
        self.reload=False
        self.speed = 90
        #
        self.unit=None
        self.game=None
        self.debug=None
        #
        self.unit_id=-1
        #
        self.dist=5
        self.step=0.9
        #
        self.tick_counter=-1

    ##########################################
    ## 12/30/2019

    def should_push_back(self,p):
        if p[2] == "N":
            self.tick_counter=-1
            return
        elif p[2] == "T":
            dt = self.game.current_tick - self.tick_counter
            if dt > p[3]:
                self.tick_counter = -1
                return
            else:
                #print("more ticks to go",self.tick_counter,self.game.current_tick)
                #print("where",p[1])
                #print("me",self.unit.position)
                self.append(p)
        
    ##########################################
    def keep_distance(self,p,q):
        d = p.x - q.x  #0  20 
        d1 =abs(d)/d
        if d==0:
           return 0
        elif abs(d)>self.dist:
             #decrease distance
             if abs(d) > self.step: #mininum step
                 return d1*self.step
             else:
                 return d1*abs(d)
        elif abs(d) < self.dist:
             #increase distance
             if abs(d) > self.step:  #minimum step
                 return -d1*self.step
             else :
                 return -d1*abs(d)

       
        d1 = abs(d) - self.dist  #3 -20
        if d1 !=0:
           d1 = abs(d1)/d1
        return d1


    def switch_stack(self):
        if self.unit.id == self.unit_id:
            if self.active_stack_1==0:
                self.active_stack_1=1
            else:
                self.active_stack_1 =0
        else:
            if self.active_stack ==0:
                self.active_stack=1
            else:
                self.active_stack=0


    def update_id(self):
         if self.unit_id==-1:
             self.unit_id = self.unit.id
         

    def appendc(self,p,which):
         if self.unit.id == self.unit_id:
             if which == "action":
                 self.actions_stack_1.append(p)
             else:
                 self.avoid_stack_1.append(p)
         else:
             if which =="action":
                 self.actions_stack.append(p)
             else:
                 self.avoid_stack.append(p)
        

    def popc(self,which):
         if self.unit.id == self.unit_id:
             if which=="action":
                 return self.actions_stack_1.pop(p)
             else:
                 return self.avoid_stack_1.pop(p)
         else:
             if which=="action":
                 return self.actions_stack.pop(p)
             else:
                 return self.avoid_stack.pop(p)

    def append(self,p):
         if self.tick_counter == -1:
            self.tick_counter = self.game.current_tick
         if self.unit.id == self.unit_id:
             if self.active_stack_1==1:
                 self.actions_stack_1.append(p)
             else:
                 self.avoid_stack_1.append(p)
         else:
             if self.active_stack ==1:
                 self.actions_stack.append(p)
             else:
                 self.avoid_stack.append(p)
        

    def pop(self):
         if self.unit.id == self.unit_id:
             if self.active_stack_1==1:
                 return self.actions_stack_1.pop()
             else:
                 return self.avoid_stack_1.pop()
         else:
             if self.active_stack ==1:
                 return self.actions_stack.pop()
             else:
                 return self.avoid_stack.pop()
    
    def get_active_stack(self,which):
         if self.unit.id == self.unit_id:
             if which == "action":
                 return self.actions_stack_1
             else:
                 return self.avoid_stack_1
         else:
             if which=="action":
                 return self.actions_stack
             else:
                 return self.avoid_stack
    
    def num_active_stack(self):
        if self.unit.id == self.unit_id:
            return self.active_stack_1
        else:
            return self.active_stack
        
    ##################################################
    def update(self,unit,game,debug):
        self.unit = unit 
        self.game = game
        self.debug = debug
        self.shoot.update(unit,game,debug)
        self.eye.update(unit,game,debug)
    
    def which_unit(self):
        if self.who == -1:
            self.who = self.unit.id
        if self.unit.id == self.who:
            self.which_stack = 0
        else:
            self.which_stack = 1
        

    def distance_sqr(self,a,b):
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

    def x_distance_sqr(self,a,b):
        return (a.x - b.x) ** 2 

    def y_distance_sqr(self,a,b):
        return  (a.y - b.y) ** 2

                    
    def do_nothing(self):
           self.shoot.can_shoot(self.actions_stack)
           self.shoot.who("nearest_enemy")
           return model.UnitAction(
                    velocity=0,
                    jump=False,
                    jump_down=False,
                    aim = self.shoot.aim,
                    shoot=self.shoot.shoot,
                    reload = self.shoot.reload,
                    swap_weapon=self.swap,
                    plant_mine=self.plant)

    def go(self):
        self.shoot.can_shoot(self.actions_stack)
        self.shoot.who("nearest_enemy")
        #pop action to execute
        self.which_unit()
        ac = self.pop()
        self.should_push_back(ac)
        return model.UnitAction(
                    velocity=self.speed*(ac[1].x-self.unit.position.x)  ,
                    jump=False,
                    jump_down=False,
                    aim = self.shoot.aim,
                    shoot=self.shoot.shoot,
                    reload = self.shoot.reload,
                    swap_weapon=self.swap,
                    plant_mine=self.plant)


    def go_jump(self):
        self.shoot.can_shoot(self.actions_stack)
        self.shoot.who("nearest_enemy")
        #pop action to execute
        self.which_unit()
        ac = self.pop()
        self.should_push_back(ac)
        return model.UnitAction(
                    velocity=self.speed*(ac[1].x-self.unit.position.x)  ,
                    jump=True,
                    jump_down=False,
                    aim = self.shoot.aim,
                    shoot=self.shoot.shoot,
                    reload = self.shoot.reload,
                    swap_weapon=self.swap,
                    plant_mine=self.plant)



    def jump(self):
        self.shoot.can_shoot(self.actions_stack)
        self.shoot.who("nearest_enemy")
        #pop action to execute
        self.which_unit()
        ac = self.pop()
        self.should_push_back(ac)
        return model.UnitAction(
                    velocity=self.speed*(self.unit.position.y-ac[1].y),
                    jump=True,
                    jump_down=False,
                    aim = self.shoot.aim,
                    shoot=self.shoot.shoot,
                    reload = self.shoot.reload,
                    swap_weapon=self.swap,
                    plant_mine=self.plant)

    def down(self):
        self.shoot.can_shoot(self.actions_stack)
        self.shoot.who("nearest_enemy")
        #pop action to execute
        self.which_unit()
        ac = self.pop()
        self.should_push_back(ac)
        return model.UnitAction(
                    velocity=self.speed*(ac[1].x-self.unit.position.x)  ,
                    jump=False,
                    jump_down=True,
                    aim = self.shoot.aim,
                    shoot=self.shoot.shoot,
                    reload = self.shoot.reload,
                    swap_weapon=self.swap,
                    plant_mine=self.plant)
    
    def wait(self):
        if self.time_control == -1 :
            self.time_control = self.game.current_tick
        
        self.which_unit()
        ac = self.pop()
        tx = self.game.current_tick
        if tx - self.time_control < ac[1]:
            self.append(ac)
            return self.do_nothing()
        else:
            self.time_control = -1
            return self.do_nothing()


    def interpreter(self):
        p = self.pop()
        self.append(p)
        if p[0]=="XY":
            return self.XY()
        if p[0]=="DI":
            return self.go_jump()
    
   


    def XY(self):
        ac = self.pop()
        fe = self.eye.canMoveForward(ac[1],self.unit,self.game)
        rx = abs(self.unit.position.x - ac[1].x) <= self.xclose
        ry = self.unit.position.y >= ac[1].y and (abs(self.unit.position.y - ac[1].y) <= self.yclose)
        da = self.unit.position.y < ac[1].y
        db = self.unit.position.y > ac[1].y
        if fe:
            if rx:
                if ry:
                    return self.do_nothing()
                else:
                    if da:
                        self.append(ac)
                        return self.jump()
                    elif db:
                        self.append(ac)
                        return self.down()
            else:
                if ry:
                    self.append(ac)
                    return self.go()
                else:
                    if da:
                        self.append(ac)
                        return self.go_jump()#
                    elif db:
                        self.append(ac)
                        return self.go()
        else:
            if rx:
                if ry:
                    return self.do_nothing()
                else:
                    if da:
                        self.append(ac)
                        return self.jump()
                    elif db:
                        self.append(ac)
                        return self.down()
            else:
                if ry:
                    self.append(ac)
                    return self.go_jump()
                else:
                    if da:
                        self.append(ac)
                        return self.go_jump()
                    elif db:
                        self.append(ac)
                        return self.go_jump()

class Coordination:
    def __init__(self):
        self.x_unit=0.3
        self.y_unit=0.3
        self.z_unit=0.3
        self.field=None
        self.center=None
        #
        self.unit=None
        self.game=None
        self.debug=None
        #
        self.avoidance_points=None

    ##################################################
    # 01/02/2020
    def avoidance_points_proxy(self,w,p,i):
        if w == "zigzag":
            return self.zigzag(p,i)


    def zigzag(self,p,i):
        self.avoidance_points = [(p.x+2,p.y+2),
                                 (p.x-2,p.y+2),
                                 (p.x+2,p.y)]
        return self.avoidance_points[i]


   


    ##################################################
    # 12/30/2019

    def update_avoidance_points(self,p):
        self.avoidance_points = [(p.x+2,p.y+2),
                                 (p.x-2,p.y+2),
                                 (p.x+2,p.y)]

    ##################################################
    # 12/29/2019
    def points_above(p):
        L =[]
        for j in self.field:
            if j.y > p.y:
                L.append(j)
        return L

    def points_below(self,p):
        L = []
        for j in self.field:
            if j.y < p.y:
                L.append(j)
        return L

    def points_between_x(self,x_1,x_2):
        ma = 0
        mi = 0
        if x_1 < x_2:
           mi = x_1
           ma = x_2
        else:
            mi = x_2
            ma = x_1

        L = []
        for j in self.field:
            if mi <= j.x and j.x<=ma:
                L.append(j)
        return L

    def points_between_y(self,y_1,y_2):
        ma = 0
        mi = 0
        if y_1 < y_2:
           mi = y_1
           ma = y_2
        else:
            mi = y_2
            ma = y_1
        L = []
        for j in self.field:
            if mi <= j.y and j.y <=ma:
                L.append(j)
        return L

    def point_at_distance(self,p,d):
         w = model.Vec2Double(0,self.center.y)
         if p.x < self.center.x:
             w.x = max(self.center.x - d,0.2)
         else:
             w.x = min(self.center.x + d,37)
         return w

    ##################################################
    # 12/28/2019
    def find_closest_point(self,p):
        mi=100
        c = None
        for j in self.field:
            d = self.distance_sqr(p,j)
            if d < mi:
                c = j
                mi = d
        return c
                
    def find_further_from(self,p):
        ma = 0
        c = None
        for j in self.field:
            d = self.distance_sqr(p,j)
            if d > ma:
                c = j
                ma = d
        return c

    ################################################## 
    def update(self,unit,game,debug):
        self.unit = unit
        self.game = game
        self.debug = debug
    
    def set_2d_field(self,p,n):
        self.field=[]
        step=0.5
        row = len(self.game.level.tiles)
        col = len(self.game.level.tiles[0])
        for i in range(2*n):
            for j in range(2*n):
                if i == n and j == n:
                    continue
                q = model.Vec2Double(p.x+(-n+i)*step, p.y+(-n-j)*step) 
                cond = (0 <= q.x and q.x<=row) and ( 0 <= q.y and q.y <= col) and self.reachable(p,q)  
                if cond:
                    cond = self.game.level.tiles[int(q.x)][int(q.y)] == model.Tile.EMPTY 
                    if cond:
                        self.field.append(q)
        #print("neighbor",self.field)
        
    

    def further_from(self,p):
        p=None
        ma=0
        for j in self.field:
            d = self.distance_sqr(j,p)
            if d > ma:
                p=j
                ma=d
        return p

    def distance_from(self,p,n):
        L = []
        for j in self.field:
            if self.distance_sqr(p,j)>=n:
                L.append(j)
        return L

    
    def above_line(self,L):
        L =[]
        for j in self.field:
            fx = L.img(j.x)
            if fx < j.y:
                L.append(j)
        return L

    def below_line(self,L):
        L =[]
        for j in self.field:
            fx = L.img(j.x)
            if fx > j.y:
                L.append(j)
        return L
    
    def on_line(self,L):
        L =[]
        for j in self.field:
            fx = L.img(j.x)
            if fx == j.y:
                L.append(j)
        return L


    def distance_sqr(self,a,b):
        return (a.x - b.x) ** 2 + (a.y - b.y) ** 2

    def x_distance_sqr(self,a,b):
        return (a.x - b.x) ** 2 

    def y_distance_sqr(self,a,b):
        return  (a.y - b.y) ** 2

    def valid(self,p,q):
        row = len(self.game.level.tiles)
        col = len(self.game.level.tiles[0])
        cond = (0<=p.x) and (p.x <=row)
        cond = cond and (0<=p.y) and (p.y<=col)
        cond = cond and (self.game.level.tiles[int(p.x)][int(p.y)] == model.Tile.EMPTY)
        cond = cond and self.reachable(p,q)
        return cond

    def reachable(self,p,q):
       L = Line(1,2)
       L.find_eq(p,q)
       x1 = p.x
       x2 = q.x 
       ma = 0
       mi = 0
       d = 0.1
       if x1 > x2:
           ma = x1
           mi = x2
       else:
           ma = x2
           mi = x1
       while mi < ma:
           if self.game.level.tiles[int(mi)][int(L.img(mi))] == model.Tile.WALL:
               return False
           mi += d
       return True

class Shoot:
    def __init__(self):
        self.shoot =True 
        self.reload = False 
        self.aim = model.Vec2Double(2,2)
        self.eye = Eyes()
        self.actions_stack=None
        #
        self.unit = None
        self.game = None
        self.debug = None
        #
        self.target = None

    def update(self,unit,game,debug):
        self.unit = unit
        self.game = game
        self.debug = debug
        self.eye.update(unit,game,debug)

    def activate(self,active):
        self.shoot = active
    
    def who(self,w):
        if w == "nearest_enemy":
            self.target = self.eye.search_enemy(None,None,None)[0].position
            self.aim = model.Vec2Double(self.target.x - self.unit.position.x, self.target.y - self.unit.position.y)

   
    def can_shoot(self,st):
       L = Line(1,2)
       self.target = self.eye.search_enemy(None,None,None)[0]
       L.find_eq(self.unit.position,self.target.position)
       x1 = self.unit.position.x
       x2 = self.target.position.x 
       ma = 0
       mi = 0
       d = 0.1
       if x1 > x2:
           ma = x1
           mi = x2
       else:
           ma = x2
           mi = x1
       while mi < ma:
           if self.game.level.tiles[int(mi)][int(L.img(mi))] == model.Tile.WALL:
               self.shoot=False
               self.reload_gun()
               return 
           mi += d
       self.shoot = True

    
    def reload_gun(self):
        if self.unit.weapon is not None:
            if self.unit.weapon.magazine ==2:
                self.reload = True
            else:
                self.reload = False

    
class MyStrategy:
    def __init__(self):
        self.sparta = Sparta()
        self.data = None
        self.unit = None
        self.game = None
        self.unit_id=-1




    ###################################################
    #01/02/2020 
    def update(self,unit,game):
        self.unit = unit
        self.game = game
        if self.unit_id == -1:
            self.unit_id = self.unit.id

    
    def how_proxy(self):
        if self.unit_id == self.unit.id:
            return self.how_ij(7,0,0)
        else:
            return self.how_ij(10,1,0)
       

    def how_ij(self,i,j,k):
        L =["5","7","9","11","13","15","rand","tick","tick1","bullet","life_ratio"]
        Q =["p100","ples"]
        R =["zigzag"]
        data = {}
        data["distance"]=L[i]
        data["pack"]=Q[j]
        data["kata"]=R[k]
        return data

    ###################################################

    def get_action(self, unit, game, debug):
        #
        self.update(unit,game)
        #run sparta with parameters
        return self.sparta.brain(unit,game,debug,self.how_proxy())
        #return self.sparta.brain(unit,game,debug,self.data[self.data[0]["id"]])
