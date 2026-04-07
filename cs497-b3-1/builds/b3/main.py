#****************************************************************************
# main.py - Forbidden Island main launcher
# v1
# Boise State University CS 497
# Dr. Henderson
# Spring 2026
#
# Three modes:
#
# 1. Headless agent run   — no display, agents only
# 2. Observed agent run   — agents play, WebSocket server streams to browser
# 3. Human + agent run    — some roles are human-controlled via browser
#
# Run headless - agents play (default):
#     python main.py
#
# Run with browser display (watch agents play):
#     python main.py --display
#
# Reserve a role for a human player:
#     python main.py --display --players=6 --agents=5
#----------------------------------------------------------------------------
from __future__ import annotations

import argparse
import threading

from lib.events import EventBus
from lib.game   import ForbiddenIslandEngine
from lib.logger import LoggingObserver
from graph  import build_graph

def run_with_display(engine: ForbiddenIslandEngine,
                     host: str = "127.0.0.1", port: int = 8000):
    """
    Run with a WebSocket server so a browser can observe or participate.
    """
    # Import here so the server deps (fastapi/uvicorn) are only required
    # when actually running in display mode.
    import uvicorn
    from lib.server import create_app

    app = create_app(engine)
    print(f"\nForbidden Island → http://{host}:{port}")

    uvicorn.run(app, host=host, port=port)

#---------------------------------------------------------------------------
# CLI
#---------------------------------------------------------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Forbidden Island")
    parser.add_argument("--display",  action="store_true", help="Start WebSocket server + browser UI")
    parser.add_argument("--agents",   type=int, default=None, help="Number of agents")
    parser.add_argument("--players",  type=int, default=2,    help="Number of players (2-4)")
    parser.add_argument("--water",    type=int, default=1,    help="Starting water level")
    parser.add_argument("--host",     type=str, default="127.0.0.1")
    parser.add_argument("--port",     type=int, default=8000)
    parser.add_argument("--load",     type=str, help="Load a saved game")
    parser.add_argument("--verbose",  action="store_true")
    parser.add_argument("--interactive",  action="store_true", help="Wait for keyboard input between turns")
    args = parser.parse_args()

    bus    = EventBus()
    engine = ForbiddenIslandEngine(num_players=args.players, water_level=args.water, bus=bus)

    if args.load:
        try:
            engine.load(args.load)
        except:
            print(f"Could not load game {args.load}")
            exit()

    LoggingObserver(verbose=args.verbose).attach(bus)

    if args.agents:
        graph = build_graph()

        if args.display:
            thread = threading.Thread(target=run_with_display, args=(engine, args.host, args.port), daemon=True)
            thread.start()

        graph.invoke({ "game": engine, "interactive": args.interactive }, {"recursion_limit": 500})
        input("Press any key to exit")
    else:
        engine.start()
        if args.display:
            run_with_display(engine, args.host, args.port)