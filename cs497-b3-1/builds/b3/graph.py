#****************************************************************************
# graph.py - Forbidden Island multi-agent app
# v1
# Boise State University CS 497
# Dr. Henderson
# Spring 2026
#
# Builds a multi-agent graph to play Forbidden Island
#----------------------------------------------------------------------------
import json

from langgraph.graph import StateGraph, START, END
from typing import Literal

from lib.game import GameTreasure
from lib.reactive import messenger, navigator, engineer, pilot, diver, explorer
from lib.state import GameState

# Override the reactive implementations when you have your agents implemented
from agents import messenger
#from agents import navigator
#from agents import engineer
#from agents import pilot
#from agents import diver
#from agents import explorer

#--------------------------------------------------------------------------------------------------
# Private state
#--------------------------------------------------------------------------------------------------
_game = None
_turns = 0
_stats = {}

#--------------------------------------------------------------------------------------------------
# Helper functions
#--------------------------------------------------------------------------------------------------

#**************************************************************************************************
# Function Nodes in the graph
#--------------------------------------------------------------------------------------------------
#--------------------------------------------------------------------------------------------------
# Initial node that starts the game
#--------------------------------------------------------------------------------------------------
def start_game(state: GameState) -> None:
    # Initialize
    global _game
    _game = state["game"]
    _game.start()

#--------------------------------------------------------------------------------------------------
# Starts a new turn
#--------------------------------------------------------------------------------------------------
def turn(state: GameState) -> None :
    global _turns
    _turns += 1
    if state["interactive"]:
        input(f"[TURN] ({_turns}) press any key to continue to phase [{phase(state)}]")
    else:
        print(f"[TURN] ({_turns})")

#--------------------------------------------------------------------------------------------------
# Returns the name of the current phase - used for routing to the appropriate node
#--------------------------------------------------------------------------------------------------
def phase(state: GameState) -> str :
    # Both discard and action will be routed to the action node. Agents are responsible for
    # distinguishing between them
    if _game.current_event == "discard":
        return "action"
    else:
        return _game.current_event

#--------------------------------------------------------------------------------------------------
# Analyzes the current state of the game and sets the goals and observations in the state
#--------------------------------------------------------------------------------------------------
# You can modify this if you want
#--------------------------------------------------------------------------------------------------
def action(state: GameState) -> dict:
    obs = _game.get_observation()
    print(f"[STRATEGY] {json.dumps(obs)}")

    # set the goals for this round
    shore = []
    # Check if Fools Landing is flooded
    if _game.is_flooded("Fools Landing"):
        shore.append("Fools Landing")

    # Check if treasure tiles are in jeopardy
    for treasure in GameTreasure:
        if treasure not in obs["treasures"]:
            for tt in _game.get_treasure_tiles(treasure):
                if _game.is_flooded(tt):
                    shore.append(tt)

    # Check who has the most for each treasure
    cards = {}
    for treasure in GameTreasure:
        if treasure not in obs["treasures"]:
            max = None
            for p in _game.players:
                if treasure not in p.treasure_cards or p.treasure_cards.count(treasure) < 2: continue
                if not max or (treasure in p.treasure_cards and p.treasure_cards.count(treasure) > max.treasure_cards.count(treasure)):
                    max = p
            if max:
                cards[treasure] = max.role.value
            # TODO: No player has an advantage, check locations

    goals = { "shore": shore, "cards": cards }
    print(f"[GOALS] {goals}")
    return { "obs": obs, "goals": goals }

#--------------------------------------------------------------------------------------------------
# Returns the name of the current player - used for routing to the appropriate node
#--------------------------------------------------------------------------------------------------
def take_turn(state: GameState) -> dict:
    player = _game.players[ _game.current_player ]
    _stats[player.role] = _stats.get(player.role, 0) + 1
    return player.role

#--------------------------------------------------------------------------------------------------
# Executes the defined actions in the state and returns the correct next node in the graph
#--------------------------------------------------------------------------------------------------
def action_execution(state: GameState):
    actions = state.get("actions", [])
    print(f"[ACTIONS] {actions}")
    for action in actions:
        result = _game.submit_action(action)

    if _game.get_num_actions() > 0:
        if not actions:
            print("[ SKIP ] remaining actions")
            _game.execute_action("skip")

#--------------------------------------------------------------------------------------------------
# Performs the treasure card draw phase
#--------------------------------------------------------------------------------------------------
def draw(state) :
    print("[ DRAW ] Drawing 2 treasure cards")
    _game.draw_treasure(2)

#--------------------------------------------------------------------------------------------------
# Performs the flood phase
#--------------------------------------------------------------------------------------------------
def flood(state) :
    print(f"[ FLOOD] Drawing flood cards")
    _game.draw_flood()

#--------------------------------------------------------------------------------------------------
# Routing node to determine if the game is over
#--------------------------------------------------------------------------------------------------
def status(state) -> Literal[ "turn", END ]:
    if _game.is_over():
        print("[======== Game over =========]")
        print(f"Turns: {_turns}")
        for key, val in _stats.items():
            print(f"{key}: {val}")
        print("Treasures captured:", end=None)
        for treasure in GameTreasure:
            if getattr(_game.treasures, treasure.name.lower()):
                print(f" {treasure.value}", end=None)
        print()
        print(f"Victory: {_game.final_result}")
        return END
    else:
        return "turn"

#--------------------------------------------------------------------------------------------------
# Build the graph
#--------------------------------------------------------------------------------------------------
def build_graph():
    graph = StateGraph(GameState)

    graph.add_node("start_game", start_game)

    # Define all the nodes you need in your graph
    graph.add_node("turn", turn)
    graph.add_node("action", action)
    graph.add_node("action_execution", action_execution)
    graph.add_node("draw", draw)
    graph.add_node("flood", flood)

    graph.add_node("messenger", messenger)
    graph.add_node("navigator", navigator)
    graph.add_node("engineer", engineer)
    graph.add_node("pilot", pilot)
    graph.add_node("diver", diver)
    graph.add_node("explorer", explorer)


    # Create all the edges you need in your graph
    graph.add_edge(START, "start_game")
    graph.add_edge("start_game", "turn")
    # Phase routes to either action or draw/flood
    graph.add_conditional_edges("turn", phase)
    graph.add_conditional_edges("action", take_turn)
    for role in ["messenger", "navigator", "engineer", "pilot", "diver", "explorer"]:
        graph.add_edge(role, "action_execution")
    # Game can be won here
    graph.add_conditional_edges("action_execution", status)
    # Game can be lost here (waters rise card)
    graph.add_conditional_edges("draw", status)
    # Game can be lost here (flooding in Fools Landing, tile with a player on it, treasure tile)
    graph.add_conditional_edges("flood", status)

    return graph.compile()

#---------------------------------------------------------------------------
# If run directly just create the graph image
#---------------------------------------------------------------------------
if __name__ == "__main__":
    graph = build_graph()

    png_data = graph.get_graph().draw_mermaid_png()
    with open("graph.png", "wb") as f:
        f.write(png_data)

    print("Graph visualization created at graph.png")