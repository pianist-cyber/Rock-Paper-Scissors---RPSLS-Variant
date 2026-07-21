# Rock Paper Scissors — Custom Variant (v1 Rules)

## 1. Match Setup
- Two players.
- Before starting, agree on a **target score**: **5, 10, or 25 points**.
- First player to reach or exceed the target wins the match.

## 2. Gestures
Five gestures, standard Rock-Paper-Scissors-Lizard-Spock logic — each gesture beats two others:

- Rock beats Scissors, Lizard
- Paper beats Rock, Spock
- Scissors beats Paper, Lizard
- Lizard beats Spock, Paper
- Spock beats Scissors, Rock

## 3. Gesture Properties

| Gesture | Category | Flavor traits |
|---|---|---|
| Rock | Aggressive | Blunt, Sturdy |
| Scissors | Aggressive | Sharp, Precise |
| Paper | Defensive | Adaptive, Patient |
| Spock | Defensive | Calculated, Logical |
| Lizard | Neutral | Sly, Opportunistic |

## 4. Choose a Playstyle
Each player picks one playstyle for the whole match. Playstyle determines base points on a win:

| Playstyle | Win vs Aggressive move | Win vs Defensive move | Win vs Neutral move (Lizard) | Draw |
|---|---|---|---|---|
| **Rogue** | 2 pts | 0 pts | 1 pt | 0 |
| **Defensive** | 0 pts | 2 pts | 1 pt | 0 |
| **Calm** | 1 pt | 1 pt | 1 pt | 0 |

## 5. Playstyle Nerf (Rogue / Defensive penalty)
Rogue and Defensive both carry a downside to offset their higher upside:

- **Rogue** loses 1 point if beaten by a **Defensive**-category gesture (Paper or Spock).
- **Defensive** loses 1 point if beaten by an **Aggressive**-category gesture (Rock or Scissors).
- Losing to a **Neutral** gesture (Lizard) never triggers this penalty, for either playstyle.
- **Calm** never takes this penalty, win or lose.
- A player's total match score can never drop below **0** — clamp at 0 if a penalty would take them lower.
- **Bonus lockout:** whenever this nerf triggers, the winner scores a **plain win only** — base playstyle points, no Affinity Clash and no Momentum bonus, even if either would otherwise apply.

## 6. Affinity Clash (thematic bonus)
Exactly five of the ten win-pairs carry a fixed **+1 bonus** on top of the base win:

| Winning move | Beats | Flavor reasoning | Bonus |
|---|---|---|---|
| Scissors | Paper | Precise cuts through Patient material | +1 |
| Paper | Rock | Adaptive smothers Blunt force | +1 |
| Rock | Lizard | Blunt crushes Sly footwork | +1 |
| Lizard | Spock | Sly poison slips past Calculated defense | +1 |
| Spock | Scissors | Logical outmaneuvers Sharp precision | +1 |

The other five wins (Scissors–Lizard, Lizard–Paper, Paper–Spock, Spock–Rock, Rock–Scissors) get no Affinity bonus. Fixed list — no live calculation needed.

*(Affinity Clash never applies on a nerf round — see Section 5's bonus lockout.)*

## 7. Modifiers

**Momentum**
- Playing the same gesture as your own previous throw builds a charge stack (max 2).
- At 2 stacks, your *next win* with that gesture scores an additional **+1**.
- Stacks reset to 0 if you play a different gesture than your last throw.
- *(Momentum never applies on a nerf round — see Section 5's bonus lockout.)*

**Feint Token**
- Each player starts the match with **2 tokens**.
- Before revealing your gesture each round, you may silently spend one token.
- If you lose that round after spending a token, the result downgrades to a **draw** (0 points, no bonuses, no nerf penalty). Tokens don't refund.
- If you win or draw the round, the spent token is simply used up with no extra effect.

## 8. Round Resolution Order
1. Both players silently declare Feint Token use (or not).
2. Both players reveal their gesture.
3. Determine win / loss / draw (Section 2).
4. **Draw** → 0 points for both, no further steps.
5. **Feint-saved loss** (loser spent a token) → downgrade to a draw. 0 points, no nerf, round ends.
6. **Unsaved loss** → check whether the Playstyle Nerf applies (Section 5): is the loser Rogue beaten by a Defensive gesture, or Defensive beaten by an Aggressive gesture?
   - **If yes (nerf round):** winner scores plain playstyle base points only (no Affinity, no Momentum). Loser takes -1 (clamped at 0). Round ends.
   - **If no:** proceed to step 7 for the winner's score.
7. **Win scoring** (non-nerf rounds):
   - Start with playstyle base score (Section 4).
   - Add Affinity Clash +1 if the pair is on the list (Section 6).
   - Add Momentum +1 if the winner had 2 stacks on the winning gesture (Section 7).
   - **5-point matches:** cap total bonuses at +1 (only the higher of Affinity/Momentum counts, not both).
   - **10 or 25-point matches:** bonuses stack freely.
8. Update Momentum stacks for both players based on the gestures just played.
9. Check for match end (target score reached).

## 9. Quick Reference — Max Round Scores
- Base win: 1–2 pts (playstyle dependent)
- + Affinity Clash: +1
- + Momentum: +1
- **5-pt matches:** max 3 pts/round (base + 1 capped bonus)
- **10/25-pt matches:** max 4 pts/round (base + both bonuses stacked)
- **Nerf rounds:** winner capped at plain base (1–2 pts), loser takes -1 → max net swing 3 points (e.g., Defensive's plain 2-pt win vs. Rogue's -1)