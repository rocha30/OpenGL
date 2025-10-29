import pygame
import pygame.display
from pygame.locals import *
import glm
from gl import Renderer
from buffer import Buffer
from model import Model
from vertexShaders import *
from fragmentShaders import *

from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader


width = 960
height = 540

deltaTime = 0.0


screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF | pygame.OPENGL)
clock = pygame.time.Clock()


rend = Renderer(screen)
rend.pointLight = glm.vec3(1,1,1)
rend.value = 0.7

currVertexShader = simpleVertex_shader
currFragmentShader = fragment_shader

rend.SetShaders(currVertexShader, currFragmentShader)

skyboxTextures = ["Yokohama2/right.jpg",
				  "Yokohama2/left.jpg",
				  "Yokohama2/up.jpg",
				  "Yokohama2/down.jpg",
				  "Yokohama2/front.jpg",
				  "Yokohama2/back.jpg"]

rend.CreateSkybox(skyboxTextures)


faceModel = Model("Centaur_Male_Lores.obj")
faceModel.AddTexture("magm_texture.jpg")
faceModel.position.z = -5
faceModel.scale = glm.vec3(0.01,0.01,0.01)

rend.scene.append(faceModel)

isRunning = True
while isRunning:

	deltaTime = clock.tick(60) / 1000

	rend.elapsedTime += deltaTime

	keys = pygame.key.get_pressed()

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			isRunning = False

		elif event.type == pygame.KEYDOWN:
			if event.key == pygame.K_f:
				rend.ToggleFilledMode()

			if event.key == pygame.K_1:
				currVertexShader = vertex_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_2:
				currVertexShader = twist_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_3:
				currVertexShader = bend_ripple_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_4:
				currVertexShader = explode_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_5:
				currVertexShader = noise_disp_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			# Fragment Shader Controls
			if event.key == pygame.K_6:
				currFragmentShader = fragment_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_7:
				currFragmentShader = halftone_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_8:
				currFragmentShader = dissolve_shader
				rend.SetShaders(currVertexShader, currFragmentShader)

			if event.key == pygame.K_9:
				currFragmentShader = pulsating_energy_shader
				rend.SetShaders(currVertexShader, currFragmentShader)


			# Controles para ajustar efectos
			if event.key == pygame.K_q:
				rend.value += 0.2
				print(f"Effect value: {rend.value:.2f}")

			if event.key == pygame.K_a:
				rend.value -= 0.2
				print(f"Effect value: {rend.value:.2f}")

			if event.key == pygame.K_e:
				rend.value = 0.0  # Reset effect
				print(f"Effect reset: {rend.value:.2f}")


	if keys[K_UP]:
		rend.camera.position.z += 1 * deltaTime

	if keys[K_DOWN]:
		rend.camera.position.z -= 1 * deltaTime

	if keys[K_RIGHT]:
		rend.camera.position.x += 1 * deltaTime

	if keys[K_LEFT]:
		rend.camera.position.x -= 1 * deltaTime



	if keys[K_w]:
		rend.pointLight.z -= 10 * deltaTime

	if keys[K_s]:
		rend.pointLight.z += 10 * deltaTime

	if keys[K_a]:
		rend.pointLight.x -= 10 * deltaTime

	if keys[K_d]:
		rend.pointLight.x += 10 * deltaTime

	if keys[K_q]:
		rend.pointLight.y -= 10 * deltaTime

	if keys[K_e]:
		rend.pointLight.y += 10 * deltaTime


	if keys[K_z]:
		if rend.value == 1:
			rend.value -= 1 * deltaTime

	if keys[K_x]:
		if rend.value < 1.0:
			rend.value += 1 * deltaTime



	faceModel.rotation.y += 15 * deltaTime


	rend.Render()
	pygame.display.flip()

pygame.quit()