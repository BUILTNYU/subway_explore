from datetime import datetime

from .config import N_VEHICLES, T_STEP, SIM_TIME
from .inits import init_vehicle, init_passenger
from .loader import load_road_graph, load_lion, merge_lion_road, load_skim_graph, load_demands, merge_stops_demands, load_turnstile_counts
from .rv_graph import init_rv_graph
from .rtv_graph import init_rtv
from .travel import init_time_to_stop, init_travel

class Sim(object):
    def load(self):
        print("====Loading Data=====")
        self.road_graph = load_road_graph()
        self.lion, self.lion_nodes = load_lion()
        self.lion_rg, self.rg_nodes = merge_lion_road(self.lion, self.lion_nodes, self.road_graph)

        self.skim_graph = load_skim_graph()
        self.demands, self.stops = load_demands()
        self.joined_stops, self.demands_with_stops = merge_stops_demands(self.stops, self.rg_nodes, self.demands)
        self.turnstile_counts = load_turnstile_counts(self.joined_stops, SIM_TIME, T_STEP)
        print("====Done=====")



    def get_x_ys(self,  n_vehicles):
        return ((s.geometry.x, s.geometry.y) for ix, s in self.rg_nodes.sample(n_vehicles).iterrows())



    def step(self, debug=False):
        if debug:
            print("RV graph generating....")
        self.rr_g, self.rv_g = self.gen_rv_graph(self.t, self.requests, self.vehicles, debug=debug)
        if debug:
            print("RV graph generating....done.")
            print("RTV graph generating....")
        self.rtv_g = self.gen_rtv_graph(self.t, self.vehicles, self.rr_g, self.rv_g)
        if debug:
            print("RTV graph generating....done.")

        self.t = self.t + config.T_STEP

    def init_demands(self):
        """
        """
        self.origins = np.random.poisson(self.turnstile_counts["lambda"], size=(SIM_TIME / T_STEP , len(self.turnstile_counts))
        self.origins = pd.DataFrame(self.origins, index=np.arange(SIM_TIME, T_STEP))
        self.origins.columns = self.turnstile_counts["stop_id"]

    def init(self):
        self.load()
        self.time_to_stop = init_time_to_stop(self.rg_nodes, self.road_graph)
        self.travel = init_travel(self.joined_stops, self.skim_graph, self.time_to_stop)
        self.gen_rv_graph = init_rv_graph(self.joined_stops, self.travel)
        self.gen_rtv_graph = init_rtv(self.travel)
  


        x_ys = self.get_x_ys( N_VEHICLES)
        self.vehicles = [(i, init_vehicle(x, y)) for i, (x, y) in enumerate(x_ys)]


        self.start = self.t = datetime.now()
        self.init_demands()
        

        self.requests = [init_passenger(d["mn_O_station"], d["mn_D_station"],
                                          self.t, self.skim_graph)\
                           for _, d in self.demands_with_stops.iterrows()\
                           if d["index_right_o"] != d["index_right_d"]]
