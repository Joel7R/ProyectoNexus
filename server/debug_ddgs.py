import sys

with open("debug_output.txt", "w", encoding="utf-8") as f:
    try:
        import ddgs
        f.write(f"Imported 'ddgs' from: {ddgs.__file__}\n")
        from ddgs import DDGS
        f.write(f"DDGS class: {DDGS}\n")
        import inspect
        f.write(f"DDGS.text signature: {inspect.signature(DDGS.text)}\n")
    except ImportError:
        f.write("Could not import 'ddgs'\n")
    except Exception as e:
        f.write(f"Error inspecting ddgs: {e}\n")

    try:
        import duckduckgo_search
        f.write(f"Imported 'duckduckgo_search' from: {duckduckgo_search.__file__}\n")
        from duckduckgo_search import DDGS
        f.write(f"DDGS class from duckduckgo_search: {DDGS}\n")
        import inspect
        f.write(f"DDGS.text signature (should match): {inspect.signature(DDGS.text)}\n")
    except ImportError:
        f.write("Could not import 'duckduckgo_search'\n")
    except Exception as e:
        f.write(f"Error inspecting duckduckgo_search: {e}\n")
