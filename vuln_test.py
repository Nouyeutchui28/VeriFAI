import os

def run_command(user_input):
    # DANGEROUS: Command Injection vulnerability
    os.system("echo " + user_input)

if __name__ == "__main__":
    run_command("hello")
