# GLSL
white_shader = '''#version 120



void main()
{
    gl_FragColor = vec4(1.0, 1.0, 1.0, 1.0);
}

'''


fragment_shader = '''#version 120

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max( 0 , dot(fragNormal, lightDir)) + ambientLight;

    gl_FragColor = texture2D(tex0, fragTexCoords) * intensity;
}

'''


toon_shader = '''#version 120

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max( 0 , dot(fragNormal, lightDir)) + ambientLight;

    if (intensity < 0.33)
        intensity = 0.2;
    else if (intensity < 0.66)
        intensity = 0.6;
    else
        intensity = 1.0;

    gl_FragColor = texture2D(tex0, fragTexCoords) * intensity;
}

'''


negative_shader = '''#version 120

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform sampler2D tex0;

void main()
{
    gl_FragColor = 1.0 - texture2D(tex0, fragTexCoords);
}

'''


magma_shader = '''#version 120

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform sampler2D tex0;
uniform sampler2D tex1;

uniform vec3 pointLight;
uniform float ambientLight;

uniform float time;

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max( 0 , dot(fragNormal, lightDir)) + ambientLight;

    gl_FragColor = texture2D(tex0, fragTexCoords) * intensity;
    gl_FragColor += texture2D(tex1, fragTexCoords) * ((sin(time) + 1.0) / 2.0);
}

'''

halftone_shader = '''#version 120

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float value;  // Escala del patrón de puntos

void main()
{
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    vec3 N = normalize(fragNormal);
    
    float ndotl = clamp(dot(N, lightDir), 0.0, 1.0);
    float q = floor(ndotl * 4.0) / 4.0;  // Cuantización de luz

    // Escala de puntos basada en value (20-200 range)
    float dotScale = 20.0 + value * 80.0;
    vec2 uv = fragTexCoords * dotScale;
    vec2 gv = fract(uv) - 0.5;
    float r = length(gv);

    // Puntos más grandes en sombra
    float dotMask = step(r, 0.35 * (1.0 - q));

    // Colores base y de sombra
    vec3 base = mix(vec3(1.0), vec3(0.2, 0.25, 0.3), q);
    vec3 col = mix(base, vec3(0.05), 1.0 - dotMask);

    // Combinar con textura base
    vec3 texColor = texture2D(tex0, fragTexCoords).rgb;
    vec3 finalColor = col * texColor;

    gl_FragColor = vec4(finalColor, 1.0);
}

'''

dissolve_shader = '''#version 120

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform sampler2D tex0;    // Usaremos como textura de ruido
uniform vec3 pointLight;
uniform float ambientLight;
uniform float value;       // Cantidad de disolución (0=sin disolver, 1=todo disuelto)

void main()
{
    // Usar la textura como ruido en escala de grises
    float noise = texture2D(tex0, fragTexCoords).r;
    
    // Calcular la disolución
    float dissolveAmount = value;
    float d = noise - dissolveAmount;

    // Descartar fragmentos que están "por debajo" del umbral
    float alpha = step(0.0, d);
    if(alpha < 0.5) discard;

    // Calcular iluminación básica
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float intensity = max(0.0, dot(fragNormal, lightDir)) + ambientLight;

    // Borde brillante cuando d es pequeño
    float edgeWidth = 0.1;  // Grosor del borde
    float edge = 1.0 - smoothstep(0.0, edgeWidth, abs(d));
    
    // Colores
    vec3 baseColor = vec3(0.85, 0.85, 0.9);  // Color base
    vec3 edgeColor = vec3(1.0, 0.5, 0.1);    // Color naranja brillante del borde
    
    // Mezclar color base con borde brillante
    vec3 color = mix(baseColor, edgeColor, edge);
    
    // Aplicar iluminación
    gl_FragColor = vec4(color, 1.0);
}

'''


holographic_glitch_shader = '''#version 120

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float value;       // Intensidad del glitch
uniform float time;

// Función de ruido simple
float noise(vec2 p) {
    return sin(p.x * 43.5453 + p.y * 37.7272) * 0.5 + 0.5;
}

// Función de glitch aleatorio
float glitch(vec2 uv, float t) {
    float n = noise(vec2(floor(t * 20.0), floor(uv.y * 25.0)));
    return step(0.95, n);
}

void main()
{
    vec2 uv = fragTexCoords;
    float t = time;
    float glitchIntensity = value;
    
    // === DISTORSIÓN TEMPORAL ===
    float timeGlitch = sin(t * 15.0) * 0.02 * glitchIntensity;
    uv.x += timeGlitch;
    
    // === LÍNEAS DE ESCANEO ===
    float scanlines = sin(uv.y * 800.0) * 0.5 + 0.5;
    scanlines = pow(scanlines, 3.0);
    
    // === GLITCH HORIZONTAL ===
    float hGlitch = glitch(uv, t);
    uv.x += hGlitch * sin(t * 50.0) * 0.05 * glitchIntensity;
    
    // === ABERRACIÓN CROMÁTICA (RGB SPLIT) ===
    float offset = 0.01 * glitchIntensity;
    vec3 texColor;
    texColor.r = texture2D(tex0, uv + vec2(offset, 0.0)).r;
    texColor.g = texture2D(tex0, uv).g;
    texColor.b = texture2D(tex0, uv - vec2(offset, 0.0)).b;
    
    // === ILUMINACIÓN BÁSICA ===
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float lightIntensity = max(0.3, dot(fragNormal, lightDir)) + ambientLight;
    
    // === COLORES HOLOGRÁFICOS ===
    vec3 holoColor1 = vec3(0.0, 1.0, 1.0);  // Cian
    vec3 holoColor2 = vec3(1.0, 0.0, 1.0);  // Magenta
    vec3 holoColor3 = vec3(0.5, 0.0, 1.0);  // Púrpura
    
    // Mezclar colores basado en posición y tiempo
    float colorMix = sin(uv.y * 10.0 + t * 8.0) * 0.5 + 0.5;
    vec3 holoBase = mix(holoColor1, holoColor2, colorMix);
    holoBase = mix(holoBase, holoColor3, sin(t * 3.0) * 0.5 + 0.5);
    
    // === EFECTO DE INTERFERENCIA ===
    float interference = sin(uv.x * 100.0 + t * 20.0) * 
                        sin(uv.y * 80.0 + t * 15.0) * 0.1;
    
    // === COMPOSICIÓN FINAL ===
    vec3 finalColor = texColor * holoBase * lightIntensity;
    finalColor += interference;
    finalColor *= scanlines * 0.8 + 0.2; // Aplicar scanlines
    
    // === GLITCH DE BRILLO ===
    float brightGlitch = glitch(uv * 2.0, t * 2.0);
    finalColor += brightGlitch * holoColor1 * 0.8;
    
    gl_FragColor = vec4(finalColor, alpha);
}

'''

pulsating_energy_shader = '''#version 120

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform sampler2D tex0;
uniform vec3 pointLight;
uniform float ambientLight;
uniform float value;       // Intensidad de la energía
uniform float time;

void main()
{
    vec3 N = normalize(fragNormal);
    vec2 uv = fragTexCoords;
    
    // === CÁLCULO DE VISTA PARA RIM LIGHTING ===
    vec3 viewPos = vec3(0.0, 0.0, 5.0);
    vec3 V = normalize(viewPos - fragPosition.xyz);
    float ndotv = clamp(dot(N, V), 0.0, 1.0);
    
    // === PULSO PRINCIPAL ===
    float mainPulse = sin(time * 4.0) * 0.5 + 0.5;
    float fastPulse = sin(time * 12.0) * 0.3 + 0.7;
    float megaPulse = sin(time * 1.5) * 0.4 + 0.6;
    
    // === RIM LIGHTING ENERGÉTICO ===
    float rim = pow(1.0 - ndotv, 2.0);
    float energyRim = rim * mainPulse * value;
    
    // === ONDAS DE ENERGÍA ===
    float wave1 = sin(length(fragPosition.xyz) * 8.0 - time * 6.0) * 0.5 + 0.5;
    float wave2 = sin(length(fragPosition.xyz) * 12.0 - time * 8.0) * 0.3 + 0.7;
    float wave3 = sin(length(fragPosition.xyz) * 5.0 + time * 4.0) * 0.4 + 0.6;
    
    float energyWaves = (wave1 + wave2 + wave3) / 3.0;
    
    // === LÍNEAS DE ENERGÍA ===
    float energyLines = sin(uv.y * 50.0 + time * 10.0) * 
                       sin(uv.x * 40.0 + time * 8.0) * 0.2 + 0.8;
    
    // === COLORES ELÉCTRICOS ===
    vec3 electricBlue = vec3(0.1, 0.3, 1.0);    // Azul eléctrico
    vec3 electricPurple = vec3(0.6, 0.1, 1.0);  // Púrpura eléctrico  
    vec3 electricWhite = vec3(1.0, 1.0, 1.0);   // Blanco brillante
    vec3 darkBase = vec3(0.05, 0.05, 0.2);      // Base oscura
    
    // === MEZCLA DE COLORES DINÁMICOS ===
    float colorShift = sin(time * 3.0) * 0.5 + 0.5;
    vec3 energyColor = mix(electricBlue, electricPurple, colorShift);
    
    // === ILUMINACIÓN BÁSICA ===
    vec3 lightDir = normalize(pointLight - fragPosition.xyz);
    float lightIntensity = max(0.2, dot(N, lightDir)) + ambientLight;
    
    // === TEXTURA BASE ===
    vec3 texColor = texture2D(tex0, uv).rgb;
    
    // === COMPOSICIÓN FINAL ===
    vec3 baseColor = darkBase + texColor * 0.3;
    
    // Agregar energía en los bordes
    vec3 finalColor = baseColor + energyRim * energyColor * 3.0;
    
    // Agregar ondas de energía
    finalColor += energyWaves * energyColor * value * 0.8;
    
    // Agregar líneas energéticas
    finalColor += energyLines * energyColor * value * 0.4;
    
    // Pulsos de energía intensa
    finalColor += mainPulse * energyColor * value * 0.6;
    
    // Megapulso ocasional de energía blanca
    finalColor += megaPulse * electricWhite * value * 0.3;
    
    // Aplicar iluminación base
    finalColor *= lightIntensity;
    
    // === EFECTO DE SOBRECARGA ===
    if(value > 1.5) {
        finalColor += electricWhite * fastPulse * 0.5;
    }

    gl_FragColor = vec4(finalColor, 1.0);
}

'''




