"""SmartCheck CLI — run `smartcheck --demo`."""
import os, sys, json
from . import core
from ._version import __version__


def _demo_dir():
    return os.path.join(os.path.dirname(__file__), "..", "..", "demo")


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--version" in argv:
        print(f"SmartCheck {__version__}"); return 0
    demo = "--demo" in argv or not argv
    print(f"\n🦔 SmartCheck {__version__}  ·  IAIso §2 · Verification")
    result = core_demo()
    print(result)
    print(f"\nBacked by IAIso §2 · Verification · part of the Smart* family · https://smarttasks.cloud\n")
    return 0


def core_demo() -> str:
    return _DEMO()


def _DEMO():
    answers = ["Revenue grew 340 last quarter.", "It always works and never fails.",
               "The capital is Paris. [contains seeded error]"]
    out = []
    for a in answers:
        v = core.check(a)
        out.append(f"{'PASS' if v.passed else 'FLAG'}  “{a[:48]}”")
        for i in v.issues:
            out.append(f"    ✗ {i.type} (conf {i.confidence})")
    return "\n".join(out)

if __name__ == "__main__":
    sys.exit(main())
