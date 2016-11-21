import numpy as np
from scipy.spatial.distance import pdist, squareform
import random

class VRP:
    """Class for vehicle routing problems.

    Can load data from text files (Solomon instances) excl. irrelevant data such as time windows"""

    def __init__(self, instancefile):
        """Initialize the vrp data object.

        Read all the data from the instancefile (string) - text file according to Solomon format"""
        coord = []; demand = []; timew = []; servicet = []                                          # initialize lists
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
                timew.append([float(vals[4]), float(vals[5])])
                servicet.append(float(vals[6]))
                line = iFile.readline().strip()
        self.NumCust = len(coord)-1                     # set number of customers
        self.Coord = np.array(coord)                    # create object variables
        self.CustTW = np.array(timew)
        self.CustSerT = np.array(servicet)
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
        self.serviceTime = 0
        self.tourValid = False
        lastc = 0   # first entry is depot
        for c in self.route:
            self.distance += vrpdata.DistMatrix[lastc][c]
            self.quantity += vrpdata.CustDem[c]
            self.serviceTime += vrpdata.DistMatrix[lastc][c] + vrpdata.CustSerT[c]
            lastc = c
        self.distance += vrpdata.DistMatrix[lastc][0]  # last entry is depot
        self.tourValid =((self.quantity <= vrpdata.MaxVehCap) and (self.serviceTime <= vrpdata.CustTW[0][1]))


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
        self.TabuRelocate = []
        self.TabuExchange = []
        self.TabuTwoOpt = []
        self.GlobalTabu = []

    def __str__(self):
        """Convert a solution into a string.
        Gives a string indicating the all routes"""
        output = "Solution for " + self.vrpdata.InstanceName + ":\n"
        output += "Total distance: " + str(round(self.objective, 5)) + "\n"
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

    def savings_algorithm(self, p):
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
                            if random.random() < p:
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

    def relocate(self, p, p2):
        nrRoute = 1
        for r in self.routes:
            i = 0
            while i <len(r.route):
                myCopy = r.route.copy()
                item = myCopy.pop(i)
                for k in range(0, len(r.route)):
                    if i != k:
                        newRoute = VRP_Route(myCopy[0:k] + [item] + myCopy[k:])
                        newRoute.update_route(self.vrpdata)
                        if ((newRoute.distance < r.distance) and (newRoute.tourValid) and (random.random() < p)) or ((random.random() < p2) and (newRoute.distance > r.distance) ):
                            lTab = [r.route[i], k]
                            if ((lTab not in self.TabuRelocate) and (lTab not in self.GlobalTabu)):
                                self.TabuRelocate.append([r.route[i], i])
                                print(newRoute)
                                loc = self.routes.index(r)
                                self.routes.remove(r)
                                self.routes.insert(loc, newRoute)
                                i = len(r.route)
                                break
                i += 1
            nrRoute += 1

    def cleare_tabu_relocate(self, n):
        criticalNumber = n
        while (len(self.TabuRelocate) > criticalNumber):
            self.TabuRelocate.remove(self.TabuRelocate[0])

    def exchange(self, p, p2):
        nrRoute1=0
        nrRoute2=0
        for r in self.routes:
            nrRoute1 += 1
            for i in range(0, len(r.route)):
                nrRoute2 = 0
                for t in self.routes:
                    nrRoute2 += 1
                    myCopy1 = r.route.copy()
                    item1 = myCopy1.pop(i)
                    for j in range(0, len(t.route)):
                        if(nrRoute1 != nrRoute2) and (r.route != t.route):
                            myCopy2 = t.route.copy()
                            item2 = myCopy2.pop(j)
                            newRoute1 = VRP_Route(myCopy1[0:i] + [item2] + myCopy1[i:])
                            newRoute2 = VRP_Route(myCopy2[0:j] + [item1] + myCopy2[j:])
                            newRoute1.update_route(self.vrpdata)
                            newRoute2.update_route(self.vrpdata)
                            
                            if ((((newRoute1.distance + newRoute2.distance) < (r.distance + t.distance)) and (newRoute1.tourValid) and (newRoute2.tourValid) and (random.random() < p)) 
                                or ((random.random() < p2) and (newRoute1.distance + newRoute2.distance) > (r.distance + t.distance)) and (newRoute1.tourValid) and (newRoute2.tourValid)):
                                lTab1 = [r.route[i], j]
                                lTab2 = [t.route[j], i]
                                if ((lTab1 not in self.TabuExchange) and (lTab2 not in self.TabuExchange) and (lTab1 not in self.GlobalTabu) and (lTab2 not in self.GlobalTabu)):
                                    self.TabuExchange.append([r.route[i-1], i])
                                    self.TabuExchange.append([t.route[j-1], j])
                                    print(newRoute1)
                                    print(newRoute2)
                                    loc1 = self.routes.index(r)
                                    loc2 = self.routes.index(t)
                                    self.routes.remove(r)
                                    self.routes.remove(t)
                                    self.routes.insert(loc1, newRoute1)
                                    self.routes.insert(loc2, newRoute2)
                                    r = newRoute1
                                    t = newRoute2
                                    break
                                else:
                                    print("asd")
                                

    def clear_tabu_exchange(self, n):
        criticalNumber = n
        while (len(self.TabuExchange) > criticalNumber):
            self.TabuExchange.remove(self.TabuExchange[0])

    def two_opt(self, p, p2):
        for r in self.routes:
            i = 0
            while i < len(r.route) - 3:
                  for k in range(i+2, len(r.route)-1):
                      val1 = self.vrpdata.DistMatrix[r.route[i]][r.route[i+1]] + self.vrpdata.DistMatrix[r.route[k]][r.route[k+1]]
                      val2 = self.vrpdata.DistMatrix[r.route[i]][r.route[k]] + self.vrpdata.DistMatrix[r.route[i+1]][r.route[k+1]]
                      if (((val1>val2) and (random.random() < p)) or ((val1<=val2) and (random.random() < p2))):
                          lTab1 = [r.route[i+1], i+1]
                          lTab2 = [r.route[k], k]
                          if((lTab1 not in self.TabuTwoOpt) and (lTab2 not in self.TabuTwoOpt) and (lTab1 not in self.GlobalTabu) and (lTab2 not in self.GlobalTabu)):
                              
                              newRoute1 = VRP_Route(r.route[:i+1] + r.route[k:i:-1] + r.route[k+1:])
                              newRoute1.update_route(self.vrpdata)
                              if(newRoute1.tourValid):
                                  self.TabuTwoOpt.append(lTab1)
                                  self.TabuTwoOpt.append(lTab2)
                                  r.route = r.route[:i+1] + r.route[k:i:-1] + r.route[k+1:]
                                  r.update_route(self.vrpdata)
                                  #loc = self.routes.index(r)
                                  #self.routes.remove(r)
                                  #self.routes.insert(loc, newRoute1)
                                  break
                  i += 1

    def clear_tabu_two_opt(self, n):
        criticalNumber = n
        while (len(self.TabuTwoOpt) > criticalNumber):
            self.TabuTwoOpt.remove(self.TabuTwoOpt[0])

    def clear_global_tabu(self, n):
        criticalNumber = n
        while (len(self.GlobalTabu) > criticalNumber):
            self.GlobalTabu.remove(self.GlobalTabu[0])