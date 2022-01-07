from pathlib import Path
import sys
pointer = 0
class_sym_table = {}
sub_sym_table = {}
field_nm = 0
static_nm = 0
arg_nm = 0
local_nm = 0
class_name = ""
label_index = 0
counter = 0
def parser_comment(file_path):
    '''
    This function is to parser all comments, white spaces and blank lines.
    :param file_path: it is string type. And it just vm file path that we want to translate.
    :return: return is the text that without comments, white spaces and blank lines.
    '''
    file = open(file_path, "r")  # read the input file
    read = ''
    for i in file:  # remove blank line(with only whitespace and just a newline)
        if i.isspace() or i == '\n':
            continue
        else:
            read += i
    text = read
    rem_lis = []

    for i in range(len(text)):  # remove comments
        remove = ''

        if text[i] == '/' and text[i + 1] == '/' and (text[i - 1] == '\n' or i == 0):
            # for remove // comment that with newline
            while True:  # and consider the comment at the begin of the content
                if text[i] == '\n':  # to find the newline then break the while loop
                    remove += text[i]  # need to include the newline symbol to remove the blank lines
                    i += 1
                    break
                else:
                    remove += text[i]
                    i += 1
            rem_lis.append(remove)  # store all remove content into the list
        if text[i] == '/' and text[i + 1] == '/':  # for remove // comment
            while True:
                if text[i] == '\n':  # to find the newline then break the while loop
                    break  # don't need to include the newline symbol
                elif i == len(text) - 1:  # deal with at the end of the content is comment.
                    remove += text[i]
                    break
                else:
                    remove += text[i]
                    i += 1
            rem_lis.append(remove)  # store all remove content into the list
        remove = ''
        if text[i] == '/' and text[i + 1] == '*':  # for remove /*.....*/ comment
            while True:
                if i == len(text) - 2:  # when the input file only have one /*, and it will remove all
                    # content after the /*
                    if text[i] != '*' and text[i + 1] != '/':
                        remove += text[i]
                        remove += text[i + 1]
                        break
                if text[i] == '*' and text[i + 1] == '/':  # when we find */ to stop the while loop
                    remove += text[i]
                    remove += text[i + 1]
                    if text[i + 2] == "\n":  # if */ with a newline symbol we need to remove it,
                        remove += text[i + 2]  # make sure that the output don't have blank lines
                    break
                else:
                    remove += text[i]
                    i += 1
            rem_lis.append(remove)
    for i in range(len(rem_lis)):
        text = text.replace(rem_lis[i], "", 1)  # replace the all comments to "" for 1 time.
    file.close()
    text = text.replace('.', ' . ')     # make these symbol more spaces, it will be easy token.
    text = text.replace(',', ' , ')
    text = text.replace(';', ' ; ')
    text = text.replace('(', ' ( ')
    text = text.replace(')', ' ) ')
    text = text.replace('[', ' [ ')
    text = text.replace(']', ' ] ')
    text = text.replace('{', ' { ')
    text = text.replace('}', ' } ')
    text = text.replace('-', ' - ')
    text = text.replace('+', ' + ')
    text = text.replace('*', ' * ')
    text = text.replace('/', ' / ')
    text = text.replace('&', ' & ')
    text = text.replace('|', ' | ')
    text = text.replace('<', ' < ')
    text = text.replace('>', ' > ')
    text = text.replace('=', ' = ')
    text = text.replace('~', ' ~ ')
    text = text.replace('\n', ' ')
    text = text.replace('\t', ' ')
    token = []
    setence = ""
    i=0
    while i< len(text):

        if text[i] == "\"":     # to get the stringConstant with two quotation mark "".
            setence += text[i]
            i += 1
            while text[i] != "\"":
                setence += text[i]
                i += 1
            setence += text[i]
            i +=1
            token.append(setence)
            setence = ""

        elif text[i] != " ":
            setence += text[i]
            i += 1

            while text[i] != " ":       # if it is not space, we token it as a whole word.
                setence += text[i]
                i+=1
            token.append(setence)
            setence = ''
        else:
            i += 1

    return token

def token_fun(token, key_dict):
    """
    For this function, we just get the special format of the token.
    :param token: token is the content get from the .jack file
    :param key_dict: it is the dictionary which contain all "keyword", "symbol" and so on.
    :return: return is the special format that we need to token.
    """
    i = 0
    xml_value = ""
    while i < len(token):
        if token[i] in key_dict["keyword"]:     # if the word is inside the dict of [keyword]
            xml_value += "<keyword> " + token[i] + " </keyword>\n"
            i +=1
        elif token[i] in key_dict["symbol"]:     # if the word is inside the dict of [symbol]
            if token[i] == "<":         # three special cases which are "<" , ">" and "&"
                xml_value += "<symbol> " + "&lt;" + " </symbol>\n"
                i += 1
            elif token[i] == ">":
                xml_value += "<symbol> " + "&gt;" + " </symbol>\n"
                i += 1
            elif token[i] == "&":
                xml_value += "<symbol> " + "&amp;" + " </symbol>\n"
                i += 1
            else:
                xml_value += "<symbol> " + token[i] + " </symbol>\n"
                i += 1
        elif token[i].isdigit():        # if the token is digit
            value = int(token[i])
            if 0 <= value <= 32767:
                xml_value += "<integerConstant> " + str(value) + " </integerConstant>\n"
                i += 1
        elif "\"" in token[i]:      # if the token with quotation mark

            front = token[i].find("\"")
            back = token[i].find("\"", front + 1)
            con_str = token[i][front + 1:back]

            xml_value += "<stringConstant> " + con_str + " </stringConstant>\n"
            i += 1
        else:
            xml_value += "<identifier> " + token[i] + " </identifier>\n"
            i += 1
    return xml_value

def compileEngine(token_value, xml_value):
    """
    Start parser the token.
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer

    if "class" in token_value[pointer]:
        xml_value = compileClass(token_value, xml_value)

    return xml_value

def compileClass(token_value, xml_value):           # start for class rule
    """
    for class rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global class_name

    pointer += 1
    if "identifier" in token_value[pointer]:
        class_name = token_value[pointer]
        class_name = class_name[13:]
        class_name = class_name[:-14]
        xml_value = compileName_OrSymbol(token_value, xml_value)
    if "{" in token_value[pointer]:
        xml_value = compileName_OrSymbol(token_value, xml_value)
    if "static" in token_value[pointer] or "field" in token_value[pointer]:
        xml_value = recuriveVarDec(token_value, xml_value)
    if "constructor" in token_value[pointer] or "function" in token_value[pointer] or "method" in token_value[pointer]:
        xml_value = recuriveSubDec(token_value, xml_value)
    if "}" in token_value[pointer]:  # the last "}" in the token.
        xml_value = compileName_OrSymbol(token_value, xml_value)
    return xml_value

def recuriveVarDec(token_value, xml_value):
    '''
    for classVarDec*  in the class rule. check contain "static" or "field"
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    '''
    global pointer
    if "static" in token_value[pointer] or "field" in token_value[pointer]:
        xml_value = compileVarDec(token_value, xml_value)
    return xml_value

def recuriveSubDec(token_value, xml_value):
    '''
    for subroutineDec*  in the class rule. check contain "constructor" or "function" or "method"
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    '''
    global pointer
    if "constructor" in token_value[pointer] or "function" in token_value[pointer] or "method" in token_value[pointer]:
        xml_value = compileSubDec(token_value, xml_value)
    return xml_value

def compileSubDec(token_value, xml_value):
    """
    for the subroutineDec rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global sub_sym_table
    global local_nm
    global arg_nm
    global class_name

    if "constructor" in token_value[pointer] or "function" in token_value[pointer]:
        if "constructor" in token_value[pointer]:
            kind = "constructor"
        else:
            kind = "function"
        pointer += 1

        if "void" in token_value[pointer]:
            pointer += 1
        else:
            xml_value = compileType(token_value, xml_value)
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            xml_value = compileName_OrSymbol(token_value, xml_value)
        if "(" in token_value[pointer]:
            xml_value = compileName_OrSymbol(token_value, xml_value)
            xml_value = compileParaList(token_value, xml_value)
        if ")" in token_value[pointer]:
            xml_value = compileName_OrSymbol(token_value, xml_value)
        xml_value = compileSubBody(token_value, xml_value, kind, name)
    elif "method" in token_value[pointer]:
        sub_sym_table.update({"this": [class_name, "argument", arg_nm]})
        arg_nm +=1
        kind = "method"
        pointer += 1
        if "void" in token_value[pointer]:
            pointer += 1
        else:
            xml_value = compileType(token_value, xml_value)
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            xml_value = compileName_OrSymbol(token_value, xml_value)
        if "(" in token_value[pointer]:
            xml_value = compileName_OrSymbol(token_value, xml_value)
            xml_value = compileParaList(token_value, xml_value)
        if ")" in token_value[pointer]:
            xml_value = compileName_OrSymbol(token_value, xml_value)
        xml_value = compileSubBody(token_value, xml_value, kind, name)

    sub_sym_table.clear()
    local_nm = 0
    arg_nm = 0

    xml_value = recuriveSubDec(token_value, xml_value)
    return xml_value

def compileSubBody(token_value, xml_value, kind, name):
    """
    for the subroutineBody rule.
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global local_nm
    global class_name
    global field_nm
    if "{" in token_value[pointer]:
        xml_value = compileName_OrSymbol(token_value, xml_value)
    if "var" in token_value[pointer]:
        xml_value = recusiveSubBody(token_value, xml_value)
    xml_value += "function " + class_name + "." + name + " " + str(local_nm) + "\n"
    if kind == "constructor":
        xml_value += "push constant " + str(field_nm) + "\n"
        xml_value += "call Memory.alloc 1\n"
        xml_value += "pop pointer 0\n"
    elif kind == "method":
        xml_value += "push argument 0\n"
        xml_value += "pop pointer 0\n"
    xml_value = compileStates(token_value, xml_value)
    if "}" in token_value[pointer]:
        pointer += 1

    return xml_value

def recusiveSubBody(token_value, xml_value):
    """
    for varDec* in the subroutineBody rule.
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    if "var" in token_value[pointer]:
        xml_value = compilevarDeclear(token_value, xml_value)
    else:
        return xml_value
    return xml_value

def compileStates(token_value, xml_value):      # statements
    """
    start for statements rule.
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    xml_value = recusiveState(token_value, xml_value)
    return xml_value

def recusiveState(token_value, xml_value):
    """
    for statement rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    if "let" in token_value[pointer]:
        xml_value = compileLetState(token_value, xml_value)
    if "if" in token_value[pointer]:
        xml_value = compileIfState(token_value, xml_value)
    if "while" in token_value[pointer]:
        xml_value = compileWhileState(token_value, xml_value)
    if "do" in token_value[pointer]:
        xml_value = compileDoState(token_value, xml_value)
    if "return" in token_value[pointer]:
        xml_value = compileReturnState(token_value, xml_value)
    return xml_value

def compileLetState(token_value, xml_value):
    """
    for letStatement rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global class_sym_table
    global sub_sym_table
    pointer += 1
    names = token_value[pointer]
    names = names[13:]
    names = names[:-14]
    pointer += 1
    if "[" in token_value[pointer]:
        flag_arr = True
        pointer += 1
        if "identifier" in token_value[pointer]:
            variable = token_value[pointer]
            variable = variable[13:]
            variable = variable[:-14]
            pointer += 1
            if variable in sub_sym_table:
                xml_value += "push " + str(sub_sym_table[variable][1]) + " " + str(sub_sym_table[variable][2]) + "\n"
            elif variable in class_sym_table:
                xml_value += "push " + str(class_sym_table[variable][1]) + " " + str(class_sym_table[variable][2]) + "\n"
        if names in sub_sym_table:
            xml_value += "push " + str(sub_sym_table[names][1]) + " " + str(sub_sym_table[names][2]) + "\n"
        elif names in class_sym_table:
            xml_value += "push " + str(class_sym_table[names][1]) + " " + str(class_sym_table[names][2]) + "\n"
        xml_value = compileExpr(token_value, xml_value)
        xml_value += "add\n"
        pointer +=1
    else:
        flag_arr = False
    if "=" in token_value[pointer]:
        pointer += 1
        xml_value = compileExpr(token_value, xml_value)
        pointer += 1
    if ";" in token_value[pointer]:
        pointer += 1
    if flag_arr:
        xml_value += "pop temp 0\n"
        xml_value += "pop pointer 1\n"
        xml_value += "push temp 0\n"
        xml_value += "pop that 0\n"
    else:
        if names in sub_sym_table:
            xml_value += "pop " + str(sub_sym_table[names][1]) + " " + str(sub_sym_table[names][2]) + "\n"
        elif names in class_sym_table:
            xml_value += "pop " + str(class_sym_table[names][1]) + " " + str(class_sym_table[names][2]) + "\n"
    xml_value = compileStates(token_value, xml_value)
    return xml_value

def compileIfState(token_value, xml_value):
    """
    for ifStatement rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global label_index
    label1= "L" + str(label_index)
    label_index += 1
    label2 = "L" + str(label_index)
    label_index += 1
    pointer += 1
    if "(" in token_value[pointer]:
        pointer += 1
        xml_value = compileExpr(token_value, xml_value)
        pointer += 1
        xml_value += "not\n"
        xml_value += "if-goto " + label1 + "\n"
    if "{" in token_value[pointer]:
        pointer += 1
        xml_value += "goto " + label2 + "\n"
        xml_value += "label " + label1 + "\n"
        xml_value = compileStates(token_value, xml_value)
        pointer += 1
        """xml_value += "goto " + label2 + "\n"
        xml_value += "label " + label1 + "\n" """
    if "else" in token_value[pointer]:
        pointer += 1
        if "{" in token_value[pointer]:
            pointer += 1

            xml_value = compileStates(token_value, xml_value)
            pointer += 1
            xml_value += "label " + label2 + "\n"

    xml_value = compileStates(token_value, xml_value)
    return xml_value

def compileWhileState(token_value, xml_value):
    """
    for whileState rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global label_index
    label1 = "L" + str(label_index)
    label_index += 1
    label2 = "L" + str(label_index)
    label_index += 1
    pointer += 1
    xml_value += "label " + label1 + "\n"
    if "(" in token_value[pointer]:
        pointer += 1
        xml_value = compileExpr(token_value, xml_value)
        pointer += 1
        xml_value += "not\n"
        xml_value += "if-goto " + label2 + "\n"
    if "{" in token_value[pointer]:
        pointer += 1
        xml_value = compileStates(token_value, xml_value)
        pointer += 1
        xml_value += "goto " + label1 + "\n"
        xml_value += "label " + label2 + "\n"

    xml_value = compileStates(token_value, xml_value)
    return xml_value

def compileDoState(token_value, xml_value):
    """
    for doStatement rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    pointer += 1
    names = token_value[pointer]
    names = names[13:]
    names = names[:-14]
    pointer += 1
    xml_value = compileSubCall(token_value, xml_value, names)
    if ";" in token_value[pointer]:
        pointer += 1
    xml_value += "pop temp 0\n"
    xml_value = compileStates(token_value, xml_value)
    return xml_value

def compileReturnState(token_value, xml_value):
    """
    for returnStatement rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer

    pointer += 1
    if ";" not in token_value[pointer]:
        xml_value = compileExpr(token_value, xml_value)
        pointer += 1
    else:
        xml_value += "push constant 0\n"
        xml_value += "return\n"
        pointer += 1

    xml_value = compileStates(token_value, xml_value)
    return xml_value

def compileExpr(token_value, xml_value):        # for expression
    """
    for expression rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer

    xml_value = compileTerm(token_value, xml_value)
    if "+" in token_value[pointer]:
        xml_value = recusiveOpTerm(token_value, xml_value)
        xml_value += "add\n"
    if "-" in token_value[pointer]:
        xml_value = recusiveOpTerm(token_value, xml_value)
        xml_value += "sub\n"
    if "*" in token_value[pointer]:
        xml_value = recusiveOpTerm(token_value, xml_value)
        xml_value += "call Math.multiply 2\n"
    if " /" in token_value[pointer]:
        xml_value = recusiveOpTerm(token_value, xml_value)
        xml_value += "call Math.divide 2\n"
    if "&amp" in token_value[pointer]:
        xml_value = recusiveOpTerm(token_value, xml_value)
        xml_value += "and\n"
    if "|" in token_value[pointer]:
        xml_value = recusiveOpTerm(token_value, xml_value)
        xml_value += "or\n"
    if "&lt" in token_value[pointer]:
        xml_value = recusiveOpTerm(token_value, xml_value)
        xml_value += "lt\n"
    if "&gt" in token_value[pointer]:
        xml_value = recusiveOpTerm(token_value, xml_value)
        xml_value += "gt\n"
    if "=" in token_value[pointer]:
        xml_value = recusiveOpTerm(token_value, xml_value)
        xml_value += "eq\n"
    return xml_value

def recusiveOpTerm(token_value, xml_value):
    """
    for (op term)* in the expression rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    pointer +=1
    xml_value = compileExpr(token_value, xml_value)
    return xml_value

def compileTerm(token_value, xml_value):
    """
    for term rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global sub_sym_table
    global class_sym_table
    if "integerConstant" in token_value[pointer]:
        number = token_value[pointer]
        number = number[18:]
        number = number[:-19]
        xml_value += "push constant " + number + "\n"
        pointer +=1
    elif "stringConstant" in token_value[pointer]:
        sent = token_value[pointer]
        sent = sent[17:]
        sent = sent[:-18]
        xml_value += "push constant " + str(len(sent)) + "\n"
        xml_value += "call String.new 1\n"
        for char in sent:
            xml_value += "push constant " + str(ord(char)) + "\n"
            xml_value += "call String.appendChar 2\n"
        pointer += 1
    elif "true" in token_value[pointer]:
        xml_value += "push constant 0\n"
        xml_value += "not\n"
        pointer += 1
    elif "false" in token_value[pointer]:
        xml_value += "push constant 0\n"
        pointer +=1
    elif "null" in token_value[pointer]:
        xml_value += "push constant 0\n"
        pointer +=1
    elif "this" in token_value[pointer]:
        xml_value += "push pointer 0\n"
        pointer +=1
    elif "identifier" in token_value[pointer]:
        names = token_value[pointer]
        names = names[13:]
        names = names[:-14]
        pointer +=1
        if "[" in token_value[pointer]:
            pointer += 1
            if "identifier" in token_value[pointer]:
                variable = token_value[pointer]
                variable = variable[13:]
                variable = variable[:-14]
                if variable in sub_sym_table:
                    xml_value += "push " + str(sub_sym_table[variable][1]) + " " + str(sub_sym_table[variable][2]) + "\n"
                elif variable in class_sym_table:
                    xml_value += "push " + str(class_sym_table[variable][1]) + " " + str(class_sym_table[variable][2]) + "\n"
            if names in sub_sym_table:
                xml_value += "push " + str(sub_sym_table[names][1]) + " " + str(sub_sym_table[names][2]) + "\n"
            elif names in class_sym_table:
                xml_value += "push " + str(class_sym_table[names][1]) + " " + str(class_sym_table[names][2]) + "\n"
            pointer += 1
            xml_value = compileExpr(token_value, xml_value)
            pointer += 1
            xml_value += "add\n"
            xml_value += "pop pointer 1\n"
            xml_value += "push that 0\n"
        elif "(" in token_value[pointer]:
            xml_value = compileSubCall(token_value, xml_value, names)

        elif "." in token_value[pointer]:
            xml_value = compileSubCall(token_value, xml_value, names)
        else:
            if names in sub_sym_table:
                xml_value += "push " + str(sub_sym_table[names][1]) + " " + str(sub_sym_table[names][2]) + "\n"
            elif names in class_sym_table:
                xml_value += "push " + str(class_sym_table[names][1]) + " " + str(class_sym_table[names][2]) + "\n"

    elif "(" in token_value[pointer]:
        pointer +=1
        xml_value = compileExpr(token_value, xml_value)
        pointer += 1
    elif "~" in token_value[pointer]:
        pointer +=1
        xml_value = compileTerm(token_value, xml_value)
        xml_value += "not\n"
    elif "-" in token_value[pointer]:
        pointer += 1
        xml_value = compileTerm(token_value, xml_value)
        xml_value += "neg\n"

    return xml_value

def compileSubCall(token_value, xml_value, names):     # for subroutineCall
    """
    for subroutineCall rule, took the subroutineName, className and varName before call this function
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global class_name
    global sub_sym_table
    global class_sym_table
    global counter
    if "(" in token_value[pointer]:
        pointer += 1
        xml_value += "push pointer 0\n"
        names = class_name + "." + names
        xml_value = compileExprList(token_value, xml_value)
        pointer += 1
    elif "." in token_value[pointer]:
        pointer += 1
        if names in sub_sym_table:
            xml_value += "push " + str(sub_sym_table[names][1]) + " " + str(sub_sym_table[names][2]) + "\n"
            names = sub_sym_table[names][0] + "."
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            names += name
        elif names in class_sym_table:
            xml_value += "push " + str(class_sym_table[names][1]) + " " + str(class_sym_table[names][2]) + "\n"
            names = class_sym_table[names][0] + "."
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            names += name
        else:
            names = names + "."
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            names += name
        pointer += 1
        if "(" in token_value[pointer]:
            pointer += 1
            xml_value = compileExprList(token_value, xml_value)
            pointer += 1
    xml_value += "call " + names + " " + str(counter) + "\n"
    return xml_value

def compileExprList(token_value, xml_value):
    """
    for expressionList rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global counter
    counter = 0
    if ")" not in token_value[pointer]:
        counter += 1
        xml_value = compileExpr(token_value, xml_value)

        if "," in token_value[pointer]:
            xml_value = recusiveExp(token_value, xml_value)
    else:
        counter += 1

    return xml_value

def recusiveExp(token_value, xml_value):
    """
    for (, expression)* in the expressionList rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global counter
    if "," in token_value[pointer]:
        counter += 1
        pointer += 1
        xml_value = compileExpr(token_value, xml_value)
        xml_value = recusiveExp(token_value, xml_value)
    return xml_value

def compilevarDeclear(token_value, xml_value):          # for varDec
    """
    for varDec rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global sub_sym_table
    global local_nm
    kind = "local"
    pointer +=1
    if "int" in token_value[pointer]:
        typ = "int"
        pointer +=1
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, local_nm]})
            local_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
        if "," in token_value[pointer]:
            pointer += 1
            xml_value = recusiveVarName(token_value, xml_value, typ)
    elif "char" in token_value[pointer]:
        typ = "char"
        pointer += 1
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, local_nm]})
            local_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
        if "," in token_value[pointer]:
            pointer += 1
            xml_value = recusiveVarName(token_value, xml_value, typ)
    elif "boolean" in token_value[pointer]:
        typ = "boolean"
        pointer += 1
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, local_nm]})
            local_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
        if "," in token_value[pointer]:
            pointer += 1
            xml_value = recusiveVarName(token_value, xml_value,typ)
    elif "identifier" in token_value[pointer]:
        typ = token_value[pointer]
        typ = typ[13:]
        typ = typ[:-14]
        xml_value = compileName_OrSymbol(token_value, xml_value)
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, local_nm]})
            local_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
        if "," in token_value[pointer]:
            pointer += 1
            xml_value = recusiveVarName(token_value, xml_value, typ)
    if ";" in token_value[pointer]:
        xml_value = compileName_OrSymbol(token_value, xml_value)
    xml_value = recusiveSubBody(token_value, xml_value)
    return xml_value

def compileParaList(token_value, xml_value):
    """
    for parameterList rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global sub_sym_table
    global arg_nm
    kind = "argument"
    if "int" in token_value[pointer]:
        typ = "int"
        pointer +=1
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, arg_nm]})
            arg_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
    elif "char" in token_value[pointer]:
        typ = "char"
        pointer += 1
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, arg_nm]})
            arg_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
    elif "boolean" in token_value[pointer]:
        typ = "boolean"
        pointer += 1
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, arg_nm]})
            arg_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
    elif "identifier" in token_value[pointer]:
        typ = token_value[pointer]
        typ = typ[13:]
        typ = typ[:-14]
        xml_value = compileName_OrSymbol(token_value, xml_value)
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, arg_nm]})
            arg_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
    if "," in token_value[pointer]:
        xml_value = recusiveTypeVarName(token_value, xml_value)

    return xml_value

def recusiveTypeVarName(token_value, xml_value):
    """
    for (, type varName)* in the parameterList rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global sub_sym_table
    global arg_nm
    kind = "argument"
    pointer += 1
    if "int" in token_value[pointer]:
        typ = "int"
        pointer += 1
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, arg_nm]})
            arg_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
    elif "char" in token_value[pointer]:
        typ = "char"
        pointer += 1
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, arg_nm]})
            arg_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
    elif "boolean" in token_value[pointer]:
        typ = "boolean"
        pointer += 1
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, arg_nm]})
            arg_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
    elif "identifier" in token_value[pointer]:
        typ = token_value[pointer]
        typ = typ[13:]
        typ = typ[:-14]
        xml_value = compileName_OrSymbol(token_value, xml_value)
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            sub_sym_table.update({name: [typ, kind, arg_nm]})
            arg_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
    if "," in token_value[pointer]:
        xml_value = recusiveTypeVarName(token_value, xml_value)
    return xml_value

def compileName_OrSymbol(token_value, xml_value):
    """
    for just extending the name or symbol into the xml_value.
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    pointer +=1
    return xml_value

def compileVarDec(token_value, xml_value):
    """
    for classVarDec rule
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global class_sym_table
    global field_nm
    global static_nm
    if "field" in token_value[pointer]:
        kind = "this"
        pointer += 1
        if "int" in token_value[pointer]:
            typ = "int"
        elif "char" in token_value[pointer]:
            typ = "char"
        elif "boolean" in token_value[pointer]:
            typ = "boolean"
        else:
            typ = token_value[pointer]
            typ = typ[13:]
            typ = typ[:-14]
        xml_value = compileType(token_value, xml_value)
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            class_sym_table.update({name: [typ, kind, field_nm]})
            field_nm += 1
            xml_value = compileName_OrSymbol(token_value, xml_value)
        if "," in token_value[pointer]:
            pointer += 1
            xml_value = recusiveVarNameField(token_value, xml_value, typ)  # for , varName
        if ";" in token_value[pointer]:
            xml_value = compileName_OrSymbol(token_value, xml_value)
    elif "static" in token_value[pointer]:
        kind = "static"
        pointer += 1
        if "int" in token_value[pointer]:
            typ = "int"
        elif "char" in token_value[pointer]:
            typ = "char"
        elif "boolean" in token_value[pointer]:
            typ = "boolean"
        else:
            typ = token_value[pointer]
            typ = typ[13:]
            typ = typ[:-14]
        xml_value = compileType(token_value, xml_value)
        if "identifier" in token_value[pointer]:
            name = token_value[pointer]
            name = name[13:]
            name = name[:-14]
            class_sym_table.update({name: [typ,kind,static_nm]})
            static_nm +=1
            xml_value = compileName_OrSymbol(token_value, xml_value)
        if "," in token_value[pointer]:
            pointer += 1
            xml_value = recusiveVarNameStat(token_value, xml_value,typ)     # for , varName
        if ";" in token_value[pointer]:
            xml_value = compileName_OrSymbol(token_value, xml_value)
    xml_value = recuriveVarDec(token_value, xml_value)
    return xml_value

def recusiveVarName(token_value, xml_value, typ):   # for , varName
    """
    for (, varName)* in the classVarDec rule.
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global sub_sym_table
    global local_nm
    kind = "local"
    if "identifier" in token_value[pointer]:
        name = token_value[pointer]
        name = name[13:]
        name = name[:-14]
        sub_sym_table.update({name: [typ, kind, local_nm]})
        local_nm += 1
        pointer +=1
        if "," in token_value[pointer]:
            pointer += 1
            xml_value = recusiveVarName(token_value, xml_value, typ)
        else:
            return xml_value
    return xml_value


def recusiveVarNameField(token_value, xml_value, typ):   # for , varName
    """
    for (, varName)* in the classVarDec rule.
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global class_sym_table
    global field_nm
    if "identifier" in token_value[pointer]:
        kind = "this"
        name = token_value[pointer]
        name = name[13:]
        name = name[:-14]
        pointer +=1
        class_sym_table.update({name: [typ, kind, field_nm]})
        field_nm += 1
        if "," in token_value[pointer]:
            pointer += 1
            xml_value = recusiveVarNameField(token_value, xml_value, typ)
        else:
            return xml_value
    return xml_value

def recusiveVarNameStat(token_value, xml_value, typ):   # for , varName
    """
    for (, varName)* in the classVarDec rule.
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    global class_sym_table
    global static_nm

    if "identifier" in token_value[pointer]:
        kind = "static"
        name = token_value[pointer]
        name = name[13:]
        name = name[:-14]
        pointer +=1
        class_sym_table.update({name: [typ, kind, static_nm]})
        static_nm += 1
        if "," in token_value[pointer]:
            pointer += 1
            xml_value = recusiveVarNameStat(token_value, xml_value, typ)
        else:
            return xml_value
    return xml_value

def compileType(token_value, xml_value):
    """
    for type rule.
    :param token_value: the token content in the list
    :param xml_value: previous content
    :return: the content that need to write into file
    """
    global pointer
    if "int" in token_value[pointer]:
        pointer +=1
    elif "char" in token_value[pointer]:
        pointer += 1
    elif "boolean" in token_value[pointer]:
        pointer += 1
    else:
        xml_value = compileName_OrSymbol(token_value, xml_value)
    return xml_value

def main():
    key_dict = {"keyword": ["class", "constructor", "function", "method", "field", "static", "var",
                            "int", "char", "boolean", "void", "true", "false", "null", "this",
                            "let", "do", "if", "else", "while", "return"],
                "symbol": ["{", "}", "(", ")", "[", "]", ".", ",", ";", "+", "-", "*", "/",
                           "&", "|", "<", ">", "=", "~"]
                }
    path = sys.argv[-1]  # read input from the command line.
    file_path = Path(path)  # the path should be use forward slashes or backward slashes. It will be converted
    global class_sym_table
    global field_nm
    global static_nm
    if file_path.is_dir():
        if "\\" in str(file_path):      # for backward slash path
            out_file = str(file_path)
            out_file = out_file.split("\\")[-1]
            out_file = str(file_path) + "\\"

        elif "/" in str(file_path):     # for forward slash path
            out_file = str(file_path)
            out_file = out_file.split("/")[-1]
            out_file = str(file_path) + "/"

        for files in file_path.iterdir():     # search all files in the directory with .jack files
            vm_code = ""
            global pointer
            pointer = 0
            if files.suffix ==".jack":
                file_path = str(files)
                out_file = file_path[:-5]
                out_file = out_file + ".vm"
                token = parser_comment(file_path)    # remove the comment
                token_value = token_fun(token, key_dict)
                token_value = token_value.split("\n")
                xml_value = compileEngine(token_value, vm_code)

                class_sym_table.clear()
                field_nm =0
                static_nm =0

                f = open(out_file,"w")
                f.write(xml_value)
                f.close()

    elif file_path.is_file():       # deal with only one .jack file
        vm_code=""
        out_file = str(file_path)  # store the string type data path
        out_file = out_file[:-5]  # remove the .jack for the input data path

        out_file = out_file + ".vm"  # store the path and output file name
        token = parser_comment(str(file_path))
        token_value = token_fun(token, key_dict)
        token_value = token_value.split("\n")
        xml_value = compileEngine(token_value,vm_code)

        class_sym_table.clear()
        field_nm = 0
        static_nm = 0
        f = open(out_file, "w")  # out_file include the path of the input file and it will create a .asm file in that path
        f.write(xml_value)
        f.close()
if __name__ == '__main__':
    main()
