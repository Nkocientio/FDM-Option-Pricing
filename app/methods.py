import streamlit as st
from intermediate import *

class FDM_Method(FDM_Start):
    def __init__(self,style,optionType,spotPrice,strike,expire,rfRate,divRate,vol,tSteps,sSteps,sMin,sMax,method,BC,dates,w=1.1,tol=1e-6):
        super().__init__(style,optionType,spotPrice,strike,expire,rfRate,divRate,vol,tSteps,sSteps,sMin,sMax,method,BC,dates,w,tol)
        self.loopCount = 0
        self.mayNotConverge = False
    def explicitMethod(self):
        for j in reversed(range(self.tSteps)):
            nextCol = self.A.dot(self.grid[1:-1,j+1])
            nextCol[0] += self.bcRef*self.alpha*self.grid[0,j+1]
            nextCol[-1] += self.bcRef*self.gamma*self.grid[-1,j+1]
            if self.exerciseNodes[j]:
                self.grid[1:-1,j] = np.maximum(nextCol,self.payoff[1:-1])
            else:
                self.grid[1:-1,j] = np.maximum(nextCol,0)

    def CrankImplicitMethod(self):
        w = self.omega
        sSteps = self.sSteps
        payoff = self.payoff
        diag  = self.A.diagonal(0) # main diagonal
        upper = self.A.diagonal(1)
        lower = self.A.diagonal(-1) 
        
        nextCol = self.grid[1:-1, -1].copy()
        for j in reversed(range(self.tSteps)):
            colLoop = 0
            if self.method == 'Implicit':
                nextCol[0] -= self.bcRef*self.alpha*self.grid[0,j]
                nextCol[-1] -= self.bcRef*self.gamma*self.grid[-1,j]
            elif self.method == 'Crank':
                nextCol = self.B.dot(nextCol) # Matrix B * nextCol
                nextCol[0] -= self.bcRef*self.alpha*(self.grid[0,j+1] + self.grid[0,j])
                nextCol[-1] -= self.bcRef*self.gamma*(self.grid[-1,j+1] + self.grid[-1,j])

            if self.exerciseNodes[j]:
                currVal = nextCol.copy() # initial guess
                oldVal = np.empty_like(currVal)
                while True:
                    colLoop += 1
                    oldVal[:] = currVal 
                    currVal[0] = np.maximum(w * (nextCol[0] - upper[0] * oldVal[1]) / diag[0] + (1 - w) * oldVal[0],payoff[1])

                    for i in range(1,sSteps-2):
                        self.loopCount += 1
                        currVal[i] = np.maximum(w * (nextCol[i] - lower[i-1] * currVal[i-1]- upper[i] * oldVal[i+1]) / diag[i]+ (1 - w) *oldVal[i],payoff[i+1])
                        
                    currVal[-1] = np.maximum(w * (nextCol[-1] - lower[-1] * currVal[-2]) / diag[-1] + (1 - w) * oldVal[-1],payoff[-2])

                    if np.max(np.abs(currVal - oldVal)) < self.tol:
                        break
                    elif colLoop > self.tSteps*15:
                        self.mayNotConverge = True
                        break
            
                nextCol = currVal
            else:
                nextCol = np.maximum(sp.linalg.spsolve(self.A,nextCol),0)
                
            self.grid[1:-1, j] = nextCol

    def blackScholes(self):
        discount = np.exp(-self.rfRate*self.expire)
        forwardPrice = self.spotPrice*np.exp((self.rfRate-self.divRate)*self.expire) 
        volRootT = self.vol*np.sqrt(self.expire)
        
        d1 = np.log(forwardPrice/self.strike) / volRootT + 0.5*volRootT
        d2 = d1 - volRootT
        
        price = self.optionRef * discount * (forwardPrice*norm.cdf(self.optionRef*d1) - self.strike*norm.cdf(self.optionRef*d2))
        return price
        
    def price(self):
        index = self.sSteps*self.spotPrice/self.sMax # Row_Ref of where the price would be on first column
        highIndex = int(np.ceil(index))
        lowIndex = max(highIndex-1,0)
        if self.method == 'Implicit' or self.method == 'Crank':
            FDM_Method.CrankImplicitMethod(self)
        else:
             FDM_Method.explicitMethod(self)
            
        premium = np.interp(index,np.array([lowIndex,highIndex]),np.array(self.grid[lowIndex:highIndex+1,0]))
        return premium
