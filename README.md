# TLA Import

## CSV - XML Order Import Tool

This program is designed to turn a properly formatted CSV into an XML that can be read as an order by Elucid. It uses a combination of the Pandas and ElementTree libraries to manipulate the data, as well as performing some basic error checking, making sure certain fields exist and are in the correct format before creating the XML.

The program works via shortcuts with arguments in them - at time of writing, the program can take between 1 and 5 additional arguments.

1. Source. The folder the program will import the CSVs from. This is the only required argument.
2. Destination. If this is filled in, the program will automatically export the produced XML to the listed folder. If not, the XML will be left in a subfolder of the Source folder, and a message will pop up asking the user to contact IS to move the files for them.
3. Display Suppression. If this argument is "suppressdisplay" then no messages to the user will be displayed outside of catastrophic errors. This is for automation purposes, allowing the program to be ran without user input.
4. Prefix. Adds whatever this argument is to the beginning of any order numbers. If this isn't provided, no prefix will be added.
5. Log Keep. How long in days the log files will be kept for. Anything older than this will be deleted the next time the process is ran. Defaults to 30 days if not provided.

Logs are kept in a logs subfolder as simple text files.
