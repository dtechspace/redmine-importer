## Assembla-to-Redmine Converter

This project helps to provide a converter for both wiki pages and issues for 
Assembla spaces to Redmine projects. It also converts the markdown appropriately
and imports the necessary images, if they exist on the Assembla side. 

### Getting Started

Ensure that both your Redmine server/project and Assembla space is ready for
import. Clone this project, and install the requirements. We recommend 
activating a Python virtual environment before pip installing the requirements.

```
git clone <GitHub URL>
cd redmine-importer
pip install -r requirements.txt
```

You will also need to create an empty folder for any images included in your 
Assembla wiki pages or tickets, in the same directory as the python scripts. 

```
cd redmine-importer
mkdir img
```

### Settings

In order to specify which Assembla space and Redmine project to target, we've
provided a settings configuration file, called settings.ini. The settings.ini 
file is outlined in the Python built-in ConfigParser library format. 

```
[Assembla Keys]
ASSEMBLA_API_KEY=<API Key from Assembla, found at https://www.assembla.com/user/edit/manage_clients>
ASSEMBLA_API_KEY_SECRET=<API Secret from Assembla, found at https://www.assembla.com/user/edit/manage_clients>
ASSEMBLA_SPACE=<Assembla Space name>

[Redmine Keys]
REDMINE_API_KEY=<Follow the steps at https://www.redmine.org/boards/2/topics/53956 to find the API key>
REDMINE_URL=<URL for your Redmine server>
REDMINE_PROJECT=<Redmine project identifier>
```

In order to find the exact naming of your Redmine and Assembla projects, you can 
run the settings.py file, which will list the available Assembla Spaces and 
Redmine Projects associated to your API keys.

### Running the Project

Once the settings.ini has been populated and saved, please run the project with 
the following python command:
``` 
python3 migration.py
```
If there are issues with importing projects or issues, error messages with the
specific page name will be printed to the terminal, and those projects and/or
issues will be skipped. We recommend posting those issues to this GitHub project 
and/or uploading those projects/issues manually. 