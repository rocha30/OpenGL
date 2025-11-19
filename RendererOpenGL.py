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

# MODELO 1: Centauro (guerrero principal) - Center stage
# Shaders: Twist + Pulsating Energy (efecto de poder divino)
centaur = Model("Centaur_Male_Lores.obj")
centaur.AddTexture("dragonScames.png")
centaur.AddTexture("magm_texture.jpg")
centaur.position = glm.vec3(0, 0.5, -7)  # Centro frontal, sobre el plano
centaur.scale = glm.vec3(0.5, 0.5, 0.5)
centaur.vertexShader = twist_shader  # Deformación de espiral
centaur.fragmentShader = pulsating_energy_shader  # Energía azul pulsante
centaur.shaderValue = 0.3  # Twist suave
centaur.visible = True

# MODELO 2: Minecraft Head (Guardian místico) - Izquierda
# Shaders: Explode + Dissolve (apareciendo/desapareciendo)
minecraft = Model("Minecraft_cartoon_head.obj")
minecraft.AddTexture("skinsteve.png")
minecraft.position = glm.vec3(-2.5, 0.5, -8.5)  # Izquierda trasera, sobre plataforma
minecraft.scale = glm.vec3(0.8, 0.8, 0.8)
minecraft.vertexShader = explode_shader  # Ondas de explosión
minecraft.fragmentShader = dissolve_shader  # Efecto de disolución
minecraft.shaderValue = 0.2  # Explosión sutil
minecraft.visible = False

# MODELO 3: Objeto 3 (Criatura secundaria) - Derecha
# Shaders: Water + Halftone (estilo cómic animado)
third = Model("3obj.obj")
third.AddTexture("skin.jpg")
third.position = glm.vec3(2.5, 0.5, -8.5)  # Derecha trasera, sobre plataforma
third.scale = glm.vec3(0.7, 0.7, 0.7)
third.vertexShader = water_shader  # Ondulación acuática
third.fragmentShader = halftone_shader  # Efecto de cómic
third.shaderValue = 0.15  # Ondulación suave
third.visible = False

# MODELO 4: Piso/Base del diorama - Arena del coliseo
# Shaders: Basic + Toon (piso simple con iluminación cel-shaded)
floor = Model("plane.obj")
floor.AddTexture("planetextures.jpeg")
floor.position = glm.vec3(0, -0.5, -8)  # Base del diorama - mismo nivel que los pies
floor.scale = glm.vec3(4.0, 1.0, 4.0)  # Plataforma plana (ancho x altura x profundo)
floor.rotation.x = 0  # Sin rotación
floor.rotation.y = 180  # Voltear en Y para corregir textura
floor.vertexShader = vertex_shader  # Shader básico sin deformación
floor.fragmentShader = fragment_shader  # Shader básico con textura
floor.shaderValue = 0.0
floor.visible = False

# MODELO 5: Elemento decorativo - Estatua
# Shaders: Bend_Ripple + Magma (estatua ondulante con efecto de lava)
statue = Model("statue.obj")
statue.AddTexture("statutexture.jpg")
statue.position = glm.vec3(0, 0.5, -9.5)  # Fondo centro, sobre plataforma
statue.scale = glm.vec3(0.9, 0.9, 0.9)  # Tamaño visible
statue.rotation.y = 0  # Sin rotación para ver de frente
statue.vertexShader = vertex_shader  # Básico primero para ver bien
statue.fragmentShader = fragment_shader  # Básico para debug
statue.shaderValue = 0.25
statue.visible = False



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

# Agregar todos los modelos a la escena en el orden correcto
# Orden: [0]=Centaur, [1]=Minecraft, [2]=Third, [3]=Floor, [4]=Statue
rend.scene.append(centaur)
rend.scene.append(minecraft)
rend.scene.append(third)
rend.scene.append(floor)
rend.scene.append(statue)

# ===== Arcball Camera (órbita alrededor del modelo activo) =====
activeModelIndex = 0

def get_active_model():
	return rend.scene[activeModelIndex]

# Nombres de los modelos para UI
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
	
	# Guardar estado de OpenGL
	glMatrixMode(GL_PROJECTION)
	glPushMatrix()
	glLoadIdentity()
	glOrtho(0, width, height, 0, -1, 1)
	glMatrixMode(GL_MODELVIEW)
	glPushMatrix()
	glLoadIdentity()
	glDisable(GL_DEPTH_TEST)
	glDisable(GL_LIGHTING)
	glEnable(GL_BLEND)
	glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
	
	# Información del modelo actual
	activeModel = get_active_model()
	modelName = modelNames[activeModelIndex]
	shaderValue = activeModel.shaderValue
	
	# Renderizar textos
	try:
		musicStatus = "♪ ON" if pygame.mixer.music.get_busy() else "♪ OFF"
	except:
		musicStatus = "♪ --"
	
	texts = [
		f"DIORAMA: Batalla Épica en el Coliseo {musicStatus}",
		f"Modelo: {modelName} ({activeModelIndex + 1}/5)",
		f"Shader Value: {shaderValue:.2f}",
		"",
		"CONTROLES:",
		"1-5: Cambiar modelo | Q: Mostrar todos | E: Mostrar solo activo",
		"Z/X: Ajustar efecto shader | TAB: Post-proceso | M: Música",
		"Mouse: LMB=orbitar | Rueda=zoom",
		"Flechas: Orbitar | -/=: Zoom | H: Toggle UI"
	]
	
	y_offset = 10
	for i, text in enumerate(texts):
		if i == 0:  # Título
			textSurface = uiFont.render(text, True, (255, 255, 100))
		elif i <= 2:  # Info del modelo
			textSurface = uiFont.render(text, True, (255, 255, 255))
		else:  # Controles
			textSurface = uiFontSmall.render(text, True, (200, 200, 200))
		
		textData = pygame.image.tostring(textSurface, "RGBA", True)
		glRasterPos2f(10, y_offset)
		glDrawPixels(textSurface.get_width(), textSurface.get_height(),
					 GL_RGBA, GL_UNSIGNED_BYTE, textData)
		y_offset += textSurface.get_height() + 2
	
	# Restaurar estado de OpenGL
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

			# Model switch: 1/2/3/4/5 (solo uno visible, cambiar foco de cámara)
			if event.key == pygame.K_1:
				if len(rend.scene) >= 1:
					activeModelIndex = 0
					for i, obj in enumerate(rend.scene):
						obj.visible = (i == activeModelIndex)
					arcball.frame_model(get_active_model())
					model = get_active_model()
					print(f"\n[MODELO {activeModelIndex+1}] {modelNames[activeModelIndex]}")
					print(f"  Posición: {model.position}")
					print(f"  Escala: {model.scale}")
					print(f"  Visible: {model.visible}\n")
					
			if event.key == pygame.K_2:
				if len(rend.scene) >= 2:
					activeModelIndex = 1
					for i, obj in enumerate(rend.scene):
						obj.visible = (i == activeModelIndex)
					arcball.frame_model(get_active_model())
					model = get_active_model()
					print(f"\n[MODELO {activeModelIndex+1}] {modelNames[activeModelIndex]}")
					print(f"  Posición: {model.position}")
					print(f"  Escala: {model.scale}")
					print(f"  Visible: {model.visible}\n")
					
			if event.key == pygame.K_3:
				if len(rend.scene) >= 3:
					activeModelIndex = 2
					for i, obj in enumerate(rend.scene):
						obj.visible = (i == activeModelIndex)
					arcball.frame_model(get_active_model())
					model = get_active_model()
					print(f"\n[MODELO {activeModelIndex+1}] {modelNames[activeModelIndex]}")
					print(f"  Posición: {model.position}")
					print(f"  Escala: {model.scale}")
					print(f"  Visible: {model.visible}\n")
					
			if event.key == pygame.K_4:
				if len(rend.scene) >= 4:
					activeModelIndex = 3
					for i, obj in enumerate(rend.scene):
						obj.visible = (i == activeModelIndex)
					arcball.frame_model(get_active_model())
					model = get_active_model()
					print(f"\n[MODELO {activeModelIndex+1}] {modelNames[activeModelIndex]}")
					print(f"  Posición: {model.position}")
					print(f"  Escala: {model.scale}")
					print(f"  Visible: {model.visible}\n")
					
			if event.key == pygame.K_5:
				if len(rend.scene) >= 5:
					activeModelIndex = 4
					for i, obj in enumerate(rend.scene):
						obj.visible = (i == activeModelIndex)
					arcball.frame_model(get_active_model())
					model = get_active_model()
					print(f"\n[MODELO {activeModelIndex+1}] {modelNames[activeModelIndex]}")
					print(f"  Posición: {model.position}")
					print(f"  Escala: {model.scale}")
					print(f"  Visible: {model.visible}\n")
			
			# Tecla Q: Mostrar todos los modelos a la vez (para ver el diorama completo)
			if event.key == pygame.K_q:
				for obj in rend.scene:
					obj.visible = True
				print("[DIORAMA] Mostrando todos los modelos")
			
			# Tecla E: Volver al modo de un solo modelo
			if event.key == pygame.K_e:
				for i, obj in enumerate(rend.scene):
					obj.visible = (i == activeModelIndex)
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