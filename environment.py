import cv2
import random
import pygame
import numpy as np
from pygame.locals import *
from collections import deque

class Environment:
    def __init__(self):
        pygame.init()
        self.width = 400
        self.height = 700
        self.screenSize = (self.width, self.height)
        self.screen = pygame.display.set_mode(self.screenSize)
        pygame.display.set_caption('AI Car Racing Game with RL Agent')

        self.gameover = False
        self.speed = 2
        self.score = 0

        self.markerWidth = 10
        self.markerHeight = 50

        self.road = (50, 0, 300, self.height)
        self.leftEdgeMarker = (40, 0, self.markerWidth, self.height)
        self.rightEdgeMarker = (350, 0, self.markerWidth, self.height)

        self.leftXlane = 100
        self.centerXlane = 200
        self.rightXlane = 300
        self.Xlanes = [self.leftXlane, self.centerXlane, self.rightXlane]
        self.laneMoveY = 0

        self.playerX = 200
        self.playerY = 550
        self.playerGroup = pygame.sprite.Group()
        self.player = PlayerVehicle(self.playerX, self.playerY)
        self.playerGroup.add(self.player)

        self.imageOtherCars = ["images/pickup_truck.png", "images/semi_trailer.png", 
                              "images/taxi.png", "images/van.png"]

        self.vehicleImages = []
        for image in self.imageOtherCars:
            imageBot = pygame.image.load(image)
            self.vehicleImages.append(imageBot)
        
        self.vehicleGroup = pygame.sprite.Group()

        self.crash = pygame.image.load("images/crash.png")
        self.crashRect = self.crash.get_rect()

        self.actionSpace = 3  
        self.observationSpace = (84, 84, 4)

        self.frameStack = deque(maxlen=4)
        
        for _ in range(4):
            self.frameStack.append(np.zeros((84, 84)))
    
    def close(self):
        pygame.quit()
    
    def reset(self):
        self.gameover = False
        self.speed = 2
        self.score = 0
        self.vehicleGroup.empty()
        self.player.rect.center = [self.playerX, self.playerY]
        self.laneMoveY = 0
        
        self.frameStack.clear()
        for _ in range(4):
            self.frameStack.append(np.zeros((84, 84)))
        
        self.render()
        return self._getState()
    
    def _getState(self):
        screenSurface = pygame.surfarray.array3d(self.screen)
        screenArray = np.transpose(screenSurface, (1, 0, 2)) 
        gray = cv2.cvtColor(screenArray, cv2.COLOR_RGB2GRAY)
        resized = cv2.resize(gray, (84, 84), interpolation=cv2.INTER_AREA)
        normalized = resized / 255.0

        self.frameStack.append(normalized)
        state = np.stack(list(self.frameStack), axis=-1)   ### -> ardisik goruntuleri tek bir kanalda birlestir. son boyutta.

        return state

    def step(self, action):
        reward = 0
        done = False
        prev_score = self.score  

        if action != 1: 
            reward -= 0.1
        
        if action == 0:  
            if self.player.rect.center[0] > self.leftXlane:
                self.player.rect.x -= 100
        elif action == 2: 
            if self.player.rect.center[0] < self.rightXlane:
                self.player.rect.x += 100
        
        self._updateGameState()

        ### collision ? -100 (high punishment)
        ### speed - directly proportional reward (low)
        ### if too close to other cars -reward (low)
        
        if pygame.sprite.spritecollide(self.player, self.vehicleGroup, True):
            self.gameover = True
            reward = -100  
            done = True
            self.crashRect.center = [self.player.rect.center[0], self.player.rect.top]
        else:
            reward += (self.score - prev_score) * 2  
            
            if self.player.rect.center[0] == self.centerXlane:
                reward += 0.2
            
            reward += self.speed * 0.1
            reward += 0.05
        
        for vehicle in self.vehicleGroup:
            if abs(vehicle.rect.center[0] - self.player.rect.center[0]) < 50:
                if vehicle.rect.top > self.player.rect.bottom and vehicle.rect.top < self.player.rect.bottom + 50:
                    reward -= 0.5
                elif vehicle.rect.bottom > self.player.rect.top - 50 and vehicle.rect.bottom < self.player.rect.top:
                    reward -= 0.8
                elif abs(vehicle.rect.center[0] - self.player.rect.center[0]) < 20:
                    reward -= 0.3
        
        self.render()       
        nextState = self._getState()       
        info = {'score': self.score}
        
        return nextState, reward, done, info
    
    def _updateGameState(self):
        self.laneMoveY += self.speed * 2
        if self.laneMoveY >= self.markerHeight * 2:
            self.laneMoveY = 0
        
        for vehicle in self.vehicleGroup:
            vehicle.rect.y += self.speed
            if vehicle.rect.top >= self.height:
                vehicle.kill()
                self.score += 1
              
                if self.score > 0 and self.score % 5 == 0:
                    self.speed += 0.2
        
        self._spawnVehicles()

    def _spawnVehicles(self):
        if len(self.vehicleGroup) < 2:
            addVehicle = True
            for vehicle in self.vehicleGroup:
                if vehicle.rect.top < vehicle.rect.height * 1.5:
                    addVehicle = False
            
            if addVehicle:
                lane = random.choice(self.Xlanes)
                image = random.choice(self.vehicleImages)
                vehicle = Vehicle(image, lane, self.height // -2)
                self.vehicleGroup.add(vehicle)
    
    def render(self):
        self.screen.fill(color="darkgreen")
        pygame.draw.rect(self.screen, color="dimgray", rect=self.road)
        pygame.draw.rect(self.screen, color="gold", rect=self.leftEdgeMarker)
        pygame.draw.rect(self.screen, color="gold", rect=self.rightEdgeMarker)
        
        for y in range(self.markerHeight * -2, self.height, self.markerHeight * 2):
            pygame.draw.rect(self.screen, color="white", 
                           rect=(self.leftXlane + 45, y + self.laneMoveY, 
                                self.markerWidth, self.markerHeight))
            pygame.draw.rect(self.screen, color="white", 
                           rect=(self.centerXlane + 45, y + self.laneMoveY, 
                                self.markerWidth, self.markerHeight))
              
        self.playerGroup.draw(self.screen)
        self.vehicleGroup.draw(self.screen)
        
        font = pygame.font.Font(pygame.font.get_default_font(), 16)
        text = font.render('Score: ' + str(self.score), True, (255, 255, 255))
        textRect = text.get_rect()
        textRect.center = (200, 20)
        self.screen.blit(text, textRect)
        
        if self.gameover:
            self.screen.blit(self.crash, self.crashRect)
        
        pygame.display.update()

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self)
        imageScale = 45 / image.get_rect().width        
        newWidth = image.get_rect().width * imageScale
        newHeight = image.get_rect().height * imageScale
        self.image = pygame.transform.scale(image, (newWidth, newHeight))
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]

class PlayerVehicle(Vehicle):
    def __init__(self, x, y):
        image = pygame.image.load('images/car.png')
        super().__init__(image, x, y)


def test_environment():
    env = Environment()
    clock = pygame.time.Clock()
    
    running = True
    state = env.reset()
    
    while running:
        clock.tick(60)
        
        action = 1  
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN:
                if event.key == K_LEFT:
                    action = 0
                elif event.key == K_RIGHT:
                    action = 2
                elif event.key == K_r: 
                    state = env.reset()
                    continue
        
        state, reward, done, info = env.step(action)
        
        if done:
            print("Game Over! Final Score:", info['score'])
            pygame.time.wait(1000)
            state = env.reset()
    
    env.close()

if __name__ == "__main__":
    test_environment()