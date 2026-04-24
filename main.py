from __future__ import annotations

import sys


def main() -> int:
    try:
        from examples.demo_project import main as demo_main
    except ModuleNotFoundError as exc:
        missing = exc.name or "unknown"
        print(
            f"[TETS] Missing dependency: {missing}. "
            "Install required packages: pip install numpy glfw vulkan pyimgui",
            file=sys.stderr,
        )
        return 1

    demo_main()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
