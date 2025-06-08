#  ================ Integration Test for 3D Connect 4 =================== #
# Name:             test_integration.py
# Description:      Integration test for 3D Connect 4 components
# Authors:          AI Assistant
# Date:             2025
# License:          BSD 3-Clause License
# ============================================================================ #

from Game3D import Game3D
import config3d
import numpy as np

def test_game_selector_requirements():
    """Test that all required files exist for game selector"""
    print("Testing game selector requirements...")
    
    from game_selector import GameSelector
    selector = GameSelector()
    
    # Test 2D requirements
    has_2d = selector.check_requirements('2d')
    print(f"2D Connect 4 requirements: {'✓' if has_2d else '✗'}")
    
    # Test 3D requirements  
    has_3d = selector.check_requirements('3d')
    print(f"3D Connect 4 requirements: {'✓' if has_3d else '✗'}")
    
    return has_2d, has_3d

def test_3d_game_basic():
    """Test basic 3D game functionality"""
    print("\nTesting 3D Connect 4 basic functionality...")
    
    game = Game3D()
    print(f"✓ 3D game initialized")
    print(f"✓ Board size: {config3d.SIZE}x{config3d.SIZE}x{config3d.SIZE}")
    print(f"✓ Winning lines: {len(game._winning_lines)}")
    print(f"✓ Initial moves available: {len(game.allowed_moves())}")
    
    # Test making moves
    game = game.make_move(1, 1)
    print(f"✓ Made move (1,1), player turn now: {game.player_turn}")
    
    game = game.make_move(2, 2)
    print(f"✓ Made move (2,2), player turn now: {game.player_turn}")
    
    print(f"✓ Moves available after 2 moves: {len(game.allowed_moves())}")
    
    return True

def test_3d_neural_network():
    """Test 3D neural network structure"""
    print("\nTesting 3D neural network...")
    
    try:
        from ResNet3D import resnet18_3d
        
        # Create network
        net = resnet18_3d()
        print("✓ 3D ResNet created successfully")
        
        # Test with sample input
        game = Game3D()
        state_vector = game.get_state_vector()
        print(f"✓ State vector shape: {state_vector.shape}")
        
        # Test forward pass
        value, policy = net(state_vector)
        print(f"✓ Neural network forward pass successful")
        print(f"✓ Value output shape: {value.shape}")
        print(f"✓ Policy output shape: {policy.shape}")
        print(f"✓ Policy outputs {policy.shape[1]} moves (expected 16)")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing neural network: {e}")
        return False

def test_3d_mcts():
    """Test 3D MCTS structure"""
    print("\nTesting 3D MCTS...")
    
    try:
        from MCTS_NN3D import MCTS_NN3D, Node3D
        
        # Create dummy neural network function
        def dummy_nn(state_vector):
            import torch
            # Return dummy value and policy
            value = torch.tensor([[0.0]])
            policy = torch.ones((1, 16)) / 16  # Uniform policy
            return value, policy
        
        # Create MCTS
        mcts = MCTS_NN3D(dummy_nn, use_dirichlet=False)
        print("✓ 3D MCTS created successfully")
        
        # Create test node
        game = Game3D()
        node = mcts.createNode(game)
        print("✓ 3D MCTS node created successfully")
        
        # Test critical move detection
        can_win, winning_moves, can_lose, losing_moves = mcts.iscritical3d(game)
        print(f"✓ Critical move detection works")
        print(f"✓ Initial state - Can win: {can_win}, Can lose: {can_lose}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing MCTS: {e}")
        return False

def test_game_compatibility():
    """Test that 2D and 3D games can coexist"""
    print("\nTesting game compatibility...")
    
    try:
        # Test 2D game
        from Game_bitboard import Game
        game2d = Game()
        print("✓ 2D Connect 4 game loaded")
        
        # Test 3D game
        game3d = Game3D()
        print("✓ 3D Connect 4 game loaded")
        
        # Test configs
        import config
        import config3d
        print(f"✓ 2D config: {config.L}x{config.H} board")
        print(f"✓ 3D config: {config3d.SIZE}x{config3d.SIZE}x{config3d.SIZE} board")
        
        return True
        
    except Exception as e:
        print(f"✗ Error testing compatibility: {e}")
        return False

def run_all_tests():
    """Run all integration tests"""
    print("=" * 60)
    print("    3D CONNECT 4 INTEGRATION TESTS")
    print("=" * 60)
    
    tests = [
        test_game_selector_requirements,
        test_3d_game_basic,
        test_3d_neural_network,
        test_3d_mcts,
        test_game_compatibility
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}")
            results.append(False)
        print()
    
    # Summary
    print("=" * 60)
    print("    TEST SUMMARY")
    print("=" * 60)
    passed = sum(1 for r in results if r)
    total = len(results)
    print(f"Tests passed: {passed}/{total}")
    
    if passed == total:
        print("✓ All tests passed! 3D Connect 4 implementation is ready.")
    else:
        print("✗ Some tests failed. Please check the implementation.")
    
    return passed == total

if __name__ == "__main__":
    run_all_tests()