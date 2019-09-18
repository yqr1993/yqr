'''
Created on 2018.3.3

@author: yu_qian_ran
'''

import pygame as pg
from sys import exit
from _overlapped import NULL
import operator
import copy
import numpy as np



class gobject(pg.sprite.Sprite):
    framerate = pg.time.Clock()
    rate=64
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
    scroll_direction=0
    scroll_speed=0
    position=[]
    y_axis=0
    moveable=False
    attribute=""
    rigid_body=False
    living=False
    hp=0
    mp=0
    ad=0
    ap=0
    
    master_image=NULL
    image=NULL
    screen=NULL
    
    def __init__(self,name,width,height,ob,columns,screen,attribute,moveable,speed,position,rigid_body,living=False,hp=0,mp=0,ad=0,ap=0):
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
        self.hp=hp
        self.mp=mp
        self.ad=ad
        self.ap=ap
        self.living=living
        
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
            if self.direction==1:
                self.row=4
                self.frame_step=1
                self.position[1]-=self.speed
            elif self.direction==2:
                self.row=1
                self.frame_step=1
                self.position[1]+=self.speed
            elif self.direction==3:
                self.row=2
                self.frame_step=1
                self.position[0]-=self.speed
            elif self.direction==4:
                self.row=3
                self.frame_step=1
                self.position[0]+=self.speed
            elif self.direction==0:
                self.frame_step=0
                    
    def scroll(self):
        self.move_api()
        if self.scroll_direction==1:
            self.position[1]+=self.scroll_speed
        elif self.scroll_direction==2:
            self.position[1]-=self.scroll_speed
        elif self.scroll_direction==3:
            self.position[0]+=self.scroll_speed
        elif self.scroll_direction==4:
            self.position[0]-=self.scroll_speed
    
    def draw(self):
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
    screen=NULL
    incident=NULL
    physical=NULL
    stage=NULL
    gtext=NULL
    def __init__(self,screen,physical,incident,stage,gtext):
        self.screen=screen
        self.physical=physical
        self.incident=incident
        self.stage=stage
        self.gtext=gtext
        
    def player_control(self):
        if pg.key.get_pressed()[pg.K_w]:
            self.physical.direction=1
        elif pg.key.get_pressed()[pg.K_s]:
            self.physical.direction=2
        elif pg.key.get_pressed()[pg.K_a]:
            self.physical.direction=3
        elif pg.key.get_pressed()[pg.K_d]:
            self.physical.direction=4
        else:
            self.physical.direction=0
        for event in pg.event.get():
            if event.type==pg.QUIT:
                exit()
            elif event.type == pg.KEYDOWN:
                if event.key==pg.K_j:
                    self.incident.attack_judge("character")
                if event.key==pg.K_u:
                    self.incident.ask_judge("character",self.stage.current_stage[1])
                    self.incident.conversationSkip()                  
        
    def main(self):
        #player device control
        self.player_control()
        #physical operation and motion of objects in the game
        self.physical.motion()
        self.gtext.motion()
        #data of the game
        self.physical.game_attribute()
        self.stage.main()     
    
    

class physical():
    direction=0
    scroll_speed=6
    world=[]
    screen=NULL
    
    def __init__(self,screen):
        self.screen=screen
    
    def scroll_start(self):
        for n in self.world:
            if not n.attribute=="UI":
                n.scroll_speed=self.scroll_speed
            else:
                pass
    
    def scroll_stop(self):
        for n in self.world:
            if not n.attribute=="UI":
                n.scroll_speed=0
            else:
                pass
    
    def y_axis_manager(self):
        for n in self.world:
            if n.attribute!="ground":
                n.y_axis=n.position[1]+n.width/2
                if n.attribute=="road":
                    n.y_axis=-800
                elif n.attribute=="walls":
                    n.y_axis=-200
                elif n.attribute=="Text":
                    n.y_axis=1000
                elif n.attribute=="UI":
                    n.y_axis=800
            else:
                n.y_axis=n.position[1]-1000
        sortcal=operator.attrgetter("y_axis")
        self.world.sort(key=sortcal)
                
    def collision(self,detect_thing,basis=None,factor=0):
        for n in self.world:
            if n.rigid_body==False or n.attribute==detect_thing.attribute:
                continue
            b1=detect_thing.position[0]>=n.position[0]-detect_thing.width+detect_thing.width-factor*10
            b2=detect_thing.position[0]<=n.position[0]+n.width-detect_thing.width+factor*10
            b3=detect_thing.position[1]>=n.position[1]-detect_thing.height+detect_thing.height-factor*10
            b4=detect_thing.position[1]<=n.position[1]+n.height-detect_thing.height+factor*10
            if ((b1 and b2) and (b3 and b4) and n.rigid_body==True and (basis==None or basis==n.attribute)):
                return True,n
    
    def motion_stop(self,n):
        if n.moveable==True:
            if self.collision(n):
                if n.attribute=="character":
                    self.scroll_stop()
                if n.direction==1:
                    n.position[1]+=n.speed
                elif n.direction==2:
                    n.position[1]-=n.speed
                elif n.direction==3:
                    n.position[0]+=n.speed
                elif n.direction==4:
                    n.position[0]-=n.speed
    
    def motion_start(self,n):
        if n.moveable==True:
            if not self.collision(n):
                if n.attribute=="character":
                    self.scroll_start()
    
    def move_main(self):
        for n in self.world:
            n.scroll_direction=self.direction
            if n.attribute=="character":
                n.direction=self.direction
            n.move()
            self.motion_start(n)
            self.motion_stop(n)
            
    def scroll_main(self):
        for n in self.world:
            n.scroll()
            n.draw()
            
    def motion(self):
        self.y_axis_manager()
        self.scroll_main()  
        self.move_main()
        
    def destroy(self,name):
        for n in self.world:
            if n.name==name:
                self.world.remove(n)

    def create(self,ob):
        self.world.append(ob)
    
    def hp_main(self):
        for n in self.world:
            if n.living==True:
                pass
        
    def mp_main(self):
        pass
    
    def game_attribute(self):
        self.hp_main()
        self.mp_main()



class incident():
    physical=NULL
    gtext=NULL
    
    ask_state=0
    
    def __init__(self,physical,gtext):
        self.physical=physical
        self.gtext=gtext
        
    def attack_judge(self,ob):
        for n in physical.world:
            if n.attribute==ob:
                judge=self.physical.collision(n,"enemy",5)
                if judge:
                    judge[1].hp-=n.ad
    
    def death_judge(self):
        label=0
        for n in physical.world:
            if n.hp<=0 and n.attribute=="character":
                print("game over")
            elif n.hp<=0 and n.living==True:
                physical.world.remove(n)
                label+=1
        return label

    def ask_judge(self,ob,target):
        for n in physical.world:
            if n.attribute==ob:
                judge=self.physical.collision(n,"NPC",2)
                if judge and judge[1].name==target:
                    self.ask_state=1
                
    def conversationSkip(self):
        if self.ask_state==1:
            self.gtext.text_index+=1
            self.gtext.conNext()
                    
    def travel(self,ob):
        for n in physical.world:
            if n.attribute==ob:
                judge=self.physical.collision(n,"point",2)
                if judge:
                    return True



class model():
    def __init__(self,main_camera,screen):
        main_camera.world.append(gobject("UI",600,150,pg.image.load("UI.png"),1,screen,"UI",False,0,[0,450],False))
        main_camera.world.append(gobject("ground",1800,1800,pg.image.load("ground.png"),1,screen,"ground",False,0,[-400,-800],False))
        main_camera.world.append(gobject("house",200,200,pg.image.load("house1.png"),1,screen,"house",False,0,[420,-200],True))
        main_camera.world.append(gobject("house",200,200,pg.image.load("house2.png"),1,screen,"house",False,0,[620,400],True))
        main_camera.world.append(gobject("walls",1200,70,pg.image.load("walls_horizontal.png"),1,screen,"walls",False,0,[-100,-520],True))
        main_camera.world.append(gobject("walls",1200,70,pg.image.load("walls_horizontal.png"),1,screen,"walls",False,0,[-100,600],True))
        main_camera.world.append(gobject("walls",70,1200,pg.image.load("walls_vertical.png"),1,screen,"walls",False,0,[-100,-520],True))
        main_camera.world.append(gobject("walls",70,1200,pg.image.load("walls_vertical.png"),1,screen,"walls",False,0,[1020,-520],True))
        main_camera.world.append(gobject("tree",62,62,pg.image.load("tree.png"),1,screen,"tree",False,0,[500,100],True))
        main_camera.world.append(gobject("tree",62,62,pg.image.load("tree.png"),1,screen,"tree",False,0,[120,400],True))
        main_camera.world.append(gobject("tree",62,62,pg.image.load("tree.png"),1,screen,"tree",False,0,[400,340],True))
        main_camera.world.append(gobject("tree",62,62,pg.image.load("tree2.png"),1,screen,"tree",False,0,[560,300],True))
        main_camera.world.append(gobject("灭神",70,70,pg.image.load("neo.png"),1,screen,"NPC",False,0,[360,200],True))
        
        main_camera.world.append(gobject("enemy_1",33,43,pg.image.load("ene.png"),6,screen,"enemy",True,4,[80,450],True,True,20,20,5,5))
        main_camera.world.append(gobject("enemy_2",33,43,pg.image.load("ene.png"),6,screen,"enemy",True,4,[50,450],True,True,20,20,5,5))
        main_camera.world.append(gobject("enemy_3",33,43,pg.image.load("ene.png"),6,screen,"enemy",True,4,[20,450],True,True,20,20,5,5))
        main_camera.world.append(gobject("Joker",40,43,pg.image.load("cha.png"),6,screen,"character",True,main_camera.scroll_speed,[300,200],True,True,100,100,10,10))
        main_camera.scroll_start()
        


class stage():
    incident=NULL
    gtext=NULL
    detail=[]
    current_stage=[]
    mission_index=0
    mission_state=0
    mission_type=0
    def __init__(self,file_path,incident,gtext):
        file=open(file_path)
        for n in file.readlines():
            temp=n.rstrip().split(',')
            self.detail.append(temp)
        self.incident=incident
        self.gtext=gtext
    
    def main(self):
        #print(self.mission_state,self.current_stage)
        if self.mission_state==0:
            self.mission_start()
            self.mission_state=1
        elif self.mission_state==1:
            self.mission()
        elif self.mission_state==2:
            self.mission_end()
            self.mission_state=0
    
    def mission_start(self):
        self.current_stage=self.detail[self.mission_index]
        if self.current_stage[0]=="对话":
            self.mission_type=1
        elif self.current_stage[0]=="战斗":
            self.mission_type=2
        elif self.current_stage[0]=="交付":
            self.mission_type=3
    
    def mission(self):
        if self.mission_type==1:
            if self.conversation():
                self.mission_state=2
        elif self.mission_type==2:
            if self.battle():
                self.mission_state=2
        elif self.mission_type==3:
            if self.delivery():
                pass
    
    def mission_end(self):
        if self.mission_index<len(self.detail)-1:
            self.mission_index+=1
    
    def conversation(self):
        print(self.gtext.text_index,len(self.gtext.con)-1)
        if self.gtext.text_index==len(self.gtext.con)-1:
            self.gtext.text_index=-1
            self.incident.ask_state=0
    
    def battle(self):
        num_temp=self.incident.death_judge()
        temp=int(self.current_stage[2])-num_temp
        self.current_stage[2]=str(temp)
        if temp==0:
            return True
    
    def delivery(self):
        pass



class gtext():
    img=NULL
    con_img=NULL
    position=[150,500]
    screen=NULL
    
    con=[]
    text_index=-1
    con_index=0
    
    atttri=[]
    
    menu=[]
    
    def __init__(self,path_con,screen):
        self.screen=screen
        self.img=pg.font.SysFont("Segoe Script",13)
        self.con_img=self.img.render("",True,(0,0,0))
        self.text_operation(path_con, self.con)
        
    def text_operation(self,path,inp):
        file=open(path)
        for n in file.readlines():
            temp=n.rstrip().split(' ')
            inp.append(temp)
        inp.append(["",""])
        
    def conNext(self):
        self.con_img=self.img.render(self.con[self.text_index][1],True,(0,0,0))
    
    def motion(self):
        self.screen.blit(self.con_img, (self.position[0],self.position[1]))
    
    
    
class test():
    def __init__(self):
        pg.display.init()
        pg.font.init()
        pg.display.set_caption("RPG MINI")
        
        screen=pg.display.set_mode((600, 600),0,32)
        gt=gtext("conversation.txt",screen)
        phy=physical(screen)
        inc=incident(phy,gt)
        sta=stage("stage.txt",inc,gt)
        model(phy,screen)
        
        gc=game_control(screen,phy,inc,sta,gt)
        
        while True:
            gc.main()
            pg.display.flip()



test()
