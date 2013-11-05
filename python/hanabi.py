#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
from random import randint

def main(argv = None):
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
        print('----------------------------------------------------------------------------------------')
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

        if self.existsKnownPlayable(table) :
            print(str(current + 1) + ' lerakja: ' + self.cards[self.knownPlayable(table)].toString())
            self.playCard(deck, table, self.knownPlayable(table))
            return

        if existNotKnownImportantCard(table, players, current, numPlayers):
            print(str(current + 1) + ' segít')
            self.helpOthers(table, players, numPlayers, current)
            return

        if table.helps > 2 or (table.helps > 0 and deck.remainingCards < 3):
            print(str(current + 1) + ' segít')
            self.helpOthers(table, players, numPlayers, current)
            return

        if self.existsKnownThrowable(table) :
            print(str(current + 1) + ' eldobja: ' + self.cards[self.knownThrowable(table)].toString())
            self.throwThrowableCard(deck, table, self.knownThrowable(table))
            return

        if table.helps > 0:
            print(str(current + 1) + ' segít')
            self.helpOthers(table, players, numPlayers, current)
        else:
            print(str(current + 1) + ' dob')
            if self.knownCards > 0:
                self.throwKnownCard(deck, table)
            else:
                self.throwNotKnownCard(deck, table)


    def knownPlayable(self, table):
        result = -1
        num = 5
        for i in range(self.knownCards):
            if table.isPlayable(self.cards[i]) and self.cards[i].number < num:
                result = i
                num = self.cards[i].number
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
        table.helps -= 1
        for i in range(numPlayers): 
            if i != current : 
                players[i].help()

    def throwKnownCard(self, deck, table):
        num = -1
        for i in range(self.knownCards):
            if self.cards[i].number != 4 and self.cards[i].number > num :
                num = self.cards[i].number
        if num == -1 :
            self.throwCard(deck, table, randint(0, self.knownCards - 1))
        else:
            self.throwCard(deck, table, num)
        self.knownCards -= 1

    def throwNotKnownCard(self, deck, table):
        self.throwCard(deck, table, randint(self.knownCards, self.numCards - 1))

    def throwThrowableCard(self, deck, table, num):
        self.throwCard(deck, table, num)
        self.knownCards -= 1

    def playCard(self, deck, table, num):
        table.playCard(self.cards[num])
        self.loseCard(deck, num)
        self.knownCards -= 1

    def throwCard(self, deck, table, num):
        table.helps += 1
        self.loseCard(deck, num)

    def loseCard(self, deck, num):
        for i in range(num, self.numCards - 1):
            self.cards[i] = self.cards[i + 1]
        self.cards[self.numCards - 1] = deck.getCard()

class Deck:
    deck = []
    remainingCards = 0
    def __init__(self):
        self.remainingCards = 50
        for i in range(5):
            self.deck.append([])
            for _ in range(5):
                self.deck[i].append(0)

    def getCard(self):
        if self.remainingCards == 0:
            return Card(0, 10)
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


class Table:
    standing = []
    helps = 0
    def __init__(self):
        self.helps = 8
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
            print("Ez nem jött össze")
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

def print_standing(deck, table, players, numPlayers, current):
    for i in range(numPlayers):
        for j in range(players[i].knownCards):
            sys.stdout.write(players[i].cards[j].toString())
        sys.stdout.write('    ')
        for j in range(players[i].knownCards, players[i].numCards):
            sys.stdout.write(players[i].cards[j].toString())
        sys.stdout.write('\n')
    print
    for i in range(5):
        sys.stdout.write(str(i) + "," + str(table.standing[i]) + ' ')
    print
    print 'megmaradó segítség: ' + str(table.helps)
    print 'megmaradó lapok: ' + str(deck.remainingCards)
    print

def cardNum(n):
    if n == 0:
        return 3
    if n == 4:
        return 1
    return 2

if __name__ == '__main__':
    sys.exit(main())
