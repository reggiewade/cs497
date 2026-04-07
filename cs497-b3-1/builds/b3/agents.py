#****************************************************************************
# agents.py - Forbidden Island multi-agent app llm agents
# v1
# Boise State University CS 497
# Dr. Henderson
# Spring 2026
#
# Create your llm-based agents here and import them in the graph.py module.
# Put all your prompts in the prompts.py module and import them here.
#----------------------------------------------------------------------------
import json

from dotenv import load_dotenv

from langchain_core.messages import SystemMessage, HumanMessage

from lib import state
import lib.chatlib as chatlib
import prompts

from lib.state import ActionResponse
from lib.events import GameAction, ActionType
from lib.state import GameState

#--------------------------------------------------------------------------------------------------
# LLMs
#
# You can set an llm to use structured output like this:
#
# llm = llm.with_structured_output(ActionResponse, method="json_mode")
#
# This will try to force the llm to adhere to the structure of ActionResponse, but you will likely
# still want to prompt it as well.
#--------------------------------------------------------------------------------------------------
load_dotenv()
# TODO: Create instances of the llms you want to use. You may want to have several types and sizes

# Agent 1 is the "reasoning" agent that decides what actions to take
llm1 = chatlib.get_chat_model("BSU_")
# Agent 2 is the "execution" agent that takes the reasoning from Agent 1 and turns it into the final GameAction format
llm2 = chatlib.get_chat_model("API_").llm.with_structured_output(ActionResponse)

#--------------------------------------------------------------------------------------------------
# Helper functions
#--------------------------------------------------------------------------------------------------
def _llm_player(state: GameState, role: str) -> dict:
    # 1. THE STRATEGIST (LLM1)
    strategy_prompt = prompts.get_strategy_prompt(state, role)
    strategy_suggestion = llm1.invoke(strategy_prompt.to_messages())

    # 2. THE TRANSLATOR (LLM2)
    translation_prompt = f"Convert this plan into a structured JSON action list: {strategy_suggestion.content}"
    structured_output = llm2.invoke([
        SystemMessage(content="You are a translation engine. Output only JSON."),
        HumanMessage(content=translation_prompt)
    ])

    # 3. CONVERT TO GAME ACTIONS
    game_actions = []
    for act in structured_output.actions:
        game_actions.append(GameAction(type=act.type, name=act.name, args=act.args))

    return {"actions": game_actions}


#--------------------------------------------------------------------------------------------------
# AI Agents
#
# These functions are called from the graph.py module on a player's turn either for actions or
# to discard. They should return a dictionary with any state variable updates but especially
# the "actions" variable which should be set to a list of GameAction objects representing the
# actions to take.
#
# For example, to move the player you could return:
#
#  { "actions": [ GameAction(type=ActionType.MOVE, args={"direction": "up"}) ] }
#
# You may want to have a pipeline of agent calls to get the output you need. For example, you
# could have one llm call do the reasoning about what actions to take, and a different llm to
# put it in the ActionResponse format. Then you can manually process that into the final GameAction
# format.
#--------------------------------------------------------------------------------------------------
# TODO: Implement AI versions of all the players
def messenger(state: GameState) -> dict:
    return _llm_player(state, "messenger")

def navigator(state: GameState) -> dict:
    return _llm_player(state, "navigator")

def explorer(state: GameState)  -> dict:
    return _llm_player(state, "explorer")

def pilot(state: GameState) -> dict:
    return _llm_player(state, "pilot")

def diver(state: GameState) -> dict:
    return _llm_player(state, "diver")

def engineer(state: GameState) -> dict:
    return _llm_player(state, "engineer")
