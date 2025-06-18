import { useState, useEffect, useCallback } from 'react';
import type { GameState } from '../types/game';
import { api } from '../services/api';

interface UseAIPlayerOptions {
  enabled: boolean;
  aiPlayer: 'yellow' | 'red';
  difficulty?: 'easy' | 'medium' | 'hard';
}

export function useAIPlayer(
  gameState: GameState,
  makeMove: (column: number) => boolean,
  options: UseAIPlayerOptions
) {
  const [isThinking, setIsThinking] = useState(false);

  const makeAIMove = useCallback(async () => {
    if (!options.enabled || gameState.winner || gameState.isDraw) return;
    if (gameState.currentPlayer !== options.aiPlayer) return;

    setIsThinking(true);

    // Add delay for better UX
    await new Promise(resolve => setTimeout(resolve, 500));

    try {
      const response = await api.getAIMove(gameState.board, gameState.currentPlayer);
      makeMove(response.column);
    } catch (error) {
      console.error('AI move failed:', error);
    } finally {
      setIsThinking(false);
    }
  }, [gameState, makeMove, options]);

  useEffect(() => {
    makeAIMove();
  }, [gameState.currentPlayer, makeAIMove]);

  return { isThinking };
}