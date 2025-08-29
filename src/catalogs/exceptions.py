from ..exceptions import BadRequestError


class CatalogParserError(BadRequestError):
    def __init__(self, detail: str):
        super().__init__(f"Catalog parser error: {detail}")