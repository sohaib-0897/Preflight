"""Durable local worker; poll interval and shutdown are bounded."""
import logging
import signal
import time
from sqlalchemy import select
from .db import Database, EvaluationRun
from .jobs import perform, transition, ACTIVE

stop = False


def shutdown(*_):
    global stop
    stop = True


def tick(database):
    with database.sessions() as db:
        expired = db.scalars(select(EvaluationRun).where(EvaluationRun.status.in_(ACTIVE), EvaluationRun.lease_until < time.time())).all()
        for run in expired:
            transition(db, run, "BLOCKED", "Worker lease expired; infrastructure failure requires explicit rerun")
        next_id = db.scalar(select(EvaluationRun.id).where(EvaluationRun.status == "QUEUED").order_by(EvaluationRun.created_at).limit(1))
    if next_id:
        return perform(database, next_id)
    return False


def main():
    signal.signal(signal.SIGTERM, shutdown)
    signal.signal(signal.SIGINT, shutdown)
    database = Database()
    database.initialize()
    while not stop:
        try:
            tick(database)
        except Exception:
            logging.exception("Worker infrastructure error")
        time.sleep(.5)
    database.engine.dispose()


if __name__ == "__main__":
    main()
