# Terminal_Randomizer
A script that changes the appearance of a Windows Terminal, randomly selecting background, foreground colors as well as the background gif


## Example


<img src="https://github.com/LucasVerdelho/Terminal_Randomizer/blob/main/readme_assets/hello_there.gif" width="630" height="350"/>
<img src="https://github.com/LucasVerdelho/Terminal_Randomizer/blob/main/readme_assets/general_kenobi.gif" width="630" height="350"/>



## How to Use
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

5. You are good to go!


Note :
> I have included a preset that I use **settings.json** file which you will need to change the paths I have included, I may still implement an initializer later on, but for now manual changes are needed.

## How to Find the Paths
Usually this path will do the trick
```
%LocalAppdata%\Packages\Microsoft.WindowsTerminal_8wekyb3d8bbwe\LocalState\settings.json
```

I recommend using the voidtools' **Everything Search** for this, but the terminal executable is generally located in the path i have included in the **input.txt**, being called **"wt.exe"**.

For the retro shader effects on the terminal just change the path of the .hlsl file to where you downloaded the repository.



## How do i make it go brr every time i open the terminal?
Unfortunately there is no clean solution that I have found to this problem, so we will have to do with a janky Windows type beat ugly fix.

1. Open the batch file that is included in this repository.

2. Make sre


