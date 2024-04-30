# URAS - Universal Resource Allocation System

URAS is an inventory management system that uses Flask, MongoDB, Bootstrap, and jQuery DataTables

## Quick Start
1. Make sure you have MongoDB running
2. Clone the repository
3. install the required packages with pip
4. Run URAS with your favorite WSGI application - I like Waitress

     ``waitress-serve --port 1234 wsgi:app``

    or flask itself

    ``flask -A wsgi:app run``
5. Open URAS and add a location, then add items

## Features

URAS allows for multiple instances of the same part number to exist in it's inventory. This allows for traceability documents to be uploaded for batches of materials that enter a facility. 

Inventory is never deleted, it is only archived. This maintains all paperwork that is assocaited with an instance of a part number existing in the system. 

The homepage offers a look at the most recently added inventory items, inventory locations, and inventory with a quantity of 0 which you can archive. 
![image](https://github.com/ens1/URAS/assets/3011085/7b178e76-4fc4-4026-9f36-c580b3548286)

URAS also offers tabulated and searchable views of inventory items and locations, sortable by any attribute of the items or locations. 
![image](https://github.com/ens1/URAS/assets/3011085/173c1974-e6a0-41c9-84ab-30e1d158859a)

![image](https://github.com/ens1/URAS/assets/3011085/477f84bc-87f7-4156-9ad3-e7bda7718cd7)

Item and Location pages offer a view of all attributes of the items or locations, and will generate a QR code that can be printed and scanned with a 2D barcode scanner
![image](https://github.com/ens1/URAS/assets/3011085/4b348f21-fa12-4c10-b60e-cfa74bc5f96d)
![image](https://github.com/ens1/URAS/assets/3011085/ef161ceb-46fa-48c6-b676-f0e0c1924ba1)

Any QR code can be scanned, and will pull up the page for a specific item or location by clicking the "Search by QR" button on any page
![image](https://github.com/ens1/URAS/assets/3011085/e8a3949f-b9e2-4ca5-b284-e7ffa48fed14)
