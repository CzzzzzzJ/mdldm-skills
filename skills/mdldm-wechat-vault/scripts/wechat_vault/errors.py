class VaultError(Exception):
    def __init__(self, code, message):
        self.code=code;self.message=message
        super().__init__(message)

def require(test,code,message):
    if not test: raise VaultError(code,message)
