import mimetypes


def _readable(path):
    try:
        with open(path, "rb"):
            return True
    except OSError:
        return False


mimetypes.knownfiles = [
    path for path in mimetypes.knownfiles if _readable(path)
]
