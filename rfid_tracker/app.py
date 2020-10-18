from datetime import datetime
from pathlib import Path

import RPi.GPIO as GPIO
import sqlalchemy
import typer
from mfrc522 import SimpleMFRC522
from models import Action, Base, Member

MAX_SPOTS = 19

app = typer.Typer()


def init_db(db_path: Path):
    engine_url = f"sqlite:///{db_path}"
    typer.echo(f"Opening db {engine_url}...")
    engine = sqlalchemy.create_engine(engine_url)
    Base.metadata.create_all(engine)
    Session = sqlalchemy.orm.sessionmaker(bind=engine)
    return Session()


def scan_card(reader, session):
    typer.secho("💳 Please scan your card...", fg=typer.colors.BLUE)
    card_id, _ = reader.read()
    typer.secho(f"💳 Card number {card_id} scanned", fg=typer.colors.GREEN)
    user_in_db = session.query(Member).filter_by(card_id=card_id).first()
    return card_id, user_in_db


def hello(first_name, last_name):
    typer.secho(f"👋 Hello {first_name} {last_name}!", fg=typer.colors.GREEN)


def bye(first_name, last_name):
    typer.secho(f"👋 Bye {first_name} {last_name}!", fg=typer.colors.RED)


def no_spots():
    typer.secho("🛑 NO AVAILABLE SPOTS!", fg=typer.colors.RED)


def ask_details():
    while True:
        first_name = typer.prompt("❓ What is your first name?")
        last_name = typer.prompt("❓ What is your last name?")
        if typer.confirm("❓ Is the information above correct?"):
            break
    return first_name, last_name


def register_new_member(session, card_id):
    typer.secho("🆕 Creating a new member", fg=typer.colors.GREEN)
    first_name, last_name = ask_details()
    new_member = Member(
        card_id=card_id,
        first_name=first_name,
        last_name=last_name,
        registration_dt=datetime.now(),
    )
    session.add(new_member)
    session.commit()


@app.command()
def register(
    db_path: Path = typer.Option(
        default="db.sqlite3",
        file_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
    )
):
    """Register a new member in the cohort."""
    reader = SimpleMFRC522()
    session = init_db(db_path)
    typer.secho("🆕 Registering new members", fg=typer.colors.MAGENTA)
    try:
        while True:
            card_id, user_in_db = scan_card(reader, session)
            if user_in_db:
                typer.secho(
                    f"💳 Card {card_id} already registered to\n"
                    f"First Name: {user_in_db.first_name}\n"
                    f"Last Name:  {user_in_db.last_name}\n"
                    f"⌚ Registration time: {user_in_db.registration_dt}",
                    fg=typer.colors.RED,
                )
                if typer.confirm("❓ Want to edit the above information?"):
                    first_name, last_name = ask_details()
                    user_in_db.first_name = first_name
                    user_in_db.last_name = last_name
                    user_in_db.registration_dt = datetime.now()
                    session.commit()
            else:
                register_new_member(session, card_id)
            if not typer.confirm("❓ Do you want to register another member?"):
                break
    finally:
        GPIO.cleanup()


@app.command()
def tracker(
    db_path: Path = typer.Option(
        default="db.sqlite3",
        file_okay=True,
        writable=True,
        readable=True,
        resolve_path=True,
    )
):
    """Track occupancy in the cohort."""
    reader = SimpleMFRC522()
    session = init_db(db_path)
    typer.secho("📋 Tracking occupancy", fg=typer.colors.MAGENTA)

    try:
        while True:
            n_occupied_spots = len(
                list(session.query(Member).filter(Member.room_id == 1))
            )
            if n_occupied_spots == MAX_SPOTS:
                no_spots()
            else:
                __color__ = (
                    typer.colors.GREEN
                    if n_occupied_spots < MAX_SPOTS * 0.75
                    else typer.colors.YELLOW
                )
                typer.secho(
                    f"🪑 {n_occupied_spots} occupied, {MAX_SPOTS - n_occupied_spots} free spots",
                    fg=__color__,
                )
            card_id, user_in_db = scan_card(reader, session)
            if user_in_db:
                if user_in_db.room_id:
                    new_action = Action(
                        member=user_in_db,
                        action_type_id=1,
                        time=datetime.now(),
                        room_id=user_in_db.room_id,
                    )
                    user_in_db.room_id = None
                    session.add(new_action)
                    session.commit()
                    bye(user_in_db.first_name, user_in_db.last_name)
                else:
                    if n_occupied_spots < MAX_SPOTS:
                        user_in_db.room_id = 1
                        new_action = Action(
                            member=user_in_db,
                            action_type_id=0,
                            time=datetime.now(),
                            room_id=user_in_db.room_id,
                        )
                        session.add(new_action)
                        session.commit()
                        hello(user_in_db.first_name, user_in_db.last_name)
                    else:
                        no_spots()
            else:
                typer.secho(
                    f"❗ Card {card_id} not found in database!", fg=typer.colors.RED
                )
                if typer.confirm(f"❓ Want to register {card_id} as a new member?"):
                    register_new_member(session, card_id)
    finally:
        GPIO.cleanup()


if __name__ == "__main__":
    app()
