"""Module for Token embeddings."""

__all__ = ["pool_embeddings"]

from typing import Iterable

import torch


def pool_embeddings(
    embeddings: Iterable[torch.Tensor],
    out_dim: int = 512,
    pre_norm: bool = True,
    post_norm: bool = True,
) -> torch.Tensor:
    """Combine multiple embedding tables into a single one by concatenating them and reducing the dimensionality in the result.
    The vocabulary size of all embeddings **must** be the same.
    Pooling is done by first concatenating the embeddings across embed_dim (`shape=(vocabulary_size, sum(e.shape[-1] for e in embeddings))`),
    then reshaping them into a 3D tensor of shape (vocabulary_size, out_dim, n), and finally taking the mean across the last dimension.
    i.e. The resulting tensor is [[mean(0:n), mean(n:2n), ..., mean(-n:total_embed_size)], ...] so the features from different embedding tables are not mixed.

    Args:
        embeddings (Iterable[torch.Tensor]): A list of 2D tensors (vocabulary_size, embedding_dim) to be combined.
        out_dim (int, optional): Number of features per token in the output tensor. Defaults to 512.
        pre_norm (bool, optional): L2 normalize each input embedding table so that each token's vector has magnitude 1. Defaults to True.
        post_norm (bool, optional): L2 normalize the pooled tensor so that each token's vector has magnitude 1. Defaults to True.

    Raises:
        ValueError: If the sum of all embedding sizes is smaller than out_dim.
        ValueError: If out_dim is not a divisor of the sum of all embedding sizes.

    Returns:
        torch.Tensor: The pooled embedding table of shape (vocabulary_size, out_dim).
    """

    stacked_size = sum(e.shape[-1] for e in embeddings)
    if stacked_size < out_dim:
        raise ValueError(f"{out_dim=} is smaller than the concatenated embedding dimension {stacked_size}")
    if stacked_size % out_dim != 0:
        raise ValueError(f"{out_dim=} is not a divisor of the concatenated embedding dimension {stacked_size}")
    if len(vocab_sizes := {e.shape[-2] for e in embeddings}) != 1:
        raise ValueError(f"All embedding tables must have the same vocabulary size. Got {vocab_sizes=}")

    embedding = torch.cat(
        [(v32 := v.type(torch.float32)) / (v32.norm(dim=-1, keepdim=True) if pre_norm else 1) for v in embeddings],
        dim=-1,
    )
    if embedding.shape[1] == out_dim:
        return embedding

    embedding = embedding.view(embedding.shape[0], out_dim, -1).mean(dim=-1)
    if post_norm:
        embedding = embedding / embedding.norm(dim=-1, keepdim=True)
    return embedding
