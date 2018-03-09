# http://pymorphy2.readthedocs.io/en/latest/user/grammemes.html#grammeme-docs
source = '''
# Вася ест кашу
# сущ  гл  сущ
# что/кто  делает с_чем-то
NOUN,nomn VERB NOUN,accs
-a-        -b- -c-  -d-
= a.tag.number = b.tag.number

# Именованная сущность
:SNOUN
# Красивый цветок
ADJF NOUN
-a-  -b-
# Правила выведения, разделяющие пробелы обязательны
= a.tag.case = b.tag.case
= a.tag.number = b.tag.number
= a.tag.gender = b.tag.gender

# Птица сидит на крыше
# сущ  гл  предлог сущ
NOUN,nomn VERB PREP NOUN,loct
-a-        -b- -c-  -d-
= a.tag.number = b.tag.number

# стали есть
VERB INFN

# хомяк Коля
NOUN Name
-a-  -b-
= a.tag.case = b.tag.case
= a.tag.number = b.tag.number

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

Эти типы стали есть на нашем складе
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
        def getNextWord(wordList):
            if len(wordList) == 0:
                return None
            index = wordList[0]
            wordList[0:1] = []
            return index
                
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
        wi = getNextWord(wordList)
        nextTag = 0
        usedP = set()
        while wi is not None:
            w = words[wi]
            res = checkWord(self.tags[nextTag].split(','), w)
            if res is not None:
                result.append(res)
                usedP.add(wi)
                if not self.checkRules(usedP, result):
                    result.remove(res)
                    usedP.remove(wi)
                else:
                    nextTag = nextTag + 1
                    if nextTag >= len(self.tags):
                        return (result, usedP)
            wi = getNextWord(wordList)
        return None

    def checkRules(self, used, result):
        for r in self.rules:
            if max(r[0]) < len(result): # У нас есть достаточно данных
                destRes = result[r[0][0]]
                destV = destRes[1]
                destFunc = r[1][0]
                srcRes = result[r[0][1]]
                srcFunc = r[2][0]
                srcV = srcRes[1]
                if not self.checkPropRule(destFunc,destV, srcFunc, srcV):
                    return False
        return True

    def checkPropRule(self, getFunc, getArgs, srcFunc, srcArgs, \
                      op = lambda x,y: x == y):
        v1 = getFunc(getArgs)
        v2 = srcFunc(srcArgs)
        return op(v1,v2)

    def setProp(self, setFunc, setArgs, srcFunc, srcArgs):
        setFunc(setArgs, srcFunc(srcArgs))

import io

def parseSource(src):
    def parseFunc(v, names):
        dest = v.split('.')
        index = names.index(dest[0])
        dest = (eval('lambda a: a.' + '.'.join(dest[1:])), index)
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
        if s[0] == ':': # имена
            names[s[1:]] = last
        elif s[0] == '-': # внутренние имена
            s = [x.strip('-') for x in s.split()]
            last.names = s
        elif s[0] == '=': # правила
            s = [x for x in s[1:].split() if x != '']
            dest = parseFunc(s[0],last.names)
            src = parseFunc(s[2],last.names)
            last.rules.append(((dest[1],src[1]), dest, src))
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
        was = False
        for p in pats:
            usedP = set()
            while True:
                res = p.checkPhrase(words, usedP)
                if res:
                    (res, newP) = res
                    used = used.union(newP)
                    first = list(newP)[0]
                    usedP = set([ x for x in range(first+1)])
                    print('+',line, p.tags, [r[0] for r in res])
                    was = True
                else:
                    break
        if not was:
            print('-',line)

    buf = io.StringIO(text)
    s = buf.readline()
    while s:
        s = s.strip()
        if s != '':
            parseLine(s)
        s = buf.readline()

def tags(word):
    morph = py.MorphAnalyzer()
    return morph.parse(word)

patterns = parseSource(source)
parseText(patterns, text)
