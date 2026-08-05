import logging
logger = logging.getLogger(__name__)

from config.args import args, base, prompts

from llm.llm import load_model, execute_model

from epub.load_content import load_chapter
from epub.write_content import write_content

phase = 'p1'

def scene_planner(dir):
    logger.debug("Starting Scene Planner")

    tokenizer, model = load_model(phase)

    for file in sorted((dir / "text").rglob("*")):
        if file.suffix.lower() not in (".html", ".xhtml", ".htm"):
            continue

        content = load_chapter(file)
        logger.debug(f"File: {file.name} Paragraphs: {len(content)}")
        if len(content) <= 1:
            logger.debug("HTMLBody doesn't contain any content, skipping")
            continue

        chunks = []
        chunk = []
        size = 0

        for p in content:
            if chunk and size + len(p) > base["general"]["max_content"]:
                chunks.append("<br>".join(chunk))
                chunk = []
                size = 0

            chunk.append(p)
            size += len(p)

        if chunk:
            chunks.append("<br>".join(chunk))

        result = None

        for i, chunk in enumerate(chunks):
            logger.debug(f"Planning scene {i + 1} / {len(chunks)}")

            if result is None:
                prompt = [
                    {
                        "role": "system",
                        "content": prompts[phase]["scene_planner"]["system"]
                    },
                    {
                        "role": "user",
                        "content": (
                            prompts[phase]["scene_planner"]["user"]
                            + chunk
                            + f"this is chunk {i + 1} of {len(chunks)}"
                        )
                    }
                ]
            else:
                prompt = [
                    {
                        "role": "system",
                        "content": prompts[phase]["scene_planner"]["system"]
                    },
                    {
                        "role": "user",
                        "content": (
                            prompts[phase]["scene_planner_continue"]["user"]
                            + f"\n\nCurrent analysis:\n{result}"
                            + f"\n\nNew chunk text:\n{chunk}"
                            + f"this is chunk {i + 1} of {len(chunks)}"
                        )
                    }
                ]

            result = execute_model(prompt, tokenizer, model, phase)

        write_content(dir, phase, file, result)

    return True