import itertools
import random
from enum import Enum

import colors


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
        card = self.cards[idx] if idx else None
        return self.card_str_fn(card)

    def is_set(self, idxs):
        if len(idxs) != self.k:
            return False
        cards = [self.cards[idx] for idx in idxs]
        return all(
            (sum(card[dim] for card in cards) % self.k == 0) for dim in range(self.n)
        )

    def any_set(self, idxs):
        return any(self.is_set(comb) for comb in itertools.combinations(idxs, self.k))


class ProjectiveSet(SetRules):
    def __init__(self, n=3, card_str_fn=str):
        super(ProjectiveSet, self).__init__(n=n, k=3, card_str_fn=card_str_fn)

    def create_cards(self):
        return list(itertools.product(range(self.k + 1), repeat=self.n))

    def is_set(self, idxs):
        if len(idxs) != self.k:
            return False
        cards = [self.cards[idx] for idx in idxs]
        for dim in range(self.n):
            cards_dim = [card[dim] for card in cards]
            if 0 in cards_dim:
                # 0-0-0 or 0-x-x
                cards_dim.remove(0)
                if len(set(cards_dim)) > 1:
                    return False
            else:
                # 1-2-3
                if len(set(cards_dim)) != len(cards_dim):
                    return False
        return True


def str_card_43(card):
    max_len = 3
    if not card:
        return max_len * '\u3000'
    number = [1, 2, 3][card[0]]
    color = ['red', 'green', 'magenta'][card[2]]
    shape_shading = [
        ['\u25cf', '\u25cd', '\u25cb'],
        ['\u25b2', '\u25ec', '\u25b3'],
        ['\u25a0', '\u25a5', '\u25a1'],
    ][card[3]][card[1]]
    symbols = shape_shading * number
    return colors.color(symbols, fg=color) + '\u3000' * (max_len - number)


def str_card_34(card):
    max_len = 3
    if not card:
        return max_len * '\u3000'
    number = [5, 1, 2, 3][card[0]]
    color = ['white', 'red', 'green', 'magenta'][card[2]]
    shape_shading = ['\u25c8', '\u25cf', '\u25b2', '\u25a0', 0][card[1]]
    symbols = shape_shading * number
    return colors.color(symbols, fg=color) + '\u3000' * (max_len - number)


def str_card_34b(card):
    max_len = 4
    if not card:
        return max_len * ' '
    return '-123'[card[0]] + '-ABC'[card[1]] + '-XYZ'[card[2]]


def str_card_33b(card):
    max_len = 4
    if not card:
        return max_len * ' '
    return '-123'[card[0]] + '-ABC'[card[1]]


BASIC_SET = SetRules(n=4, k=3, card_str_fn=str_card_43)
PROJ_SET = ProjectiveSet(card_str_fn=str_card_34b)
PROJ_SET_EASY = ProjectiveSet(n=2, card_str_fn=str_card_33b)


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
        change = any(idx is None or idx is True for idx in self.board)
        self.board[self.min_board :] = [
            idx for idx in self.board[self.min_board :] if idx is not None
        ]
        for ix, idx in enumerate(self.board):
            if idx is None or idx is True:
                if self.deck:
                    self.board[ix] = self.deck.pop(0)
                else:
                    self.board[ix] = False
        return change

    def add_card(self):
        if self.deck:
            self.board.append(True)
            return True
        return False

    def remove_cards(self, ixs):
        for ix in ixs:
            self.board[ix] = None

    def remove_set(self, ixs):
        if self.is_set(ixs):
            self.remove_cards(ixs)
            return True
        return False

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

    def any_set(self, ixs):
        idxs = [self.board[ix] for ix in ixs]
        return self.rules.any_set(idxs)

    def has_set(self):
        ixs = [
            ix
            for ix in range(len(self.board))
            if isinstance(self.board[ix], int) and not isinstance(self.board[ix], bool)
        ]
        return self.any_set(ixs)

    def all_sets(self):
        ixs = [
            ix
            for ix in range(len(self.board))
            if isinstance(self.board[ix], int) and not isinstance(self.board[ix], bool)
        ]
        return [
            '\t'.join(self.str_position(ix) for ix in comb)
            for comb in itertools.combinations(ixs, self.rules.k)
            if self.is_set(comb)
        ]


class Action(Enum):
    PRINT = 0
    HINT = 1
    COUNT = 2
    NO_SET = 3
    DEAL_ = 4
    END_ = 5
    SET = 6
    RM_FIRST = 7
    RM_LAST = 8
    RM_50 = 9
    HELP = 10


ACTIONS_DICT = {
    '?': Action.HELP,
    'print': Action.PRINT,
    'p': Action.PRINT,
    'hint': Action.HINT,
    'h': Action.HINT,
    'count': Action.COUNT,
    'c': Action.COUNT,
    'noset': Action.NO_SET,
    'n': Action.NO_SET,
    'set': Action.SET,
    's': Action.SET,
    'deal!': Action.DEAL_,
    'end!': Action.END_,
    'rm!': Action.RM_FIRST,
    'rml!': Action.RM_LAST,
    'rm50!': Action.RM_50,
}


def input_action():
    action_s = input('action> ').lower().strip()
    return ACTIONS_DICT.get(action_s, action_s)


def input_cards():
    ixs_input = input('cards> ')
    return [int(ix) for ix in ixs_input.split()]


def main(min_board, is_projective):
    game = SetGame(PROJ_SET if is_projective else BASIC_SET, min_board=min_board)

    while True:
        change = game.refill_board()
        if change:
            game.print_board()
        act = input_action()
        if act is Action.PRINT:
            game.print_board()
        elif act is Action.HINT:
            for hint in game.all_sets():
                print(hint)
        elif act is Action.COUNT:
            print(len(game.all_sets()))
        elif act is Action.NO_SET:
            if not game.has_set():
                if not game.add_card():
                    print('deck is empty, game ended :)')
                    break
            else:
                print('find the set first, or use deal! / end! to force')
        elif act is Action.DEAL_:
            if not game.add_card():
                print('deck is empty')
        elif act is Action.RM_FIRST:
            game.remove_cards([0])
        elif act is Action.RM_LAST:
            game.remove_cards([-1])
        elif act is Action.RM_50:
            for i in range(49):
                game.deck.pop(0)
            game.remove_cards([0])
        elif act is Action.END_:
            print('game ended :)')
            break
        elif act is Action.SET:
            try:
                ixs = input_cards()
            except ValueError:
                print('invalid cards input')
                continue
            try:
                if not game.remove_set(ixs):
                    print('not a valid set')
            except IndexError:
                print('invalid cards choice')
                continue
        else:
            if act is not Action.HELP:
                print(f'invalid action {act!r}')
            print(f'usage: {list(ACTIONS_DICT.keys())}')


if __name__ == "__main__":
    main(min_board=9, is_projective=True)
