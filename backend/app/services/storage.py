from pathlib import Path
import shutil
class LocalPrivateStorage:
    def __init__(self, root): self.root = Path(root).resolve(); self.root.mkdir(parents=True, exist_ok=True)
    def _path(self, key):
        path = (self.root / key).resolve()
        if self.root not in path.parents: raise ValueError("Invalid storage key")
        return path
    def save(self, source, key):
        path = self._path(key); path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("wb") as target: shutil.copyfileobj(source, target)
    def open(self, key): return self._path(key).open("rb")
class S3CompatibleStorage:
    def __init__(self, *args, **kwargs): raise NotImplementedError("Configure an S3-compatible provider before use")
def storage():
    from app.core.config import get_settings
    return LocalPrivateStorage(get_settings().upload_dir)
