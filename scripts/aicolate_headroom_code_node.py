import os
import sys
import subprocess

# ==============================================================================
# Aicolate Code Node - Headroom Context Compression
# ==============================================================================
#
# USAGE IN AICOLATE:
# 1. Add a "Code" node (Python) to your workflow
# 2. Connect input: body (from previous HTTP request node)
# 3. Copy this entire code into the Code node
# 4. Configure outputs as shown below
#
# INPUTS:
#   - body: str (rules document text to compress)
#   - target_ratio: float (optional, default 0.5 = keep 50% tokens)
#
# OUTPUTS:
#   - body_compressed: str (compressed rules text)
#   - original_tokens: int (token count before compression)
#   - compressed_tokens: int (token count after compression)
#   - tokens_saved: int (tokens saved)
#   - compression_ratio: float (0.86 = 86% compression)
# ==============================================================================

TARGET_RATIO = 0.5  # Default: keep 50% of tokens

def install_headroom():
    """Install headroom-ai if not already installed."""
    try:
        import headroom
        return True
    except ImportError:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", "--quiet", "headroom-ai==0.27.0"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            return True
        except Exception:
            return False

async def main(args: Args) -> Output:
    params = args.params
    rules_text = params.get("body", "")
    target_ratio = params.get("target_ratio", TARGET_RATIO)

    if not rules_text or not isinstance(rules_text, str) or len(rules_text.strip()) < 100:
        ret: Output = {
            "body_compressed": rules_text,
            "original_tokens": 0,
            "compressed_tokens": 0,
            "tokens_saved": 0,
            "compression_ratio": 0.0,
            "error": "Input text too short or empty - skipping compression",
        }
        return ret

    os.environ["HEADROOM_DISABLE_PROTECTION"] = "1"
    os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"

    if not install_headroom():
        ret: Output = {
            "body_compressed": rules_text,
            "original_tokens": 0,
            "compressed_tokens": 0,
            "tokens_saved": 0,
            "compression_ratio": 0.0,
            "error": "Failed to install headroom-ai",
        }
        return ret

    try:
        from headroom.transforms.kompress_compressor import KompressCompressor
        compressor = KompressCompressor()
        result = compressor.compress(rules_text, target_ratio=target_ratio)

        ret: Output = {
            "body_compressed": result.compressed,
            "original_tokens": result.original_tokens,
            "compressed_tokens": result.compressed_tokens,
            "tokens_saved": result.tokens_saved,
            "compression_ratio": round(1 - result.compression_ratio, 4),
            "error": None,
        }
        return ret

    except Exception as e:
        ret: Output = {
            "body_compressed": rules_text,
            "original_tokens": 0,
            "compressed_tokens": 0,
            "tokens_saved": 0,
            "compression_ratio": 0.0,
            "error": f"Compression failed: {str(e)}",
        }
        return ret
