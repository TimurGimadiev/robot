from chython import ReactionContainer
from .molecule import Molecule
from typing import Optional, Iterable, Dict


class Reaction(ReactionContainer):

    def __init__(self,
                 reactants: Iterable[Molecule] = (),
                 products: Iterable[Molecule] = (),
                 reagents: Iterable[Molecule] = (), meta: Optional[Dict] = None,
                 name: Optional[str] = None):
        super().__init__(reactants, products, reagents, meta, name)
        self.__reaction_params = None
        self.__reaction_mols = None
        self.__target = None
        # stoichiometry = {reactants:[{mol1: 1, mol2: 1}
        # 1,1], products:[1], reagents:[0.05]}

    @property
    def reaction_mols(self) -> Optional[float]:
        return self.__reaction_mols

    @reaction_mols.setter
    def reaction_mols(self, reaction_mols):
        if not isinstance(reaction_mols, float):
            raise TypeError('Amount of Mols should be float')
        self.__reaction_mols = reaction_mols

    @property
    def reaction_params(self) -> Optional[dict]:
        return self.__reaction_params

    @reaction_params.setter
    def reaction_params(self, reaction_params):
        if not isinstance(reaction_params, dict):
            raise TypeError('should be dict')
        if reaction_params.get("target") and \
                reaction_params["target"].get("idx") and \
                reaction_params["target"].get("mols") and \
                reaction_params["target"]["idx"]:
            if reaction_params["target"].get("product"):
                if reaction_params["target"]["product"]:
                    molecule = self.products[reaction_params["target"]["idx"]-1]
                    molecule.target_mol = True
                else:
                    molecule = self.products[reaction_params["target"]["idx"] - 1]
                    molecule.target_mol = False
                molecule.mols = reaction_params["target"]["mols"]
            self._fill_mols(reaction_params["target"]["mols"], reaction_params["stoichiometry"])
        self.__reaction_params = reaction_params

    @property
    def target(self):
        if self.__reaction_params and self.__reaction_params.get("target"):
            return self.__reaction_params["target"]

    def _fill_mols(self, target_mols, stoichiometry):
        if stoichiometry.get("reactants"):
            self._fill_group_mols(self.reactants, stoichiometry["reactants"], target_mols)
        if stoichiometry.get("products"):
            self._fill_group_mols(self.products, stoichiometry["products"], target_mols)
        if stoichiometry.get("reagents"):
            self._fill_group_mols(self.reagents, stoichiometry["reagents"], target_mols)

    @staticmethod
    def _fill_group_mols(molecules, mapping, target_mols):
        for num, molecule in enumerate(molecules, start=1):
            molecule.mols = mapping[num] * target_mols









# хочу провести реакцию
# как задать стехиометрию ? словарь атрибутов?
#     def calculate_mols(self):
#         target_mol = list(self.molecules())[self.meta["target"]["idx"]]
#         self.mols =
#         for num, molecule in enumerate(self.molecules()):
#             mass = self.meta["target"]["mols"] * molecule.molecular_mass






