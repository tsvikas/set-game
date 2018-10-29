import itertools
import random
from enum import Enum


class SetRules:
    def __init__(self, n, k, card_str_fn=str):
        self.n = n
        self.k = k
        self.card_str_fn = card_str_fn
        self.cards = self.create_cards()

    def create_cards(self):
        return list(itertools.product(range(self.k), repeat=self.n))

    @property
    def deck_size(self):
        return len(self.cards)

    def str_card(self, idx):
        return self.card_str_fn(self.cards[idx])

    def is_set(self, idxs):
        if len(idxs) != self.k:
            return False
        cards = [self.cards[idx] for idx in idxs]
        return all(
            (sum(card[dim] for card in cards) % self.k == 0) for dim in range(self.n)
        )

    def any_set(self, idxs):
        return any(self.is_set(comb) for comb in itertools.combinations(idxs, self.k))


BASIC_SET = SetRules(n=4, k=3, card_str_fn=str)


class SetGame:
    def __init__(self, rules: SetRules, min_board=12, rand_seed=None):
        self.rules = rules
        self.min_board = min_board
        # set deck
        random.seed(rand_seed)
        self.deck = list(range(rules.deck_size))
        random.shuffle(self.deck)
        # set board
        self.board = [None] * min_board

    def refill_board(self):
        change = any(idx is None for idx in self.board)
        self.board[self.min_board :] = [
            idx for idx in self.board[self.min_board :] if idx is not None
        ]
        self.board = [
            idx if idx is not None else self.deck.pop(0) for idx in self.board
        ]
        return change

    def add_card(self):
        self.board.append(self.deck.pop(0))

    def remove_cards(self, ixs):
        for ix in ixs:
            self.board[ix] = None

    def str_position(self, ix):
        idx = self.board[ix]
        return f'{ix:2}: {self.rules.str_card(idx)}'

    def print_board(self):
        for ix, _idx in enumerate(self.board):
            print(
                self.str_position(ix),
                end='\n' if ix % 3 == 2 or ix == len(self.board) - 1 else '\t',
            )
        print(f'deck: {len(self.deck)}')

    def print_deck(self):
        for i, idx in enumerate(self.deck):
            print(f'{i:2}: {self.rules.str_card(idx)}')

    def is_set(self, ixs):
        idxs = [self.board[ix] for ix in ixs]
        return self.rules.is_set(idxs)

    def has_set(self):
        return self.rules.any_set(self.board)

    def all_sets(self):
        ixs = range(len(self.board))
        return [
            '\t'.join(self.str_position(ix) for ix in comb)
            for comb in itertools.combinations(ixs, self.rules.k)
            if self.is_set(comb)
        ]


class Action(Enum):
    PRINT = 0
    HELP = 1
    COUNT = 2
    NO_SET = 3
    DEAL_ = 4
    END_ = 5
    SET = 6


ACTIONS_DICT = {
    'print': Action.PRINT,
    'help': Action.HELP,
    'count': Action.COUNT,
    'noset': Action.NO_SET,
    'deal!': Action.DEAL_,
    'end!': Action.END_,
    'set': Action.SET,
}


def input_action():
    action_s = input('action> ').lower().strip()
    return ACTIONS_DICT.get(action_s, action_s)


def main():
    game = SetGame(BASIC_SET)

    while True:
        change = game.refill_board()
        if change:
            game.print_board()
        act = input_action()
        if act is Action.PRINT:
            game.print_board()
        elif act is Action.HELP:
            for hint in game.all_sets():
                print(hint)
        elif act is Action.COUNT:
            print(len(game.all_sets()))
        elif act is Action.NO_SET:
            if not game.has_set():
                if game.deck:
                    game.add_card()
                else:
                    print('deck is empty, game ended :)')
                    break
            else:
                print('find the set first, or use deal! / end! to force')
        elif act is Action.DEAL_:
            if game.deck:
                game.add_card()
            else:
                print('deck is empty')
        elif act is Action.END_:
            print('game ended :)')
            break
        elif act is Action.SET:
            ixs_input = input('cards> ')
            try:
                ixs = [int(ix) for ix in ixs_input.split()]
            except ValueError:
                print('invalid cards input')
                continue
            try:
                if game.is_set(ixs):
                    game.remove_cards(ixs)
                else:
                    print('not a valid set')
            except IndexError:
                print('invalid cards choice')
                continue
        else:
            print(f'invalid action {act!r}')
            print(f'use: {list(ACTIONS_DICT.keys())}')


if __name__ == "__main__":
    main()
