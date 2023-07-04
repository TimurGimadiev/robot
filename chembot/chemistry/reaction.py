from chython import ReactionContainer
from .molecule import Molecule
from typing import Optional, Iterable, Dict
from .solution import Solution2C


class Reaction(ReactionContainer):
    __slots__ = ("__reaction_params", "__reaction_mols", "__target", "__solvent")

    def __init__(self,
                 reactants: Iterable[Molecule] = (),
                 products: Iterable[Molecule] = (),
                 reagents: Iterable[Molecule] = (),
                 meta: Optional[Dict] = None,
                 name: Optional[str] = None,
                 solvent: Optional[Molecule] = None):
        super().__init__(reactants, products, reagents, meta, name)
        self.__reaction_params = None
        self.__reaction_mols = None
        self.__target = None
        self.__total_volume = None
        self.max_volume = 100/10e5
        self.__solvent = solvent
        # stoichiometry = {reactants:[{mol1: 1, mol2: 1}
        # 1,1], products:[1], reagents:[0.05]}

    @property
    def solvent(self) -> Optional[Molecule]:
        try:
            return self.__solvent
        except AttributeError:
            return None

    @solvent.setter
    def solvent(self, mol: Molecule):
        if isinstance(mol, Molecule):
            self.__solvent = mol

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
        # target params parsing
        if reaction_params.get("target") and \
                reaction_params["target"].get("idx") and \
                reaction_params["target"].get("mols") and \
                reaction_params["target"]["idx"]:
            if reaction_params["target"].get("product"):
                if reaction_params["target"]["product"]:
                    molecule = self.products[reaction_params["target"]["idx"] - 1]
                    molecule.target = True
                else:
                    molecule = self.reactants[reaction_params["target"]["idx"] - 1]
                    molecule.target = True
                molecule.mols = reaction_params["target"]["mols"]
            self._fill_mols(reaction_params["target"]["mols"], reaction_params["stoichiometry"])

        self._fill_props(reaction_params, "states")
        self._fill_props(reaction_params, "density")
        #solvent = smiles(reaction_params["solvent"]["smiles"])
        #solvent.density = reaction_params["solvent"]["density"]
        self.__reaction_params = reaction_params

    @property
    def target(self):
        if self.__reaction_params and self.__reaction_params.get("target"):
            return self.__reaction_params["target"]

    def _fill_props(self, reaction_params, name):
        properties = reaction_params[name]
        if name == "states":
            func = self._fill_mol_states
        elif name == "density":
            func = self._fill_mol_densities
        else:
            raise ValueError(f"No such prop {name}")
        if properties.get("reactants"):
            func(self.reactants, properties["reactants"])
        if properties.get("products"):
            func(self.products, properties["products"])
        if properties.get("reagents"):
            func(self.reagents, properties["reagents"])

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
            molecule.mols = mapping[str(num)] * target_mols

    @staticmethod
    def _fill_mol_states(molecules, props):
        for num, molecule in enumerate(molecules, start=1):
            molecule.state = props[str(num)]

    @staticmethod
    def _fill_mol_densities(molecules, props):
        for num, molecule in enumerate(molecules, start=1):
            molecule.density = props[str(num)]

    # @staticmethod
    # def _fill_group_(molecules, mapping, target_mols):
    #     for num, molecule in enumerate(molecules, start=1):
    #         molecule.mols = mapping[num] * target_mols

    def _solve_volumes(self):
        for mol in self.reactants:
            # need solvent?
            if mol.volume < self.max_volume:  # yes solvent needed
                sol = Solution2C(mol, self.general_solvent)  # make solution
                sol.total_volume = 0.2

            else: #no solvent
                pass

        self.total_volume = sum([x.volume if x.volume else 0 for x in self.reactants])

    def __additives(self, props):
        pass








# хочу провести реакцию
# как задать стехиометрию ? словарь атрибутов?
#     def calculate_mols(self):
#         target_mol = list(self.molecules())[self.meta["target"]["idx"]]
#         self.mols =
#         for num, molecule in enumerate(self.molecules()):
#             mass = self.meta["target"]["mols"] * molecule.molecular_mass






