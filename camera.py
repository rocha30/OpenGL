import glm 

class Camera(object):
    def __init__(self, width, height):
        self.position = glm.vec3(0.0, 0.0, 0.0)  # Camera position
        
        self.width = width
        self.height = height
        
        #angulo de euler
        self.rotation = glm.vec3(0.0, 0.0, 0.0)  # Camera rotation (pitch, yaw, roll)

        self.viewMatrix = None  
        
        self.CreateProjectionMatrix(60, 0.1, 1000)
        
    def Update(self):
        identity = glm.mat4(1.0)
        
        traslateM= glm.translate(identity, -self.position)
        
        pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
        yawMat = glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
        rollMat = glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

        rotationMat = rollMat * pitchMat * yawMat 
        
        camMat = rotationMat * traslateM
        
        self.viewMatrix = glm.inverse(camMat)


    def CreateProjectionMatrix(self, fov, nearPlane, farPlane):
        self.projectionMatrix = glm.perspective(glm.radians(fov), self.width / self.height, nearPlane, farPlane)