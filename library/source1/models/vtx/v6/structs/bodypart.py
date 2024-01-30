from dataclasses import dataclass

from SourceIO.library.utils import Buffer
from .model import Model


@dataclass(slots=True)
class BodyPart:
    models: list[Model]
    MODEL_CLASS = Model

    @classmethod
    def from_buffer(cls, buffer: Buffer, extra8: bool = False):
        entry = buffer.tell()
        model_count, model_offset = buffer.read_fmt('II')

        models = []
        with buffer.save_current_offset():
            buffer.seek(entry + model_offset)
            for _ in range(model_count):
                model = cls.MODEL_CLASS.from_buffer(buffer, extra8)
                models.append(model)
        return cls(models)
