from otree.api import *
import random as r


doc = """
    3x3 Game with varying payoffs. Players are to choose 
"""


class C(BaseConstants):
    NAME_IN_URL = 'threebythree'

    # Players per group and Roles. This is so we can manipulate each player later on should we need to.
    PLAYERS_PER_GROUP = 2
    ORANGE_ROLE = 'Orange'
    GREEN_ROLE = 'Green'

    # For now we have a fixed number of rounds.
    NUM_ROUNDS = 5


    # Choices that an individual player sees. A,B,C is what they see on the screen and 0,1,2 is the input we take from them.
    CHOICES = [
            [0, "A"],
            [1, "B"],
            [2, "C"],
        ]


    PAYOFF_DICT_LIST = {}
    '''
        Making C.NUM_ROUNDS different 3x3 games with accessible keys. The key's follow Cij_k style:
        E.g. C21_0:
        C --> 'Cell'
        i == 2 --> Player 1 decision i in [0,1,2]
        j == 1 --> Player 2 decision j in [0,1,2]
        k == 0 --> for Player 1 decision i == 2, & Player 2 decision j == 1, we have Player 1 payoff k == 0 Player 2 payoff k == 1.
    '''
    for round in range(NUM_ROUNDS):
        PAYOFF_DICT_LIST[f"payoff_round_{round + 1}"] = {}
        for i in range(3):
            for j in range(3):
                for k in range(2):
                    PAYOFF_DICT_LIST[f"payoff_round_{round + 1}"][f"C{i}{j}_{k}"] = 10 * r.randint(1,9)


    # randomly decides which round is the one that pays the players. Is between 1 and NUM_ROUNDS inclusive.
    PAYOFF_ROUND = r.randint(1, NUM_ROUNDS)

class Subsession(BaseSubsession):
    pass


class Group(BaseGroup):
    pass


class Player(BasePlayer):

    # from C.CHOICES, we ask players for their decision.
    decision = models.IntegerField(label = "What is your choice?",
                                   choices = C.CHOICES,
                                   widget = widgets.RadioSelectHorizontal)

# PAGES

# Introduction Page. Only shown once at the beginning of session.
class IntroPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == 1:
            return True
        else:
            return False

# Decision Page. There will be C.NUM_ROUNDS DecisionPages and C.NUM_ROUNDS decisions by/for each player.
class DecisionPage(Page):
    form_model = "player"
    form_fields = ["decision"]

    # introduces the matrix "payoff_round_{player.round_number}" for each round.
    @staticmethod
    def vars_for_template(player: Player):
        for round in range(C.NUM_ROUNDS):
            if player.round_number == round + 1:
                payoff_for_this_round = C.PAYOFF_DICT_LIST[f"payoff_round_{round + 1}"]
            else:
                pass
        return payoff_for_this_round


    # Failsafe method that ensures a session continues even if we push a player to the next round.
    @staticmethod 
    def before_next_page(player: Player, timeout_happened):
        import random as r
        if timeout_happened:
            player.decision = r.choice(C.CHOICES)[0]

# After each DecisionPage, there will be a RelaxationPage. This is to momentarily get the participant's mind off the last game.
class RelaxationPage(Page):
    @staticmethod
    def is_displayed(player: Player):
        if player.round_number != C.NUM_ROUNDS:
            return True
        else:
            return False

# Once a player finishes their choices, they will see WaitingForCounterPart page, which basically tells them that
# They need to wait until we find a match for them so we can calculate their payoffs.

class WaitingForCounterPart(WaitPage):

    # Uses the html template.
    template_name = 'threebythree/WaitingForCounterPart.html'

    #Title of WaitPage.
    title_text = "Thank you for your time!"
    
    # Method so this page is only relevant at the last round.
    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True
        else:
            return False
    

    # This calculates payoffs after the 2 players in each group finish all of their games.
    @staticmethod
    def after_all_players_arrive(group: Group):
        payoff_list = group.in_round(C.PAYOFF_ROUND) # gets a group's info for the round randomly decided by C.PAYOFF_ROUND.
        p1, p2 = payoff_list.get_players() # assign's p1 & p2 to player 1 and player 2.

        # This is the payoff Key to find a specific value in C.PAYOFF_DICT_LIST[f"payoff_round_{C.PAYOFF_ROUND}"]
        p1_key = f"C{p1.decision}{p2.decision}_0"
        p2_key = f"C{p1.decision}{p2.decision}_1"

        # Finds player 1 & 2's payoff based on their Key (Looks something like C00_0 or C21_1)
        p1.payoff = C.PAYOFF_DICT_LIST[f"payoff_round_{C.PAYOFF_ROUND}"][p1_key]
        p2.payoff = C.PAYOFF_DICT_LIST[f"payoff_round_{C.PAYOFF_ROUND}"][p2_key]

# Classic Results Page
class Results(Page):

    # Method so this page is only relevant at the last round.
    @staticmethod
    def is_displayed(player: Player):
        if player.round_number == C.NUM_ROUNDS:
            return True
        else:
            return False


page_sequence = [IntroPage, DecisionPage, RelaxationPage, WaitingForCounterPart, Results]