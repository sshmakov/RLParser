
source = '''
Вася ест кашу
# сущ  гл  сущ
# что/кто  делает с_чем-то
NOUN,nomn VERB NOUN,accs

'''

text = '''
Мама мыла раму
Вася разбил окно
Лара сама мыла раму
Рано ушла наша Шура
Мама мыла пластиковые окна
'''

class PPattern:
    def __init__(self):
        super().__init__()


import io

def parseSource(src):
    def parseLine(s):
        nonlocal arr, last
        s = s.strip()
        if s == '':
            last = None
            return
        if s[0] == '#':
            return
        if last is None:
            last = PPattern()
            arr.append(last)
            last.example = s
        else:
            last.tags = s.split()
        
    arr = []
    last = None
    buf = io.StringIO(src)
    s = buf.readline()
    while s:
        parseLine(s)
        s = buf.readline()
    return arr


#print(a.split('\n'))
s = parseSource(source)
