# BetsuRental
BetsuRental is a multi-user rental application allowing said useres to create virtual "shops" where they post items which are available for rental.

## Requirements

* Python 2

## Instillation
*Instillation instructions assume you have access to the vagrant directory containing the catalog subdirectory, which is running on a virtual machine*

**Clone** the **rentalApp** repository from `https://github.com/jlmcco06/rentalApp.git` into a directory on your machine which has access to the virtual machine/vagrant, using terminal or commandline.

When repository has been cloned, the following files should be present:

* **README.md** - You're reading this!
* **database_setup.py** - Start the database
* **dbpopulator.py** - Add departments, and a couple of test-shops with pieces for rent
* **application.py** - Run application
* **client_secret.json - Google sign-in client secret information
* **fb_client_secrets.json - Facebook sign-in client secrets
* **static (directory)** - Directory containing imaged for application, css stylesheet, and uploads directory containing files uploaded by users.
* **templates (directory)** - Contains all html files for site.

##Getting started
First, establish your database by running `python database_setup.py` in your terminal (or commandline).

Second, add departments and dummy shops to your database by running `python dbpopulator.py` in your terminal. A message stating the departments and test shops have been added should print in the terminal if this action has been sucessfully executed.

Now, you should be ready to run the application! Run `python application.py`in the termainlal. The application has been configured to run on localhost port 8000, so if you open your browser, and navigate to that port, you should she the "BetsuRental" homescreen.

##Using BetsuRental

Hopefully the application is sucessfully running! 

Users have three options for browsing: by department, by shop, all items. 

Departments currently include: 

*Art
*Lighting
*Props
*Seating
*Storage
*Tables
*Textiles

Users with less specific needs can choose to browse by shop, or search through all items in the database.

##Creating a shop

In order to create a shop, the user must be logged-in. Currently, the application only supports login through third-party authorization with Google, of Facebook sign-in buttons. Once logged in, the user must navigate shops page, by clicking the "Browse shops" or "My shop" links, and the the "Open a shop here" link on the shops page.

If the user would like to edit and shop profile information or delete the shop, the shop page will have a link the the form to accomplish these actions.  

Once the user has completed the create shop form and the shop has been added, they can add items to their virtual store from the shops page.

##Adding items

From the shop page, users who are logged-in, and own the shop are able to add items information and photos which will be displayed as an individual piece profile. If a photo is not added to as part of the piece profile form when the shop is created, the path to a placeholder photo will be automatically saved to this piece object in the database.

If the user would like to remove or edit any information in a piece profile, a link for this exists on the individual piece page.   

  