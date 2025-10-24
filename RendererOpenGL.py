import pygame 
from pygame.locals import *
from gl import Renderer
from buffer import Buffer
from model import Model
from vertexShaders import vertex_Shader
from fragmentShaders import fragment_shader


height = 960
width = 540

deltaTime = 0.0
screen = pygame.display.set_mode((width, height), pygame.SCALED | pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()


triangle = [
    -0.5, -0.5, 0.0,  1,0, 0.0, 0.0,  # Vertex 1: position (x, y, z) and color (r, g, b)
     0.5, 0.5, 0.0,   0, 1, 0.0, 0.0,  # Vertex 2: position (x, y, z) and color (r, g, b)
     0.0, -0.5, 0.0,  0, 0, 1.0, 0.0   # Vertex 3: position (x, y, z) and color (r, g, b)
]



rend = Renderer(screen)

# win = glfw.create_window(800, 600, "Renderer", None, None)
# glfw.make_context_current(win) 
rend.SetShader(vertex_Shader, fragment_shader)

faceModel = Model("Centaur_Male_Lores.obj")
faceModel.position.z = -5
faceModel.scale.x = 0.005
faceModel.scale.y = 0.005
faceModel.scale.z = 0.005

rend.scene.append(faceModel)



isRunning = True
while isRunning:
    deltaTime = clock.tick(60) / 1000

    keys = pygame.key.get_pressed()
    
    
    for event in pygame.event.get():
        if event.type == QUIT:
            isRunning = False
        elif event.type == KEYDOWN:
            if event.key == pygame.K_f: 
                rend.ToggleFilledMode()
            
    if keys[K_UP]:
            rend.camera.position.y += 1 * deltaTime 
    
    if keys[K_DOWN]:
            rend.camera.position.y -= 1 * deltaTime
            
    if keys[K_RIGHT]:
            rend.camera.position.x += 1 * deltaTime
    
    if keys[K_LEFT]:
            rend.camera.position.x -= 1 * deltaTime

    # if keys[K_W]:
    #         render.camera.position.z += 1 * deltaTime

    # if keys[K_S]:
    #         render.camera.position.z -= 1 * deltaTime
            
    faceModel.rotation.y += 45 * deltaTime

    rend.Render()
    pygame.display.flip()

pygame.quit()