import numpy as np
import numpy.typing as npt
import rustworkx as rx
from scipy.spatial.distance import jensenshannon


W1: float = 0.45
W2: float = 0.45
W3: float = 0.1


# I am assuming the log is base e
def network_node_dispersion(graph: npt.NDArray) -> np.float64:
    ndd, graph_diameter = node_distance_distribution(graph=graph, return_diameter=True)
    ndd = np.pad(ndd, [(0, 0), (0, ndd.shape[0] - ndd.shape[1])])
    averages = np.sum(ndd, axis=0) / graph.shape[0]
    aux = np.divide(ndd, averages, where=averages != 0, out=np.zeros(ndd.shape))
    jsd = np.sum(ndd * np.log(aux, where=aux != 0)) / graph.shape[0]
    return jsd / np.log(graph_diameter + 1), averages


def node_distance_distribution(
    graph: npt.NDArray[np.int64], return_diameter: np.bool_ = False
) -> npt.NDArray[np.float64]:
    G: rx.PyGraph = rx.PyGraph(multigraph=False).from_adjacency_matrix(
        graph.astype(np.float64)
    )
    dist: npt.NDArray[np.int_] = rx.distance_matrix(G, parallel_threshold=300).astype(
        np.int64
    )
    dist[dist < 0] = dist.shape[0]
    N: np.int_ = dist.max() + 1
    dist_offsets: npt.NDArray[np.int_] = dist + np.arange(dist.shape[0])[:, None] * N

    ndd: npt.NDArray[np.float64] = np.delete(
        np.bincount(dist_offsets.ravel(), minlength=dist.shape[0] * N).reshape(-1, N)
        / (dist.shape[0] - 1),
        0,
        axis=1,
    )
    if return_diameter:
        graph_diameter: np.int64 = np.max(dist)
        return ndd, graph_diameter
    return ndd


def dissimilarity_measure(G, H):
    nnd_G, averages_G = network_node_dispersion(G)
    print(f"nnd_G: {nnd_G}")
    nnd_H, averages_H = network_node_dispersion(H)

    print("first")
    print(jensenshannon(averages_H, averages_G, base=2))
    print("second")
    print(np.abs(np.sqrt(nnd_G) - np.sqrt(nnd_H)))

    return W1 * max(jensenshannon(averages_H, averages_G, base=2), 0) + W2 * np.abs(
        np.sqrt(nnd_G) - np.sqrt(nnd_H)
    )
