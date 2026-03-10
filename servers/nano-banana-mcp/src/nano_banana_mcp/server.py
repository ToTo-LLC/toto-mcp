import os

from dotenv import load_dotenv
from fastmcp import FastMCP
from fastmcp.utilities.types import Image
from google import genai
from google.genai import types

load_dotenv()

mcp = FastMCP(name="Nano Banana MCP")

api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError(
        "GEMINI_API_KEY environment variable is required. "
        "Set it to your Google Gemini API key before running this server."
    )
gemini_client = genai.Client(api_key=api_key)


@mcp.tool
def generate_image(prompt: str) -> list[Image] | str:
    """Generate an image using Gemini. Returns the generated image."""
    response = gemini_client.models.generate_content(
        model="gemini-3.1-flash-image-preview",
        contents=prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )

    candidates = response.candidates
    if not candidates or not candidates[0].content or not candidates[0].content.parts:
        return "No response from the model. The prompt may have been blocked by safety filters."

    results = []
    for part in candidates[0].content.parts:
        if part.inline_data is not None:
            results.append(Image(data=part.inline_data.data, format="png"))

    if not results:
        return "No image was generated. Try a different prompt."

    return results


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
