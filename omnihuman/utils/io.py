"""
IO Module
=========

This module provides utility functions for reading and writing files.

Functions:
----------
- read_frames: Read frames from image or video file as 4D tensor (n_frames, n_channels, height, width).
- fetch_pretrained_weights: Downloads & reads specific tensors from a Hugging Face Hub repository.
"""

__all__ = ["read_frames", "fetch_pretrained_weights"]

from mimetypes import guess_type
from typing import Dict

import torch
from huggingface_hub import hf_hub_download
from safetensors import safe_open
from torchvision.io import read_image, read_video


def read_frames(path: str) -> torch.Tensor:
    """Read frames from image or video file as 4D tensor (n_frames, n_channels, height, width).

    Args:
        path (str): Where the image or video file is located.

    Raises:
        ValueError: If the file type is neither image nor video.

    Returns:
        torch.Tensor: Frames as 4d torch tensor of shape (n_frames, n_channels, height, width).
    """

    file_type = guess_type(path)[0] or ""
    if file_type.startswith("image"):
        frames = read_image(path)
        frames = frames.unsqueeze(0)
    elif file_type.startswith("video"):
        frames, *_ = read_video(path)
    else:
        raise ValueError(f"Unsupported file type: '{file_type}' of '{path}'")

    return frames


def fetch_pretrained_weights(
    repo_id: str,
    weight_name_to_file_name: Dict[str, str],
) -> Dict[str, torch.Tensor]:
    """Downloads specific files from a Hugging Face Hub repository and loads specific tensors from them.

    Args:
        repo_id (str): Model repository name on Hugging Face Hub (e.g. "organization/their-awesome-model").
        weight_name_to_file_name (Dict[str, str]): mapping of layer name to the shard file that contains its weights (Explore the `model.safetensors.index.json` in the HF model repo for names)

    Returns:
        Dict[str, torch.Tensor]: mapping from layer name to its weights tensor
    """
    weights = {}
    for weight_name, filename in weight_name_to_file_name.items():
        file_path = hf_hub_download(repo_id=repo_id, filename=filename)
        with safe_open(file_path, framework="pt", device="cpu") as f:
            weights[weight_name] = f.get_tensor(weight_name)

    return weights
