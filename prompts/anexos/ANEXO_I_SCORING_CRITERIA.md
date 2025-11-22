# ANEXO I — GUIA DE AVALIAÇÃO PADRONIZADA (v5.3)

## Complete Q1-Q19 Deterministic Scoring Criteria

This document provides the complete, deterministic scoring criteria for all 19 questions in the Yudor rubric. Use these criteria to ensure consistency and objectivity in every analysis.

---

## TECHNIQUE (25 points max)

### Q1: Qualidade Jogadores-Chave (0-8)

**Fontes**: Transfermarkt (valor de mercado), SofaScore (rating médio), Flashscore (G/A stats)

**Critério Determinístico**:
1. Identifique Top 3 G/A + Top Defensor (4 jogadores)
2. Para cada jogador, calcule:
   - **Valor**: €50M+ = 2.0, €30-50M = 1.5, €15-30M = 1.0, <€15M = 0.5
   - **Rating**: >7.5 = +0.5, 7.0-7.5 = 0, <7.0 = -0.5
3. Some os pontos dos 4 jogadores e normalize:
   - **Total ≥ 10**: +8
   - **Total 8-9**: +6
   - **Total 6-7**: +3
   - **Total <6**: 0

**Exemplo**: Inter tem Lautaro (€80M, 7.6 rating = 2.5), Barella (€60M, 7.4 = 2.0), Çalhanoğlu (€25M, 7.3 = 1.5), Bastoni (€50M, 7.2 = 2.0) → Total = 8.0 → **+6**

---

### Q2: Poder Ofensivo (0-7)

**Fontes**: Flashscore (G/J), FotMob/SofaScore (xG)

**Critério**:
- **+7**: G/J > 2.0 E xG > 1.8
- **+5**: G/J 1.5-2.0 E xG 1.5-1.8
- **+4**: G/J 1.3-1.5 E xG 1.3-1.5
- **+2**: G/J ≈ 1.0 E xG ≈ 1.0
- **0**: G/J < 1.0 OU xG < 1.0

---

### Q3: Profundidade de Banco (0-5)

**Fontes**: Transfermarkt (squad list), Sports Mole (team news)

**Critério**:
- **+5**: Possui 2+ substitutos de qualidade em TODAS as posições-chave (ATK, MID, DEF)
- **+3**: Possui 1-2 substitutos de qualidade em 2 posições-chave
- **+1**: Possui 1 substituto de qualidade em 1 posição
- **0**: Banco fraco ou inexistente

**Qualidade = jogador com valor >€10M ou rating >6.8**

**Default**: +2 para top-6 teams, +1 para outros se dados incompletos

---

### Q4: Equilíbrio Defensivo (0-5)

**Fontes**: Flashscore (GA/J), FotMob/SofaScore (xGA)

**Critério**:
- **+5**: GA/J < 0.8 E xGA < 0.9
- **+3**: GA/J 0.8-1.2 E xGA 0.9-1.3
- **+1**: GA/J 1.2-1.5 E xGA 1.3-1.6
- **0**: GA/J > 1.5 OU xGA > 1.6

---

## TACTICS (25 points max)

### Q5: Classe do Técnico (0-7)

**Fontes**: UEFA Coefficient, Transfermarkt (histórico)

**Critério**:
- **+7**: Vencedor Champions League OU Top 5 técnicos da liga (ex: Guardiola, Ancelotti, Klopp)
- **+5**: Semifinalista Champions OU Top 10 técnicos
- **+4**: Experiência internacional (10+ anos)
- **+2**: Técnico consolidado na liga (5+ anos)
- **0**: Técnico novato (<2 anos) ou sem histórico relevante

**Default**: +2 se dados incompletos

---

### Q6: Estrutura vs. Estrutura (0-8) — MATRIZ TÁTICA

**Fontes**: Sports Mole (tactical preview), FotMob (formation stats)

**MATRIZ COMPLETA DE MATCHUPS**:

| Home \ Away | 4-3-3 Posse | 4-3-3 Press | 4-2-3-1 | 4-4-2 Compact | 3-5-2 Wide | 3-4-3 | 5-3-2 Def |
|:---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| **4-3-3 Posse** | 0/0 | +4/+4 | +2/+2 | +2/+6 | +6/+2 | +4/+4 | +2/+6 |
| **4-3-3 Press** | +4/+4 | 0/0 | +6/+2 | +4/+4 | +8/0 | +6/+2 | +4/+4 |
| **4-2-3-1** | +2/+2 | +2/+6 | 0/0 | +4/+4 | +4/+4 | +2/+2 | +2/+6 |
| **4-4-2 Compact** | +6/+2 | +4/+4 | +4/+4 | 0/0 | +4/+4 | +4/+4 | +6/+2 |
| **3-5-2 Wide** | +2/+6 | 0/+8 | +4/+4 | +4/+4 | 0/0 | +2/+6 | +4/+4 |
| **3-4-3** | +4/+4 | +2/+6 | +2/+2 | +4/+4 | +6/+2 | 0/0 | +4/+4 |
| **5-3-2 Def** | +6/+2 | +4/+4 | +6/+2 | +2/+6 | +4/+4 | +4/+4 | 0/0 |

**Como usar**:
1. Identifique formação provável de cada time (Sports Mole)
2. Localize a intersecção na matriz
3. Primeiro valor = Home score, Segundo valor = Away score

**Exemplo**: Inter (4-3-3 Press) vs Lazio (3-5-2 Wide) → Home: +8, Away: 0

**Default**: 0/0 se formações não confirmadas

---

### Q7: Transições (Def ↔ Ataque) (0-5)

**Fontes**: FotMob (counter-attack stats), SofaScore (pressing intensity)

**Critério**:
- **+5**: Pressing alto (PPDA <8) E contra-ataque letal (>0.3 xG/counter)
- **+3**: Pressing médio (PPDA 8-12) OU contra-ataque eficiente
- **+2**: Equilíbrio entre defesa e ataque
- **0**: Transições lentas (PPDA >15) E baixa eficiência

**Default**: +2 se dados incompletos

---

### Q8: Bolas Paradas (0-5)

**Fontes**: WhoScored, FotMob (set-piece stats)

**Critério**:
- **+5**: ≥25% dos gols vêm de BP E concede <10% dos gols em BP
- **+3**: 15-25% dos gols de BP OU defesa sólida em BP
- **+1**: Média (10-15% gols de BP)
- **0**: <10% gols de BP E concede >20% em BP

**Default**: +2 se dados incompletos

---

## MOTIVATION (17 points max)

### Q9: Must-Win (0-12) — REGRA DE CONFLITO ⚠️

**Fontes**: Tabela da liga, mídia local (Gazzetta, AS, GE)

**Critério Base**:
- **+12**: Decisivo para título, Z4 (rebaixamento), ou classificação europeia (últimas 5 rodadas)
- **+6**: Meta parcial (top 4, top 6)
- **0**: Meio de tabela sem objetivo claro

**⚠️ REGRA DE CONFLITO** (se ambos os times têm must-win):
1. Se **apenas 1 time** tem must-win → Aplica +12
2. Se **ambos** têm must-win E estão competindo pelo mesmo objetivo:
   - Time **atrás na tabela** → +12
   - Time **à frente na tabela** → +6
   - Se **empatados** na tabela → Ambos +9
3. Se **ambos** têm must-win mas objetivos diferentes (ex: um luta por título, outro contra Z4):
   - Ambos recebem +12 (não cancela)

**Exemplo 1**: Inter (1º, 75 pts) vs Napoli (2º, 73 pts) — Última rodada, disputa título
- Napoli (atrás): +12
- Inter (frente): +6

**Exemplo 2**: Real Madrid (3º, luta por Champions) vs Sevilla (18º, luta contra Z4)
- Real Madrid: +12 (Champions spot)
- Sevilla: +12 (Survival)

---

### Q10: Dérbi / Técnico Estreante / Vingança (0-5)

**Fontes**: Portais locais, Sports Mole (preview)

**Critério**:
- **+5**: Derby histórico (ex: Inter vs Milan, Barça vs Real, Boca vs River) OU estreia de técnico de alto perfil
- **+3**: Revanche de eliminação recente (Copa, playoffs)
- **+2**: Rivalidade regional
- **0**: Jogo normal

---

## FORM (8 points max)

### Q11: Forma Bruta (Últimos 5 Jogos) (0-4)

**Fontes**: Flashscore (results)

**Critério**:
- **+4**: ≥4 vitórias em 5 jogos
- **+3**: 3 vitórias
- **+2**: 2 vitórias
- **+1**: 1 vitória
- **0**: 0 vitórias

---

### Q12: Normalização da Forma (0-4)

**Fontes**: Transfermarkt (opponent rankings/value)

**Critério**: Ajuste baseado na qualidade dos oponentes enfrentados

1. Calcule valor médio dos oponentes (últimos 5 jogos):
   - **Top 6**: Valor médio >€400M
   - **Mid-table**: Valor médio €200-400M
   - **Bottom 6**: Valor médio <€200M

2. Ajuste:
   - **+4**: Venceu majoritariamente times Top 6
   - **+3**: Venceu times Top 6 + Mid-table
   - **+2**: Venceu times Mid-table
   - **+1**: Venceu times Bottom 6
   - **0**: Venceu poucos jogos ou apenas Bottom 6

**Default**: Q11 score - 1 se dados incompletos

---

## PERFORMANCE (10 points max)

### Q13: Delta xG (Real − Esperado) (0-5)

**Fontes**: Understat, FotMob (xG stats)

**Critério**:
- **+5**: xG > Gols Reais +0.4 (azar, tendência a reverter positivamente)
- **+3**: xG > Gols Reais +0.2
- **+2**: xG ≈ Gols Reais (±0.1)
- **+1**: Gols Reais > xG +0.2 (sorte)
- **0**: Gols Reais > xG +0.4 (muita sorte, insustentável)

**Lógica**: Times com xG superior aos gols reais estão criando chances e têm tendência de melhora.

---

### Q14: Qualidade da Atuação (0-5)

**Fontes**: SofaScore (average rating), FotMob (performance index)

**Critério**:
- **+5**: Média SofaScore (últimos 5j) ≥ 7.0 E xG superior ao oponente em ≥3 jogos
- **+3**: Média SofaScore 6.7-6.9 E xG superior em 2 jogos
- **+1**: Média SofaScore 6.5-6.7
- **0**: Média SofaScore < 6.5

---

## INJURIES (−12 penalty max)

### Q15: Ausência Jogador-Chave (0 ou −8)

**Fontes**: Transfermarkt (injuries), Sports Mole (team news)

**Critério**:
- **−8**: Jogador Top 3 G/A OU Defensor Top (identificado em Q1) está fora
- **0**: Todos jogadores-chave disponíveis

---

### Q16: Cluster Defensivo (0 ou −4)

**Fontes**: Sports Mole, Transfermarkt

**Critério**:
- **−4**: 2+ defensores titulares fora (incluindo GK)
- **0**: Defesa normal

---

## HOME/AWAY (40 points max total; normalize para 25 em Camada 2)

### Q17: Fortaleza Casa vs Fraqueza Fora (0-10)

**Fontes**: Flashscore (Home/Away tables, últimos 5 jogos)

**Critério**:
1. **Mandante**: Calcule vitórias em casa (últimos 5j)
2. **Visitante**: Calcule vitórias fora (últimos 5j)

**Mandante Score**:
- **≥4 vitórias em casa**: Base +6
- **3 vitórias em casa**: Base +4
- **2 vitórias em casa**: Base +2
- **<2 vitórias em casa**: Base 0

**Visitante Penalty**:
- **≤1 vitória fora**: +4 bonus para mandante
- **2 vitórias fora**: +2 bonus
- **≥3 vitórias fora**: 0 bonus

**Total Q17**: Base + Bonus (max 10)

**Exemplo**: Inter tem 4 vitórias em casa, Lazio tem 1 vitória fora → +6 (base) +4 (bonus) = **+10**

---

### Q18: H2H no Estádio (Últimos 3 Jogos) (0-5)

**Fontes**: Flashscore (H2H tab)

**Critério** (para mandante):
- **+5**: 3 vitórias nos últimos 3 H2H em casa
- **+3**: 2 vitórias
- **+1**: 1 vitória
- **0**: 0 vitórias

---

### Q19: Cenário Ruim Mandante (0 ou −25) ⚠️

**Fontes**: Flashscore (H2H histórico)

**Critério**:
- **−25**: Mandante perdeu ou empatou TODOS os últimos 3 H2H em casa
- **0**: Mandante tem pelo menos 1 vitória nos últimos 3 H2H

**⚠️ Este é um VETO forte.** Use com cautela.

---

## SUMMARY TABLE

| Category | Total Points | Questions |
|:---|:---:|:---|
| Technique | 25 | Q1-Q4 |
| Tactics | 25 | Q5-Q8 |
| Motivation | 17 | Q9-Q10 |
| Form | 8 | Q11-Q12 |
| Performance | 10 | Q13-Q14 |
| Injuries | −12 (penalty) | Q15-Q16 |
| Home/Away | 40 (normalize to 25) | Q17-Q19 |

---

## MISSING DATA PROTOCOL

**If ANY data source fails**:
1. Use defaults documented above
2. Document in analysis notes
3. Mark as "estimated" or "default"
4. NEVER leave a Q-score null - always provide a value

**Example documentation**:
```
Q3: No bench data from Transfermarkt - used +2 default for top-6 team
Q7: Pressing stats unavailable - inferred +3 from tactical preview
Q12: Opponent values unknown - used Q11 score - 1
```

---

*ANEXO I — Yudor System v5.3*
*Deterministic Scoring Criteria*
