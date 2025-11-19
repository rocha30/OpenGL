from OpenGL.GL import *
from obj import Obj
from buffer import Buffer

import glm

import pygame

class Model(object):
	def __init__(self, filename):
		self.objFile = Obj(filename)

		self.position = glm.vec3(0,0,0)
		self.rotation = glm.vec3(0,0,0)
		self.scale = glm.vec3(1,1,1)

		self.BuildBuffers()

		self.textures = []

		self.visible = True
		
		# Shaders específicos de este modelo (None = usar shaders globales del renderer)
		self.vertexShader = None
		self.fragmentShader = None
		
		# Parámetros personalizados del shader para este modelo
		self.shaderValue = 0.5  # Valor general (para deformaciones, efectos, etc.)
		self.shaderColor = glm.vec3(1.0, 1.0, 1.0)  # Color personalizado
		self.useCustomColor = False  # Si debe usar el color personalizado


	def GetModelMatrix(self):

		identity = glm.mat4(1)

		translateMat = glm.translate(identity, self.position)

		pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
		yawMat =   glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
		rollMat =  glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

		rotationMat = pitchMat * yawMat * rollMat

		scaleMat = glm.scale(identity, self.scale)

		return translateMat * rotationMat * scaleMat


	def BuildBuffers(self):

		positions = []
		texCoords = []
		normals = []

		self.vertexCount = 0

		for face in self.objFile.faces:

			facePositions = []
			faceTexCoords = []
			faceNormals = []

			for i in range(len(face)):
				# Posiciones (siempre requeridas)
				facePositions.append( self.objFile.vertices [ face[i][0] - 1 ] )
				
				# Coordenadas de textura (opcionales, usar [0,0] si no existen)
				if len(face[i]) > 1 and face[i][1] > 0 and len(self.objFile.texCoords) > 0:
					faceTexCoords.append( self.objFile.texCoords[ face[i][1] - 1 ] )
				else:
					faceTexCoords.append([0.0, 0.0])  # Default UV
				
				# Normales (opcionales, usar [0,1,0] si no existen)
				if len(face[i]) > 2 and face[i][2] > 0 and len(self.objFile.normals) > 0:
					faceNormals.append( self.objFile.normals[ face[i][2] - 1 ] )
				else:
					faceNormals.append([0.0, 1.0, 0.0])  # Default normal (apuntando arriba)


			for value in facePositions[0]: positions.append(value)
			for value in facePositions[1]: positions.append(value)
			for value in facePositions[2]: positions.append(value)

			for value in faceTexCoords[0]: texCoords.append(value)
			for value in faceTexCoords[1]: texCoords.append(value)
			for value in faceTexCoords[2]: texCoords.append(value)

			for value in faceNormals[0]: normals.append(value)
			for value in faceNormals[1]: normals.append(value)
			for value in faceNormals[2]: normals.append(value)

			self.vertexCount += 3

			if len(face) == 4:
				for value in facePositions[0]: positions.append(value)
				for value in facePositions[2]: positions.append(value)
				for value in facePositions[3]: positions.append(value)

				for value in faceTexCoords[0]: texCoords.append(value)
				for value in faceTexCoords[2]: texCoords.append(value)
				for value in faceTexCoords[3]: texCoords.append(value)

				for value in faceNormals[0]: normals.append(value)
				for value in faceNormals[2]: normals.append(value)
				for value in faceNormals[3]: normals.append(value)

				self.vertexCount += 3


		self.posBuffer = Buffer(positions)
		self.texCoordsBuffer = Buffer(texCoords)
		self.normalsBuffer = Buffer(normals)


	def AddTexture(self, filename):
		textureSurface = pygame.image.load(filename)
		textureData = pygame.image.tostring(textureSurface, "RGB", True)

		texture = glGenTextures(1)
		glBindTexture(GL_TEXTURE_2D, texture)

		glTexImage2D(GL_TEXTURE_2D,
					 0,
					 GL_RGB,
					 textureSurface.get_width(),
					 textureSurface.get_height(),
					 0,
					 GL_RGB,
					 GL_UNSIGNED_BYTE,
					 textureData)

		glGenerateMipmap(GL_TEXTURE_2D)

		self.textures.append(texture)


	def Render(self):

		if not self.visible:
			return

		# Dar la textura
		for i in range(len(self.textures)):
			glActiveTexture(GL_TEXTURE0 + i)
			glBindTexture(GL_TEXTURE_2D, self.textures[i])


		self.posBuffer.Use(1, 3)
		self.texCoordsBuffer.Use(0, 2)
		self.normalsBuffer.Use(2, 3)


		glDrawArrays(GL_TRIANGLES, 0, self.vertexCount)

		glDisableVertexAttribArray(0)
		glDisableVertexAttribArray(1)
		glDisableVertexAttribArray(2)







