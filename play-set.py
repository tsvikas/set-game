import itertools
import random


class SetRules:
    def __init__(self, n=4, k=3):
        self.n = n
        self.k = k
        self.cards = self.create_cards()

    def create_cards(self):
        return list(itertools.product(range(self.k), repeat=self.n))

    @property
    def deck_size(self):
        return len(self.cards)

    def str_card(self, idx):
        return str(self.cards[idx])

    def is_set(self, idxs):
        if len(idxs) != self.k:
            return False
        cards = [self.cards[idx] for idx in idxs]
        return all(
            (sum(card[dim] for card in cards) % self.k == 0) for dim in range(self.n)
        )

    def any_set(self, idxs):
        return any(self.is_set(comb) for comb in itertools.combinations(idxs, self.k))

    def all_sets(self, idxs):
        return [
            [self.cards[idx] for idx in comb]
            for comb in itertools.combinations(idxs, self.k)
            if self.is_set(comb)
        ]


class SetBoard:
    def __init__(self, deck_size, min_board=12, rand_seed=None):
        self.min_board = min_board
        random.seed(rand_seed)
        self.deck = list(range(deck_size))
        random.shuffle(self.deck)
        self.board = [None] * min_board

    def refill(self):
        self.board[self.min_board :] = [
            idx for idx in self.board[self.min_board :] if idx is not None
        ]
        self.board = [
            idx if idx is not None else self.deck.pop(0) for idx in self.board
        ]

    def add_card(self):
        self.board.append(self.deck.pop(0))

    def remove_cards(self, ixs):
        for ix in ixs:
            self.board[ix] = None

    def print(self, card_str_fn):
        for i, idx in enumerate(self.board):
            print(
                f'{i:2}: {card_str_fn(idx)}',
                end='\n' if i % 3 == 2 or i == len(self.board) - 1 else '\t',
            )
        print(f'deck: {len(self.deck)}')

    def print_deck(self, card_str_fn):
        for i, idx in enumerate(self.deck):
            print(f'{i:2}: {card_str_fn(idx)}')


def main():
    rules = SetRules()
    board = SetBoard(rules.deck_size)

    while True:
        board.refill()
        board.print(rules.str_card)
        action = input('action> ')
        if action in ['help']:
            print(rules.all_sets(board.board))
        elif action in ['noset']:
            if not rules.any_set(board.board):
                if board.deck:
                    board.add_card()
                else:
                    print('deck is empty, game ended :)')
                    break
            else:
                print('find the set first, or use deal! / end! to force')
        elif action in ['deal!']:
            if board.deck:
                board.add_card()
            else:
                print('deck is empty')
        elif action in ['end!']:
            print('game ended :)')
            break
        elif action in ['set']:
            ixs_input = input(' cards> ')
            try:
                ixs = [int(ix) for ix in ixs_input.split()]
            except ValueError:
                print('invalid cards input')
                continue
            try:
                idxs = [board.board[ix] for ix in ixs]
            except IndexError:
                print('invalid cards choice')
                continue
            if rules.is_set(idxs):
                board.remove_cards(ixs)
            else:
                print('not a valid set')
        else:
            print(f'invalid action {action!r}')


if __name__ == "__main__":
    main()
