from getpass import getuser
from sshaolin.client import SSHClient
client = SSHClient(
    hostname="localhost", username=getuser(), look_for_keys=True)
client.execute_command("ls")
