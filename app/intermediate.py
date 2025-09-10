import numpy as np
import pandas as pd
from datetime import datetime
from scipy.stats import norm
import scipy.sparse as sp
from code_excel import print_excel,get_workbook_as_bytes

class FDM_Start():
    def __init__(self,style,optionType,spotPrice,strike,expire,rfRate,divRate,vol,tSteps,sSteps,sMin,sMax,method,BC,dates,w,tol):
        self.optionType = optionType
        self.style = style
        self.spotPrice = spotPrice
        self.strike =strike
        self.expire = expire
        self.rfRate,self.divRate = rfRate,divRate
        self.vol = vol
        self.sMin,self.sMax = sMin, sMax
        self.sSteps = int(sSteps) 
        self.method=method
        self.BC = BC
        self.omega = w
        self.tSteps = self.timeSteps(tSteps)
        self.tolN = self.tolerance(tol)
        self.tol = 10**(-self.tolN)
        self.bcRef = 0 if BC == 'Neumann' else 1
        self.optionRef = 1 if optionType =='Call' else -1
        self.dt, self.ds = self.expire/self.tSteps , self.sMax/self.sSteps
        self.exercise_dates = dates
        self.exerciseNodes = self.exerciseOn()
        self.assetV = np.linspace(self.sMin, self.sMax, self.sSteps+1)
        self.timeV = np.linspace(0, self.expire, self.tSteps+1)
        self.grid = np.zeros(shape=(self.sSteps+1, self.tSteps+1))
        self.boundries()
        self.setMatrix()

    def timeSteps(self,tSteps):
        if self.method == 'Explicit':
            dt = 0.99/(self.sSteps*self.vol)**2
            Nt = int(np.ceil(self.expire/dt))
            # if tSteps < Nt:
            #     return Nt
        return int(tSteps)

    def tolerance(self,tolN):
        n = (self.sSteps+self.tSteps)//200
        newTolN = 12-n
        if tolN < newTolN:
            return tolN
        else:
            return max(4,newTolN)

    def exerciseOn(self):
        n = self.tSteps + 1 
        self.b_dates = []
        if self.style == 'American':
            return np.full(n, True)
        elif self.style == 'Bermudan':
            arr = np.full(n, False)
            today = np.datetime64(datetime.now().strftime('%Y-%m-%d'))
            self.exercise_dates = np.array(self.exercise_dates, dtype='datetime64[D]')
            for date in self.exercise_dates:
                days = (date - today) 
                yrs = days.astype('timedelta64[D]').astype(int) / 365
                node = int(yrs/self.dt)
                arr[min(node,n-1)] = True
                self.b_dates.append(f"{date.astype(datetime).strftime('%d %b %Y')} ({node})")
            return arr
        else:
            arr = np.full(n, False)
            arr[-1] = True
            return arr  #Eur style

    def boundries(self):
        self.payoff =  np.maximum(self.optionRef*(self.assetV - self.strike), 0)
        self.grid[:, -1] = self.payoff
        for j in range(self.tSteps):
            t_factor = self.dt * (self.tSteps - j)
            if self.exerciseNodes[j]:
                strike_val = self.strike
                sMin_discounted = self.sMin
                sMax_discounted = self.sMax
            else:
                strike_val = self.strike * np.exp(-self.rfRate * t_factor)
                sMin_discounted = self.sMin * np.exp(-self.divRate * t_factor)
                sMax_discounted = self.sMax * np.exp(-self.divRate * t_factor)
                
            self.grid[0, j] = max(self.optionRef * (sMin_discounted - strike_val), 0)
            self.grid[-1, j] = max(self.optionRef * (sMax_discounted - strike_val), 0)

    def setCoeffients(self):
        seq = np.arange(1,self.sSteps)
        self.a = 0.5 * self.dt * ((self.vol * seq) ** 2 - (self.rfRate - self.divRate) * seq)
        self.b = -self.dt * ((self.vol * seq) ** 2 + self.rfRate)
        self.c = 0.5 * self.dt * ((self.vol * seq) ** 2 + (self.rfRate - self.divRate) * seq)
    
    def setMatrix(self):
        self.setCoeffients()
        if self.method == 'Implicit':
            self.a,self.b,self.c = -self.a,-self.b,-self.c
        elif self.method == 'Crank':
            self.a, self.b, self.c = -self.a/2, -self.b/2, -self.c/2

            self.a2, self.b2, self.c2 = -self.a, -self.b, -self.c
            self.B = sp.diags_array([np.roll(self.a2,-1), 1+self.b2, self.c2], offsets=[-1, 0, 1],shape=(self.sSteps-1,self.sSteps-1)).toarray()
            if self.bcRef==0:
                self.B[0,0] += 2*self.a2[0]
                self.B[0,1] -= self.a2[0]
                self.B[-1,-2] -=  self.c2[-1]
                self.B[-1,-1] += 2*self.c2[-1]

        self.alpha,self.gamma = self.a[0], self.c[-1]
        self.A = sp.diags_array([np.roll(self.a,-1), 1+self.b, self.c], offsets=[-1, 0, 1],shape=(self.sSteps-1,self.sSteps-1),format='csc')
        if self.bcRef == 0:
            self.A[0,0] += 2*self.a[0]
            self.A[0,1] -= self.a[0]
            self.A[-1,-2] -=  self.c[-1]
            self.A[-1,-1] += 2*self.c[-1]

    def excel_values(self,bsPrice,price):
        _exercised = (self.exerciseNodes) & (self.grid == self.payoff.T.reshape(-1,1)) & (self.grid > 0)
        if self.method != 'Crank':
            self.B = self.A
            
        params= [self.style,self.sMin,self.sMax,self.sSteps,self.tSteps,self.method,self.BC,self.omega,self.tolN,self.optionType,self.A,self.B,self.grid,_exercised,self.spotPrice,self.strike,self.expire,self.rfRate,self.divRate,self.vol,price,bsPrice,self.b_dates,[self.alpha,self.gamma]]
        wb = print_excel(*params)
        return get_workbook_as_bytes(wb)
    
