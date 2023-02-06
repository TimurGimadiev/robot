from chython import MoleculeContainer, smiles as chy_smiles, ReactionContainer

def attach_dyn_propr(instance, prop_name, propr):
    """Attach property proper to instance with name prop_name.

    Reference:
      * https://stackoverflow.com/a/1355444/509706
      * https://stackoverflow.com/questions/48448074
    """
    class_name = instance.__class__.__name__ + 'WithProperties'
    child_class = type(class_name, (instance.__class__,), {prop_name: propr})

    instance.__class__ = child_class


def mass(self):
    if self.mols is not None:
        return self.mols * self.molecular_mass


def add_props(molecule, mols, target_mol):
    #molecule.meta["mols"] = mols
    #molecule.meta["target_mol"] = target_mol
    molecule.mols = mols
    molecule.target_mol = target_mol
    prop = property(mass)
    attach_dyn_propr(molecule, "mass", prop)
    return molecule


def smiles(smiles_str, mols: list = None, target_mol:list=False):
    result = chy_smiles(smiles_str)
    if isinstance(result, MoleculeContainer):
        return add_props(result, mols[0], target_mol[0])
    elif isinstance(result, ReactionContainer):
        for molecule, i_mols, i_target_mol in zip(result.molecules(), mols, target_mol):
            add_props(molecule, i_mols, i_target_mol)
        return result

