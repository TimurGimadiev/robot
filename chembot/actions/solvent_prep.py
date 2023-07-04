from ..chemistry import Molecule, Reaction, smiles, Solution2C
from ..robot import chembot
from ..storage import Storages
from ..custom_types import Slots

class SolutionPrepare:
    #only for liquids
    def __init__(self, molecule, molecule_volume, solvent, solvent_volume):
        avilable_slot = chembot.storages.tube_storage.next_avilable_slot
        pipet_id, pipet = chembot.storages.pipet_holder.next_pipet()
        success = False
        for slot in chembot.storages.tube_storage.search_molecule(molecule):
            if chembot.storages.tube_storage.slots[slot].volume > molecule_volume:
                success = True
                chembot.storages.tube_storage.left_pipet_get(slot, molecule_volume,
                                                         chembot.storages.pipet_holder[pipet_id])
                chembot.storages.tube_storage.left_pipet_put(avilable_slot, molecule_volume,
                                                         chembot.storages.pipet_holder[pipet_id])
        else:
            if not success:
                ValueError(f"No enough compound {str(molecule)} in storage")
            chembot.storages.tube_storage[avilable_slot] = Slots.PROCESSING
        pipet_id = chembot.storages.pipet_holder.next_pipet()
        success = False
        for slot in chembot.storages.tube_storage.search_molecule(solvent):
            if chembot.storages.tube_storage.slots[slot].volume > solvent_volume:
                success = True
                chembot.storages.tube_storage.left_pipet_get(slot, solvent_volume,
                                                         chembot.storages.pipet_holder[pipet_id])
                chembot.storages.tube_storage.left_pipet_put_and_mix(avilable_slot, solvent_volume,
                                                                 chembot.storages.pipet_holder[
                                                                     pipet_id])

        else:
            if not success:
                ValueError(f"No enough compound {str(solvent)} in storage")
            chembot.storages.tube_storage[avilable_slot] = Slots.PROCESSING
        # mixed noe we have to calculate what is in the final tube
        new = molecule.copy()





