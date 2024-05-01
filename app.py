from flask import Flask, render_template, request, send_file, redirect, url_for
from pymongo import MongoClient
from bson.objectid import ObjectId
from pathlib import Path
from datetime import datetime
import qrcode
from werkzeug.middleware.proxy_fix import ProxyFix


app = Flask(__name__)

app.wsgi_app = ProxyFix(
    app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1
)

client = MongoClient("mongodb://localhost:27017/")
db = client["URAS"]
inventory_items = db["Inventory_Items"] 
inventory_locations = db["Inventory_Locations"]
inventory_items_archive = db["Inventory_Items_Archive"]


@app.route('/')
def index():
    items = inventory_items.find().sort({"$natural": -1}).limit(15)
    locations = inventory_locations.find().sort({"$natural": -1}).limit(5)
    zero = inventory_items.find({"Quantity": "0"})
    return render_template('index.html', items=items, locations=locations, zero=zero)

#Show all items
@app.route('/items')
def items():
    documents = inventory_items.find()
    return render_template('items.html', documents=documents)

#Show all locations
@app.route('/locations')
def locations():
    documents = list(inventory_locations.find())
    for document in documents:
        for i in range(0,len(document['Items'])):
           specific = inventory_items.find_one({"_id": document["Items"][i]})
           document['Items'][i] = [specific["Part Number"], "QTY: " + str(specific["Quantity"]), document["Items"][i]]
    return render_template('locations.html', documents=documents)

#Show a specific location
@app.route('/locations/<location_id>')
def location_by_id(location_id):
    document = inventory_locations.find_one({"Name": location_id})
    if document:
        for i in range(0,len(document['Items'])):
            specific = inventory_items.find_one({"_id": document["Items"][i]})
            document['Items'][i] = [specific["Part Number"], "QTY: " + str(specific["Quantity"]), document["Items"][i]]
        return render_template("location.html", document=document)
    else:
        return "Location does not exist"


#Show a specific item
@app.route('/item/<item_id>')
def item_by_id(item_id):
    document = inventory_items.find_one({"_id": ObjectId(item_id)})
    return render_template("item.html", document=document, item_id=item_id)

#Upload files for locations or items
@app.route('/upload/<type>/<id>/<what_is_it>', methods=['POST'])
def upload(type, id, what_is_it):
    if 'file' not in request.files:
        return "No file part"
    file = request.files['file']
    if file.filename == '':
        return "No selected file"
    if file:
        Path("static/"+type+"/"+id+"/").mkdir(parents=True, exist_ok=True)
        file.save("static/"+type+"/"+id+"/"+file.filename)
        img_files = ["apng", "bmp", "gif", "jpeg", "jpg", "png", "webp", "svg"]
        if what_is_it == "image":
            if file.filename.split(".")[-1].lower() not in img_files:
                return ("Not an allowed image file")
            else:
                if type == "inventory_items":
                    inventory_items.update_one({"_id": ObjectId(id)}, { "$set" :{"Image": "static/"+type+"/"+id+"/"+file.filename}})
                    return redirect(url_for('item_by_id', item_id=id))
                elif type =="inventory_locations":
                    inventory_locations.update_one({"Name": id}, { "$set" : {"Image": "static/"+type+"/"+id+"/"+file.filename}})
                    return redirect(url_for('location_by_id', location_id=id))
        else:
            if type == "inventory_items":
                inventory_items.update_one({"_id": ObjectId(id)}, { "$push" :{"Files": "static/"+type+"/"+id+"/"+file.filename}})
                return redirect(url_for('item_by_id', item_id=id))
            elif type =="inventory_locations":
                inventory_locations.update_one({"Name": id}, { "push" :{"Files": "static/"+type+"/"+id+"/"+file.filename}})
                return redirect(url_for('location_by_id', location_id=id))
        

#Add items
@app.route("/new_item", methods = ["GET", "POST"])
def new_item():
    if request.method == 'POST':
        part_number = request.form['part_number']
        quantity = request.form['quantity']
        description = request.form['description']
        location = request.form['location']
        user = request.form['user']
        if location:
            if inventory_locations.find_one({"Name": location}) == None:
                return "Location does not exist"
        id = inventory_items.insert_one({"Part Number": part_number, "Description": description, "Quantity": quantity, "Location":location, "Notes": "", "Date Added":datetime.now().strftime("%m/%d/%Y %H:%M:%S"), "Files" :[], "Image":"", "Added By": user})
        inventory_locations.update_one({"Name": location}, {'$push': {'Items': id.inserted_id}})
        return redirect(url_for('item_by_id', item_id = id.inserted_id))
    return render_template('new_item.html')

@app.route("/new_location", methods = ["GET", "POST"])
def new_location():
    if request.method == 'POST':
        name = request.form['name']
        user = request.form['user']
        id = inventory_locations.insert_one({"Name": name, "Items" :[], "Image":"", "Added By": user, "Date Added":datetime.now().strftime("%m/%d/%Y %H:%M:%S")})
        return redirect(url_for('location_by_id', location_id = name))
    return render_template('new_item.html')


@app.route('/edit/<type>/<id>/<key>/', methods = ["GET", "POST"])
def edit_item(type, id, key):
    if request.method == "POST":
        value = request.form["value"]
        if type == "inventory_items":
            inventory_items.update_one({"_id": ObjectId(id)}, {'$set' : {key: value}})
            if key == "Location":
                inventory_locations.update_one({"Name": value}, {'$push': {'Items': ObjectId(id)}})
            return redirect(url_for('item_by_id', item_id=id))
        elif type =="inventory_locations":
            inventory_locations.update_one({"_id": ObjectId(id)}, {'$set' : {key: value}})
            return redirect(url_for('location_by_id', location_id=id))
        
@app.route('/archive_item/<id>')
def archive_item(id):
    item = inventory_items.find_one({"_id": ObjectId(id)})
    inventory_items_archive.insert_one(item)
    inventory_locations.update_one({"Name": item["Location"]}, {'$pull': {'Items': ObjectId(id)}})
    inventory_items.delete_one(item)
    return redirect(url_for("index"))

@app.route('/printqr/<id>/', methods=["GET", "POST"])
def printqr(id):
    img = qrcode.make(id)
    type(img)  # qrcode.image.pil.PilImage
    Path("static/tmp/").mkdir(parents=True, exist_ok=True)
    img.save("static/tmp/qr.png")
    info = request.form
    return render_template('label.html', info=info)

@app.route('/scanqr/', methods=["GET", "POST"])
def scanqr():
    id = request.form["qrvalue"]
    if inventory_items.find_one({"_id": ObjectId(id)}):
        return redirect(url_for('item_by_id', item_id=id))
    elif inventory_locations.find_one({"Name": id}):
        return redirect(url_for('location_by_id', str(inventory_locations.find_one({"Name": id})["_id"])))
