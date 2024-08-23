from SourceIO.library.shared.app_id import SteamAppId
from SourceIO.library.shared.content_manager.provider import ContentProvider
from SourceIO.library.shared.content_manager.providers.gma_provider import GMAContentProvider
from SourceIO.library.shared.content_manager.providers.loose_files import LooseFilesContentProvider
from SourceIO.library.shared.content_manager.providers.source1_gameinfo_provider import Source1GameInfoProvider
from SourceIO.library.utils.path_utilities import backwalk_file_resolver
from SourceIO.library.utils.tiny_path import TinyPath
from SourceIO.logger import SourceLogMan
from .source1 import Source1Detector

log_manager = SourceLogMan()
logger = log_manager.get_logger('GModDetector')


class GModDetector(Source1Detector):
    @classmethod
    def scan(cls, path: TinyPath) -> list[ContentProvider]:
        gmod_root = None
        gmod_dir = backwalk_file_resolver(path, 'garrysmod/dupes')
        if gmod_dir is not None:
            gmod_root = gmod_dir.parent
        if gmod_root is None:
            return []
        providers = {}
        initial_mod_gi_path = backwalk_file_resolver(path, "gameinfo.txt")
        if initial_mod_gi_path is not None:
            cls.add_provider(Source1GameInfoProvider(initial_mod_gi_path), providers)

        garrysmod_mod_gi_path = gmod_root / "garrysmod/gameinfo.txt"
        if initial_mod_gi_path != garrysmod_mod_gi_path:
            cls.add_provider(Source1GameInfoProvider(garrysmod_mod_gi_path), providers)

        cls.register_common(gmod_root, providers)
        for addon in (gmod_dir / "addons").iterdir():
            if addon.suffix == ".gma":
                provider = GMAContentProvider(addon)
            else:
                provider = LooseFilesContentProvider(addon, SteamAppId.GARRYS_MOD)
            cls.add_provider(provider, providers)
        return list(providers.values())
