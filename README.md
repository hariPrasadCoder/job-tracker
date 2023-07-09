# job-tracker

Run the fastapi using:

`uvicorn main:app --reload`

## Keep server running on EC2 instance after ssh is terminated:

## Managing a single session
Here is a great answer by Hamish Downer given to a similar question over at askubuntu.com:

I would use a terminal multiplexer - screen being the best known, and tmux being a more recent implementation of the idea. I use tmux, and would recommend you do to.

Basically tmux will run a terminal (or set of terminals) on a computer. If you run it on a remote server, you can disconnect from it without the terminal dying. Then when you login in again later you can reconnect, and see all the output you missed.

To start it the first time, just type

`tmux`
Then, when you want to disconnect, you do Ctrl+B, D (ie press Ctrl+B, then release both keys, and then press d)

When you login again, you can run

`tmux attach`
and you will reconnect to tmux and see all the output that happened. Note that if you accidentally lose the ssh connection (say your network goes down), tmux will still be running, though it may think it is still attached to a connection. You can tell tmux to detach from the last connection and attach to your new connection by running

`tmux attach -d`
In fact, you can use the -d option all the time. On servers, I have this in my >.bashrc

`alias tt='tmux attach -d'`
So when I login I can just type tt and reattach. You can go one step further >if you want and integrate the command into an alias for ssh. I run a mail client >inside tmux on a server, and I have a local alias:

`alias maileo='ssh -t mail.example.org tmux attach -d'`
This does ssh to the server and runs the command at the end - tmux attach -d The -t option ensures that a terminal is started - if a command is supplied then it is not run in a terminal by default. So now I can run maileo on a local command line and connect to the server, and the tmux session. When I disconnect from tmux, the ssh connection is also killed.

This shows how to use tmux for your specific use case, but tmux can do much more than this. This tmux tutorial will teach you a bit more, and there is plenty more out there.

## Managing multiple sessions
This can be useful if you need to run several processes in the background simultaneously. To do this effectively, each session will be given a name.

Start (and connect to) a new named session:

`tmux new-session -s session_name`
Detach from any session as described above: Ctrl+B, D.

List all active sessions:

`tmux list-sessions`
Connect to a named session:

`tmux attach-session -t session_name`
To kill/stop a session, you have two options. One option is to enter the exit command while connected to the session you want to kill. Another option is by using the command:

`tmux kill-session -t session_name`


# Supervisor:

## Edit config file
`sudo vim /etc/supervisor/conf.d/job-tracker.conf`

## After editing restart supervisor
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl restart all
sudo supervisorctl status

## Check error logs
`cat -n /var/log/supervisor/fastapi_error.log`


#### =================== ###

To keep the Uvicorn server running even if you close the terminal or SSH session, you can use a tool like `nohup` (no hang-up) or run Uvicorn as a background process. Here's how you can achieve this:

1. Connect to your EC2 instance via SSH.

2. Navigate to the directory where your FastAPI application is located.

3. Run the Uvicorn server as a background process using the following command:
   ```
   nohup uvicorn main:app --host 0.0.0.0 --port 80 &
   ```
   This command uses `nohup` to prevent the process from receiving the hang-up (HUP) signal when the terminal is closed. The `&` at the end runs the process in the background.

4. Press Enter to execute the command. You should see a message like "nohup: ignoring input and appending output to 'nohup.out'". This indicates that the process is running in the background.

5. You can now safely close the terminal or SSH session without stopping the Uvicorn server. It will continue running in the background.

To check the status of the Uvicorn server or stop it later, you can use the following commands:

- To check if the Uvicorn process is running:
  ```
  ps aux | grep uvicorn
  ```
  This will display the running processes that match the name "uvicorn". You should see the Uvicorn process with its corresponding process ID (PID).

- To stop the Uvicorn process, you can use the `kill` command followed by the PID of the Uvicorn process:
  ```
  kill <PID>
  ```
  Replace `<PID>` with the actual process ID obtained from the previous command.

By running Uvicorn as a background process, you ensure that it continues running even if you close the terminal or SSH session. However, keep in mind that if the EC2 instance is restarted, you will need to manually start the Uvicorn process again. Consider using process management tools like Supervisor or init system configurations to automatically start the Uvicorn server on system boot.