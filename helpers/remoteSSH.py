import paramiko


def ssh_execute_command(host, port, username, password, command):
    """
    Connects to a remote server via SSH and executes a command.

    :param host: Remote server hostname or IP
    :param port: SSH port (default 22)
    :param username: SSH username
    :param password: SSH password
    :param command: Command to execute on the remote server
    :return: (stdout, stderr)
    """
    client = paramiko.SSHClient()
    # Automatically add the server's host key (for first-time connections)
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        # Connect to the remote server
        client.connect(hostname=host, port=port, username=username, password=password, timeout=10)

        # Execute the command
        stdin, stdout, stderr = client.exec_command(command)

        # Read outputs
        output = stdout.read().decode().strip()
        error = stderr.read().decode().strip()

        return output, error

    except paramiko.AuthenticationException:
        return None, "Authentication failed. Check username/password."
    except paramiko.SSHException as e:
        return None, f"SSH connection error: {e}"
    except Exception as e:
        return None, f"Unexpected error: {e}"
    finally:
        client.close()


if __name__ == "__main__":
    # Example usage
    host = "192.168.1.100"  # Replace with remote IP or hostname
    port = 22
    username = "your_username"
    password = "your_password"
    command = "uname -a"  # Example command

    stdout, stderr = ssh_execute_command(host, port, username, password, command)

    if stdout:
        print("Command Output:\n", stdout)
    if stderr:
        print("Error Output:\n", stderr)
