from mbg import MapBoxGraph
import matplotlib
import matplotlib.pyplot as plt
from map2grid import cablecollection_from_json, GridByK, assign_power_to_building, assign_current_to_building
from bbox_split.main import grid_locs, bbox_splits
import krangpower as kp
import networkx as nx

matplotlib.use('Qt5Agg')

if __name__ == '__main__':

    # AROSIO = (46.043510148612334,
    #           8.894011974334717,
    #           46.05036097561633,
    #           8.908238410949707)

    # LUGANO = (45.99958511234106,
    #           8.94510269165039,
    #           45.92634956657254,
    #           8.967718353271484)

    MOLINO_NUOVO = (46.01675400235616,
                    8.95686149597168,
                    46.01931695579516,
                    8.961067199707031)

    GRAPHIC_OPTS = {
        'node_shape': 'h',
    }

    um = kp.UM
    POWER_TAG = 'power'
    CURRENT_TAG = 'current'

    kp.set_log_level(10)

    name = 'prova'
    cb = cablecollection_from_json(
        r'C:/Users/charitha.heendeniya/PycharmProjects/spectral_grid_parent/map2grid/map2grid/data/ams_entities_2.json')
    nominal_voltage = 400.0 * um.V
    voltage_drop = 15 * um.V

    xp, yp = grid_locs(MOLINO_NUOVO, 2, 3)
    splits = bbox_splits(xp, yp)

    for i, bb in enumerate(splits):

        print(f'{i} -> {bb}')

        mbg = MapBoxGraph(bb, log_level=10)
        mbg.compute([.25, .35, .4], maxiter=100, imbalance_tol=1e-1)
        mbg.subplot(**GRAPHIC_OPTS)

        pee = {b.id: assign_power_to_building(b) for b in mbg.downloaded_buildings}
        for b, pow in pee.items():
            mbg.g.nodes[b][POWER_TAG] = pow

        cee = {b.id: assign_current_to_building(b, nominal_voltage) for b in mbg.downloaded_buildings}
        for b, cur in cee.items():
            mbg.g.nodes[b][CURRENT_TAG] = cur

        print('Creating digraph')
        dgra = mbg.as_digraphs()  # Generates a list of nx.digraph objects for each subgraph

        for ii, comp in enumerate(dgra):

            relo = {x: str(x) for x in comp.nodes}
            nx.relabel_nodes(comp, relo)
            cg = GridByK(name, comp, cb)

            cg.compute(nominal_voltage, voltage_drop)

            # kogo is the krang object: kogo.Ybus gives the Y-bus matrix
            # kogo.<class name of the grid element> gives the list of those elements in the network
            # kogo.save_json saves the json file of the network
            # kp.Krang.from_json loads the network from the json

            kogo = cg.get_krang()
            kogo.snap()

            lolo = kp.gv.AmpaView(kogo)
            posi = nx.get_node_attributes(comp, 'pos')
            del kogo

            ampe = nx.get_edge_attributes(cg.dg, 'div_current')
            ampe = {k: v.magnitude for k, v in ampe.items() if v is not None}

            def fint(x):
                try:
                    if '_' in x:
                        return x
                except TypeError:
                    pass
                try:
                    return int(x)
                except:
                    return x


            ampel = []
            edgeli = []

            for kk, (lin_lin, x) in enumerate(ampe.items()):
                edge = (fint(lin_lin[0]), fint(lin_lin[1]))

                edgeli.append(edge)
                if x is None:
                    ampel.append(1)
                else:
                    ampel.append(x)

            mamp = min(ampel)
            delt = max(ampel) - mamp
            ampel = [((x - mamp) / delt + 0.07) * 3 for x in ampel]

            # mbox.subplot()
            # lolo.remove_nodes_from(['trmain0', 'main_entry_0'])

            nx.draw_networkx(nx.Graph(comp), pos=posi, nodelist=list(posi.keys()), width=ampel, edgelist=edgeli,
                             with_labels=False, node_size=10)

            nx.draw_networkx_nodes(nx.Graph(comp), pos=posi, node_color='red', node_size=30,
                                   nodelist=[x for x in posi.keys() if str(x).startswith('trmain')])

        plt.show()
