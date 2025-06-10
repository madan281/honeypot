import argparse
import honeypot_module
from web_honeypot import run_app
from dashboard_data_parser import *
from web_app import *

# Parse Arguments
if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument('-a', '--address',type=str, required=True)
    parser.add_argument('-p', '--port', type=int ,required= True)
    parser.add_argument('-u','--username', type=str)
    parser.add_argument('-pw','--password',type=str)

    parser.add_argument('-s','--ssh', action ="store_true")
    parser.add_argument('-w','--http',action ="store_true")

    args = parser.parse_args()
    try:
        if args.ssh:
            print("[-] Running SSH Honeypot...")
            honeypot(args.address, args.port, args.username, args.password, args.tarpit)

        elif args.http:
            print('[-] Running HTTP Wordpress Honeypot...')
            #if args.nocountry:
                #pass_country_status(True)
            if not args.username:
                args.username = "admin"
                print("[-] Running with default username of admin...")
            if not args.password:
                args.password = "deeboodah"
                print("[-] Running with default password of deeboodah...")
            print(f"Port: {args.port} Username: {args.username} Password: {args.password}")
            def run_app(port=5000, input_username="admin", input_password="deeboodah"):
                app = baseline_web_honeypot(input_username, input_password)
                app.run(debug=True, port=port, host="0.0.0.0")
        else:
            print("[!] You can only choose SSH (-s) (-ssh) or HTTP (-h) (-http) when running script.")
    except KeyboardInterrupt:
        print("\nProgram exited.")
