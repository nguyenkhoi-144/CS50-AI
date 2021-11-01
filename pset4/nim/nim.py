import math
import random
import time


class Nim():

    def __init__(self, initial=[1, 3, 5, 7]):
        """
        Initialize game board.
        Each game board has
            - `piles`: a list of how many elements remain in each pile
            - `player`: 0 or 1 to indicate which player's turn
            - `winner`: None, 0, or 1 to indicate who the winner is
        Khởi tạo bảng trò chơi.
        Mỗi bảng trò chơi có
            - `cọc`: danh sách có bao nhiêu phần tử còn lại trong mỗi cọc
            - `player`: 0 hoặc 1 để cho biết lượt của người chơi
            - `người chiến thắng`: Không có, 0 hoặc 1 để cho biết ai là người chiến thắng

        """
        self.piles = initial.copy()
        self.player = 0
        self.winner = None

    @classmethod
    def available_actions(cls, piles):
        """
        Nim.available_actions(piles) takes a `piles` list as input
        and returns all of the available actions `(i, j)` in that state.

        Action `(i, j)` represents the action of removing `j` items
        from pile `i` (where piles are 0-indexed).

        Nim.available_actions (cọc) lấy danh sách `cọc` làm đầu vào
        và trả về tất cả các hành động có sẵn `(i, j)` ở trạng thái đó.

        Hành động `(i, j)` đại diện cho hành động xóa các mục `j`
        từ cọc `i` (trong đó các cọc được lập chỉ mục 0).

        """
        actions = set()
        for i, pile in enumerate(piles):
            for j in range(1, pile + 1):
                actions.add((i, j))
        return actions

    @classmethod
    def other_player(cls, player):
        """
        Nim.other_player(player) returns the player that is not
        `player`. Assumes `player` is either 0 or 1.
        Nim.other_player (trình phát) trả về trình phát không phải
        `người chơi`. Giả sử `player` là 0 hoặc 1.
        """
        return 0 if player == 1 else 1

    def switch_player(self):
        """
        Switch the current player to the other player.
        Chuyển trình phát hiện tại sang trình phát khác.
        """
        self.player = Nim.other_player(self.player)

    def move(self, action):
        """
        Make the move `action` for the current player.
        `action` must be a tuple `(i, j)`.
        Thực hiện hành động `` hành động '' cho người chơi hiện tại.
        `action` phải là một tuple` (i, j) `.
        """
        pile, count = action

        # Check for errors
        if self.winner is not None:
            raise Exception("Game already won")
        elif pile < 0 or pile >= len(self.piles):
            raise Exception("Invalid pile")
        elif count < 1 or count > self.piles[pile]:
            raise Exception("Invalid number of objects")

        # Update pile
        self.piles[pile] -= count
        self.switch_player()

        # Check for a winner
        if all(pile == 0 for pile in self.piles):
            self.winner = self.player


class NimAI():

    def __init__(self, alpha=0.5, epsilon=0.1):
        """
        Initialize AI with an empty Q-learning dictionary,
        an alpha (learning) rate, and an epsilon rate.

        The Q-learning dictionary maps `(state, action)`
        pairs to a Q-value (a number).
         - `state` is a tuple of remaining piles, e.g. (1, 1, 4, 4)
         - `action` is a tuple `(i, j)` for an action
         Khởi tạo AI với từ điển Q-learning trống,
        tỷ lệ alpha (học tập) và tỷ lệ epsilon.

        Bản đồ từ điển Q-learning '(trạng thái, hành động)'
        ghép nối thành giá trị Q (một số).
         - `trạng thái` là một loạt các cọc còn lại, ví dụ: (1, 1, 4, 4)
         - `action` là một tuple` (i, j) `cho một hành động
        """
        self.q = dict()
        self.alpha = alpha
        self.epsilon = epsilon

    def update(self, old_state, action, new_state, reward):
        """
        Update Q-learning model, given an old state, an action taken
        in that state, a new resulting state, and the reward received
        from taking that action.
        Cập nhật mô hình Q-learning, với trạng thái cũ, một hành động được thực hiện
        ở trạng thái đó, trạng thái kết quả mới và phần thưởng nhận được
        từ việc thực hiện hành động đó.
        """
        old = self.get_q_value(old_state, action)
        best_future = self.best_future_reward(new_state)
        self.update_q_value(old_state, action, old, reward, best_future)

    def get_q_value(self, state, action):
        """
        Return the Q-value for the state `state` and the action `action`.
        If no Q-value exists yet in `self.q`, return 0.
        Trả về giá trị Q cho trạng thái `trạng thái` và hành động` hành động`.
        Nếu chưa có giá trị Q nào tồn tại trong `self.q`, hãy trả về 0.
        """
        # Trả về giá trị Q cho trạng thái `trạng thái` và hành động` hành động`.
        if (tuple(state), action) in self.q:
            q = self.q[(tuple(state), action)]
            return q
        # Nếu không có giá trị Q nào tồn tại trong `self.q`, hãy trả về 0.
        else:
            return 0

    def update_q_value(self, state, action, old_q, reward, future_rewards):
        """
        Update the Q-value for the state `state` and the action `action`
        given the previous Q-value `old_q`, a current reward `reward`,
        and an estiamte of future rewards `future_rewards`.

        Use the formula:

        Q(s, a) <- old value estimate
                   + alpha * (new value estimate - old value estimate)

        where `old value estimate` is the previous Q-value,
        `alpha` is the learning rate, and `new value estimate`
        is the sum of the current reward and estimated future rewards.

        Cập nhật giá trị Q cho trạng thái `state` và hành động` action`
        đã đưa ra giá trị Q trước đó `old_q`, phần thưởng hiện tại là` phần thưởng`,
        và một loạt các phần thưởng trong tương lai `future_rewards`.

        Sử dụng công thức:

        Q (s, a) <- ước tính giá trị cũ
                   + alpha * (ước tính giá trị mới - ước tính giá trị cũ)

        trong đó `ước tính giá trị cũ` là giá trị Q trước đó,
        `alpha` là tốc độ học tập và` ước tính giá trị mới`
        là tổng của phần thưởng hiện tại và phần thưởng ước tính trong tương lai.
        """
        new_q = old_q + self.alpha * (reward + future_rewards - old_q)
        return new_q

    def best_future_reward(self, state):
        """
        Given a state `state`, consider all possible `(state, action)`
        pairs available in that state and return the maximum of all
        of their Q-values.

        Use 0 as the Q-value if a `(state, action)` pair has no
        Q-value in `self.q`. If there are no available actions in
        `state`, return 0.

        Đưa ra một trạng thái `trạng thái`, hãy xem xét tất cả có thể có` (trạng thái, hành động) '
        các cặp có sẵn ở trạng thái đó và trả về giá trị tối đa của tất cả
        giá trị Q của chúng.

        Sử dụng 0 làm giá trị Q nếu một cặp `(trạng thái, hành động)` không có
        Giá trị Q trong `self.q`. Nếu không có hành động nào trong
        `trạng thái`, trả về 0.
        """
        # Sử dụng 0 làm giá trị Q nếu một cặp `(trạng thái, hành động)` không có
        #Giá trị Q trong `self.q`. Nếu không có hành động nào trong
        #`trạng thái`, trả về 0.
        best = 0
        # Cho một trạng thái `trạng thái`, hãy xem xét tất cả có thể`
        # (trạng thái, hành động) '
        pos = Nim.available_actions(state)
        for action in pos:
            q = self.get_q_value(state, action)
            if q > best:
                q = best
        return best

    def choose_action(self, state, epsilon=True):
        """
        Given a state `state`, return an action `(i, j)` to take.

        If `epsilon` is `False`, then return the best action
        available in the state (the one with the highest Q-value,
        using 0 for pairs that have no Q-values).

        If `epsilon` is `True`, then with probability
        `self.epsilon` choose a random available action,
        otherwise choose the best action available.

        If multiple actions have the same Q-value, any of those
        options is an acceptable return value.

        Cho một trạng thái `trạng thái`, trả về một hành động` (i, j) `để thực hiện.

        Nếu `epsilon` là` False`, thì trả về hành động tốt nhất
        có sẵn ở trạng thái (trạng thái có giá trị Q cao nhất,
        sử dụng 0 cho các cặp không có giá trị Q).

        Nếu `epsilon` là` True`, thì với xác suất
        `self.epsilon` chọn một hành động ngẫu nhiên có sẵn,
        nếu không, hãy chọn hành động tốt nhất hiện có.

        Nếu nhiều hành động có cùng giá trị Q, thì bất kỳ hành động nào trong số đó
        các tùy chọn là giá trị trả về có thể chấp nhận được.
        """
        best_action = 0
        best_reward = 0

        pos = Nim.available_actions(state)

        for action in pos:
            q = self.get_q_value(state, action)
            # tìm và trả về giá trị tối đa của tất cả các giá trị Q của chúng.
            if q >= best_reward:
                best_reward = q
                best_action = action
        # Nếu `epsilon` là` False`, thì trả về hành động tốt nhất
        # có sẵn ở trạng thái (trạng thái có giá trị Q cao nhất,
        # sử dụng 0 cho các cặp không có giá trị Q).
        if epsilon is False:
            return best_action
        # Nếu `epsilon` là` True`, thì với xác suất
        # `self.epsilon` chọn một hành động ngẫu nhiên có sẵn,
        # nếu không, hãy chọn hành động tốt nhất hiện có.
        else:
            # nhận xác suất được chọn ngẫu nhiên cho mỗi khả năng
            rand_prob = self.epsilon / len(pos)
            # Chỉ định xác suất và hành động trở lại
            probs = [(1 - self.epsilon) + rand_prob if possibility == best_action else rand_prob for possibility in list(pos)]
            action = random.choices(list(pos), probs)[0]
            return action






def train(n):
    """
    Train an AI by playing `n` games against itself.
    Đào tạo AI bằng cách chơi trò chơi `n` với chính nó.
    """

    player = NimAI()

    # Play n games
    for i in range(n):
        print(f"Playing training game {i + 1}")
        game = Nim()

        # Keep track of last move made by either player
        last = {
            0: {"state": None, "action": None},
            1: {"state": None, "action": None}
        }

        # Game loop
        while True:

            # Keep track of current state and action
            state = game.piles.copy()
            action = player.choose_action(game.piles)

            # Keep track of last state and action
            last[game.player]["state"] = state
            last[game.player]["action"] = action

            # Make move
            game.move(action)
            new_state = game.piles.copy()

            # When game is over, update Q values with rewards
            if game.winner is not None:
                player.update(state, action, new_state, -1)
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    1
                )
                break

            # If game is continuing, no rewards yet
            elif last[game.player]["state"] is not None:
                player.update(
                    last[game.player]["state"],
                    last[game.player]["action"],
                    new_state,
                    0
                )

    print("Done training")

    # Return the trained AI
    return player


def play(ai, human_player=None):
    """
    Play human game against the AI.
    `human_player` can be set to 0 or 1 to specify whether
    human player moves first or second.
    Chơi trò chơi con người chống lại AI.
    `human_player` có thể được đặt thành 0 hoặc 1 để chỉ định xem
    người chơi di chuyển đầu tiên hoặc thứ hai.
    """

    # If no player order set, choose human's order randomly
    if human_player is None:
        human_player = random.randint(0, 1)

    # Create new game
    game = Nim()

    # Game loop
    while True:

        # Print contents of piles
        print()
        print("Piles:")
        for i, pile in enumerate(game.piles):
            print(f"Pile {i}: {pile}")
        print()

        # Compute available actions
        available_actions = Nim.available_actions(game.piles)
        time.sleep(1)

        # Let human make a move
        if game.player == human_player:
            print("Your Turn")
            while True:
                pile = int(input("Choose Pile: "))
                count = int(input("Choose Count: "))
                if (pile, count) in available_actions:
                    break
                print("Invalid move, try again.")

        # Have AI make a move
        else:
            print("AI's Turn")
            pile, count = ai.choose_action(game.piles, epsilon=False)
            print(f"AI chose to take {count} from pile {pile}.")

        # Make move
        game.move((pile, count))

        # Check for winner
        if game.winner is not None:
            print()
            print("GAME OVER")
            winner = "Human" if game.winner == human_player else "AI"
            print(f"Winner is {winner}")
            return
