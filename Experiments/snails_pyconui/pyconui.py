from __future__ import annotations
from typing import List, Dict
try: # Import colorama
    import colorama
except ImportError:
    input("This library requires colorama to work properly. Please use 'pip install colorama' and try again.")
    exit(None)
from sys import platform
from os import system
colorama.init()

def print_error(e : str = "Unknown error"):
    print(f"{colorama.Fore.RED}{colorama.Back.BLACK}{colorama.Style.BRIGHT}ERROR: '{e}'")
    input("Press enter to continue...")

#region SCREEN CLEAR SETUP
cls = lambda : None
if platform == "linux" or platform == "linux2":
    cls = lambda : [system("clear"), print('\e[3J')]
elif platform == "darwin":
    cls = lambda : system("osascript -e 'if application \"Terminal\" is frontmost then tell application \"System Events\" to keystroke \"k\" using command down'")
elif platform == "win32":
    cls = lambda : system("cls")
else:
    print_error("pyconui is not compatible with your operating system. The program will shut down.")
    exit(None)
#endregion

#region COLOR & STYLE DICS AND METHODS FOR FBS
_fcolor = {
    "white" : colorama.Fore.WHITE, 
    "yellow" : colorama.Fore.YELLOW,
    "cyan" : colorama.Fore.CYAN,
    "magenta" : colorama.Fore.MAGENTA,
    "red" : colorama.Fore.RED,
    "green" : colorama.Fore.GREEN,
    "blue" : colorama.Fore.BLUE,
    "black" : colorama.Fore.BLACK
    }

_bcolor = {
    "white" : colorama.Back.WHITE, 
    "yellow" : colorama.Back.YELLOW,
    "cyan" : colorama.Back.CYAN,
    "magenta" : colorama.Back.MAGENTA,
    "red" : colorama.Back.RED,
    "green" : colorama.Back.GREEN,
    "blue" : colorama.Back.BLUE,
    "black" : colorama.Back.BLACK
    }

_style = {
    "bright" : colorama.Style.BRIGHT,
    "normal" : colorama.Style.NORMAL,
    "dim" : colorama.Style.DIM
}

def get_cuifbs(f : str = "white", b : str = "black", s : str = "bright") -> str:
    try:
        f = _fcolor[f]
    except:
        print_error(f"Could not find fore color: '{f}'")
        f = ""
    try:
        b = _bcolor[b]
    except:
        print_error(f"Could not find back color: '{b}'")
        b = ""
    try:
        s = _style[s]
    except:
        print_error(f"Could not find style: '{s}'")
        s = ""
    return f + b + s
#endregion

class CUIScreen:
    """_summary_
    Represents a console screen that remains the same shape but has some content that can change.
    """
    def __init__(self, lines : List[CUILine]):
        self.lines : List[CUILine] = lines
    
    def __str__(self):
        value = ""
        for line in self.lines:
            value += line.__str__() + "\n"
        return value[:-1]
    
    def print(self):
        cls()
        print(self.__str__(), end="")

class CUILine:
    """
    Represents a single line inside a CUIScreen.
    """
    
    def __init__(self, content : list = [], fbs : str = f"{colorama.Fore.WHITE}{colorama.Back.BLACK}{colorama.Style.NORMAL}"):
        self._content : list = content
        self._fbs : str = fbs
    
    def set_fbs(self, fbs : str): # Set fore, back, style
        """_summary_
        Sets a prefix that is always put behind the line, intended to contain a "Fore-Back-Style" value, based on coloramas constants.
        Args:
            fbs (str): A string prefix
        """
        self._fbs = fbs
    
    def __str__(self) -> str:
        value = ""
        for c in self.content:
            if c is not str:
                value += c.__str__()
            else:
                value += self.fbs + c
        return value

class CUILineContent:
    """
    Represents a space where content can be written inside a CUILine
    """
    _next_id : int = 0
    _contents : Dict[int, CUILineContent] = {}
    
    def __init__(self, length : int = 1, value : str = "", fbs : str = ""):
        self.id = CUILineContent._next_id
        CUILineContent._next_id += 1
        self._length = length
        self._fbs = fbs
        self._value = value
        CUILineContent._contents[self.id] = self
        
    def set_fbs(self, fbs : str):
        self._value = fbs + self._value[len(self._fbs):]
        self._fbs = fbs
    
    def set_value(self, value):
        self._value = self._fbs
        if len(value) > self._length:
            self._value += value[:self._length]
        elif len(value) == self._length:
            self._value += value
        else:
            self._value += value
            self._value += " "*(self._length - len(value))
    
    def __str__(self) -> str:
        return self._value
    
    @staticmethod
    def get_content(id : int) -> CUILineContent:
        return CUILineContent._contents[id]

def parse_content(content : str) -> CUILineContent:
    pass

def parse_line(line : str) -> CUILine:
    parsed = []
    current_s = ""
    special = False
    content_mode = False
    for i in range(len(line)):
        c = line[i]
        if not content_mode:
            if c == "{":
                if not special:
                    parsed.append(current_s)
                    current_s = ""
                    content_mode = True
                else:
                    special = False
                    current_s += c
            elif c == "\n":
                break
            elif c == "\\":
                if special:
                    special = False
                    current_s += "\\"
                else:
                    special == True
            else:
                if special:
                    special = False
                    current_s += "\\"
                current_s += c
        else:
            if c == "}":
                parse_content(current_s)
                current_s = ""
                content_mode = False
            else:
                current_s += c
                
    # TODO: Allow setting of fbs in lines and, you know, stuff
    return CUILine(parsed, "")

def parse_cuiscreen(lines) -> CUIScreen:
    parsed = []
    for l in lines:
        parsed.append(parse_line(l))
    screen = CUIScreen(parsed)
    
def load_cuiscreen(f) -> CUIScreen:
    lines = None
    try:
        with open(f, "r") as file:
            lines = file.readlines()
    except:
        print_error(f"Could not open file '{f}'")
        exit(None)
    return parse_cuiscreen(lines)
    