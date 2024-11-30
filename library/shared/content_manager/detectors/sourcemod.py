from SourceIO.library.shared.content_manager.provider import ContentProvider
from SourceIO.library.utils.path_utilities import backwalk_file_resolver
from SourceIO.library.utils.tiny_path import TinyPath
from .source1 import Source1Detector
from ..providers.source1_gameinfo_provider import Source1GameInfoProvider


class SourceMod(Source1Detector):
    @classmethod
    def scan(cls, path: TinyPath) -> list[ContentProvider]:
        smods_dir = backwalk_file_resolver(path, 'sourcemods')
        mod_root = None
        mod_name = None
        if smods_dir is not None and path.is_relative_to(smods_dir):
            mod_name = path.relative_to(smods_dir).parts[0]
            mod_root = smods_dir / mod_name
        if mod_root is None:
            return []
        content_providers = {}
        initial_mod_gi_path = backwalk_file_resolver(path, "gameinfo.txt")
        if initial_mod_gi_path is not None:
            cls.add_provider(Source1GameInfoProvider(initial_mod_gi_path), content_providers)
        return list(content_providers.values())
