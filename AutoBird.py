import argparse                                 # Argument settings
import messagebird                              # MessageBird's API
import configparser                             # Writing and reading .ini config files and logs
from datetime import datetime                   # Time settings
from colorama import init, Fore, Back, Style    # Font coloring

init(convert=True)  # Coloring for windows systems
appversion = "v1.1" # App version variable. Version goes into log files.

# Shortcuts for coloring
err = Fore.RED+"[-] "+Style.RESET_ALL
pos = Fore.GREEN+"[+] "+Style.RESET_ALL

# Opening bannner
print("\n-----------------------------------------")
print("- AutoBird "+appversion+" By github.com/n0khodsia -")
print("-----------------------------------------")

# Define all arguments and help menu
parser = argparse.ArgumentParser(description='This is a tool for sending SMS via MessageBird')
parser.add_argument('-a', '--apikey', action='store', dest='apikey', help='Your messagebird api key')
parser.add_argument('-s', '--sender', action='store', dest='sender', help='Your SMS Sender ID, an alphanumeric name')
parser.add_argument('-n', '--number', action='store', dest='number', help='A single number to send to')
parser.add_argument('-nl', '--numlist', action='store', dest='list', help='Load a list of numbers from a file, one number per line')
parser.add_argument('-m', '--message', action='store', dest='message', help='SMS message content')
parser.add_argument('-sv', '--save', action='store_true', default=False, dest='save', help='Save action for future use')
parser.add_argument('-l', '--load', action='store', dest='filename', help='Load from A saved AutoBird file')
parser.add_argument('--confirm', action='store_true', default=False, dest='confirm', help='Send the message instantly without further confirmation')
parser.add_argument('-v', '--verbose', action='store_true', default=False, dest='verbose', help='Show more info when sending messages (for multiple numbers only)')
args, leftovers = parser.parse_known_args()

# Define Main Function
def main():
    if args.apikey is not None: #If -a argument was supplied, define variables from args
        api_key = args.apikey
        sender_name = args.sender
        to_number = args.number
        list_number = args.list
        sms_message = args.message

    elif args.filename is not None: # If --load was supplied, define variables from .log file
        try:
            print("Loading file:",args.filename)
            rlog = configparser.ConfigParser()
            rlog.read(format(args.filename))
            api_key = (rlog['AutoBird']['LOG_API_KEY'])
            sender_name = (rlog['AutoBird']['LOG_SENDER'])
            try: # Check if file has one number or list of numbers
                to_number = (rlog['AutoBird']['LOG_NUMBER'])
            except:
                to_number = None
                list_number = (rlog['AutoBird']['LOG_NUMFILE'])
            sms_message = (rlog['AutoBird']['LOG_MESSAGE'])
        except:
            print("Cannot load file or it's corrupt. Usage:\nfilename.py --load <AutoBird_name_date.ini>\n")
            return 1

    else:
        # If no api key / load from file was supplied, exit
        print("Please enter --apikey or --load an existing .log file.\nYou can also enter -h/--help for help menu.")
        return 1

    # Making sure arguments aren't mixed in a problematic way
    if args.apikey is not None and args.filename is not None:
        print(err+"Cannot --load a file and enter arguemnts.")
        return 1
    if args.save is True and args.filename is not None:
        print(err+"Cannot --load a file and --save a file.")
        return 1
    if args.number is not None and args.list is not None:
        print(err+"Choose either --list OR --number.")
        return 1

    # Making sure values are not blank
    if sender_name is None:
        print(err+"Please prodive --sender name")
        return 1
    if to_number is None and list_number is None:
        print(err+"Please provide --number or --numlist")
        return 1
    if sms_message is None:
        print(err+"Please enter a --message")
        return 1

    # Making sure values are matching SMS sending standards
    if sender_name.isalpha() == False:
        print(err+"Sender name must be alphanumeric.")
        return 1
    if to_number is not None and to_number.isdigit() is False: # Do not run this test if a list is provided
        print(err+"Number must contain digits only. A plus [+] is automatically added.")
        return 1

    # If a list of numbers is used, make sure the file exists and is readable
    if list_number is not None:
        try:
            open(list_number)
            open(list_number).close()
        except:
            print(err+"Could not find/read from number file: "+list_number)
            return 1

    # Print a summary of the upcoming action
    print ("Your API Key:",api_key) # Should be removed in final version, as API KEY is a sensitive information
    print ("Sender ID:",sender_name)

    if to_number is not None: # If a single number is chosen, print it
        print ("Recepient's phone is: +",to_number)

    elif list_number is not None: # If a list of numbers is chosen
        numfile = open(list_number)
        numcount = 0 # Counting the amount of numbers (lines) in file
        for line in numfile: # loop to get get the amount of numbers
            numcount += 1
        print ('Found ('+str(numcount)+') numbers in file:',list_number)
        numfile.close()

    print ("Your message is: \n\n",sms_message,"\n")
    if args.save is True: # if --save was provided, run save function
        save_message()
    # Sending the SMS, calling function
    send_sms(to_number, api_key, sender_name, sms_message, list_number, numcount)

# Defining sms function
def send_sms(to_number, api_key, sender_name, sms_message, list_number, numcount):
    if args.confirm is False: # Ask for confirmation if --confirm was not supplied
        ask_verify = input("\nReady to send it? (y/n): ")
    if args.confirm == True or ask_verify.lower() == "y":

        if to_number is not None: # if only one number was provided
            ## MessageBirds API in action
            msgbrd_client = messagebird.Client(api_key)
            try:
                msg = msgbrd_client.message_create(sender_name, '+'+to_number, sms_message)
                print(pos+"Success:\n",msg.__dict__)
            except messagebird.client.ErrorException as e:
                print(err+"Error:\n")
                for error in e.errors:
                    print(error)
            return 1

        if list_number is not None: # if a list of numbers was provided
            numfile = open(list_number)
            final_scc = 0 # Success count variable
            final_err = 0 # Error count variable
            if args.verbose is False: # if -v was NOT supplied, only print the following line
                print("Sending messages... DO NOT EXIT! A report will be ready soon.\n")
            for line in numfile: # loop of numbers from file
                if args.verbose is True: # if -v was supplied, print every single action per number from file
                    print("\n---------------------------------------------------------------------------------------------------")
                    print("\n[*] Sending to: "+line)

                ## MessageBirds API in action
                msgbrd_client = messagebird.Client(api_key)
                try:
                    msg = msgbrd_client.message_create(sender_name, '+'+line, sms_message)
                    if args.verbose is True:
                        print(pos+"Success:\n",msg.__dict__)
                    final_scc += 1
                except messagebird.client.ErrorException as e:
                    final_err += 1
                    if args.verbose is True:
                        print(err+"Error:\n")
                        for error in e.errors:
                            print(error)

                # If -v was NOT supplied, show minimal info
                if args.verbose is not True:
                    print("\033[A                             \033[A")
                    print('(',final_scc+final_err,'/',numcount,')', sep='')

        # Print the final report
        print("\n---------------------------------------------------------------------------------------------------")
        print (pos+"Done.")
        print (pos+"Messages sent successfully: "+str(final_scc)+"/"+str(numcount))
        print (err+"Messages failed: "+str(final_err)+"/"+str(numcount))
        numfile.close()
        return 1

    # If "n" was picked, exit
    elif ask_verify.lower() == "n":
        print (err+"Exiting...")
        return 1
    else: # In a case where --confirm was not supplied or value enetered isn't y/n, restart func
        print (err+"Please enter either (y)es or (n)o.")
        send_sms(to_number, api_key, sender_name, sms_message, list_number, numcount)

# --save Function - saves to .ini file
def save_message():
    clog = configparser.ConfigParser()
    clog['AutoBird'] = {}
    clog['AutoBird']['LOG_TIME'] = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
    clog['AutoBird']['LOG_API_KEY'] = args.apikey
    clog['AutoBird']['LOG_SENDER'] = args.sender
    if args.number is not None:
        clog['AutoBird']['LOG_NUMBER'] = args.number
    elif args.list is not None:
        clog['AutoBird']['LOG_NUMFILE'] = args.list
    clog['AutoBird']['LOG_MESSAGE'] = args.message
    clog['AutoBird']['VERSION'] = appversion
    try:
        filename = 'AutoBird_'+args.sender+'_'+datetime.now().strftime('%Y_%m_%d_%H_%M_%S')+'.log'
        with open(filename, 'w') as configfile:
            clog.write(configfile)
            print (pos+"Log saved to:",filename,"\nYou can view it or re-use it next time.\n")
    except:
        print (err+"Error: File not saved. Could not create log file. Check premissions.\n")

 # Launch main function
if __name__ == "__main__":
    exit (main())
