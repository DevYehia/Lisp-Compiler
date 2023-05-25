from Tokens import *
import re
def Tokens_to_dict(Tokens):
    tokens_List = []
    for i in range(len(Tokens)):
        dct = Tokens[i].to_dict()
        if dct["token_type"] == Token_type.Comment:
            continue
        tokens_List.append(dct)
    return tokens_List

def getDelimiters(tokens_List,delimiter_List):
    for token in range(len(tokens_List)):
        if tokens_List[token]["token_type"] == Token_type.RightBracket:
            delimiter_List.append(token)


def getQuotations(text):
    lst = list()
    for i in range(len(text)):
        if text[i] == "\"":
            lst.append(i)
    return lst


def find_token(text,Tokens):
    text = text.lower()

    ########################
    # Start String Extraction
    ########################

    quote_list = getQuotations(text)
    words = []
    if len(quote_list) == 0:
        words = text.split()
    else:
        if quote_list[0] != 0:
            for word in text[0:quote_list[0]].split():
                words.append(word)

    i = 0
    while i < len(quote_list) - 1:
        words.append(text[quote_list[i]:quote_list[i + 1] + 1])
        i += 1
        if i == len(quote_list) - 1:
            for word in text[quote_list[i] + 1:len(text)].split():
                words.append(word)
        else:
            for word in text[quote_list[i] + 1:quote_list[i + 1]].split():
                words.append(word)
        i += 1
    if len(quote_list) % 2 != 0:
        words.append(text[quote_list[-1]:len(text)])

    #########################
    # End of String Extraction
    #########################
    commentfound = False
    commentInmiddle=-1
    wordPosition=-1
    for index, word in enumerate(words):
        if commentfound:
            break

        start = 0
        end = len(word) - 1
        if word[0] != '\"':
            semiColonIndex = word.find(";")
            if semiColonIndex == 0:
                commentfound = True
                break
            elif semiColonIndex != -1:
                end = semiColonIndex - 1
                word = word[0:semiColonIndex]
                commentfound= True
                wordPosition=index
                commentInmiddle=semiColonIndex


            # for Left Brackets
            while start <= end and word[start] == '(':
                Tokens.append(token('(', Token_type.LeftBracket))
                start += 1
            # get start of Right Brackets
            while start <= end and word[end] == ')':
                end -= 1

            # word only consisted of brackets
            if start > end:
                while end != len(word) - 1:
                    Tokens.append(token(')', Token_type.RightBracket))
                    end += 1
                
                continue

        # bracket-free word

        innerWord = word[start:end + 1]
        # check for reserved words
        if innerWord in ReservedWords:
            Tokens.append(token(innerWord, ReservedWords[innerWord]))

        # check for operators
        elif innerWord in Operators:
            Tokens.append(token(innerWord, Operators[innerWord]))

        elif re.match('\"[^"]*\"', innerWord):
            Tokens.append(token(innerWord, Token_type.String))


        elif re.match(r'^-?[0-9]+(\.[0-9]+)?$', innerWord):
            Tokens.append(token(innerWord, Token_type.Constant))

        elif re.match("[^#\'\"`]+", innerWord):
            Tokens.append(token(innerWord, Token_type.Identifier))


        else:
            Tokens.append(token(innerWord, Token_type.Error))

        while end != len(word) - 1:
            Tokens.append(token(')', Token_type.RightBracket))
            end += 1

    #comment token
    if commentfound:
        if commentInmiddle != -1 :
            index2=wordPosition
        else:
            index2=index

        comment=""
        while index2 < len(words):
            if comment == "" :
                if commentInmiddle != -1 :
                    comment = comment + words[index2][commentInmiddle:]
                else:
                    comment=comment+words[index2]
                index2 += 1
            else :
                comment=comment+" "+words[index2]
                index2 += 1
        Tokens.append(token(comment, Token_type.Comment))