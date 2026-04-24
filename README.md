# TETS Engine (Python 3D Engine Foundation)

## 1. ARCHITECTURE OVERVIEW

TETS Engine is split into runtime engine systems and editor tooling with a shared data model (ECS + scene graph + resources + visual scripts).

### High-level flow diagram (text)

```
[Input] ---> [InputManager] ----> [Gameplay Templates]
                                \-> [VisualScriptRuntime]

[ECSWorld] <---- [Scene Graph] <---- [Editor: Hierarchy/Inspector]
    |                  |
    |                  +--> [Serialization]
    |
    +--> [PhysicsWorld]
    +--> [Renderer] ---> [Vulkan Backend] ---> [Swapchain/Frame]
                      \-> [ModernGL fallback]

[ResourceManager] <--> [Asset Browser]
[HotReloadService] --> [Resource/Shader Rebuild Hooks]
[DebugOverlay] -----> [Viewport overlay]
```

## 2. SYSTEM DESIGN

### Engine Core
- `ECSWorld` owns entities and component storage.
- `Scene` is a hierarchical wrapper over ECS entities.
- `ResourceManager` registers mesh/texture/shader assets.
- `SceneSerializer` persists scene/world payload to JSON.

### Rendering (Vulkan-first)
- `Renderer` selects Vulkan first and falls back to ModernGL when Vulkan is unavailable.
- `VulkanBackend` handles window and swapchain metadata lifecycle.
- `Pipeline` contains PS1 style toggles:
  - affine texture warping toggle
  - vertex jitter amount
  - color quantization depth
  - low-res scaling
  - dithering toggle

### Editor
- `EditorApp` orchestrates:
  - Scene hierarchy panel
  - Inspector panel
  - Viewport descriptor
  - Asset browser
  - Node editor
- `play_mode` toggles runtime simulation intent.

### Visual Scripting
- `VisualScriptGraph` stores nodes + directed links.
- Built-in nodes include:
  - Events: Start/Update
  - Logic: Branch
  - Math: Add
  - Transform: Translate
- `VisualScriptRuntime` executes event-driven node flows and mutates ECS components.
- `GraphSerializer` saves graph topology and node metadata to JSON.

### Gameplay Templates
- Character controller
- Shooting system
- Time-of-day cycle
- Inventory system
- Vehicle movement module

All templates are pure Python classes and can be called from either game code or visual script wrappers.

### Input System
- Action bindings with runtime remapping (`InputManager.bind`).
- Keyboard/mouse abstraction interface prepared for GLFW integration.

### Physics MVP
- Gravity integration on rigid bodies.
- AABB overlap checks.
- Basic overlap resolution by zeroing velocity.

### Developer Experience
- `setup_logger` for console/file logs.
- JSON config manager.
- Hot reload service (mtime polling).
- Debug overlay with FPS sampling.

## 3. FOLDER STRUCTURE

```
engine/
editor/
rendering/
ecs/
physics/
input/
scripting/
templates/
assets/
examples/
main.py
README.md
```

## 4. IMPLEMENTATION (key files)

- `engine/app.py`: app loop and subsystem orchestration.
- `rendering/renderer.py`: backend selection + frame loop adapter.
- `rendering/vulkan_backend.py`: Vulkan-first backend scaffold.
- `editor/editor_app.py`: editor shell and panel integration.
- `scripting/*`: node graph data model, runtime execution, graph serialization.
- `templates/*`: gameplay modules.
- `examples/demo_project.py`: project wiring and bootstrap.

## 5. HOW TO RUN

1. Create virtual env and install dependencies:
   - `pip install numpy glfw vulkan pyimgui`
2. Run demo bootstrap:
   - `python main.py`
3. For realtime runtime loop, uncomment `engine.run()` in `examples/demo_project.py`.

## 6. HOW TO EXTEND

- Add components in `ecs/components.py` and query via `ECSWorld.query`.
- Add new render pipelines by expanding `rendering/pipeline.py` and binding shader permutations.
- Add custom node classes under `scripting/nodes.py`; register in graph builders.
- Extend editor by adding new panel classes in `editor/panels.py` and composing in `EditorApp.draw`.
- Add module templates under `templates/` and expose as script-callable nodes.

## 7. LIMITATIONS

- Vulkan backend is a scaffold and does not yet create full device/command buffer pipelines.
- ModernGL fallback is lifecycle-compatible but currently no-op rendering.
- Editor rendering is data-model-based; pyimgui draw calls are integration TODOs.
- Physics is intentionally minimal and not deterministic/network-ready.

## Zip Packaging

From repository root:

```bash
cd /workspace
zip -r tets_engine.zip tets -x "*/.git/*" "*/__pycache__/*"
```

This creates `tets_engine.zip` ready for transfer.
