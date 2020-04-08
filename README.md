## CODESIDE 2019
>Open artificial intelligence programming contest. Test yourself writing a game strategy! It's simple, clear and fun.
>In each game you are to compete against another player's strategy. Your team's goal - is to gain score by killing or
>doing damage to your opponent. 


[Link to CodeSide2019](https://russianaicup.ru) <br/>
[My Profile](russianaicup.ru/profle/a24benzene)  <br/> 


## STRATEGY
The strategy was implemented into 5 classes, Sparta, Eyes, Duration, Control, Coordination and Shoot responsible of querying data from the game world, 
finding paths and adjusting the position of the units. In brief, the strategy relied on keeping my units at any given time at a specific distance from 
the enemy units.  


## CODE 
The essential of the strategy was executed by the method "brain" of 
the class "Sparta". In order of priority, the steps are:   

1. Test if there is an action to execute.
2. Get a gun. 
3. Get a health pack if some conditions are met.
4. Find an enemy unit.
5. Choose the ideal distance to stay from the enemy unit.
6. Choose how to avoid the bullets.
7. Send command to the game world.    

```python
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
```





