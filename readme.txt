Contact Management System


*****/This is a web-based Contact Management System built with Flask and MongoDB. It allows users to sign up, log in, and manage their contacts with additional features such as contact import/export in VCF format, tag-based contact organization, and search functionality.*****/

Features

****/User Authentication: Users can sign up and log in to manage their personal contact lists.
Contact Management: Users can add, edit, delete, and search contacts.
Tagging: Organize contacts by adding comma-separated tags for better categorization and filtering.
Search Functionality: Search contacts by name, email, or tags.
VCF File Support:
Import: Upload contacts from a .vcf file.
Export: Download contacts in .vcf format.****/


Prerequisites
Python 3.x
MongoDB (local or cloud-based, such as MongoDB Atlas)
Flask
PyMongo
vObject
bcrypt


How to Use
1. Sign Up / Login
Navigate to the /signup route to create a new account.
After successful signup, log in with your credentials using the /login route.


2. Managing Contacts
After logging in, you will be redirected to the contact management page where you can:
Add new contacts with name, email, phone number, and tags.
Search for contacts by name, email, or tags.
View all your contacts.
Edit or delete contacts.


3. Import/Export Contacts
Import Contacts:
Navigate to the /import page to upload a .vcf file and import contacts.
Export Contacts:
Navigate to the /export page to download all your contacts as a .vcf file.

