from local_workflow.abstract_game import AbstractGame
from external_tools.shortest_path_tools import _load_graph, inspect, move, submit

class ShortestPathGame(AbstractGame):
    # ------------------------------------------------------------------ #
    # Lifecycle hooks                                                    #
    # ------------------------------------------------------------------ #
    def _on_start(self, agent):
        super()._on_start(agent)           # send system + user prompts first

        info = _load_graph(self.configs)   # build graph internally
        agent.update(
            f"Graph loaded: start={info['start']}, end={info['end']}, "
            f"optimal_cost={info['optimal_cost']}",
            role="assistant"
        )

    # ------------------------------------------------------------------ #
    # Tool handler                                                       #
    # ------------------------------------------------------------------ #
    def tool_handler(self, agent, tools_avail):
        call = agent.messages[-1].tool_calls[0]     # single-tool call pattern
        name = call["function"]["name"]
        args = call["function"]["arguments"]

        if name == "inspect":
            return inspect()
        elif name == "move":
            return move(**args)
        elif name == "submit":
            self.solution = {"path": args["path"]}  # stop condition
            return submit(**args)
        else:
            raise ValueError(f"Unknown tool {name}")
