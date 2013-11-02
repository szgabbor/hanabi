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
        deck = Deck()
        table = Table()
        players = []
        numPlayers = 5
        numCards = 4
        current = 0
        for _ in range(numPlayers):
            players.append(Player(numCards, deck.getHand(numCards)))

        remainingMoves = numPlayers
        while remainingMoves > 0 :
            log('----------------------------------------------------------------------------------------')
            if deck.remainingCards == 0:
                remainingMoves -= 1
            print_standing(deck, table, players, numPlayers, current)
            players[current].move(deck, table, players, numPlayers, current)
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
    
    def isNecessary(self, table, deck):
        return table.standing[self.color] <= self.number and deck.discarded[self.color][self.number] == cardNum(self.number) - 1

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

    def move(self, deck, table, players, numPlayers, current):

        if self.existsKnownPlayable(table, deck) :
            log(str(current + 1) + ' lerakja: ' + self.cards[self.knownPlayable(table, deck)].toString())
            self.playCard(deck, table, self.knownPlayable(table, deck))
            return

        if existNotKnownImportantCard(table, players, current, numPlayers):
            log(str(current + 1) + ' segít')
            self.helpOthers(table, players, numPlayers, current)
            return

        if table.helps > 2 or (table.helps > 0 and deck.remainingCards < 3):
            log(str(current + 1) + ' segít')
            self.helpOthers(table, players, numPlayers, current)
            return

        if self.existsKnownThrowable(table) :
            log(str(current + 1) + ' eldobja: ' + self.cards[self.knownThrowable(table)].toString())
            self.throwKnownCard(deck, table, self.knownThrowable(table))
            return


        if table.helps > 0:
            log(str(current + 1) + ' segít')
            self.helpOthers(table, players, numPlayers, current)
        else:
            log(str(current + 1) + ' dob')
            if self.existKnownNotNecessary(table, deck) :
                log('nem fontosat: ' + self.cards[self.knownNotNecessary(table, deck)].toString())
                self.throwKnownCard(deck, table, self.knownNotNecessary(table, deck))
                return
            if self.numCards - self.knownCards > 0:
                self.throwNotKnownCard(deck, table)
            else:
                self.throwRandomKnownCard(deck, table)

    def knownNotNecessary(self, table, deck):
        for i in range(self.knownCards):
            if not self.cards[i].isNecessary(table, deck):
                return i
        return -1

    def existKnownNotNecessary(self, table, deck):
        return self.knownNotNecessary(table, deck) != -1
    
    def knownPlayable(self, table, deck):
        result = -1
        min_num = 5
        for i in range(self.knownCards):
            if table.isPlayable(self.cards[i]) and self.cards[i].number < min_num:
                min_num = self.cards[i].number

        for i in range(self.knownCards):
            if table.isPlayable(self.cards[i]) and self.cards[i].number == min_num:
                if self.cards[i].isNecessary(table, deck):
                    return i
                else:
                    result = i

        return result

    def existsKnownPlayable(self, table, deck):
        return self.knownPlayable(table, deck) != -1

    def knownThrowable(self, table):
        for i in range(self.knownCards):
            if table.isThrowable(self.cards[i]):
                return i
        return -1

    def existsKnownThrowable(self, table):
        return self.knownThrowable(table) != -1

    def helpOthers(self, table, players, numPlayers, current):
        table.helps -= 1
        for i in range(numPlayers): 
            if i != current : 
                players[i].help()

    def throwRandomKnownCard(self, deck, table):
        num = -1
        toThrow = 0
        for i in range(self.knownCards):
            if self.cards[i].number > num :
                num = self.cards[i].number
                toThrow = i
        self.throwKnownCard(deck, table, toThrow)

    def throwNotKnownCard(self, deck, table):
        self.throwCard(deck, table, randint(self.knownCards, self.numCards - 1))

    def throwKnownCard(self, deck, table, num):
        self.throwCard(deck, table, num)
        self.knownCards -= 1

    def playCard(self, deck, table, num):
        table.playCard(self.cards[num])
        self.loseCard(deck, num)
        self.knownCards -= 1

    def throwCard(self, deck, table, num):
        table.helps += 1
        deck.throwCard(self.cards[num])
        self.loseCard(deck, num)

    def loseCard(self, deck, num):
        for i in range(num, self.numCards - 1):
            self.cards[i] = self.cards[i + 1]
        if deck.remainingCards > 0:
            self.cards[self.numCards - 1] = deck.getCard()
        else:
            self.numCards -= 1

class Deck:
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

    def getCard(self):
        if self.remainingCards == 0:
            log("Ez nem jött össze")
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


class Table:
    standing = []
    helps = 0
    def __init__(self):
        self.helps = 8
        self.standing = []
        for _ in range(5):
            self.standing.append(0)

    def isPlayable(self, card):
        return self.standing[card.color] == card.number

    def isThrowable(self, card):
        return self.standing[card.color] > card.number

    def playCard(self, card):
        if self.isPlayable(card):
            self.standing[card.color] += 1
        else:
            log("Ez nem jött össze")
            sys.exit(255)

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

def existsKnownPuttableCard(table, players):
    pass

def print_standing(deck, table, players, numPlayers, current):
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
    log('megmaradó lapok: ' + str(deck.remainingCards))
    log('')

def cardNum(n):
    if n == 0:
        return 3
    if n == 4:
        return 1
    return 2

if __name__ == '__main__':
    sys.exit(main())
