# Yudor Model Data Schema

This document defines the data schema for the new `yudor_model`. A structured and unified data schema is the foundation for building a robust and accurate predictive model. The following tables will be the "single source of truth" for all data used in the model.

## `matches` table

This table contains all match-level data, including results, statistics, and betting odds.

| Column Name          | Data Type | Description                                                                 | Example                               | Source(s)                                   |
| -------------------- | --------- | --------------------------------------------------------------------------- | ------------------------------------- | ------------------------------------------- |
| `match_id`           | `string`  | Unique identifier for the match.                                            | `PL_20251124_MUN_EVE`                 | Generated                                   |
| `date`               | `date`    | Date of the match.                                                          | `2025-11-24`                          | `scraped_matches.json`                      |
| `league`             | `string`  | The league the match belongs to.                                            | `Premier League`                      | `scraped_matches.json`                      |
| `home_team_id`       | `string`  | Foreign key to the `teams` table.                                           | `MUN`                                 | Generated/mapped from `scraped_matches.json` |
| `away_team_id`       | `string`  | Foreign key to the `teams` table.                                           | `EVE`                                 | Generated/mapped from `scraped_matches.json` |
| `home_goals`         | `integer` | Goals scored by the home team.                                              | `2`                                   | Scraped from sources like Sofascore, etc.   |
| `away_goals`         | `integer` | Goals scored by the away team.                                              | `1`                                   | Scraped from sources like Sofascore, etc.   |
| `home_xg`            | `float`   | Expected goals for the home team.                                           | `2.1`                                 | Understat, FBref                            |
| `away_xg`            | `float`   | Expected goals for the away team.                                           | `0.8`                                 | Understat, FBref                            |
| `home_possession`    | `integer` | Ball possession for the home team (%).                                      | `65`                                  | Sofascore, FBref                            |
| `away_possession`    | `integer` | Ball possession for the away team (%).                                      | `35`                                  | Sofascore, FBref                            |
| `home_shots`         | `integer` | Total shots for the home team.                                              | `15`                                  | Sofascore, FBref                            |
| `away_shots`         | `integer` | Total shots for the away team.                                              | `8`                                   | Sofascore, FBref                            |
| `home_shots_on_target` | `integer` | Shots on target for the home team.                                          | `6`                                   | Sofascore, FBref                            |
| `away_shots_on_target` | `integer` | Shots on target for the away team.                                          | `2`                                   | Sofascore, FBref                            |
| `odds_home_win`      | `float`   | Betting odds for a home win.                                                | `1.50`                                | Betfair, other bookmakers                   |
| `odds_draw`          | `float`   | Betting odds for a draw.                                                    | `4.00`                                | Betfair, other bookmakers                   |
| `odds_away_win`      | `float`   | Betting odds for an away win.                                               | `6.50`                                | Betfair, other bookmakers                   |
| `odds_ah_line`       | `float`   | Asian Handicap line.                                                        | `-1.5`                                | Betfair, other bookmakers                   |
| `odds_ah_home`       | `float`   | Asian Handicap odds for the home team.                                      | `1.95`                                | Betfair, other bookmakers                   |
| `odds_ah_away`       | `float`   | Asian Handicap odds for the away team.                                      | `1.95`                                | Betfair, other bookmakers                   |

## `teams` table

This table stores team-level information.

| Column Name    | Data Type | Description                                 | Example             | Source(s)      |
| -------------- | --------- | ------------------------------------------- | ------------------- | -------------- |
| `team_id`      | `string`  | Unique identifier for the team.             | `MUN`               | Generated      |
| `team_name`    | `string`  | Full name of the team.                      | `Manchester United` | Sofascore, etc. |
| `league`       | `string`  | The primary league the team plays in.       | `Premier League`    | Sofascore, etc. |
| `current_elo`  | `float`   | The team's current Elo rating.              | `1850.0`            | Calculated     |
| `market_value` | `float`   | Total market value of the squad (in EUR M). | `850.5`             | Transfermarkt  |
