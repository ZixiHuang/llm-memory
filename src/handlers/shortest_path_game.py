from local_workflow.environment import AbstractGame
from external_tools import (
    observe, move, submit_solution, verify, _init_graph, G, _current
)
import json
import copy

class ShortestPathGame(AbstractGame):
    """
    One episode = generate a fresh graph, expose observe/move/submit tools,
    let LLM explore until it calls submit_solution().
    """
    def __init__(self, configs, setup_data, tools, results_path=""):
        # Inject graph parameters & initialise tools
        graph_kw = configs["graph_params"]
        _init_graph(**graph_kw)

        # Now G should be initialized, so we can access its properties
        from external_tools import G
        
        # Add graph information to setup_data for templates
        setup_data.update({
            "start_node": G.start,
            "goal_node": G.end,
            "current_node": G.start
        })

        super().__init__(configs, setup_data, tools, results_path)

    # ------------------------------------------------------------------ #
    # Tool dispatch                                                      #
    # ------------------------------------------------------------------ #
    def tool_handler(self, agent, tools_avail):
        """
        Follow the same pattern as QwenGame/LlamaGame for tool handling.
        """
        tool_schemas = [self.tool_schemas[tool_name] for tool_name in tools_avail]
        message = agent.act(tool_schemas=tool_schemas)
        content = message.content or None
        
        # Check if response contains tool calls
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_calls = [
                {
                    "id": tool_call.id,
                    "type": "function",
                    "function": {
                        "name": tool_call.function.name,
                        "arguments": tool_call.function.arguments
                    }
                } for tool_call in message.tool_calls
            ]
            # Llama can only handle a single tool call at once
            tool_calls = tool_calls[:1]
            agent.update(content, role="assistant", tool_calls=tool_calls)
            output = copy.deepcopy(tool_calls)
            for tool_call in output: 
                tool_call['function']['arguments'] = json.loads(tool_call['function']['arguments'])
        else:
            agent.update(content, role="assistant")
            output = content 
            
        if type(output) == list:
            # Execute tools and add results
            for tool_call in output:
                tool_name = tool_call['function']['name']
                tool_args = tool_call['function']['arguments']
                
                if tool_name == "submit_solution":
                    self.solution = tool_args
                    return
                    
                if tool_name in tools_avail and tool_name in self.tools:
                    # Execute the tool
                    tool_result = self.tools[tool_name](**tool_args)
                    tool_call['output'] = tool_result
                    
                    # Update current node position if agent moved
                    if tool_name == "move":
                        from external_tools import _current
                        self.setup_data["current_node"] = _current
                    
                    # Add tool result to agent conversation
                    agent.update(
                        role="tool",
                        content=str(tool_result),
                        tool_call_id=tool_call['id'],
                    )
            
            # Let assistant process tool results before adding user message  
            assistant_response = agent.generate().content
            agent.update(assistant_response, role='assistant')
            
        # Return the final response
        return output
