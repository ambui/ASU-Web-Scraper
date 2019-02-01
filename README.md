# ASU Web Scraper (WIP)
## Description:
**Language:** Python
Web scrapes content from discussion boards on Blackboard  
Creates Virtual Browser and uses student info to login and navigate to course pages  
Parses Student Question and Instructor Response  
*Option for peer response commented out (usually not helpful)  
Can be integrated into AWS for automated data pulls
**Output:** JSON file Sample  
```  
{
	"CSE470": [
		{
			"q": "Hello,I have all of my solutions in one folder and have saved everything onto a location on my computer (not within VS), and everything is running smoothly. However, when I submit to Blackboard and redownload the submission to test it, VS is giving me the following error:  "One or more projects in the solution were not loaded correctly" and nothing appears on the screen.How do I fix this??Thanks, Brandon ",
			"a": "You need to check which project is not open correctly, and then, double check if you have that project in your submission folder."
		},
],
"title": "blackboard scrape"
}
```

## To Do:
- Add Canvas support
- Account for time and only parse until reaching last pull data
