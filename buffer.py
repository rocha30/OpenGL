import glm
from OpenGL.GL import *
from numpy import array, float32


class Buffer(object):
    def __init__(self,data):
        self.data = data
        
        # vertex buffer 
        self.vertexBuffer = array(self.data, dtype = float32)
        
        # OpenGL objects - will be created when needed
        self.VBO = glGenBuffers(1)

    def Use(self, attribNumber, size):
        
        glBindBuffer(GL_ARRAY_BUFFER, self.VBO)
    
        
        # Mandar la informacion de vertices 
        glBufferData(GL_ARRAY_BUFFER,   #Buffer id 
                     self.vertexBuffer.nbytes,   #Buffer size in byts 
                     self.vertexBuffer,   #Buffer data
                     GL_STATIC_DRAW)   #Usage
        
        # atributos 
        #normales, posiciones, colores, texCoords
        
        #Atributos de posiciones 
        glVertexAttribPointer(attribNumber,                    # Atribute number
                              size,                    #size 
                              GL_FLOAT,             #Type 
                              GL_FALSE,             # normalized? 
                              0,                #Stride 
                              ctypes.c_void_p(0))   # Offset 
        
        glEnableVertexAttribArray(attribNumber)
        
        
        

        
        
                          
        