# -*- coding:utf-8 -*-

from datetime import datetime
from typing import Any, List, Optional, Union

from pydantic import BaseModel, Field

class CustomModeGenerateParam(BaseModel):
    """Generate with Custom Mode"""

    prompt: str = Field(..., description="lyrics")
    mv: str = Field(
        ...,
        description="model version, default: chirp-v3-0",
        examples=["chirp-v3-0"],
    )
    title: str = Field(..., description="song title")
    tags: str = Field(..., description="style of music")
    continue_at: Optional[str] = Field(
        default=None,
        description="continue a new clip from a previous song, format mm:ss",
        examples=["01:23"],
    )
    continue_clip_id: Optional[str] = None


class DescriptionModeGenerateParam(BaseModel):
    """Generate with Song Description"""

    gpt_description_prompt: str
    make_instrumental: bool = False
    mv: str = Field(
        ...,
        description="model version, default: chirp-v3-0",
        examples=["chirp-v3-0"],
    )
    prompt: str = Field(
        default="",
        description="Placeholder, keep it as an empty string, do not modify it",
    )

class LyricsGenerateParam(BaseModel):
    """Generate with Song Lyrics"""
    prompt: str = Field(
        default="Someone who is passionate about work and life.",
    )