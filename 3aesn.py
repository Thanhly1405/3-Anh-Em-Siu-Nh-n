import pygame
from pygame.locals import *
from constants import *
from pacman import Pacman
from nodes import NodeGroup
from pellets import PelletGroup
from ghosts import GhostGroup
from fruit import Fruit
from pauser import Pause
from text import TextGroup
from sprites import LifeSprites
from sprites import TimerSprites
from sprites import SchoolSprites
from sprites import MazeSprites
from mazedata import MazeData
from random import random
from Label import Label
from Button import Button
from Label import show_labels
import random
import sys
import pygame.gfxdraw
import time

class GameController(object):
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode(SCREENSIZE, pygame.RESIZABLE | pygame.SCALED, 32)
        self.background = None
        self.background_norm = None
        self.background_flash = None
        self.clock = pygame.time.Clock()
        self.limit_time = pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.fruit = None
        self.pause = Pause(True)
        self.level = 0
        self.lives = 5
        self.counter = 4*60
        self.score = 0
        self.textgroup = TextGroup()
        self.lifesprites = LifeSprites(self.lives)
        self.timersprite = TimerSprites()
        self.schoolsprite = SchoolSprites()
        self.flashBG = False
        self.flashTime = 0.2
        self.flashTimer = 0
        self.fruitCaptured = []
        self.fruitNode = None
        self.mazedata = MazeData()
        #self.gui_font = pygame.font.Font(None,30)
        self.gui_font = pygame.font.Font("times.ttf",30)
        self.buttons = pygame.sprite.Group()
        self.question_label = []
        self.qnum = 1
        self.qnum_max = 5
        self.questions = [
        ["UEH được thành lập vào năm nào ?", ["1976", "2005", "1980", "2023"]],
        ["UEH có bao nhiêu cơ sở ?", ["10", "9", "8", "7"]],
        ["Các ngành mới của trường là gì ?", ["Cả 3 ngành trên","Truyền thông số", "Robotics and AI", "Logistics Technology"]],
        ["Logtech có nghĩa là gì ?", ["Là ứng dụng CN vào quản lý chuỗi cung ứng","Là ngành công nghệ", "Là ngành quản lý chuỗi cung ứng",  "Cả 3 đều sai"]],
        ["UEH được thành lập vào năm nào ?", ["1976", "2005", "1980", "2023"]],
        ["Năm thành lập Viện CN Thông minh và Tương tác ?",["2021","2023","2022","2020"]],
        ["Tên viết tắt của Viện CN Thông minh và Tương tác?",["FTI","UII","HUREDIN","AEP"]],
        ["Viện công nghệ thông minh và tương tác có mấy ngành chính", ["2: LogTech và Robot&AI", "1: LogTech", "1: Robot&AI", "Cả 3 đáp án trên đều sai"]],
        ["Bằng kỹ sư đòi hỏi cần học ít nhất bao nhiêu tín chỉ", ["Lớn hơn hoặc bằng 150 tín", "Bé hơn hoặc bằng 150 tín", "Cả 2 đáp án trên đều đúng", "Cả 2 đáp án trên đều sai"]],
        ["Điểm chuẩn đại học của ngành LogTech là bao nhiêu", ["26.09", "26.9", "27.0", "Cả 3 đáp án đều sai"]],
        ["Đại học UEH có bao nhiêu ktx", ["2", "1", "4", "3"]],
        [" Bộ phim được Viện cho xem vào ngày 19/12/2023 có tên là gì?", ["3 chàng ngốc", "3 nữ điệp viên", "3 chàng lính ngự lâm", "Cả 3 đáp án trên đều sai"]],
        ]
        

        self.quiz = False
        self.quiz_true = False

    def setBackground(self):
        # khởi tạo màu nền đằng sau màn hình 
        self.background_norm = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_norm.fill(BLACK)
        self.background_flash = pygame.surface.Surface(SCREENSIZE).convert()
        self.background_flash.fill(BLACK)
        self.background_norm = self.mazesprites.constructBackground(self.background_norm, self.level%5)
        self.background_flash = self.mazesprites.constructBackground(self.background_flash, 5)
        self.flashBG = False
        self.background = self.background_norm

    def startGame(self):      
        # hàm khởi tạo màn chơi 
        self.mazedata.loadMaze(self.level)
        self.mazesprites = MazeSprites(self.mazedata.obj.name+".txt", self.mazedata.obj.name+"_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup(self.mazedata.obj.name+".txt")
        self.mazedata.obj.setPortalPairs(self.nodes)
        self.mazedata.obj.connectHomeNodes(self.nodes)
        # khởi tạo nhân vật chính
        self.pacman = Pacman(self.nodes.getNodeFromTiles(*self.mazedata.obj.pacmanStart))
        self.pellets = PelletGroup(self.mazedata.obj.name+".txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)
        # khởi tạo các nhân vạat phụ
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(0, 3)))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(4, 3)))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 3)))
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(*self.mazedata.obj.addOffset(2, 0)))
        # khởi tạo các quyền được truy cập hàm nodes của các nhân vật khác nhau =
        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.mazedata.obj.denyGhostsAccess(self.ghosts, self.nodes)
       

    def startGame_old(self):      
        self.mazedata.loadMaze(self.level)#######
        self.mazesprites = MazeSprites("maze1.txt", "maze1_rotation.txt")
        self.setBackground()
        self.nodes = NodeGroup("maze1.txt")
        self.nodes.setPortalPair((0,17), (27,17))
        homekey = self.nodes.createHomeNodes(11.5, 14)
        self.nodes.connectHomeNodes(homekey, (12,14), LEFT)
        self.nodes.connectHomeNodes(homekey, (15,14), RIGHT)
        self.pacman = Pacman(self.nodes.getNodeFromTiles(15, 26))
        self.pellets = PelletGroup("maze1.txt")
        self.ghosts = GhostGroup(self.nodes.getStartTempNode(), self.pacman)
        self.ghosts.blinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 0+14))
        self.ghosts.pinky.setStartNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))
        self.ghosts.inky.setStartNode(self.nodes.getNodeFromTiles(0+11.5, 3+14))
        self.ghosts.clyde.setStartNode(self.nodes.getNodeFromTiles(4+11.5, 3+14))
        self.ghosts.setSpawnNode(self.nodes.getNodeFromTiles(2+11.5, 3+14))

        self.nodes.denyHomeAccess(self.pacman)
        self.nodes.denyHomeAccessList(self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, LEFT, self.ghosts)
        self.nodes.denyAccessList(2+11.5, 3+14, RIGHT, self.ghosts)
        self.ghosts.inky.startNode.denyAccess(RIGHT, self.ghosts.inky)
        self.ghosts.clyde.startNode.denyAccess(LEFT, self.ghosts.clyde)
        self.nodes.denyAccessList(12, 14, UP, self.ghosts)
        self.nodes.denyAccessList(15, 14, UP, self.ghosts)
        self.nodes.denyAccessList(12, 26, UP, self.ghosts)
        self.nodes.denyAccessList(15, 26, UP, self.ghosts)
        
        

    def update(self):
        # hàm cập nhật trạng thái chính của game 
        # dt = delta time, biến chính để giới hạn tốc độ game
        # khiến cho tốc độ game không phụ thuộc vào tốc độ khung hình
        dt = self.clock.tick(30) / 1000.0
        self.textgroup.update(dt)
        self.pellets.update(dt)
        # kiểm tra các sự kiện (event) xảy ra trong game
        if not self.pause.paused:
            self.ghosts.update(dt)      
            if self.fruit is not None:
                self.fruit.update(dt)
            # sự kiện ăn hạt
            self.checkPelletEvents()
            # sự kiện đụng độ nhân vật phụ
            self.checkGhostEvents()
            # sự kiện nhặt item
            self.checkFruitEvents()
        # sự kiện đếm ngược thời gian giới hạn
        if self.counter < 0:
            match self.level:
                case 0:
                    self.counter = 4*60
                    pass
                case _:
                    self.counter = (4*60)/(self.level-1) 
                    pass
            if self.pacman.alive:
                self.lives =  0
                self.lifesprites.removeImage()
                self.pacman.die()               
                self.ghosts.hide()
                if self.lives <= 0:
                    self.textgroup.showText(GAMEOVERTXT)
                    self.pause.setPause(pauseTime=3, func=self.restartGame)
                else:
                    self.pause.setPause(pauseTime=3, func=self.resetLevel)
        if self.pacman.alive:
            if not self.pause.paused:
                self.pacman.setSpeed(100)
                self.pacman.update(dt)
        else:
            self.pacman.update(dt)
        # hàm kiểm tra đã hết màn để tạo hoạt ảnh chuyển màn 
        if self.flashBG:
            self.flashTimer += dt
            if self.flashTimer >= self.flashTime:
                self.flashTimer = 0
                if self.background == self.background_norm:
                    self.background = self.background_flash
                else:
                    self.background = self.background_norm

        afterPauseMethod = self.pause.update(dt)
        if afterPauseMethod is not None:
            afterPauseMethod()
        # Render hình ảnh game sau khi đã cập nhật các biến số của game 
        self.checkEvents()
        self.render()

    def checkEvents(self):
        # hàm kiểm tra game dừng hay game tắt
        # nếu game còn chạy thực hiện đếm ngược thời gian 
        for event in pygame.event.get():
            if event.type == QUIT:
                exit()
            elif event.type == pygame.USEREVENT: 
                if not self.pause.paused:
                    self.counter = self.counter - 1
                    self.textgroup.updateTimer(self.counter)
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    if self.pacman.alive:
                        self.pause.setPause(playerPaused=True)
                        if not self.pause.paused:
                            self.textgroup.hideText()
                            self.showEntities()
                        else:
                            self.textgroup.showText(PAUSETXT)
                            #self.hideEntities()
    

    def checkPelletEvents(self):
        # hàm kiếm tra có ăn hạt chưa, nếu ăn hạt bé tăng điểm
        # nếu ăn hạt to đổi trạng thái của nhân vật phụ
        # nếu ăn hết hạt đổi màn mới 
        pellet = self.pacman.eatPellets(self.pellets.pelletList)
        if pellet:
            self.pellets.numEaten += 1
            self.updateScore(pellet.points)
            if self.pellets.numEaten == 30:
                self.ghosts.inky.startNode.allowAccess(RIGHT, self.ghosts.inky)
            if self.pellets.numEaten == 70:
                self.ghosts.clyde.startNode.allowAccess(LEFT, self.ghosts.clyde)
            self.pellets.pelletList.remove(pellet)
            if pellet.name == POWERPELLET:
                self.ghosts.startFreight()
            if self.pellets.isEmpty():
                self.flashBG = True
                self.hideEntities()
                self.pause.setPause(pauseTime=3, func=self.nextLevel)

    def checkGhostEvents(self):
        # hàm kiểm tra đụng độ nhân vật phụ 
        for ghost in self.ghosts:
            if self.pacman.collideGhost(ghost):
                if ghost.mode.current is FREIGHT: # kiểm tra trạng thái của nhân vật phụ, nếu trạng thái 2 ăn được 
                    self.pacman.visible = False
                    ghost.visible = False
                    self.updateScore(ghost.points)                  
                    self.textgroup.addText(str(ghost.points), WHITE, ghost.position.x, ghost.position.y, 8, time=1)
                    self.ghosts.updatePoints()
                    self.pause.setPause(pauseTime=1, func=self.showEntities)
                    ghost.startSpawn()
                    self.nodes.allowHomeAccess(ghost)
                elif ghost.mode.current is not SPAWN: # nếu trạng thái 1 không ăn được 
                    game_on = 1
                    self.question(self.qnum)
                    # mở ra trò chơi trắc nghiệm 
                    while not self.quiz:
                        for event in pygame.event.get():
                            if (event.type == pygame.QUIT):
                                game_on = 0
                                pygame.quit()
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    pygame.quit()
                                    game_on = 0
                        if game_on:
                            self.buttons.update()
                            self.buttons.draw(self.screen)
                        else:
                            pygame.quit()
                            sys.exit()
                        self.buttons.draw(self.screen)
                        pygame.display.update()
                    # nếu trả lời sai giảm mạng và trừ thời gian 20s 
                    if self.pacman.alive and not self.quiz_true:
                        self.lives -=  1
                        self.counter -= 20
                        self.lifesprites.removeImage()
                        self.pacman.die()               
                        self.ghosts.hide()
                        # nếu hết mạng kết thúc game 
                        if self.lives <= 0:
                            match self.level:
                                case 0:
                                    self.counter = 4*60
                                    pass
                                case _:
                                    self.counter = (4*60)/(self.level-1) 
                                    pass
                            self.textgroup.showText(GAMEOVERTXT)
                            self.pause.setPause(pauseTime=3, func=self.restartGame)
                        else:
                            self.pause.setPause(pauseTime=3, func=self.resetLevel)
                    # nếu trả lời đúng đổi trạng thái nhân vật phụ 
                    elif self.quiz_true:
                        ghost.startFreight()
        self.quiz_true = False
        self.quiz = False
        if (self.qnum > self.qnum_max):
            self.qnum = 0
        
    
    def checkFruitEvents(self):
        # hàm kiểm tra ăn item, nếu ăn item cộng thêm điểm 
        if self.pellets.numEaten == 50 or self.pellets.numEaten == 140:
            if self.fruit is None:
                self.fruit = Fruit(self.nodes.getNodeFromTiles(9, 20), self.level)
                print(self.fruit)
        if self.fruit is not None:
            if self.pacman.collideCheck(self.fruit):
                self.updateScore(self.fruit.points)
                self.textgroup.addText(str(self.fruit.points), WHITE, self.fruit.position.x, self.fruit.position.y, 8, time=1)
                fruitCaptured = False
                for fruit in self.fruitCaptured:
                    if fruit.get_offset() == self.fruit.image.get_offset():
                        fruitCaptured = True
                        break
                if not fruitCaptured:
                    self.fruitCaptured.append(self.fruit.image)
                self.fruit = None
            elif self.fruit.destroy:
                self.fruit = None

    def showEntities(self):
        self.pacman.visible = True
        self.ghosts.show()

    def hideEntities(self):
        self.pacman.visible = False
        self.ghosts.hide()

    def nextLevel(self):
        # hàm chuyển màn và giảm thời gian đếm ngược 
        self.showEntities()
        self.level += 1
        match self.level:
            case 0:
                self.counter = 4*60
                pass
            case _:
                self.counter = (4*60)/(self.level + 1)
                pass
        self.pause.paused = True
        self.startGame()
        self.textgroup.updateLevel(self.level)

    def restartGame(self):
        self.lives = 5
        self.level = 0
        self.pause.paused = True
        self.fruit = None
        self.startGame()
        self.score = 0
        self.textgroup.updateScore(self.score)
        self.textgroup.updateLevel(self.level)
        self.textgroup.showText(READYTXT)
        self.lifesprites.resetLives(self.lives)
        self.fruitCaptured = []

    def resetLevel(self):
        self.pause.paused = True
        self.pacman.reset()
        self.ghosts.reset()
        self.fruit = None
        self.textgroup.showText(READYTXT)

    def updateScore(self, points):
        self.score += points
        self.textgroup.updateScore(self.score)

    def render(self):

        self.screen.blit(self.background, (0, 0))
        #self.nodes.render(self.screen)
        self.pellets.render(self.screen)
        if self.fruit is not None:
            self.fruit.render(self.screen)
        self.pacman.render(self.screen)
        self.ghosts.render(self.screen)
        self.textgroup.render(self.screen)
        self.screen.blit(self.timersprite.getImage(12,10),(11*TILEWIDTH,0))
        self.screen.blit(self.schoolsprite.getImage(16,4),(0*TILEWIDTH,14.5*TILEWIDTH))
        self.screen.blit(self.schoolsprite.getImage(12,4),(24.4*TILEWIDTH,14.5*TILEWIDTH))

        for i in range(len(self.lifesprites.images)):
            x = self.lifesprites.images[i].get_width() * i
            y = SCREENHEIGHT - self.lifesprites.images[i].get_height()
            self.screen.blit(self.lifesprites.images[i], (x, y))

        for i in range(len(self.fruitCaptured)):
            x = SCREENWIDTH - self.fruitCaptured[i].get_width() * (i+1)
            y = SCREENHEIGHT - self.fruitCaptured[i].get_height()
            self.screen.blit(self.fruitCaptured[i], (x, y))

        pygame.display.update()
    def question(self,qnum):
        ''' put your buttons here '''

        for sprites in self.buttons:
            sprites.kill()

        pos = [100, 150, 200, 250]
        random.shuffle(pos)
        # this is a label, a button with no border does nothing: command = None
        Button(self.screen,self.buttons,(0, 0), str(qnum-1), 20, "white on black",
            hover_colors="blue on orange", style=2, borderc=(0,0,0),
            command=None)

        Button(self.screen,self.buttons,(10, 10), self.questions[qnum-1][0], 30, "white on black",
            hover_colors="blue on orange", style=2, borderc=(0,0,0),
            command=None)

        # ______------_____ BUTTONS FOR ANSWERS _____------______ #

        Button(self.screen,self.buttons,(10, 100), "1. ", 36, "red on yellow",
            hover_colors="blue on orange", style=2, borderc=(255,255,0),
            command=None)
        Button(self.screen,self.buttons,(10, 150), "2. ", 36, "red on yellow",
            hover_colors="blue on orange", style=2, borderc=(255,255,0),
            command=None)
        Button(self.screen,self.buttons,(10, 200), "3. ", 36, "red on yellow",
            hover_colors="blue on orange", style=2, borderc=(255,255,0),
            command=None)
        Button(self.screen,self.buttons,(10, 250), "4. ", 36, "red on yellow",
            hover_colors="blue on orange", style=2, borderc=(255,255,0),
            command=None)

        Button(self.screen,self.buttons,(50, pos[0]), self.questions[qnum-1][1][0], 36, "red on yellow",
            hover_colors="blue on orange", style=2, borderc=(255,255,0),
            command=self.on_right)


        Button(self.screen,self.buttons,(50, pos[1]), self.questions[qnum-1][1][1], 36, "red on yellow",
            hover_colors="blue on orange", style=2, borderc=(255,255,0),
            command=self.on_false)

        Button(self.screen,self.buttons,(50, pos[2]), self.questions[qnum-1][1][2], 36, "red on yellow",
            hover_colors="blue on orange", style=2, borderc=(255,255,0),
            command=self.on_false)

        Button(self.screen,self.buttons,(50, pos[3]), self.questions[qnum-1][1][3], 36, "red on yellow",
            hover_colors="blue on orange", style=2, borderc=(255,255,0),
            command=self.on_false)
    def forward(self):
        self.screen.fill(0)
        if self.qnum < len(self.questions):
            time.sleep(.3)
            self.qnum += 1
            self.question(self.qnum)
    def on_click():
        print("Click on one answer")

    def on_run(): 
        print("Ciao bello questo è RUN")

    def on_save():
        print("This is Save")

    def on_right(self):
        print("Right")
        time.sleep(.3)
        self.qnum += 1
        self.quiz = True
        self.quiz_true = True
        #score.change_text("100")
        #self.forward()

    def on_false(self):
        print("Wrong")
        time.sleep(.3)
        self.qnum += 1
        self.quiz = True
        self.quiz_true = False
        #self.forward()

    


if __name__ == "__main__":
    
    game = GameController()
    game.startGame()
    while True:
        game.update()
            



