---
title: "Why Compression Is Prediction: The Information-Theoretic View of LLMs"
date: 2026-08-12T13:01:55+00:00
tags:
  - llm
  - compression
  - information-theory
  - next-token-prediction
  - language-models
  - machine-learning
  - scaling-laws
description: "Compression is prediction: an LLM that predicts the next token is secretly a world-class data compressor, and the reverse is true too."
draft: false
cover:
  image: "/images/compression-is-prediction-llm-guide-2026.png"
  alt: "Why Compression Is Prediction: The Information-Theoretic View of LLMs"
  relative: false
schema: "schema-compression-is-prediction-llm-guide-2026"
---

Compression is prediction, and prediction is compression: these are two sides of the same information-theoretic coin. Any model that accurately predicts the next token can be turned into a lossless data compressor, and any compressor can be turned into a generative model. This guide explains why that equivalence holds, how DeepMind and Meta proved it in 2023, and why it reframes how you should think about large language models.

## What Does It Mean That Compression Is Prediction?

Compression is prediction because a good predictor implicitly assigns low code lengths to likely sequences, which is exactly what a compressor does. When you predict "the" follows "of the", you are acting like an entropy coder that gives "the" a short code because it is probable. The tighter your predictions match the real distribution of data, the fewer bits you need to store that data.

The reverse is the deeper insight. If a program can compress a corpus to a small size, then it has extracted the statistical regularities in that corpus — the same regularities that let it predict what comes next. A file that compresses well is a file whose next symbols you can guess well. This is why researchers call language modeling "implicit compression" of the training distribution.

## The Information-Theoretic Core: Entropy, Probability, and Code Length

Claude Shannon's information theory gives the exact mathematical link. The entropy of a source, measured in bits, is the minimum average number of bits needed to encode each symbol from that source:

**H = −Σ p(x) log₂ p(x)**

The key practical result is that the optimal code assigns shorter code lengths to more probable symbols. This is the principle behind entropy coding — Huffman coding and arithmetic coding both do exactly this. If a symbol appears with probability p, its optimal code length is approximately −log₂(p) bits.

Here is where prediction enters. When a model predicts the probability of the next token, it is estimating p for each candidate symbol. A well-calibrated language model naturally assigns shorter codes to tokens it thinks are likely, and longer codes to surprising ones. Feed those probabilities into an arithmetic coder and you have converted prediction into lossless compression. The better the predictions, the shorter the compressed output.

This is not an analogy; it is a theorem. Shannon showed in 1948 that there is no way to compress below entropy on average, and that entropy-coding schemes can approach that limit arbitrarily closely given accurate probabilities.

## The Prediction–Compression Equivalence (and the DeepMind/Meta Result)

The formal equivalence between prediction and compression is a long-established result in information theory: predictive models can be transformed into lossless compressors, and vice versa. The 2023 paper *Language Modeling Is Compression* (DeepMind/Meta, arXiv 2309.10668) turned this abstract theorem into a striking empirical demonstration.

The researchers took large language models that were trained only to predict the next token — nothing else — and used them as compressors on data they had never seen and were not specifically trained on. Because arithmetic coding can consume model probabilities as a prior, a language model can be plugged directly into an arithmetic coder to compress arbitrary sequences.

The results were remarkable. A Chinchilla 70B model, trained mostly on text, compressed ImageNet image patches to **43.4%** of their raw size — beating PNG, the purpose-built image codec, which achieved only **58.5%**. On audio, the same model compressed LibriSpeech to **16.4%** of raw size, beating FLAC at **30.3%**. A text-trained model outperformed domain-specific codecs on images and audio it was never trained on.

| Data type | Chinchilla 70B | Domain codec | Codec result |
|-----------|---------------|--------------|--------------|
| ImageNet patches | 43.4% of raw | PNG | 58.5% of raw |
| LibriSpeech audio | 16.4% of raw | FLAC | 30.3% of raw |

The paper's conclusion is a powerful statement of the compression-is-prediction thesis: LLMs are not merely text statistics learners but general-purpose predictors, and their ability to compress across modalities is direct evidence that they capture general predictive structure.

## How an LLM "Compresses" the World: Training as Implicit Compression

You can think of every training run as a search for a compressed representation of the training distribution. The language model's weights, which might occupy a few gigabytes, encode statistical knowledge distilled from terabytes of text. That is compression on an enormous scale: the model is a lossy, learned codebook that captures the regularities of human language.

The framing explains a counter-intuitive fact: the model does not memorize the data; it summarizes it. A 70-billion-parameter model trained on trillions of tokens cannot possibly store every string. Instead, it stores the predictive patterns — which is exactly what a compression algorithm stores. What it cannot predict well, it must store with more detail or fail to reproduce.

This is why larger models compress better. A bigger model has more capacity to capture subtle predictive regularities, which shows up in information-theoretic terms as better compression of the training distribution. The connection to scaling laws is direct: as models scale, their ability to predict (and hence compress) improves, following the smooth power-law curves that scaling-law research has documented.

## Cross-Modal Evidence: Beating PNG and FLAC With a Text-Trained Model

The most surprising part of the DeepMind/Meta result is the cross-modal generalization. Chinchilla 70B compressed ImageNet patches and LibriSpeech audio better than codecs designed specifically for those modalities, despite being trained almost entirely on text.

Why does this matter? A model that only learned surface text statistics — common word pairs, punctuation rules — would fail completely on images and raw audio, which share no symbols with text. The fact that it succeeds suggests the model learned something more general: a predictive model of the world that transcends the token modality.

Compressing an image patch or an audio segment well means the model has a good probabilistic model of what images and sounds are like, not just what words look like. This is evidence that next-token prediction, far from being a narrow task, forces the model to learn deep structure about how the world generates data. The compressor's loss, measured in bits, is a direct, objective measure of how much the model "understands" the source.

## The Gzip Surprise: Zero-Parameter Compression as Understanding

The compression-is-prediction thesis does not require a billion-parameter model. A 2022 paper, *Less Is More: Parameter-Free Text Classification with Gzip* (Jiang et al., arXiv 2212.09410), showed that a simple string compressor plus a nearest-neighbor classifier can rival trained models.

The approach uses Normalized Compression Distance (NCD): the compressed size of two documents concatenated, minus their individual compressed sizes, normalized. Documents that share a lot of statistical structure compress well together, indicating they are semantically similar. Gzip captures word and phrase repetition — a proxy for topical overlap.

The results were striking: with zero parameters and zero training, gzip + kNN achieved state-of-the-art accuracy on several text classification benchmarks (on 5 of 12 benchmarks in the original study), beating methods that required full training runs. The practical lesson is that compression distance IS a form of understanding. If a compressor finds two documents similar, it is capturing genuine semantic overlap without any learned representations at all.

| Method | Parameters | Training | Benchmark performance |
|--------|-----------|----------|----------------------|
| Gzip + kNN | 0 | None | SOTA on 5 of 12 benchmarks |
| TF-IDF + classifier | Small | Required | Beaten by gzip on several |
| Trained embeddings | Large | Required | Beaten by gzip on several |

## What This Reveals About Scaling Laws, Tokenization, and In-Context Learning

Viewing LLMs as compressors clarifies three phenomena that otherwise look mysterious.

**Scaling laws.** If training is compression, then the scaling laws are compression curves. Larger models and more data compress the training distribution to fewer effective bits, which is why loss (a surrogate for compression) falls on predictable power laws. The compression viewpoint offers a principled reason why the curves are smooth and why diminishing returns appear.

**Tokenization.** Tokenizers are themselves a form of compression — they map text to a vocabulary of subword units to reduce sequence length. The compression lens shows why subword tokenization works: frequent word parts get short tokens, echoing the entropy-coding principle of assigning short codes to probable symbols. Better tokenizers are better compressors of the text stream.

**In-context learning.** When a model does a task in-context, it is effectively adapting its conditional distribution to the new examples in its context window. The compression framing treats this as online compression: the model uses the examples to predict (and compress) subsequent data more efficiently. This connects in-context learning to the same predictive machinery that drives compression.

## From Theory to Practice: Quantization and Real-World LLM Compression

The information-theoretic lens is not just academic; it motivates the practical techniques used to shrink deployed models.

**Quantization** reduces the number of bits per weight (from 16-bit to 8-bit, 4-bit, or even lower). From a compression viewpoint, this is lossy compression of the model's learned representation. The surprise is how well it works: models tolerate aggressive quantization because the weights contain redundant statistical structure — the same redundancy a compressor exploits.

**Pruning** removes weights that contribute least to prediction, which is compression of the model's parameter space. **Prompt caching** and **KV-cache reuse** compress computation by storing and reusing predictive state across calls.

The practical takeaway is that LLM compression is a spectrum, and the theory tells you where the redundancy lives. Because models are compressible — because their parameters encode redundant predictive structure — they can be aggressively quantized, pruned, and cached with minimal quality loss.

## Key Takeaways: Why the Information-Theoretic View Matters for LLMs

The compression-is-prediction equivalence is one of the most clarifying ideas in modern machine learning. Here is what to remember:

- **Prediction and compression are mathematically equivalent.** A good predictor is a good compressor, and vice versa, via Shannon's entropy-coding theorem.
- **LLM training is implicit compression.** Every training run finds a compressed representation of the training distribution; the weights are a learned codebook.
- **Text-trained LLMs are general predictors.** Chinchilla 70B beats PNG and FLAC on images and audio it was never trained on — evidence of general predictive structure.
- **Compression is understanding.** Gzip + kNN rivals trained classifiers with zero parameters, showing compression distance captures semantic similarity.
- **The lens explains scaling laws, tokenization, and in-context learning.** All three are manifestations of the same predictive-compressive machinery.
- **It motivates real compression techniques.** Quantization, pruning, and caching all exploit the redundancy that the theory predicts.

The next time you see an LLM predict the next token, remember: it is doing something far grander. It is compressing the world.

## FAQ

### What does "compression is prediction" mean?
It means that predicting the next symbol and compressing a sequence are the same underlying operation. A model that predicts probabilities accurately can be used as a compressor (via entropy coding), and a compressor that extracts statistical regularities is implicitly predicting the data. DeepMind and Meta demonstrated this formally and empirically in their 2023 paper *Language Modeling Is Compression*.

### How can an LLM be used as a compressor?
By plugging the model's predicted probabilities into an arithmetic coder. Arithmetic coding encodes a sequence using the probability of each symbol; feed in the LLM's next-token probabilities and you get a lossless compressor whose output size reflects how well the model predicts the data. The better the predictions, the shorter the compressed output.

### Did LLMs really beat PNG and FLAC?
Yes. In the DeepMind/Meta study, a text-trained Chinchilla 70B compressed ImageNet image patches to 43.4% of raw size (PNG achieved 58.5%) and LibriSpeech audio to 16.4% (FLAC achieved 30.3%), despite never being trained on images or audio. This cross-modal result is key evidence that LLMs learn general predictive structure.

### How does gzip achieve good text classification with zero parameters?
Gzip's Normalized Compression Distance (NCD) measures how much two documents compress when concatenated versus separately. Documents sharing statistical structure compress well together, indicating semantic similarity. Gzip + kNN classifies by finding the nearest compressed neighbor, achieving state-of-the-art results on several benchmarks with zero training.

### Why is the compression viewpoint useful for understanding LLMs?
It provides a single unifying lens for scaling laws (models are compressors of the training distribution), tokenization (tokenizers are subword compressors), in-context learning (online adaptation of the predictive model), and practical model compression (quantization and pruning exploit the redundancy the theory predicts). It turns fuzzy notions of "understanding" into an objective, measurable quantity: bits.
