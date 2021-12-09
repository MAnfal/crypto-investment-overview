class CSVRow:
    def __init__(self) -> None:
        self.timestamp = None
        self.transaction_description = None
        self.currency = None
        self.amount = None
        self.to_currency = None
        self.to_amount = None
        self.native_currency = None
        self.native_amount = None
        self.native_amount_in_usd = None
        self.transaction_kind = None