"""
Akium Sampler - Momentum Guided Diffusion (core math)
by Akium (https://github.com/AkiumAI)

Framework-agnostic k-diffusion sampler functions. Imported by:
  - __init__.py            (ComfyUI custom node entry point)
  - scripts/akium_sampler.py (Forge Neo extension entry point)
"""

import torch
from tqdm import trange


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


# ── core sampler ────────────────────────────────────────────────────────────────

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
    s_in = x.new_ones([x.shape[0]])  # sigma broadcast to batch size (k-diffusion convention)

    for i in trange(n_steps, disable=disable):
        sigma_curr = sigmas[i]
        sigma_next = sigmas[i + 1]

        if s_churn > 0 and s_tmin <= sigma_curr.item() <= s_tmax:
            gamma = min(s_churn / n_steps, 2 ** 0.5 - 1)
            sigma_hat = sigma_curr * (1 + gamma)
            x = x + torch.randn_like(x) * s_noise * (sigma_hat ** 2 - sigma_curr ** 2) ** 0.5
            sigma_curr = sigma_hat

        dt = sigma_next - sigma_curr

        denoised = model(x, sigma_curr * s_in, **extra_args)
        d_curr = (x - denoised) / sigma_curr
        momentum = momentum_beta * momentum + (1.0 - momentum_beta) * d_curr

        if sigma_next.item() > 0:
            x_la = x + momentum * dt * lookahead_scale
            denoised_la = model(x_la, sigma_next * s_in, **extra_args)
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
    # only on standard 4D latents [B, C, H, W] with at least 3 channels
    # (SD1.5 / SDXL / Illustrious). Other layouts (video / packed DiT
    # latents like some Anima/Qwen pipelines) are left untouched to avoid
    # shape-mismatch errors.
    try:
        if result.dim() == 4 and result.shape[1] >= 3:
            result[:, 1:3, :, :] = result[:, 1:3, :, :] * 1.15
        else:
            print(f"[Akium] AkiumColor: chroma boost skipped (unsupported latent shape {tuple(result.shape)}).")
    except Exception as e:
        print(f"[Akium] AkiumColor: chroma boost skipped ({e}).")
    return result
