import pygame
import sys
import os
from blackjack_game import Deck, Hand, Chips  # unchanged core logic

# -------------------- Configuration --------------------
WIDTH, HEIGHT = 1024, 768 # window dimensions
FPS = 30 # target frames per second. How many times the program redraws the entire screen each second
CARD_WIDTH, CARD_HEIGHT = 100, 145 # card image display size
TABLE_COLOR = (34, 139, 34) # table color (green)
TEXT_COLOR = (255, 255, 255) # text color (white)
BUTTON_COLOR = (200, 200, 200) # button color (light gray)
BUTTON_BORDER = (0, 0, 0) # button border color (black)
FONT_NAME = 'verdana'
# IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'images', 'cards') # path to the images folder

# -------------------- Game States --------------------
STATE_BETTING    = 'BETTING' # before the hand is dealt, player sets bet`
STATE_PLAYER     = 'PLAYER_TURN' # player's turn to hit or stand
STATE_DEALER     = 'DEALER_TURN' # dealer will draw until 17+
STATE_ROUND_OVER = 'ROUND_OVER' # show results and allow next round

# -------------------- Pygame Init --------------------
pygame.init() # initialize all imported Pygame modules
screen = pygame.display.set_mode((WIDTH, HEIGHT)) # create the main window of a given size
pygame.display.set_caption("Blackjack Game") # set window title
clock = pygame.time.Clock() # clock to manage frame rate

# -------------------- Fonts --------------------
font_small = pygame.font.SysFont(FONT_NAME, 24)
font_med   = pygame.font.SysFont(FONT_NAME, 30)
font_large = pygame.font.SysFont(FONT_NAME, 36)

# -------------------- Button Class --------------------
class Button:
    """
        Simple clickable rectangle with label.
        rect: (x, y, width, height)
        text: string shown on button
        font: pygame Font object to render text
        action: identifier passed back to main loop on click
        """
    def __init__(self, rect, text, font, action):
        self.rect = pygame.Rect(rect) # store position and size
        self.text = text
        self.font = font
        self.action = action

    def draw(self, surf):
        # draw the button rectangle and label
        pygame.draw.rect(surf, BUTTON_COLOR, self.rect)
        # draw the button border
        pygame.draw.rect(surf, BUTTON_BORDER, self.rect, 2)
        # render text centered at the button
        txt = self.font.render(self.text, True, BUTTON_BORDER)
        surf.blit(txt, txt.get_rect(center=self.rect.center)) # centers that the text surface within the button

    def clicked(self, pos):
        # check if the button was clicked
        return self.rect.collidepoint(pos)

# -------------------- Load Card Images --------------------
# point at the single images folder:
# Kenney asset file names: e.g. 'card_hearts_02.png', 'card_back.png', etc.
IMAGE_DIR = os.path.join(os.path.dirname(__file__), 'images')

# how rank names map to Kenney’s codes:
RANK_CODES = {
    'Two':'02','Three':'03','Four':'04','Five':'05','Six':'06',
    'Seven':'07','Eight':'08','Nine':'09','Ten':'10',
    'Jack':'J','Queen':'Q','King':'K','Ace':'A'
}
SUITS = ['hearts','diamonds','clubs','spades']

def load_card_images():
    images = {}
    """
        Load and scale all card face images plus card back and empty.
        Returns dict mapping keys like 'Ten_of_hearts' to a Pygame surface.
        """

    # load each of the 52 faces
    for suit in SUITS:
        for rank, code in RANK_CODES.items():
            # our lookup key matches the Card.__str__ pattern:
            key   = f"{rank}_of_{suit.capitalize()}"
            fname = f"card_{suit}_{code}.png"
            path  = os.path.join(IMAGE_DIR, fname)
            try:
                img = pygame.image.load(path).convert_alpha()
                images[key] = pygame.transform.scale(img, (CARD_WIDTH, CARD_HEIGHT))
            except:
                print(f"[Warning] Missing image: {path}")
                images[key] = None

    # load the card-back and empty placeholders
    back_path  = os.path.join(IMAGE_DIR, 'card_back.png')
    empty_path = os.path.join(IMAGE_DIR, 'card_empty.png')
    images['back']  = pygame.image.load(back_path).convert_alpha()  if os.path.exists(back_path)  else None
    images['empty']= pygame.image.load(empty_path).convert_alpha() if os.path.exists(empty_path) else None

    return images

card_images = load_card_images()


# -------------------- Draw Card --------------------
def draw_card(card, pos, hidden=False):
    x, y = pos
    """
        Blit either the face or back of a card at given position.
        card: Hand/Card object with .rank and .suit
        pos: (x, y) pixel coordinates on screen
        hidden: if True, draw the back image instead of face
        """

    # if we're drawing a face-down card:
    if hidden:
        # always show back or empty placeholder
        img = card_images['back'] or card_images['empty']
    else:
        # build lookup key e.g. 'Ten_of_hearts'
        # look up the exact face image by rank & suit
        key = f"{card.rank}_of_{card.suit}"
        img = card_images.get(key, card_images['empty'])

    # if we found an image, blit it; otherwise skip (you'll see
    # whatever was left on the screen already)
    if img:
        screen.blit(img, (x, y))
    else:
        # optional fallback: draw a white box with initials
        pygame.draw.rect(screen, (255,255,255), (x, y, CARD_WIDTH, CARD_HEIGHT))
        pygame.draw.rect(screen, BUTTON_BORDER, (x, y, CARD_WIDTH, CARD_HEIGHT), 2)
        r = font_small.render(card.rank[0], True, BUTTON_BORDER)
        s = font_small.render(card.suit[0], True, BUTTON_BORDER)
        screen.blit(r, (x+5, y+5))
        screen.blit(s, (x+5, y+25))


# -------------------- Game Logic Helpers --------------------

def reset_round():
    """
        Prepare new deck and empty hands, reset state to BETTING.
        """
    global deck, player_hand, dealer_hand, state, message
    deck = Deck()
    deck.shuffle() # fresh 52-card deck
    player_hand = Hand()
    dealer_hand = Hand()
    state = STATE_BETTING
    message = "Place your bet" # prompt shown on screen


def deal_cards():
    """
        Deal two cards each to player and dealer, then switch to player state.
        """
    global state, message
    for _ in range(2):
        player_hand.add_card(deck.deal())
        dealer_hand.add_card(deck.deal())
    state = STATE_PLAYER
    message = "Your turn"


def dealer_play():
    global state, message, chips
    while dealer_hand.value < 17:
        dealer_hand.add_card(deck.deal())
    # Evaluate outcome
    if dealer_hand.value > 21:
        message = "Dealer busts! You win"
        chips.win_bet()
    elif dealer_hand.value < player_hand.value:
        message = "You win!"
        chips.win_bet()
    elif dealer_hand.value > player_hand.value:
        message = "Dealer wins!"
        chips.lose_bet()
    else:
        message = "Push"
    state = STATE_ROUND_OVER

# -------------------- Initialization --------------------
chips = Chips() # starting chips (default 100)
reset_round() # set up deck and state

# create UI buttons with positions, labels, fonts, and action tags
buttons = [
    Button((50, 700, 50, 40), "+",        font_large, 'inc_bet'),
    Button((120,700, 50, 40), "-",        font_large, 'dec_bet'),
    Button((200,700,100,40), "Deal",     font_med,   'deal'),
    Button((350,700,100,40), "Hit",      font_med,   'hit'),
    Button((500,700,100,40), "Stand",    font_med,   'stand'),
    Button((800,700,120,40), "Next Round",font_med,  'next')
]

# -------------------- Main Loop --------------------
while True:
    # 1) Event handling
    for ev in pygame.event.get():
        if ev.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if ev.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for b in buttons:
                if not b.clicked(pos):
                    continue
                act = b.action

                # — BETTING state —
                if state == STATE_BETTING:
                    if act == 'inc_bet':
                        if chips.bet < chips.total:
                            chips.bet += 1
                        else:
                            message = "Sorry, you do not have enough chips"
                    elif act == 'dec_bet':
                        if chips.bet > 1:
                            chips.bet -= 1
                    elif act == 'deal':
                        # already guarded so deal only when valid
                        if 1 <= chips.bet <= chips.total:
                            deal_cards()
                        else:
                            message = f"Bet must be between 1 and {chips.total}"

                # — PLAYER TURN: hit ot stand —
                elif state == STATE_PLAYER:
                    if act == 'hit':
                        player_hand.add_card(deck.deal())
                        if player_hand.value > 21:
                            message = "You bust! Dealer wins"
                            chips.lose_bet()
                            state = STATE_ROUND_OVER
                    elif act == 'stand':
                        dealer_play()

                # — ROUND OVER —
                elif state == STATE_ROUND_OVER:
                    if act == 'next':
                        reset_round()

                break  # we've handled one button

    # 2) Draw everything exactly once
    screen.fill(TABLE_COLOR)

    # Dealer
    screen.blit(font_large.render("Dealer", True, TEXT_COLOR), (400, 20))
    for i, c in enumerate(dealer_hand.cards):
        hidden = (i == 0 and state == STATE_PLAYER) # hide first card until player stands
        draw_card(c, (400 + i*120, 80), hidden)

    # Player
    screen.blit(font_large.render("Player", True, TEXT_COLOR), (50, 300))
    for i, c in enumerate(player_hand.cards):
        draw_card(c, (50 + i*120, 350), False)

    # UI text
    screen.blit(font_med.render(f"Chips: {chips.total}", True, TEXT_COLOR), (50, 20))
    screen.blit(font_med.render(f"Bet:   {chips.bet}",   True, TEXT_COLOR), (50, 60))
    screen.blit(font_med.render(message, True, TEXT_COLOR), (400, 600))

    # Buttons (only the ones valid in the current state)
    for b in buttons:
        if b.action in ('inc_bet','dec_bet','deal') and state == STATE_BETTING:
            b.draw(screen)
        elif b.action in ('hit','stand') and state == STATE_PLAYER:
            b.draw(screen)
        elif b.action == 'next' and state == STATE_ROUND_OVER:
            b.draw(screen)

    # 3) Present the frame
    pygame.display.flip()
    clock.tick(FPS)
