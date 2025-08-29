from ..exceptions import BadRequestError


class ProductParserError(BadRequestError):
    def __init__(self, detail: str):
        super().__init__(f"Product parser error: {detail}")