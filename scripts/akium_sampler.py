"""
Akium Sampler for Forge Neo - Momentum Guided Diffusion
by Akium (https://github.com/AkiumAI)

Registers "Akium" and "Akium Color" in the Sampling method dropdown.
The sampler math lives in akium_core.py at the extension root (shared
with the ComfyUI entry point in __init__.py).
"""

import os
import sys

_basedir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if _basedir not in sys.path:
    sys.path.insert(0, _basedir)

import akium_core

try:
    from modules import sd_samplers, sd_samplers_common
    from modules.sd_samplers_kdiffusion import KDiffusionSampler

    for label, func, aliases in (
        ("Akium", akium_core.sample_akium, ["akium"]),
        ("Akium Color", akium_core.sample_akium_color, ["akium_color"]),
    ):
        sd_samplers.add_sampler(sd_samplers_common.SamplerData(
            label,
            lambda model, fn=func: KDiffusionSampler(fn, model),
            aliases,
            {},
        ))

    print("[Akium] Registered 'Akium' and 'Akium Color' samplers.")
except Exception as e:
    print(f"[Akium] Forge sampler registration failed: {e}")
