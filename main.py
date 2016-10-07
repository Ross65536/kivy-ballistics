import kivy
import os
import random

kivy.require('1.9.0')

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.togglebutton import ToggleButton
from kivy.uix.widget import Widget
from kivy.properties import ReferenceListProperty
from kivy.properties import ObjectProperty
from kivy.graphics import Color
from kivy.graphics import Rectangle
from kivy.graphics import Ellipse
from kivy.graphics import PopMatrix
from kivy.graphics import PushMatrix
from kivy.graphics import Rotate
from kivy.clock import Clock
from kivy.config import Config
from kivy.vector import Vector
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.base import EventLoop
from functools import partial
from random import random, randint
import itertools
import math
from kivy.uix.screenmanager import FadeTransition, FallOutTransition
#from kivy.core.audio import SoundLoader
#from kivy.core.audio.audio_sdl2 import SoundSDL2
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.core.text import LabelBase

Config.set('graphics', 'width', '400')
Config.set('graphics', 'height', '711')

# settings, level selection : Rabbid-Highway-Sign

KIVY_FONTS = [
    {
        "name": "moonhouse",
        "fn_regular": "Resources/fonts/moonhouse.ttf"
    }
]
    
for font in KIVY_FONTS:
    LabelBase.register(**font)



class Space_Background (Widget):
    rect=None
    main_app= None
    background_num= None
    def __init__ (self, main_app, background_num= None, randomf0to1=None):
        super(Space_Background, self).__init__()
        self.main_app=main_app
        if background_num==None:
            background_num= randint(1,main_app.number_of_backgrounds)
        if randomf0to1==None:
            randomf0to1=random()
        self.background_num=background_num
        with self.canvas:
            self.rect=Rectangle(source= 'Resources/backgrounds/' + str(background_num) + '.png' , pos= (-0.25 * main_app.screen_manager.height * randomf0to1 ,0) , size= (main_app.screen_manager.height , main_app.screen_manager.height))
    def update_pos (self, a2, screen_size):
        self.rect.size= (screen_size[1] , screen_size[1])
    def rotate (self):
        rand=self.background_num
        while rand== self.background_num:
            rand=randint(1,self.main_app.number_of_backgrounds)
        randomf0to1=random()
        self.background_num=rand
        self.rect.source= 'Resources/backgrounds/' + str(rand) + '.png'
        self.rect.pos= (-0.25 * self.main_app.screen_manager.height * randomf0to1 , 0)

class Planet_Background (Widget):
    rect=None
    main_app= None
    def __init__ (self, main_app, background_num= None, randomf0to1=0):
        super(Planet_Background, self).__init__()
        self.main_app=main_app
        with self.canvas:
            self.rect=Rectangle(source= 'Resources/backgrounds/planet_background.png' , pos= (0,0) , size= (main_app.screen_manager.height , main_app.screen_manager.height))
    def update_pos (self, a2, screen_size):
        self.rect.size= (screen_size[1] , screen_size[1])


class StartScreen(Screen):
    game_button= ObjectProperty(None)
    pass

class LevelSelectionScreen(Screen):
    gridlayout=ObjectProperty(None)
    pass

class SettingsScreen(Screen):
    checkbox_SFX=ObjectProperty(None)
    checkbox_Music=ObjectProperty(None)
    pass

class GameScreen(Screen):
    pass

class LevelWonScreen(Screen):
    pass

class LevelWonScreenEnd(Screen):
    pass

class LevelLostScreen(Screen):
    pass

class LevelLostScreen2(LevelLostScreen):
    lost_label= None
    pass

class LevelSelectionButton(Button):
    main_app= ObjectProperty(None)
    level= ObjectProperty(None)
    text= ObjectProperty(None)
    def __init__ (self, **kwargs):
           super(LevelSelectionButton, self).__init__(**kwargs)
           self.bind(on_press=self.on_press_f)

    def on_press_f(self, instance):
        if self.main_app.beat_to_the_level >= self.level:
            self.main_app.game_widget.current_level=self.level
            self.main_app.create_level()
            self.main_app.screen_game.space_background.rotate()
            self.main_app.screen_manager.current = 'game_screen'
        

class Widget(Widget):
    bbase_enemy_ball=False
    bbase_objective_ball=False




class BaseBullet(Widget):
    
    speed=[0,0]
    ellip=None

    def __init__(self,pos,speed, **kwargs):
        super(BaseBullet, self).__init__(**kwargs)
        self.pos=pos
        self.speed=speed
    def update(self, root, dt):


        self.pos[0]=self.pos[0]+dt*self.speed[0]
        self.pos[1]=self.pos[1]+dt*self.speed[1]
        #self.draw_instruction.pos=self.pos        
        
        ar=[0, 0]
        for ball in root.balls_list:
            dy=ball[0][1]-self.pos[1]
            dx=ball[0][0]-self.pos[0]
            r2=dx**2+dy**2
            r= math.sqrt(r2)
            if (r<=ball[1]):
                return 1
            ang=math.atan2(dy,dx) 
            a = ( root.gravity_constant * root.bullet_gravity_constant * ball[2] / float(r2) )
            ar[0] = ar[0] + a * math.cos(ang)
            ar[1] = ar[1] + a * math.sin(ang)
            
        for ball in root.balls_objective_list:
            dy=ball[0][1]-self.pos[1]
            dx=ball[0][0]-self.pos[0]
            r2=dx**2+dy**2
            r= math.sqrt(r2)
            if (r<=ball[1]):
                root.remove_widget(ball[4])
                root.balls_objective_list.remove(ball)
                return 2
            ang=math.atan2(dy,dx) 
            a = ( root.gravity_constant * root.bullet_gravity_constant * ball[3] * ball[2] / float(r2) )
            ar[0] = ar[0] + a * math.cos(ang)
            ar[1] = ar[1] + a * math.sin(ang)
        # [ [ [center_x, center_y], radius, mass, density, widget_ref ] , ...]

        self.speed=[self.speed[0] + ar[0] * dt , self.speed[1] + ar[1] * dt ]
        
    
        if (self.pos[1]>1.5 * root.height) or (self.pos[1]< -0.5 * root.height):
            return 1
        elif self.pos[0]<-0.5 * root.width or self.pos[0]>root.width * 1.5:     # TODO: Physics!
            return 1
        return 0


class Bullet(BaseBullet):
    pass

class HeavyBullet(BaseBullet):
    def update(self, root, dt):
        self.pos[0]=self.pos[0]+dt*self.speed[0]
        self.pos[1]=self.pos[1]+dt*self.speed[1]
        #self.draw_instruction.pos=self.pos        
        
        ar=[0, 0]
        for ball in root.balls_list:
            dy=-1*ball[0][1]+self.pos[1]
            dx=-1*ball[0][0]+self.pos[0]
            r2=dx**2+dy**2
            r= math.sqrt(r2) 
            ang=math.atan2(dy,dx) 
            if (r<=ball[1]):
                ball[4].bmove=True
                ball[4].brotate=True

                # TODO: rotation maths
                ball[4].brotate=False

                vang=math.atan2(self.speed[1], self.speed[0])
                dang=ang-vang
                cdang=math.cos(dang)
                dvCM=math.sqrt((self.speed[1]**2+self.speed[0]**2) * 1.0 * root.heavy_bullet_constant * (cdang ** 2) / ball[2])
                ball[4].speed[0]=ball[4].speed[0] - dvCM * math.cos(ang)
                ball[4].speed[1]=ball[4].speed[1] - dvCM * math.sin(ang)
                return 1

            a = ( root.gravity_constant * root.bullet_gravity_constant * ball[3] * ball[2] / float(r2) )
            ar[0] = ar[0] - a * math.cos(ang)
            ar[1] = ar[1] - a * math.sin(ang)
            
        for ball in root.balls_objective_list:
            dy=-1*ball[0][1]+self.pos[1]   # change to center_x
            dx=-1*ball[0][0]+self.pos[0]
            r2=dx**2+dy**2                                           
            ang=math.atan2(dy,dx) 
            r= math.sqrt(r2)
            if (r<=ball[1]):
                ball[4].bmove=True
                ball[4].brotate=True

                # TODO: rotation maths
                ball[4].brotate=False

                vang=math.atan2(self.speed[1], self.speed[0])
                dang=ang-vang
                cdang=math.cos(dang)
                dvCM=math.sqrt((self.speed[1]**2+self.speed[0]**2) * 1.0 * root.heavy_bullet_constant * (cdang ** 2) / ball[2])
                ball[4].speed[0]=ball[4].speed[0] - dvCM * math.cos(ang)
                ball[4].speed[1]=ball[4].speed[1] - dvCM * math.sin(ang)
                return 1
            
            a = ( root.gravity_constant * root.bullet_gravity_constant * ball[2] / float(r2) )
            ar[0] = ar[0] - a * math.cos(ang)
            ar[1] = ar[1] - a * math.sin(ang)
        # [ [ [center_x, center_y], radius, mass, density, widget_ref ] , ...]

        self.speed=[self.speed[0] + ar[0] * dt , self.speed[1] + ar[1] * dt ]
        
    
        if (self.pos[1]>1.2 * root.height) or (self.pos[1]< -0.2 * root.height):
            return 1
        elif self.pos[0]<-0.5 * root.width or self.pos[0]>root.width * 1.5:     # TODO: Physics!
            return 1
        return 0

class StrangeMatterBullet(BaseBullet):
    def update(self, root, dt):
        self.pos[0]=self.pos[0]+dt*self.speed[0]
        self.pos[1]=self.pos[1]+dt*self.speed[1]
        #self.draw_instruction.pos=self.pos        
        
        ar=[0, 0]
        for ball in root.balls_list:
            dy=-1*ball[0][1]+self.pos[1]
            dx=-1*ball[0][0]+self.pos[0]
            r2=dx**2+dy**2
            r= math.sqrt(r2) 
            if (r<=ball[1]):
                root.remove_widget(ball[4])
                root.balls_list.remove(ball)
                return 1

            
        for ball in root.balls_objective_list:
            dy=-1*ball[0][1]+self.pos[1]   # change to center_x
            dx=-1*ball[0][0]+self.pos[0]
            r2=dx**2+dy**2          
            r= math.sqrt(r2)
            if (r<=ball[1]):
                root.remove_widget(ball[4])
                root.balls_objective_list.remove(ball)
                return 2
            
        # [ [ [center_x, center_y], radius, mass, density, widget_ref ] , ...]

        
    
        if (self.pos[1]>1.2 * root.height) or (self.pos[1]< -0.2 * root.height):
            return 1
        elif self.pos[0]<-0.5 * root.width or self.pos[0]>root.width * 1.5:     # TODO: Physics!
            return 1
        return 0



class Planet(Widget):
    benemy=False
    bupdate= False
    radius= ObjectProperty(None)
    mass= ObjectProperty(None)
    '''
    def __init__ (self, **kwargs):
        super(Planet, self).__init__(**kwargs)
        self.mass=self.radius*self.radius*math.pi
    '''

class TurretBarrel(Widget):
    pass

class TurretBuilding(Widget):
    benemy=False
    bupdate=False
    pass

class TurretGun(Widget):
    benemy=False
    bupdate=True
    bullet_speed_factor=1.2
    bullet_damage_factor=2.0
    num_bullets_be_destroy=3
    num_heavy_bullets_to_destroy=0
    num_bulletsy_to_fire=3
    num_heavy_bullets_to_fire=0
    num_strange_bullets_to_fire=0
    num_strange_bullets_to_destroy=0
    current_ammo_type=0     # 0 - normall || 1 - heavy 
    num_ammo_types=3
    bshoot=False
    root_widget=ObjectProperty(None)
    rotate_instruction= ObjectProperty(None)
     
    def create_bullet_count(self, num_bullets_for_level=3, num_heavy_bullets=0, num_strange_bullets=0):
        self.num_bulletsy_to_fire=num_bullets_for_level
        self.num_bullets_be_destroy=num_bullets_for_level
        self.num_heavy_bullets_to_fire=num_heavy_bullets
        self.num_heavy_bullets_to_destroy=num_heavy_bullets
        self.num_strange_bullets_to_fire=num_strange_bullets
        self.num_strange_bullets_to_destroy=num_strange_bullets
    def on_touch_down(self, touch):
        
        if touch.y < self.y - self.barrel_length/2.0:
            if touch.is_double_tap:
                 # TODO:  
                if not (self.num_bulletsy_to_fire==0 and self.num_heavy_bullets_to_fire==0 and self.num_strange_bullets_to_fire==0):
                    self.current_ammo_type = (1 + self.current_ammo_type) % self.num_ammo_types
                    brotate=True
                    while brotate:
                        if self.current_ammo_type==0:
                            if self.num_bulletsy_to_fire==0:
                                self.current_ammo_type = (1 + self.current_ammo_type) % self.num_ammo_types
                            else:
                                brotate=False
                        elif self.current_ammo_type==1:
                            if self.num_heavy_bullets_to_fire==0:
                                self.current_ammo_type = (1 + self.current_ammo_type) % self.num_ammo_types
                            else:
                                brotate=False
                        elif self.current_ammo_type==2:
                            if self.num_strange_bullets_to_fire==0:
                                self.current_ammo_type = (1 + self.current_ammo_type) % self.num_ammo_types
                            else:
                                brotate=False
                self.root_widget.update_bullet_graphic_colors()
                #print "ammo type "+ str(self.current_ammo_type)
        elif touch.y >= self.y - self.barrel_length/2.0:
            self.touch=touch
            self.bshoot=True

            if self.touch.x-self.x==0:
                    self.ang= math.pi/2
         
            else:
                    frac=0.0
                    self.ang=math.atan2(self.touch.y*1.0-self.y , self.touch.x*1.0-self.x)
                    if self.ang < math.pi*frac and self.ang > -1*math.pi/2:
                        self.ang=math.pi*frac
                    elif self.ang > math.pi*(1-frac) or self.ang < -1*math.pi/2:
                        self.ang=math.pi*(1-frac)
            # ------------
            self.rotate_instruction.angle= self.ang * 180 / math.pi
            print ("{} - {}".format( touch.x*1.0/self.root_widget.width , touch.y*1.0/self.root_widget.height))
        
        return True
    def on_touch_up(self, touch):
        if self.bshoot:
            self.bshoot=False
            if (self.current_ammo_type==0 and self.num_bulletsy_to_fire>0) or (self.current_ammo_type==1 and self.num_heavy_bullets_to_fire>0) or (self.current_ammo_type==2 and self.num_strange_bullets_to_fire>0):
                 #!!
                factor=1
                if self.current_ammo_type==2:
                    factor=1.2
                speed=self.bullet_speed_factor*self.root_widget.width * factor
                s=math.sin(self.ang)
                c=math.cos(self.ang)
                root=self.root_widget
                if self.current_ammo_type==0: 
                    bull=Bullet([self.x+c*self.barrel_length,self.y+s*self.barrel_length], [speed*c,speed*s])
                    self.num_bulletsy_to_fire-=1
                    self.root_widget.normal_bullets_label.text=str(self.num_bulletsy_to_fire)
                    '''if root.main_app.bMute_SFX==False:
                        root.SFX_small_Bullets.play()
                    else:
                        if root.SFX_small_Bullets.state=='play':
                            root.SFX_small_Bullets.stop()'''
                elif self.current_ammo_type==1: 
                    bull=HeavyBullet([self.x+c*self.barrel_length,self.y+s*self.barrel_length], [speed*c,speed*s])
                    self.num_heavy_bullets_to_fire-=1
                    self.root_widget.heavy_bullets_label.text=str(self.num_heavy_bullets_to_fire) 
                    '''if root.main_app.bMute_SFX==False:
                        root.SFX_Heavy_Bullets.play()
                    else:
                        if root.SFX_Heavy_Bullets.state=='play':
                            root.SFX_Heavy_Bullets.stop()'''
                elif self.current_ammo_type==2: 
                    bull=StrangeMatterBullet([self.x+c*self.barrel_length,self.y+s*self.barrel_length], [speed*c,speed*s])
                    self.num_strange_bullets_to_fire-=1
                    
                    self.root_widget.strange_bullet_label.text=str(self.num_strange_bullets_to_fire)
                    '''
                    if root.main_app.bMute_SFX==False:
                        root.SFX_strange_bullets.play()
                    else:
                        if root.SFX_strange_bullets.state=='play':
                            root.SFX_strange_bullets.stop()'''
                    

                self.root_widget.turret_gun.add_widget(bull)

        return True

    def update(self,dt):
       # if hasattr(self, 'touch'):
         #   print(self.touch.pos)
        
        if self.bshoot:
            
            if self.touch.x-self.x==0:
                self.ang= math.pi/2
         
            else:
                frac=0.0
                self.ang=math.atan2(self.touch.y*1.0-self.y , self.touch.x*1.0-self.x)
                if self.ang < math.pi*frac and self.ang > -1*math.pi/2:
                    self.ang=math.pi*frac
                elif self.ang > math.pi*(1-frac) or self.ang < -1*math.pi/2:
                    self.ang=math.pi*(1-frac)

            self.rotate_instruction.angle= self.ang * 180 / math.pi
            return 0


class BallBase(Widget): #TODO : clean up atributtes
    bmove=False
    brotate=False
    benemy=True
    mass=0
    radius=0
    speed=0
    rotation_speed=0
    rect=ObjectProperty(None)
    def __init__ (self, root, ball_size, ball_position, density, **kwargs):
        self.ball_size=ball_size
        self.ball_position=ball_position
        self.density= density
        self.speed=[0,0]
        super(BallBase, self).__init__(**kwargs)
        self.update_pos(root.main_app.root)
        
    def update_pos (self, root):
        diam=self.ball_size*root.width
        self.radius=diam/2
        self.mass=((diam/2)**3) * math.pi * 4 / 3 * self.density
        
        self.size=(diam,diam)
        self.center=root.width* self.ball_position[0],root.height* self.ball_position[1]
        self.pos=[self.center[0]-self.radius,self.center[1]-self.radius]
    def move(self, planet_in_list, root, dt):

        

        self.pos[0]=self.pos[0]+dt*self.speed[0]
        self.pos[1]=self.pos[1]+dt*self.speed[1]
        planet_in_list[0][0]=self.pos[0]+self.radius
        planet_in_list[0][1]=self.pos[1]+self.radius
        self.rect.pos=self.pos
        self.rot.origin=(self.pos[0] + self.radius, self.pos[1] + self.radius)

        if (self.pos[1]>1.3 * root.height) or (self.pos[1]< -0.3 * root.height):
            if isinstance(self, Objective_Ball):
                return 3
            return 1
        elif self.pos[0]<-0.2 * root.width or self.pos[0]>root.width * 1.2:     # TODO: Physics!
            if isinstance(self, Objective_Ball):
                return 3
            return 1
       

        factor_for_dvCM= 1.0/3
        radiusmult= 2
        ar=[0, 0]
        for ball in root.balls_list + root.balls_objective_list:
            if ball[4] != self:
                dy=-1*ball[0][1]+self.pos[1] + self.radius
                dx=-1*ball[0][0]+self.pos[0] + self.radius
                r2=dx**2+dy**2
                r= math.sqrt(r2) 
                ang=math.atan2(dy,dx) 
                if (r <= radiusmult * ( ball[1] + self.radius)): # whitin gravitation range
                    ball[4].bmove=True
                    if (r <= ( ball[1] + self.radius)): # planet collision
                        delta= math.sqrt( (-1* r**3 + 4 * ((ball[2] * 1.0 / ball[3] + self.mass * 1.0 / self.density)/(4.0/3*math.pi))) / (3 * r) )
                        rbigger= 0.5 * (r + delta)
                        rsmaller= r - rbigger
                        if (rsmaller < root.smallest_poss_planet_radius):
                            rsmaller = 0.0
                            rbigger = ( (ball[2] * 1.0 / ball[3] + self.mass * 1.0 / self.density)/(4.0/3*math.pi) ) ** (1.0/3)
                        if (self.radius >= ball[1]):
                            
                            volbigger= rbigger**3 * 4.0/3 * math.pi
                            massbigger= volbigger * self.density
                            voltransfer = volbigger - self.mass * 1.0 / self.density
                            masstransfer= voltransfer * ball[3]

                            vang=math.atan2(ball[4].speed[1] , ball[4].speed[0])
                            dang=ang-vang
                            cdang=math.cos(dang)
                            dvCM=math.sqrt((ball[4].speed[1]**2+ball[4].speed[0]**2) * 1.0 * masstransfer * (cdang ** 2) / self.mass) * factor_for_dvCM
                            ratmass= math.sqrt(self.mass * 1.0 /massbigger)
                            self.speed[0] = (self.speed[0] + dvCM * math.cos(ang) ) * ratmass
                            self.speed[1] = (self.speed[1] + dvCM * math.sin(ang) ) * ratmass

                            self.mass= massbigger
                            planet_in_list[2]=massbigger
                            ball[2]= (rsmaller ** 3) * 4.0 / 3 * math.pi * ball[3]
                            
                            ball[4].mass= ball[2]
                            biggersize= rbigger * 1.0 / self.radius * self.rect.size[0]
                            biggersize1= (biggersize, biggersize)
                            self.size= biggersize1
                            self.rect.size= biggersize1

                            smallersize= rsmaller * 1.0 / ball[1] * ball[4].rect.size[0]
                            smallersize1= (smallersize, smallersize)
                            ball[4].size= smallersize1
                            ball[4].rect.size= smallersize1

                            self.radius= rbigger
                            planet_in_list[1]= rbigger
                            ball[4].radius= rsmaller
                            ball[1]= rsmaller

                        else: # ball bigger than self
                            volbigger= rbigger**3 * 4.0/3 * math.pi
                            massbigger= volbigger * ball[3]
                            voltransfer = volbigger - ball[2] * 1.0 / ball[3]
                            masstransfer= voltransfer * self.density

                            vang=math.atan2(self.speed[1] , self.speed[0])
                            dang=vang - ang
                            cdang=math.cos(dang)
                            dvCM=math.sqrt((self.speed[1]**2+self.speed[0]**2) * 1.0 * masstransfer * (cdang ** 2) / ball[2]) * factor_for_dvCM
                            ratmass= math.sqrt(ball[2] * 1.0 /massbigger)
                            ball[4].speed[0] = (ball[4].speed[0] - dvCM * math.cos(ang) ) * ratmass
                            ball[4].speed[1] = (ball[4].speed[1] - dvCM * math.sin(ang) ) * ratmass

                            ball[4].mass= massbigger
                            ball[2]= massbigger
                            self.mass= (rsmaller ** 3) * 4.0 / 3 * math.pi * self.density
                            planet_in_list[2]=self.mass

                            smallersize= rsmaller * 1.0 / self.radius * self.rect.size[0] 
                            smallersize1= (smallersize, smallersize)
                            self.size= smallersize1
                            self.rect.size= smallersize1

                            biggersize= rbigger * 1.0 / ball[1] * ball[4].rect.size[0]
                            biggersize1= (biggersize, biggersize)
                            ball[4].size= biggersize1
                            ball[4].rect.size= biggersize1

                            self.radius= rsmaller
                            planet_in_list[1]=rsmaller
                            ball[4].radius= rbigger
                            ball[1]= rbigger

                              # [ [ [center_x, center_y], radius, mass, density, widget_ref ] , ...]
                            
                    if ball[1]< root.smallest_poss_planet_radius:

                        if ball in root.balls_objective_list:
                            root.remove_widget(ball[4])
                            root.balls_objective_list.remove(ball)
                            root.num_objective_balls-=1
                            
                        else:
                            root.remove_widget(ball[4])
                            root.balls_list.remove(ball)
                    else:
                        a = ( root.gravity_constant * ball[2] / float(r2) )  # TODO delete ball[3]
                        ar[0] = ar[0] - a * math.cos(ang)
                        ar[1] = ar[1] - a * math.sin(ang)
            
        # [ [ [center_x, center_y], radius, mass, density, widget_ref ] , ...]
        

        if self.radius < root.smallest_poss_planet_radius:
            return 1

        self.speed=[self.speed[0] + ar[0] * dt , self.speed[1] + ar[1] * dt ]
        return 0
    
    def colors_and_rotation(self):
        pass
        '''
        with self.canvas.before:
            PushMatrix()
            Rotate (angle= random()*360, origin= self.center)  # TODO breaks the code
            PopMatrix()
        
        with self.canvas.before:
                PushMatrix()
                #Rotate (angle= random()*360, origin= self.center)  # TODO breaks the code
                #Color(0.9375, 0.9375, 0.3671875)
        with self.canvas.after:
                PopMatrix()
        '''
class Base_Enemy(BallBase):
    bbase_enemy_ball=True
    def __init__ (self, root, ball_size, ball_position, density, **kwargs):
        super(Base_Enemy, self).__init__(root, ball_size, ball_position, density, **kwargs)
        rand=random()
        s=''
        if root.main_app.bArt_White:
            s='_w'
        else:
            s=str(randint(1,root.main_app.number_of_planets))
        with self.canvas: 
            PushMatrix()
            self.rot=Rotate (angle= rand*360, origin= self.center)  # TODO breaks the code
            self.rect=Rectangle(source= 'Resources/balls/e' + s + '.png',	pos=self.pos, size= self.size)
            PopMatrix()
        
class Objective_Ball(BallBase):
    bbase_objective_ball=True
    def __init__ (self, root, ball_size, ball_position, density, **kwargs):
        super(Objective_Ball, self).__init__(root, ball_size, ball_position, density, **kwargs)
        rand=random()
        s=''
        if root.main_app.bArt_White:
            s='_w'
        else:
            s=str(randint(1,root.main_app.number_of_planets))
        with self.canvas:
            PushMatrix()
            self.rot=Rotate (angle= rand*360, origin= self.center)  # TODO breaks the code
            self.rect=Rectangle(source= 'Resources/balls/o' + s + '.png', pos=self.pos, size= self.size)
            PopMatrix()

class GameWidget(Widget):
    main_app=None
    turret_gun= ObjectProperty(None)
    balls_list=[]  # [ [ [center_x, center_y], radius, mass, widget_ref ] , ...]
                   #      [i][0][0], [i][0][1], [i][1], [i][2], [i][3]
    balls_objective_list=[]  # [ [ [center_x, center_y], radius, mass, widget_ref ] , ...]
    gravity_constant=50.0 / 4
    bullet_gravity_constant= 1.0 * 4
    main_planet= ObjectProperty(None)
    current_level=0
    turret_building= ObjectProperty(None)
    num_objective_balls=0
    heavy_bullet_constant=900.0
    smallest_poss_planet_radius= 0.75
    SFX_small_Bullets=None
    SFX_Heavy_Bullets=None
    SFX_strange_bullets= None
    sounds=None
    count=0
    count2=0
    normal_bullets_label= None
    heavy_bullets_label= None
    heavy_bullet_graphic= None
    strange_bullet_label= None
    strange_bullet_graphic= None
    def __init__(self,**kwargs):
        super(GameWidget, self).__init__(**kwargs)    
          # ---- SFX sound
        
        #self.SFX_small_Bullets = SoundSDL2(source= 'Resources/audio/bullet_SFX.mp3')
        #self.SFX_Heavy_Bullets = SoundSDL2(source= 'Resources/audio/Heavy_Bullet_SFX.mp3')
        #self.SFX_strange_bullets= SoundSDL2(source= 'Resources/audio/strange_bullet_SFX.mp3')
        

        #self.bind(size=self.update_balls_pos)
    '''
    def update_balls_pos(self, obj, value):
        for child in self.children:
            if child.bbase_objective_ball or child.bbase_enemy_ball: 
                child.update_pos(self)
                #[[child.center_x,child.center_y], child.radius, child.mass, 1.0, child]
        
        for i in range(len(self.balls_list)):
            self.balls_list[i]=[[self.balls_list[i][4].center_x, self.balls_list[i][4].center_y], self.balls_list[i][4].radius, self.balls_list[i][4].mass, self.balls_list[i][4].density, self.balls_list[i][4]]
                
        for i in range(len(self.balls_objective_list)):
            self.balls_objective_list[i]=[[self.balls_objective_list[i][4].center_x, self.balls_objective_list[i][4].center_y], self.balls_objective_list[i][4].radius, self.balls_objective_list[i][4].mass, self.balls_objective_list[i][4].density, self.balls_objective_list[i][4]]
    '''   
    def update_bullet_graphic_colors(self): 
        if self.turret_gun.current_ammo_type==0:
            with self.normal_bullet_graphic.canvas.before:
                PushMatrix()
                Color(0.9375, 0.9375, 0.3671875)
            with self.normal_bullet_graphic.canvas.after:
                PopMatrix()
            if self.heavy_bullet_graphic != None:
                self.heavy_bullet_graphic.canvas.before.clear()
                self.heavy_bullet_graphic.canvas.after.clear()
            if self.strange_bullet_graphic!= None:
                self.strange_bullet_graphic.canvas.before.clear()
                self.strange_bullet_graphic.canvas.after.clear()

        elif self.turret_gun.current_ammo_type==1 and self.heavy_bullet_graphic != None:
            with self.heavy_bullet_graphic.canvas.before:
                PushMatrix()
                Color(0.9375, 0.9375, 0.3671875)
            with self.heavy_bullet_graphic.canvas.after:
                PopMatrix()
            self.normal_bullet_graphic.canvas.before.clear()
            self.normal_bullet_graphic.canvas.after.clear()
            if self.strange_bullet_graphic!= None:
                self.strange_bullet_graphic.canvas.before.clear()
                self.strange_bullet_graphic.canvas.after.clear()

        elif self.turret_gun.current_ammo_type==2 and self.strange_bullet_graphic!= None:
            with self.strange_bullet_graphic.canvas.before:
                PushMatrix()
                Color(0.9375, 0.9375, 0.3671875)
            with self.strange_bullet_graphic.canvas.after:
                PopMatrix()
            self.normal_bullet_graphic.canvas.before.clear()
            self.normal_bullet_graphic.canvas.after.clear()
            if self.heavy_bullet_graphic != None:
                self.heavy_bullet_graphic.canvas.before.clear()
                self.heavy_bullet_graphic.canvas.after.clear()

    def update(self, dt):
        #print len(self.balls_list)
        '''
        str1=""
        for ball in self.balls_list + self.balls_objective_list:
            str1= str1 + "vx= " + str(ball[4].speed[0]) + "   " + "vy= " + str(ball[4].speed[1]) + " ||| "
        print str1
        '''

        for bullet in self.turret_gun.children:
            
            ret=bullet.update(self,dt)
            if ret==1:   # just remove bullet --------------------------------------------------------------------------------
                self.turret_gun.remove_widget(bullet)
                if isinstance(bullet, Bullet):
                    self.turret_gun.num_bullets_be_destroy-=1
                elif isinstance(bullet, HeavyBullet):
                    self.turret_gun.num_heavy_bullets_to_destroy-=1
                elif isinstance(bullet, StrangeMatterBullet):
                    self.turret_gun.num_strange_bullets_to_destroy-=1
                #print "bullets to destroy " + str(self.turret_gun.num_bullets_be_destroy) + " bullets left " + str(self.turret_gun.num_bulletsy_to_fire)
                

            elif ret==2:  # hit objectve, objective ball removed in other function  --------------------------------------------------------------------------------
                self.turret_gun.remove_widget(bullet)
                self.num_objective_balls-=1
                if isinstance(bullet, Bullet):
                    self.turret_gun.num_bullets_be_destroy-=1
                elif isinstance(bullet, StrangeMatterBullet):
                    self.turret_gun.num_strange_bullets_to_destroy-=1
                if self.num_objective_balls<=0:
                    self.main_app.destroy_level()
                    if self.current_level == self.main_app.beat_to_the_level:
                        self.main_app.beat_to_the_level += 1
                        num=self.main_app.beat_to_the_level
                        with open('saves.txt','w') as filemap:
                            str1=""
                            if num < 10:
                                str1= "0"
                            str1+=str(num)
                            filemap.write(str1)
                    if self.current_level==20:
                        self.main_app.screen_manager.current="level_won_screen_end"
                        self.main_app.dict_space_backgrounds['won_end'].rotate()
                    else:
                        self.main_app.screen_manager.current="level_won_screen"
                        self.main_app.dict_space_backgrounds['won'].rotate()
                #print "Won the level"



    def update_balls(self,dt):
        #dt=dt/4.0
        '''
        self.count+=dt
        self.count2= (self.count2+1)%120
        print(str(self.count) + " " + str(self.count2))
        '''
        bMovement=False
        for planet in self.balls_list:
            if planet[4].bmove:
                bMovement=True
                ret=planet[4].move(planet, self, dt)
                if ret==1:  #remove planet
                    self.remove_widget(planet[4])
                    self.balls_list.remove(planet)
            if planet[4].brotate:
                pass
        for planet in self.balls_objective_list:
            if planet[4].bmove:
                bMovement=True
                ret=planet[4].move(planet, self, dt)
                if ret==1:  #remove planet
                    self.remove_widget(planet[4])
                    self.balls_objective_list.remove(planet)
                    self.num_objective_balls-=1
                if ret==3:
                    self.main_app.dict_space_backgrounds['lost2'].rotate()
                    self.main_app.screen_manager.current="level_lost_screen_2"
                    self.main_app.destroy_level()
            if planet[4].brotate:
                pass

        if self.num_objective_balls<=0:
                self.main_app.destroy_level()
                if self.current_level == self.main_app.beat_to_the_level:
                        self.main_app.beat_to_the_level += 1
                        num=self.main_app.beat_to_the_level
                        with open('saves.txt','w') as filemap:
                            str1=""
                            if num < 10:
                                str1= "0"
                            str1+=str(num)
                            filemap.write(str1)
                if self.current_level==20:
                    self.main_app.screen_manager.current="level_won_screen_end"
                    self.main_app.dict_space_backgrounds['won_end'].rotate()
                else:
                    self.main_app.screen_manager.current="level_won_screen"
                    self.main_app.dict_space_backgrounds['won'].rotate()
                

        elif self.turret_gun.num_bullets_be_destroy<=0 and self.turret_gun.num_heavy_bullets_to_destroy<=0 and self.turret_gun.num_strange_bullets_to_destroy<=0 and bMovement==False:
                    self.main_app.dict_space_backgrounds['lost'].rotate()
                    self.main_app.screen_manager.current="level_lost_screen" 
                    self.main_app.destroy_level()

    def create_ball (self, type, size_frac, pos_frac_tuple, speed_tuple=None):
        if type=="base_enemy":
            base=Base_Enemy(self, size_frac, pos_frac_tuple, 1.0)
            if speed_tuple != None:
                base.speed=[speed_tuple[0] * self.width, speed_tuple[1] * self.width]
                base.bmove=True
            self.add_widget(base)
            self.balls_list.append([[base.center_x, base.center_y], base.radius, base.mass, base.density, base])
        if type=="base_objective":
            base=Objective_Ball(self, size_frac, pos_frac_tuple, 1.0)
            if speed_tuple != None:
                base.bmove=True
                base.speed=[speed_tuple[0] * self.width, speed_tuple[1] * self.width]
            self.add_widget(base)
            self.balls_objective_list.append([[base.center_x, base.center_y], base.radius, base.mass, base.density, base])
    def schedule_enemies(self):
        #            ( "enemy type", diameter= number*width , (width* number, heigth * number) )
        if self.current_level==3:
            self.create_ball("base_enemy", 0.22, (0.5, 0.5))
            self.create_ball("base_enemy", 0.15, (0.2, 0.25))
            self.create_ball("base_enemy", 0.15, (0.8, 0.25))
            self.create_ball("base_enemy", 0.15, (0.2, 0.75))
            self.create_ball("base_enemy", 0.15, (0.8, 0.75))
            self.num_objective_balls=1
            self.create_ball("base_objective", 0.17, (0.5, 0.9))

        elif self.current_level==1:
            self.turret_gun.create_bullet_count(9)
            self.create_ball("base_enemy", 0.25, (0.2, 0.8)) 
            self.num_objective_balls=1
            self.create_ball("base_objective", 0.25, (0.8, 0.8))

        elif self.current_level==2:
            self.turret_gun.create_bullet_count(5)
            self.create_ball("base_enemy", 0.2, (0.5, 0.65))
            self.create_ball("base_enemy", 0.2, (0.5, 0.35))
            self.num_objective_balls=1
            self.create_ball("base_objective", 0.2, (0.5, 0.9))
            
        elif self.current_level==4:
            self.turret_gun.create_bullet_count(5)
            self.create_ball("base_enemy", 0.2, (0.25, 0.71))
            self.create_ball("base_enemy", 0.2, (1-0.25, 0.71))
            #self.create_ball("base_enemy", 0.25, (0.5, 0.65))
            self.create_ball("base_enemy", 0.3, (0.85, 0.4))
            self.create_ball("base_enemy", 0.3, (0.15, 0.4))
            self.num_objective_balls=2
            self.create_ball("base_objective", 0.15, (0.15, 0.9))
            self.create_ball("base_objective", 0.15, (0.85, 0.9))

        elif self.current_level==5:
            self.turret_gun.create_bullet_count(5)
            self.create_ball("base_enemy", 0.23, (0.5, 0.35))
            self.create_ball("base_enemy", 0.23, (0.5, 0.7))
            
            self.num_objective_balls=2
            self.create_ball("base_objective", 0.1, (0.5, 0.92))
            self.create_ball("base_objective", 0.1, (0.5, 0.52))
        
        elif self.current_level==6:
            self.turret_gun.create_bullet_count(7)
            self.create_ball("base_enemy", 0.23, (0.5, 0.7))
            self.create_ball("base_enemy", 0.23, (0.15, 0.4))
            self.create_ball("base_enemy", 0.23, (0.85, 0.4))

            self.num_objective_balls=3
            self.create_ball("base_objective", 0.15, (0.1, 0.65))
            self.create_ball("base_objective", 0.15, (0.9, 0.65))        
            self.create_ball("base_objective", 0.15, (0.5, 0.92))        
        
        elif self.current_level==7:
            self.turret_gun.create_bullet_count(7)
            self.create_ball("base_enemy", 0.18, (0.5, 0.8))
            self.create_ball("base_enemy", 0.18, (0.1, 0.8))
            self.create_ball("base_enemy", 0.4, (1.0, 0.5))

            self.num_objective_balls=2
            self.create_ball("base_objective", 0.12, (0.3, 0.8))
            self.create_ball("base_objective", 0.12, (0.7, 0.8))        
        
        elif self.current_level==8:
            self.turret_gun.create_bullet_count(1,3)
            self.create_ball("base_enemy", 0.2, (0.5, 0.7))
            self.create_ball("base_enemy", 0.2, (0.9, 0.64))
            self.create_ball("base_enemy", 0.2, (0.1, 0.64))
            
            self.create_ball("base_enemy", 0.2, (0.3, 0.42))
            self.create_ball("base_enemy", 0.2, (0.7, 0.42))

            self.num_objective_balls=1
            
            self.create_ball("base_objective", 0.15, (0.5, 0.9))        
 
        elif self.current_level==9:
            self.turret_gun.create_bullet_count(3,2)
            self.create_ball("base_enemy", 0.14, (-0.25, 0.5))
            self.create_ball("base_enemy", 0.14, (0.05, 0.5))
            self.create_ball("base_enemy", 0.14, (0.35, 0.5))
            self.create_ball("base_enemy", 0.14, (0.65, 0.5))
            self.create_ball("base_enemy", 0.14, (0.95, 0.5))
            self.create_ball("base_enemy", 0.14, (1.25, 0.5))

            self.create_ball("base_enemy", 0.14, (-0.1, 0.66))
            self.create_ball("base_enemy", 0.14, (0.2, 0.66))
            self.create_ball("base_enemy", 0.14, (0.5, 0.66))
            self.create_ball("base_enemy", 0.14, (0.8, 0.66))
            self.create_ball("base_enemy", 0.14, (1.1, 0.66))

            self.create_ball("base_enemy", 0.14, (-0.1, 0.34))
            self.create_ball("base_enemy", 0.14, (0.2, 0.34))
            self.create_ball("base_enemy", 0.14, (0.5, 0.34))
            self.create_ball("base_enemy", 0.14, (0.8, 0.34))
            self.create_ball("base_enemy", 0.14, (1.1, 0.34))

            self.num_objective_balls=1
            
            self.create_ball("base_objective", 0.15, (0.5, 0.9))    
            
        elif self.current_level==10:
            self.turret_gun.create_bullet_count(3,2)
            self.create_ball("base_enemy", 0.15, (0.6, 0.7))

            self.create_ball("base_enemy", 0.32, (1.22, 0.4))

            self.create_ball("base_enemy", 0.24, (0.7, 0.4))

            self.num_objective_balls=1
            
            self.create_ball("base_objective", 0.14, (0.9, 0.8))       
 
        elif self.current_level==11:
            self.turret_gun.create_bullet_count(3,2)
            self.create_ball("base_enemy", 0.2, (0.19, 0.6))
            self.create_ball("base_enemy", 0.2, (0.81, 0.6))

            self.create_ball("base_enemy", 0.12, (0.5, 0.4))

            self.num_objective_balls=1
            
            self.create_ball("base_objective", 0.10, (0.5, 0.9))        

        elif self.current_level==12:
            self.turret_gun.create_bullet_count(5)
            self.create_ball("base_enemy", 0.15, (0.2, 0.75))
            self.create_ball("base_enemy", 0.2, (0.8, 0.55))

            self.create_ball("base_enemy", 0.2, (0.4, 0.35))

            self.num_objective_balls=1
            
            self.create_ball("base_objective", 0.10, (0.7, 0.95))        

        elif self.current_level==13:
            self.turret_gun.create_bullet_count(0,2)
            self.create_ball("base_enemy", 0.2, (0.1, 0.65))
            self.create_ball("base_enemy", 0.2, (0.9, 0.65))

            self.create_ball("base_enemy", 0.2, (0.27, 0.4))
            self.create_ball("base_enemy", 0.2, (0.73, 0.4))

            self.create_ball("base_enemy", 0.2, (0.5, 0.6))

            self.num_objective_balls=1
            
            self.create_ball("base_objective", 0.30, (0.5, 0.95))        

        elif self.current_level==14:
            self.num_objective_balls=4
            
            self.turret_gun.create_bullet_count(1,2)
            self.create_ball("base_objective", 0.35, (0.5, 0.75))
            self.create_ball("base_objective", 0.15, (0.9, 0.57))

            
            self.create_ball("base_objective", 0.15, (0.13, 0.95))

            self.create_ball("base_objective", 0.2, (0.35, 0.4))
        
        elif self.current_level==15:
            self.turret_gun.create_bullet_count(1,2)
            self.create_ball("base_enemy", 0.2, (0.5, 0.4))
            
             
            self.num_objective_balls=3
            self.create_ball("base_objective", 0.15, (0.15, 0.9))  
            self.create_ball("base_objective", 0.15, (0.85, 0.9))
            self.create_ball("base_objective", 0.2, (0.5, 0.7))

        elif self.current_level==16:
            self.turret_gun.create_bullet_count(3,0,2)
            self.create_ball("base_enemy", 0.5, (0.0, 0.5))

            self.num_objective_balls=1
            self.create_ball("base_objective", 0.2, (0.7, 0.9))

        elif self.current_level==17:
            self.turret_gun.create_bullet_count(3,0,1)
            self.create_ball("base_enemy", 0.2, (0.1, 0.7))
            self.create_ball("base_enemy", 0.2, (0.9, 0.7))

            self.create_ball("base_enemy", 0.35, (0.5, 0.5))

            self.num_objective_balls=1
            
            self.create_ball("base_objective", 0.20, (0.5, 0.9))        

        elif self.current_level==18:
            self.turret_gun.create_bullet_count(3,0,1)
            self.create_ball("base_enemy", 0.3, (0.7, 0.6))
            self.create_ball("base_enemy", 0.4, (0.0, 0.4))
            self.create_ball("base_enemy", 0.2, (0.2, 0.7))

            self.num_objective_balls=1
            
            self.create_ball("base_objective", 0.20, (0.5, 0.95))  

        elif self.current_level==19:
            self.turret_gun.create_bullet_count(0,2,1)
            self.create_ball("base_enemy", 0.17, (0.55, 0.35))
            self.create_ball("base_enemy", 0.17, (0.55, 0.75))
             
            self.num_objective_balls=2
            self.create_ball("base_objective", 0.2, (0.35, 0.55))  
            self.create_ball("base_objective", 0.2, (0.75, 0.95))  
            
        elif self.current_level==20:
            self.turret_gun.create_bullet_count(3,0,1)
            self.create_ball("base_enemy", 0.17, (0.1, 0.4))
            self.create_ball("base_enemy", 0.17, (0.9, 0.4))
             
            self.create_ball("base_enemy", 0.3, (0.5, 0.5))
            self.create_ball("base_enemy", 0.3, (0.5, 0.75))

            self.num_objective_balls=1
            self.create_ball("base_objective", 0.15, (0.5, 0.97))   

        elif self.current_level==24:
            self.turret_gun.create_bullet_count(3,0,3)
            self.create_ball("base_enemy", 0.1, (0.5, 0.3))
            self.create_ball("base_enemy", 0.3, (0.5, 0.6))
            self.create_ball("base_enemy", 0.2, (0.3, 0.9))
            self.num_objective_balls=2
            self.create_ball("base_objective", 0.2, (0.3, 0.7))
        
        elif self.current_level==25:
            self.turret_gun.create_bullet_count(3,3,3)
            self.create_ball("base_enemy", 0.1, (0.5, 0.3))
            self.create_ball("base_enemy", 0.3, (0.5, 0.6))
            self.create_ball("base_enemy", 0.2, (0.3, 0.9))
            self.num_objective_balls=2
            self.create_ball("base_objective", 0.2, (0.3, 0.7))

class GameApp(App):
    game_widget= ObjectProperty(None)
    screen_manager= ObjectProperty(None)
   # level_selection_gridlayout= ObjectProperty(None)
    num_buttons=20
    bcreated_first_level=False
    list_clock_repeat_schedule=[0,0,0]
    refresh_rate=1.0/60
    refresh_rate_balls_physics= 1.0/60
    beat_to_the_level=0
    bMute_SFX=False  # mute all sounds
    bMute_soundtrack=False
    list_soundtracks=[]
    settings_screen= None
    number_of_backgrounds=6
    number_of_planets=5
    dict_space_backgrounds={}
    bArt_White= True
    bFPS_60T_30F= True
    conf=Config
    def build(self): 
        self.icon= 'WEB_icon.png'
        self.title= 'Space Ballistics'
        self.use_kivy_settings=False


        background_randint= randint(1,self.number_of_backgrounds)
        background_float0to1= random()
        planet_background_randint=0
        planet_background_float0to1=0

        with open('saves.txt','r') as filemap:
            filelines=filemap.readlines()
        self.beat_to_the_level= int(filelines[0][:2])

        sm = ScreenManager(transition=FadeTransition())
        self.screen_manager=sm

        start_screen=StartScreen(name='start_menu')
        if self.beat_to_the_level == 0:
            start_screen.game_button.text='New Game'
        self.button_text=start_screen.game_button
        planet_background=Planet_Background(self,planet_background_randint, planet_background_float0to1)
        sm.bind(size=planet_background.update_pos)
        start_screen.add_widget(planet_background,10)
        sm.add_widget(start_screen)
        

        
        self.settings_screen=SettingsScreen(name='settings')
        planet_background=Planet_Background(self,planet_background_randint, planet_background_float0to1)
        sm.bind(size=planet_background.update_pos)
        self.settings_screen.add_widget(planet_background, 10)
        sm.add_widget(self.settings_screen)

        #self.settings_screen.checkbox_Music.bind(active=self.checkbox.settings_screen.)

        level_selection=LevelSelectionScreen(name='level_selection')

        planet_background=Planet_Background(self,planet_background_randint, planet_background_float0to1)
        sm.bind(size=planet_background.update_pos)
        level_selection.add_widget(planet_background, 10)
       # self.level_selection_gridlayout=level_selection.gridlayout
        self.button_grid=level_selection.gridlayout
        for i in range(1,self.num_buttons+1):
            button=LevelSelectionButton()
            button.level=i
            button.text=str(i)
            button.main_app=self 
            level_selection.gridlayout.add_widget(button)
    
        

        sm.add_widget(level_selection)
        gamescreen=GameScreen(name='game_screen')
        space_background=Space_Background(self)
        sm.bind(size=space_background.update_pos)
        gamescreen.add_widget(space_background, 10)
        gamescreen.space_background=space_background
        self.screen_game=gamescreen
        game=GameWidget()
        self.game_widget=game
        game.main_app=self
        
        gamescreen.add_widget(game)
        sm.add_widget(gamescreen)

        level_won_screen=LevelWonScreen(name='level_won_screen')
        space_background=Space_Background(self, background_randint, background_float0to1)
        sm.bind(size=space_background.update_pos)
        level_won_screen.add_widget(space_background, 10)
        sm.add_widget(level_won_screen)
        self.dict_space_backgrounds['won']=space_background
        
        level_won_screen_end=LevelWonScreenEnd(name='level_won_screen_end')
        space_background=Space_Background(self, background_randint, background_float0to1)
        sm.bind(size=space_background.update_pos)
        level_won_screen_end.add_widget(space_background, 10)
        sm.add_widget(level_won_screen_end)
        self.dict_space_backgrounds['won_end']=space_background

        level_lost_screen=LevelLostScreen(name='level_lost_screen')
        space_background=Space_Background(self, background_randint, background_float0to1)
        sm.bind(size=space_background.update_pos)
        level_lost_screen.add_widget(space_background, 10)
        sm.add_widget(level_lost_screen)
        self.dict_space_backgrounds['lost']=space_background

        lost2=LevelLostScreen2(name='level_lost_screen_2')
        lost2.lost_label.text="Level Lost:\nPlanet out of range"
        space_background=Space_Background(self, background_randint, background_float0to1)
        sm.bind(size=space_background.update_pos)
        lost2.add_widget(space_background, 10)
        self.dict_space_backgrounds['lost2']=space_background
        sm.add_widget(lost2)

        EventLoop.window.bind(on_keyboard=self.hook_keyboard)

        #sm.current = "game_screen"
        # TODO
        
        game.screen_manager=sm

        if self.beat_to_the_level==0:
            self.beat_to_the_level=1
            with open('saves.txt','w') as filemap:
                filemap.write('01')

        self.update_button_colors()
        # audio soundtrack
        #self.list_soundtracks.append(SoundSDL2(source= 'Resources/audio/chimes_soundtrack.mp3'))
        #self.list_soundtracks.append(SoundSDL2(source= 'Resources/audio/Chimera.mp3'))
        #self.soundtrack_position= randint(0,len(self.list_soundtracks)-1)
        #Clock.schedule_interval(self.update_soundtrack_music, 1.0 / 2)
        #self.update_soundtrack_music()

        return sm

    def on_pause(self):
        return True
    
    #def update_soundtrack_music (self):
     #   if self.bMute_soundtrack==False:
      #      if self.list_soundtracks[self.soundtrack_position].state!="play":
       #         self.soundtrack_position= (self.soundtrack_position+1) % len(self.list_soundtracks)
        #        self.list_soundtracks[self.soundtrack_position].play()
       # else:
        #    if self.list_soundtracks[self.soundtrack_position].state=="play":
         #       self.list_soundtracks[self.soundtrack_position].stop()
                #self.soundtrack_position= (self.soundtrack_position+1) % len(self.list_soundtracks)
                

    def update_button_colors(self):
        
        for button in self.button_grid.children:
            if button.level <= self.beat_to_the_level:
                button.disabled=False
            else:    
                button.disabled=True
            '''
            if button.level <= self.beat_to_the_level:
                button.background_color= (0,1,0,1)
            else:    
                button.background_color= (1,0,0,1)
            '''
    def destroy_level(self):
        if self.bcreated_first_level==True:
            
            #self.game_widget.current_level=0
           
            for event in self.list_clock_repeat_schedule:
                Clock.unschedule(event)
            self.game_widget.balls_list=[]
            self.game_widget.balls_objective_list=[]
            self.game_widget.clear_widgets()
            
    def create_planet_and_turret(self, type):
            
            if type == "flat":
                planet=Planet()

                '''
                planet.pos= 0, 0
                planet.size= self.root.width,self.root.width * 0.212037037 
                with planet.canvas:
                    Rectangle(source= 'Resources/Spaceship.png', pos= planet.pos, size= planet.size)
                '''

                planet.pos= 0, 0   #-self.root.width/ 20.0
                planet.size= self.root.width,self.root.width * 2.5 / 9
                planet.radius= planet.width/2
                planet.mass= (planet.width**3.0) / 8 * 3.141593 * 4 / 3 
                s=''
                if self.bArt_White:
                    s='_w'
                with planet.canvas:
                    Rectangle(source= 'Resources/planet'+s+'.png', pos= planet.pos, size= planet.size)
                    
                self.game_widget.main_planet=planet
                


                turret_building=TurretBuilding()
                turret_building.pos= planet.center_x-planet.width/7, planet.width/5.4
                turret_building.size=0.3*planet.width,0.3*planet.width
                s=''
                if self.bArt_White:
                    s='_w'
                with turret_building.canvas:
                    Rectangle(source= 'Resources/turret_building'+s+'.png', pos= turret_building.pos, size= turret_building.size)

                turret_gun=TurretGun()
                turret_gun.root_widget= self.game_widget
                turret_gun.pos= turret_building.x + turret_building.width/2, turret_building.y + turret_building.height*2/7.0
                
                turret_gun.size=0.1*planet.width , 0.25 * (0.1 * planet.width)
                turret_barrel= TurretBarrel()
                s=''
                if self.bArt_White:
                    s='_w'
                with turret_barrel.canvas:
                    Rectangle(source= 'Resources/barrel'+s+'.png', pos= turret_gun.pos, size= turret_gun.size)
                    
                with turret_barrel.canvas.before:
                    PushMatrix()
                    turret_gun.rotate_instruction= Rotate (angle= 0, origin= (turret_gun.pos[0], turret_gun.pos[1]+ 0.25 * (0.1 * planet.width) / 2))
                    
                with turret_barrel.canvas.after:
                    PopMatrix()
                    
                    

                self.game_widget.turret_building=turret_building
                self.game_widget.turret_gun=turret_gun
                turret_gun.barrel_length = turret_gun.root_widget.turret_building.width/3.2

                
                self.game_widget.add_widget(turret_gun)
                self.game_widget.add_widget(turret_barrel)
                self.game_widget.add_widget(turret_building)
                self.game_widget.add_widget(planet)


                

                '''
            elif type == "round old":
                planet=Planet()

                planet.pos= self.root.width/2-self.root.width*0.75/2,-self.root.width*0.6
                planet.size= self.root.width*0.75,self.root.width*0.75
                planet.radius= planet.width/2
                planet.mass= planet.width*planet.width/4*3.141593
                with planet.canvas:
                    Rectangle(source= 'Resources/planet_full.png', pos= planet.pos, size= planet.size)
                self.game_widget.main_planet=planet
        
                turret_building=TurretBuilding()
                turret_building.pos= planet.center_x-planet.width/7, planet.center_y+planet.width/2-planet.width/70
                turret_building.size=0.3*planet.width,0.3*planet.width
                with turret_building.canvas:
                    Rectangle(source= 'Resources/turret_building.png', pos= turret_building.pos, size= turret_building.size)

                turret_gun=TurretGun()
                turret_gun.root_widget= self.game_widget
                turret_gun.pos= turret_building.x + turret_building.width/2, turret_building.y + turret_building.height*2/5
                turret_gun.barrel_length = turret_gun.root_widget.turret_building.width/3.0
                
                

                self.game_widget.turret_gun=turret_gun
                
                self.game_widget.add_widget(turret_gun)
                self.game_widget.add_widget(turret_building)
                self.game_widget.add_widget(planet)
                '''
                
    def create_additional_widgets_on_level_creation (self):
        butt_size = self.screen_manager.width/14.0
        factor= 1.2
        replay_butt= Button()
        replay_butt.background_normal= 'Resources/restart_button.png'
        replay_butt.background_down= 'Resources/restart_button.png'
        replay_butt.size=(butt_size, butt_size)
        replay_butt.pos= (self.screen_manager.width - factor * butt_size, self.screen_manager.height - factor * butt_size)
        replay_butt.border= (0,0,0,0)
        self.game_widget.add_widget(replay_butt)
        replay_butt.bind(on_press=self.replay_button_f)
                   
        music_butt= ToggleButton()
        music_butt.background_normal= 'Resources/Music_button.png'
        music_butt.background_down= 'Resources/Music_button_off.png'
       # if (self.bMute_SFX and self.bMute_soundtrack):
        #    music_butt.state='down' 
        music_butt.size=(butt_size, butt_size)
        music_butt.pos= (self.screen_manager.width - factor * 2 * butt_size, self.screen_manager.height - factor * butt_size)
        music_butt.border= (0,0,0,0)
        self.game_widget.add_widget(music_butt)
        music_butt.bind(on_press=self.music_button_f)

        normal_bullets_label= Label()
        self.game_widget.normal_bullets_label=normal_bullets_label
        normal_bullets_label.text= str(self.game_widget.turret_gun.num_bulletsy_to_fire)
        normal_bullets_label.pos= (0.4 * butt_size, self.screen_manager.height - 1.0 * butt_size)
        normal_bullets_label.size=(butt_size, butt_size )
        normal_bullets_label.text_size= (butt_size, butt_size ) 
        normal_bullets_label.halign= 'right'
        #normal_bullets_label.shorten_from="left"
        #normal_bullets_label.shorten=True
        self.game_widget.add_widget(normal_bullets_label)

        normal_bullet_graphic= Widget()
        self.game_widget.normal_bullet_graphic= normal_bullet_graphic
        normal_bullet_graphic.pos= (normal_bullets_label.x + butt_size/0.9 , normal_bullets_label.y - butt_size / 8.0)
        normal_bullet_graphic.size= (butt_size/1.2, butt_size/1.2)

        with normal_bullet_graphic.canvas:
            Rectangle(source="Resources/normal_bullets_graphic.png", pos= normal_bullet_graphic.pos, size= normal_bullet_graphic.size)
         
        self.game_widget.add_widget(normal_bullet_graphic)
        diff=0
        if self.game_widget.turret_gun.num_heavy_bullets_to_fire !=0:
            heavy_bullets_label= Label()
            self.game_widget.heavy_bullets_label=heavy_bullets_label
            heavy_bullets_label.text= str(self.game_widget.turret_gun.num_heavy_bullets_to_fire)
            heavy_bullets_label.pos= (2.5 * butt_size, normal_bullets_label.y)
            heavy_bullets_label.size=(butt_size, butt_size )
            heavy_bullets_label.text_size= (butt_size, butt_size ) 
            heavy_bullets_label.halign= 'right'
            #heavy_bullets_label.shorten_from="left"
            #heavy_bullets_label.shorten=True
            self.game_widget.add_widget(heavy_bullets_label)

            heavy_bullet_graphic= Widget()
            self.game_widget.heavy_bullet_graphic= heavy_bullet_graphic
            heavy_bullet_graphic.pos= (heavy_bullets_label.x + butt_size/0.9 , heavy_bullets_label.y - butt_size / 8.0)
            heavy_bullet_graphic.size= (butt_size/1.2, butt_size/1.2)
            with heavy_bullet_graphic.canvas:
                Rectangle(source="Resources/heavy_bullets_graphic.png", pos= heavy_bullet_graphic.pos, size= heavy_bullet_graphic.size)
            self.game_widget.add_widget(heavy_bullet_graphic)
            diff=butt_size * 2.0

        if self.game_widget.turret_gun.num_strange_bullets_to_fire !=0:
            strange_bullet_label= Label()
            self.game_widget.strange_bullet_label=strange_bullet_label
            strange_bullet_label.text= str(self.game_widget.turret_gun.num_strange_bullets_to_fire)
            strange_bullet_label.pos= (2.5 * butt_size + diff, normal_bullets_label.y)
            strange_bullet_label.size=(butt_size, butt_size )
            strange_bullet_label.text_size= (butt_size, butt_size ) 
            strange_bullet_label.halign= 'right'
            #strange_bullet_label.shorten_from="left"
            #strange_bullet_label.shorten=True
            self.game_widget.add_widget(strange_bullet_label)

            strange_bullet_graphic= Widget()
            self.game_widget.strange_bullet_graphic= strange_bullet_graphic
            strange_bullet_graphic.pos= (strange_bullet_label.x + butt_size/0.9 , strange_bullet_label.y - butt_size / 8.0)
            strange_bullet_graphic.size= (butt_size/1.2, butt_size/1.2)
            with strange_bullet_graphic.canvas:
                Rectangle(source="Resources/strange_bullets_graphic.png", pos= strange_bullet_graphic.pos, size= strange_bullet_graphic.size)
           
            self.game_widget.add_widget(strange_bullet_graphic)

        self.game_widget.update_bullet_graphic_colors()

    def create_level(self):
        '''
        if self.bFPS_60T_30F:
            Config.set('graphics', 'maxfps', 60)
            Config.write()
        else:
            Config.set('graphics', 'maxfps', 30)
            Config.write()
        '''
        if (self.game_widget.current_level>=1) and (self.game_widget.current_level<=24):
            self.create_planet_and_turret('flat')
        
        elif (self.game_widget.current_level==25):
            self.create_planet_and_turret('flat')

        if (self.game_widget.current_level==8) and self.beat_to_the_level==8:
            label=Label(text='Double tap anywhere on the main planet (below the turret) to change ammo type.')
            
            popup = Popup(title='Heavy Bullets available', content=label ,size_hint=(0.7, 0.4))
            popup.title_align='center'
            label.text_size=(self.screen_manager.width * 0.5 , None)
            popup.title_size= '20sp'
            popup.open()
                          
        elif (self.game_widget.current_level==16) and self.beat_to_the_level==16:
            label=Label(text='Double tap anywhere on the main planet (below the turret) to change ammo type.')
            
            popup = Popup(title='Strange Matter Bullets available', content=label ,size_hint=(0.7, 0.4))
            popup.title_align='center'
            label.text_size=(self.screen_manager.width * 0.5 , None)
            popup.title_size= '20sp'
            popup.open()
                                      
        self.game_widget.schedule_enemies()

        self.create_additional_widgets_on_level_creation()

        self.list_clock_repeat_schedule[0]=Clock.schedule_interval(self.game_widget.update, self.refresh_rate)
        self.list_clock_repeat_schedule[1]=Clock.schedule_interval(self.game_widget.turret_gun.update, self.refresh_rate)   
        self.list_clock_repeat_schedule[2]=Clock.schedule_interval(self.game_widget.update_balls, self.refresh_rate_balls_physics)   
        self.bcreated_first_level=True

    def hook_keyboard(self, window, key, *largs):
        if key == 27:
            if self.screen_manager.current == "start_menu":
                self.get_running_app().stop()

            elif self.screen_manager.current == "settings":
                 self.screen_manager.current = "start_menu"

            elif self.screen_manager.current == "level_selection":
                if self.beat_to_the_level > 0:
                    self.button_text.text='Continue'
        
                self.screen_manager.current = "start_menu"

            elif self.screen_manager.current == "level_lost_screen": 
                 self.update_button_colors()
                 self.screen_manager.current = "level_selection"

            elif self.screen_manager.current == "level_lost_screen_2": 
                 self.update_button_colors()
                 self.screen_manager.current = "level_selection"

            elif self.screen_manager.current == "level_won_screen":
                 self.update_button_colors()
                 self.screen_manager.current = "level_selection"

            elif self.screen_manager.current == "game_screen":
                 self.destroy_level()
                 self.update_button_colors()
                 self.screen_manager.current = "level_selection"

            elif self.screen_manager.current == "level_won_screen_end":
                 self.update_button_colors()
                 self.screen_manager.current = "level_selection"

        return True

    def replay_button_f (self, button):
        self.destroy_level()
        self.create_level()
        

    def music_button_f (self, toggle_button):
        return 
        ''' if toggle_button.state == 'normal':
            self.bMute_SFX= False
            self.bMute_soundtrack= False
            self.settings_screen.checkbox_Music.active=False
            self.settings_screen.checkbox_SFX.active=False
        else:
            self.bMute_SFX= True
            self.bMute_soundtrack= True
            self.settings_screen.checkbox_Music.active=True
            self.settings_screen.checkbox_SFX.active=True'''

       # self.update_soundtrack_music()

if __name__ == '__main__':
    GameApp().run()
       