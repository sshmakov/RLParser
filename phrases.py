# http://pymorphy2.readthedocs.io/en/latest/user/grammemes.html#grammeme-docs
source = '''
Вася ест кашу
# сущ  гл  сущ
# что/кто  делает с_чем-то
NOUN,nomn VERB NOUN,accs

Красивый цветок
ADJF NOUN

Птица сидит на крыше
# сущ  гл  предлог сущ
NOUN,nomn VERB NOUN,loct
'''

text = '''
Мама мыла раму
Вася разбил окно
Лара сама мыла раму
Рано ушла наша Шура
Мама мыла пластиковые окна

Наша семья
У нас большая семья
Папа и брат Илья работают на заводе
Мама ведет хозяйство
Сестра Татьяна - учительница
Я учусь в школе
Младшие братья Миша и Вова ходят в детский сад
'''

import pymorphy2 as py

class PPattern:
    def __init__(self):
        super().__init__()

    def checkPhrase(self,text):
        def checkWordTags(tags, grams):
            for t in tags:
                if t not in grams:
                    return False
            return True
        def checkWord(tags, word):
            variants = morph.parse(word)
            for v in variants:
                if checkWordTags(self.tags[nextTag].split(','), v.tag.grammemes):
                    return (word, v)
            return None
        
        morph = py.MorphAnalyzer()
        words = text.split()
        nextTag = 0
        result = []
        for w in words:
            res = checkWord(self.tags[nextTag].split(','), w)
            if res is not None:
                result.append(res)
                nextTag = nextTag + 1
                if nextTag >= len(self.tags):
                    return result
        return None

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


def parseText(pats, text):
    def parseLine(line):
        was = False
        for p in pats:
            res = p.checkPhrase(line)
            if res:
                print('+',line, p.tags, [r[0] for r in res])
                was = True
        if not was:                
            print('-',line)

    buf = io.StringIO(text)
    s = buf.readline()
    while s:
        s = s.strip()
        if s != '':
            parseLine(s)
        s = buf.readline()

#print(a.split('\n'))
patterns = parseSource(source)
parseText(patterns, text)
