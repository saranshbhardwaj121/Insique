from sqlalchemy.orm import Session


class WatchlistService:
    def __init__(self, session: Session) -> None:
        self.session = session
