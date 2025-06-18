import axios from 'axios';
import type { Move, Player } from '../types/game';

const API_BASE_URL = 'http://localhost:5000';

export interface AIResponse {
  column: number;
  evaluation: number;
}

export const api = {
  getAIMove: async (board: Player[][], currentPlayer: Player): Promise<AIResponse> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/ai-move`, {
        board,
        currentPlayer
      });
      return response.data;
    } catch (error) {
      console.error('Error getting AI move:', error);
      // Fallback to random valid move
      const validColumns = board.map((col, idx) => col[col.length - 1] === null ? idx : -1)
        .filter(idx => idx !== -1);
      const randomColumn = validColumns[Math.floor(Math.random() * validColumns.length)];
      return { column: randomColumn, evaluation: 0 };
    }
  },

  validateMove: async (board: Player[][], move: Move): Promise<boolean> => {
    try {
      const response = await axios.post(`${API_BASE_URL}/validate-move`, {
        board,
        move
      });
      return response.data.valid;
    } catch (error) {
      console.error('Error validating move:', error);
      // Fallback to local validation
      return board[move.column][board[move.column].length - 1] === null;
    }
  }
};