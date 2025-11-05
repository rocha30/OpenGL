import pygame
import pygame.display
from pygame.locals import *

import glm
import math

from gl import Renderer
from camera import ArcballOrbit
from buffer import Buffer
from model import Model
from vertexShaders import *
from fragmentShaders import *
from postProcessingShaders import *

width = 960
height = 540

deltaTime = 0.0


screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()


rend = Renderer(screen)
rend.pointLight = glm.vec3(1,1,1)
rend.ambientLight = 0.3  # brighten to ensure visibility while debugging

currVertexShader = vertex_shader
currFragmentShader = fragment_shader

rend.SetShaders(currVertexShader, currFragmentShader)

rend.SetPostProcessingShaders(vertex_postProcess, none_postProcess)



skyboxTextures = ["Yokohama2/right.jpg",
				  "Yokohama2/left.jpg",
				  "Yokohama2/up.jpg",
				  "Yokohama2/down.jpg",
				  "Yokohama2/front.jpg",
				  "Yokohama2/back.jpg"]

rend.CreateSkybox(skyboxTextures)


centaur = Model("Centaur_Male_Lores.obj")
centaur.AddTexture("dragonScames.png")
centaur.AddTexture("magm_texture.jpg")
centaur.position.z = -5
centaur.scale = glm.vec3(0.5,0.5,0.5)
centaur.visible = True

# Segundo modelo
minecraft = Model("Minecraft_cartoon_head.obj")
minecraft.AddTexture("skinsteve.png")
minecraft.position.z = -5
minecraft.scale = glm.vec3(1.0,1.0,1.0)
minecraft.visible = False

# Tercer modelo
third = Model("3obj.obj")
third.AddTexture("skin.jpg")
third.position.z = -5
third.scale = glm.vec3(1.0,1.0,1.0)
third.visible = False



modelIndex = 0
postProcessIndex = 0

postProcesses = [none_postProcess,
				 grayScale_postProcess,
				 negative_postProcess,
				 hurt_postProcess,
				 depth_postProcess,
				 fog_postProcess,
				 dof_postProcess,
				 edgeDetection_postProcess,
				 outline_postProcess]

camAngle = 0

rend.scene.append(centaur)
# Agregar los otros modelos a la escena
rend.scene.append(minecraft)
rend.scene.append(third)

# ===== Arcball Camera (órbita alrededor del modelo activo) =====
activeModelIndex = 0

def get_active_model():
	return rend.scene[activeModelIndex]

arcball = ArcballOrbit(rend.camera)
arcball.frame_model(get_active_model())

isRunning = True

while isRunning:

	deltaTime = clock.tick(60) / 1000

	rend.elapsedTime += deltaTime

	keys = pygame.key.get_pressed()
	mouseVel = pygame.mouse.get_rel()


	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			isRunning = False


		elif event.type == pygame.MOUSEBUTTONDOWN:
			if pygame.mouse.get_pressed()[2]:
				modelIndex += 1
				modelIndex %= len(rend.scene)
				for i in range(len(rend.scene)):
					rend.scene[i].visible = i == modelIndex


		elif event.type == pygame.MOUSEWHEEL:
			# Zoom con rueda (ajusta el radio de órbita)
			arcball.on_scroll(event.y)


		elif event.type == pygame.KEYDOWN:
			# (Removed unused keys F and R per request)


			if event.key == pygame.K_TAB:
				postProcessIndex += 1
				postProcessIndex %= len(postProcesses)
				rend.SetPostProcessingShaders(vertex_postProcess, postProcesses[postProcessIndex])

			# Model switch: 1/2/3 (solo uno visible)
			if event.key == pygame.K_1:
				if len(rend.scene) >= 1:
					activeModelIndex = 0
					for i, obj in enumerate(rend.scene):
						obj.visible = (i == activeModelIndex)
					arcball.frame_model(get_active_model())
			if event.key == pygame.K_2:
				if len(rend.scene) >= 2:
					activeModelIndex = 1
					for i, obj in enumerate(rend.scene):
						obj.visible = (i == activeModelIndex)
					arcball.frame_model(get_active_model())
			if event.key == pygame.K_3:
				if len(rend.scene) >= 3:
					activeModelIndex = 2
					for i, obj in enumerate(rend.scene):
						obj.visible = (i == activeModelIndex)
					arcball.frame_model(get_active_model())

			# Fragment shaders remapeados
			if event.key == pygame.K_4:
				currFragmentShader = fragment_shader
				rend.SetShaders(currVertexShader, currFragmentShader)
			if event.key == pygame.K_5:
				currFragmentShader = toon_shader
				rend.SetShaders(currVertexShader, currFragmentShader)
			if event.key == pygame.K_6:
				currFragmentShader = negative_shader
				rend.SetShaders(currVertexShader, currFragmentShader)
			if event.key == pygame.K_m:
				currFragmentShader = magma_shader
				rend.SetShaders(currVertexShader, currFragmentShader)


			if event.key == pygame.K_7:
				currVertexShader = vertex_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_8:
				currVertexShader = fat_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_9:
				currVertexShader = water_shader
				rend.SetShaders(currVertexShader, currFragmentShader)


	if keys[K_z]:
		if rend.value > 0.0:
			rend.value -= 1 * deltaTime

	if keys[K_x]:
		if rend.value < 1.0:
			rend.value += 1 * deltaTime

	# Arcball con mouse: LMB rotación (theta/phi)
	if pygame.mouse.get_pressed()[0]:
		arcball.on_mouse_drag(mouseVel[0], mouseVel[1])

	# Arcball con teclado
	arcball.on_keys(keys, deltaTime)

	# Aplicar cámara (LookAt al target)
	arcball.apply()

	rend.Render()
	pygame.display.flip()

pygame.quit()