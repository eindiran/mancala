#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# mancala.py
# Modified: Tue 26 Dec 2017

import random
import sys
from time import sleep

__description__ = "Play mancala in the terminal."
__version__ = "1.0.0"
__author__ = "Elliott Indiran <eindiran@uchicago.edu>"


class MoveError(Exception):
    """Raise this error when a bucket has no beads to move."""
    pass


class BeadCountError(Exception):
    """Raise this error when a count of beads is not a positive int."""
    pass


class MancalaBucket():
    """Mancala game board bucket: 6 per side + scoring buckets."""
    def __init__(self, number, is_scoring, player):
        """Initialize a MancalaBucket object."""
        self.number = number
        self.scoring = is_scoring
        self.next_bucket = None
        self.num_beads = 0
        self.owner = player

    def __repr__(self):
        """Define how a MancalaBucket is represented internally or by print()."""
        output_str = "Bucket number: {}\n".format(self.number)
        output_str += "Beads: {}\n".format(self.num_beads)
        output_str += "Scoring: {}\n".format(self.scoring)
        output_str += "Owner: {}\n".format(self.owner)
        return output_str

    def __str__(self):
        """Define how to turn a MancalaBucket object into a string."""
        output_str = "Bucket number: {}\n".format(self.number)
        output_str += "Beads: {}\n".format(self.num_beads)
        output_str += "Scoring: {}\n".format(self.scoring)
        output_str += "Owner: {}\n".format(self.owner)
        return output_str

    def __cmp__(self, other):
        """Define how to compare two MancalaBucket objects."""
        if self.num_beads < other.num_beads:
            return -1
        elif self.num_beads > other.num_beads:
            return 1
        else:
            return 0

    def set_next_bucket(self, next_bucket):
        """Set the bucket that follows current bucket."""
        self.next_bucket = next_bucket

    def get_beads(self):
        """Fetch the beads out of this bucket."""
        if self.scoring:
            raise MoveError("Can't remove beads from a scoring bucket.")
        beads = self.num_beads
        self.num_beads = 0
        return beads

    def add_beads(self, n):
        """Adds n bead to the mancala bucket object."""
        if type(n) is not int:
            raise BeadCountError("The number of beads must be a positive integer or zero.")
        if n < 0:
            raise BeadCountError("The number of beads must be a positive integer or zero.")
        self.num_beads += n

    def add_bead(self):
        """Add a bead to the mancala bucket object."""
        self.add_beads(1)


class MancalaBoard():
    """Mancala game board object."""
    def __init__(self, starting_beads):
        """Initialize the board and make all required MancalaBucket objects."""
        self.buckets = []
        self.opposite_map = {}
        self.p1_scoring_bucket = None
        self.p2_scoring_bucket = None
        # player one non-scoring buckets
        for i in range(6):
            bucket = MancalaBucket(i, False, 1)
            bucket.add_beads(starting_beads)  # Populate with initial beads
            if (i != 0):
                self.buckets[i-1].set_next_bucket(bucket)
            self.buckets.append(bucket)
        scoring_bucket_p1 = MancalaBucket(-1, True, 1)
        self.buckets[-1].set_next_bucket(scoring_bucket_p1)
        self.p1_scoring_bucket = scoring_bucket_p1
        # player 2 non-scoring buckets
        for i in range(6, 12):
            bucket = MancalaBucket(i, False, 2)
            bucket.add_beads(starting_beads)
            self.buckets[-1].set_next_bucket(bucket)
            self.buckets.append(bucket)
        scoring_bucket_p2 = MancalaBucket(-2, True, 2)
        self.buckets[-1].set_next_bucket(scoring_bucket_p2)
        scoring_bucket_p2.set_next_bucket(self.buckets[0])
        self.p2_scoring_bucket = scoring_bucket_p2
        # Now set up the opposites_map
        non_scoring_buckets = [bucket for bucket in self.buckets if not bucket.scoring]
        for bucket in non_scoring_buckets:
            self.opposite_map[bucket.number] = non_scoring_buckets[11 - bucket.number]

    def move(self, bucket_index, player):
        """Performs a single move."""
        bucket = self.buckets[bucket_index]
        beads = bucket.get_beads()
        if not beads:
            raise MoveError
        while beads:
            bucket = bucket.next_bucket
            if bucket.scoring and bucket.owner == player:
                continue
            bucket.add_bead()
            beads -= 1
        # Perform take -- Only do take if last bead placed in an empty bucket
        if bucket.owner == player and bucket.num_beads == 1:
            opposite = self.opposite_map[bucket.number]
            if opposite.num_beads:
                if player == 1:
                    self.p1_scoring_bucket.add_beads(opposite.get_beads())
                if player == 2:
                    self.p2_scoring_bucket.add_beads(opposite.get_beads())

    def get_opposite(self, bucket_index):
        """Get the bucket opposite of a particular index."""
        return self.opposites_map[bucket_index]

    def check_victory(self):
        beads_p1 = sum([bucket.num_beads for bucket in self.buckets
                        if bucket.owner == 1 and not bucket.scoring])
        beads_p2 = sum([bucket.num_beads for bucket in self.buckets
                        if bucket.owner == 2 and not bucket.scoring])
        return beads_p1 == 0 or beads_p2 == 0

    def player_ahead(self):
        """Returns 1 if P1 in lead, 2 if P2 or 0 if it is tied."""
        if self.p1_scoring_bucket.num_beads > self.p2_scoring_bucket.num_beads:
            return 1
        elif self.p2_scoring_bucket.num_beads > self.p1_scoring_bucket.num_beads:
            return 2
        else:
            return 0


def print_bucket(bucket, endl=''):
    """Display a bucket onscreen."""
    print("[{}]".format(bucket.num_beads), end=endl)


def display_mancala_board(mancala_board):
    """Used to print the board state."""
    p1_buckets = [bucket for bucket in mancala_board.buckets
                  if bucket.owner is 1 and not bucket.scoring]
    p2_buckets = [bucket for bucket in mancala_board.buckets
                  if bucket.owner is 2 and not bucket.scoring]
    print("-------", end=' ')
    for bucket in p1_buckets:
        print_bucket(bucket, ' ')
    print("-------")
    print("[[ {} ]]".format(mancala_board.p1_scoring_bucket.num_beads), end=' ')
    print("-----------------------", end=' ')
    print("[[ {} ]]".format(mancala_board.p2_scoring_bucket.num_beads))
    print("-------", end=' ')
    for bucket in p2_buckets[::-1]:
        print_bucket(bucket, ' ')
    print("-------")


def handle_victory(mancala_board):
    """Handle a victory."""
    winner = mancala_board.player_ahead()
    if winner is 1:
        print("Player 1 wins!")
    elif winner is 2:
        print("Player 2 wins!")
    else:
        print("Tie game!")
    sys.exit(0)


def find_best_move(mancala_board, difficulty='easy'):
    """Used by the computer to determine its move."""
    if difficulty == 'easy':
        return random.choice([7, 8, 9, 10, 11, 12])
    elif difficulty == 'medium':
        # TODO: Write this
        return random.choice([7, 8, 9, 10, 11, 12])
    else:  # difficulty == 'hard'
        # TODO: Write this
        return random.choice([7, 8, 9, 10, 11, 12])


def validate_move(move):
    """
    Takes user input and validates it, returning the result if valid.
    """
    try:
        move = int(move)
        assert move in [1, 2, 3, 4, 5, 6]
    except (ValueError, AssertionError):
        raise ValueError("Choose a value in [1-6]. Please try again.")
    return move


def simulate_thinking(wait_len=6):
    """
    Pretend the computer is thinking. Default is 3 seconds. wait_len in half seconds.
    """
    for i in range(wait_len):
        sleep(0.5)
        print('.', end='')
        sys.stdout.flush()
    print('\n')


def two_player_game():
    """
    Run a two-player game, where each player is a human.
    """
    mancala_board = MancalaBoard(4)
    turn = 1
    display_mancala_board(mancala_board)
    while True:
        if mancala_board.check_victory():
            handle_victory(mancala_board)
        if turn is 1:
            print("[Player One] - ", end='')
        if turn is 2:
            print("[Player Two] - ", end='')
        move = input("Choose which bucket to move:\n\n> ")
        try:
            move = validate_move(move)
            if turn is 1:
                mancala_board.move(move-1, turn)
                turn = 2
            else:
                move = 7 - move  # Reverse the order of the buckets so its easier to use
                mancala_board.move((move+5), turn)
                turn = 1
        except ValueError:
            continue
        except MoveError:
            print("Please move a bucket with beads in it.")
            continue
        display_mancala_board(mancala_board)


def single_player_game(difficulty):
    """
    Run a single player game, w/ the opponent managed by the computer.
    """
    mancala_board = MancalaBoard(4)
    display_mancala_board(mancala_board)
    while True:
        if mancala_board.check_victory():
            handle_victory(mancala_board)
        print("[Player One] - ", end='')
        move = input("Choose which bucket to move:\n\n> ")
        try:
            move = validate_move(move)
            mancala_board.move(move-1, 1)
        except ValueError:  # raised by validate_move()
            continue
        except MoveError:
            print("Please move a bucket with beads in it.")
            continue
        display_mancala_board(mancala_board)
        print("\n[Player Two] - Moving.", end='')
        sys.stdout.flush()
        simulate_thinking(6)
        not_moved = True
        while not_moved:
            move = find_best_move(mancala_board, difficulty)
            try:
                mancala_board.move(move-1, 2)
                not_moved = False
            except MoveError:
                continue
        display_mancala_board(mancala_board)


def main():
    """
    Main function which chooses whether a single player or two
    player game is played.
    """
    print("\nMANCALA\n\n")
    while True:
        players = input("Choose number of players: [1 or 2]\n\n> ")
        try:
            players = int(players)
            assert players in [1, 2]
            if players is 1:
                difficulty = input("\nChoose difficulty: [easy, medium, or hard]\n\n> ")
                assert difficulty.lower() in ['easy', 'medium', 'hard']
                print('\n')
                single_player_game(difficulty.lower())
            else:
                two_player_game()
        except (AssertionError, ValueError):
            print("Bad input.")
            continue


if __name__ == "__main__":
    main()
