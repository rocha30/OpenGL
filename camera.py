import glm
from math import sin, cos, radians, sqrt

# Utility
def clamp(v, vmin, vmax):
	return max(vmin, min(vmax, v))

class Camera(object):
	def __init__(self, width, height):

		self.screenWidth = width
		self.screenHeight = height
		
		self.position = glm.vec3(0,0,0)

		# Angulos de Euler
		self.rotation = glm.vec3(0,0,0)

		self.viewMatrix = None

		self.CreateProjectionMatrix(60, 0.1, 1000)

		self.usingLookAt = False


	def Update(self):
		# M = T * R
		# R = pitchMat * yawMat * rollMat

		if not self.usingLookAt:
			identity = glm.mat4(1)

			translateMat = glm.translate(identity, self.position)

			pitchMat = glm.rotate(identity, glm.radians(self.rotation.x), glm.vec3(1,0,0))
			yawMat =   glm.rotate(identity, glm.radians(self.rotation.y), glm.vec3(0,1,0))
			rollMat =  glm.rotate(identity, glm.radians(self.rotation.z), glm.vec3(0,0,1))

			rotationMat = pitchMat * yawMat * rollMat

			camMat = translateMat * rotationMat

			self.viewMatrix = glm.inverse(camMat)

		self.usingLookAt = False


	def CreateProjectionMatrix(self, fov, nearPlane, farPlane):
		self.projectionMatrix = glm.perspective( glm.radians(fov), self.screenWidth / self.screenHeight, nearPlane, farPlane)


	def LookAt(self, center):
		self.usingLookAt = True
		self.viewMatrix = glm.lookAt(self.position, center, glm.vec3(0,1,0) )


	def Orbit(self, center, distance, angle):

		self.position.x = center.x + sin(radians(angle) ) * distance
		self.position.z = center.z + cos(radians(angle) ) * distance


class ArcballOrbit:
	"""
	Arcball-style orbit controller bound to a Camera instance.
	Keeps the camera looking at a target, with spherical coordinates:
	  radius (with min/max), theta (azimuth), phi (elevation with clamps)
	Provides helpers to frame a model (compute AABB from its OBJ data).
	"""

	def __init__(self, camera: Camera):
		self.camera = camera
		self.target = glm.vec3(0, 0, 0)
		# Spherical params
		self.radius = 10.0
		self.radiusMin = 1.0
		self.radiusMax = 200.0
		self.theta = 0.0                 # radians
		self.phi = radians(35.0)         # radians
		self.phiMin = radians(5.0)
		self.phiMax = radians(85.0)

	def set_target(self, target: glm.vec3):
		self.target = glm.vec3(target)

	def on_mouse_drag(self, dx: float, dy: float, sensitivity: float = 0.01):
		self.theta += dx * sensitivity
		self.phi   -= dy * sensitivity
		self.phi = clamp(self.phi, self.phiMin, self.phiMax)

	def on_scroll(self, delta: float, zoomSpeed: float = 1.5):
		# Positive delta typically means scroll up; keep same convention as app
		self.radius -= delta * zoomSpeed
		self.radius = clamp(self.radius, self.radiusMin, self.radiusMax)

	def on_keys(self, keys, deltaTime: float):
		# Pygame key constants are available in caller; we avoid importing here
		from pygame.locals import K_LEFT, K_RIGHT, K_UP, K_DOWN, K_MINUS, K_EQUALS
		if keys[K_LEFT]:
			self.theta -= 1.2 * deltaTime
		if keys[K_RIGHT]:
			self.theta += 1.2 * deltaTime
		if keys[K_UP]:
			self.phi -= 1.2 * deltaTime
		if keys[K_DOWN]:
			self.phi += 1.2 * deltaTime
		self.phi = clamp(self.phi, self.phiMin, self.phiMax)
		if keys[K_MINUS]:
			self.radius += 8.0 * deltaTime
		if keys[K_EQUALS]:
			self.radius -= 8.0 * deltaTime
		self.radius = clamp(self.radius, self.radiusMin, self.radiusMax)

	def apply(self):
		# Compute eye from spherical coords and look at target
		eye = glm.vec3(
			self.target.x + self.radius * sin(self.theta) * sin(self.phi),
			self.target.y + self.radius * cos(self.phi),
			self.target.z + self.radius * cos(self.theta) * sin(self.phi)
		)
		self.camera.position = eye
		self.camera.LookAt(self.target)

	@staticmethod
	def compute_model_bounds(model):
		"""Return (center, size) of the model's AABB in model space."""
		verts = getattr(model.objFile, 'vertices', None)
		if not verts:
			return glm.vec3(0, 0, 0), glm.vec3(1, 1, 1)
		minv = glm.vec3(verts[0][0], verts[0][1], verts[0][2])
		maxv = glm.vec3(minv)
		for v in verts:
			minv.x = min(minv.x, v[0]); minv.y = min(minv.y, v[1]); minv.z = min(minv.z, v[2])
			maxv.x = max(maxv.x, v[0]); maxv.y = max(maxv.y, v[1]); maxv.z = max(maxv.z, v[2])
		center = (minv + maxv) * 0.5
		size = (maxv - minv)
		return center, size

	def frame_model(self, model):
		"""Set target and radius to frame the given model based on its AABB and scale."""
		center, size = self.compute_model_bounds(model)
		scaleMax = max(model.scale.x, model.scale.y, model.scale.z)
		diag = sqrt(size.x*size.x + size.y*size.y + size.z*size.z) * scaleMax
		desired = max(self.radiusMin, diag * 0.8)
		self.radius = clamp(desired, self.radiusMin, self.radiusMax)
		self.target = glm.vec3(model.position + center * scaleMax)