import argparse
from local_workflow.agent import BaseAgent
from local_workflow.local_logging.utils import setup_logs, configure_logging
from local_workflow import environment
from external_tools import observe, move, submit_solution, verify, _init_graph
import inspect

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', type=str, help="location of config file")
    parser.add_argument(
        '--log-level',
        default='TRACE',
        choices=['DEBUG', 'TRACE', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help='Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)'
    )
    args = parser.parse_args()

    configure_logging(level=args.log_level)
    config, results_path = setup_logs(args.config_file)

    # Initialize the graph
    graph_kw = config["graph_params"]
    _init_graph(**graph_kw)

    # Re-import G after initialization
    from external_tools import G

    # Prepare setup_data for templates
    setup_data = {
        "start_node": G.start,
        "goal_node": G.end,
        "current_node": G.start
    }

    tools = [observe, move, submit_solution, verify]

    env_classes = {
        name: cls
        for name, cls in inspect.getmembers(environment, inspect.isclass)
        if cls.__module__ == environment.__name__
    }

    game = env_classes[config['tool']['handler']](config, setup_data=setup_data, tools=tools, results_path=results_path)
    agent = BaseAgent(config["generation"], config["server"])
    game.play(agent)

    print("✅ Optimal path found!" if game.correctness else "❌ Not optimal.")