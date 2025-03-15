# http://pymorphy2.readthedocs.io/en/latest/user/grammemes.html#grammeme-docs
source = '''
# Вася ест кашу
# сущ  гл  винительный
# что/кто  делает с_чем-то
NOUN,nomn VERB NOUN,accs

# Мама мыла нас
NOUN,nomn VERB NPRO,accs

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

# начал есть
# прошлое инфинитив
past INFN

# Мы сказали спасибо маме
NPRO,nomn VERB NOUN,loct
'''

#  Положительные примеры
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
Я учусь в школе
Младшие братья Миша и Вова ходят в детский сад

Эти типы стали есть на нашем складе

Мама мыла нас
Мы сказали спасибо маме
'''

#  Отрицательные примеры
notext = '''
Сестра Татьяна - учительница
Мама мыла Вася
'''

non_nouns = ['в', 'л', 'и', 'к']

import pymorphy3 as py

names = {}
morph = py.MorphAnalyzer()


class PPattern:
    def __init__(self):
        super().__init__()
        self.tags = []
        self.rules = []
        self.example = ''

    def checkPhrase(self, words, used=None):
        if used is None:
            used = set()

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
                if 'NOUN' in v.tag.grammemes and word in non_nouns:
                    continue
                if checkWordTags(tags, v.tag.grammemes):
                    return (word, v)
            return None

        allResults = []
        result = []
        wordList = list(set([x for x in range(0, len(words))]) - used)
        wordList.sort()
        # print('wordList',wordList)
        wi = getNextWord(wordList)
        nextTag = 0
        usedP = set()
        while wi is not None:
            # print('wordList',wordList, 'wi',wi)
            w = words[wi]
            res = checkWord(self.tags[nextTag].split(','), w)
            if res is not None:
                result.append(res)
                usedP.add(wi)
                nextTag = nextTag + 1
                if nextTag >= len(self.tags):
                    return (result, usedP)
            wi = getNextWord(wordList)
        return None

    def checkPropRule(self, getFunc, getArgs, srcFunc, srcArgs, op=lambda x, y: x == y):
        return op(getFunc(getArgs), srcFunc(srcArgs))

    def setProp(self, setFunc, setArgs, srcFunc, srcArgs):
        setFunc(setArgs, srcFunc(srcArgs))


import io


def parseSource(src):
    def parseFunc(v, names):
        dest = v.split('.')
        index = names.index(dest[0])
        dest = (eval('lambda a: a.' + dest[1]), index)
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
            # last.example = s
        if s[0] == ':':  # имена
            names[s[1:]] = last
        elif s[0] == '-':  # внутренние имена
            s = [x.strip('-') for x in s.split()]
            last.names = s
        elif s[0] == '=':  # правила
            s = [x for x in s[1:].split() if x != '']
            dest = parseFunc(s[0], last.names)
            src = parseFunc(s[2], last.names)
            last.rules.append(((dest[1], src[1]), dest, src))
        else:
            last.tags = s.split()

    arr = []
    last = None
    buf = io.StringIO(src)
    line = buf.readline()
    while line:
        parseLine(line)
        line = buf.readline()
    return arr


def parseText(pats, text):
    def parseLine(line):
        words = line.split()
        allSet = set([x for x in range(len(words))])
        used = set()
        was = False
        # print(used)
        for p in pats:
            usedP = set()
            while True:
                res = p.checkPhrase(words, usedP)
                if res:
                    # print(res)
                    (res, newP) = res
                    # if newP < usedP:
                    #    break
                    used = used.union(newP)
                    # print(words,usedP,newP)
                    first = list(newP)[0]
                    usedP = set([x for x in range(first + 1)])
                    print('+', line, p.tags, [r[0] for r in res])
                    was = True
                else:
                    break
        if not was:
            print('-', line)
            for word in line.split():
                print(" ", word + ':')
                for v in morph.parse(word):
                    print("   ", ','.join([g for g in v.tag.grammemes]))
            # break

    buf = io.StringIO(text)
    s = buf.readline()
    while s:
        s = s.strip()
        if s != '':
            parseLine(s)
        s = buf.readline()


if __name__ == "__main__":
    patterns = parseSource(source)
    print("Положительные примеры")
    parseText(patterns, text)
    print("Отрицательные примеры")
    parseText(patterns, notext)
