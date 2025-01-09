

class VarBuffer:

    def store(self, name: str, value):
        self.__setattr__(name, value)


vars_ = VarBuffer()

