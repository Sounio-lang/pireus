# PIREUS Marco M7: Autonomous Operator Exploration & Scaled Foundry Atlas

Este diretório contém os resultados da exploração autônoma exaustiva do espaço quociente $GL(4,2) \times C_2$
através de todas as $2^{16} = 65.536$ matrizes de fase bilinear em $\mathbb{F}_2^{4 \times 4}$ (kind=2).

## 1. Censo Exaustivo de Álgebras de Fase Bilinear ($N = 65.536$)

A gramática de operadores convolucionais torcidos por fase bilinear atua na base $e_i, e_j$ ($0 \le i, j \le 15$):
$$e_i \star e_j = \sigma_B(i, j) \, e_{i \oplus j}, \quad \sigma_B(i, j) = \text{cd\_sigma}(i, j) \cdot (-1)^{i^T B j}$$

### Partição Estrutural
- **Distribuição de Posto em $\mathbb{F}_2$**:
  - Posto 0: 1 (matriz nula)
  - Posto 1: 225
  - Posto 2: 7350
  - Posto 3: 37800
  - Posto 4 ($GL(4,2)$ invertíveis): 20160
  - Total: 65.536 matrizes
- **Tipos de Formas Bilineares**:
  - Simétricas ($B = B^T$): 1024 matrizes ($2^{10} = 1024$)
  - Alternantes / Skew-symmetric ($B = B^T$ e $\text{diag}(B) = 0$): 64 matrizes ($2^6 = 64$)
  - Gerais: 64512 matrizes
- **Métricas de Defeito**:
  - **Defeito do Associador** $D_{assoc}(B) = \sum_{i,j,k} |(e_i \star e_j) \star e_k - e_i \star (e_j \star e_k)|$:
    - Identicamente igual a **3696** (1848 componentes booleanas) para todas as 65.536 fases.
    - **Teorema de Preservação**: Toda forma bilinear $b_B(i, j) = i^T B j$ é um 2-cociclo de grupo sobre $\mathbb{F}_2^4$:
      $$b_B(i, j) \oplus b_B(i \oplus j, k) \oplus b_B(j, k) \oplus b_B(i, j \oplus k) = 0$$
      Portanto, a torção bilinear preserva exatamente o defeito associativo da álgebra de Cayley-Dickson de base.
  - **Defeito do Comutador** $D_{comm}(B) = \sum_{i,j} [\sigma_B(i, j) \ne \sigma_B(j, i)]$:
    - Depende estritamente da parte alternante $A = B \oplus B^T \in \mathbb{F}_2^{4 \times 4}$:
    - Defeito 90: 28672 operadores (28 partes alternantes)
    - Defeito 114: 35840 operadores (35 partes alternantes)
    - Defeito 210 (Cayley-Dickson padrão): 1024 operadores (1 parte alternante nula)

## 2. Quociente de Gauge e Decomposição em Órbitas de $GL(4,2) \times C_2$

- **Fibras de Gauge**: As 65.536 matrizes projetam-se em $2^{10} = 1024$ códigos quadráticos $Q_B(x) = x^T B x$, cada uma com fibra exata de $2^6 = 64$ matrizes geradas pelo subespaço de cobordos alternantes.
- **Ações Admitidas**: Das 40.320 ações de $GL(4,2) \times C_2$, exatamente **336** (168 sem troca de operandos, 168 com troca) estabilizam a família de Cayley-Dickson módulo cobordo.
- **Classes Semânticas de Órbita**: As 336 ações particionam os 1024 códigos quadráticos em exatamente **32 classes semânticas exatas**.
- **Cobertura de Atlas**:
  - Classes visitadas no atlas M5: 12 classes ([0, 3, 4, 10, 13, 16, 18, 21, 24, 25, 26, 27])
  - Classes **inéditas (unvisited)** descobertas no M7: 20 classes ([1, 2, 5, 6, 7, 8, 9, 11, 12, 14, 15, 17, 19, 20, 22, 23, 28, 29, 30, 31])

## 3. Lote M7 de Operadores Admitidos e Avaliação GRPO

Foram selecionados 16 operadores representativos de classes inéditas e sintetizados formalmente:
- **Taxa de Admissão**: 16/16 (100% ADMIT pelo oráculo nativo Sounio `/tmp/pireus_admission_engine.elf`).
- **Recompensa Média Registrada**: 1.0. O lote foi pré-filtrado para classes não visitadas e cada termo é constante ($R_{syntax}=0.1$, $R_{admission}=0.4$, $R_{novelty}=0.5$), então o desvio é 0 e toda vantagem GRPO registrada é 0. Isso não é um sinal grupo-relativo.
- **Kernels PTX Materializados**: 16 kernels `sm_121` com tabelas de sinais de fase bilinear calculadas formalmente pelo pipeline nativo do Sounio.

| Índice | Fase | Classe | Defeito Comutador | $Q_{min}$ | Operadores na Classe | Decisão | Recompensa | Vantagem GRPO | Kernel PTX |
|---|---|---|---|---|---|---|---|---|---|
| 000 | 32841 | 29 | 90 | 201 | 5376 | ADMIT | 1.00 | 0.0000 | `000.proposal.ptx` |
| 001 | 33896 | 30 | 90 | 206 | 1792 | ADMIT | 1.00 | 0.0000 | `001.proposal.ptx` |
| 002 | 32840 | 28 | 90 | 200 | 5376 | ADMIT | 1.00 | 0.0000 | `002.proposal.ptx` |
| 003 | 33897 | 31 | 90 | 207 | 1792 | ADMIT | 1.00 | 0.0000 | `003.proposal.ptx` |
| 004 | 35 | 5 | 114 | 19 | 448 | ADMIT | 1.00 | 0.0000 | `004.proposal.ptx` |
| 005 | 32777 | 14 | 114 | 73 | 448 | ADMIT | 1.00 | 0.0000 | `005.proposal.ptx` |
| 006 | 32811 | 22 | 114 | 91 | 1344 | ADMIT | 1.00 | 0.0000 | `006.proposal.ptx` |
| 007 | 36 | 6 | 114 | 20 | 1792 | ADMIT | 1.00 | 0.0000 | `007.proposal.ptx` |
| 008 | 32770 | 7 | 114 | 24 | 1344 | ADMIT | 1.00 | 0.0000 | `008.proposal.ptx` |
| 009 | 32803 | 8 | 114 | 27 | 448 | ADMIT | 1.00 | 0.0000 | `009.proposal.ptx` |
| 010 | 32804 | 9 | 114 | 28 | 1792 | ADMIT | 1.00 | 0.0000 | `010.proposal.ptx` |
| 011 | 40 | 12 | 114 | 66 | 2688 | ADMIT | 1.00 | 0.0000 | `011.proposal.ptx` |
| 012 | 32808 | 15 | 114 | 74 | 2688 | ADMIT | 1.00 | 0.0000 | `012.proposal.ptx` |
| 013 | 42 | 17 | 114 | 82 | 1344 | ADMIT | 1.00 | 0.0000 | `013.proposal.ptx` |
| 014 | 44 | 19 | 114 | 84 | 5376 | ADMIT | 1.00 | 0.0000 | `014.proposal.ptx` |
| 015 | 32778 | 20 | 114 | 88 | 2688 | ADMIT | 1.00 | 0.0000 | `015.proposal.ptx` |

## 4. Ordem e Rigor Formal
Em estrita conformidade com as invariantes do Sounio:
- A autoridade semântica de admissão pertence exclusivamente ao executável nativo Sounio compilado.
- Os 16 arquivos `.ptx` são fontes SM121 emitidas pelo pipeline nativo. Este diretório não contém receipt de carga, lançamento ou comparação numérica em GPU.
