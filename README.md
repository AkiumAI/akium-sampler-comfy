# Akium Sampler (ComfyUI)

A custom k-diffusion sampler for ComfyUI.

Akium is a second-order stochastic sampler that builds a sense of direction as it generates — using that momentum to make smarter decisions at each step. The result is sharper fine details compared to pure SDE samplers like ER-SDE, without losing the creative variety that stochastic sampling is known for.

> Tested on Anima and Illustrious. Compatible with any k-diffusion model.

---

## Installation

### Step 1 — Add the custom node

**Via ComfyUI-Manager:**

1. Open **Manager → Install via Git URL**
2. Paste: `https://github.com/AkiumAI/akium-sampler-comfy`
3. Restart ComfyUI

**Manual:** Download and drop the `comfyui-akium` folder into your `ComfyUI/custom_nodes/` directory, then restart ComfyUI.

### Step 2 — Use it

After restarting, **akium** and **akium_color** appear automatically in the standard **KSampler** `sampler_name` dropdown, alongside euler, dpmpp, etc. No extra setup.

Check the console on startup for:
```
[Akium] Registered 'akium' and 'akium_color' in the KSampler dropdown.
```

---

## Samplers

| Name           | Description                                                                                                                           |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| **akium**      | Standard version                                                                                                                      |
| **akium_color** | Same as Akium with a subtle chroma boost on the final output. More vivid colors. Experimental and subject to possible future changes. |

> The chroma boost in **akium_color** is tuned for 4-channel latents (SD1.5 / SDXL / Illustrious). On Anima (Qwen-Image VAE) the color effect may differ.

---

## Two ways to use it

**Standard KSampler (recommended)** — just select `akium` or `akium_color` from the `sampler_name` dropdown on any KSampler node. Set the seed to `randomize` as usual.

**Custom sampling pipeline (optional)** — the package also adds **Akium Sampler** / **AkiumColor Sampler** nodes under `sampling > custom_sampling > samplers`. Wire the `SAMPLER` output into a **SamplerCustom** node, with a scheduler feeding `SIGMAS`.

---

## How it works

Most samplers work step by step in isolation — each step looks only at the current noisy latent and asks the model what to do next, with no knowledge of where things were heading before or after.

Akium works differently:

**Memory** — It builds a running sense of direction from previous steps, weighting recent ones more heavily. This momentum grows stronger as the generation progresses.

**Look-ahead** — Before committing to the next step, Akium uses that momentum to simulate where the latent is heading and asks the model what it sees there. The final step blends the current direction with that prediction.

**Adaptive noise** — Once the sampler has a strong sense of direction, it reduces the stochastic noise automatically. Noise is useful for exploration early on — but once the model knows where it's going, extra randomness only works against fine details.

The end result: sharper details and more coherent structure, while keeping the variety you get from stochastic sampling. Two model calls per step, same as Heun or DPM++ 2S.

---

## Comparisons

All comparisons use the same seed, prompt, and the respective recommended settings.

### Anima

**Close-up** [![anima-closeup](assets/anima_closeup.jpg)](assets/anima_closeup.jpg)

**Upper body** [![anima-upper](assets/anima_upper.jpg)](assets/anima_upper.jpg)

**Full body** [![anima-full](assets/anima_full.jpg)](assets/anima_full.jpg)

### Illustrious

**Close-up** [![illustrious-closeup](assets/illustrious_closeup.jpg)](assets/illustrious_closeup.jpg)

**Upper body** [![illustrious-upper](assets/illustrious_upper.jpg)](assets/illustrious_upper.jpg)

**Full body** [![illustrious-full](assets/illustrious_full.jpg)](assets/illustrious_full.jpg)

---

## Recommended settings

**Anima / Anima-based merges**

| Setting   | Value |
| --------- | ----- |
| Steps     | 30–35 |
| CFG       | 4–5   |
| Scheduler | Beta  |

**Illustrious**

| Setting   | Value  |
| --------- | ------ |
| Steps     | 28–32  |
| CFG       | 5–7    |
| Scheduler | Karras |

---

## Support

If you find Akium useful, consider supporting via Ko-fi: [ko-fi.com/akinak4](https://ko-fi.com/akinak4)

---

## License

CC BY 4.0 — free to use including commercially, credit required.
Credit: "Akium Sampler by AkiumAi". (optional) github.com/AkiumAI
