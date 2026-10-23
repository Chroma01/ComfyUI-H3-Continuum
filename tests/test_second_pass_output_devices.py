"""CPU-only output ownership tests; not a CUDA memory measurement."""
import weakref
from types import SimpleNamespace

import pytest
import torch

from ComfyUI_H3_Continuum_Join.v3.second_pass import run_second_pass_groups
from .test_v35_second_pass_sampling import _group, _latent, _plan


@pytest.mark.parametrize("selected", [None, [1]])
def test_finished_video_outputs_do_not_hold_previous_device_tokens(selected):
    live = weakref.WeakSet()
    prior, transfers = [], []

    class DeviceToken:
        """CPU-backed stand-in for a guider output on its intermediate device."""
        device = SimpleNamespace(type="cuda")
        requires_grad = False
        def __init__(self, value):
            self.value = value
            live.add(self)

        @property
        def shape(self):
            return self.value.shape

        def float(self):
            return self.value.float()

        def detach(self):
            return self

        def to(self, device):
            transfers.append(device)
            assert device == "cpu"
            return self.value.detach()

    groups = [_group(i, temporal=3, prompt=f"Synthetic {i}") for i in range(3)]
    videos = [dict(_latent(torch.zeros(1, 24, 3, 48, 48)), marker=i) for i in range(3)]
    audios = [_latent(torch.full(tuple(g["source_audio_shape"]), float(i))) for i, g in enumerate(groups)]

    def sample(**kwargs):
        prior.append(len(live))
        return {"video": DeviceToken(kwargs["latent"]["video"] + 1),
                "audio": kwargs["latent"]["audio"] + 99}

    refined, output_audio, _, _ = run_second_pass_groups(
        model=object(), clip=object(), sampler=object(), sigmas=torch.tensor([.3, 0.]),
        video_latents=videos, audio_latents=audios, assembly_plan=_plan(groups),
        refine_seed=1, encode_prompt_fn=lambda *a, **k: ["synthetic"],
        latent_builder=lambda video, audio: {"video": video, "audio": audio},
        sample_fn=sample, stream_extractor=lambda s: (s["video"], s["audio"]),
        clone_model_fn=lambda m, **k: m, selected_group_indices=selected,
    )
    count = 3 if selected is None else 1
    assert prior == [0] * count
    assert transfers == ["cpu"] * count
    assert not live
    for i, (video, audio) in enumerate(zip(refined, output_audio, strict=True)):
        assert audio is audios[i]
        assert torch.equal(audio["samples"], audios[i]["samples"])
        assert video["samples"].device.type == "cpu"
        assert video["marker"] == i
        if selected is not None and i not in selected:
            assert video is videos[i]
        else:
            assert torch.equal(video["samples"], videos[i]["samples"] + 1)
        assert not torch.count_nonzero(videos[i]["samples"])


def test_cpu_output_detaches_graph_without_changing_dtype_or_audio():
    group = _group(0, temporal=3, prompt="Synthetic")
    video = _latent(torch.zeros(1, 24, 3, 48, 48, dtype=torch.float64))
    audio = _latent(torch.ones(tuple(group["source_audio_shape"])))
    refined, output_audio, _, _ = run_second_pass_groups(
        model=object(), clip=object(), sampler=object(), sigmas=torch.tensor([.3, 0.]),
        video_latents=[video], audio_latents=[audio], assembly_plan=_plan([group]),
        refine_seed=1, encode_prompt_fn=lambda *a, **k: ["synthetic"],
        latent_builder=lambda v, a: {"video": v, "audio": a},
        sample_fn=lambda **k: {"video": (k["latent"]["video"] + 1).requires_grad_(), "audio": k["latent"]["audio"] + 99},
        stream_extractor=lambda s: (s["video"], s["audio"]), clone_model_fn=lambda m, **k: m,
    )
    assert refined[0]["samples"].dtype == torch.float64
    assert not refined[0]["samples"].requires_grad
    assert output_audio[0] is audio
