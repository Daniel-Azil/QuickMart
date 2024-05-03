"""
    A module that contains all routes  for html and Post methods for backend
    operation for the web app that would be executed in the app file.
"""

from config import app
from flask import render_template
from flask import request, flash, redirect, url_for, session

from models import db, User, Cart, Category, Product, Order, Transaction

from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime




import os
import imghdr
import uuid
from flask import request, session, send_from_directory
from werkzeug.utils import secure_filename






def validate_image(stream):
    header = stream.read(512)
    stream.seek(0)
    format = imghdr.what(None, header)
    if not format:
        return None
    return "." + (format if format != "jpeg" else "jpg")








##################################### Authenticator ##########################################################
# auth_required, checks if the user is logged in or not to retrieve their session and unique activity
def auth_required(func):
    """
        A custom function that is use to wrap around other functions that
        requires utilizing the user session for unique usage and
        render the users own session and activity when accessing given pages
        the function wraps around other pages like the login page, the index or home page, profile page, etc.
    """
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' in session:
            return func(*args, **kwargs)
        else:
            flash('please login to continue')
            return redirect(url_for('login_page'))
    return inner


# admin_required, checks if the user is admin to grant them access the to admin pages
def admin_required(func):
    """
        A custom function that is use to wrap around other functions that
        requires utilizing the admin session for unique usage of admin specific activity and
        render the ammind own session and activity when accessing amdin pages
        the function wraps around other routes like the category route, etc.

        checks if the user is not admin and redirect them to the user dashboard
    """
    @wraps(func)
    def inner(*args, **kwargs):
        # checks if user is not is logged in, else redirects them to the login page
        if 'user_id' not in session:
            flash("please login to continue")
            return redirect(url_for('login_page'))
        
        # we retrieve the user unique session if they are logged in
        # we check if they are not admin and restrict them from accessing the admin pages
        # if they are admins, we grant them access to the admin required pages
        user = User.query.get(session['user_id'])
        if not user.is_admin:
            flash("You are not authorized to access this page")
            return redirect(url_for('home_page'))
        else:
            return func(*args, **kwargs)
    return inner
################################## End of Authenticator #############################################

















#################################  FRONTEND ROUTE [home page]  #################################################



@app.route('/')
@auth_required 
def home_page():
    """Return the index page or the admin page if user is admin."""
    user = User.query.get(session['user_id'])
    if user.is_admin:
        return redirect(url_for('admin_dashboard')) ##The route for admin_dashboard is below
    

    # normal display without search
    # retrieves all categories from the database for the index.html file to use
    # and dispay the each category and their products
    categories = Category.query.all()



    # search functionality
    # retrieve the form name for searching this includes the select and input from name the search form in
    # the search_bar.html file included with context in the index.html file
    
    cname = request.args.get('cname') or ''
    pname = request.args.get('pname') or ''
    price = request.args.get('price')

    # check if the user is searching for a category name\
    if cname:
        categories = Category.query.filter(Category.cat_name.ilike(f'%{cname}%')).all()

    # check if price is given and convert it to a float 
    if price:
        try:
            price = float(price)
        except ValueError:
            flash('Invalid price')
            return redirect(url_for('home_page'))
        if price <= 0:
            flash('Invalid price')
            return redirect(url_for('home_page'))





    # renders normal display without search
    return render_template('index.html', categories=categories, cname=cname, pname=pname, price=price)






################################# END of FRONTEND ROUTE [home page]  #################################################

# BACKEND operation for the 'Frontend route' above is the 'Backend controller' below

#################################  BACKEND Controller [home page]  #################################################
@app.route('/add_to_cart/<int:product_id>', methods=['POST'])
def home_page_add_to_cart_post(product_id):
    """
    
    """
    # check if the products exits and and store it in the variable product
    product = Product.query.get(product_id)
    if not product:
        flash('Product not found')
        return redirect(url_for('home_page'))


    # retrieve the user input of the quantity they want to add to cart
    # from the quantity_input in the form in index.html file

    quantity_input = request.form.get('quantity_input')

    # check if quantity entered is integer
    try:
        quantity_input = int(quantity_input)
    except ValueError:
        flash('Please enter a valid quantity')
    
    # check if quantity is lesser than 0 or equal to 0
    # also checks if quantity is greater than the quantity available in the database
    if quantity_input <= 0 or quantity_input > product.quantity_available:
        flash('Invalid quantity, should be between 1 and {}'.format(product.quantity_available))
        return redirect(url_for('home_page'))

    # check if the user is available in in the cart table and check if the prodcut is available in the cart table
    cart = Cart.query.filter_by(user_id=session['user_id'], product_id=product_id).first()
    
    # check if the user already added the same product to cart and increase the quantity when they add the product again
    if cart:

        # check if the total sum of the quantity inputted by the user plus the previous one added to cart
        # on different occasion is greater than the quantity available in the database
        if quantity_input + cart.quantity_added_to_cart > product.quantity_available:
            flash('Invalid quantity, should be between 1 and {}'.format(product.quantity_available))
            return redirect(url_for('home_page'))
        
        # else increase the quantity of the same product in the cart table
        else:
            cart.quantity_added_to_cart += quantity_input

    # if the user has not added the product to cart before, add the product to cart now.
    else:
        cart = Cart(user_id=session['user_id'], product_id=product_id, quantity_added_to_cart=quantity_input)
        db.session.add(cart) 
    
    # save the changes to the database
    db.session.commit()

    flash('Product added to cart successfully')
    return redirect(url_for('home_page'))


#################################  END of BACKEND Controller [home page]  #################################################





















#################################  FRONTEND ROUTING [home, login, register, profile, logout]  #################################################
# Routes for the html desings for the front end view of the application




@app.route('/login')
def login_page():
    """Return the login page."""
    return render_template('login.html')

@app.route('/register')
def register_page():
    """Returns the register page"""
    return render_template('register.html')


@app.route("/profile")
@auth_required  
def profile_page():
    user  = User.query.get(session["user_id"])  # saves the user id in the  variable
    ## renders the profile page with the user's unique session and activity
    return render_template("profile.html", user=user) 
    


@app.route("/logout")
@auth_required ## checks for user's session
def logout_page():
    session.pop('user_id')
    return redirect(url_for('login_page'))

############################### END of FRONTEND ROUTES #################################################

# BACKEND operation for the 'Frontend route' above is the 'Backend controller' below

################################ BACKEND CONTROLLERS #####################################################
# register, login, profile backend controllers
#Retriving user submitted information for backend operation




#### Register Backend controller
# Related html file => register.html
@app.route('/register', methods=['POST'])   
def register_post():                        
    input_username =  request.form.get('username')
    password = request.form.get('password')
    confirm_password = request.form.get('confirm_password')
    name = request.form.get('name')
    #return ("input_username is {}, password is {}, confirm password is {}, name is {}".format(input_username, password, confirm_password, name))   ## for debug to check if retriving is working.
    

    ## checks if nothing is inputed and displays a message not for security but just to ensure
    # they enter their datails. security is done in the backend cos on this side of the front end,
    # they can easy inspect the html code on the bowser and change the lines of code.
    if not input_username or not password or not confirm_password:   
        flash("Please fill out all fields")
        return redirect(url_for('register_page'))
    ### checks if both confirm passwords and password is the same
    if password != confirm_password:  
        flash("Passwords do not match!")
        return redirect(url_for('register_page'))
    
    
    # DATABASE auto creation handler (from frontend to backend).
    # After setting up the retrieved input with post html verb above, we query the
    # database below to add data to the database in models.py

    # Check if the input_username from the page input is already in the database,
    # if it is, save it in the variable
    user = User.query.filter_by(username=input_username).first()
    ### checks if the user variable is empty or not empty
    if user:
        flash("Username already exists")
        return redirect(url_for('register_page'))
    
    ### secure the users password
    hashPassword = generate_password_hash(password)
    ## set the newly registered user to database query
    new_user = User(username=input_username, hashed_password=hashPassword, name=name)
    # Initialises the new user database query
    db.session.add(new_user)
    # save and commit the query in the database
    db.session.commit()

    ## After adding the user to the database, we now rediect the user to the login page.
    return redirect(url_for('login_page'))



#### login Backend and controller
# the related html file => login.html
@app.route('/login', methods=['POST']) 
def login_post():      
    input_username = request.form.get("username")
    password = request.form.get("password")
    #return ("input_username is {}, password is {}".format(input_username, password))   ## for debug to check if retriving is working.

    if not input_username or not password:
        flash("Please fill out all fields")
        return redirect(url_for('login_page'))
    
    ## checks if the user name is in the database and if it is, it saves it in the variable user
    user = User.query.filter_by(username=input_username).first()
    
    
    
    # checks if the user and user password is in the database with the same user variable.
    # if it is, it saves it in the variable password.
    # for the user password we use the check_password_hash function from werkzeug.security to check
    # if the password is the same as the one in the database with the same given user name
    if not user or not check_password_hash(user.hashed_password, password):
        flash("Invalid username or password")
        return redirect(url_for('login_page'))
    
    
    # return the home page when successful logged in.
    # Before we send the user to the home or index page,
    # we create the user cookies to track their unique activities.
    session['user_id'] = user.id
    flash('Login Successful')
    return redirect(url_for('home_page'))



#### Profile Backend  Controller
# related html file => profile.html
@app.route("/profile", methods=["POST"])
def profile_post():
    username = request.form.get("username")
    current_password = request.form.get("current_password")
    new_password = request.form.get("new_password")
    confirm_new_password = request.form.get("confirm_new_password")
    name = request.form.get("name")


    if username is None or current_password is None or new_password is None or confirm_new_password is None or name is None:
        flash('Please fill out all fields')
        return redirect(url_for('profile_page'))
    
    user = User.query.get(session["user_id"])  ## gets the user session id for their unique info
    if not check_password_hash(user.hashed_password, current_password):
        flash('Incorrect current password!')
        return redirect(url_for('profile_page'))
    
    # checks if username is already in the database for further implementation to change their user name with the line -> user.username = username, located below.
    if username != user.username:
        new_username = User.query.filter_by(username=username).first()
        if new_username:
            flash('Username already exists!')
            return redirect(url_for('profile_page'))


    # # don't want the user to change user name but rather use their username to make extra checks if user is the correct user to change their password
    # # use the line of code below
    # if username != user.username:
    #     flash("please input your correct username")
    #     return redirect(url_for('profile_page'))


    # checks if new password and confirm new password is the same and continue else redirects them to input the same password for the new password
    if new_password != confirm_new_password:  
        flash("new passwords do not match!")
        return redirect(url_for('profile_page'))
    
    #check if new password is the same as current password
    if new_password == current_password:
        flash("New password cannot be the same as current password")
        return redirect(url_for('profile_page'))

    # hashes the new user password
    new_password_hash = generate_password_hash(new_password)


    user.username = username  ##updates the current user's name to the new user name.
    user.hashed_password = new_password_hash ## upadtes the current user's password to the new user's password
    user.name = name
    db.session.commit()  ## saves the changes to the database
    
    # updats the user on seccussful update of their profile and returns them to their profile page.
    flash('Profile updated successfully')
    return redirect(url_for('profile_page'))

#################################### END OF BACKEND CONTROLLERS [register, login and profile] ################################################
















#################################### ADMIN CATEGORY CRUDE FRONTEND ROUTER ###################################################################
# add, show, edit and delete frontend html routers

# related html file => admin.html ---- serves the page that displays a table of all categories available in the database and given links to add, show, edit and delete caegories.
@app.route("/admin_dashboard")
@admin_required
def admin_dashboard():
    categories = Category.query.all() ## This retrieves all category names that were recently added to the database or already availble in the database.
    return render_template("admin.html", categories=categories)


# related html file => admin.html  ---- give a preview of the button to add category in the table in admin.html page and return the rendered page in the admin.html file when clicked
# related html file => category/add.html  ---- serves the page for the actual adding operation that the backend post method found below operates with.
@app.route("/category/add")
@admin_required
def add_category():
    return render_template('category/add.html')









                                # show category route has an entire page that has different frontend routes within it. Below after the admin category backend, are the frontend routes for the show category route and backend post method for the show category inner routes.
# related html file => admin.html  ---- give a preview of the link to list products in a category in the table in admin.html page and return the rendered page show.html with the admin.html page when the button for show products is clicked.
# related html file => show.html  ---- serves the page for the actual listinh and CRUD opration for adding, editing, and deleting products
@app.route("/category/show/<int:id>/")  ## we user <int:id> to identify the category we want to show using the ID of the category
@admin_required
def show_category(id):  ## id is the ID number of the category we want to show. flask automatically trask the ID that is been worked on, on the frontend view on the browser to relate them to the actual codes we are working with, in the code or programming section.
    # check if id from the route is in the database
    category = Category.query.get(id)
    datetime_now = datetime.now().strftime('%Y-%m-%d')
    if not category:
        flash("Category not found")
        return redirect(url_for('admin_dashboard'))
    else:

        return render_template('category/show.html', category=category)  ## if the category is found in the database, it renders the show.html page with the category name in the database.



@app.route("/category/show/<int:id>/product/add/")
@admin_required
def add_product(id):
    category = Category.query.get(id)
    if not category:
        flash('Category not found')
        return redirect(url_for('admin_dashboard'))
    categories = Category.query.all()
    return render_template('category/product/add.html', category=category, categories=categories)



@app.route("/category/show/<int:id>/product/edit/")
@admin_required
def edit_product(id):
    categories = Category.query.all()
    product = Product.query.get(id)
    return render_template('category/product/edit.html', product=product, categories=categories)



@app.route("/category/show/<int:id>/product/delete/")
@admin_required
def delete_product(id):
    product = Product.query.get(id)
    category = Category.query.get(product.category_id)
    return render_template('category/product/delete.html', product=product, category=category)
















# related html file => admin.html  ---- give a preview of the link to edit category in the table in admin.html page and return the rendered page in the admin.html file when clicked
# related html file => edit.html  ---- serves the page for the actual editing operation that the backend post method found below operates with.
@app.route("/category/<int:id>/edit")
@admin_required
def edit_category(id):  ## id is the ID number of the category we want to edit. flask automatically trask the ID that is been worked on, on the frontend view on the browser to relate them to the actual codes we are working with, in the code or programming section.
    category = Category.query.get(id) ## the ID is not retrieved from the ID base but from the frontend route of the category we are working with to edit. It checks the database if the iD is available and saves it into the varible to work with. 
    # check if ID is available in the database and flash given msg, else edit the retrieved category based ont the retrieved ID number.
    if not category:
        flash("Category not found")
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('category/edit.html', category=category)  


# related html file => admin.html  ---- give a preview of the link to delete category in the table in admin.html page and return the rendered page in the admin.html file when clicked
# related html file => delete.html  ---- serves the page for the actual delete operation that the backend post method found below operates with.
@app.route("/category/<int:id>/delete")
@admin_required
def delete_category(id): ## id is the ID number of the category we want to delete. flask automatically trask the ID that is been worked on, on the frontend view on the browser to relate them to the actual codes we are working with, in the code or programming section.
    category = Category.query.get(id)  ## the ID is not retrieved from the ID database but from the frontend route of the category we are working with to edit. It checks the database if the iD is available and saves it into the varible to work with. 
    # check if the category id from the frontend route is available in the database and flash given msg, else render the html page to delete category from the database
    if not category:
        flash("Category not found")
        return redirect(url_for('admin_dashboard'))
    else:
        return render_template('category/delete.html', category=category)

##################################### END OF ADMIN CATEGORY CRUD FRONTEND ROUTER ################################################################

# BACKEND operation for the 'Frontend route' above is the 'Backend controller' below

##################################### ADMIN CATEGORY BACKEND CRUD OPERATION #####################################################################
# add, show, edit and delete backend operations

# Add Backend Controller
@app.route("/category/add", methods=['POST'])
def add_category_post():
    """
        A function that request the form name from the html routing on the same
        route as /category/add retrieves the user input from the form name.
        If there is no form name, flash given message. Else creates a new category
        name and saves it in the database.

        Related Html File(s):
            add.html: serves the page for the actual adding operation that
            the backend post method 'add_Category_post' operates with.

    """

    name = request.form.get('category_name')
    if not name:
        flash('Please fill out all fields')
        return redirect(url_for('add_category'))
    else:
        add_cat_name = Category(cat_name=name)
        db.session.add(add_cat_name)
        db.session.commit()

        flash('Successfully added category')
        return redirect(url_for('admin_dashboard'))
    










# show inner route Backend Controller

@app.route("/category/show/<int:id>/product/add/", methods=['POST'])
@admin_required
def add_product_post(id):
    
    name = request.form.get('product_name')
    price = request.form.get('price')
    category_id = request.form.get('category_id')
    quantity_available = request.form.get('quantity_available')
    manu_date = request.form.get('manu_date')
    image = request.files.get('product_image')


    category = Category.query.get(category_id)
    if not category:
        flash('Category not found')
        return redirect(url_for('admin_dashboard'))
    if not name or not price or not category_id or not quantity_available or not manu_date:
        flash('Please fill out all fields')
        return redirect(url_for('add_product', id=category.id))
    try:
        price = float(price)
        quantity_available = int(quantity_available)
        manu_date = datetime.strptime(manu_date, '%Y-%m-%d')
    except ValueError:
        flash('Price and quantity must be numbers')
        return redirect(url_for('add_product', id=category.id))
    
    if quantity_available <= 0:
        flash('Quantity must be greater than 0')
        return redirect(url_for('add_product', id=category.id))
    if manu_date > datetime.now():
        flash('Manufacture date cannot be in the future')
        return redirect(url_for('add_product', id=category.id))
    


    if image is None:
        flash('No image file provided')
        return redirect(url_for('add_product', id=category.id))

    # check if filepath already exists. append random string if it does
    filename = secure_filename(image.filename)
    existing_paths = [p.product_image_path for p in Product.query.all()]

    if filename and filename in existing_paths:
        unique_str = str(uuid.uuid4())[:8]
        image.filename = f"{unique_str}_{image.filename}"


    if filename:
            file_ext = os.path.splitext(filename)[1]
            if file_ext not in app.config[
                "UPLOAD_EXTENSIONS"
            ]:
                flash('"error": "Image extension not supported"')
                return redirect(url_for('add_product', id=category.id))
            
            image_path = os.path.join(app.config["UPLOAD_PATH"], image.filename)
            image.save(image_path)



    product = Product(product_name=name, price=price, category_id=category.id, quantity_available=quantity_available, manu_date=manu_date, product_image_path=image_path)
    db.session.add(product)
    db.session.commit()

    flash('Product added successfully')
    return redirect(url_for('show_category', id=category.id))
    


    
# edit product backend controller
@app.route("/category/show/<int:id>/product/edit/", methods=['POST'])
def edit_product_post(id):
    name = request.form.get('product_name')
    price = request.form.get('price')
    category_id = request.form.get('category_id')
    quantity_available = request.form.get('quantity_available')
    manu_date = request.form.get('manu_date')
    image = request.files.get('product_image')

    category = Category.query.get(category_id)
    product = Product.query.get(id)

    if not category:
        flash('Category not found')
        return redirect(url_for('admin_dashboard'))
    if not name or not price or not category_id or not quantity_available or not manu_date:
        flash('Please fill out all fields')
        return redirect(url_for('edit_product', id=product.id))
    try:
        price = float(price)
        quantity_available = int(quantity_available)
        manu_date = datetime.strptime(manu_date, '%Y-%m-%d')
    except ValueError:
        flash('Price and quantity must be numbers')
        return redirect(url_for('edit_product', id=product.id))
    
    if quantity_available <= 0:
        flash('Quantity must be greater than 0')
        return redirect(url_for('edit_product', id=product.id))
    if manu_date > datetime.now():
        flash('Manufacture date cannot be in the future')
        return redirect(url_for('edit_product', id=product.id))


    if image:

        # remove previous file path from database and dir before updating new one
         # remove file from dir
        if os.path.exists(product.product_image_path):
            os.remove(product.product_image_path)
        
        # remove path from database
        product.product_image_path = 'No file yet'
        db.session.commit()



        filename = secure_filename(image.filename)
        existing_paths = [p.product_image_path for p in Product.query.all()]

        if filename and filename in existing_paths:
            unique_str = str(uuid.uuid4())[:8]
            image.filename = f"{unique_str}_{image.filename}"

        file_ext = os.path.splitext(filename)[1]
        if file_ext.lower() not in app.config["UPLOAD_EXTENSIONS"]:
            flash('"error": "Image extension not supported"')
            return redirect(url_for('edit_product_post', id=product.id))

        image_path = os.path.join(app.config["UPLOAD_PATH"], image.filename)
        image.save(image_path)
        product.product_image_path = image_path


    product.product_name = name
    product.price = price
    product.category_id = category.id
    product.quantity_available = quantity_available
    product.manu_date = manu_date
    
    
    db.session.commit()

    flash('Product edited successfully')
    return redirect(url_for('show_category', id=category.id))


@app.route("/category/show/<int:id>/product/delete/", methods=['POST'])
def delete_product_post(id):
    product = Product.query.get(id)
    category = Category.query.get(product.category_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully')
    return redirect(url_for('show_category', id=category.id))















# Edit Back Controller
@app.route("/category/<int:id>/edit", methods=['POST'])
def edit_category_post(id):
    """
        A function that retrieves the user input from the html input form name
        and updates the category name in the database with the retrieved name.

        Args:
            id: This is the ID of the category to edit. Flask automatically tracks the ID of the category that is been worked on,
            on the frontend view on the browser to relate them to the actual codes section.
            The ID is not retrieved from the database but from the frontend route of the category we are working with
            to check if the ID or category is in the database and make the requested modifications to the category name in the database
        
        Related Html File(s):
            edit.html: serves the frontend page which the user interacts with to edit the category name
            for the 'edit_category_post' backend controller to update the category name in the database.
    """
    
    
      ## id is the ID number of the category we want to edit. flask automatically trask the ID that is been worked on,
      ## on the frontend view on the browser to relate them to the actual codes we are working with, in the code or programming section.
    category = Category.query.get(id) 

    # check if ID is available in the database and flash given msg,
    # else edit the retrieved category based on the retrieved ID number in the database.
    if not category:
        flash("Category not found")
        return redirect(url_for('admin_dashboard'))
    
    # make a second check if html post method name for category to be editted or updated is empty and flash given message,
    # else update the category name in the database.
    name = request.form.get('category_name')
    if not name:
        flash('Please fill out all fields')
        return redirect(url_for('edit_category',id=id))
    else:
        # Now, we perform the actual update of the category name in the database with retrieved name from the frontend,
        # `name = request.form.get('category_name')`
        category.cat_name = name
        db.session.commit()
        flash('Category updated successfully')
        return redirect(url_for('admin_dashboard'))
    


# Delete Backend Controller
@app.route("/category/<int:id>/delete", methods=['POST'])
def delete_category_post(id):
    """
        A function that deletes a category from the database.

        Args:
            id: The ID of the category to delete. Flask automatically tracks the ID of the category that is been worked on,
            on the frontend view on the browser to relate them to the actual codes section.
            The ID is not retrieved from the database but from the frontend route of the category we are working with
            to check if the ID or category is in the database and delete the category from the database.
        
        Related Html File(s):
            delete.html: serves the frontend page which the user interacts with to delete the category
    """
    
    # checks the ID is available in the database, retrieves it and saves it into the varible to work with. 
    category = Category.query.get(id)
    # check if the category id from the frontend route is available in the database and flash given msg,
    # else delete category from the database
    if not category:
        flash("Category not found")
        return redirect(url_for('admin_dashboard'))
    else:
        db.session.delete(category)
        db.session.commit()
        flash('Category deleted successfully')
        return redirect(url_for('admin_dashboard'))
   

##################################### END of ADMIN CATEGORY BACKEND CRUD OPERATION ##################################################
    
















######################################  FRONTEND ROUTE  for CART and Order now button  ###########################################################################


@app.route('/cart')
@auth_required
def cart_page():
    """
        A function that retrieves the user's cart items from the database
        and renders the cart.html page with the user's cart items.

        Related Html File(s):
            cart.html: serves the frontend page which the user interacts with to view their cart items.
    """
    # retrieves the user's cart items from the database
    cart_items = Cart.query.filter_by(user_id=session['user_id']).all()
    
    # get the sum of the total price of the cart items
    total_price = sum([cart_item.product.price * cart_item.quantity_added_to_cart for cart_item in cart_items])
    
    return render_template('cart.html', carts=cart_items,total=total_price)



######################################  END of FRONTEND ROUTE CART and Order now button ###########################################################################

# BACKEND operation for the 'Frontend route' above is the 'Backend controller' below

######################################  BACKEND CONTROLLER for cart and order now button ###########################################################################

# cart 
@app.route('/cart/<int:id>/delete', methods=['POST'])
@auth_required
def cart_delete(id):
    """
        A function that deletes a product from the user's cart.

        Args:
            id: The ID of the product to delete from the user's cart. Flask automatically tracks the ID of the product that is been worked on,
            on the frontend view on the browser to relate them to the actual codes section.
            The ID is not retrieved from the database but from the frontend route of the product we are working with
            to check if the ID or product is in the database and delete the product from the user's cart.
        
        Related Html File(s):
            cart.html: serves the frontend page which the user interacts with to delete a product from their cart.
    """
    # retrieves the product from the user's cart
    cart_item = Cart.query.get(id)
    
    #check if the user is not deleting other user's scart page.
    if cart_item.user_id != session['user_id']:
        flash('You are not authorized to delete this item')
        return redirect(url_for('cart_page'))
    
    
    # check if the product is in the user's cart and delete the product from the user's cart
    if cart_item:
        db.session.delete(cart_item)
        db.session.commit()
        flash('Product removed from cart successfully')
    else:
        flash('Product not found in cart')

    
    
    return redirect(url_for('cart_page'))




# order now button in cart
@app.route("/order_now", methods=['POST'])
@auth_required
def order_now_button():
    carts = Cart.query.filter_by(user_id=session['user_id']).all()

    if not carts:
        flash('Cart is empty')
        return redirect(url_for('cart_page'))
    
    # Add the cart items to the transaction table
    transaction = Transaction(user_id=session['user_id'], date_time=datetime.now(), price=sum([cart.product.price * cart.quantity_added_to_cart for cart in carts]))

    # Add transaction to the session to generate its id
    db.session.add(transaction)
    db.session.commit()


    for cart in carts:
        order = Order(user_id=session['user_id'], product_id=cart.product_id, quantity=cart.quantity_added_to_cart, transaction_id=transaction.id, price=cart.product.price)
        # check if the product quantity saved in the cart is less than the total cart quantity
        if cart.product.quantity_available < cart.quantity_added_to_cart:
            flash(f'Product, {cart.product.product_name} is out of stock')
            return redirect(url_for('delete_product', id=cart.id))
        cart.product.quantity_available -= cart.quantity_added_to_cart
        
        db.session.add(order)
        db.session.delete(cart)

    db.session.add(transaction)
    db.session.commit()

    flash('Order placed successfully')
    return redirect(url_for('cart_page'))


######################################  END OF BACKEND CONTROLLER for cart and order now button ###########################################################################

















######################################  FRONTEND ROUTE FOR SHOW ORDER TRANSACTION HISTORY ###########################################################################

@app.route("/transaction_history")
@auth_required
def show_orders():
    """
        A function that retrieves the user's order history from the database
        and renders the order_history.html page with the user's order history.

        Related Html File(s):
            transaction_history.html: serves the frontend page which the user interacts with to view their order history.
    """
    # retrieves the user's order transaction history from the database
    transactions = Transaction.query.filter_by(user_id=session['user_id']).order_by(Transaction.date_time.desc()).all()
    return render_template('transaction_history.html', transactions=transactions)

######################################  END OF FRONTEND ROUTE FOR SHOW ORDER TRANSACTION HISTORY ###########################################################################

# BACKEND operation for the 'Frontend route' above is the 'Backend controller' below

######################################  BACKEND CONTROLER FOR SHOW ORDER TRANSACTION HISTORY ###########################################################################




######################################  END OF BACKEND CONTROLER FOR SHOW ORDER TRANSACTION HISTORY ###########################################################################
