import networkx as nx
import numpy as np
from scipy import optimize as sop
from os import path

import krangpower as kp
from map2graph_master.map2graph import calc_length
from map2grid.map2grid import GridGenerator, CableCollection, um
from auxiliary_functions import load_curve_csv
from map2grid.map2grid._building_estimation import assign_power_to_building
from map2grid.map2grid._ongraph_calculations import DivCurrentInserter, LengthInserter, ImpedanceFromKInserter
from map2grid.map2grid._ongraph_calculations import POWER_TAG

THISDIR = path.dirname(path.realpath(__file__))


class GridByK(GridGenerator):
    def __init__(self, circuit_name, dg, cable_col: CableCollection):
        super().__init__(circuit_name, dg, cable_col)

    def calculate_k(self, target_dv, root_node, length_prop):

        # we find k of proportionality resistance = k / I
        # such that the most L-distant node is exactly at the desired dV when the currents are the computed diversified

        self.insert_graph_property('div_current',
                                   DivCurrentInserter,
                                   f_diversification=load_curve_csv(path.join(THISDIR, '../data/diversity_factors.csv')),
                                   root_node=root_node)

        if length_prop is None:
            lpn = 'length'
            self.insert_graph_property(lpn, LengthInserter, pos_key='pos')
        else:
            lpn = length_prop

        for e in self.dg.edges:
            self.dg.edges[e]['mlength'] = self.dg.edges[e][lpn].to('m').magnitude

        worst_path = nx.algorithms.dag.dag_longest_path(self.dg, weight='mlength', default_weight=0.0)

        def calc_dv(k):
            dv = 0.0 * um.V
            for idx in range(len(worst_path)-1):
                # dv = (k/I) * I * L
                dv += self.dg.edges[worst_path[idx], worst_path[idx + 1]][lpn] * k * um.V / um.m

            return dv - target_dv

        final_k = sop.fsolve(calc_dv, np.asarray(1.0))

        return final_k[0]

    def compute(self, base_voltage, target_dv, root_node='trmain', length_prop=None):

        k = self.calculate_k(target_dv, root_node, length_prop)
        self.insert_graph_property('impedance', ImpedanceFromKInserter, k=k, current_key='div_current')

        p = nx.get_node_attributes(self.dg, POWER_TAG)
        # print(sum(p.values()))

        src = kp.Vsource(basekv=base_voltage)
        ck = kp.Krang(self.name, src, source_bus_name=root_node)
        self.cables.declare_into(ck)
        # todo transformer
        ldic = nx.get_edge_attributes(self.dg, length_prop)

        done = []

        for e in self.dg.edges:

            try:
                betty_targetty = self.dg.edges[e]['impedance'].to('ohm/m').magnitude
            except ZeroDivisionError:
                raise

            lg = self.cables.get_nextr(betty_targetty)
            # if self.g.edges[e]['phases'] < 3:
            #     ph = [str(x) for x in list(randint(1, 4, self.g.edges[e]['phases']))]
            #     trm = '.' + '.'.join(ph)
            # else:
            #     trm = ''
            # todo terminalize correctly and divide cable collections by nphases
            trm = '.1.2.3'

            def hunt_daisy(go, n):
                gr = nx.Graph(go)
                totry = [n]
                totrynew = []
                while True:
                    for n in totry:
                        for nono in gr[n]:
                            try:
                                phase = gr.edges[n, nono]['phase']
                                return phase
                            except KeyError:
                                totrynew.append(nono)
                    totry = totrynew

            if length_prop is not None:
                ck[str(e[0]) + trm, str(e[1]) + trm] << kp.Line(length=ldic[e],
                                                                phases=3).aka(
                    'ln_' + str(e[0]) + '_' + str(e[1])) * lg
            else:
                ck[str(e[0]) + trm, str(e[1]) + trm] << kp.Line(length=calc_length(self.dg, e, pos_key='pos'),
                                                                phases=3).aka(
                    'ln_' + str(e[0]) + '_' + str(e[1])) * lg

            if e[0] in p.keys() and e[0] not in done:
                try:
                    l_term = '.' + str(self.dg.edges[e]['phase'])
                except KeyError:
                    l_term = '.' + str(hunt_daisy(self.dg, e[0]))
                done.append(e[0])
                ck[str(e[0]) + l_term, ] << kp.Load(kv=0.23 * um.kV, kw=p[e[0]], conn='wye', phases=1, pf=0.9).aka('load_' + str(e[0]))
            if e[1] in p.keys() and e[1] not in done:
                try:
                    l_term = '.' + str(self.dg.edges[e]['phase'])
                except KeyError:
                    if len(self.dg[e[1]]) > 0:
                        l_term = '.' + str(hunt_daisy(self.dg, e[1]))
                    else:
                        assert len(self.dg[e[0]]) > 0
                        l_term = '.' + str(hunt_daisy(self.dg, e[0]))
                done.append(e[1])
                ck[str(e[1]) + l_term, ] << kp.Load(kv=0.23 * um.kV, kw=p[e[1]], conn='wye', phases=1, pf=0.9).aka('load_' + str(e[1]))

        posdic = nx.get_node_attributes(self.dg, 'pos')
        # adding the positions inside the krang
        for bus in posdic.keys():
            ck[str(bus)].X(posdic[bus][0])
            ck[str(bus)].Y(posdic[bus][1])

        self._krang = ck
