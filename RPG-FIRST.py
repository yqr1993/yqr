'''
Created on 2017年1月3日

@author: 余谦然
'''

import pygame as pg
from sys import exit
from _overlapped import NULL
import operator
import copy
import numpy as np
               

class gobject(pg.sprite.Sprite):
    framerate = pg.time.Clock()
    rate=32
    frame=1
    first_frame=1
    last_frame=0
    frame_step=1
    row=1
    
    name=""
    width=0
    height=0
    speed=0
    direction=1
    position=[]
    y_axis=0
    moveable=False
    attribute=""
    rigid_body=False
    
    scroll_direction=0
    scroll_speed=0
    
    master_image=NULL
    image=NULL
    screen=NULL
    
    def __init__(self,name,width,height,ob,columns,screen,attribute,moveable,speed,position,rigid_body):
        self.master_image = ob
        self.last_frame=columns
        self.frame_width = width
        self.frame_height = height
        self.width=width
        self.height=height
        self.name=name
        self.position=position.copy()
        self.attribute=attribute
        self.rect = 0,0,width,height
        self.columns = columns
        self.screen=screen
        self.speed=speed
        self.moveable=moveable
        self.rigid_body=rigid_body
        self.framerate.tick(self.rate)
        
    def move_api(self):
        self.frame += self.frame_step
        if self.frame > self.last_frame:
            self.frame = self.first_frame
        frame_x = (self.frame-1) * self.frame_width
        frame_y=(self.row-1)*self.frame_height
        rect = (frame_x, frame_y, self.frame_width, self.frame_height)
        self.image = self.master_image.subsurface(rect)

        
    def move(self):
        if self.moveable:
            if self.name=="zoom":
                if self.direction==1:
                    self.position[1]-=self.speed
                elif self.direction==2:
                    self.position[1]+=self.speed
                elif self.direction==3:
                    self.position[0]-=self.speed
                elif self.direction==4:
                    self.position[0]+=self.speed         
            else:       
                if self.direction==1:
                    self.row=4
                    self.position[1]-=self.speed
                elif self.direction==2:
                    self.row=1
                    self.position[1]+=self.speed
                elif self.direction==3:
                    self.row=2
                    self.position[0]-=self.speed
                elif self.direction==4:
                    self.row=3
                    self.position[0]+=self.speed
                    
    def scroll(self):
        self.move_api()
        self.screen.blit(self.image,(self.position[0],self.position[1]))    
        
    def AI(self,target):
        position=target.position
        vector=[0,0]
        vector[0]=position[0]-self.position[0]
        vector[1]=position[1]-self.position[1]
        factor=int(np.random.random()*2)
        if factor==0:
            if vector[0]>0:
                self.direction=4
            else:
                self.direction=3
        if factor==1:
            if vector[1]>0:
                self.direction=2
            else:
                self.direction=1


               
class game_control():
    audio=NULL
    UI=[]
    gtext=NULL
    stage=NULL
    screen=NULL
    
    object=NULL
    world=[]
    world_effect=[]
    world_enemy=[]
    position_manager=[]
    position_manager_enemy=[]
    
    speed=6
    speed_effect=6
    level=1
    exp=0
    level_up_counter=100
    
    effect_counter=11
    enemy_ai_counter=0
    if_enemy_show=True
    incident_main=["",False]
    effect={}
    
    def __init__(self,cobject,UI,screen,audio,gtext,stage):
        self.object=cobject
        self.UI.append(UI)
        self.UI.append(gtext)
        self.screen=screen
        self.audio=audio
        self.gtext=gtext
        self.stage=stage
        self.effect={"zoom":[gobject("zoom",50,50,pg.image.load("zoom.png"),1,screen,"effect",True,16,[0,0],False),False],
                     "fire":[gobject("fire",64,64,pg.image.load("fire1.png"),16,screen,"effect",False,0,[0,0],False),False]}
        
    def control(self):
        self.audio.control()
        self.gtext.text_control(self.incident_main[1],self.level)
        self.position_control()
        self.player_control()
        self.position_enemy_control()
        self.AI_start()
        self.motion()
        self.enemy_motion()
        self.effect_motion()
        self.UI_motion()
        self.enemy_motion_stand_trigger()
        self.motion_stand_trigger(self.object)
        self.stage.mission_control()
        self.enemy_show_trigger()
        self.skip_plot()
        self.attack_judge()
        self.failure_killed()
        self.level_trigger()
                
    def player_control(self):
        if pg.key.get_pressed()[pg.K_w]:
            for n in self.world:
                n.position[1]+=self.speed
            for n in self.world_effect:
                n[0].position[1]+=self.speed_effect
            for n in self.world_enemy:
                n.position[1]+=self.speed_effect
            self.fixed()
            self.object.direction=1
            self.object.frame_step=1
        elif pg.key.get_pressed()[pg.K_s]:
            for n in self.world:
                n.position[1]-=self.speed
            for n in self.world_effect:
                n[0].position[1]-=self.speed_effect
            for n in self.world_enemy:
                n.position[1]-=self.speed_effect
            self.fixed()
            self.object.direction=2
            self.object.frame_step=1
        elif pg.key.get_pressed()[pg.K_a]:
            for n in self.world:
                n.position[0]+=self.speed
            for n in self.world_effect:
                n[0].position[0]+=self.speed_effect
            for n in self.world_enemy:
                n.position[0]+=self.speed_effect
            self.fixed()
            self.object.direction=3
            self.object.frame_step=1
        elif pg.key.get_pressed()[pg.K_d]:
            for n in self.world:
                n.position[0]-=self.speed
            for n in self.world_effect:
                n[0].position[0]-=self.speed_effect
            for n in self.world_enemy:
                n.position[0]-=self.speed_effect
            self.fixed()
            self.object.direction=4
            self.object.frame_step=1
        else:
            self.object.frame_step=0
        for event in pg.event.get():
            if event.type == pg.KEYDOWN:
                if event.key==pg.K_j:
                    self.effect.get("fire")[1]=False
                    self.effect.get("zoom")[1]=True
                    for n in self.world_effect:
                        if n[1]=="fire":
                            self.world_effect.remove(n)
                    if self.effect.get("zoom")[1]:
                        zoom=self.effect.get("zoom")[0]
                        zoom.position=self.object.position.copy()
                        zoom.direction=self.object.direction
                        self.world_effect.append([copy.copy(zoom),"zoom"])
                if event.key==pg.K_u:
                    self.conversation_trigger(self.object)
            elif event.type==pg.KEYUP:
                if event.key==pg.K_j:
                    self.effect.get("zoom")[1]=False
                    self.effect.get("fire")[1]=True
                    fire=self.effect.get("fire")[0]
                    fire.position=self.world_effect[0][0].position
                    self.world_effect.append([copy.copy(fire),"fire"])
                    for n in self.world_effect:
                        if n[1]=="zoom":
                            self.world_effect.remove(n)                       
            if event.type==pg.QUIT:
                exit()
                
    def motion(self):
        for n in self.world:
            n.move()
            n.scroll()
    
    def skip_plot(self):
        if len(self.world_enemy)==0 and self.incident_main[0]=="1-2":
            self.incident_main[0]="1-3"
            self.gtext.id=1
            self.incident_main[1]=True
            
    def effect_motion(self):
        for n in self.world_effect:
            n[0].move()
            n[0].scroll()
            if n[0].name=="fire":
                self.effect_counter+=1
                if self.effect_counter%10==0:
                    self.world_effect.remove(n)
                    self.effect_counter=11
            
    def enemy_motion(self):
        for n in self.world_enemy:
            n.move()
            n.scroll()
    
    def UI_motion(self):
        for n in self.UI:
            n.move()
            n.scroll() 
    
    def fixed(self):
        self.object.position[1]=200
        self.object.position[0]=300
        self.UI[0].position=[0,450]
        self.UI[1].position=[150,500]
        
    def position_control(self):
        for n in self.world:
            if n.attribute!="map":
                n.y_axis=n.position[1]+n.width/2
                if n.attribute=="road":
                    n.y_axis=-800
                elif n.attribute=="wall":
                    n.y_axis=-200
                elif n.attribute=="Text":
                    n.y_axis=1000
            else:
                n.y_axis=n.position[1]-1000
        sortcal=operator.attrgetter("y_axis")
        self.world.sort(key=sortcal)
        for n in self.world:
            self.position_manager.append(n.position.copy())
            
    def position_enemy_control(self):
        for n in self.world_enemy:
            self.position_manager_enemy.append(n.position.copy())              
    
    def AI_start(self):
        self.enemy_ai_counter+=1
        if self.enemy_ai_counter%20==0:
            for n in self.world_enemy:
                n.AI(self.object)
            self.enemy_ai_counte=0
            
    def enemy_show_trigger(self):
        if self.stage.stage.get("1-1")[3] and not self.stage.stage.get("1-2")[3] and self.if_enemy_show:
            self.incident_main[0]="1-2"
            self.audio.switch=True
            self.audio.music_switch("battle.mp3")
            self.enemy_add(1)
            self.stage.stage.get("1-2")[3]=True
            self.if_enemy_show=False
            
            
    def collision(self,detect_thing,detected_thing,factory):
        if not(detected_thing.attribute=="ground" or detected_thing.attribute=="character"):
            b1=detect_thing.position[0]>detected_thing.position[0]-detect_thing.width+detect_thing.width*factory
            b2=detect_thing.position[0]<detected_thing.position[0]+detected_thing.width-detect_thing.width*factory
            b3=detect_thing.position[1]>detected_thing.position[1]-detect_thing.height+detect_thing.height*factory
            b4=detect_thing.position[1]<detected_thing.position[1]+detected_thing.height-detect_thing.height*factory
            if (b1 and b2) and (b3 and b4) and detected_thing.rigid_body==True:
                return True
        
    def motion_stand_trigger(self,object_detect):
        temp=self.world.copy()
        self.speed_effect=6
        for n in temp:
            if self.collision(object_detect,n,1):
                self.speed_effect=0
                for m,n in zip(self.world,self.position_manager):
                    m.position=n.copy()
        self.position_manager.clear()

    def enemy_motion_stand_trigger(self):
        temp=self.world.copy()
        for n in self.world_enemy:
            for m in temp:
                if self.collision(n,m,1):
                    n.position=self.position_manager_enemy[self.world_enemy.index(n)]
                    break
        self.position_manager_enemy.clear()
                
    def attack_judge(self):
        for n in self.world_effect:
            if n[1]=="fire":
                for m in self.world_enemy:
                    if self.collision(m,n[0],1):
                        self.world_enemy0.remove(m)
                        self.exp+=10
    
    def failure_killed(self):
        for m in self.world_enemy:
            if self.collision(m,self.object,1):
                return True
     
    def enemy_add(self,num):
        speed=4
        for _ in range(num):
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[0,-50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[0,0],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[0,50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[50,-50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[50,0],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[50,50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[100,50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[100,0],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[100,50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[750,-50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[750,0],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[750,50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[800,-50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[800,0],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[800,50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[850,-50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[850,0],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[850,50],False)) 
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[900,-50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[900,0],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[900,50],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[50,450],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[50,500],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[50,550],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[100,450],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[100,500],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[100,550],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[150,450],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[150,500],False))
            self.world_enemy.append(gobject("enemy",33,43,pg.image.load("ene.png"),6,self.screen,"enemy",True,speed,[150,550],False))                
    
    def conversation_trigger(self,object_detect):
        temp=self.world.copy()
        self.gtext.skip=True
        for n in temp:
            if self.collision(object_detect,n,0) and n.attribute=="NPC" and n.rigid_body==True and not self.stage.stage.get("1-1")[3]:
                self.incident_main[0]="1-1"
                self.speed=0
                self.incident_main[1]=True
            if self.gtext.index==len(self.gtext.text[0]):
                self.incident_main[1]=False
                self.speed=6
                self.stage.stage.get(self.incident_main[0])[3]=True
    
    def level_trigger(self):
        if self.exp>=self.level*40:
            self.level+=1
            self.level_up_counter=51
        if not self.level_up_counter%50==0:
            self.gtext.level_trigger=True
            self.level_up_counter+=1
        else:
            self.gtext.level_trigger=False
            self.level_up_counter=100
                
                

class Model():
    def model_load(self,main_camera,screen):
        wall_create_position3=[-140,760]
        wall_count3=31
        wall_interval3=40
        
        wall_create_position4=[-140,760]
        wall_count4=34
        wall_interval4=40
        
        wall_create_position1=[-140,-560]
        wall_count1=31
        wall_interval1=40
        
        wall_create_position2=[1060,-560]
        wall_count2=34
        wall_interval2=40
        
        road_create_position1=[-500,400]
        road_count1=16
        road_interval1=160
        
        road_create_position2=[200,800]
        road_count2=12
        road_interval2=160
        
        main_camera.world.append(gobject("ground",1800,1800,pg.image.load("ground.png"),1,screen,"map",False,0,[-400,-800],False))
        main_camera.world.append(gobject("house",300,288,pg.image.load("house.png"),1,screen,"house",False,0,[420,200],True))
        main_camera.world.append(gobject("house",200,200,pg.image.load("house1.png"),1,screen,"house",False,0,[420,-200],True))
        main_camera.world.append(gobject("house",200,200,pg.image.load("house2.png"),1,screen,"house",False,0,[620,550],True))
        
        for _ in range(wall_count3):
            main_camera.world.append(gobject("wall",70,70,pg.image.load("wall.png"),1,screen,"wall",False,0,wall_create_position3,True))
            wall_create_position3[0]+=wall_interval3
        
        for _ in range(wall_count4):
            main_camera.world.append(gobject("wall",70,70,pg.image.load("wall2.png"),1,screen,"wall",False,0,wall_create_position4,True))
            wall_create_position4[1]-=wall_interval4
        
        for _ in range(wall_count1):
            main_camera.world.append(gobject("wall",70,70,pg.image.load("wall.png"),1,screen,"wall",False,0,wall_create_position1,True))
            wall_create_position1[0]+=wall_interval1            
        
        for _ in range(wall_count2):
            main_camera.world.append(gobject("wall",70,70,pg.image.load("wall2.png"),1,screen,"wall",False,0,wall_create_position2,True))
            wall_create_position2[1]+=wall_interval2  
        
        for _ in range(road_count1):
            main_camera.world.append(gobject("road",293,293,pg.image.load("road.png"),1,screen,"road",False,0,road_create_position1,False))
            road_create_position1[0]+=road_interval1
            
        for _ in range(road_count2):
            main_camera.world.append(gobject("road",293,293,pg.image.load("road1.png"),1,screen,"road",False,0,road_create_position2,False))
            road_create_position2[1]-=road_interval2
            
        main_camera.world.append(gobject("tree",62,62,pg.image.load("tree.png"),1,screen,"tree",False,0,[500,100],True))
        main_camera.world.append(gobject("tree",62,62,pg.image.load("tree.png"),1,screen,"tree",False,0,[120,700],True))
        main_camera.world.append(gobject("tree",62,62,pg.image.load("tree.png"),1,screen,"tree",False,0,[400,640],True))
        main_camera.world.append(gobject("tree",62,62,pg.image.load("tree2.png"),1,screen,"tree",False,0,[560,600],True))
        main_camera.world.append(gobject("Destroy",70,70,pg.image.load("neo.png"),1,screen,"NPC",False,0,[300,400],True))



class Stage():
    stage_id=[]
    temp=""
    stage={}
    
    def __init__(self,file_path):
        file=open(file_path)
        for n in file.readlines():
            temp=n
            self.stage[temp.split(" ")[0]]=[temp.split(" ")[1],temp.split(" ")[2],temp.split(" ")[3],False]
    
    def mission_control(self):
        pass
             
       

class Audio():
    background=[]
    sound={}
    switch=False
    def __init__(self):
        pg.mixer.init()
        pg.mixer.music.load("back1.mp3")
        pg.mixer.music.set_volume(1)
        pg.mixer.music.play()
        
    def music_switch(self,music_path):
        if self.switch:
            pg.mixer.music.load(music_path)
            pg.mixer.music.play()
            self.switch=False
        
    def control(self):
        if not pg.mixer.music.get_busy:
            pg.mixer.music.rewind()
            
            
 
class Text():
    mytext=NULL
    leveltext=NULL
    screen=NULL
    position=[150,500]
    img=NULL
    img2=NULL
    attribute="Text"
    rigid_body=False
    speed=0
    y_axis=1000
    width=100
    text=[]
    index=0
    skip=True
    level_trigger=False
    current=""
    id=0
    
    def __init__(self,screen,moveable):
        for m in range(2):
            self.text.append([])
            file=open("1-"+str(m+1)+".dat")
            for n in file.readlines():
                n.strip()
                self.text[m].append(n)
            file.close()
        self.mytext=pg.font.SysFont("Segoe Script",13)
        self.leveltext=pg.font.SysFont("Segoe Script",13)
        self.screen=screen
        self.moveable=moveable
    
    def text_control(self,trigger,level):
        self.img=self.mytext.render(self.current,True, (0, 0, 0))
        if trigger:
            c_len=len(self.text[self.id])
            if self.index<c_len and self.skip:
                self.current=self.text[self.id][self.index]
                self.index+=1
                self.skip=False
            self.img=self.mytext.render(self.current.rstrip(),True, (0, 0, 0))
        else:
            self.index=0
            self.current=""
        if self.level_trigger==True:
            self.level_up()
        self.img2=self.leveltext.render(str(level),True, (0, 0, 0))
    
    def level_up(self):
        self.current="level up!"
        self.img=self.mytext.render(self.current, True, (0, 0, 0))
    
    def scroll(self):
        self.screen.blit(self.img, (self.position[0],self.position[1]))
        self.screen.blit(self.img2,[88,545])
     
    def move(self):
        if self.moveable:
            if self.direction==1:
                self.position[1]-=self.speed
            elif self.direction==2:
                self.position[1]+=self.speed
            elif self.direction==3:
                self.position[0]-=self.speed
            elif self.direction==4:
                self.position[0]+=self.speed
    
    
    
class game():
    def __init__(self):
        global screen,character,UI,audio,model,main_camera
        pg.display.init()
        pg.font.init()
        pg.display.set_caption("RPG MINI")
        screen=pg.display.set_mode((600, 600),0, 32)
        
        character=gobject("Joker",40,43,pg.image.load("cha.png"),6,screen,"character",True,0,[300,200],False)
        UI=gobject("UI",600,150,pg.image.load("UI.png"),1,screen,"UI",False,0,[0,450],False)
        audio=Audio()
        gtext=Text(screen,False)
        stage=Stage("mission.dat")
        
        main_camera=game_control(character,UI,screen,audio,gtext,stage)
        model=Model()
        
        model.model_load(main_camera,screen)
        main_camera.world.append(character)
        
        while True:
            if main_camera.failure_killed():
                dead_text=pg.font.SysFont("Segoe Script",13)
                img3=dead_text.render("you are dead!!",True, (0, 0, 0))
                screen.blit(img3, (gtext.position[0],gtext.position[1]))
                pg.display.update()
                self.restart()
            main_camera.control()
            pg.display.flip()

    def restart(self):
        global screen,character,model,main_camera
        main_camera.world.clear()
        main_camera.world_enemy.clear()
        main_camera.exp=0
        main_camera.level=1
        model.model_load(main_camera, screen)
        main_camera.enemy_add(1)
        main_camera.world.append(character)
     
                
game()











