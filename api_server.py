from flask import Flask, request, jsonify
from flask_cors import CORS
import numpy as np
import torch
from MCTS_NN import MCTS_NN
from ResNet import ResNet
from Game_bitboard import Connect4
import config

app = Flask(__name__)
CORS(app)

# Load the trained model
device = torch.device("cuda" if torch.cuda.is_available() and config.use_cuda else "cpu")
model = ResNet()
model.load_state_dict(torch.load('best_model_resnet.pth', map_location=device))
model.to(device)
model.eval()

def board_to_bitboard(board_array):
    """Convert 2D array board to bitboard format"""
    yellow_bitboard = 0
    red_bitboard = 0
    
    for col in range(7):
        for row in range(6):
            if board_array[col][row] == 'yellow':
                yellow_bitboard |= (1 << (col * 7 + row))
            elif board_array[col][row] == 'red':
                red_bitboard |= (1 << (col * 7 + row))
    
    return yellow_bitboard, red_bitboard

def get_ai_move(board_array, current_player):
    """Get AI move using MCTS with neural network"""
    yellow_bitboard, red_bitboard = board_to_bitboard(board_array)
    
    # Determine player turn (1 for yellow, -1 for red)
    player_turn = 1 if current_player == 'yellow' else -1
    
    # Create game state
    game = Connect4()
    game.yellowboard = yellow_bitboard
    game.redboard = red_bitboard
    game.playerturn = player_turn
    
    # Use MCTS to find best move
    mcts = MCTS_NN(model, device, game, cpuct=config.CPUCT)
    
    # Run simulations
    for _ in range(config.sim_number_defense):
        mcts.run_sims(game)
    
    # Get move probabilities
    probs = mcts.probs(game, tau=0)  # tau=0 for deterministic play
    
    # Choose best valid move
    best_col = np.argmax(probs)
    
    # Get evaluation
    state = game.get_state()
    state_tensor = torch.FloatTensor(state).unsqueeze(0).to(device)
    with torch.no_grad():
        _, value = model(state_tensor)
        evaluation = value.item()
    
    return int(best_col), float(evaluation)

@app.route('/ai-move', methods=['POST'])
def ai_move():
    data = request.json
    board = data['board']
    current_player = data['currentPlayer']
    
    if current_player not in ['yellow', 'red']:
        return jsonify({'error': 'Invalid player'}), 400
    
    try:
        column, evaluation = get_ai_move(board, current_player)
        return jsonify({
            'column': column,
            'evaluation': evaluation
        })
    except Exception as e:
        print(f"Error in AI move: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/validate-move', methods=['POST'])
def validate_move():
    data = request.json
    board = data['board']
    move = data['move']
    
    column = move['column']
    if column < 0 or column >= 7:
        return jsonify({'valid': False})
    
    # Check if column has space
    column_cells = board[column]
    valid = any(cell is None for cell in column_cells)
    
    return jsonify({'valid': valid})

@app.route('/health', methods=['GET'])
def health():
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(port=5000, debug=True)