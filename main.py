import logging
from enum import Enum
import re

class TokenClass(Enum):
    CONST_TRUE = 1
    CONST_FALSE = 2
    CONST_NIL = 3
    THIS = 4
    SUPER = 5
    WHILE = 6
    PRINT = 7
    RETURN = 8
    IF = 9
    ELSE = 10
    FOR = 11
    VAR = 12
    FUN = 13
    LOGIC_AND = 14
    LOGIC_OR = 15
    OPERATOR_NOT = 16
    OPERATOR_GT = 17
    OPERATOR_GTE = 18
    OPERATOR_LT = 19
    OPERATOR_LTE = 20
    OPERATOR_NOT_EQUAL = 21
    OPERATOR_EQUAL = 22
    OPERATOR_ADD = 23
    OPERATOR_SUB = 24
    OPERATOR_MUL = 25
    OPERATOR_DIV = 26
    OPERATOR_ASSIGN = 27
    DELIM_OPEN_PAREN = 28
    DELIM_CLOSE_PAREN = 29
    DELIM_OPEN_BRACE = 30
    DELIM_CLOSE_BRACE = 31
    DELIM_DOT = 32
    DELIM_COMMA = 33
    DELIM_SEMICOLON = 34
    CONST_NUMBER = 35
    CONST_STRING = 36
    IDENTIFIER = 37
    END_OF_FILE = 38

class Token:
    def __init__(self, token_class, value):
        self.token_class = token_class
        self.value = value

    def __str__(self):
        return "<Token: {} - {}>".format(self.token_class.name, self.value)

class Lexer:
    def __init__(self, text):
        self.text = text
        self.tokens = self.tokenize()
        self.current_token_index = 0

    def tokenize(self):
        token_specification = [
            (TokenClass.CONST_TRUE, r"true\b"),
            (TokenClass.CONST_FALSE, r"false\b"),
            (TokenClass.CONST_NIL, r"nil\b"),
            (TokenClass.THIS, r"this\b"),
            (TokenClass.SUPER, r"super\b"),
            (TokenClass.WHILE, r"while\b"),
            (TokenClass.PRINT, r"print\b"),
            (TokenClass.RETURN, r"return\b"),
            (TokenClass.IF, r"if\b"),
            (TokenClass.ELSE, r"else\b"),
            (TokenClass.FOR, r"for\b"),
            (TokenClass.VAR, r"var\b"),
            (TokenClass.FUN, r"fun\b"),
            (TokenClass.LOGIC_AND, r"and\b"),
            (TokenClass.LOGIC_OR, r"or\b"),
            (TokenClass.OPERATOR_NOT, r"!"),
            (TokenClass.OPERATOR_GT, r">"),
            (TokenClass.OPERATOR_GTE, r">="),
            (TokenClass.OPERATOR_LT, r"<"),
            (TokenClass.OPERATOR_LTE, r"<="),
            (TokenClass.OPERATOR_NOT_EQUAL, r"!="),
            (TokenClass.OPERATOR_EQUAL, r"=="),
            (TokenClass.OPERATOR_ADD, r"\+"),
            (TokenClass.OPERATOR_SUB, r"\-"),
            (TokenClass.OPERATOR_MUL, r"\*"),
            (TokenClass.OPERATOR_DIV, r"\/"),
            (TokenClass.OPERATOR_ASSIGN, r"="),
            (TokenClass.DELIM_OPEN_PAREN, r"\("),
            (TokenClass.DELIM_CLOSE_PAREN, r"\)"),
            (TokenClass.DELIM_OPEN_BRACE, r"\{"),
            (TokenClass.DELIM_CLOSE_BRACE, r"\}"),
            (TokenClass.DELIM_DOT, r"\."),
            (TokenClass.DELIM_COMMA, r","),
            (TokenClass.DELIM_SEMICOLON, r";"),
            (TokenClass.CONST_NUMBER, r"\d+(\.\d+)?"),
            (TokenClass.CONST_STRING, r"\".*?\""),
            (TokenClass.IDENTIFIER, r"[a-zA-Z_]\w*"),
        ]

        token_regex = "|".join("(?P<{}>{})".format(t.name, p) for t, p in token_specification)
        tokens = []
        for line in self.text.split("\n"):
            line = line.strip()
            if line.startswith("//"):
                continue
            for match in re.finditer(token_regex, line):
                token_class = TokenClass[match.lastgroup]
                value = match.group()
                tokens.append(Token(token_class, value))
                lista_de_token.append(value)           

        tokens.append(Token(TokenClass.END_OF_FILE, ""))
        return tokens



class SyntaxAnalyzer:
    def __init__(self, lexer):
        self.lexer = lexer
        self.peek_token = None

    def program(self):
        logging.info("<< start program()")

        self.current_token = self.lexer[0]
        self.declaration()


        current_token_index = self.lexer.index(self.current_token)
        index = current_token_index

        while index < len(self.lexer):
            if self.current_token.token_class == TokenClass.END_OF_FILE:
                break
            else:
                self.declaration()
                index += 1

        logging.info("end program() >>\n")

        
    def declaration(self):
        logging.info("<< start declaration()")

        if self.current_token is None:
            return  # Final do arquivo, retorna sem fazer mais verificações

        if self.current_token.token_class == TokenClass.FUN:
            self.funDecl()
        elif self.current_token.token_class == TokenClass.VAR:
            self.varDecl()
        else:
            self.statement()
        logging.info("end declaration() >>\n")


    def funDecl(self):
        logging.info("<< start funDecl()")
        self.validate_class(TokenClass.FUN)
        self.function()
        logging.info("end funDecl() >>\n")

    def varDecl(self):
        logging.info("<< start varDecl()")
        self.validate_class(TokenClass.VAR)
        self.validate_class(TokenClass.IDENTIFIER)
        if self.test_class(TokenClass.OPERATOR_ASSIGN):
            self.validate_class(TokenClass.OPERATOR_ASSIGN)
            self.expression()
        self.validate_class(TokenClass.DELIM_SEMICOLON)
        logging.info("end varDecl() >>\n")

    def statement(self):
        logging.info("<< start statement()")
        if self.test_class(TokenClass.FOR):
            self.forStmt()
        elif self.test_class(TokenClass.IF):
            self.ifStmt()
        elif self.test_class(TokenClass.PRINT):
            self.printStmt()
        elif self.test_class(TokenClass.RETURN):
            self.returnStmt()
        elif self.test_class(TokenClass.WHILE):
            self.whileStmt()
        elif self.test_class(TokenClass.DELIM_OPEN_BRACE):
            self.block()
        else:
            self.expr_stmt()
        logging.info("end statement() >>\n")

    def expr_stmt(self):
        logging.info("<< start expr_stmt()")
        self.expression()
        self.validate_class(TokenClass.DELIM_SEMICOLON)
        logging.info("expr_stmt() >>\n")

    def forStmt(self):
        logging.info("<< start forStmt()")
        self.validate_class(TokenClass.FOR)
        self.validate_class(TokenClass.DELIM_OPEN_PAREN)

        if self.test_class(TokenClass.VAR):
            self.varDecl()
        elif not self.test_class(TokenClass.DELIM_SEMICOLON):
            self.expr_stmt()

        self.validate_class(TokenClass.DELIM_SEMICOLON)
        if not self.test_class(TokenClass.DELIM_SEMICOLON):
            self.expression()

        self.validate_class(TokenClass.DELIM_SEMICOLON)
        if not self.test_class(TokenClass.DELIM_CLOSE_PAREN):
            self.expression()

        self.validate_class(TokenClass.DELIM_CLOSE_PAREN)
        self.statement()

        logging.info("end forStmt() >>")

    def ifStmt(self):
        logging.info("<< start ifStmt()")
        self.validate_class(TokenClass.IF)
        self.validate_class(TokenClass.DELIM_OPEN_PAREN)
        self.expression()
        self.validate_class(TokenClass.DELIM_CLOSE_PAREN)
        self.statement()
        if self.test_class(TokenClass.ELSE):
            self.validate_class(TokenClass.ELSE)
            self.statement()
        logging.info("end ifStmt()>>\n")

    def printStmt(self):
        logging.info("<< start printStmt()")
        self.validate_class(TokenClass.PRINT)
        self.expression()
        self.validate_class(TokenClass.DELIM_SEMICOLON)
        logging.info("end printStmt() >>\n")


    def returnStmt(self):
        logging.info("<< start returnStmt()")
        self.validate_class(TokenClass.RETURN)
        if self.current_token != TokenClass.DELIM_SEMICOLON:
            self.expression()
        self.validate_class(TokenClass.DELIM_SEMICOLON)
        logging.info("end returnStmt() >>\n")


    def whileStmt(self):
        logging.info("<< start whileStmt()")
        self.validate_class(TokenClass.WHILE)
        self.validate_class(TokenClass.DELIM_OPEN_PAREN)
        self.expression()
        
        if self.test_class(TokenClass.DELIM_CLOSE_PAREN):
            self.validate_class(TokenClass.DELIM_CLOSE_PAREN)
            self.statement()
        else:
            logging.error("Expected ')' after expression in while statement")

        logging.info("end whileStmt() >>\n")

    def block(self):
        logging.info("<< start block()")
        self.validate_class(TokenClass.DELIM_OPEN_BRACE)
        while not self.test_class(TokenClass.DELIM_CLOSE_BRACE):
            self.declaration()
        self.validate_class(TokenClass.DELIM_CLOSE_BRACE)
        logging.info("end block() >>\n")

    def expression(self):
        logging.info("<< start expression()")
        self.assignment()
        logging.info("end expression() >>\n")

    def assignment(self):
        logging.info("<< start assignment()")

        if self.test_class(TokenClass.DELIM_OPEN_PAREN):
            self.call()
            if self.test_class(TokenClass.DELIM_DOT):
                self.validate_class(TokenClass.DELIM_DOT)

                if self.test_class(TokenClass.IDENTIFIER):
                    self.validate_class(TokenClass.IDENTIFIER)
        else:
            self.logic_or()

        if self.test_class(TokenClass.OPERATOR_ASSIGN):
            self.validate_class(TokenClass.OPERATOR_ASSIGN)
            self.assignment()

        logging.info("end assignment() >>\n")

    def logic_or(self):
        logging.info("<< start logic_or()")
        self.logic_and()
        while self.current_token.token_class == TokenClass.LOGIC_OR:
            self.validate_class(TokenClass.LOGIC_OR)
            self.logic_and()
        logging.info("end logic_or() >>\n")

    def logic_and(self):
        logging.info("<< start logic_and()")
        self.equality()
        while self.current_token.token_class == TokenClass.LOGIC_AND:
            self.validate_class(TokenClass.LOGIC_AND)
            self.equality()
        logging.info("end logic_and() >>\n")

    def equality(self):
        logging.info("<< start equality()")
        self.comparison()
        while self.test_class(TokenClass.OPERATOR_NOT_EQUAL, TokenClass.OPERATOR_EQUAL):
            self.comparison()
        logging.info("end equality() >>\n")
        
    def comparison(self):
        logging.info("<< start comparison()")
        self.term()
        while self.test_class(TokenClass.OPERATOR_GT, TokenClass.OPERATOR_GTE, TokenClass.OPERATOR_LT, TokenClass.OPERATOR_LTE):
            self.validate_class(TokenClass.OPERATOR_GT, TokenClass.OPERATOR_GTE, TokenClass.OPERATOR_LT, TokenClass.OPERATOR_LTE)
            self.term()
        logging.info("end comparison() >>\n")

    def term(self):
        logging.info("<< start term()")
        self.factor()
        while self.test_class(TokenClass.OPERATOR_ADD, TokenClass.OPERATOR_SUB):
            self.validate_class(TokenClass.OPERATOR_ADD, TokenClass.OPERATOR_SUB)
            self.factor()
        logging.info("end term() >>\n")

    def factor(self):
        logging.info("<< start factor()")
        self.unary()
        while self.test_class(TokenClass.OPERATOR_DIV, TokenClass.OPERATOR_MUL):
            self.validate_class(TokenClass.OPERATOR_DIV, TokenClass.OPERATOR_MUL)
            self.unary()
        logging.info("end factor() >>\n")

    def unary(self):
        logging.info("<< start unary()")
        if self.test_class(TokenClass.OPERATOR_NOT, TokenClass.OPERATOR_SUB):
            self.validate_class(TokenClass.OPERATOR_NOT, TokenClass.OPERATOR_SUB)
            self.unary()
        else:
            self.call()
        logging.info("end unary() >>\n")

    def call(self):
        logging.info("<< start call()")
        self.primary()

        while True:
            if self.test_class(TokenClass.DELIM_OPEN_PAREN):
                self.validate_class(TokenClass.DELIM_OPEN_PAREN)
                self.arguments()
                self.validate_class(TokenClass.DELIM_CLOSE_PAREN)
            elif self.test_class(TokenClass.DELIM_DOT):
                self.validate_class(TokenClass.DELIM_DOT)
                self.validate_class(TokenClass.IDENTIFIER)
            else:
                break

        logging.info("end call() >>\n")



    def primary(self):
        logging.info("<< start primary()")
        
        if self.test_class(TokenClass.CONST_TRUE):
            self.validate_class(TokenClass.CONST_TRUE)
            pass
        elif self.test_class(TokenClass.CONST_FALSE):
            self.validate_class(TokenClass.CONST_FALSE)
            pass
        elif self.test_class(TokenClass.CONST_NIL):
            self.validate_class(TokenClass.CONST_NIL)
            pass
        elif self.test_class(TokenClass.THIS):
            self.validate_class(TokenClass.THIS)
            pass
        elif self.test_class(TokenClass.CONST_NUMBER):
             self.validate_class(TokenClass.CONST_NUMBER)
             pass
        elif self.test_class(TokenClass.CONST_STRING):
            self.validate_class(TokenClass.CONST_STRING)
            pass
        elif self.test_class(TokenClass.IDENTIFIER):
            self.validate_class(TokenClass.IDENTIFIER)
            pass
        elif self.test_class(TokenClass.DELIM_OPEN_PAREN):
            self.validate_class(TokenClass.DELIM_OPEN_PAREN)
            self.expression()
            self.validate_class(TokenClass.DELIM_CLOSE_PAREN)
        elif self.test_class(TokenClass.SUPER):
            self.validate_class(TokenClass.SUPER)
            self.validate_class(TokenClass.DELIM_DOT)
            self.validate_class(TokenClass.IDENTIFIER)
        else:
            raise SyntaxError("Unexpected token. Expected primary expression.")
        
        logging.info("end primary() >>\n")


    def function(self):
        logging.info("<< start function()")
        self.validate_class(TokenClass.IDENTIFIER)
        self.validate_class(TokenClass.DELIM_OPEN_PAREN)
        parameters = self.parameters() if self.test_class(TokenClass.IDENTIFIER) else []
        self.validate_class(TokenClass.DELIM_CLOSE_PAREN)
        self.block() 
        logging.info("end function() >>\n")


    def parameters(self):
        logging.info("<< start parameters()")
        parameters = []
        if self.test_class(TokenClass.IDENTIFIER):
            parameters.append(self.validate_class(TokenClass.IDENTIFIER))
            while self.test_class(TokenClass.DELIM_COMMA):
                self.validate_class(TokenClass.DELIM_COMMA)
                parameter = self.validate_class(TokenClass.IDENTIFIER)
                parameters.append(parameter)
        else:
            logging.info("No parameters found")
        logging.info("end parameters() >>\n")
        return parameters




    def arguments(self):
        logging.info("<< start arguments() >>\n")
        self.expression()
        while self.test_class(TokenClass.DELIM_COMMA):
            self.validate_class(TokenClass.DELIM_COMMA)
            self.expression()
        logging.info("end arguments() >>\n")

    def test_class(self, *classes_token):
        classes_string = ", ".join(str(cls) for cls in classes_token)
        logging.info("Testing classes {} => {}".format(classes_string, self.current_token))

        if self.current_token is None:
            return False

        result = self.current_token.token_class in classes_token

        if result:
            index = self.lexer.index(self.current_token)
            if index + 1 < len(self.lexer):
                self.current_token = self.lexer[index]
                return result
            else:
                self.current_token = None
        
    def validate_class(self, *classes_token):
        classes_string = ", ".join(str(cls) for cls in classes_token)
        logging.info("Validating classes {} => {}".format(classes_string, self.current_token))

        if self.current_token is None:
            raise SyntaxError("Unexpected end of input.")

        if self.current_token.token_class in classes_token:
            current_token_index = self.lexer.index(self.current_token)
            next_token_index = current_token_index + 1
            self.current_token = self.lexer[next_token_index] if next_token_index < len(self.lexer) else None
            print("\nToken: ", self.current_token, "\n")
            token = self.current_token
            return token
        else:
            raise SyntaxError("Unexpected token '{}'. Expected one of: {}".format(self.current_token, classes_string))


#TRADUTOR-----------------------------------------
lista_de_token=[]
aux = 0
identacao = ""
traducao = ""
cabeca = []

def check():
    
    global lista_de_token, aux
    
    if lista_de_token[aux] == 'print':
        cabeca.append(lista_de_token[aux])
    elif lista_de_token[aux] == 'var':
        cabeca.append(lista_de_token[aux])
    elif lista_de_token[aux] == 'while':
        cabeca.append(lista_de_token[aux])
    elif lista_de_token[aux] == 'fun':
        cabeca.append(lista_de_token[aux])
    elif lista_de_token[aux] == 'if' or lista_de_token[aux] == 'else':
        cabeca.append(lista_de_token[aux])
    elif not cabeca:
        cabeca.append(lista_de_token[aux])

def tradutor():
    
    global lista_de_token, aux, traducao, cabeca
    
    if aux >= len(lista_de_token):
        return 0
    
    check()
        
    if cabeca[-1]=='print':
        escrever_print()
    elif cabeca[-1]=='var':
        escrever_var()
    elif cabeca[-1]=='while':
        escrever_while()
    elif cabeca[-1]=='fun':
        escrever_fun()
    elif cabeca[-1]=='if' or cabeca[-1]=='else':
        escrever_ifelse()
    else:
        escrever_programa()

def escrever_ifelse():
        global aux, identacao, traducao
        if lista_de_token[aux] == "if":
            traducao = traducao + identacao + lista_de_token[aux] + " "
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == "else":
            if lista_de_token[aux+1] == "if":
                traducao = traducao + identacao + 'elif' + " "
                aux = aux + 2
                tradutor()
            else:
                traducao = traducao + identacao + lista_de_token[aux]
                aux = aux + 1
                tradutor() 
        elif lista_de_token[aux] == "}":
            traducao = traducao + "\n"
            identacao = identacao[: -1]
            cabeca.pop()
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == "{":
            traducao = traducao + ":" + "\n"
            identacao = identacao + " "
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == "(":
            traducao = traducao + "("
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == ")":
            traducao = traducao + ")"
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == ";":
            traducao = traducao + "\n"
            aux = aux + 1
            tradutor()
        else:
            escrever_programa()

def escrever_fun():
        global aux, identacao, traducao
        if lista_de_token[aux] == "}":
            traducao = traducao + "\n"
            identacao = identacao[: -1]
            cabeca.pop()
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == "{":
            traducao = traducao + ":" + "\n"
            identacao = identacao + " "
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == "(":
            traducao = traducao + "("
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == ")":
            traducao = traducao + ")"
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == ";":
            traducao = traducao + "\n"
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == "fun":
            traducao = traducao + "def "
            aux = aux + 1
            tradutor()
        else:
            escrever_programa()

def escrever_while():
        global aux, identacao, traducao
        if lista_de_token[aux] == "}":
            traducao = traducao + "\n"
            identacao = identacao[: -1]
            cabeca.pop()
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == "{":
            traducao = traducao + ":" + "\n"
            identacao = identacao + " "
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == "(":
            traducao = traducao + " "
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == ")":
            traducao = traducao + ""
            aux = aux + 1
            tradutor()
        elif lista_de_token[aux] == ";":
            traducao = traducao + "\n"
            aux = aux + 1
            tradutor()
        else:
            escrever_programa()

def escrever_var():
    global aux, traducao, identacao
    if lista_de_token[aux] == ";":
        traducao = traducao + "\n"
        cabeca.pop()
        aux = aux + 1
        tradutor()
    elif lista_de_token[aux] == "var":
        traducao = traducao + identacao + ""
        aux = aux + 1
        tradutor()
    else:
        escrever_programa()
    
def escrever_print():
    global aux, traducao
    if lista_de_token[aux] == ";":
        traducao = traducao + ")\n"
        cabeca.pop()
        aux = aux + 1
        tradutor()
    elif lista_de_token[aux] == "print":
        traducao = traducao + identacao + lista_de_token[aux] + "("
        aux = aux + 1
        escrever_programa()
    else:
        escrever_programa()

def escrever_programa():
    global aux, traducao, lista_de_token

    if lista_de_token[aux] == "}":
        print(f"--- SemanticError: Unexpected token '{lista_de_token[aux]}'. ---")
        sys.exit()
    elif lista_de_token[aux] == "{":
        print(f"--- SemanticError: Unexpected token '{lista_de_token[aux]}'. ---")
        sys.exit()
    elif lista_de_token[aux] == "(":
        traducao = traducao + "("
        aux = aux + 1
        tradutor()
    elif lista_de_token[aux] == ")":
        traducao = traducao + ")"
        aux = aux + 1
        tradutor()
    elif lista_de_token[aux] == ";":
        traducao = traducao + "\n"
        aux = aux + 1
        tradutor()
    elif lista_de_token[aux] == "!":
        traducao = traducao + "not "
        aux = aux + 1
        tradutor()
    elif lista_de_token[aux] == "and":
        traducao = traducao + " and "
        aux = aux + 1
        tradutor()
    elif lista_de_token[aux] == "or":
        traducao = traducao + " or "
        aux = aux + 1
        tradutor()
    elif lista_de_token[aux] == "true":
        traducao = traducao + "True"
        aux = aux + 1
        tradutor()
    elif lista_de_token[aux] == "false":
        traducao = traducao + "False"
        aux = aux + 1
        tradutor()
    elif lista_de_token[aux] == "nil":
        traducao = traducao + "None"
        aux = aux + 1
        tradutor()
    else:
        traducao = traducao + identacao + lista_de_token[aux]
        aux = aux + 1
        tradutor()
  

def main():
    logging.basicConfig(level=logging.INFO)

    text =  """ 
// Programa de exemplo 4
var x = true;
var y = 100;

if(10 > y or x) {
  print "1";
} else {
  if(10 < y and !x) {
    print "2";
  } else {
    print "3";
  }
}
"""

    lexer = Lexer(text)
    tokens = lexer.tokens
    syntax_analyzer = SyntaxAnalyzer(tokens)
    syntax_analyzer.program()
    print('============CÓDIGO EM PYTHON============\n')
    tradutor()
    print(traducao)
    print('============EXECUTANDO CÓDIGO EM PYTHON============\n')
    exec(traducao)

if __name__ == "__main__":
    main()