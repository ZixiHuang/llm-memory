import argparse
from local_workflow.agent import BaseAgent
from local_workflow.local_logging.utils import setup_logs, configure_logging
from src.handlers.shortest_path_game import ShortestPathGame
from external_tools import (
    observe, move, submit_solution
)

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--config_file", required=True)
    p.add_argument("--log-level", default="TRACE")
    args = p.parse_args()

    configure_logging(args.log_level)
    config, results_path = setup_logs(args.config_file)

    # Tools exposed this run
    tools = [observe, move, submit_solution]

    # Create the game instance directly
    game = ShortestPathGame(config, setup_data={}, tools=tools, results_path=results_path)
    agent = BaseAgent(config["generation"], config["server"])
    game.play(agent)

    print("✅ Optimal path found!" if game.correctness else "❌ Not optimal.")