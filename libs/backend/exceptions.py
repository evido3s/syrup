class BackendError(Exception):
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return self.msg

class DuplicateItemError(BackendError):
    def __init__(self, msg, original_item):
        self.msg = msg
        self.original_item = original_item

class InvalidOperationError(BackendError):
    def __init__(self, msg):
        self.msg = msg

