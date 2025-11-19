# 🎮 OpenGL Diorama - "Batalla Épica en el Coliseo"

Proyecto de diorama 3D interactivo usando OpenGL 2.1 / GLSL 120 en Python. Presenta 5 modelos posicionados artísticamente, cada uno con shaders únicos, cámara orbital completa, post-procesado y UI en tiempo real.

## 🎯 Concepto del Diorama

**Tema:** Batalla épica en un coliseo místico donde guerreros y criaturas se enfrentan con poderes sobrenaturales.

**Modelos:**
1. **Centauro** (Guerrero Principal) - Centro, con efecto de poder divino (twist + energía pulsante)
2. **Cabeza Minecraft** (Guardián Místico) - Izquierda, aparece/desaparece (explosión + disolución)
3. **Criatura Secundaria** - Derecha, estilo cómic animado (agua + halftone)
4. **Piso/Arena** - Base del coliseo con cel-shading
5. **Columna/Decoración** - Fondo, pilar ondulante con lava (bend + magma)

## 🚀 Características Implementadas

### ✅ Modelos (25 pts)
- 5 modelos cargados y posicionados en la escena
- Cada modelo en coordenadas específicas (no todos en el origen)
- Incluye piso/base del diorama
- Sistema de visibilidad: un modelo a la vez o todos juntos

### ✅ Cámara (30 pts)
- **Zoom:** Mouse wheel + teclas `-` y `=`
- **Orbitar:** Click izquierdo + arrastrar, o flechas ← → ↑ ↓
- **Desplazamiento vertical:** Integrado en sistema orbital (phi)
- **Mouse y Teclado:** Ambos sistemas funcionan simultáneamente
- **Cambio de foco:** Teclas 1-5 cambian el target de la cámara a cada modelo
- Auto-framing: La cámara se reposiciona automáticamente al cambiar de modelo

### ✅ Shaders (30 pts)
**Sistema modular:** Cada modelo tiene sus propios shaders (vertex + fragment)

| Modelo    | Vertex Shader      | Fragment Shader         | Efecto                         |
| --------- | ------------------ | ----------------------- | ------------------------------ |
| Centauro  | twist_shader       | pulsating_energy_shader | Espiral + energía azul/púrpura |
| Minecraft | explode_shader     | dissolve_shader         | Ondas radiales + disolución    |
| Criatura  | water_shader       | halftone_shader         | Ondulación + patrón de cómic   |
| Piso      | vertex_shader      | toon_shader             | Básico + cel-shading           |
| Columna   | bend_ripple_shader | magma_shader            | Curvatura + lava animada       |

**Control en tiempo real:**
- Teclas Z/X ajustan el parámetro `shaderValue` del modelo activo
- Cada modelo tiene su propio valor independiente

### ✅ Skybox (5 pts)
- Cubemap Yokohama2 implementado
- Renderizado correctamente sin ocultar geometría

### ✅ Extras (25 pts)
- **UI en pantalla:** Info del modelo actual, controles, valor de shader
- **Post-procesado:** 9 efectos (TAB para ciclar)
  - None, Grayscale, Negative, Hurt, Depth, Fog, DOF, Edge Detection, Outline
- **FBO completo:** Render to texture con depth buffer

### ✅ Creatividad (10 pts)
- Composición temática coherente
- Shaders únicos por modelo
- Posicionamiento artístico
- Sistema de visualización flexible (individual o todos)

## 🎮 Controles

### Cámara (Arcball)
- Click izquierdo y arrastrar: orbitar (theta/phi)
- Rueda del mouse: zoom (acercar/alejar)
- Flechas ← →: orbitar horizontal
- Flechas ↑ ↓: orbitar vertical (limitado para no voltear)
- Teclas - y =: zoom out / zoom in

### Modelos
- **1-5:** Cambiar foco de cámara a cada modelo (solo uno visible)
- **Q:** Mostrar todos los modelos a la vez (vista del diorama completo)
- **E:** Volver a mostrar solo el modelo activo
- Click derecho: NO USAR (deprecated)

### Shaders
- **Z/X:** Disminuir/Aumentar el parámetro `shaderValue` del modelo activo
  - Controla intensidad de deformación, efectos, animaciones
  - Cada modelo tiene su propio valor independiente

### Post-proceso (FBO)
- **TAB:** Alternar entre efectos de post-procesado

### UI
- **H:** Toggle mostrar/ocultar UI overlay

## 📥 Modelos Necesarios

### Archivos que YA TIENES:
✅ `Centaur_Male_Lores.obj` + texturas  
✅ `Minecraft_cartoon_head.obj` + `skinsteve.png`  
✅ `3obj.obj` + `skin.jpg`

### Archivos que DEBES DESCARGAR:

**Para el piso (Modelo 4):**
- Busca: "plane.obj" o "floor.obj" o "ground.obj"
- Sitios recomendados: 
  - [Free3D.com](https://free3d.com) - busca "plane"
  - [CGTrader Free](https://www.cgtrader.com/free-3d-models) - busca "floor"
- **Dónde ponerlo:** Raíz del proyecto (`/Users/mariorocha/Documents/Programacion/RENDERER/`)
- **Nombre del archivo:** Renombra a `plane.obj`
- **Textura recomendada:** Textura de arena, piedra o mármol (`floor_texture.jpg`)

**Para la columna/decoración (Modelo 5):**
- Busca: "column.obj" o "pillar.obj" o "statue.obj"
- Sitios recomendados: mismos de arriba
- **Dónde ponerlo:** Raíz del proyecto
- **Nombre del archivo:** Renombra a `column.obj`
- **Textura recomendada:** Textura de piedra, mármol o roca (`column_texture.jpg`)

**Después de descargar:** Edita `RendererOpenGL.py` líneas ~60 y ~70 para cambiar:
```python
# Cambiar esto:
floor = Model("Centaur_Male_Lores.obj")  # TEMPORAL
# Por esto:
floor = Model("plane.obj")

# Y cambiar esto:
decoration = Model("Minecraft_cartoon_head.obj")  # TEMPORAL
# Por esto:
decoration = Model("column.obj")
```

## 🛠️ Instalación y Ejecución

### Requisitos
- Python 3.10+ (probado con CPython 3.13)
- macOS con soporte OpenGL 2.1

### Dependencias
```bash
python -m venv venv
source venv/bin/activate
pip install pygame PyOpenGL PyOpenGL_accelerate PyGLM numpy
```

### Ejecutar
```bash
python RendererOpenGL.py
```

## 🧱 Estructura del Proyecto

```
RENDERER/
├── RendererOpenGL.py        # Loop principal, inputs, configuración del diorama
├── gl.py                    # Renderer (FBO, shaders por modelo, pipeline)
├── camera.py                # Camera + ArcballOrbit controller
├── model.py                 # Clase Model con shaders propios
├── buffer.py                # VBO management
├── obj.py                   # Parser de .obj
├── skybox.py                # Skybox con cubemap
├── vertexShaders.py         # 8 vertex shaders GLSL 120
├── fragmentShaders.py       # 9 fragment shaders GLSL 120
├── postProcessingShaders.py # 10 efectos de post-proceso
├── Yokohama2/              # Texturas del skybox
├── *.obj                   # Modelos 3D
└── *.png, *.jpg            # Texturas
```

## 🤖 Uso de Inteligencia Artificial

Este proyecto utilizó **Claude Sonnet 4.5** (a través de GitHub Copilot en VS Code) como herramienta de asistencia en desarrollo.

### Tareas realizadas con IA:

1. **Análisis del código existente:**
   - Revisión completa de la arquitectura del proyecto
   - Identificación de componentes (renderer, cámara, shaders, modelos)
   - Evaluación contra los requisitos de la rúbrica

2. **Diseño de arquitectura:**
   - Sistema de shaders por modelo (cada instancia con sus propios shaders)
   - Modificación de `model.py` para agregar propiedades `vertexShader`, `fragmentShader`, `shaderValue`
   - Modificación de `gl.py` para compilar y usar shaders por modelo en el render loop

3. **Implementación del diorama:**
   - Concepto temático: "Batalla Épica en el Coliseo"
   - Posicionamiento artístico de 5 modelos en coordenadas variadas
   - Asignación de combinaciones únicas de shaders a cada modelo
   - Sistema de nombres y metadata para UI

4. **Sistema de controles:**
   - Mapeo de teclas 1-5 para cambio de foco entre modelos
   - Teclas Q/E para alternar entre vista individual y diorama completo
   - Teclas Z/X para ajustar parámetros de shader del modelo activo
   - Integración con sistema arcball existente

5. **UI en pantalla:**
   - Overlay con pygame.font mostrando info del modelo actual
   - Lista de controles en pantalla
   - Toggle con tecla H

6. **Documentación:**
   - README completo con concepto, características, controles
   - Instrucciones de descarga de modelos faltantes
   - Esta sección de uso de IA

### Proceso de integración:

El estudiante (Mario Rocha) proporcionó el código base del laboratorio y especificó los requisitos del proyecto. La IA analizó el código existente, propuso un plan de implementación priorizado y generó el código necesario para cumplir con la rúbrica.

Todas las modificaciones fueron revisadas, probadas e integradas por el estudiante. El estudiante es responsable de:
- Descargar los 2 modelos faltantes (piso y columna)
- Probar el diorama y ajustar valores según preferencia estética
- Verificar que todo funcione correctamente antes de entregar

## 📌 Notas Técnicas

- **GLSL 120:** Compatibilidad con OpenGL 2.1 legacy de macOS
- **Shaders por modelo:** Compilación lazy (solo se compilan cuando se usan)
- **Convención de atributos:** 0=inTexCoords, 1=inPosition, 2=inNormals
- **Post-proceso:** Quad de pantalla completa en immediate mode

## 🎨 Personalización

Para cambiar shaders de un modelo, edita `RendererOpenGL.py`:
```python
centaur.vertexShader = noise_disp_shader  # Cambiar vertex shader
centaur.fragmentShader = halftone_shader  # Cambiar fragment shader
centaur.shaderValue = 0.5  # Valor inicial del efecto
```

Shaders disponibles (ver `vertexShaders.py` y `fragmentShaders.py` para todos):
- Vertex: `vertex_shader`, `fat_shader`, `water_shader`, `twist_shader`, `bend_ripple_shader`, `noise_disp_shader`, `explode_shader`
- Fragment: `fragment_shader`, `toon_shader`, `negative_shader`, `magma_shader`, `halftone_shader`, `dissolve_shader`, `pulsating_energy_shader`

---

**Desarrollado por:** Mario Rocha  
**Curso:** Gráficos por Computadora  
**Fecha:** Noviembre 2025