#version 150

uniform sampler2D Sampler0;
uniform float GameTime;

in vec2 texCoord;
in vec4 vertColor;
in float dreamPulse;

out vec4 fragColor;

vec3 rgb2hsv(vec3 c) {
    vec4 K = vec4(0.0, -1.0 / 3.0, 2.0 / 3.0, -1.0);
    vec4 p = mix(vec4(c.bg, K.wz), vec4(c.gb, K.xy), step(c.b, c.g));
    vec4 q = mix(vec4(p.xyw, c.r), vec4(c.r, p.yzx), step(p.x, c.r));

    float d = q.x - min(q.w, q.y);
    float e = 1.0e-10;
    return vec3(abs(q.z + (q.w - q.y) / (6.0 * d + e)), d / (q.x + e), q.x);
}

vec3 hsv2rgb(vec3 c) {
    vec3 p = abs(fract(c.xxx + vec3(0.0, 2.0 / 3.0, 1.0 / 3.0)) * 6.0 - 3.0);
    return c.z * mix(vec3(1.0), clamp(p - 1.0, 0.0, 1.0), c.y);
}

void main() {
    vec4 base = texture(Sampler0, texCoord) * vertColor;

    // DreamCore tone shaping: pastel foggy highlights + mild magenta/cyan shift.
    vec3 hsv = rgb2hsv(base.rgb);
    hsv.x += 0.02 * sin(GameTime * 0.25 + texCoord.y * 8.0);
    hsv.y *= 0.78;
    hsv.z = pow(hsv.z, 0.92);

    vec3 color = hsv2rgb(hsv);

    vec3 pinkGlow = vec3(1.0, 0.72, 0.88);
    vec3 cyanGlow = vec3(0.70, 0.93, 1.0);
    float pulse = 0.5 + 0.5 * sin(GameTime * 0.55 + dreamPulse * 6.2831);
    color = mix(color, mix(pinkGlow, cyanGlow, texCoord.y), 0.10 + pulse * 0.08);

    // Soft vignette to emulate nostalgic camcorder framing.
    vec2 centered = texCoord * 2.0 - 1.0;
    float vignette = 1.0 - dot(centered, centered) * 0.22;

    // Slight film haze.
    float haze = 0.03 * sin((texCoord.x + texCoord.y + GameTime) * 25.0);

    fragColor = vec4(clamp(color * vignette + haze, 0.0, 1.0), base.a);
}
