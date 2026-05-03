#version 120

uniform sampler2D colortex0;
uniform float viewWidth;
uniform float viewHeight;
uniform float frameTimeCounter;

void main() {
    vec2 uv = gl_FragCoord.xy / vec2(viewWidth, viewHeight);

    // chromatic aberration for surreal edge separation
    vec2 center = uv - 0.5;
    float dist = length(center);
    vec2 shift = normalize(center + 1e-6) * dist * 0.0035;

    vec3 col;
    col.r = texture2D(colortex0, uv + shift).r;
    col.g = texture2D(colortex0, uv).g;
    col.b = texture2D(colortex0, uv - shift).b;

    // dreamy bloom-ish blur tap
    vec2 px = 1.0 / vec2(viewWidth, viewHeight);
    vec3 blur = vec3(0.0);
    blur += texture2D(colortex0, uv + px * vec2( 1.5, 0.0)).rgb;
    blur += texture2D(colortex0, uv + px * vec2(-1.5, 0.0)).rgb;
    blur += texture2D(colortex0, uv + px * vec2(0.0,  1.5)).rgb;
    blur += texture2D(colortex0, uv + px * vec2(0.0, -1.5)).rgb;
    blur *= 0.25;

    float glowMask = smoothstep(0.55, 1.0, dot(col, vec3(0.2126, 0.7152, 0.0722)));
    col = mix(col, col + blur * 0.28, glowMask);

    // VHS grain + scanline whisper
    float noise = fract(sin(dot(gl_FragCoord.xy + frameTimeCounter * 13.0, vec2(12.9898, 78.233))) * 43758.5453);
    col += (noise - 0.5) * 0.025;
    col *= 1.0 - 0.03 * sin(gl_FragCoord.y * 1.15 + frameTimeCounter * 2.2);

    // slight vignette + lifted blacks
    float vignette = smoothstep(0.9, 0.22, dist);
    col = col * vignette + vec3(0.035, 0.04, 0.05);

    // low-contrast dreamy tonemap
    col = pow(max(col, 0.0), vec3(0.92));
    col = mix(col, vec3(dot(col, vec3(0.333))), 0.06);

    gl_FragColor = vec4(clamp(col, 0.0, 1.0), 1.0);
}
