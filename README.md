# Terminal_Randomizer
A script that changes the appearance of a Windows Terminal, randomly selecting background, foreground colors as well as the background gif


## Example


<img src="https://github.com/LucasVerdelho/Terminal_Randomizer/blob/main/readme_assets/hello_there.gif" width="630" height="350"/>
<img src="https://github.com/LucasVerdelho/Terminal_Randomizer/blob/main/readme_assets/general_kenobi.gif" width="630" height="350"/>



## How to Use
You will need to put some gifs on the **"photos"** folder in this repository in order for the script to do anything, so be sure to do that first.

1. Make sure you have installed the Windows Terminal from the Microsoft Store.

2. You will also need to have python installed and to have this repository downloaded somewhere on your pc where you will be able to remember it's location.

3. Open your Windows Terminal and change the directory to:
```
%The_Path_To_The_Repository%\Terminal_Randomizer\src
```
where you change the Path to wherever you downloaded the repository.

4. Run the following command:
```
python terminal_randomizer.py
```

5. If it changed, means everything is probably working


Note :
> I have included a preset that I use **settings.json** file which you will need to change the paths I have included, I may still implement an initializer later on, but for now manual changes are needed.

Another Note :
> I am using the font Source Code Pro Light

## How to Find the Paths
To find the settings.json file, this path usually works:
(You will have to change the user to your own)
```
C:\Users\{user}\AppData\Local\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\
```

If you find the settings.json file, just go over to the input.txt file, and change the user there as well.


I recommend using the voidtools' **Everything Search** for this, but the terminal executable is generally located in the path i have included in the **WinTerminal_Run.bat file**, being called **"wt.exe"**. 

For the retro shader effects on the terminal just change the path of the .hlsl file to where you downloaded the repository.



## How do i make it go brr every time i open the terminal?
Unfortunately there is no clean solution that I have found to this problem, so we will have to do with a janky Windows type beat ugly fix.

1. Open the batch file that is included in this repository.

2. Make sure the **"cd"** command will place you in the right path

3. Change the wt.exe path to where the Windows Terminal is installed on your pc

4. Open Task Scheduler and make a new folder named "WinTerminal" inside the Task Scheduler Library folder.

5. Create a new Task and also name it "WinTerminal" 

6. Select the option "Run with the highest privileges" and on the "Configure for:" select "Windows 10"

7. Go to the Actions tab and make a new action, it will default to Start a Program which is what we want.

8. Browse to the WinTerminal_Run.bat file and save the action

9. Save the task and close Task Scheduler

10. Go to your Desktop and create a new shortcut

11. If you followed the naming convention the location of the item shall simple be:
```
C:\Windows\System32\schtasks.exe /RUN /TN "WinTerminal\Winterminal"
```
Else, make sure to reopen the TaskScheduler and check the path to your task

12. Name the Shortcut and you are all set!


Note: 
>You can also change the icon to the terminal.ico from Windows, I will include a copy of it in the repository



