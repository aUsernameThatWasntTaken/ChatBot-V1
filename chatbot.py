#TODO:
# add pronouns
#
#
#
#
#

import string
import random
import functools

class thing:
    def __init__(self,name: str, adjectives: list[str],activeVerbs: dict[str,list[str]],passiveVerbs: dict[str,list[str]]):
        self.name: str = name
        self.adjectives: list[str] = adjectives
        self.activeVerbs: dict[str,list[str]] = activeVerbs
        self.passiveVerbs: dict[str,list[str]] = passiveVerbs

    def __str__(self):
        return f"{self.name}, it is {str(self.adjectives)}"

class person(thing):
    def __init__(self, name: str, adjectives: list[str], activeVerbs: dict[str,list[str]], passiveVerbs: dict[str,list[str]], DOB: int, DOD: int= None):
        super().__init__(name,adjectives,activeVerbs,passiveVerbs)
        self.DOB = DOB
        self.DOD = DOD

class sentence:
    def __init__(self,bot,text):
        self.words: list[str] = text.split()
        self.pastParticiple: str = ""
        self.verb: str = ""
        self.subject: str = ""
        self.object: str = ""
        if len(self.words) > 0:
            self.isQuestion: bool = self.words[0] in relativePronouns
            self.isAnswerable: bool = True
            self.isClosed: bool = self.words[0] in specialVerbs
            if self.isClosed:
                self.isQuestion = True
                self.analyseClosedQuestion()
            elif self.isQuestion:
                self.analyseOpenQuestion()
            else:
                self.isAnswerable = False
                self.analyseStatement()

    def analyseClosedQuestion(self):
        subject: bool = True
        for word in self.words:
            if word in specialVerbs:
                self.verb = word
            else:
                if word in adjectives or word in determiners or wordInVerbs(word):
                    subject = False
                if self.verb == "has" and wordInVerbs(word):
                    self.pastParticiple = word.removesuffix("d").removesuffix("e")+"ed"
                else:
                    if subject:
                        if self.subject == "":
                            self.subject = word
                        else:
                            self.subject += " "+word
                    else:
                        if self.object == "":
                            self.object = word
                        else:
                            self.object += " "+word
    def analyseOpenQuestion(self):                  #What did person verb?
        subject: bool = True
        for word in self.words:
            if word in relativePronouns:
                self.relativePronoun = word
                self.object = word
            elif word == "has":
                self.verb = "has"
            else:
                if word in adjectives or word in determiners or wordInVerbs(word):
                    subject = False
                if wordInVerbs(word):
                    self.pastParticiple = word.removesuffix("d").removesuffix("e")+"ed"
                else:
                    if self.subject == "":
                        self.subject = word
                    else:
                        self.subject += " "+word
    
    def analyseStatement(self):
        for word in self.words:
            if word in specialVerbs:
                self.verb = word
            else:
                if self.verb == "":
                    if self.subject == "":
                        self.subject = word
                    else:
                        self.subject += " "+word
                else:
                    if self.object == "":
                        self.object = word
                    else:
                        self.object += " "+word
    
    def __str__(self):
        return f"subject: {self.subject}, Verb: {self.verb}, object: {self.object}, past participle: {self.pastParticiple}"

def computerise(bot,text):
    for character in string.punctuation:
        text = text.replace(character,"")
    substitutions = {"ur":"self is","you":"self","are":"is","i ":"user ","am ":"is ","have":"has","did":"has"}
    text = text.lower()
    for original, substitution in substitutions.items():
        text = text.replace(original,substitution)
    if not bot.user.name == "":
        text = text.replace("user",user.name)
    return text

def decomputerise(bot,text):
    if not bot.user.name == "" and not text.startswith("I will remember that"):
        text = text.replace(user.name,"user")
    substitutions = {"self is":"I am","user is":"you are","self":"me","user has":"you have","user":"you"}
    for original, substitution in substitutions.items():
        text = text.replace(original,substitution)
    return text

def findInMemory(bot,name):
    for item in bot.memory:
        if item.name.lower() == name.lower():
            return item

def wordInVerbs(word):
    for verb in verbs:
        if (word.removesuffix("d").removesuffix("e")+"ed").lower() == verb.lower():
            return True
    return False

def greeting():
    return random.choice(greetings)

def ifNotQuestion(wordsList):
    global memory
    global user
    global adjectives
    if wordsList.subject == "user" and user.name == "":
        username = ""
        for word in wordsList.object.split():
            username += " " + word.capitalize()                                               #I really dislike American Spelling
        username = username.removeprefix(" ")
        if findInMemory(wordsList.object) == None:
            if askUser(f"I have never heard of {username}. Are you sure?"):
                user.name = username
                return f"I will remember that, {user.name.split()[0]}."
            return "Ok. Who are you then?"
        else:
            user = findInMemory(wordsList.object)
            return f"I will remember that, {user.name.split()[0]}."
    if wordsList.verb == "has":
        pass
    else:
        if findInMemory(wordsList.subject) == None:
            if askUser("I don't know who that is. Are you sure you spelled that right?"):
                memory.append(person(wordsList.subject,[],{},{},0))
            else:
                return "Can you repeat that please, but with the right name?"
        findInMemory(wordsList.subject).adjectives.append(wordsList.object)
        adjectives.append(wordsList.object)
        
    return "Ok."

def process(bot,text):
    global user
    if text in greetings:
        return greeting()+"."
    relevantAdjective: str = ""
    text = computerise(bot,text)
    wordsList = sentence(bot,text)
    if debug:
        print(str(wordsList))
    if wordsList.subject == "" or wordsList.object == "" or wordsList.verb == "":
        return random.choice(["What do you mean? I don't get it.","Could you say that a bit differently?","I don't understand.","That might not be a full sentence."])
    if not wordsList.isQuestion:
        return ifNotQuestion(wordsList)                                 #Trying to keep this enormity more concise.
    if not wordsList.isAnswerable:
        return "I don't know how to answer that sort of question"
    subjectData = findInMemory(bot,wordsList.subject)
    if subjectData == None:
        return f"I don't know who or what {wordsList.subject} is."
    #'What has x y'd?' type question:
    if not wordsList.isClosed:
        if not wordsList.pastParticiple == "":
            openQuAnswer: str = ""                                      #This will be used to store a string that looks like this: "a, b, c and d"
            *items, lastItem = subjectData.activeVerbs[wordsList.pastParticiple]
            if items == []:
                openQuAnswer = lastItem
            else:
                for item in items:
                    openQuAnswer += f"{item}, "
                openQuAnswer += f"and {lastItem}"
            return f"{wordsList.subject} {wordsList.verb} {wordsList.pastParticiple} {openQuAnswer}."
        else:
            return f"Who has {subjectData.name} what'ed?"
        if answer:
            return f"{subjectData.name} {wordsList.verb} {wordsList.pastParticiple} {openQuAnswer}."
        else:
            return f"No, {subjectData.name} {wordsList.verb} not {wordsList.object}."
    #'Has x y'd z' type question:
    if not wordsList.pastParticiple == "":
        answer = wordsList.object in subjectData.activeVerbs[wordsList.pastParticiple]
        wordsList.pastParticiple += " "
    #'Is x y' type question:
    else:
        answer = wordsList.object in adjectives and wordsList.object in subjectData.adjectives
    if answer:
        return f"Yes, {subjectData.name} {wordsList.verb} {wordsList.pastParticiple}{wordsList.object}."
    else:
        return f"No, {subjectData.name} {wordsList.verb} not {wordsList.object}."

def askUser(text,isTOrF = True):
    if isTOrF:
        print(" Bot: " + text)
        userReply = input("User: ").lower()
        if userReply.startswith("y"):
            return True
        elif userReply.startswith("n"):
            return False
        else:
            return askUser("I need a yes or no answer")
    else:
        return input("User: ").lower()
    

#Main Code Starts Here
debug: bool = False
class chatbot:
    def __init__(self,requestInput,output):
        self.shutDownPhrases = ["quit","shut up","go fuck yourself","great","yay"]
        self.requestInput = requestInput
        self.output = output
        self.user = person("",[],{},{},0)
        
        self.memory = [thing("self",["useful","sure"],{},{"created":["Max Byzdra"]}),person("Max Byzdra",["stupid"],{"created":["self"]},{},2010)]
        #person Blueprint: person("",[""],{"":[""]},{},0)
        #science knowledge:
        self.memory.append(person("Ernest Rutherford",[],{"created":[" the Nuclear Model of the Atom"]},{},1871))

    def run(self):
        while True:
            userInput: str = computerise(self,self.requestInput())
            if userInput in self.shutDownPhrases:
                self.output("Bye!")
                break
            if userInput == "":
                continue
            clauses = userInput.split(",")
            answer = ""
            for clause in clauses:
                answer += " " + decomputerise(self,process(self,clause))
            self.output(answer)

#random code testing Area


def init():
    global greetings
    greetings = ["hello","hi"]
    global specialVerbs
    specialVerbs = ["is","has"]
    global verbs
    verbs = ["created"]
    global adjectives
    adjectives = ["dead","useful","stupid","sure"]
    global determiners
    determiners = ["a","the"]
    global relativePronouns
    relativePronouns = ["who","what","when","where","why","how"]

init()
chat_bot = chatbot(functools.partial(input,"User: "),lambda output : print(" Bot:" + output))
chat_bot.run()
