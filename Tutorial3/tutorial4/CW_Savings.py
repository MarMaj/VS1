import numpy as np
from scipy.spatial.distance import pdist, squareform

class VRP:
    """Class for vehicle routing problems.

    Can load data from text files (Solomon instances) excl. irrelevant data such as time windows"""

    def __init__(self, instancefile):
        """Initialize the vrp data object.

        Read all the data from the instancefile (string) - text file according to Solomon format"""
        coord = []; demand = [],                                          # initialize lists
        with open(instancefile,"r") as iFile:               # read data from file
            self.InstanceName = iFile.readline().strip()    # name of instamce
            iFile.readline(); iFile.readline(); iFile.readline()    # skip lines
            vals = iFile.readline().strip().split()
            self.MaxNumVeh = int(vals[0])                    # read data
            self.MaxVehCap = float(vals[1])                  # read data
            iFile.readline(); iFile.readline(); iFile.readline(); iFile.readline()  # skip lines
            line = iFile.readline().strip()
            while line != "":                               # read customer data
                vals = line.split()
                coord.append([float(vals[1]), float(vals[2])])
                demand.append(float(vals[3]))
                line = iFile.readline().strip()
        self.NumCust = len(coord)-1                     # set number of customers
        self.Coord = np.array(coord)                    # create object variables
        self.CustDem = np.array(demand)
        self.DistMatrix = squareform(pdist(self.Coord,"euclidean"))     # compute distance matrix

class VRP_Route:
    """Class for representing a single route in the VRP.

    Used to manage all the information for a single route"""

    def __init__(self, r=[]):
        """Initialize a route.

        route (list): list of visited customers excl. depot (default=[])
        distance(float): indicates the distance of the route
        quantity(float): total demand met on the route
        tourValid(bool): Is the capacity restriction of vehicles fulfilled."""

        self.route = r
        self.distance = 0
        self.quantity = 0
        self.tourValid = False

    def __str__(self):
        """Convert a route into a string.

        Gives a string indicating the full route"""
        output = "0->"
        for c in self.route:
            output += str(c) + "->"
        output += "0"
        return output

    def update_route(self, vrpdata):
        """"Update route data.

        Use the VRP data from vrpdata to compute current distance, quantity, checks tourValid """
        self.distance = 0
        self.quantity = 0
        self.tourValid = False
        lastc = 0   # first entry is depot
        for c in self.route:
            self.distance += vrpdata.DistMatrix[lastc][c]
            self.quantity += vrpdata.CustDem[c]
            lastc = c
        self.distance += vrpdata.DistMatrix[lastc][0]  # last entry is depot
        self.tourValid = (self.quantity <= vrpdata.MaxVehCap)


class VRP_Solution:
    """Class for representing a solution to the VRP.

    Used to manage the solution itself."""

    def __init__(self, vrpdata):
        """Initialize a VRP solution.

        vrpdata(VRP): object holding all necessary VRP data.
        objective(float): total distance of all routes or -1 if solution is not valid.
        routes(list):  list of VRP_Route objects
        solutionValid(bool): Does the solution only contain valid routes and is the max no. of vehicles not exceeded?"""
        self.vrpdata = vrpdata
        self.objective = 0
        self.routes = []
        self.solutionValid = False

    def __str__(self):
        """Convert a solution into a string.

        Gives a string indicating the all routes"""
        output = "Solution for " + self.vrpdata.InstanceName + ":\n"
        output += "Total distance: " + str(round(self.objective, 2)) + "\n"
        output += "Solution valid: " + str(self.solutionValid) + "\n\n"
        count = 1  # count routes
        for r in self.routes:
            output += "Route #" + str(count) + "\n" + str(r) + "\n" + str(round(r.distance, 2)) + "\n" + str(r.quantity) + "\n"
            count += 1
        return output

    def get_objective(self):
        """Update all route data and compute the objective.

        It returns the objective (total distance) or -1 if the solution is not valid."""
        self.objective = 0
        for r in self.routes:
            r.update_route(self.vrpdata)
            self.objective += r.distance
        # all() returns True if all elements of the iterable are true
        self.solutionValid = (all([r.tourValid for r in self.routes]) and len(self.routes) <= self.vrpdata.MaxNumVeh)
        if self.solutionValid:
            return self.objective
        return -1

    def generate_trivial_tours(self):
        """Generate a trivial solution.

        Generates a solution with 0->i->0 tours"""
        self.routes = []
        for c in range(1, self.vrpdata.NumCust+1):
            self.routes.append(VRP_Route([c]))
        return self.get_objective()

    def savings2routes(self,r1,r2):
        """Computes the savings if two routes are joined.

        It creates an new route consisting of 2 VRP_Route objects r1 and r2 and returns the cost savings (positive)
        or increase (negative). It returns -1 if the new route violates any constraints"""
        newRoute = VRP_Route(r1.route+r2.route)
        newRoute.update_route(self.vrpdata)     # compute distance, quantity for newRoute, check whether valid
        if newRoute.tourValid:
            return r1.distance + r2.distance - newRoute.distance
        return -1

    def savings_algorithm(self):
        """Perform the savings algorithm

        Performs the savings algorithm and generates a solution"""
        self.generate_trivial_tours()       # generate trivial solution
        while True:                         # endless loop
            maxSavings = 0                  # values for best savings decision
            bestr1 = None
            bestr2 = None
            for r1 in self.routes:          # loop through all route combinations
                for r2 in self.routes:
                    if r1 != r2:
                        currentSavings = self.savings2routes(r1,r2)
                        if currentSavings > maxSavings:     # if the savings are greater than the so far best savings
                            bestr1 = r1                     # store the routes and the savings value
                            bestr2 = r2
                            maxSavings = currentSavings
            if (bestr1 == None):                          # if no savings or no feasible joins exist break out of the loop
                break
            newRoute = VRP_Route(bestr1.route+bestr2.route) # generate new route and delete old routes
            self.routes.remove(bestr1)
            self.routes.remove(bestr2)
            self.routes.append(newRoute)
            self.get_objective()
        return self.objective


