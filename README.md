# Akium Sampler (ComfyUI / Forge Neo)

A custom k-diffusion sampler for ComfyUI and SD WebUI Forge Neo.

Akium is a second-order stochastic sampler that builds a sense of direction as it generates — using that momentum to make smarter decisions at each step. The result is sharper fine details compared to pure SDE samplers like ER-SDE, without losing the creative variety that stochastic sampling is known for.

> Tested on Anima and Illustrious. Compatible with any k-diffusion model.

---

## Installation (ComfyUI)

### Step 1 — Add the custom node

**Via ComfyUI-Manager:**

1. Open **Manager → Install via Git URL**
2. Paste: `https://github.com/AkiumAI/akium-sampler-comfy`
3. Restart ComfyUI

**Manual:** Download and drop the `akium-sampler-comfy` folder into your `ComfyUI/custom_nodes/` directory, then restart ComfyUI.

### Step 2 — Use it

After restarting, **akium** and **akium_color** appear automatically in the standard **KSampler** `sampler_name` dropdown, alongside euler, dpmpp, etc. No extra setup.

Check the console on startup for:
```
[Akium] Registered 'akium' and 'akium_color' in the KSampler dropdown.
```

---

## Installation (Forge Neo)

The same repository also works as a [Forge Neo](https://github.com/Haoming02/sd-webui-forge-classic/tree/neo) extension:

1. Open **Extensions → Install from URL**
2. Paste: `https://github.com/AkiumAI/akium-sampler-comfy`
3. Click **Install**, then restart the WebUI

(Or clone/copy this folder into your `<forge>/extensions/` directory manually.)

After restarting, **Akium** and **Akium Color** appear in the **Sampling method** dropdown. Check the console on startup for:
```
[Akium] Registered 'Akium' and 'Akium Color' samplers.
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

**Close-up** 
<img width="4256" height="1330" alt="xyz_grid-0015-1" src="https://github.com/user-attachments/assets/0a066505-107c-4932-bcfb-c42aa120a66d" />

**Upper body** 
<img width="4256" height="1330" alt="xyz_grid-0010-1" src="https://github.com/user-attachments/assets/7849da02-74de-496c-ad37-cfd27bb2eed4" />

**Full body** 
<img width="4256" height="1330" alt="xyz_grid-0012-1" src="https://github.com/user-attachments/assets/cb55b574-5abc-41e9-82ed-cfd251bf6325" />

### Illustrious

**Close-up**
<img width="4256" height="1330" alt="xyz_grid-0020-1" src="https://github.com/user-attachments/assets/88627a94-4a5d-4ac5-98b4-f64e75e243df" />

**Upper body** 
<img width="4256" height="1330" alt="xyz_grid-0023-1" src="https://github.com/user-attachments/assets/c464c5fb-d36d-4cf3-bc57-8f30d7cd87ff" />

**Full body** 
<img width="4256" height="1330" alt="xyz_grid-0022-1" src="https://github.com/user-attachments/assets/62f8eca6-0783-491c-91fb-66f4e6b97bf5" />

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
