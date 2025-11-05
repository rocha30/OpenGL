vertex_postProcess = '''
#version 120

varying vec2 fragTexCoords;

void main()
{
    // Using fixed-function attributes for compatibility (no VBOs needed)
    gl_Position = gl_Vertex;
    fragTexCoords = gl_MultiTexCoord0.xy;
}

'''

none_postProcess = '''
#version 120

varying vec2 fragTexCoords;

uniform sampler2D frameBuffer;

void main(){
    gl_FragColor = texture2D(frameBuffer, fragTexCoords);
}

'''

grayScale_postProcess = '''
#version 120

varying vec2 fragTexCoords;

uniform sampler2D frameBuffer;

void main(){
    vec4 color = texture2D(frameBuffer, fragTexCoords);
    float gray = dot(color.rgb, vec3(0.3, 0.6, 0.1) );
    gl_FragColor = vec4(gray, gray, gray, 1.0);
}

'''

negative_postProcess = '''
#version 120

varying vec2 fragTexCoords;

uniform sampler2D frameBuffer;

void main(){
    gl_FragColor = vec4(1.0) - texture2D(frameBuffer, fragTexCoords);
}

'''

hurt_postProcess = '''
#version 120

varying vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform float time;

void main(){
    vec3 color = texture2D(frameBuffer, fragTexCoords).rgb;

    vec2 centered = fragTexCoords * 2.0 - 1.0;
    float dist = length(centered);
    float vignetteStrength = smoothstep(sin(time * 5.0) * 0.1 + 0.6, 1.0, dist) * 0.5;
    vec3 redTint = vec3(1.0, 0.0, 0.0);

    color = mix(color, redTint, vignetteStrength);

    gl_FragColor = vec4(color, 1.0);
}

'''

depth_postProcess = '''
#version 120

varying vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;

void main(){
    float depth = texture2D(depthTexture, fragTexCoords).r;

    depth = 1.0 - depth;
    depth = clamp(depth, 0.0, 0.1) * 10.0;

    gl_FragColor = vec4(vec3(depth), 1.0);
}

'''

fog_postProcess = '''
#version 120

varying vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;

void main(){
    vec3 color = texture2D(frameBuffer, fragTexCoords).rgb;
    float depth = texture2D(depthTexture, fragTexCoords).r;

    depth = 1.0 - depth;
    depth = clamp(depth, 0.0, 0.1) * 10.0;

    vec3 fogColor = vec3(0.5, 0.5, 0.5);
    color = mix(fogColor, color, depth);

    gl_FragColor = vec4(color, 1.0);
}

'''

dof_postProcess = '''
#version 120

varying vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;
uniform vec2 texelSize; // 1.0 / vec2(width, height)

void main() {
    float depth = texture2D(depthTexture, fragTexCoords).r;
    depth = clamp(depth, 0.0, 0.1) * 10.0;

    vec3 color = vec3(0.0);
    float samples = 0.0;
    for(int x=-1; x<=1; x++){
        for(int y=-1; y<=1; y++){
            vec2 offset = vec2(float(x), float(y)) * texelSize * depth * 2.0;
            color += texture2D(frameBuffer, fragTexCoords + offset).rgb;
            samples += 1.0;
        }
    }
    color /= samples;

    gl_FragColor = vec4(color, 1.0);
}
'''

edgeDetection_postProcess = '''
#version 120

varying vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;
uniform vec2 texelSize; // 1.0 / vec2(width, height)

void main()
{
    vec2 step = 5.0 * texelSize;
    float depthC = texture2D(depthTexture, fragTexCoords).r;
    float depthL = texture2D(depthTexture, fragTexCoords + vec2(-step.x, 0.0)).r;
    float depthR = texture2D(depthTexture, fragTexCoords + vec2(step.x, 0.0)).r;
    float depthU = texture2D(depthTexture, fragTexCoords + vec2(0.0, step.y)).r;
    float depthD = texture2D(depthTexture, fragTexCoords + vec2(0.0, -step.y)).r;

    float edge = abs(depthL - depthR) + abs(depthU - depthD);
    edge *= 5.0;
    gl_FragColor = vec4(vec3(edge), 1.0);
}
'''

outline_postProcess = '''
#version 120

varying vec2 fragTexCoords;

uniform sampler2D frameBuffer;
uniform sampler2D depthTexture;
uniform vec2 texelSize; // 1.0 / vec2(width, height)

void main() {
    vec2 step = 3.0 * texelSize;
    float depthC = texture2D(depthTexture, fragTexCoords).r;
    float depthL = texture2D(depthTexture, fragTexCoords + vec2(-step.x, 0.0)).r;
    float depthR = texture2D(depthTexture, fragTexCoords + vec2(step.x, 0.0)).r;
    float depthU = texture2D(depthTexture, fragTexCoords + vec2(0.0, step.y)).r;
    float depthD = texture2D(depthTexture, fragTexCoords + vec2(0.0, -step.y)).r;

    float edge = abs(depthL - depthR) + abs(depthU - depthD);
    edge *= 5.0;
    if(edge > 0.01)
    {
        gl_FragColor = vec4(0.0, 0.0, 0.0, 1.0);
    }
    else
    {
        gl_FragColor = texture2D(frameBuffer, fragTexCoords);
    }
}
'''