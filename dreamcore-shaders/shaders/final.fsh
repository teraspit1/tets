#version 150

uniform sampler2D colortex0;
uniform vec2 OutSize;
uniform float GameTime;

in vec2 texCoord;
out vec4 fragColor;

float rand(vec2 co) {
    return fract(sin(dot(co, vec2(12.9898, 78.233))) * 43758.5453);
}

void main() {
    vec2 uv = texCoord;

    // Chromatic drift for surreal, old-lens effect.
    vec2 ca = vec2(0.0012 * sin(GameTime * 0.4), 0.0);
    float r = texture(colortex0, uv + ca).r;
    float g = texture(colortex0, uv).g;
    float b = texture(colortex0, uv - ca).b;
    vec3 col = vec3(r, g, b);

    // Analog grain.
    float noise = rand(uv * OutSize + GameTime * 60.0) - 0.5;
    col += noise * 0.03;

    // Bloom-like fake glow by simple neighborhood sample.
    vec2 px = 1.0 / OutSize;
    vec3 blur = vec3(0.0);
    blur += texture(colortex0, uv + vec2(px.x, 0.0)).rgb;
    blur += texture(colortex0, uv - vec2(px.x, 0.0)).rgb;
    blur += texture(colortex0, uv + vec2(0.0, px.y)).rgb;
    blur += texture(colortex0, uv - vec2(0.0, px.y)).rgb;
    blur *= 0.25;

    col = mix(col, blur, 0.18);

    // Gentle contrast compression for dreamy softness.
    col = pow(clamp(col, 0.0, 1.0), vec3(0.93));

    fragColor = vec4(col, 1.0);
}
