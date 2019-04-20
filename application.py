import psycopg2
import database as db

#first prompt to print at the top of the main loop
def initialPrompt():
    print("\nMAIN: Please select one of the following query categories:\n"+\
            "\t1. Specific procedure lookup\n"+\
            "\t2. Hospital complications lookup\n"+\
            "\t3. Find average statistics for an area\n"+\
            "\tEXIT. Exit the program\n")

#hospitalQuery not yet implemented
if __name__ == "__main__":
    while(1):
        functions = {"1": db.procedureQuery,"2": db.compQuery,"3":db.avgQuery}
        initialPrompt()
        command = db.safeInput()
        if (command == "EXIT" ):
            break
        elif (command not in ["1","2","3"]):
            print("ERROR: invalid input")
        else:
            functions[command]()
