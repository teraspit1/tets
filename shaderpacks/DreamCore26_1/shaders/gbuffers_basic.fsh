#version 120

uniform sampler2D texture;
uniform float frameTimeCounter;

varying vec2 texcoord;
varying vec4 tint;

void main() {
    vec2 uv = texcoord;

    // soft lens warping for dreamlike perspective
    vec2 centered = uv * 2.0 - 1.0;
    float r2 = dot(centered, centered);
    uv += centered * r2 * 0.015;

    // small hand-held drift to make scene feel unstable
    uv.x += sin(frameTimeCounter * 0.27) * 0.0012;
    uv.y += cos(frameTimeCounter * 0.19) * 0.0010;

    vec4 base = texture2D(texture, uv) * tint;

    // pastel remap (green/cyan/magenta bias)
    vec3 c = base.rgb;
    c = mix(c, vec3(dot(c, vec3(0.299, 0.587, 0.114))), 0.08);
    c.r *= 1.07;
    c.g *= 1.11;
    c.b *= 1.14;

    // highlight glow pre-pass feel
    float luma = dot(c, vec3(0.2126, 0.7152, 0.0722));
    c += smoothstep(0.65, 1.0, luma) * vec3(0.08, 0.12, 0.16);

    gl_FragColor = vec4(clamp(c, 0.0, 1.0), base.a);
}
