# -*- encoding: utf-8 -*-

from __future__ import annotations

from typing import Any, List, Optional, Sequence, Type

import mobase
from basic_games.basic_features.mod_requirement import (
    IWithModRequirements,
    RequirementModFiles,
)
from PyQt5.QtCore import QCoreApplication


class ModRequirementChecker(mobase.IPluginDiagnose):
    """Show problems for mods with missing requirements.

    Uses requirements defined by a game or feature implementing `IWithModRequirements`.
    """

    def __init__(self):
        super().__init__()
        self.__organizer: mobase.IOrganizer = None
        self.__mods_with_missing_requirements_cache: Sequence[RequirementModFiles] = []

    def init(self, organizer: mobase.IOrganizer) -> bool:
        self.__organizer = organizer
        return True

    # IPlugin interface:

    def author(self) -> str:
        return "Zash"

    def description(self) -> str:
        return self.__tr("Checks mod files for missing requirements.")

    def name(self) -> str:
        return "Mod Requirement Checker"

    def localizedName(self) -> str:
        return self.__tr(self.name())

    def requirements(self) -> List[mobase.IPluginRequirement]:
        return [
            mobase.PluginRequirementFactory.basic(
                lambda o: self.__get_game_with_mod_requirements(o) is not None,
                self.__tr(
                    "This plugin can only be enabled for game plugins implementing"
                    " {0} either directly or with a feature."
                ).format(IWithModRequirements.__name__),
            )
        ]

    def settings(self) -> List[mobase.PluginSetting]:
        return []

    def version(self) -> mobase.VersionInfo:
        return mobase.VersionInfo(0, 1, 0)

    # IPluginDiagnose interface:

    def activeProblems(self) -> List[int]:
        return list(range(0, len(self.__mods_with_missing_requirements())))

    def shortDescription(self, key: int) -> str:
        return self.__tr("Missing mod requirement: {0}").format(
            self.__mods_with_missing_requirements_cache[key].requirement.name
        )

    def fullDescription(self, key: int) -> str:
        """The description of the unfulfilled requirement.
        Uses `ModRequirement.get_problem_description`.
        """
        if key > len(self.__mods_with_missing_requirements_cache):
            return ""
        requirement, mod_file_map = self.__mods_with_missing_requirements_cache[key]

        description = requirement.get_problem_description(self.__organizer)
        if description.lstrip().startswith("<p"):
            description = f"<p>{description}</p>"

        mod_file_pairs = sorted(mod_file_map.items())

        return (
            "<style>"
            "th {text-align: left;} th, td {padding: 0 2ex 1ex 0;}"
            # "tr.even {background-color: #242424;}"
            "</style>"
            "<p>"
            + self.__tr("Requirement: {0}").format(requirement.name)
            + f"</p>{description}"
            f'<p>{self.__get_mod_file_table(mod_file_pairs, even_tr_class="even")}</p>'
        )

    def hasGuidedFix(self, key: int) -> bool:
        return False

    def startGuidedFix(self, key: int):
        pass

    # Specific:

    def __tr(self, txt: str) -> str:
        return QCoreApplication.translate(type(self).__name__, txt)

    def __get_game_with_mod_requirements(
        self, organizer: Optional[mobase.IOrganizer] = None
    ) -> Optional[IWithModRequirements]:
        """Returns a `IWithModRequirements` instance, derived either from
        `mobase.IPluginGame` or a game feature."""
        if organizer is None:
            organizer = self.__organizer
        game = organizer.managedGame()
        if isinstance(game, IWithModRequirements):
            return game
        features: dict[Type[Any], Any] = game.featureList()
        feature = next(
            (f for f in features.values() if isinstance(f, IWithModRequirements)), None
        )
        if feature is not None:
            return feature
        return None

    def __mods_with_missing_requirements(
        self,
    ) -> Sequence[RequirementModFiles]:
        """Returns the list of missing requirements and the corresponding mods.
        Sets `__mods_with_missing_requirements_cache`.
        """
        game_with_mod_requirements = self.__get_game_with_mod_requirements()
        if game_with_mod_requirements is None:
            return []
        self.__mods_with_missing_requirements_cache = list(
            game_with_mod_requirements.mods_with_missing_requirements(self.__organizer)
        )
        return self.__mods_with_missing_requirements_cache

    def __get_mod_file_table(self, mod_file_pairs, even_tr_class="even"):
        b = True
        return "".join(
            (
                "<table><tr><th>",
                self.__tr("Mod"),
                "</th><th>",
                self.__tr("File"),
                "</th></tr>",
                *(
                    f"""<tr{
                    f' class="{even_tr_class}"'
                    if (even_tr_class and (b := not b))
                    else ""
                }>"""  # type: ignore[no-redef]
                    f"<td>{m}</td><td>{'<br>'.join(f)}</td>"
                    "</tr>"
                    for m, f in mod_file_pairs
                ),
                "</table>",
            )
        )
