from obj import Obj
from buffer import Buffer
import glm
from OpenGL.GL import *

class Model (object): 
    def __init__(self, filename):
        self.objFile = Obj(filename)
        
        self.position = glm.vec3(0.0, 0.0, 0.0)
        self.rotation = glm.vec3(0.0, 0.0, 0.0)
        self.scale = glm.vec3(1.0, 1.0,1.0)
        
        self.BuildBuffers()
    
    
    def GetModelMatrix(self):
        identity = glm.mat4(1.0)
        
        translateM = glm.translate(identity, self.position)
        
        pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
        yawMat = glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
        rollMat = glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))
        
        rotationMat = rollMat * pitchMat * yawMat 
        
        scaleMat = glm.scale(identity, self.scale)
        
        return  translateM * rotationMat * scaleMat
    
    def BuildBuffers(self):
        positions = []
        self.vertexCount = 0
        
        for face in self.objFile.faces:
            
            facePositions = []
            
            for i in range(len(face)): #asumimos que son triangulos
                facePositions.append(self.objFile.vertices[face[i][0] - 1])
            
            for value in facePositions[0]:positions.append(value)
                
            for value in facePositions[1]:positions.append(value)
                
            for value in facePositions[2]:positions.append(value)
                            
                
            self.vertexCount += 3 
            
            #existe la posibilidad de que una cara tenga 4 vertices o algo así 
            
            if len(face) == 4:
                
                for value in facePositions[0]:positions.append(value)
                
                for value in facePositions[2]:positions.append(value)
                    
                for value in facePositions[3]:positions.append(value)
                    
                    
                    
                self.vertexCount += 3
        
        
        
        self.posBuffer = Buffer(positions)
        
    
    def Render(self):
        self.posBuffer.Use(0, 3)

        glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)

        glDisableVertexAttribArray(0)