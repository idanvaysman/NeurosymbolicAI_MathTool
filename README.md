===============================================================================
⚡ AIDER & OLLAMA: COMPLETE MACHINE SETUP & PROJECT WORKFLOW GUIDE
===============================================================================
This document contains everything from the initial server configuration to the 
daily project workflows. Copy or download this text file for quick reference.

-------------------------------------------------------------------------------
PHASE 1: REMOTE OLLAMA SERVER CONFIGURATION
-------------------------------------------------------------------------------
Run these steps once on your SEPARATE BACKEND SERVER MACHINE running Ubuntu 
to allow network connections.

1. Edit the systemd service configuration for Ollama:
   sudo systemctl edit ollama.service

2. Add the following lines in the text editor exactly as shown:
   [Service]
   Environment="OLLAMA_HOST=0.0.0.0:11434"

3. Reload systemd and restart the service:
   sudo systemctl daemon-reload
   sudo systemctl restart ollama

4. Open the firewall port if UFW is enabled:
   sudo ufw allow 11434/tcp

5. Get your Server's IP address (Save this as SERVER_IP):
   ip route get 1 | awk '{print $7; exit}'


-------------------------------------------------------------------------------
PHASE 2: LOCAL DEVELOPMENT MACHINE INITIALIZATION
-------------------------------------------------------------------------------
Run these steps once on your LOCAL MACHINE to install global tools and 
configure Git identity.

1. Update system packages and install pipx + git:
   sudo apt update
   sudo apt install python3-pip python3-venv pipx git -y

2. Configure pipx path and force-install global Aider:
   pipx ensurepath
   pipx install --force aider-chat

3. Reload your terminal profile to apply global paths instantly:
   source ~/.bashrc

4. Set your global Git identity (Required for Aider's auto-commits):
   git config --global user.name "Idan Vaysman"
   git config --global user.email "idanvaysman@gmail.com"


-------------------------------------------------------------------------------
PHASE 3: CREATING A NEW PROJECT WORKSPACE
-------------------------------------------------------------------------------
Follow this workflow every time you want to spin up a completely brand-new 
agent project from your template folder.

1. Navigate to your main projects directory:
   cd ~/agent_projects

2. Duplicate the template folder into your new project folder:
   cp -r project_template/ project_name/

3. Enter your new project workspace:
   cd project_name

4. Generate a completely fresh, isolated virtual environment:
   python3 -m venv .venv

5. Initialize clean Git tracking:
   git init
   echo ".venv/" >> .gitignore


-------------------------------------------------------------------------------
PHASE 4: THE EVERYDAY LAUNCH SEQUENCE
-------------------------------------------------------------------------------
Run these commands every single time you open a fresh terminal window to start 
programming on a project.

1. Jump into your specific project folder:
   cd ~/agent_projects/project_name

2. Activate your project's isolated environment:
   source .venv/bin/activate

3. Target your remote Ollama server (Replace SERVER_IP with your actual IP):
   export OLLAMA_API_BASE=http://SERVER_IP:11434

4. Fire up Aider globally using the high-quality Qwen 14B model:
   aider --model ollama_chat/qwen2.5-coder:14b-instruct-q6_K


-------------------------------------------------------------------------------
PHASE 5: CORE AIDER CONTROLS REFERENCE
-------------------------------------------------------------------------------
Once the terminal displays the active "⚡" prompt, use these primary controls 
to direct your development agent:

* /add <file path>
  Grants Aider permission to read and rewrite a specific file.
  Example: /add src/main.py

* /drop <file path>
  Removes a file from the active chat memory to save context window space.
  Example: /drop src/main.py

* !<terminal command>
  Executes an external system command or runs your script directly inside the 
  chat interface without exiting.
  Example: !python3 src/main.py

* /exit
  Safely shuts down the Aider session and hands control back to your standard 
  terminal shell. (Keyboard Shortcut: Ctrl + D)


-------------------------------------------------------------------------------
💡 ENGINEERING PEER BEST PRACTICES
-------------------------------------------------------------------------------
1. Always add files before prompting: Aider cannot edit code it hasn't been 
   explicitly given via the /add command.
2. Prompt naturally: Once a file is added, you don't need to specify file paths 
   anymore. Simply type: "Refactor the main execution block to handle empty 
   array edge cases cleanly."
3. Let it handle Git: Aider automatically reviews changes, shows you a clean 
   diff, and generates descriptive local Git commit histories on its own.
===============================================================================
