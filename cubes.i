C ====================================================================== C
C Created by SuperMC/MCAM Converter, version 5.2 
C MCAM, Monte Carlo Automatic Modeling Program for Radiation Transport Codes.
C Copyright 1999-2015, FDS Team, China
C FDS Team, China.
C ACIS version:24.0.1
C ====================================================================== C
C Model Name  : /cubes.i
C Start Time  : 2023/06/19 5:06:51 PM:Monday
C All Elapsed Time: 0 seconds.
C Solids Analysis Time£º0 seconds.
C Model Size  : 2 Cell(s), 15 Surface(s)
C
C ======================================================================
1     0   ( 3 8 -6
          -13 14 -2)                                       
          IMP:N=1.0  IMP:P=1.0  IMP:E=0.0 TMP=2.53005e-008   
2     0   ( 3 -2 -12 13 9 -7)                                       
          IMP:N=1.0  IMP:P=1.0  IMP:E=0.0 TMP=2.53005e-008   
3     0   ( -1 4 -5 10 -11 15)((-3:-8:6:13:-14:2))((-3:2:12:-13:-9
          :7))                                                             
          IMP:N=1.0  IMP:P=1.0  IMP:E=0.0            $void reach face limit
4     0   (11:-15:-10:-4:5:1)                                       
          IMP:N=0  IMP:P=0  IMP:E=0          
          $The outer cell

C ===========================SURFACE Card=============================== C
1        PX   101.000000000000000                                           
2        PX   0.200000000000000                                             
3        PX   -0.200000000000000                                            
4        PX   -101.000000000000000                                          
5        PY   101.000000000000000                                           
6        PY   0.400000000000000                                             
7        PY   0.300000000000000                                             
8        PY   0.0                                                           
9        PY   -0.100000000000000                                            
10       PY   -101.000000000000000                                          
11       PZ   101.000000000000000                                           
12       PZ   0.400000000000000                                             
13       PZ   0.0                                                           
14       PZ   -0.400000000000000                                            
15       PZ   -101.000000000000000                                          

SDEF POS 0 0 0
mode  n  
nps  10000  
phys:n  150  0  
cut:n  1.0e+99  0.0  -0.50  -0.25  0.0  
rand  gen=1  seed=19073486328125  stride=152917  hist=1  
