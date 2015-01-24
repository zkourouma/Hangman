# from django.db import models

# Create your models here.
import fileinput
# import string
from random import choice
# import operator


# class HangmanGame(models.Model):
class HangmanGame(object):
    """The gameplay engine"""
    def __init__(self):
        self.mode = self.select_mode()

        self.play_game(self.mode)

    def select_mode(self):
        try:
            print "Guess the computer's word (1), have the computer guess yours (2),"
            print "play against a friend (3), or have the computer play itself (4)"
            mode = int(raw_input())
            return mode
        except ValueError:
            print "Invalid input, must be an integer"
        self.select_mode()

    def play_game(self, mode):
        if mode == 1:
            player1 = HumanPlayer()
            player1.play(ComputerPlayer())
        elif mode == 2:
            player1 = ComputerPlayer()
            player1.play(HumanPlayer())
        elif mode == 3:
            player1 = HumanPlayer()
            player1.play(HumanPlayer())
        else:
            player1 = ComputerPlayer()
            player1.play(ComputerPlayer())
        return None


# class Player(models.Model):
class Player(object):
    """Basic type of game participant"""
    def __init__(self):
        self.won = False
        self.already_guessed = []
        self.word = ""
        self.word_length = 0

    class Meta:
        abstract = True

    def have_won(self):
        return self.won

    def win(self):
        self.won = True
        return self.won

    def word_length(self):
        return self.word_length

    def add_to_guessed(self, new_guess):
        if new_guess not in self.already_guessed:
            self.already_guessed += [new_guess]
        return None

    def guessed_list(self):
        return self.already_guessed

    def ending(self, opponent, word_shell):
        if self.have_won():
            print "\n\nCongratulations, you win!"
            print "The word was '%s'" % "".join(word_shell).rstrip()
        else:
            print "\n\nSorry, you lose!"
        if isinstance(opponent, ComputerPlayer):
            print "The word was '%s'" % "".join(opponent.say_word())

        return None


class HumanPlayer(Player):
    """Human participant"""
    def __init__(self):
        super(HumanPlayer, self).__init__()
        self.guesses = 8

    def play(self, opponent):
        opponent.choose_word()

        word_shell = ['_ '] * opponent.word_length

        print "The word is %d letters long." % opponent.word_length
        turn = 0
        while not self.have_won():
            if turn >= self.guesses:
                break

            print "Turns left: %d" % (self.guesses - turn)
            print "Secret word: %s" % "".join(word_shell).rstrip()

            new_guess = self.guess_letter()

            if not opponent.confirm_guess(word_shell, new_guess, opponent):
                turn += 1

            opponent.add_to_guessed(new_guess)

            if "_ " not in word_shell:
                self.win()

        self.ending(opponent, word_shell)

    def choose_word(self):
        try:
            self.word_length = int(raw_input("Enter number of letters: "))
            return None
        except ValueError:
            print "Invalid input, must be an integer"
            self.choose_word(self)

    def confirm_guess(self, word_shell, new_guess, opponent):
        if new_guess in opponent.guessed_list():
            print "You already guessed %s" % new_guess
            return True

        confirm = raw_input("Is '%s' in your word? (y/n): " % new_guess)
        if confirm.lower() == 'y':
            places = raw_input("Which places? (comma separated, starting at 1. e.g. '1,3,4': ")
            places = [int(i) for i in places.split(',')]
            for n in places:
                word_shell[n-1] = new_guess
            return True
        elif confirm.lower() == 'n':
            return False

    def guess_letter(self):
        letter = raw_input("Guess letter: ")
        if len(letter) != 1:
            letter = self.guess_letter()
        return letter.lower()


class ComputerPlayer(Player):
    """Computer participant using AI"""
    def __init__(self):
        super(ComputerPlayer, self).__init__()
        self.guesses = 7
        self.dictionary = self.load_words()

    def load_words(self):
        word_list = [line.rstrip() for line in fileinput.input("hangman/dictionary.txt")]

        return word_list

    def play(self, opponent):
        opponent.choose_word()

        word_shell = ['_ '] * opponent.word_length
        print "The word is %d letters long." % opponent.word_length
        turn = 0

        while not self.have_won():
            if turn > self.guesses:
                break

            print "Turns left: %d" % (self.guesses - turn)
            print "Secret word %s" % "".join(word_shell).rstrip()

            new_guess = self.best_guess(word_shell, opponent)

            if type(new_guess) == list:
                word_shell = new_guess[0]
                self.win()
                break

            opponent.add_to_guessed(new_guess)

            if not opponent.confirm_guess(word_shell, new_guess, self):
                turn += 1

        self.ending(opponent, word_shell)

    def choose_word(self):
        self.word = list(choice(self.dictionary))
        self.word_length = len(self.word)
        return None

    def say_word(self):
        return self.word

    def confirm_guess(self, word_shell, new_guess, opponent):
        if new_guess in opponent.guessed_list():
            print "You already guessed %s" % new_guess
            return True
        elif new_guess not in self.word:
            print "Sorry, '%s' is not in the word." % new_guess
            return False
        else:
            print "Good guess, '%s' is in the word." % new_guess
            for i in range(len(word_shell)):
                if self.word[i] == new_guess:
                    word_shell[i] = self.word[i]
            return True

    def best_guess(self, word_shell, opponent):
        potentials = self.potential_words(self.dictionary, word_shell, opponent)
        if len(potentials) == 1:
            return potentials

        occurances = {}
        for char in list("".join(potentials)):
            if char in opponent.guessed_list():
                continue
            occurances.setdefault(char, 0)
            occurances[char] += 1

        bestChar = ""
        bestTimes = 0
        for char, times in occurances.items():
            if times > bestTimes:
                bestChar = char
                bestTimes = times
        return bestChar

    def potential_words(self, total_words, word_shell, opponent):
        potential = [word for word in total_words
                     if len(word) == opponent.word_length]
        potential_list = [word for word in potential
                          if self.possible_word(word, word_shell)]
        return potential_list

    def possible_word(self, word, word_shell):
        for i, c in enumerate(list(word)):
            if not (word_shell[i] == "_ " or word_shell[i] == c):
                return False

        return True
