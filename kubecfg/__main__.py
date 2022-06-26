import typer
from .cli import curl, main, show, get


def app_main():
    app = typer.Typer(short_help="Cool")

    app.callback()(main.main)
    app.command()(curl.curl)
    app.command()(show.show)
    app.command()(get.get)
    app()


if __name__ == "__main__":
    app_main()
