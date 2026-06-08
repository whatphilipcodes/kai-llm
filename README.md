# K.ai LLM Module

> This repository is primarily developed against a `Linux` target

Make sure the CUDA driver is installed via Windows
Install the NVIDIA CUDA Toolkit (in WSL):

```sh
wget https://developer.download.nvidia.com/compute/cuda/repos/wsl-ubuntu/x86_64/cuda-keyring_1.1-1_all.deb
sudo dpkg -i cuda-keyring_1.1-1_all.deb
sudo apt-get update
sudo apt-get -y install cuda-toolkit-13-2
```

https://developer.nvidia.com/cuda-downloads

### known issues

- leaked semaphore object (happens both with wrapper script and cli -> vllm issue)

```sh
UserWarning: resource_tracker: There appear to be 1 leaked semaphore objects to clean up at shutdown: {'/mp-358x9v61'}
  warnings.warn(
```

- `Gemma 4 - unified (12B)` runs into a config issue with the current `transformers` version `5.10.2` requiring a manual override whenever the `.env` is rebuilt:

```sh
sed -i 's/config\.vision_config\.num_soft_tokens/getattr(config.vision_config, "num_soft_tokens", getattr(config.vision_config, "mm_posemb_size", 280))/g' .venv/lib/python3.13/site-packages/vllm/model_executor/models/gemma4_unified.py
```