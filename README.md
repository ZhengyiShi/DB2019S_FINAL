# DB2019S_FINAL  
Database System 2019 Spring Final Project  
  
## Environment  
Python 3.6  
psycopg2, numpy, pandas  
  
## Files:  
load_data.py - CSV loader by Ian  
Utils.py, XMLparser.py, MainDebug.py - XML loader by Simon  
  
## Members:  
Yihao Huang  
Ian Diaz  
Hantian (Simon) Jiang  
Zhengyi Shi  

1. Get compFile and paymentFile from datasets.txt. (preferably putting them directly in the folder with the other provided files)
1. Run hospital.sql to set up the database 
2. Run load_data.py to populate the database. 
   Make sure to change "compfile" and "paymentfile" in load_data to reflect location and name of the csv's
   (placing the two csv's in the same folder as load_data.py with the default names should work)