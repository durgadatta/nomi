from typing import Iterator

# control flow exception should not be caught
# by broad "Exception", so use one level up!
class ControlException(BaseException):
    pass

class ReturnException(ControlException):
    def __init__(self, value: Any):
        self.value = value

class BreakException(ControlException):
    pass

class ContinueException(ControlException):
    pass

class YieldException(ControlException):
    def __init__(self, value: Any):
        self.value = value

class YieldFromException(ControlException):
    def __init__(self, iterator: Iterator):
        self.iterator = iterator

