#Marcin tu był2
import CW_Savings
import csv

files25 = ["solomon_25//C101.txt", "solomon_25/C201.txt", "solomon_25/R101.txt", "solomon_25/R201.txt", "solomon_25/RC101.txt", "solomon_25/RC201.txt"]
files50 = ["solomon_50/C101.txt", "solomon_50/C201.txt", "solomon_50/R101.txt", "solomon_50/R201.txt", "solomon_50/RC101.txt", "solomon_50/RC201.txt"]
files100 = ["solomon_100/C101.txt", "solomon_100/C201.txt", "solomon_100/R101.txt", "solomon_100/R201.txt", "solomon_100/RC101.txt", "solomon_100/RC201.txt"]
folders = [files25, files50, files100]
bestSolutions = []

for folder in folders:
    for file in folder:
        myVRP = CW_Savings.VRP(file)
        mySolution = CW_Savings.VRP_Solution(myVRP)
        bestSolution = mySolution
        bestObjectiv = 0
        k = 0
        csvName = file[:-4] + ".csv"
        with open(csvName, 'w', newline='') as fp:
            a = csv.writer(fp, delimiter=',')
            
            for i in range(0, 1):                                           # Number of iteration all program
                print("-------------------------------------")
                mySolution.savings_algorithm(1)
                print(mySolution)
                a.writerows([['0', str(mySolution.objective)]])
        
                for j in range(0, 10):                                      # Nuber of relocate and exchange iteration
                    for m in range(0, 2):                                   # Nuber of relocate iteration
                        k += 1
                        mySolution.relocate(0.7, 0.0001)
                        mySolution.get_objective()
                        mySolution.cleare_tabu_relocate(50)
                        print(mySolution)
                        a.writerows([[k, str(mySolution.objective)]])
                        if(bestObjectiv > mySolution.objective):            # If actual solution is best solution then add to best Solution
                            bestObjectiv = mySolution.objective
                            bestSolution = mySolution

                    for n in range(0, 2):                                   # Nuber of  exchange iteration
                        k += 1
                        mySolution.exchange(0.7, 0)
                        mySolution.get_objective()
                        mySolution.clear_tabu_exchange(1000000)
                        print(mySolution)
                        a.writerows([[k, str(mySolution.objective)]])
                        if(bestObjectiv > mySolution.objective):            # If actual solution is best solution then add to best Solution
                            bestObjectiv = mySolution.objective
                            bestSolution = mySolution
            bestSolutions.append(bestSolution)




            


