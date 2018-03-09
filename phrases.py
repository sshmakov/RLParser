# http://pymorphy2.readthedocs.io/en/latest/user/grammemes.html#grammeme-docs
source = '''
# Вася ест кашу
# сущ  гл  сущ
# что/кто  делает с_чем-то
NOUN,nomn VERB NOUN,accs

# Именованная сущность
:SNOUN
# Красивый цветок
ADJF NOUN
-a-  -b-
# Правила выведения, разделяющие пробелы обязательны
= a.case = b.case
= a.number = b.number
= a.gender = b.gender

# Птица сидит на крыше
# сущ  гл  предлог сущ
NOUN,nomn VERB PREP NOUN,loct
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

names = {}

class PPattern:
    def __init__(self):
        super().__init__()
        self.tags = []
        self.rules = []
        self.example = ''

    def checkPhrase(self, words, used = set()):
        def getNextWord():
            nonlocal wordList
            if len(wordList) == 0:
                return None
            nextTag = wordList[0]
            wordList[0:1] = []
            return nextTag
                
        def checkWordTags(tags, grams):
            for t in tags:
                if t not in grams:
                    return False
            return True
        
        def checkWord(tags, word):
            variants = morph.parse(word)
            for v in variants:
                if checkWordTags(tags, v.tag.grammemes):
                    return (word, v)
            return None
        
        morph = py.MorphAnalyzer()
        allResults = []
        result = []
        wordList = list(set([ x for x in range(0, len(words)) ]) - used)
        wordList.sort()
        wi = getNextWord()
        nextTag = 0
        while wi is not None:
            w = words[wi]
            res = checkWord(self.tags[nextTag].split(','), w)
            if res is not None:
                result.append(res)
                used.add(wi)
                nextTag = nextTag + 1
                if nextTag >= len(self.tags):
                    return (result, used)
            wi = getNextWord()
        return None

    def checkPropRule(self, getFunc, getArgs, srcFunc, srcArgs, \
                      op = lambda x,y: x == y):
        return op(destFunc(destArgs), srcFunc(srcArgs))

    def setProp(self, setFunc, setArgs, srcFunc, srcArgs):
        setFunc(setArgs, srcFunc(srcArgs))
                  
    

import io

def parseSource(src):
    def parseFunc(v):
        dest = v.split('.')
        dest = (eval('lambda a: a.' + dest[1]), dest[0])
        return dest
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
            #last.example = s
        if s[0] == ':': # имена
            names[s[1:]] = last
        elif s[0] == '-': # внутренние имена
            s = [x.strip('-') for x in s.split()]
            last.names = s
        elif s[0] == '=': # правила
            s = [x for x in s[1:].split() if x != '']
            dest = parseFunc(s[0])
            src = parseFunc(s[2])
            last.rules.append((dest, src))
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
        words = line.split()
        allSet = set([x for x in range(len(words))])
        used = set()
        while used < allSet:
            was = False
            for p in pats:
                res = p.checkPhrase(words,used)
                if res:
                    (res, used) = res
                    print('+',line, p.tags, [r[0] for r in res])
                    was = True
            if not was:                
                print('-',line)
                break

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
