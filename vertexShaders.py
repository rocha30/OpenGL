simpleVertex_shader = '''#version 120

attribute vec2 inTexCoords;
attribute vec3 inPosition;
attribute vec3 inNormals;

varying vec4 fragPosition;
varying vec2 fragTexCoords;
varying vec3 fragNormal;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;


void main()
{
    fragTexCoords = inTexCoords;
    fragPosition = modelMatrix * vec4(inPosition, 1.0);

    fragNormal = normalize( vec3(modelMatrix * vec4(inNormals, 0.0)));
    
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(inPosition, 1.0);
    
}

'''


vertex_shader = '''#version 120

attribute vec2 inTexCoords;
attribute vec3 inPosition;
attribute vec3 inNormals;

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;


void main()
{
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(inPosition, 1.0);

    fragPosition = modelMatrix * vec4(inPosition, 1.0);

    fragNormal = normalize( vec3(modelMatrix * vec4(inNormals, 0.0)));

    fragTexCoords = inTexCoords;
}

'''


fat_shader = '''#version 120

attribute vec2 inTexCoords;
attribute vec3 inPosition;
attribute vec3 inNormals;

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float value;


void main()
{
    fragPosition = modelMatrix * vec4(inPosition + inNormals * value, 1.0);

    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = normalize( vec3(modelMatrix * vec4(inNormals, 0.0)));

    fragTexCoords = inTexCoords;
}

'''


water_shader = '''#version 120

attribute vec2 inTexCoords;
attribute vec3 inPosition;
attribute vec3 inNormals;

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;
uniform float value;


void main()
{
    float displacement = sin(time + inPosition.x + inPosition.z) * value;
    fragPosition = modelMatrix * vec4(inPosition + vec3(0,displacement, 0)  , 1.0);

    gl_Position = projectionMatrix * viewMatrix * fragPosition;

    fragNormal = normalize( vec3(modelMatrix * vec4(inNormals, 0.0)));

    fragTexCoords = inTexCoords;
}

'''

twist_shader = '''#version 120
attribute vec2 inTexCoords;
attribute vec3 inPosition;
attribute vec3 inNormals;

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;
uniform float value;

void main() {
    vec3 p = inPosition;
    float theta = value * p.y;   // <- (antes decía "vaule")
    float c = cos(theta);
    float s = sin(theta);

    vec2 xz = vec2(p.x, p.z);    // <- (antes decía "vex2")
    xz = mat2(c, -s, s, c) * xz;
    p.x = xz.x; 
    p.z = xz.y;

    fragTexCoords = inTexCoords;

    vec4 worldPos = modelMatrix * vec4(p, 1.0);
    fragPosition = worldPos;

    vec3 n = inNormals;          // <- (antes era vec2)
    vec2 nxz = vec2(n.x, n.z);
    nxz = mat2(c, -s, s, c) * nxz;
    n.x = nxz.x;
    n.z = nxz.y;

    // Nota: esto usa modelMatrix para la normal; es correcto solo si NO hay escala no uniforme.
    fragNormal = normalize((mat3(modelMatrix) * n));

    gl_Position = projectionMatrix * viewMatrix * worldPos;
}

'''


bend_ripple_shader = '''#version 120

attribute vec2 inTexCoords;
attribute vec3 inPosition;
attribute vec3 inNormals;

varying vec2 fragTexCoords;
varying vec3 fragNormal;
varying vec4 fragPosition;

uniform mat4 modelMatrix;
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

uniform float time;
uniform float value;        // bend radius (5.0 a 50.0)
uniform float ambientLight; // ripple amplitude (0.02 a 0.2)

void main()
{
    vec3 p = inPosition;

    // Bend alrededor del eje X (curva en el plano YZ)
    float R = max(value, 0.001);  // bend radius
    float ang = p.x / R;
    float c = cos(ang), s = sin(ang);
    float y = p.y, z = p.z;
    
    // Centro del arco en (0, 0, -R) para que p.x=0 no se mueva
    float yb = y * c + (z + R) * s;
    float zb = -y * s + (z + R) * c - R;
    p.y = yb; 
    p.z = zb;

    // Ripple senoidal usando ambientLight como amplitud
    float rippleAmp = ambientLight * 0.5;  // escala para que 0.1 de ambientLight = 0.05 de ripple
    p.y += rippleAmp * sin(p.x * 6.0 + time * 1.5) *
                      sin(p.z * 6.0 + time * 1.1);

    fragTexCoords = inTexCoords;

    // Posición en mundo
    vec4 worldPos = modelMatrix * vec4(p, 1.0);
    fragPosition = worldPos;

    // Normal aproximada (rotamos igual que la posición para el bend)
    vec3 n = inNormals;
    float ny = n.y, nz = n.z;
    float nyb = ny * c + nz * s;
    float nzb = -ny * s + nz * c;
    n.y = nyb; 
    n.z = nzb;

    fragNormal = normalize(vec3(modelMatrix * vec4(n, 0.0)));

    gl_Position = projectionMatrix * viewMatrix * worldPos;
}

'''