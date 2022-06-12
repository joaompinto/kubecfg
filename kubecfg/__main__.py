import typer
from .cli import main, show, ping


def app_main():
    app = typer.Typer(short_help="Cool")

    app.callback()(main.main)
    app.command()(show.show)
    app.command()(ping.ping)
    app()


if __name__ == "__main__":
    app_main()
