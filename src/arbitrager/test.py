from pprint import pformat

from colorama import init, Fore


class ColorfulString(str):
    def __repr__(self):
        return self.__str__()


init(autoreset=True)
s = ColorfulString('default ' + Fore.BLUE + 'red')
# s.__repr__() = s.__str__()
print(pformat(s))
# print(s)
