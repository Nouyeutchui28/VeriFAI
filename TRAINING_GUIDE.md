# TRAINING_GUIDE.md

This document provides a practical, reproducible training and alignment guide for creating a security-specialized LLM similar in behavior to the model used in VeriFAI LLM. This is an instructional guide you can follow to train or fine-tune an open or licensed base model; it does not claim the model in this repository was trained here.

## Overview
Goal: Fine-tune or instruction-align a base LLM (e.g., LLaMA-family checkpoint) to act as a Senior Security Researcher focused on exploit reasoning and remediation generation.

Sections:
- Data and preprocessing
- Model choices and compute
- Training recipes (objective, loss functions, optimizer)
- Alignment & instruction tuning
- Evaluation and metrics
- Practical commands and reproducible config

---

## 1. Data and Preprocessing

1. Curated Security Corpus
- Public vulnerability writeups (CVE, exploit-db), secure coding guides, OWASP documentation.
- Code examples: vulnerable and fixed code pairs across languages (Python, JS, Java, Go, SQL).
- Semgrep rules and annotations (rule_id, pattern, severity).

2. Constructed Training Examples
- "Find-and-fix" pairs: (vulnerable_code, explanation, unified-diff_patch).
- Chain-of-Thought style annotations: stepwise reasoning traces that show exploit logic.
- Instruction-response examples for remediation generation.

3. Preprocessing steps
- Normalize line endings, tokenize with same tokenizer as base model.
- For code: preserve indentation, use special tokens for file boundaries: <FILE_START>, <FILE_END>.
- Chunking: newline-aware sliding window with overlap (e.g., 2k tokens, 200 token stride).

---

## 2. Model Choice & Compute
- Start from a permissively licensed base model (e.g., LLaMA-derived or Llama 2/3 licensed checkpoint you have rights to use).
- GPU recommendation: 8x A100 40GB or equivalent for medium-sized fine-tune (7B–13B models). For larger models, scale accordingly.
- Mixed precision training: use AMP (fp16 or bfloat16) and ZeRO optimizer for memory scaling.

---

## 3. Training Recipe (Objectives & Equations)

Notation:
- x: input tokens
- y: target tokens (response or patch)
- θ: model parameters
- p_θ(y|x): model probability of y given x
- L_MLE: maximum likelihood (cross-entropy) loss
- L_KD: optional knowledge distillation loss from a teacher model
- L_align: alignment loss for instruction-following behavior
- λ_k: scalar weights for loss terms

1) MLE (Cross-entropy) loss

L_MLE(θ) = - ∑_{(x,y)∈D} log p_θ(y|x)

2) Knowledge Distillation (optional)

Using a stronger teacher with probabilities q(y|x):
L_KD(θ) = - ∑_{(x)∈D} ∑_{t=1}^T q(y_t|x) log p_θ(y_t|x)

3) Alignment Loss (Instruction-following / RLHF style)

For instruction alignment, use a preference model or reward r(x,y) and optimize via proximal policy optimization (PPO) or direct preference optimization.

Policy gradient objective (PPO simplified):

J(θ) = E_{y∼p_θ(.|x)} [ r(x,y) ]

Using PPO surrogate loss with importance sampling ratio r_t(θ) = p_θ(y_t|x_t) / p_{θ_old}(y_t|x_t):

L_PPO(θ) = - E_t [ min( r_t(θ) A_t, clip(r_t(θ), 1-ε, 1+ε) A_t ) ]

where A_t is the advantage estimate from the reward model.

4) Full combined objective

L(θ) = L_MLE(θ) + λ_KD L_KD(θ) - λ_PPO J(θ) + λ_align L_align(θ)

Choose λ weights empirically.

---

## 4. Alignment & Instruction Tuning Steps
1. Supervised Fine-tuning (SFT)
- Train on instruction-response pairs (find-and-fix, reasoning traces) with L_MLE.
- Typical hyperparams: epochs 1–3, batch size 128 tokens per device, LR 1e-5–3e-5 for 7B model.

2. Reward Model (RM)
- Collect human (or expert) preference data: rank multiple candidate model responses.
- Train a scalar reward model r_φ(x,y) via regression/classification on rankings.

3. Reinforcement Tuning (PPO)
- Use RM to score generations, apply PPO to optimize policy for higher reward while keeping proximity to SFT policy.

4. Safety Filters
- Hard-coded checks for dangerous outputs; ensure patches are syntactically safe.

---

## 5. Evaluation & Metrics
- Precision/Recall on a labeled vulnerability corpus (per-vuln-type).
- False positive rate measured by manual review on sampled outputs.
- Patch correctness: automated tests asserting patched code passes original unit tests.
- Calibration: expected calibration error for model confidences.

---

## 6. Example Commands (Hugging Face Transformers / PEFT style)

Below are simplified commands for SFT using Hugging Face + DeepSpeed/Accelerate. Adjust config for your infra.

1) Install:

```bash
python -m pip install transformers accelerate datasets deepspeed peft
```

2) Convert data to JSONL with keys `instruction`, `input`, `output` and use an SFT script. Example invocation:

```bash
python sft_train.py \
  --model_name_or_path /path/to/base-model \
  --train_file data/train.jsonl \
  --per_device_train_batch_size 1 \
  --gradient_accumulation_steps 8 \
  --num_train_epochs 2 \
  --learning_rate 2e-5 \
  --fp16 \
  --output_dir /path/to/out-sft
```

3) Reward model training (simplified):

```bash
python train_reward_model.py --data reward_pairs.jsonl --output reward-model
```

4) PPO tuning (using trl):

```bash
python ppo_train.py --sft_model /path/to/out-sft --reward_model /path/to/reward-model --out /path/to/out-ppo
```

---

## 7. Reproducibility Checklist
- Record dataset provenance, licenses, and filtering steps.
- Save training logs, checkpoints, and random seeds.
- Keep compute details (instance types, counts, wall-clock hours).
- Save reward-model artifacts and preference data.

---

## 8. Math Appendix (Key Equations)

Cross-entropy (token-level):

$$
L_{CE} = -\sum_{t=1}^T \log p_\theta(y_t|x, y_{<t})
$$

Policy gradient objective (REINFORCE style):

$$
\nabla_\theta J(\theta) = E_{y\sim p_\theta} \left[ r(x,y) \nabla_\theta \log p_\theta(y|x) \right]
$$

PPO surrogate loss fragment:

$$
L^{CLIP}(\theta) = -E_t \left[ \min\left(r_t(\theta) A_t, \mathrm{clip}(r_t(\theta), 1-\epsilon, 1+\epsilon) A_t \right) \right]
$$

Distillation loss (soft labels):

$$
L_{KD} = -\tau^2 \sum_{t} q(y_t|x) \log p_\theta(y_t|x)
$$

where $\tau$ is temperature for softening logits.

---

## 9. Templates & Artifacts to Keep
- `data/` raw and processed
- `checkpoints/` SFT and PPO
- `rewards/` labeled preferences and reward-model
- `training_config.yaml` full hyperparameters

---

## 10. Notes on Claims and Transparency
If you publish or claim a model was "self-trained":
- Provide dataset provenance and compute logs.
- Share or archive model checkpoints or at minimum training metadata.
- Do not claim compliance or ownership of base models you do not legally own.

---

End of guide.
