import glm #pip install PyGLM
from OpenGL.GL import *
from buffer import Buffer
from camera import Camera
from OpenGL.GL.shaders import compileProgram, compileShader
from skybox import Skybox

class Renderer:
    def __init__(self,screen):
        self.screen = screen
        _,_, self.width, self.height = screen.get_rect()
        
        glClearColor(0.2, 0.2, 0.2, 1.0)
        glEnable(GL_DEPTH_TEST)
        glViewport(0, 0, self.width, self.height)
        
        
        self.camera = Camera(self.width, self.height)
        self.scene = []
        
        self.activeShader = None
        
        
        self.filledMode = False
        self.ToggleFilledMode()
        
    def CreateSkybox(self, textureList):
        self.skybox = Skybox(textureList)
        self.skybox.cameraRef = self.camera
        
    def ToggleFilledMode(self):
        self.filledMode = not self.filledMode
        if self.filledMode:
            glEnable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)
        else:
            glDisable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)
        
        
        
        
    def SetShader(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.activeShader = compileProgram(compileShader(vertexShader, GL_VERTEX_SHADER),
                                               compileShader(fragmentShader, GL_FRAGMENT_SHADER))
        else: 
            self.activeShader = None

    def Render(self):
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
        
        self.camera.Update() 
        
        if self.activeShader is not None:
            glUseProgram(self.activeShader)

            glUniformMatrix4fv(glGetUniformLocation(self.activeShader, "viewMatrix"), 
                               1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix))
            
            glUniformMatrix4fv(glGetUniformLocation(self.activeShader, "projectionMatrix"), 
                               1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix))


        for obj in self.scene:
            if self.activeShader is not None:
                glUniformMatrix4fv(glGetUniformLocation(self.activeShader, "modelMatrix"), 
                               1, GL_FALSE, glm.value_ptr(obj.GetModelMatrix()))
                
            obj.Render()
            