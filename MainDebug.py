import pandas
import numpy
import psycopg2
import Utils
from XMLparser import XMLparser

#For testing purposes
if __name__ == "__main__":
    
    print("Framing Payment Data...", Utils.DATA_HOSPITAL_PAYMENT)
    p1 = XMLparser(Utils.DATA_HOSPITAL_PAYMENT, Utils.PaymentTags)
    f1 = p1.parse()
    print("Done.")
    while(True):
        flag = input("Print out portion of data?(y/n)")
        if(flag == "y"):
            print(f1)
            break
        if(flag == "n"):
            break
    
    print("Framing Comp&Death Data...", Utils.DATA_COMPLICATIONS)
    p2 = XMLparser(Utils.DATA_COMPLICATIONS, Utils.CompTags)
    f2 = p2.parse()
    print("Done.")
    while(True):
        flag = input("Print out portion of data?(y/n)")
        if(flag == "y"):
            print(f1)
            break
        if(flag == "n"):
            break
    