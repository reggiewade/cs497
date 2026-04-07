#****************************************************************************
# agent.py - Build 2 agent file
# v1
# Boise State University CS 497
# Dr. Henderson
# Spring 2026
#
# Implements the agent that b2.py uses to solve the maze
#----------------------------------------------------------------------------
from typing import List, Tuple

from langchain.agents import create_agent
from langchain.tools import tool

import chatlib

#--------------------------------------------------------------------------------------------------
# TODO: Define your system prompt. (25 pts)
#--------------------------------------------------------------------------------------------------
SYSTEM_PROMPT = """You are a maze solver
"""

#--------------------------------------------------------------------------------------------------
# Global instance of the game object (set below and available for use in your tools)
#--------------------------------------------------------------------------------------------------
maze_game = None

#--------------------------------------------------------------------------------------------------
# TODO: Define any variables to keep track of state for your agent here. (10 pts)
#--------------------------------------------------------------------------------------------------

#--------------------------------------------------------------------------------------------------
# TODO: Define tools you want your agent to be able to use here. (150 pts)
#--------------------------------------------------------------------------------------------------
@tool('is_solved', description='Returns True if the maze has been solved', return_direct=False)
def is_solved():
    return maze_game.has_won()


#--------------------------------------------------------------------------------------------------
# TODO: Create an array of functions to pass to your agent as tools. (5 pts)
#--------------------------------------------------------------------------------------------------
tools = [ is_solved
          ]

#--------------------------------------------------------------------------------------------------
# Uses chatlib to get a chat model to serve as your agent using your tools and system prompt
#--------------------------------------------------------------------------------------------------
maze_agent = create_agent(
     chatlib.get_chat_model().llm,
    tools = tools,
    system_prompt = SYSTEM_PROMPT
)

#--------------------------------------------------------------------------------------------------
# The agent function will be set to control the maze in b2.py. The maze instance is passed in.
#--------------------------------------------------------------------------------------------------
def agent(game):
    global maze_game
    maze_game = game

    # static approach
    #response = maze_agent.invoke({
    #    'messages': [ { 'role': 'user', 'content': 'Please solve the maze'  } ]
    #})
    #return

    # Send the initial prompt and print trace until the agent solves the maze
    for chunk in maze_agent.stream({
            'messages': [ {'role': 'user', 'content': 'Please solve the maze'} ]
        }):
        for key, value in chunk.items():
            if key == 'tools' and 'messages' in value:
                for msg in value['messages']:
                    print(f"   ↳ Result: {msg.content}")
            elif 'messages' in value:
                for msg in value['messages']:
                    if hasattr(msg, 'content') and msg.content:
                        print(f"💭  Agent: {msg.content}")

                    if hasattr(msg, 'tool_calls') and msg.tool_calls:
                        for tc in msg.tool_calls:
                            print(f"🔧  Calling: {tc['name']}({tc['args']})")


// Total points: 190
