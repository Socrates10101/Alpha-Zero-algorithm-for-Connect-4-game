#  ================ AlphaZero algorithm for 3D Connect 4 game =================== #
# Name:             MCTS_NN3D.py
# Description:      MCTS simulations guided by NN for 3D Connect 4
# Authors:          AI Assistant
# Date:             2025
# License:          BSD 3-Clause License
# ============================================================================ #

# ================================= PREAMBLE ================================= #
# Packages
import numpy as np
from Game3D import Game3D
import random
import config3d
# ============================================================================ #

# =============================== CLASS: NODE3D ================================ #
# A class representing a node of a 3D MCTS
class Node3D:
    # ---------------------------------------------------------------------------- #
    # Constructs a node from a 3D game state
    def __init__(self, game_state, move=None, parent=None):
        self.game_state = game_state  # Game3D instance
        self.move = move  # (x, y) tuple that was played from parent to get here
        self.parent = parent
        self.children = []
        self.proba_children = np.zeros(config3d.OUTPUT_SIZE)  # 16 possible moves

        self.N = 0  # visits
        self.W = 0  # cumulative reward
        self.Q = 0  # average reward

    def isLeaf(self):
        return len(self.children) == 0

    def isterminal(self):
        return self.game_state.is_game_over()

# ============================================================================ #

# =============================== CLASS: MCTS3D ================================ #
# A class representing a 3D MCTS
class MCTS_NN3D:

    # ---------------------------------------------------------------------------- #
    def __init__(self, player, use_dirichlet):
        self.root = None
        self.player = player
        self.use_dirichlet = use_dirichlet
        self.usecounter = config3d.use_counter_in_mcts_nn

    # ---------------------------------------------------------------------------- #
    def createNode(self, game_state, move=None, parent=None):
        node = Node3D(game_state, move, parent)
        return node

    # ---------------------------------------------------------------------------- #
    def PUCT(self, child, cpuct):
        """PUCT formula for 3D Connect 4"""
        move_index = self.game_state.get_move_index(child.move[0], child.move[1])
        return child.Q + cpuct * child.parent.proba_children[move_index] * np.sqrt(child.parent.N) / (1 + child.N)

    # ---------------------------------------------------------------------------- #
    def selection(self, node, cpuct):
        """Selection phase of MCTS for 3D"""
        random.seed()

        # if the provided node is already a leaf
        if node.isLeaf():
            return node, node.isterminal()

        else:  # the given node is not a leaf, pick a leaf according to PUCT
            current = node

            if config3d.use_counter_in_mcts_nn:
                current = self.superselect(current, cpuct)
            else:
                while not current.isLeaf():
                    values = []

                    for child in current.children:
                        values += [self.PUCT(child, cpuct)]

                    max_val = max(values)
                    where_max = [i for i, j in enumerate(values) if j == max_val]

                    if len(where_max) == 1:
                        current = current.children[where_max[0]]
                    else:
                        imax = where_max[int(random.random() * len(where_max))]
                        current = current.children[imax]

        return current, current.isterminal()

    # ---------------------------------------------------------------------------- #
    def superselect(self, node, cpuct):
        """Enhanced selection with critical move detection for 3D"""
        # Check if current player can win or prevent loss
        can_win, winning_moves, can_lose, losing_moves = self.iscritical3d(node.game_state)
        
        if can_win:
            # Take the win
            for child in node.children:
                if child.move in winning_moves:
                    return child
        
        if can_lose:
            # Block the loss
            for child in node.children:
                if child.move in losing_moves:
                    return child
        
        # Otherwise use normal selection
        return self.selection(node, cpuct)[0]

    # ---------------------------------------------------------------------------- #
    def iscritical3d(self, game_state):
        """Check for critical moves in 3D Connect 4"""
        can_win = False
        winning_moves = []
        can_lose = False
        losing_moves = []

        allowed_moves = game_state.allowed_moves()

        # Check if current player can win
        for move in allowed_moves:
            virtual_game = game_state.make_move(move[0], move[1])
            if virtual_game and virtual_game.check_win(-virtual_game.player_turn):  # Previous player won
                can_win = True
                winning_moves.append(move)

        # Check if opponent can win (current player can lose)
        for move in allowed_moves:
            # Create state where opponent would play
            temp_game = game_state.copy()
            temp_game.player_turn = -temp_game.player_turn
            virtual_game = temp_game.make_move(move[0], move[1])
            if virtual_game and virtual_game.check_win(-virtual_game.player_turn):  # Opponent would win
                can_lose = True
                losing_moves.append(move)

        return can_win, winning_moves, can_lose, losing_moves

    # ---------------------------------------------------------------------------- #
    def expansion(self, node):
        """Expansion phase - add all possible moves as children"""
        if not node.isterminal():
            allowed_moves = node.game_state.allowed_moves()
            
            for move in allowed_moves:
                new_game_state = node.game_state.make_move(move[0], move[1])
                if new_game_state:  # Valid move
                    child = self.createNode(new_game_state, move, node)
                    node.children.append(child)

    # ---------------------------------------------------------------------------- #
    def evaluation(self, node):
        """Evaluation using neural network"""
        # Get state vector for neural network
        state_vector = node.game_state.get_state_vector()
        
        # Get NN prediction
        q_value, policy = self.player(state_vector)
        
        # Apply Dirichlet noise if needed
        if self.use_dirichlet:
            policy = self.add_dirichlet_noise(policy, node.game_state.allowed_moves())
        
        # Store policy probabilities
        node.proba_children = policy.detach().numpy().flatten()
        
        return q_value.item()

    # ---------------------------------------------------------------------------- #
    def add_dirichlet_noise(self, policy, allowed_moves):
        """Add Dirichlet noise to policy for exploration"""
        noise = np.random.dirichlet([config3d.alpha_dir] * len(allowed_moves))
        
        # Create mask for allowed moves
        mask = np.zeros(config3d.OUTPUT_SIZE)
        for i, move in enumerate(allowed_moves):
            move_index = Game3D().get_move_index(move[0], move[1])
            mask[move_index] = 1
        
        # Apply noise only to allowed moves
        policy_np = policy.detach().numpy().flatten()
        noise_full = np.zeros(config3d.OUTPUT_SIZE)
        
        allowed_indices = [Game3D().get_move_index(move[0], move[1]) for move in allowed_moves]
        for i, idx in enumerate(allowed_indices):
            noise_full[idx] = noise[i]
        
        # Mix original policy with noise
        policy_np = (1 - config3d.epsilon_dir) * policy_np + config3d.epsilon_dir * noise_full
        
        # Renormalize
        policy_np = policy_np * mask
        if np.sum(policy_np) > 0:
            policy_np = policy_np / np.sum(policy_np)
        
        return torch.FloatTensor(policy_np).unsqueeze(0)

    # ---------------------------------------------------------------------------- #
    def backpropagation(self, node, reward):
        """Backpropagation phase"""
        current = node
        
        while current is not None:
            current.N += 1
            current.W += reward
            current.Q = current.W / current.N
            
            # Flip reward for opponent
            reward = -reward
            current = current.parent

    # ---------------------------------------------------------------------------- #
    def simulation(self, cpuct):
        """One MCTS simulation"""
        # Selection
        leaf, is_terminal = self.selection(self.root, cpuct)
        
        if is_terminal:
            # Terminal node - get actual reward
            winner = leaf.game_state.get_winner()
            if winner is None:
                reward = 0  # Should not happen in terminal
            elif winner == 0:
                reward = 0  # Draw
            else:
                # Reward from perspective of player who just moved
                reward = winner * (-leaf.game_state.player_turn)
        else:
            # Non-terminal node - expand and evaluate
            if leaf.N == 0:  # First visit
                # Evaluate with NN
                reward = self.evaluation(leaf)
                # Expand
                self.expansion(leaf)
            else:
                # Should not happen in proper MCTS
                reward = 0
        
        # Backpropagate
        self.backpropagation(leaf, reward)

    # ---------------------------------------------------------------------------- #
    def run_simulations(self, game_state, num_simulations, cpuct):
        """Run multiple MCTS simulations"""
        self.root = self.createNode(game_state)
        
        # Initialize root
        if not self.root.isterminal():
            self.evaluation(self.root)
            self.expansion(self.root)
        
        # Run simulations
        for _ in range(num_simulations):
            self.simulation(cpuct)
        
        return self.root

    # ---------------------------------------------------------------------------- #
    def get_action_probabilities(self, temperature=1.0):
        """Get action probabilities from MCTS tree"""
        if not self.root or not self.root.children:
            return np.ones(config3d.OUTPUT_SIZE) / config3d.OUTPUT_SIZE
        
        # Get visit counts
        visits = np.zeros(config3d.OUTPUT_SIZE)
        for child in self.root.children:
            move_index = Game3D().get_move_index(child.move[0], child.move[1])
            visits[move_index] = child.N
        
        if temperature == 0:
            # Greedy selection
            probs = np.zeros(config3d.OUTPUT_SIZE)
            best_move = np.argmax(visits)
            probs[best_move] = 1.0
        else:
            # Temperature scaling
            if temperature != 1.0:
                visits = np.power(visits, 1.0 / temperature)
            
            if np.sum(visits) > 0:
                probs = visits / np.sum(visits)
            else:
                probs = np.ones(config3d.OUTPUT_SIZE) / config3d.OUTPUT_SIZE
        
        return probs

# ============================================================================ #

# Import torch here to avoid circular dependency issues
import torch