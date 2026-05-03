#version 150

in vec3 Position;
in vec2 UV0;
in vec4 Color;

uniform mat4 ModelViewMat;
uniform mat4 ProjMat;
uniform float GameTime;

out vec2 texCoord;
out vec4 vertColor;
out float dreamPulse;

void main() {
    vec4 worldPos = ModelViewMat * vec4(Position, 1.0);

    // Very light breathing distortion for liminal/dream sensation.
    float wobble = sin((worldPos.x + worldPos.z) * 0.11 + GameTime * 0.45) * 0.015;
    worldPos.y += wobble;

    texCoord = UV0;
    vertColor = Color;
    dreamPulse = 0.5 + 0.5 * sin(GameTime * 0.35 + worldPos.y * 0.2);

    gl_Position = ProjMat * worldPos;
}
