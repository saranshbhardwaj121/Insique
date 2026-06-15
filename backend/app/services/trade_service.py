from sqlalchemy.orm import Session


class TradeService:
    def __init__(self, session: Session) -> None:
        self.session = session
