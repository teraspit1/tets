from __future__ import annotations

from engine.config import ConfigManager
from engine.debug import DebugOverlay
from engine.hotreload import HotReloadService
from engine.logger import setup_logger
from engine.time import Time
from ecs.ecs_world import ECSWorld
from ecs.scene import Scene
from input.input_manager import InputManager
from physics.physics_world import PhysicsWorld
from rendering.renderer import Renderer
from scripting.visual_runtime import VisualScriptRuntime


class EngineApp:
    def __init__(self, config_path: str = "engine_config.json") -> None:
        self.logger = setup_logger()
        self.config = ConfigManager(config_path).load()
        self.time = Time()
        self.debug_overlay = DebugOverlay()

        self.world = ECSWorld()
        self.scene = Scene("MainScene", self.world)
        self.physics = PhysicsWorld(self.world)
        self.input = InputManager()
        self.renderer = Renderer(self.config)
        self.visual_runtime = VisualScriptRuntime(self.world)
        self.hot_reload = HotReloadService()

        self.running = False

    def initialize(self) -> None:
        self.renderer.initialize()
        self.logger.info("Engine initialized with backend: %s", self.renderer.backend_name)

    def tick(self) -> None:
        self.time.update()
        self.input.poll()
        self.hot_reload.poll()
        self.visual_runtime.update(self.time.delta_time)
        self.physics.step(self.time.delta_time)
        self.renderer.render(self.scene, self.debug_overlay)
        self.debug_overlay.tick()

    def run(self) -> None:
        self.running = True
        self.initialize()
        while self.running and not self.renderer.should_close():
            self.tick()
        self.shutdown()

    def shutdown(self) -> None:
        self.renderer.shutdown()
        self.logger.info("Engine shutdown")
