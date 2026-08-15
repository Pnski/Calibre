import logging
logger = logging.getLogger(__name__)

# Silence noisy 3rd-party loggers
for name in [
    "httpcore",
    "httpx",
    "urllib3",
    "requests",
    "transformers",
    "datasets",
    "accelerate",
    "openai",
]:
    logging.getLogger(name).setLevel(logging.WARNING)

import torch

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    BitsAndBytesConfig,
)

from config.args import (
    args,
    base,
)



def load_model(phase):
    logger.debug("Loading model...")

    device = "cuda" if torch.cuda.is_available() else "cpu"

    logger.debug(f"Using device: {device}")

    tokenizer = AutoTokenizer.from_pretrained(base[phase]["model"])

    bnb_config = BitsAndBytesConfig(
        #load_in_4bit=True,
        #bnb_4bit_quant_type="nf4",
        #bnb_4bit_compute_dtype=torch.float16,
        load_in_8bit=True,
        llm_int8_threshold=1.0, #lower value = more vram
        llm_int8_skip_modules=None,
        llm_int8_enable_fp32_cpu_offload=False, #if true let some weights stay on the CPU->slower
    )

    model = AutoModelForCausalLM.from_pretrained(
        base[phase]["model"],  # MODEL_NAME
        #quantization_config=bnb_config,
        device_map="auto",
        dtype="auto",
        #| dtype    | VRAM |
        #| -------- | ---: |
        #| float32  | 100% |
        #| float16  |  50% |
        #| bfloat16 |  50% |
        #| int8     |  25% |
        #| nf4      |  12% |
    )

    model.eval()#This disables training-specific behavior such as dropout (if present).
    #model = torch.compile(model)

    return tokenizer, model


def execute_model(
    prompt,
    tokenizer,
    model,
    phase,
):
    formatted = tokenizer.apply_chat_template(
        prompt,
        tokenize=False,
        add_generation_prompt=True,
        enable_thinking=True,
    )

    #logger.debug(formatted)

    inputs = tokenizer(formatted, return_tensors="pt").to(model.device)

    #with torch.no_grad():

    with torch.inference_mode():

        output = model.generate(
            **inputs,
            max_new_tokens=base[phase]['max_new_tokens'],
            temperature=base[phase]['temperature'],
            top_k=base[phase]['top_k'],
            top_p=base[phase]['top_p'],
            do_sample=base[phase]['do_sample'],
            repetition_penalty=base[phase]['repetition_penalty'],
            #presence_penalty=base[phase]['presence_penalty'],
            use_cache=True,
            #cache_implementation="quantized",
            #cache_implementation="offloaded",
        )

    result = tokenizer.decode(
        output[0][inputs.input_ids.shape[1] :], skip_special_tokens=True
    )
    return result