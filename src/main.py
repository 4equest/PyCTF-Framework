import utils
import framework

import argparse
import pygments.lexers.asm
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.syntax import Syntax

if __name__ == "__main__":
    console = Console()
    parser = argparse.ArgumentParser()
    # どのくらい起動時の引数指定できたらいいと思う？
    parser.add_argument(
        "--config",
        type=str,
        default="config.toml",
        help="config file path"
    )
    parser.add_argument(
        "--web-ui",
        action="store_true",
        help="use web ui instead of command line"
    )
    parser.add_argument(
        "--debug", "-d",
        action="store_true",
        help="debug mode"
    )
    args = parser.parse_args()
    print(parser.format_help())

    console.print(Panel(Syntax(parser.format_help(), lexer=pygments.lexers.asm.CObjdumpLexer()), title="help", expand=False))
    exit(0)
    