from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Union, Literal


class ImageModel(str, Enum):
    """Standard image model identifiers."""

    DALL_E_2 = "dall-e-2"
    DALL_E_3 = "dall-e-3"


@dataclass
class ImageContent:
    """Representation of image content, either as URL, base64, or file path."""

    source: Union[str, Path]
    type: Literal["url", "base64", "path"]
