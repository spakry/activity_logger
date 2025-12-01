"""Local inference utilities for running LLaVA vision-language models."""

from typing import Optional

import torch
from PIL import Image
from transformers import (
    AutoModelForCausalLM,
    AutoProcessor,
    BitsAndBytesConfig,
)

DEFAULT_LLAVA_MODEL_ID = "llava-hf/llava-1.6-7b-hf"


class LocalLlavaAnalyzer:
    """Run LLaVA 1.6 locally for screenshot analysis."""

    def __init__(
        self,
        model_id: str = DEFAULT_LLAVA_MODEL_ID,
        device: Optional[str] = None,
        load_in_4bit: bool = True,
    ) -> None:
        self.model_id = model_id
        self.device = device or "auto"
        quantization_config = None

        if load_in_4bit:
            quantization_config = BitsAndBytesConfig(
                load_in_4bit=True,
                bnb_4bit_use_double_quant=True,
                bnb_4bit_quant_type="nf4",
                bnb_4bit_compute_dtype=torch.bfloat16,
            )

        self.processor = AutoProcessor.from_pretrained(self.model_id)
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_id,
            torch_dtype=torch.bfloat16,
            quantization_config=quantization_config,
            device_map=self.device,
        )

    def generate_activity_log(
        self,
        image: Image.Image,
        activity_prompt: str,
        max_new_tokens: int = 200,
    ) -> str:
        """Generate a short log line for the provided screenshot."""

        prompt = f"USER: <image>\n{activity_prompt}\nASSISTANT:"
        inputs = self.processor(
            images=image,
            text=prompt,
            return_tensors="pt",
        ).to(self.model.device)

        with torch.inference_mode():
            output_ids = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
            )

        generated_text = self.processor.batch_decode(
            output_ids[:, inputs["input_ids"].shape[1]:],
            skip_special_tokens=True,
        )[0]

        return generated_text.strip()
