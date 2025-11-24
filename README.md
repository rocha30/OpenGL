# Diorama OpenGL – Batalla Épica

Proyecto 3D con Python + PyOpenGL (GLSL 120) mostrando 5 modelos siempre visibles, cámara orbital, shaders por modelo y efectos de post‑proceso.

## Ejecutar
```bash
conda activate py38 && python RendererOpenGL.py
```

## Modelos
Centauro | Cabeza Minecraft | Criatura secundaria | Piso | Estatua.
Todos visibles simultáneamente; las teclas 1‑5 solo enfocan la cámara.

## Controles
1..5: Enfocar cámara en modelo
LMB arrastrar: Orbitar
Rueda: Zoom
Z / X: Ajustar shaderValue del modelo enfocado
TAB: Ciclar post‑proceso
H: Mostrar/ocultar UI
M: Pausar/Reanudar música (opcional)

## Shaders (ejemplos)
Centauro: twist + pulsating_energy
Minecraft: explode + dissolve
Criatura: water + halftone
Estatua / Piso: básicos

## Post‑Proceso
None, GrayScale, Negative, Hurt, Depth, Fog, DoF, EdgeDetection, Outline.

## Arquitectura
`RendererOpenGL.py` (loop y escena)  
`gl.py` (renderer, skybox, post‑proceso)  
`model.py` (carga OBJ, shaders por instancia)  
`vertexShaders.py` / `fragmentShaders.py` (colección GLSL)  
`postProcessingShaders.py` (efectos pantalla completa)  
`camera.py` (ArcballOrbit)  

## Notas Técnicas
OpenGL 2.1 (GLSL 120) para compatibilidad macOS.  
Cada modelo define `vertexShader`, `fragmentShader`, `shaderValue`.  
`FLOOR_SURFACE_Y = 10` eleva los modelos sobre el piso escalado.  

## Dependencias
```bash
pip install pygame PyOpenGL PyOpenGL_accelerate PyGLM numpy
```

## Personalización rápida
```python
centaur.vertexShader = explode_shader
centaur.fragmentShader = halftone_shader
centaur.shaderValue = 0.5
```

## Créditos
Uso educativo. Modelos y texturas externos.  
Autor: Mario Rocha – Nov 2025