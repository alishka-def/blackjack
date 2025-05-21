
import random

suits = ('Hearts', 'Diamonds', 'Spades', 'Clubs')
ranks = ('Two', 'Three', 'Four', 'Five', 'Six', 'Seven', 'Eight', 'Nine', 'Ten', 'Jack', 'Queen', 'King', 'Ace')
values = {'Two':2, 'Three':3, 'Four':4, 'Five':5, 'Six':6, 'Seven':7, 'Eight':8,
            'Nine':9, 'Ten':10, 'Jack':10, 'Queen':10, 'King':10, 'Ace':11}

playing = True # controls the player hit/stand loop

# Card class
class Card:

    def __init__(self, suit, rank):
        self.suit = suit
        self.rank = rank
        self.value = values[rank]  # use the values dictionary to assign a value to the card

    def __str__(self):
        return self.rank + " of " + self.suit  # return a string representation of the card

# Deck class
class Deck:

    def __init__(self):
        self.deck = []  # start with an empty list
        for suit in suits:
            for rank in ranks:
                created_card = Card(suit, rank)  # create a card object
                self.deck.append(created_card)  # add the card to the deck

    def __str__(self):
        deck_comp = ' '
        for card in self.deck:
            deck_comp += '\n ' + card.__str__()  # add each Card object's print string
        return "The deck has: " + deck_comp

    def shuffle(self):
        random.shuffle(self.deck)

    def deal(self):
        single_card = self.deck.pop()  # remove the last card from the deck and return it
        return single_card


# Hand class
# representing how many cards are currently in the hand
class Hand:
    def __init__(self):
        self.cards = []  # start with an empty list as we did in the Deck class
        self.value = 0  # start with zero value
        self.aces = 0  # add an attribute to keep track of aces

    def add_card(self, card):
        # card passed in from deck.deal() --> single Card object
        self.cards.append(card)
        self.value += values[card.rank]

        if card.rank == 'Ace':
            self.aces += 1  # add to the number of aces in the hand

    def adjust_for_ace(self):
        print("test")
        while self.value > 21 and self.aces:
            self.value -= 10
            self.aces -= 1


# Chips class
class Chips:

    def __init__(self, total=100):
        self.total = total  # This can be set to a default value or supplied by a user input
        self.bet = 0

    def win_bet(self):
        self.total += self.bet

    def lose_bet(self):
        self.total -= self.bet

# Function for taking bets
def take_bet(chips):
    while True:
        try:
            chips.bet = int(input("How many chips would you like to bet? "))
        except:
            print("Sorry, please provide an integer")
        else:
            if chips.bet > chips.total:
                print("Sorry, you do not have enough chips! You have {}".format(chips.total))
            else:
                break

# Function for taking hits
def hit(deck,hand):
    hand.add_card(deck.deal())
    hand.adjust_for_ace()

# Function prompting the player to hit or stand
def hit_or_stand(deck,hand):
    global playing  # to control an upcoming while loop

    while True:
        x = input("Would you like to Hit or Stand? Enter 'h' or 's' ")
        if x[0].lower() == 'h':
            hit(deck,hand)
            break
        elif x[0].lower() == 's':
            print("Player Stands Dealer's Turn")
            playing = False
            break
        else:
            print("Sorry, I did not understand that. Please enter 'h' or 's' only!")
            continue


# Function to display the cards
def show_some(player, dealer):
    # show only ONE of the dealer's cards
    print("\n Dealer's Hand: ")
    print("First card hidden!")
    print(dealer.cards[1])  # show the dealer's second card
    # show all the player's cards
    print("\n Player's Hand: ")
    for card in player.cards:
        print(card)


def show_all(player, dealer):
    # show all the dealer's cards
    print("\n Dealer's Hand: ")
    for card in dealer.cards:
        print(card)
    # calculate and display value
    print(f"Dealer's Hand Value: {dealer.value} ")
    # show all the player's cards
    print("\n Player's Hand: ")
    for card in player.cards:
        print(card)
    print(f"Player's Hand Value: {player.value} ")


# Function to handle the end of the game
def player_busts(player, dealer, chips):
    print("Player busts! Dealer wins!")
    chips.lose_bet()


def player_wins(player, dealer, chips):
    print("Player wins! Dealer loses!")
    chips.win_bet()


def dealer_busts(player, dealer, chips):
    print("Dealer busts! Player wins!")
    chips.win_bet()


def dealer_wins(player, dealer, chips):
    print("Dealer wins! Player loses!")
    chips.lose_bet()


def push(player, dealer):
    print("Dealer and Player tie! It's a push.")

# Gaming logic
def play_game():
    global playing
    while True:
        # Print an opening statement
        print("Welcome to the game of Blackjack!")
        # Create & shuffle the deck, deal two cards to each player
        deck = Deck()
        deck.shuffle()

        # deal 2 cards to player
        player_hand = Hand()
        player_hand.add_card(deck.deal())
        player_hand.add_card(deck.deal())

        # deal 2 cards to dealer
        dealer_hand = Hand()
        dealer_hand.add_card(deck.deal())
        dealer_hand.add_card(deck.deal())

        # Set up the Player's chips
        player_chips = Chips()  # remember the default value is 100

        # Prompt the Player for their bet
        take_bet(player_chips)

        # Show cards (but keep one dealer card hidden)
        show_some(player_hand, dealer_hand)

        while playing:  # recall this variable from our hit_or_stand function

            # Prompt for Player to Hit or Stand
            hit_or_stand(deck, player_hand)

            # Show cards (but keep one dealer card hidden)
            show_some(player_hand, dealer_hand)

            # If player's hand exceeds 21, run player_busts() and break out of loop
            if player_hand.value > 21:
                player_busts(player_hand, dealer_hand, player_chips)

                break

        # If Player hasn't busted, play Dealer's hand until Dealer reaches 17
        if player_hand.value <= 21:
            while dealer_hand.value < 17:
                hit(deck, dealer_hand)

            # Show all cards
            show_all(player_hand, dealer_hand)

            # Run different winning scenarios
            if dealer_hand.value > 21:
                dealer_busts(player_hand, dealer_hand, player_chips)
            elif dealer_hand.value > player_hand.value:
                dealer_wins(player_hand, dealer_hand, player_chips)
            elif dealer_hand.value < player_hand.value:
                player_wins(player_hand, dealer_hand, player_chips)
            else:
                push(player_hand, dealer_hand)

        # Inform Player of their chips total
        print("\n Player's total chips are at: {}".format(player_chips.total))
        # Ask to play again
        new_game = input("Would you like to play again? Enter 'y' or 'n' ")
        if new_game[0].lower() == 'y':
            playing = True  # reset playing variable to True
            continue
        else:
            print("Thanks for playing!")
            break
if __name__ == "__main__":
    play_game()