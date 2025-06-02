import pygame
from pygame.locals import *
import random

pygame.init()

#screen : 
width = 400
height = 700
screenSize = (width,height)
screen = pygame.display.set_mode(screenSize)
pygame.display.set_caption('AI Car Racing Game')

#game settings :
gameover = False
speed = 2
score = 0

#marker sizes :
markerWidth = 10
markerHeight = 50

#edge markers : 
road = (50, 0, 300, height)
leftEdgeMarker = (40, 0, markerWidth, height)
rightEdgeMarker = (350, 0, markerWidth, height)

#X lane coordinates : 
leftXlane = 100
centerXlane = 200
rightXlane = 300
Xlanes = [leftXlane,centerXlane,rightXlane]
#animation :
laneMoveY = 0

class Vehicle(pygame.sprite.Sprite):
    def __init__(self, image, x, y):
        pygame.sprite.Sprite.__init__(self=self)

        imageScale = 45 / image.get_rect().width        
        newWidth = image.get_rect().width * imageScale
        newHeight = image.get_rect().height * imageScale
        self.image = pygame.transform.scale(image, (newWidth,newHeight))

        self.rect = self.image.get_rect()
        self.rect.center = [x,y]

class PlayerVehicle(Vehicle):
    
    def __init__(self, x, y):
        image = pygame.image.load('images/car.png')
        super().__init__(image, x, y)

#start coordinates:  
playerX = 200
playerY = 550

#player car:
playerGroup = pygame.sprite.Group()
player = PlayerVehicle(playerX,playerY)
playerGroup.add(player)

#bot cars :
imageOtherCars = ["images/pickup_truck.png","images/semi_trailer.png","images/taxi.png","images/van.png"]
vehicleImages = []
for image in imageOtherCars:
    imageBot = pygame.image.load(image)
    vehicleImages.append(imageBot)

vehicleGroup = pygame.sprite.Group()

#crash image:
crash = pygame.image.load("images/crash.png")
crashRect = crash.get_rect()

clock = pygame.time.Clock()
fps = 120
running = True

while running:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == QUIT:
            running = False

        if event.type == KEYDOWN:
            if event.key == K_LEFT and player.rect.center[0] > leftXlane:
                player.rect.x -= 100
            elif event.key == K_RIGHT and player.rect.center[0] < rightXlane:
                player.rect.x += 100
            
            for vehicle in vehicleGroup:
                if pygame.sprite.collide_rect(player,vehicle):
                    gameover = True

                    if event.key == K_LEFT:
                        player.rect.left = vehicle.rect.right
                        crashRect.center = [player.rect.left, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                    elif event.key == K_RIGHT:
                        player.rect.right = vehicle.rect.left
                        crashRect.center = [player.rect.right, (player.rect.center[1] + vehicle.rect.center[1]) / 2]
                
    screen.fill(color="darkgreen")

    pygame.draw.rect(screen, color="dimgray", rect=road)

    pygame.draw.rect(screen, color="gold", rect=leftEdgeMarker)
    pygame.draw.rect(screen, color="gold", rect=rightEdgeMarker)
    
    laneMoveY += speed * 2
    if laneMoveY >= markerHeight * 2:
        laneMoveY = 0
        
    for y in range(markerHeight * -2, height, markerHeight * 2):
        pygame.draw.rect(screen, color="white", rect=(leftXlane + 45, y + laneMoveY, markerWidth, markerHeight))
        pygame.draw.rect(screen, color="white", rect=(centerXlane + 45, y + laneMoveY, markerWidth, markerHeight))

    playerGroup.draw(screen)
    if len(vehicleGroup) < 2:
        addVehicle = True
        for vehicle in vehicleGroup:
            if vehicle.rect.top < vehicle.rect.height * 1.5:
                addVehicle = False
        
        if addVehicle:
            lane = random.choice(Xlanes)

            image = random.choice(vehicleImages)
            vehicle = Vehicle(image,lane,height/-2)
            vehicleGroup.add(vehicle)
    
    for vehicle in vehicleGroup:
        vehicle.rect.y += speed

        if vehicle.rect.top >= height:
            vehicle.kill()
            score += 1

            if score > 0 and score % 5 == 0:
                speed += 0.2

    vehicleGroup.draw(screen)

    font = pygame.font.Font(pygame.font.get_default_font(),16)
    text = font.render('Score: ' + str(score), True, (255, 255, 255))
    textRect = text.get_rect()
    textRect.center = (200,20)
    screen.blit(text, textRect)

    if pygame.sprite.spritecollide(player,vehicleGroup, True):
        gameover = True
        crashRect.center = [player.rect.center[0], player.rect.top]

    if gameover:
        
        screen.blit(crash, crashRect)
        pygame.draw.rect(screen, "red", (0,50,width,150))
        font = pygame.font.Font(pygame.font.get_default_font(),16)

        text = font.render('Game over, play again? (Enter Y or N)', True, "white")
        textRect = text.get_rect()
        textRect.center = (width/2, 100)
        screen.blit(text, textRect)

        text = font.render('Score : ' + str(score), True, "white")
        textRect = text.get_rect()
        textRect.center = (width/2, 150)
        screen.blit(text, textRect)

    pygame.display.update()

    while gameover:

        clock.tick(fps)

        for event in pygame.event.get():

            if event.type == QUIT:
                gameover = False
                running = False
            
            if event.type == KEYDOWN:

                if event.key == K_y:

                    gameover = False
                    speed = 2
                    score = 0
                    vehicleGroup.empty()
                    player.rect.center = [playerX, playerY]
                elif event.key == K_n:

                    gameover = False
                    running = False

pygame.quit()

