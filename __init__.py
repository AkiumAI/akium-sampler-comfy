"""
Akium Sampler for ComfyUI - Momentum Guided Diffusion
by Akium (https://github.com/AkiumAI)

Exposes Akium and AkiumColor as SAMPLER nodes with recommended
settings baked in (no widgets). Use them with the "SamplerCustom" node:

    Connect the SAMPLER output of "Akium Sampler" / "AkiumColor Sampler"
    directly into SamplerCustom.

The sampler math lives in akium_core.py (shared with the Forge Neo
entry point in scripts/akium_sampler.py).
"""

from comfy.samplers import KSAMPLER

from .akium_core import AKIUM_DEFAULTS, sample_akium, sample_akium_color


# ── ComfyUI nodes (no widgets — defaults baked in) ─────────────────────────────

class AkiumSampler:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("SAMPLER",)
    FUNCTION = "build"
    CATEGORY = "sampling/custom_sampling/samplers"

    def build(self):
        return (KSAMPLER(sample_akium, extra_options=dict(AKIUM_DEFAULTS)),)


class AkiumColorSampler:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {}}

    RETURN_TYPES = ("SAMPLER",)
    FUNCTION = "build"
    CATEGORY = "sampling/custom_sampling/samplers"

    def build(self):
        return (KSAMPLER(sample_akium_color, extra_options=dict(AKIUM_DEFAULTS)),)


# ── register in the standard KSampler dropdown ─────────────────────────────────
# This makes "akium" and "akium_color" appear in the normal KSampler
# sampler_name dropdown, alongside euler / dpmpp / etc. — no custom node or
# special workflow needed. The baked-in defaults live in the function signature.

def _register_in_dropdown():
    try:
        import comfy.samplers
        import comfy.k_diffusion.sampling as kds

        # expose the functions where ComfyUI's sampler_object() looks for them
        kds.sample_akium = sample_akium
        kds.sample_akium_color = sample_akium_color

        for name in ("akium", "akium_color"):
            if name not in comfy.samplers.KSampler.SAMPLERS:
                comfy.samplers.KSampler.SAMPLERS.append(name)
            if hasattr(comfy.samplers, "SAMPLER_NAMES") and name not in comfy.samplers.SAMPLER_NAMES:
                comfy.samplers.SAMPLER_NAMES.append(name)

        print("[Akium] Registered 'akium' and 'akium_color' in the KSampler dropdown.")
    except Exception as e:
        print(f"[Akium] Dropdown registration failed (custom nodes still work): {e}")


_register_in_dropdown()


NODE_CLASS_MAPPINGS = {
    "AkiumSampler": AkiumSampler,
    "AkiumColorSampler": AkiumColorSampler,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "AkiumSampler": "Akium Sampler",
    "AkiumColorSampler": "AkiumColor Sampler",
}
