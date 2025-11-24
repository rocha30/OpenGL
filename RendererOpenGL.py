import pygame
import pygame.display
from pygame.locals import *

import glm
import math

from OpenGL.GL import *  # Importar funciones de OpenGL para la UI

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

# Configurar fuente para UI en pantalla
pygame.font.init()
uiFont = pygame.font.SysFont('Arial', 18)
uiFontSmall = pygame.font.SysFont('Arial', 14)


rend = Renderer(screen)

# pygame.mixer.init()
# pygame.mixer.music.load("music.mp3")
# pygame.mixer.music.play(-1)  # Loop infinito
# musicEnabled = False  # Cambiar a True cuando tengas el archivo

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

# ============================================================
# DIORAMA: "BATALLA ÉPICA EN EL COLISEO"
# 5 modelos posicionados artísticamente, cada uno con shaders únicos
# ============================================================

#############################
# MODELOS DEL DIORAMA
#############################
# Piso base
floor = Model("plane.obj")
floor.AddTexture("planetextures.jpeg")
floor.scale = glm.vec3(0.3, 0.3, 0.3)
floor.position = glm.vec3(0.0, -3.5, -8.0)
floor.rotation.x = 200
floor.vertexShader = vertex_shader
floor.fragmentShader = fragment_shader
floor.shaderValue = 0.0
floor.visible = True

# Centauro
centaur = Model("Centaur_Male_Lores.obj")
centaur.AddTexture("dragonScames.png")
centaur.AddTexture("magm_texture.jpg")
centaur.scale = glm.vec3(0.012, 0.012, 0.012)
centaur.position = glm.vec3(0.0, 0.0, -8.0)
centaur.vertexShader = twist_shader
centaur.fragmentShader = pulsating_energy_shader
centaur.shaderValue = 0.3
centaur.visible = True

# Minecraft
minecraft = Model("Minecraft_cartoon_head.obj")
minecraft.AddTexture("skinsteve.png")
minecraft.scale = glm.vec3(0.3, 0.3, 0.3)
minecraft.position = glm.vec3(-3.0, 0.0, -7.0)
minecraft.vertexShader = explode_shader
minecraft.fragmentShader = dissolve_shader
minecraft.shaderValue = 0.2
minecraft.visible = True

# Third creature
third = Model("3obj.obj")
third.AddTexture("skin.jpg")
third.scale = glm.vec3(7.5, 7.5, 7.5)
third.position = glm.vec3(3.0, 0.0, -7.0)
third.vertexShader = water_shader
third.fragmentShader = halftone_shader
third.shaderValue = 0.15
third.visible = True

# Statue
statue = Model("statue.obj")
statue.AddTexture("statutexture.jpg")
statue.scale = glm.vec3(12.0, 12.0, 12.0)
statue.position = glm.vec3(-2.5, 0.0, -9.0)
statue.vertexShader = vertex_shader
statue.fragmentShader = fragment_shader
statue.shaderValue = 0.25
statue.rotation.y = 0
statue.visible = True

FLOOR_SURFACE_Y = 10
for m in [centaur, minecraft, third, statue]:
    model_bottom_local = m.minY * m.scale.y
    m.position.y = FLOOR_SURFACE_Y - model_bottom_local + 0.15

## Distribución
centaur.position.x = 0.0
centaur.position.z = -7.0
minecraft.position.x = -3.0
minecraft.position.z = -8.0
third.position.x = 3.0
third.position.z = -8.0
statue.position.x = 0.0
statue.position.z = -9.0



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

# Agregar modelos a la escena
rend.scene.append(centaur)
rend.scene.append(minecraft)
rend.scene.append(third)
rend.scene.append(floor)
rend.scene.append(statue)

## Arcball Camera
activeModelIndex = 0

def get_active_model():
	return rend.scene[activeModelIndex]

# Nombres para UI
modelNames = [
	"Centauro (Guerrero Principal)",
	"Cabeza Minecraft (Guardián)",
	"Criatura Secundaria",
	"Piso/Arena del Coliseo",
	"Estatua Decorativa"
]

arcball = ArcballOrbit(rend.camera)
arcball.frame_model(get_active_model())

# Variables de UI
showUI = True

def draw_ui_overlay():
	"""Dibuja información en pantalla sobre el modelo actual y controles"""
	if not showUI:
		return

	activeModel = get_active_model()
	modelName = modelNames[activeModelIndex]

	lines = [
		"DIORAMA: Batalla Épica en el Coliseo",
		f"Modelo activo: {modelName} ({activeModelIndex+1}/5)",
		"Teclas: 1-5 modelos | Q todos | E solo activo",
		"Z/X valor shader | TAB post-proceso | H UI"
	]

	glMatrixMode(GL_PROJECTION)
	glPushMatrix()
	glLoadIdentity()
	glOrtho(0, width, height, 0, -1, 1)
	glMatrixMode(GL_MODELVIEW)
	glPushMatrix()
	glLoadIdentity()

	glDisable(GL_DEPTH_TEST)
	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)

	# Fondo
	glColor4f(0,0,0,0.55)
	glBegin(GL_QUADS)
	glVertex2f(8,8)
	glVertex2f(380,8)
	glVertex2f(380,8+len(lines)*22+10)
	glVertex2f(8,8+len(lines)*22+10)
	glEnd()

	y = 15
	for idx, text in enumerate(lines):
		color = (255,255,120) if idx == 0 else (255,255,255)
		fontSurf = uiFont.render(text, True, color)
		px = pygame.image.tostring(fontSurf, 'RGBA', True)
		glRasterPos2f(15, y)
		glDrawPixels(fontSurf.get_width(), fontSurf.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, px)
		y += fontSurf.get_height() + 4

	glDisable(GL_BLEND)
	glEnable(GL_DEPTH_TEST)
	glPopMatrix()
	glMatrixMode(GL_PROJECTION)
	glPopMatrix()
	glMatrixMode(GL_MODELVIEW)

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

			# Teclas 1-5: Enfocar cámara (todos visibles)
			if event.key == pygame.K_1:
				if len(rend.scene) >= 1:
					activeModelIndex = 0
					arcball.frame_model(get_active_model())
					model = get_active_model()
					print(f"\n[ENFOQUE MODELO {activeModelIndex+1}] {modelNames[activeModelIndex]}")
					print(f"  Posición: {model.position}")
					print(f"  Escala: {model.scale}\n")
					
			if event.key == pygame.K_2:
				if len(rend.scene) >= 2:
					activeModelIndex = 1
					arcball.frame_model(get_active_model())
					model = get_active_model()
					print(f"\n[ENFOQUE MODELO {activeModelIndex+1}] {modelNames[activeModelIndex]}")
					print(f"  Posición: {model.position}")
					print(f"  Escala: {model.scale}\n")
					
			if event.key == pygame.K_3:
				if len(rend.scene) >= 3:
					activeModelIndex = 2
					arcball.frame_model(get_active_model())
					model = get_active_model()
					print(f"\n[ENFOQUE MODELO {activeModelIndex+1}] {modelNames[activeModelIndex]}")
					print(f"  Posición: {model.position}")
					print(f"  Escala: {model.scale}\n")
					
			if event.key == pygame.K_4:
				if len(rend.scene) >= 4:
					activeModelIndex = 3
					arcball.frame_model(get_active_model())
					model = get_active_model()
					print(f"\n[ENFOQUE MODELO {activeModelIndex+1}] {modelNames[activeModelIndex]}")
					print(f"  Posición: {model.position}")
					print(f"  Escala: {model.scale}\n")
					
			if event.key == pygame.K_5:
				if len(rend.scene) >= 5:
					activeModelIndex = 4
					arcball.frame_model(get_active_model())
					model = get_active_model()
					print(f"\n[ENFOQUE MODELO {activeModelIndex+1}] {modelNames[activeModelIndex]}")
					print(f"  Posición: {model.position}")
					print(f"  Escala: {model.scale}\n")
				print(f"[MODELO] Mostrando solo: {modelNames[activeModelIndex]}")
			
			# Tecla H: Toggle UI overlay
			if event.key == pygame.K_h:
				showUI = not showUI
				print(f"[UI] {'Activada' if showUI else 'Desactivada'}")
			
			# Tecla M: Toggle música (mutear/unmutear)
			if event.key == pygame.K_m:
				if pygame.mixer.music.get_busy():
					pygame.mixer.music.pause()
					print("[MÚSICA] Pausada")
				else:
					pygame.mixer.music.unpause()
					print("[MÚSICA] Reanudada")


	# Controles para ajustar el efecto del shader del modelo activo
	if keys[K_z]:
		activeModel = get_active_model()
		if activeModel.shaderValue > 0.0:
			activeModel.shaderValue -= 0.5 * deltaTime
			activeModel.shaderValue = max(0.0, activeModel.shaderValue)

	if keys[K_x]:
		activeModel = get_active_model()
		if activeModel.shaderValue < 1.0:
			activeModel.shaderValue += 0.5 * deltaTime
			activeModel.shaderValue = min(1.0, activeModel.shaderValue)

	# Arcball con mouse: LMB rotación (theta/phi)
	if pygame.mouse.get_pressed()[0]:
		arcball.on_mouse_drag(mouseVel[0], mouseVel[1])

	# Arcball con teclado
	arcball.on_keys(keys, deltaTime)

	# Aplicar cámara (LookAt al target)
	arcball.apply()

	rend.Render()
	
	# Dibujar UI overlay sobre la escena 3D
	draw_ui_overlay()
	
	pygame.display.flip()

pygame.quit()