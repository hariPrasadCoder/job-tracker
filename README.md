# job-tracker

Run the fastapi using:

`uvicorn main:app --reload`

#### =================== ###

To keep the Uvicorn server running even if you close the terminal or SSH session, you can use a tool like `nohup` (no hang-up) or run Uvicorn as a background process. Here's how you can achieve this:

1. Connect to your EC2 instance via SSH.

2. Navigate to the directory where your FastAPI application is located.

3. Run the Uvicorn server as a background process using the following command:
   ```
   nohup uvicorn main:app --host 0.0.0.0 --workers=4 &
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