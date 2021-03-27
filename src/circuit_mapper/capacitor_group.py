from . load_group import LoadGroup
from . capacitor import Capacitor


class CapacitorGroup(LoadGroup):
    dss_module_name = 'Capacitors'
    ele_class = Capacitor

    def get_cappu_matrix(self):
        """
        return 3 x n matrix of kvar values summed over Bus
        columns indexed by Bus index
        """
        return self._get_attr_by_bus('cappu', orient='col')