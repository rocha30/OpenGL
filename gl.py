import glm # pip install PyGLM
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader

from camera import Camera
from skybox import Skybox

class Renderer(object):
    def __init__(self, screen):
        self.screen = screen
        _,_, self.width, self.height = screen.get_rect()
        
        glClearColor(0.2, 0.2, 0.2, 1.0)

        glEnable(GL_DEPTH_TEST)
        glViewport(0,0, self.width, self.height)

        self.camera = Camera(self.width, self.height)

        self.scene = []
        

        self.filledMode = False
        self.ToggleFilledMode()

        self.activeShader = None
        self.active_postProcessing_Shader = None


        self.skybox = None

        self.pointLight = glm.vec3(0,0,0)
        self.ambientLight = 0.1


        self.value = 0.0;
        self.elapsedTime = 0.0;

        self.CreateFrameBuffer()



    def CreateSkybox(self, textureList):
        self.skybox = Skybox(textureList)
        self.skybox.cameraRef = self.camera


    def CreateFrameBuffer(self):
        # Crear frameBuffer
        self.FBO = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

        # Crear la textura del framebuffer
        self.FBOTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.FBOTexture)
        glTexImage2D(GL_TEXTURE_2D,0, GL_RGBA, self.width, self.height, 0, GL_RGBA, GL_UNSIGNED_BYTE,None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_COLOR_ATTACHMENT0, GL_TEXTURE_2D, self.FBOTexture, 0)

        # Create depthTexture/Z buffer
        self.depthTexture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depthTexture)
        glTexImage2D(GL_TEXTURE_2D,0, GL_DEPTH_COMPONENT24, self.width, self.height, 0, GL_DEPTH_COMPONENT, GL_FLOAT ,None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT, GL_TEXTURE_2D, self.depthTexture, 0)

        # Unbind
        glBindFramebuffer(GL_FRAMEBUFFER, 0)



    def ToggleFilledMode(self):
        self.filledMode = not self.filledMode

        if self.filledMode:
            glEnable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT, GL_FILL)
        else:
            glDisable(GL_CULL_FACE)
            glPolygonMode(GL_FRONT_AND_BACK, GL_LINE)


    def SetShaders(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.activeShader = compileProgram( compileShader(vertexShader, GL_VERTEX_SHADER),
                                                compileShader(fragmentShader, GL_FRAGMENT_SHADER) )
        else:
            self.activeShader = None


    def SetPostProcessingShaders(self, vertexShader, fragmentShader):
        if vertexShader is not None and fragmentShader is not None:
            self.active_postProcessing_Shader = compileProgram( compileShader(vertexShader, GL_VERTEX_SHADER),
                                                compileShader(fragmentShader, GL_FRAGMENT_SHADER) )
        else:
            self.active_postProcessing_Shader = None


    def Render(self):
        # If post-processing is enabled, render the scene into the FBO first
        if self.active_postProcessing_Shader is not None:
            glBindFramebuffer(GL_FRAMEBUFFER, self.FBO)

        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

        self.camera.Update()

        # Render skybox FIRST so it never occludes scene geometry
        if self.skybox is not None:
            glDisable(GL_DEPTH_TEST)
            self.skybox.Render()
            glEnable(GL_DEPTH_TEST)

        # Draw all scene objects (cada uno puede tener sus propios shaders)
        for obj in self.scene:
            # Determinar qué shaders usar: los del modelo o los globales
            useShader = None
            if obj.vertexShader is not None and obj.fragmentShader is not None:
                # El modelo tiene shaders propios, compilarlos si no están compilados
                if not hasattr(obj, '_compiledShader'):
                    obj._compiledShader = compileProgram(
                        compileShader(obj.vertexShader, GL_VERTEX_SHADER),
                        compileShader(obj.fragmentShader, GL_FRAGMENT_SHADER)
                    )
                useShader = obj._compiledShader
            else:
                # Usar shaders globales
                useShader = self.activeShader
            
            if useShader is not None:
                glUseProgram(useShader)
                
                # Uniforms comunes (view, projection, lights)
                glUniformMatrix4fv(glGetUniformLocation(useShader, "viewMatrix"),
                                   1, GL_FALSE, glm.value_ptr(self.camera.viewMatrix))
                
                glUniformMatrix4fv(glGetUniformLocation(useShader, "projectionMatrix"),
                                   1, GL_FALSE, glm.value_ptr(self.camera.projectionMatrix))
                
                glUniformMatrix4fv(glGetUniformLocation(useShader, "modelMatrix"),
                                   1, GL_FALSE, glm.value_ptr(obj.GetModelMatrix()))
                
                glUniform3fv(glGetUniformLocation(useShader, "pointLight"), 
                            1, glm.value_ptr(self.pointLight))
                glUniform1f(glGetUniformLocation(useShader, "ambientLight"), self.ambientLight)
                
                # Value: usar el del modelo si tiene shaders propios, sino el global
                valueToUse = obj.shaderValue if (obj.vertexShader is not None) else self.value
                glUniform1f(glGetUniformLocation(useShader, "value"), valueToUse)
                
                glUniform1f(glGetUniformLocation(useShader, "time"), self.elapsedTime)
                
                # Texturas
                glUniform1i(glGetUniformLocation(useShader, "tex0"), 0)
                glUniform1i(glGetUniformLocation(useShader, "tex1"), 1)
                
                # Color personalizado (si el shader lo soporta y el modelo lo usa)
                if obj.useCustomColor:
                    colorLoc = glGetUniformLocation(useShader, "customColor")
                    if colorLoc != -1:
                        glUniform3fv(colorLoc, 1, glm.value_ptr(obj.shaderColor))
            
            obj.Render()

        # Skybox was already rendered as background

        # If post-processing is enabled, now render the FBO to the screen with the PP shader
        if self.active_postProcessing_Shader is not None:
            glBindFramebuffer(GL_FRAMEBUFFER, 0)
            glClear(GL_COLOR_BUFFER_BIT)

            glDisable(GL_DEPTH_TEST)

            glUseProgram(self.active_postProcessing_Shader)

            glActiveTexture(GL_TEXTURE0)
            glBindTexture(GL_TEXTURE_2D, self.FBOTexture)

            glActiveTexture(GL_TEXTURE1)
            glBindTexture(GL_TEXTURE_2D, self.depthTexture)

            glUniform1i(glGetUniformLocation(self.active_postProcessing_Shader, "frameBuffer"), 0)
            glUniform1i(glGetUniformLocation(self.active_postProcessing_Shader, "depthTexture"), 1)

            glUniform1f(glGetUniformLocation(self.active_postProcessing_Shader, "time"), self.elapsedTime)

            # Provide texel size for effects that need neighbor lookups
            texelSizeLoc = glGetUniformLocation(self.active_postProcessing_Shader, "texelSize")
            if texelSizeLoc != -1:
                glUniform2f(texelSizeLoc, 1.0 / float(self.width), 1.0 / float(self.height))

            # Draw a full-screen quad using immediate mode (compat profile) and fixed-function attrs
            # Ensure state won't cull the screen quad
            cullEnabled = glIsEnabled(GL_CULL_FACE)
            if cullEnabled:
                glDisable(GL_CULL_FACE)
            glBegin(GL_QUADS)
            glTexCoord2f(0.0, 0.0); glVertex2f(-1.0, -1.0)
            glTexCoord2f(1.0, 0.0); glVertex2f( 1.0, -1.0)
            glTexCoord2f(1.0, 1.0); glVertex2f( 1.0,  1.0)
            glTexCoord2f(0.0, 1.0); glVertex2f(-1.0,  1.0)
            glEnd()
            if cullEnabled:
                glEnable(GL_CULL_FACE)

            glEnable(GL_DEPTH_TEST)

