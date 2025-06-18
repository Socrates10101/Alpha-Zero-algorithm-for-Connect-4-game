# Connect 4 3D UI

立体的なThree.jsベースのConnect 4ゲームUIです。

## 機能

- **3Dビジュアライゼーション**: Three.jsを使用した立体的なゲームボード
- **アニメーション**: ピースの落下アニメーションと勝利時のエフェクト
- **ゲームモード**: 
  - Player vs Player (対人戦)
  - Player vs AI (AI対戦)
- **AIプレイヤー**: 既存のAlpha Zero AIモデルとの連携

## セットアップ

### フロントエンド

```bash
cd connect4-3d-ui
npm install
npm run dev
```

### バックエンド（AI機能用）

```bash
python api_server.py
```

## 使い方

1. フロントエンドサーバーを起動（http://localhost:5173）
2. AI対戦を使用する場合は、バックエンドサーバーも起動（http://localhost:5000）
3. ゲームモードを選択（PvPまたはPvE）
4. ボード上のカラムをクリックしてピースを配置

## 技術スタック

- **フロントエンド**: React, TypeScript, Three.js (@react-three/fiber)
- **バックエンド**: Python Flask, PyTorch
- **AI**: Alpha Zero algorithm (MCTS + Neural Network)