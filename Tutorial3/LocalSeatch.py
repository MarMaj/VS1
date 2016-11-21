import CW_Savings
import csv

files25 = ["solomon_100//C101.txt", "solomon_25/C201.txt", "solomon_25/R101.txt", "solomon_25/R201.txt", "solomon_25/RC101.txt", "solomon_25/RC201.txt"]
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
            a.writerows([['0', str(mySolution.objective)]])



            for i in range(0, 5):                                           # Number of iteration all program
                print("-------------------------------------")
                mySolution.savings_algorithm(1)
                print(mySolution)
                for j in range(0, 3):                                      # Nuber of relocate and exchange iteration
                    for m in range(0, 6):                                   # Nuber of relocate iteration
                        k += 1
                        mySolution.relocate(0.7, 0.0001)
                        mySolution.get_objective()
                        mySolution.cleare_tabu_relocate(1000)
                        mySolution.GlobalTabu += mySolution.TabuRelocate    # optional
                        mySolution.clear_global_tabu(1000000000)            # optional
                        print(mySolution)
                        a.writerows([[k, str(mySolution.objective)]])
                        if(bestObjectiv > mySolution.objective):            # If actual solution is best solution then add to best Solution
                            bestObjectiv = mySolution.objective
                            bestSolution = mySolution
                    for n in range(0, 2):                                   # Nuber of  exchange iteration
                        k += 1
                        mySolution.exchange(0.7, 0.0000001)
                        mySolution.get_objective()
                        mySolution.clear_tabu_exchange(1000)
                        mySolution.GlobalTabu += mySolution.TabuRelocate    # optional
                        mySolution.clear_global_tabu(1000000000)            # optional
                        print(mySolution)
                        a.writerows([[k, str(mySolution.objective)]])
                        if(bestObjectiv > mySolution.objective):            # If actual solution is best solution then add to best Solution
                            bestObjectiv = mySolution.objective
                            bestSolution = mySolution
                    for o in range(0, 4):
                        k += 1
                        mySolution.two_opt(0.7, 0.000000001)
                        mySolution.get_objective()
                        mySolution.clear_tabu_two_opt(1000)
                        mySolution.GlobalTabu += mySolution.TabuRelocate    # optional
                        mySolution.clear_global_tabu(1000000000)            # optional
                        print(mySolution)
                        a.writerows([[k, str(mySolution.objective)]])
                        if(bestObjectiv > mySolution.objective):            # If actual solution is best solution then add to best Solution 9
                            bestObjectiv = mySolution.objective
                            bestSolution = mySolution
            bestSolutions.append(bestSolution)
        break
    break


            


