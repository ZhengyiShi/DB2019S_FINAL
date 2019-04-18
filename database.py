import psycopg2
import psycopg2.extras
import csv
import os
import Utils

#Constants
paytypes= ["PAYM_%%_AMI","PAYM_%%_HF","PAYM_%%_HIP_KNEE","PAYM_%%_PN"]
comptypes = ["MORT_%%_AMI","MORT_%%_HF","COMP_HIP_KNEE","MORT_%%_PN"]

#This is checked for every user input to prevent SQL injection
def safeInput():
    text = input(">")
    if ";" in text:
        return "ERROR"
    return text
#Creates part of the inner query pertaining to location
def locationInner(zip,state,city):
    #Formulate location inner query
    if (zip != ""): #zip search
        deststr = "WHERE hospital.zip = '" + zip +"' AND city.zip = '"+zip+"'"
    elif (state != ""): #state
        deststr = "WHERE hospital.zip = city.zip AND city.stateName = '" + state + "'"
        if (city != ""): #city
            deststr = deststr + "AND city.cityName = '" + city + "'"
    else:
        return "(SELECT hospital.providerID as pid, hospitalName as name, hospital.address as address,city.cityName as city, city.stateName as state, hospital.phone as phone from hospital,city WHERE hospital.zip = city.zip) as loc,"
    deststr = "(SELECT hospital.providerID as pid, hospitalName as name, hospital.address as address,city.cityName as city, city.stateName as state, hospital.phone as phone FROM hospital, city " + deststr + ") as loc,"
    return deststr

#Determines the order of the results displayed
def orderInner(mode):
    #NOTE LOWER SCORE IS BETTER CARE
    arr = [ "ORDER BY loc.name;", \
            "ORDER BY paym.cost;", \
            "ORDER BY paym.cost DESC;", \
            "ORDER BY comp.score;", \
            "ORDER BY comp.score DESC;"]
    return arr[mode-1]
'''
#This allows a user to search for 1 of four specific measures and provide either:
    -ZIP code
    -State (specified by leaving zip and city empty)
    -City and State (specified by leaving zip empty)
    -No location (specified by leaving the prompts empty)
    Providing a ZIP gives an exact location, so state/city are skipped, and you can access the nOtherwise
    by leaving the field blank when prompted
And choose to order their query by
    -alphabetical order of hospital name
    -cheapest/most expensive
    -least/most safe

PROCEDURE:
1. Get inputs from user realted to location,medical procedure, and sort order
2. Build SQL query out of destq,payq,compq,and orderq
3. Execute query and return/print

EXAMPLE FINAL query
SELECT loc.pid,loc.name,loc.address, loc.city, loc.state, loc.phone, paym.cost,comp.score
FROM (SELECT hospital.providerID as pid, hospitalName as name, hospital.address as address,city.cityName as city,
        city.stateName as state, hospital.phone as phone
	    FROM hospital,city) as loc,
	 (SELECT paymentAmount as cost,providerID
		FROM hospital_payment
		WHERE paymentID like 'PAYM_%%_AMI') as paym,
	 (SELECT compScore as score,providerID
		FROM hospital_comp
		WHERE measureID like 'MORT_%%_AMI') as comp
WHERE loc.pid = paym.providerId
AND loc.pid = comp.providerID
ORDER BY loc.name;
'''
def procedureQuery():
    conn = psycopg2.connect("dbname = 'postgres' user = 'postgres'")
    cur = conn.cursor()
    while(1):
        care = "ERROR"
        state = "ERROR"
        city = "ERROR"
        zip = "ERROR"
        sort = "ERROR"

        #initial prompt
        print("\nPROCEDURE SEARCH: Choose a type of care/service to search for:\n"+
                "\t1. Heart attack-related care\n"+\
                "\t2. Heart failure-realted care\n"+\
                "\t3. Hip/Knee replacement\n"\
                "\t4. Pneumonia treatment\n"\
                "\tBACK. Return to MAIN prompt\n")
        while(care == "ERROR"):
            care = safeInput()
            if (care not in ["1","2","3","4","BACK"]):
                print("ERROR: invalid input")
                care = "ERROR"
        if (care == "BACK"):
            break
        paystr = paytypes[int(care)-1]
        compstr = comptypes[int(care)-1]

        #INFORMATION block
        #get the zip code
        print("\nIf you know the zip code you want to search, enter here. \nOtherwise, please leave blank\n")
        while (zip == "ERROR"):
            zip = safeInput()
            if (len(zip) > 0 and len(zip) != 5):
                print("ERROR: invalid input")
                zip = "ERROR"
        if (zip == ""):
            #Get the State
            print("\nIf you want to search a specific state for hospitals, enter here. \nOtherwise, please leave blank\n")
            while (state == "ERROR"):
                state = safeInput()
                if (len(state) >0 and len(state) != 2):
                    print("ERROR: invalid input")
                    state = "ERROR"
            #Get the city if state wasn't empty
            if (state != ""):
                print("\nIf you want to search a specific city, enter here. \nOtherwise, please leave blank\n")
                while(city == "ERROR"):
                    city = safeInput()
        #Order by
        print("\nPlease specify how the data is ordered:\n"+\
                "\t1. Alphabetically, by hospital name\n"+\
                "\t2. Cheapest procedure first\n"+\
                "\t3. Most expensive procedure first\n"+\
                "\t4. Best safety score first\n"+\
                "\t5. Worst safety score first\n")
        while(sort == "ERROR"):
            sort = safeInput()
            if (sort not in ["1","2","3","4","5"]):
                print("ERROR: invalid input")
                sort = "ERROR"

        #QUERY BUILD BLOCK
        destq = locationInner(zip,state,city)
        payq = "(SELECT paymentAmount as cost,providerID FROM hospital_payment WHERE paymentID like '"+paystr+"') as paym,"
        compq = "(SELECT compScore as score,providerID FROM hospital_comp WHERE measureID like '"+compstr+"') as comp"
        orderq = orderInner(int(sort))

        finalq = "SELECT loc.pid,loc.name,loc.address, loc.city, loc.state, loc.phone, paym.cost,comp.score" + \
                 " FROM " + destq + payq + compq + \
                 " WHERE loc.pid = paym.providerId AND loc.pid = comp.providerID " + \
                 orderq
        #QUERY EXECUTION BLOCK
        cur.execute(finalq)
        rows = cur.fetchall()
        if(rows): #results found
            #pid,name,address,city,state,phone,cost,score
            print("\nNAME                COST       SCORE    ADDRESS                         CITY            STATE    PHONE")
            for a,b,c,d,e,f,g,h in rows:
                print("{:<16}".format(b)[:16] + "    " + "{:<7}".format(g)[:7] + "    " +"{:<5}".format(h)[:5]+"\t"+"{:<30}".format(c)[:28]+"    "+"{:<12}".format(d)[:12]+"\t"+"{:<5}".format(e)[:5]+ "    "+f )
        else:
            print("\nNo results found")

def hospitalQuery():
    print("This is hospitalQuery()")
