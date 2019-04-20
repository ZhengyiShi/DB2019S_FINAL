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
def locationInner():
        zip = "ERROR"
        state = "ERROR"
        city = "ERROR"
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
        sort = "ERROR" #how to sort results
        care = "ERROR" #type of care to search for

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
        if (care == "BACK"): #BACK TO THE MAIN LOOP
            break

        paystr = paytypes[int(care)-1]
        compstr = comptypes[int(care)-1]
        destq = locationInner() #here so the client gets the prompts in the correct order

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

def compQuery():
    conn = psycopg2.connect("dbname = 'postgres' user = 'postgres'")
    cur = conn.cursor()
    while(1):
        response="ERROR"
        num = "ERROR"
        print("\nPlease select a hospital to search for\n"+\
              "or type BACK to return to previous prompt\n")
        while(response == "ERROR"):
            response = safeInput()
            if (response == "ERROR"):
                print("ERROR: invalid input")
        if (response == "BACK"):
            break
        searchq = "SELECT DISTINCT hospital.hospitalName, hospital.zip FROM hospital, hospital_comp WHERE hospital.providerID = hospital_comp.providerID AND hospital.hospitalName LIKE '%"+response+"%';"
        cur.execute(searchq)
        rows = cur.fetchall()

        if(rows): #We have some matches, time to ask which hospital
            print("\n   NAME                                 ZIP CODE")
            count =1
            for a,b in rows:
                print("{:36}".format(str(count)+". "+a)[:36]+"    "+b)
                count+=1
            print("\nFrom the above results, please select a hospital to query\n")
            while(num == "ERROR"):
                num = safeInput()
                if (not num.isdigit()):
                    num = "ERROR"
                    print("ERROR: invalid input")
                elif (int(num) not in range(1,count)):
                    num = "ERROR"
                    print("ERROR: invalid input")
            num = int(num)-1
            hosp = rows[num][0]
            zip = rows[num][1]
            finalq = "SELECT hospital.hospitalName, hospital.zip, hospital_comp.measureID, hospital_comp.compScore,hospital_comp.quantity "+\
                        "FROM hospital, hospital_comp " + \
                        "WHERE hospital.providerID = hospital_comp.providerID " + \
                        "AND hospital.zip = '"+zip+"' " + \
                        "AND hospital.hospitalName like '"+hosp+"%'"
            print(finalq)
            cur.execute(finalq)
            rows = cur.fetchall()
            print("\nSTATISTICS FOR: "+hosp+"")
            print("COMPLICATION                                    SCORE     SUBJECTS")
            for a,b,c,d,e in rows:
                if(d == -1 or e == -1):
                    continue
                if (c == "COMP_HIP_KNEE"):
                    print("{:48}".format("Complications for hip/knee patients")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "MORT_30_AMI"):
                    print("{:48}".format("Death rate for heart attack patients")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "MORT_30_CABG"):
                    print("{:48}".format("Death rate for CABG surgery patients")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "MORT_30_COPD"):
                    print("{:48}".format("Death rate for COPD patients")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "MORT_30_HF"):
                    print("{:48}".format("Death rate for heart failure patients")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "MORT_30_PN"):
                    print("{:48}".format("Death rate for pneumonia patients")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "MORT_30_STK"):
                    print("{:48}".format("Death rate for stroke patients")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_10_POST_KIDNEY"):
                    print("{:48}".format("Kidney injuries post-operation")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_11_POST_RESP"):
                    print("{:48}".format("Respiratory failure post-operation")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_12_POSTOP_PULMEMB_DVT"):
                    print("{:48}".format("Serious blood clot post-operation")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_13_POST_SEPSIS"):
                    print("{:48}".format("Blood stream infection post-operation")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_14_POSTOP_DEHIS"):
                    print("{:48}".format("A wound re-opened post operation")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_15_ACC_LAC"):
                    print("{:48}".format("Accidental cuts during treatment")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_3_ULCER"):
                    print("{:48}".format("Pressure sores")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_4_SURG_COMP"):
                    print("{:48}".format("Deaths post-operation that were treatable")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_6_IAT_PTX"):
                    print("{:48}".format("Collapsed lungs due to treatments")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_8_POST_HIP"):
                    print("{:48}".format("Broken hip from fall post-procedure")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_90_SAFETY"):
                    print("{:48}".format("Serious general complications")+"{:6}".format(str(d))+"    "+str(e))
                elif (c == "PSI_9_POST_HEM"):
                    print("{:48}".format("Hemorrhage or Hematoma rate")+"{:6}".format(str(d))+"    "+str(e))
        else: #no matches, loop back
            print("\nNo results found\n")

def Safest_Hospital():
    conn = psycopg2.connect("dbname = 'postgres' user = 'postgres'")
    cur = conn.cursor()
    while(1):
        care = "ERROR" #type of care to search for

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
        if (care == "BACK"): #BACK TO THE MAIN LOOP
            break

        destq = locationInner() #here so the client gets the prompts in the correct order

        comptype = comptypes[int(care)-1]

        compq = """(SELECT hospital.providerID, hospitalName, address, zip, compScore as score 
                        FROM hospital_comp INNER JOIN hospital
                        ON hospital_comp.providerID = hospital.providerID
                        WHERE measureID LIKE '"""+ comptype + "') as comp"

        finalq = "SELECT comp.hospitalName, score, loc.address, loc.city, loc.state, comp.zip, loc.phone"+ \
                    " FROM " + destq + compq + \
                    " WHERE loc.pid = comp.providerID ORDER BY score ASC;"
        
        cur.execute(finalq)
        rows = cur.fetchall()
        if(not rows):
            print("\nNo results found")

        safest = rows[0][1]
        for row in rows:
            if(row[1] == safest): #results found
                #pid,name,address,city,state,phone,cost,score
                print("\nNAME                SCORE    ADDRESS                         CITY            STATE    ZIP      PHONE")
                print("{:<16}".format(row[0])[:16] + "    " + "{:<5}".format(row[1])[:5] + "    " +"{:<30}".format(row[2])[:28]+"    "+"{:<12}".format(row[3])[:12]+"    "+"{:<5}".format(row[4])[:5]+"    "+"{:<5}".format(row[5])[:5]+ "    "+row[6] )
        

def Search_by_Budget():
    conn = psycopg2.connect("dbname = 'postgres' user = 'postgres'")
    cur = conn.cursor()
    while(1):
        care = "ERROR" #type of care to search for

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
        if (care == "BACK"): #BACK TO THE MAIN LOOP
            break

        upper = "ERROR"
        lower = "ERROR"
        while(1):
            print("\nBudget: Enter the UPPER limit of budget for this type of care/service:\n")
            while(upper == "ERROR"):
                upper = safeInput()
                if (not upper.isdigit()):
                    print("ERROR: invalid input")
                    upper = "ERROR"
            
            print("\nBudget: Enter the LOWER limit of budget for this type of care/service:\n")
            while(lower == "ERROR"):
                lower = safeInput()
                if (not lower.isdigit()):
                    print("ERROR: invalid input")
                    lower = "ERROR"
            if (upper >= lower):
                break
            else:
                print("ERROR: upper limit is less than lower limit")
                upper = "ERROR"
                lower = "ERROR"

        destq = locationInner() #here so the client gets the prompts in the correct order
        
        paytype = paytypes[int(care)-1]
        payq = """(SELECT hospital.providerID, paymentAmount, zip, hospitalName
                    FROM hospital INNER JOIN hospital_payment 
                    ON hospital.providerID = hospital_payment.providerID
                    WHERE paymentAmount <= """ + upper + " AND paymentAmount >= "+ lower + ") as pay"""

        print(payq)
        finalq = "SELECT pay.hospitalName, paymentAmount, loc.address, loc.city, loc.state, pay.zip, loc.phone"+ \
                    " FROM " + destq + payq +\
                    " WHERE loc.pid = pay.providerID ORDER BY paymentAmount ASC;"
        print(finalq)
        cur.execute(finalq)
        rows = cur.fetchall()

        if(not rows):
            print("\nNo results found")

        count = 1
        page = 0
        for row in rows:
            if (count <= 10):
                #pid,name,address,city,state,phone,cost,score
                print("\nNAME                COST    ADDRESS                         CITY            STATE    ZIP      PHONE")
                print("{:<16}".format(row[0])[:16] + "    " + "{:<5}".format(row[1])[:5] + "   " +"{:<30}".format(row[2])[:28]+"    "+"{:<12}".format(row[3])[:12]+"    "+"{:<5}".format(row[4])[:5]+"    "+"{:<5}".format(row[5])[:5]+ "    "+row[6])
                count += 1
            else:
                print("\nMessages %d to %d of %d" %(page*10+1, (page+1)*10, len(rows)))
                print("Type 1 to go next page or type 2 to return to previous prompt") 
                go_next_page = "ERROR"
                while(go_next_page == "ERROR"):
                    go_next_page = safeInput()
                    if (care not in ["1","2"]):
                        print("ERROR: invalid input")
                        care = "ERROR"
                if (go_next_page == "1"):
                    count = 1
                    page += 1
                else:
                    break
        
        if (count != 10):
                #pid,name,address,city,state,phone,cost,score
                print("\nMessages %d to %d of %d" %(page*10+1, len(rows), len(rows)))
