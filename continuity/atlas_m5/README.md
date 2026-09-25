# PIREUS Marco M5 & M6: Atlas de Novos Operadores e Avaliação GRPO

Este diretório contém os resultados da exploração da álgebra de convolução com torção por fase bilinear (kind=2) em Z^{16 x 16 x 16}, governada pelo quociente de calibre GL(4,2) x C_2.

## 1. Operadores Convolucionais com Torção por Fase Bilinear
Para cada elemento da base e_i, e_j (0 <= i, j <= 15), o produto é definido por:
    e_i * e_j = sigma_B(i, j) * e_{i XOR j}
onde:
    sigma_B(i, j) = cd_sigma(i, j) * (-1)^(i^T * B * j)
com B em F_2^{4x4} codificada pelo inteiro `phase` em [0, 65535] cujo bit (4*i + j) determina B_{ij}.

## 2. Conteúdo do Lote
- `context.json`: Contexto ontológico formal do hardware alvo (DGX Spark GB10 SM121).
- `*.proposal.json`: Propostas estruturadas de operadores e esquemas de lane schedule / unroll.
- `*.proposal.ptx`: Kernels de GPU PTX nativos gerados pelo materializador formal Sounio (`materialize_ptx.sio`), contendo a tabela de sinais `.const .align 4 .u32 pireus_signs[16]`.
- `grpo_atlas_batch_results.json`: Avaliação exata de recompensas R em [0.0, 1.0] e vantagens relativas de grupo A_i computadas pelo motor verificável Sounio sem oráculo neural (`grpo_reward_engine.py`).

## 3. Censo de Admissão Formal
- Total de operadores avaliados: 16
- Total admitido pelo oráculo Sounio: 16 (100%)
- Total de tensores únicos na álgebra: 16
- Recompensa média do grupo: 0.975
