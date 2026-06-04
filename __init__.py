"""
Akium Sampler for ComfyUI - Momentum Guided Diffusion
by Akium (https://github.com/AkiumAI)

Exposes Akium and AkiumColor as SAMPLER nodes with recommended
settings baked in (no widgets). Use them with the "SamplerCustom" node:

    Connect the SAMPLER output of "Akium Sampler" / "AkiumColor Sampler"
    directly into SamplerCustom.
"""

import torch
from tqdm import trange
from comfy.samplers import KSAMPLER


# ── baked-in defaults (same as the Forge version) ──────────────────────────────

AKIUM_DEFAULTS = {
    "momentum_beta": 0.7,
    "lookahead_scale": 0.4,
    "g_scale": 0.9,
    "noise_exponent": 2.0,
    "noise_momentum_inv": 0.7,
}


# ── helpers ───────────────────────────────────────────────────────────────────

def _er_sde_noise(sigma_curr, sigma_next, g_scale=1.0):
    diff = sigma_curr.item() ** 2 - sigma_next.item() ** 2
    diff = max(diff, 0.0)
    return diff ** 0.5 * g_scale


# ── core sampler (same math as the Forge version) ──────────────────────────────

@torch.no_grad()
def sample_akium(
    model,
    x,
    sigmas,
    extra_args=None,
    callback=None,
    disable=None,
    momentum_beta: float = 0.7,
    lookahead_scale: float = 0.4,
    g_scale: float = 0.9,
    noise_exponent: float = 2.0,
    noise_momentum_inv: float = 0.7,
    s_churn: float = 0.0,
    s_tmin: float = 0.0,
    s_tmax: float = float("inf"),
    s_noise: float = 1.0,
    **kwargs,
):
    extra_args = extra_args or {}
    n_steps = len(sigmas) - 1
    sigma_max = sigmas[0]
    momentum = torch.zeros_like(x)

    for i in trange(n_steps, disable=disable):
        sigma_curr = sigmas[i]
        sigma_next = sigmas[i + 1]

        sigma_curr_1d = sigma_curr.reshape(1)
        sigma_next_1d = sigma_next.reshape(1)

        if s_churn > 0 and s_tmin <= sigma_curr.item() <= s_tmax:
            gamma = min(s_churn / n_steps, 2 ** 0.5 - 1)
            sigma_hat = sigma_curr * (1 + gamma)
            x = x + torch.randn_like(x) * s_noise * (sigma_hat ** 2 - sigma_curr ** 2) ** 0.5
            sigma_curr = sigma_hat
            sigma_curr_1d = sigma_hat.reshape(1)

        dt = sigma_next - sigma_curr

        denoised = model(x, sigma_curr_1d, **extra_args)
        d_curr = (x - denoised) / sigma_curr
        momentum = momentum_beta * momentum + (1.0 - momentum_beta) * d_curr

        if sigma_next.item() > 0:
            x_la = x + momentum * dt * lookahead_scale
            denoised_la = model(x_la, sigma_next_1d, **extra_args)
            d_guided = (x_la - denoised_la) / sigma_next

            momentum_magnitude = momentum.abs().mean().item()
            d_curr_magnitude = d_curr.abs().mean().item()
            guided_weight = min(momentum_magnitude / (d_curr_magnitude + 1e-6), 1.0) * 0.5

            d_final = (1.0 - guided_weight) * d_curr + guided_weight * d_guided
            x = x + d_final * dt

            noise_reduction = noise_momentum_inv * min(guided_weight * 2.0, 1.0)
            effective_g = g_scale * (1.0 - noise_reduction)
            effective_g = max(effective_g, g_scale * 0.1)

            noise_w = (sigma_curr.item() / sigma_max.item()) ** noise_exponent
            er_noise = _er_sde_noise(sigma_curr, sigma_next, effective_g)
            x = x + torch.randn_like(x) * er_noise * noise_w
        else:
            x = x + d_curr * dt

        if callback is not None:
            callback({
                "x": x, "i": i,
                "sigma": sigma_curr, "sigma_hat": sigma_curr,
                "denoised": denoised,
            })

    return x


@torch.no_grad()
def sample_akium_color(model, x, sigmas, extra_args=None, callback=None, disable=None, **kwargs):
    """AkiumColor: Akium + chroma boost on the final latent."""
    result = sample_akium(model, x, sigmas, extra_args=extra_args, callback=callback, disable=disable, **kwargs)
    # boost chroma channels of the latent (ch 1 and 2)
    if result.shape[1] >= 3:
        result[:, 1:3, :, :] = result[:, 1:3, :, :] * 1.15
    return result


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
