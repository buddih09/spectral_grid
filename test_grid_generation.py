from mbg import MapBoxGraph
import matplotlib
from time import time
matplotlib.use('Qt5Agg')

if __name__ == '__main__':

    # AROSIO = (46.043510148612334,
    #           8.894011974334717,
    #           46.05036097561633,
    #           8.908238410949707)

    LUGANO = (45.99958511234106,
              8.94510269165039,
              46.02634956657254,
              8.977718353271484)

    GRAPHIC_OPTS = {
        'node_shape': 'h',
    }

    mbg = MapBoxGraph(LUGANO, log_level=10)
    mbg.compute([.25, .35, .4], maxiter=100, imbalance_tol=1e-1)
    mbg.subplot(**GRAPHIC_OPTS)
