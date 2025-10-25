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




