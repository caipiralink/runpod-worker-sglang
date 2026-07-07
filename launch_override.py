"""launch_server entrypoint with optional default-sampling overrides.

OVERRIDE_DEFAULT_TOP_K: replace the model's default top_k sampling param
(-1 disables the top-k truncation baked into the checkpoint's
generation_config). Unset means stock behavior.
"""

import os
import runpy

top_k = os.getenv("OVERRIDE_DEFAULT_TOP_K")
if top_k:
    import sglang.srt.configs.model_config as model_config

    _orig = model_config.ModelConfig.get_default_sampling_params
    _top_k = int(top_k)

    def _patched(self):
        return {**_orig(self), "top_k": _top_k}

    model_config.ModelConfig.get_default_sampling_params = _patched

runpy.run_module("sglang.launch_server", run_name="__main__")
