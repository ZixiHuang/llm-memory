import argparse, inspect
from local_workflow.local_logging.utils import setup_logs, configure_logging
from local_workflow.agent import BaseAgent
from local_workflow import environment
from external_tools.shortest_path_tools import inspect, move, submit

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", required=True)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    configure_logging(level=args.log_level)
    config, results_path = setup_logs(args.config_file)

    # Locate the handler
    env_classes = {
        n: c for n, c in inspect.getmembers(environment, inspect.isclass)
        if c.__module__ == environment.__name__
    }
    Game = env_classes[config["tool"]["handler"]]

    game = Game(
        configs=config,
        setup_data={},                 # no per-record data
        tools=[inspect, move, submit], # 👈 NO load_graph here
        results_path=results_path
    )
    agent = BaseAgent(config["generation"], config["server"])
    game.play(agent)
    print("Solved?", game.correctness, "Path:", game.solution)

if __name__ == "__main__":
    main()
