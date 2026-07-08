# PIE-NN LLM Interface Sidecar

import socket
import json
import readline

class LLMSidecar:
    def __init__(self, socket_path):
        self.socket_path = socket_path

    def compile_to_idl(self, nl_command):
        """Compiles natural language to a simplified IDL command."""
        nl_command = nl_command.lower().strip()
        if "status" in nl_command:
            return {"method": "get_status", "params": {}}
        elif "hierarchy" in nl_command:
            return {"method": "get_tc_hierarchy", "params": {}}
        elif nl_command.startswith("process"):
            source = nl_command.replace("process", "").strip()
            return {"method": "process_source", "params": {"source": source}}
        else:
            return {"method": "unknown", "params": {"command": nl_command}}

    def send_command(self, idl_command):
        """Sends a command to the daemon and gets the response."""
        try:
            client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            client.connect(self.socket_path)
            client.sendall(json.dumps(idl_command).encode())
            response = client.recv(1024)
            client.close()
            return json.loads(response.decode())
        except (ConnectionRefusedError, FileNotFoundError):
            return {"error": "Daemon not running or socket not found."}

    def narrate_response(self, response):
        """Presents the JSON response in a user-friendly way."""
        if "error" in response:
            print(f"Error: {response["error"]}")
        else:
            print("Daemon Response:")
            print(json.dumps(response, indent=2))

    def run_interactive_shell(self):
        print("PIE-NN LLM Interface. Type your commands.")
        while True:
            try:
                nl_command = input("> ")
                if nl_command.lower() in ["exit", "quit"]:
                    break
                idl_command = self.compile_to_idl(nl_command)
                response = self.send_command(idl_command)
                self.narrate_response(response)
            except EOFError:
                break

if __name__ == "__main__":
    sidecar = LLMSidecar("/tmp/pie_nn_daemon.sock")
    sidecar.run_interactive_shell()
