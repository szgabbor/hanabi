#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from random import randint
import argparse

def main(argv = None):

    parser = argparse.ArgumentParser(description = 'Plays the hanabi game')
    parser.add_argument('iter', metavar = 'iter', type = int, nargs = '?', 
            default = 1, help = 'Ha meg van adva, akkor ennyiszer fog \
                    lefutni a program, és csak a végső pontszám lesz \
                    kiírva minden iterációban')

    args = parser.parse_args()
    iter = args.iter
    
    global log
    global log_without_newline

    if iter == 1 :
        def log(message) :
            print(message)
    else :
        def log(message) :
            pass


    if iter == 1 :
        def log_without_newline(message) :
            sys.stdout.write(message)
    else :
        def log_without_newline(message) :
            pass

    for _ in range(iter) :
        table = Table()
        players = []
        numPlayers = 5
        numCards = 4
        current = 0
        for _ in range(numPlayers):
            players.append(Player(numCards, table.getHand(numCards)))

        remainingMoves = numPlayers
        while remainingMoves > 0 :
            log('----------------------------------------------------------------------------------------')
            if table.remainingCards == 0:
                remainingMoves -= 1
            print_standing(table, players, numPlayers, current)
            players[current].move(table, players, numPlayers, current)
            current = (current + 1) % numPlayers

        print('végső pontszám: ' + str(table.getScore()))

class Card:
    color = 0
    number = 0
    def __init__(self, color, number):
        self.color = color
        self.number = number
    
    def toString(self):
        return str(self.color) + ',' + str(self.number) + " "
    
class Player:
    cards = []
    numCards = 0
    knownCards = 0
    def __init__(self, numberOfCards, cards):
        self.numCards = numberOfCards
        self.cards = cards
        self.knownCards = 0

    def help(self):
        if self.knownCards < self.numCards:
            self.knownCards += 1

    def move(self, table, players, numPlayers, current):

        if self.existsKnownPlayable(table) :
            log(str(current + 1) + ' lerakja: ' + self.cards[self.knownPlayable(table)].toString())
            self.playCard(table, self.knownPlayable(table))
            return

        if table.helps > 2 or (table.helps > 0 and (table.remainingCards < 3 or
                existNotKnownImportantCard(table, players, current, numPlayers))):
            log(str(current + 1) + ' segít')
            self.helpOthers(table, players, numPlayers, current)
            return

        if self.existsKnownThrowable(table) :
            log(str(current + 1) + ' eldobja: ' + self.cards[self.knownThrowable(table)].toString())
            self.throwKnownCard(table, self.knownThrowable(table))
            return


        if table.helps > 0:
            log(str(current + 1) + ' segít')
            self.helpOthers(table, players, numPlayers, current)
        else:
            log(str(current + 1) + ' dob')
            if self.existKnownNotNecessary(table) :
                log('nem fontosat: ' + self.cards[self.knownNotNecessary(table)].toString())
                self.throwKnownCard(table, self.knownNotNecessary(table))
                return
            if self.numCards - self.knownCards > 0:
                self.throwNotKnownCard(table)
            else:
                self.throwRandomKnownCard(table)

    def knownNotNecessary(self, table):
        for i in range(self.knownCards):
            if not table.isNecessary(self.cards[i]):
                return i
        return -1

    def existKnownNotNecessary(self, table):
        return self.knownNotNecessary(table) != -1
    
    def knownPlayable(self, table):
        result = -1
        min_num = 5
        for i in range(self.knownCards):
            if table.isPlayable(self.cards[i]) and self.cards[i].number < min_num:
                min_num = self.cards[i].number

        for i in range(self.knownCards):
            if table.isPlayable(self.cards[i]) and self.cards[i].number == min_num:
                if table.isNecessary(self.cards[i]):
                    return i
                else:
                    result = i

        return result

    def existsKnownPlayable(self, table):
        return self.knownPlayable(table) != -1

    def knownThrowable(self, table):
        for i in range(self.knownCards):
            if table.isThrowable(self.cards[i]):
                return i
        return -1

    def existsKnownThrowable(self, table):
        return self.knownThrowable(table) != -1

    def helpOthers(self, table, players, numPlayers, current):
        table.useHelp()
        for i in range(numPlayers): 
            if i != current : 
                players[i].help()

    def throwRandomKnownCard(self, table):
        num = -1
        toThrow = 0
        for i in range(self.knownCards):
            if self.cards[i].number > num :
                num = self.cards[i].number
                toThrow = i
        self.throwKnownCard(table, toThrow)

    def throwNotKnownCard(self, table):
        self.throwCard(table, randint(self.knownCards, self.numCards - 1))

    def throwKnownCard(self, table, num):
        self.throwCard(table, num)
        self.knownCards -= 1

    def playCard(self, table, num):
        table.playCard(self.cards[num])
        self.loseCard(table, num)
        self.knownCards -= 1

    def throwCard(self, table, num):
        table.throwCard(self.cards[num])
        self.loseCard(table, num)

    def loseCard(self, table, num):
        for i in range(num, self.numCards - 1):
            self.cards[i] = self.cards[i + 1]
        if table.remainingCards > 0:
            self.cards[self.numCards - 1] = table.getCard()
        else:
            self.numCards -= 1

class Table:
    standing = []
    helps = 0
    deck = []
    discarded = []
    remainingCards = 0

    def __init__(self):
        self.deck = []
        self.discarded = []
        self.remainingCards = 50
        for i in range(5):
            self.deck.append([])
            self.discarded.append([])
            for _ in range(5):
                self.deck[i].append(0)
                self.discarded[i].append(0)
        self.helps = 8
        self.standing = []
        for _ in range(5):
            self.standing.append(0)


    def getCard(self):
        if self.remainingCards == 0:
            log("Nem maradt lap a pakliban")
            sys.exit(255)

        self.remainingCards -= 1
        rand = randint(0, self.remainingCards)
        for i in range(5):
            for j in range(5):
                diff = cardNum(j) - self.deck[i][j]
                if rand < diff :
                    self.deck[i][j] += 1
                    return Card(i, j)
                else:
                    rand -= diff

    def getHand(self, numOfCards):
        result = []
        for _ in range(numOfCards):
            result.append(self.getCard())
        return result

    def throwCard(self, card):
        self.discarded[card.color][card.number] += 1
        self.helps += 1

    def useHelp(self) :
        if self.helps == 0 :
            log("Nem maradt segítség")
            sys.exit(255)
        self.helps -= 1

    def isPlayable(self, card):
        return self.standing[card.color] == card.number

    def isThrowable(self, card):
        return self.standing[card.color] > card.number

    def playCard(self, card):
        if self.isPlayable(card):
            self.standing[card.color] += 1
        else:
            log("Ez nem jött össze3")
            sys.exit(255)

    def isNecessary(self, card):
        return (self.standing[card.color] <= card.number and 
                self.discarded[card.color][card.number] == cardNum(card.number) - 1)

    def getScore(self):
        score = 0
        for i in range(5):
            score += self.standing[i]
        return score

def existNotKnownImportantCard(table, players, current, numPlayers):
    min = 5
    for j in range(5):
        if table.standing[j] < min:
            min = table.standing[j]

    minPlaces = set()

    for j in range(5):
        if table.standing[j] == min:
            minPlaces.add(j)

    for i in range(numPlayers):
        for j in range(players[i].knownCards):
            if players[i].cards[j].color in minPlaces:
                if players[i].cards[j].number == min:
                    if i == current:
                        return False
                    else:
                        minPlaces.remove( players[i].cards[j].color)

    for i in range(numPlayers):
        if  i != current: 
            for j in range(players[i].knownCards, players[i].numCards):
                if players[i].cards[j].color in minPlaces:
                    if players[i].cards[j].number == min:
                        return True
    return False

def existsKnownPlayableCard(table, players, numPlayers):
    for i in range(numPlayers) :
        for j in range(players[i].knownCards) :
            if table.isPlayable(players[i].cards[j]) :
                return True
    return False

def existsKnownThrowableCard(table, players, numPlayers):
    for i in range(numPlayers) :
        for j in range(players[i].knownCards) :
            if table.isThrowable(players[i].cards[j]) :
                return True
    return False

def print_standing(table, players, numPlayers, current):
    for i in range(numPlayers):
        for j in range(players[i].knownCards):
            log_without_newline(players[i].cards[j].toString())
        log_without_newline('    ')
        for j in range(players[i].knownCards, players[i].numCards):
            log_without_newline(players[i].cards[j].toString())
        log('')
    log('')
    for i in range(5):
        log_without_newline(str(i) + "," + str(table.standing[i]) + ' ')
    log('')
    log('megmaradó segítség: ' + str(table.helps))
    log('megmaradó lapok: ' + str(table.remainingCards))
    log('')

def cardNum(n):
    if n == 0:
        return 3
    if n == 4:
        return 1
    return 2

if __name__ == '__main__':
    sys.exit(main())
